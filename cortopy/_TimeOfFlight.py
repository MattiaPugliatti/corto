"""
===================
Simulated Time-of-Flight (ToF) camera class for the CORTO rendering pipeline.


Mirrors the Camera class pattern: the ToF object is instantiated once,
configured via set_* methods or directly from the State JSON, and then
process_one() is called inside the rendering loop after each
ENV.RenderOne() call to convert the rendered EXR passes into a ToF images.

Typical usage in a rendering script
-------------------------------------
see S10_Spacecraft.py for a complete example.

Output files
-------------
Two images per frame, saved under <output_path>/tof/images/:

    <######>_depth.npy      float32 (H, W)   metric radial range (m),
                                              NaN where no valid return.

    <######>_intensity.npy  float32 (H, W)   normalised return amplitude
                                              [0, 1], NaN where invalid.
"""
from __future__ import annotations

import os
import math
import numpy as np
from scipy.ndimage import uniform_filter, sobel, binary_dilation, generate_binary_structure

# Optional EXR backends (same pattern as LiDAR.py)
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


class TimeOfFlight:
    """Simulated Time-of-Flight camera sensor.

    Converts Blender depth + normal + albedo EXR passes (written by
    Compositing.create_tof_branch) into a physically realistic pair of
    depth and intensity images modelling the key artefacts of a
    phase-modulation or pulsed ToF camera.
    """

    _DEFAULTS = dict(
        width                = 640,
        height               = 480,
        fov_x_deg            = 70.0,
        max_range            = 10.0,
        range_bin_m          = 0.001,
        sigma_thermal        = 0.005,
        sigma_wiggling_k     = 0.003,
        shot_noise           = True,
        multipath_strength   = 0.02,
        flying_pixel_radius  = 2,
        min_intensity        = 0.005,
        grazing_deg          = 75.0,
        seed                 = None,
    )

    def __init__(self, state):
        for k, v in self._DEFAULTS.items():
            setattr(self, k, v)
        if hasattr(state, "tof") and isinstance(state.tof, dict):
            self._load_from_dict(state.tof)
        self._rng = np.random.default_rng(self.seed)

    # ------------------------------------------------------------------
    # Configuration helpers
    # ------------------------------------------------------------------

    def set_sensor(self, width: int = 640, height: int = 480,
                   fov_x_deg: float = 70.0):
        """Set sensor resolution and horizontal field of view.

        Args:
            width (int): image width in pixels.
            height (int): image height in pixels.
            fov_x_deg (float): horizontal FOV in degrees. Must match the
                Blender camera's angle_x setting.
        """
        self.width     = width
        self.height    = height
        self.fov_x_deg = fov_x_deg

    def set_camera_rotation(self, R: np.ndarray):
        """Provide the camera rotation matrix for world-to-camera normal transform.

        Must be called every frame after ENV.PositionAll() because the
        camera pose changes between frames.

        Args:
            R (np.ndarray): shape (3,3), columns are the camera X, Y, Z
                axes expressed in world coordinates. Obtain from Blender as:
                    bl_cam = bpy.context.scene.camera
                    R = np.array(bl_cam.matrix_world)[:3, :3].astype(np.float32)
        """
        self.cam_R = np.asarray(R, dtype=np.float32)

    def set_range(self, max_range: float = 10.0, range_bin_m: float = 0.001):
        """Set range measurement parameters.

        Args:
            max_range (float): maximum measurable radial range (m).
            range_bin_m (float): depth quantisation step (m). Typical: 0.001-0.005.
        """
        self.max_range   = max_range
        self.range_bin_m = range_bin_m

    def set_noise(self, sigma_thermal: float = 0.005,
                  sigma_wiggling_k: float = 0.003,
                  shot_noise: bool = True,
                  seed: int | None = None):
        """Set noise model parameters.

        Args:
            sigma_thermal (float): constant Gaussian noise floor (m).
                Models read noise and fixed-pattern noise. Typical: 0.002-0.010.
            sigma_wiggling_k (float): wiggling coefficient (m/m^2).
                sigma_wiggling(r) = k * r^2. Typical: 0.001-0.005.
            shot_noise (bool): if True, add photon shot noise scaling
                with 1/sqrt(intensity).
            seed (int | None): random seed for reproducibility.
        """
        self.sigma_thermal    = sigma_thermal
        self.sigma_wiggling_k = sigma_wiggling_k
        self.shot_noise       = shot_noise
        self.seed             = seed
        self._rng             = np.random.default_rng(seed)

    def set_artefacts(self, multipath_strength: float = 0.02,
                      flying_pixel_radius: int = 2):
        """Set systematic artefact parameters.

        Args:
            multipath_strength (float): maximum positive range bias (m) added
                near depth discontinuities to model multi-path interference.
                Typical: 0.01-0.05 m.
            flying_pixel_radius (int): half-width in pixels of the edge zone
                in which flying pixel artefacts are injected. Typical: 1-3 px.
        """
        self.multipath_strength  = multipath_strength
        self.flying_pixel_radius = flying_pixel_radius

    def set_returns(self, min_intensity: float = 0.005, grazing_deg: float = 75.0):
        """Set invalid-pixel gate parameters.

        Args:
            min_intensity (float): minimum normalised intensity [0,1] below
                which a pixel is declared invalid (NaN).
            grazing_deg (float): surface incidence angle above which pixels
                are unconditionally declared invalid (NaN).
        """
        self.min_intensity = min_intensity
        self.grazing_deg   = grazing_deg

    # ------------------------------------------------------------------
    # Main per-frame entry point
    # ------------------------------------------------------------------

    def process_one(self, state, index: int, cam) -> tuple[np.ndarray, np.ndarray]:
        """Generate ToF depth and intensity images for a single rendered frame.

        Call this immediately after ENV.RenderOne() inside the rendering loop.

        Args:
            state: corto State object (carries output_path).
            index (int): frame index.
            cam: corto Camera object (used to read FOV).

        Returns:
            tuple(depth_m, intensity): two float32 (H, W) arrays.
            NaN marks invalid / missing pixels.
            Both arrays are also saved to <output_path>/tof/images/.
        """
        fov_x               = self._get_fov_x(cam)
        depth_m, intensity  = self._render_to_tof(state, index, fov_x)
        self._save(state, index, depth_m, intensity)
        return depth_m, intensity

    # ------------------------------------------------------------------
    # Geometry helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _get_fov_x(cam) -> float:
        for attr in ("FOV", "fov", "fov_x", "angle_x", "lens_angle_x"):
            if hasattr(cam, attr):
                val = getattr(cam, attr)
                return math.degrees(val) if val < math.pi * 2 else val
        try:
            import bpy
            obj = bpy.data.objects.get("Camera")
            if obj is not None:
                return math.degrees(obj.data.angle_x)
        except Exception:
            pass
        return 60.0

    @staticmethod
    def _ray_directions(H: int, W: int, fov_x_deg: float) -> np.ndarray:
        """Per-pixel unit ray directions (H, W, 3), +Z into scene."""
        fx       = (W / 2.0) / math.tan(math.radians(fov_x_deg) / 2.0)
        u        = np.arange(W, dtype=np.float32) - (W - 1) / 2.0
        v        = np.arange(H, dtype=np.float32) - (H - 1) / 2.0
        uu, vv   = np.meshgrid(u, v)
        dirs     = np.stack([uu / fx, -vv / fx,
                             np.ones((H, W), np.float32)], axis=-1)
        return dirs / np.linalg.norm(dirs, axis=-1, keepdims=True)

    # ------------------------------------------------------------------
    # EXR loading (identical to LiDAR.py)
    # ------------------------------------------------------------------

    @staticmethod
    def _load_exr_channel(path: str, channel: str = "R") -> np.ndarray:
        if _HAS_OPENEXR:
            f   = OpenEXR.InputFile(path)
            dw  = f.header()["dataWindow"]
            W   = dw.max.x - dw.min.x + 1
            H   = dw.max.y - dw.min.y + 1
            pt = Imath.PixelType(Imath.PixelType.FLOAT)

            # Auto-detect: try requested channel, then common fallbacks
            available = list(f.header()["channels"].keys())
            fallbacks = [channel, "R", "V", "Y", "Z"]
            chosen = next((c for c in fallbacks if c in available), available[0])
            if chosen != channel:
                print(f"[ToF] Channel '{channel}' not found in {path}, "
                    f"using '{chosen}'. Available: {available}")
                
            raw = f.channel(chosen, pt)
            arr = np.frombuffer(raw, dtype=np.float32).reshape(H, W).copy()
            f.close()
            return arr
        if _HAS_IMAGEIO:
            import imageio.v3 as iio
            img = iio.imread(path, plugin="EXR-FI")
            idx = {"R": 0, "G": 1, "B": 2}.get(channel, 0)
            return (img[:, :, idx] if img.ndim == 3 else img).astype(np.float32)
        raise ImportError("Install OpenEXR or imageio[freeimage] to load EXR files.")

    @staticmethod
    def _load_exr_rgb(path: str) -> np.ndarray:
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
            return np.stack([r, g, b], axis=-1).copy()
        if _HAS_IMAGEIO:
            import imageio.v3 as iio
            return iio.imread(path, plugin="EXR-FI").astype(np.float32)
        raise ImportError("Install OpenEXR or imageio[freeimage] to load EXR files.")

    # ------------------------------------------------------------------
    # Core physics pipeline
    # ------------------------------------------------------------------

    def _render_to_tof(
        self, state, index: int, fov_x_deg: float
    ) -> tuple[np.ndarray, np.ndarray]:
        """Full ToF physics pipeline -> (depth_m, intensity) float32 (H, W)."""

        base  = state.path["output_path"]
        fname = f"{index:06d}.exr"

        # ── 1. Load EXR passes ────────────────────────────────────────
        Z_cam = self._load_exr_channel(
            os.path.join(base, "tof", "depth_exr", fname), "R")
        H, W  = Z_cam.shape

        normals_world = self._load_exr_rgb(
            os.path.join(base, "tof", "normal_exr", fname))
        # Blender Normal pass is already in [-1,1] – just normalise defensively
        n_norm        = np.linalg.norm(normals_world, axis=-1, keepdims=True)
        normals_world = normals_world / np.where(n_norm < 1e-6, 1.0, n_norm)

        albedo_path = os.path.join(base, "tof", "albedo_exr", fname)
        if os.path.exists(albedo_path):
            albedo = self._load_exr_rgb(albedo_path).mean(axis=-1)
        else:
            albedo = np.full((H, W), 0.5, dtype=np.float32)

        # ── 2. Z (orthographic) -> slant range ────────────────────────
        rays_cam  = self._ray_directions(H, W, fov_x_deg)   # (H,W,3) cam space
        cos_theta = np.clip(rays_cam[:, :, 2], 1e-6, None)
        r_true    = (Z_cam / cos_theta).astype(np.float32)

        # ── 3. FIX: incidence angle in world space ────────────────────
        # Camera rotation matrix: columns = cam X,Y,Z axes in world space.
        if hasattr(self, "cam_R") and self.cam_R is not None:
            R = self.cam_R
        else:
            # Blender default: camera looks along world -Y, up = world +Z
            R = np.array([
                [ 1,  0,  0],
                [ 0,  0,  1],
                [ 0, -1,  0],
            ], dtype=np.float32)

        # Transform every pixel's camera-space ray to world space (H,W,3)
        rays_world = np.einsum("ij,hwj->hwi", R, rays_cam)
        rw_norm    = np.linalg.norm(rays_world, axis=-1, keepdims=True)
        rays_world = rays_world / np.where(rw_norm < 1e-6, 1.0, rw_norm)

        # cos(incidence) = dot(-ray_world, surface_normal_world)
        cos_inc = np.einsum("hwc,hwc->hw",
                            -rays_world,
                            normals_world).astype(np.float32)

        # ── 4. Intensity: albedo x |cos_inc| / (r/max_range)^2 ───────
        # Normalised by max_range^2 so intensity stays in [0,1] across
        # the full sensor range (same fix as LiDAR BUG 3).
        intensity = np.clip(
            albedo * np.abs(cos_inc)
            / np.clip((r_true / self.max_range) ** 2, 1e-6, None),
            0.0, 1.0
        ).astype(np.float32)

        # ── 5. Invalid mask ───────────────────────────────────────────
        grazing_cos = math.cos(math.radians(self.grazing_deg))
        invalid = (
            (np.abs(cos_inc) < grazing_cos)
            | (r_true <= 0.0)
            | (r_true > self.max_range)
            | (intensity < self.min_intensity)
        )

        # ── 6. Wiggling noise  (sigma = k * r^2) ──────────────────────
        r_noisy = r_true + (
            self._rng.normal(0.0, 1.0, (H, W)).astype(np.float32)
            * self.sigma_wiggling_k * r_true ** 2
        )

        # ── 7. Thermal noise (constant floor) ─────────────────────────
        r_noisy += self._rng.normal(
            0.0, self.sigma_thermal, (H, W)).astype(np.float32)

        # ── 8. Shot noise (1/sqrt(intensity)) ─────────────────────────
        if self.shot_noise:
            sigma_shot = np.where(
                intensity > 1e-4,
                self.sigma_thermal / np.sqrt(np.clip(intensity, 1e-4, 1.0)),
                0.0
            ).astype(np.float32)
            r_noisy += (
                self._rng.normal(0.0, 1.0, (H, W)).astype(np.float32)
                * sigma_shot
            )

        # ── 9. Multi-path bias near discontinuities ───────────────────
        if self.multipath_strength > 0.0:
            edge    = np.hypot(sobel(r_true, axis=1),
                               sobel(r_true, axis=0)).astype(np.float32)
            edge_sm = uniform_filter(
                edge, size=max(1, self.flying_pixel_radius * 2 + 1))
            e_max   = edge_sm.max()
            if e_max > 1e-6:
                r_noisy += (edge_sm / e_max) * self.multipath_strength

        # ── 10. Flying pixels at depth edges ──────────────────────────
        if self.flying_pixel_radius > 0:
            edge  = np.hypot(sobel(r_true, axis=1), sobel(r_true, axis=0))
            valid = ~invalid
            if valid.any():
                thresh = np.percentile(edge[valid], 95)
                emask  = edge > thresh
                struct = generate_binary_structure(2, 1)
                for _ in range(self.flying_pixel_radius):
                    emask = binary_dilation(emask, struct)
                r_bg    = uniform_filter(r_true, size=5).astype(np.float32)
                alpha   = self._rng.uniform(0.0, 1.0, (H, W)).astype(np.float32)
                r_noisy = np.where(emask,
                                   alpha * r_true + (1.0 - alpha) * r_bg,
                                   r_noisy)

        # ── 11. Quantisation ──────────────────────────────────────────
        r_q = np.clip(
            np.round(r_noisy / self.range_bin_m) * self.range_bin_m,
            0.0, self.max_range
        ).astype(np.float32)

        # ── 12. Apply NaN mask ────────────────────────────────────────
        depth_out     = np.where(invalid, np.nan, r_q)
        intensity_out = np.where(invalid, np.nan, intensity)

        return depth_out.astype(np.float32), intensity_out.astype(np.float32)
    
    # ------------------------------------------------------------------
    # Output
    # ------------------------------------------------------------------

    def _save(self, state, index: int,
              depth_m: np.ndarray, intensity: np.ndarray):
        out_dir = os.path.join(state.path["output_path"], "tof", "images")
        os.makedirs(out_dir, exist_ok=True)
        np.save(os.path.join(out_dir, f"{index:06d}_depth.npy"),     depth_m)
        np.save(os.path.join(out_dir, f"{index:06d}_intensity.npy"), intensity)

    def _load_from_dict(self, d: dict):
        for k in self._DEFAULTS:
            if k in d:
                setattr(self, k, d[k])
