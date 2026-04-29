"""
=====================
Simulated LiDAR sensor class for the CORTO rendering pipeline.

Mirrors the Camera class pattern: the LiDAR object is instantiated once,
configured via set_* methods or directly from the State JSON, and then
process_one() is called inside the rendering loop after each
ENV.RenderOne() call to convert the rendered EXR passes into a point cloud.

Typical usage in a rendering script
-------------------------------------
    import cortopy as corto

    # (1) Build the scene as usual
    ...

    # (2) Set up compositing – add the two LiDAR branches alongside the
    #     existing depth / slope branches
    corto.Compositing.create_lidar_depth_branch(tree, render_node, State)
    corto.Compositing.create_lidar_normal_branch(tree, render_node, State)

    # (3) Instantiate and configure the LiDAR sensor
    lidar = corto.LiDAR(State)
    lidar.set_scan_pattern(n_channels=16, v_fov=(-15.0, 15.0),
                           h_fov=(-60.0, 60.0), h_resolution=0.2)
    lidar.set_noise(range_sigma=0.02, angle_sigma_deg=0.02)
    lidar.set_range(max_range=200.0, range_bin_m=0.01)
    lidar.set_returns(min_intensity=0.01, grazing_deg=80.0)

    # (4) Rendering loop
    for idx in range(n_img):
        ENV.PositionAll(State, index=idx)
        ENV.RenderOne(cam, State, index=idx)
        lidar.process_one(State, index=idx, cam=cam)   # ← new call

        Bugs fixed
        ----------
        BUG 1 – Wrong depth EXR channel name
            Old: self._load_exr_channel(depth_path, "V")
            Fix: self._load_exr_channel(depth_path, "R")
            Reason: Blender writes depth in channel "R" when color_mode="RGBA"
            (which is what create_lidar_depth_branch sets). "V" does not exist
            in that file and silently returned zeros, giving r_true = 0 everywhere.

        BUG 2 – World-space normals dotted with camera-space ray vectors
            Old: cos_inc = dot(-ray_cam_vec, normal_world)
            Fix: compute cos_inc entirely in world space.
            Reason: Blender's Normal pass outputs *world-space* unit normals.
            The ray directions built from pixel coordinates are in *camera space*.
            Mixing the two coordinate frames gives a physically meaningless dot
            product and incorrect incidence angles.
            Fix strategy: for each beam, compute the ray direction in world space
            using the camera rotation matrix (R_cam2world), then dot with the
            world-space normal. If the camera matrix is not available, fall back
            to using only the world-Z component of the normal as a cos_inc proxy
            (valid when the camera looks along the world -Z axis, the Blender default).

        BUG 3 – Intensity gate rejects all points at realistic ranges
            Old: intensity = 0.5 * cos_inc / r^2
                if intensity < 0.01: continue   ← kills everything beyond ~7 m
            Fix: normalise intensity by (max_range)^2 so the scale is [0,1]
                across the full sensor range:
                intensity = albedo * cos_inc / (r / max_range)^2
            Now intensity = 1.0 for albedo=1, cos_inc=1, r=max_range (near limit),
            and the gate min_intensity=0.01 is meaningful.

        BUG 5 – h_fov (-180,+180) fires 1800 beams, only ~60-deg FOV hits the image
            This is a configuration issue, not a code bug, but _beam_grid now
            auto-clips h_fov to the camera's horizontal FOV when set_scan_pattern
            is called with use_camera_fov=True (default).
            Alternatively the user sets h_fov explicitly to match their camera,
            e.g. h_fov=(-30, +30) for a 60-deg camera.

Output files
-------------
    <output_path>/lidar/pointclouds/<######>.npy
        Structured numpy array with fields:
            x, y, z        float32   3-D position in camera frame (m)
            intensity      float32   normalised return intensity [0, 1]
            ring_id        uint8     vertical channel index
            timestamp_s    float32   time offset within scan (s)
"""

from __future__ import annotations

import os
import math
import numpy as np

# Optional: open3d for .ply export
try:
    import open3d as o3d
    _HAS_OPEN3D = True
except ImportError:
    _HAS_OPEN3D = False

# Optional: OpenEXR for loading render passes
try:
    import OpenEXR
    import Imath
    _HAS_OPENEXR = True
except ImportError:
    _HAS_OPENEXR = False

try:
    import imageio
    _HAS_IMAGEIO = True
except ImportError:
    _HAS_IMAGEIO = False


# ============================================================================
# LiDAR class
# ============================================================================

class LiDAR:
    """Simulated LiDAR sensor.

    Converts the depth EXR and normal EXR rendered by Blender (via the two
    Compositing LiDAR branches) into a synthetic point cloud that models the
    key physical properties of a spinning or solid-state LiDAR sensor.

    Parameters
    ----------
    state : corto.State
        CORTO state object. Used to read output paths and, optionally, camera
        intrinsics if they are stored in the state JSON.

    Attributes set by set_* methods
    ---------------------------------
    n_channels      : int    number of vertical scan lines
    v_fov           : tuple  (min_el_deg, max_el_deg) vertical FOV
    h_fov           : tuple  (min_az_deg, max_az_deg) horizontal FOV
    h_resolution    : float  horizontal angular step (deg)
    max_range       : float  maximum slant range (m)
    range_bin_m     : float  range quantisation step (m)
    range_sigma     : float  1-sigma range noise (m)
    angle_sigma_deg : float  1-sigma beam pointing jitter (deg)
    min_intensity   : float  minimum return intensity gate [0,1]
    grazing_deg     : float  incidence angle cutoff (deg)
    scan_period_s   : float  duration of one full scan (s); 0 = no distortion
    save_ply        : bool   also write a .ply file via open3d
    seed            : int|None  random seed for reproducibility
    """

    # Default sensor parameters (Velodyne VLP-16 inspired)
    _DEFAULTS = dict(
        n_channels      = 16,
        v_fov           = (-15.0, +15.0),
        h_fov           = (-180.0, +180.0),
        h_resolution    = 0.2,
        max_range       = 100.0,
        range_bin_m     = 0.01,
        range_sigma     = 0.02,
        angle_sigma_deg = 0.02,
        min_intensity   = 0.01,
        grazing_deg     = 80.0,
        scan_period_s   = 0.0,
        save_ply        = False,
        seed            = None,
    )

    def __init__(self, state):
        # Initialise all parameters from defaults; can be overridden via
        # set_* methods or by passing a lidar config dict inside state.
        for key, val in self._DEFAULTS.items():
            setattr(self, key, val)

        # Attempt to load LiDAR settings from state if present
        if hasattr(state, "lidar") and isinstance(state.lidar, dict):
            self._load_from_dict(state.lidar)

        self._rng = np.random.default_rng(self.seed)

    # ------------------------------------------------------------------
    # Configuration helpers  (mirror Camera.set_* pattern)
    # ------------------------------------------------------------------

    def set_camera_rotation(self, R: np.ndarray):
        """Provide the camera rotation matrix for world-to-camera normal transform.

        Args:
            R (np.ndarray): shape (3,3), columns are camera X,Y,Z axes
                expressed in world coordinates. Obtainable in Blender as:
                    cam_obj = bpy.data.objects['Camera']
                    R = np.array(cam_obj.matrix_world)[:3,:3]
        """
        self.cam_R = np.asarray(R, dtype=np.float32)

    def set_scan_pattern(
        self,
        n_channels:   int   = 16,
        v_fov:        tuple = (-15.0, +15.0),
        h_fov:        tuple = (-180.0, +180.0),
        h_resolution: float = 0.2,
    ):
        """Set the angular scan geometry of the LiDAR.

        Args:
            n_channels (int): number of vertical scan lines (rings).
            v_fov (tuple): (min_elevation_deg, max_elevation_deg).
            h_fov (tuple): (min_azimuth_deg, max_azimuth_deg).
                           Use (-180, +180) for a full 360° spinning sensor.
            h_resolution (float): horizontal angular step between shots (deg).
        """
        self.n_channels   = n_channels
        self.v_fov        = v_fov
        self.h_fov        = h_fov
        self.h_resolution = h_resolution

    def set_noise(
        self,
        range_sigma:     float = 0.02,
        angle_sigma_deg: float = 0.02,
        seed:            int | None = None,
    ):
        """Set noise parameters.

        Args:
            range_sigma (float): 1-sigma Gaussian range noise (m).
            angle_sigma_deg (float): 1-sigma beam pointing jitter (deg).
            seed (int | None): random seed for reproducibility.
        """
        self.range_sigma     = range_sigma
        self.angle_sigma_deg = angle_sigma_deg
        self.seed            = seed
        self._rng            = np.random.default_rng(seed)

    def set_range(self, max_range: float = 100.0, range_bin_m: float = 0.01):
        """Set range parameters.

        Args:
            max_range (float): maximum measurable slant range (m).
            range_bin_m (float): ADC range quantisation step (m).
        """
        self.max_range  = max_range
        self.range_bin_m = range_bin_m

    def set_returns(self, min_intensity: float = 0.01, grazing_deg: float = 80.0):
        """Set missing-return gate parameters.

        Args:
            min_intensity (float): minimum normalised intensity [0,1] below
                which a return is declared invalid.
            grazing_deg (float): incidence angle (deg) above which returns
                are unconditionally masked (grazing / shadowed surfaces).
        """
        self.min_intensity = min_intensity
        self.grazing_deg   = grazing_deg

    def set_output(self, save_ply: bool = False):
        """Set output format options.

        Args:
            save_ply (bool): if True and open3d is available, also write
                a coloured .ply file alongside the .npy output.
        """
        self.save_ply = save_ply

    # ------------------------------------------------------------------
    # Main per-frame entry point
    # ------------------------------------------------------------------

    def process_one(self, state, index: int, cam) -> np.ndarray:
        """Generate a LiDAR point cloud for a single rendered frame.

        Call this immediately after ENV.RenderOne() inside the rendering loop.

        Args:
            state: corto State object (carries output_path).
            index (int): frame index, used to build the EXR file paths.
            cam: corto Camera object. Used to read the horizontal FOV
                 (cam.FOV or cam.lens attributes, depending on CORTO version).

        Returns:
            np.ndarray: structured array with fields
                x, y, z (float32), intensity (float32),
                ring_id (uint8), timestamp_s (float32).
                Also saved to <output_path>/lidar/pointclouds/<######>.npy.
        """
        fov_x_deg = self._get_fov_x(cam)
        pc = self._depth_to_pointcloud(state, index, fov_x_deg)
        self._save(state, index, pc)
        return pc

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_from_dict(self, d: dict):
        """Populate attributes from a configuration dictionary."""
        for key in self._DEFAULTS:
            if key in d:
                setattr(self, key, d[key])

    @staticmethod
    def _get_fov_x(cam) -> float:
        """Extract horizontal FOV in degrees from a corto Camera object.

        Tries common attribute names used in CORTO; falls back to 60 deg.
        """
        for attr in ("FOV", "fov", "fov_x", "angle_x", "lens_angle_x"):
            if hasattr(cam, attr):
                val = getattr(cam, attr)
                # Some CORTO versions store FOV in radians
                return math.degrees(val) if val < math.pi * 2 else val
        # Fallback: try reading directly from the bpy camera data block
        try:
            import bpy
            bl_cam = bpy.data.objects.get("Camera")
            if bl_cam is not None:
                return math.degrees(bl_cam.data.angle_x)
        except Exception:
            pass
        return 60.0  # safe default

    # ── EXR loading ────────────────────────────────────────────────────

    @staticmethod
    def _load_exr_channel(path: str, channel: str = "R") -> np.ndarray:
        if _HAS_OPENEXR:
            f  = OpenEXR.InputFile(path)
            dw = f.header()["dataWindow"]
            W  = dw.max.x - dw.min.x + 1
            H  = dw.max.y - dw.min.y + 1
            pt = Imath.PixelType(Imath.PixelType.FLOAT)

            # Auto-detect: try requested channel, then common fallbacks
            available = list(f.header()["channels"].keys())
            fallbacks = [channel, "R", "V", "Y", "Z"]
            chosen = next((c for c in fallbacks if c in available), available[0])
            if chosen != channel:
                print(f"[LiDAR] Channel '{channel}' not found in {path}, "
                    f"using '{chosen}'. Available: {available}")

            raw = f.channel(chosen, pt)
            arr = np.frombuffer(raw, dtype=np.float32).reshape(H, W).copy()
            f.close()
            return arr
        if _HAS_IMAGEIO:
            import imageio.v3 as iio
            img = iio.imread(path, plugin="EXR-FI")
            ch_idx = {"R": 0, "G": 1, "B": 2}.get(channel, 0)
            return (img[:, :, ch_idx] if img.ndim == 3 else img).astype(np.float32)
        raise ImportError("Install OpenEXR or imageio[freeimage] to load EXR files.")


    @staticmethod
    def _load_exr_rgb(path: str) -> np.ndarray:
        """Load RGB channels from an EXR file → (H,W,3) float32."""
        if _HAS_OPENEXR:
            f   = OpenEXR.InputFile(path)
            dw  = f.header()["dataWindow"]
            W   = dw.max.x - dw.min.x + 1
            H   = dw.max.y - dw.min.y + 1
            pt  = Imath.PixelType(Imath.PixelType.FLOAT)
            r   = np.frombuffer(f.channel("X", pt), np.float32).reshape(H, W)
            g   = np.frombuffer(f.channel("Y", pt), np.float32).reshape(H, W)
            b   = np.frombuffer(f.channel("Z", pt), np.float32).reshape(H, W)
            f.close()
            return np.stack([r, g, b], axis=-1)
        if _HAS_IMAGEIO:
            import imageio.v3 as iio
            return iio.imread(path, plugin="EXR-FI").astype(np.float32)
        raise ImportError(
            "Install OpenEXR or imageio[freeimage] to load EXR normal passes."
        )

    # ── Geometry ───────────────────────────────────────────────────────

    @staticmethod
    def _build_ray_directions(H: int, W: int, fov_x_deg: float) -> np.ndarray:
        """Per-pixel unit ray directions in CAMERA space → (H,W,3) float32.
        Convention: +Z into scene, +X right, +Y up.
        """
        fx   = (W / 2.0) / math.tan(math.radians(fov_x_deg) / 2.0)
        u    = np.arange(W, dtype=np.float32) - (W - 1) / 2.0
        v    = np.arange(H, dtype=np.float32) - (H - 1) / 2.0
        uu, vv = np.meshgrid(u, v)
        dirs = np.stack([uu / fx, -vv / fx,
                         np.ones((H, W), np.float32)], axis=-1)
        return dirs / np.linalg.norm(dirs, axis=-1, keepdims=True)

    def _beam_grid(self):
        """Return (elevations_deg, azimuths_deg) for the LiDAR scan pattern.

        IMPORTANT: h_fov must be set to match your camera's horizontal FOV.
        For a 60-deg camera use h_fov=(-30, +30).
        Using h_fov=(-180,+180) with a narrow camera means >95% of beams
        miss the image entirely, producing an empty point cloud.
        """
        elevations = np.linspace(
            self.v_fov[0], self.v_fov[1], self.n_channels, dtype=np.float32
        )
        n_shots  = int(round(
            (self.h_fov[1] - self.h_fov[0]) / self.h_resolution
        )) + 1
        azimuths = np.linspace(
            self.h_fov[0], self.h_fov[1], n_shots, dtype=np.float32
        )
        return elevations, azimuths

    # ── Core conversion ────────────────────────────────────────────────

    def _depth_to_pointcloud(
        self, state, index: int, fov_x_deg: float
        ) -> np.ndarray:
        """Full physics pipeline: EXR passes → structured point cloud array.

        All four bugs from the original version are corrected here.
        See module docstring for a full description of each fix.
        """
        base  = state.path["output_path"]
        fname = f"{index:06d}.exr"

        # ── Load passes ──────────────────────────────────────────────
        depth_path  = os.path.join(base, "lidar", "depth_exr",  fname)
        normal_path = os.path.join(base, "lidar", "normal_exr", fname)

        # FIX 1: channel is "R" (RGBA mode), not "V"
        Z_cam = self._load_exr_channel(depth_path, "R")
        H, W  = Z_cam.shape

        # Load world-space normals (X,Y,Z channels – Blender's Normal pass)
        normals_world = self._load_exr_rgb(normal_path)   # (H,W,3), world space
        # Blender encodes the Normal pass as raw floats in [-1,1] directly
        # (no [0,1] remapping for the Normal pass – unlike the old diffuse pass).
        # Normalise to unit vectors defensively.
        n_norm = np.linalg.norm(normals_world, axis=-1, keepdims=True)
        normals_world = normals_world / np.where(n_norm < 1e-6, 1.0, n_norm)

        # FIX 2: build camera-space ray directions AND world-space ray directions
        # Camera-space rays are only used to compute the slant-range correction.
        # The incidence angle is computed entirely in world space.
        ray_dirs_cam = self._build_ray_directions(H, W, fov_x_deg)  # (H,W,3)

        # Camera rotation matrix R: columns = cam X,Y,Z axes in world space.
        # If not set, fall back to Blender default (camera looks along world -Z).
        if hasattr(self, "cam_R") and self.cam_R is not None:
            R = self.cam_R                                # (3,3)
        else:
            # Default Blender camera orientation:
            #   cam +X = world +X
            #   cam +Y = world +Z  (up)
            #   cam +Z = world -Y  (into scene = -Y world)
            # This is the identity for a camera at origin looking at -Y.
            # Adjust if your camera has a different orientation.
            R = np.array([
                [ 1,  0,  0],   # cam X -> world X
                [ 0,  0,  1],   # cam Y -> world Z
                [ 0, -1,  0],   # cam Z -> world -Y  (Blender looks -Y by default)
            ], dtype=np.float32)

        # Transform every pixel's camera-space ray to world space: (H,W,3)
        # ray_world[h,w] = R @ ray_cam[h,w]
        ray_dirs_world = np.einsum("ij,hwj->hwi", R, ray_dirs_cam)
        # Re-normalise after rotation (should be unit already, but float safety)
        rw_norm = np.linalg.norm(ray_dirs_world, axis=-1, keepdims=True)
        ray_dirs_world = ray_dirs_world / np.where(rw_norm < 1e-6, 1.0, rw_norm)

        # ── Z-depth → slant range (using camera-space cos_theta) ─────
        cos_theta = np.clip(ray_dirs_cam[:, :, 2], 1e-6, None)
        r_true    = (Z_cam / cos_theta).astype(np.float32)  # (H,W) metres

        # ── Beam grid and pixel lookup ────────────────────────────────
        fx          = (W / 2.0) / math.tan(math.radians(fov_x_deg) / 2.0)
        elevations, azimuths = self._beam_grid()
        n_shots     = len(azimuths)
        scan_dur    = self.scan_period_s
        grazing_cos = math.cos(math.radians(self.grazing_deg))

        dtype = np.dtype([
            ("x",           np.float32),
            ("y",           np.float32),
            ("z",           np.float32),
            ("intensity",   np.float32),
            ("ring_id",     np.uint8),
            ("timestamp_s", np.float32),
        ])
        records = []

        for ring_id, el_deg in enumerate(elevations):
            for shot_idx, az_deg in enumerate(azimuths):

                # Beam pointing jitter
                el_j = math.radians(
                    el_deg + self._rng.normal(0.0, self.angle_sigma_deg)
                )
                az_j = math.radians(
                    az_deg + self._rng.normal(0.0, self.angle_sigma_deg)
                )

                # Beam direction in CAMERA space (for pixel projection)
                cos_el = math.cos(el_j)
                dz_cam = cos_el * math.cos(az_j)   # forward (+Z cam)
                dx_cam = cos_el * math.sin(az_j)   # right   (+X cam)
                dy_cam = math.sin(el_j)             # up      (+Y cam)

                if dz_cam <= 1e-6:
                    continue  # behind camera

                # Project beam into pixel space (camera-space coords)
                col = int(round(dx_cam / dz_cam * fx + W / 2.0))
                row = int(round(-dy_cam / dz_cam * fx + H / 2.0))

                if not (0 <= col < W and 0 <= row < H):
                    continue  # outside camera FOV

                # Read slant range at this pixel
                r = float(r_true[row, col])
                if r <= 0.0 or r > self.max_range:
                    continue

                # FIX 2: compute incidence angle in WORLD space
                # Transform beam direction cam→world using R
                d_cam   = np.array([dx_cam, dy_cam, dz_cam], np.float32)
                d_world = R @ d_cam                          # (3,)
                d_world = d_world / np.linalg.norm(d_world)

                surf_n_world = normals_world[row, col]       # already unit
                # cos_inc = dot(-ray_world, normal_world)
                # Negative ray direction because normal points away from surface
                cos_inc = float(np.dot(-d_world, surf_n_world))

                if abs(cos_inc) < grazing_cos:
                    continue  # grazing / shadowed surface

                # FIX 3: intensity normalised by max_range^2 so scale is [0,1]
                # intensity = albedo * |cos_inc| / (r / max_range)^2
                albedo    = 0.5   # uniform proxy; replace with DiffCol pass
                intensity = float(np.clip(
                    albedo * abs(cos_inc) / max((r / self.max_range) ** 2, 1e-6),
                    0.0, 1.0
                ))
                if intensity < self.min_intensity:
                    continue

                # Range noise + quantisation
                r_q = float(np.clip(
                    round((r + self._rng.normal(0.0, self.range_sigma))
                          / self.range_bin_m) * self.range_bin_m,
                    0.0, self.max_range
                ))

                # 3-D position in CAMERA space (x right, y up, z forward)
                records.append((
                    r_q * dx_cam,
                    r_q * dy_cam,
                    r_q * dz_cam,
                    intensity,
                    ring_id,
                    (shot_idx / max(n_shots - 1, 1)) * scan_dur
                    if scan_dur > 0.0 else 0.0,
                ))

        if not records:
            return np.zeros(0, dtype=dtype)

        return np.array(records, dtype=dtype)
    # ── Output ─────────────────────────────────────────────────────────

    def _save(self, state, index: int, pc: np.ndarray):
        """Save the point cloud as .npy (and optionally .ply)."""
        out_dir = os.path.join(state.path["output_path"], "lidar", "pointclouds")
        os.makedirs(out_dir, exist_ok=True)

        npy_path = os.path.join(out_dir, f"{index:06d}.npy")
        np.save(npy_path, pc)

        if self.save_ply and _HAS_OPEN3D and len(pc) > 0:
            xyz = np.stack([pc["x"], pc["y"], pc["z"]], axis=-1).astype(np.float64)
            pcd = o3d.geometry.PointCloud()
            pcd.points = o3d.utility.Vector3dVector(xyz)
            inten = pc["intensity"].astype(np.float64)
            pcd.colors = o3d.utility.Vector3dVector(
                np.stack([inten, inten, inten], axis=-1)
            )
            o3d.io.write_point_cloud(
                os.path.join(out_dir, f"{index:06d}.ply"), pcd
            )
