"""
================================
Simulated structured-light sensor class for the CORTO rendering pipeline.

Mirrors the LiDAR and ToF class patterns:
  - Instantiated once before the rendering loop.
  - Configured via set_* methods.
  - process_one() called inside the loop after ENV.PositionAll().

Working principle
-----------------
Five red spot lights are arranged in a cross pattern and rigidly parented
to the Blender camera object, so they move with it exactly.  For each
frame the sensor:
  1. Enables all five lights.
  2. Calls bpy.ops.render.render() to capture the scene with the
     projected pattern.
  3. Saves the RGB image.
  4. Disables all five lights, leaving the scene clean for other sensors.

Light layout (viewed from behind the projector, looking toward target)
-----------------------------------------------------------------------

                        [top]
                          |
             [left] -- [centre] -- [right]
                          |
                       [bottom]

The four outer lights are canted outward by `cant_deg` so their beams
diverge slightly from the optical axis, spreading the cross pattern over
a wider area on the target surface.

Cant angle convention
---------------------
    cant_deg = 0   → all five beams are parallel (pure translation pattern)
    cant_deg > 0   → outer beams toe outward; pattern spreads with distance

Output
------
One PNG image per frame saved to:
    <output_path>/structured_light/images/<######>.png

Typical usage
-------------
    import cortopy as corto

    sl = corto.StructuredLight(State)
    sl.set_projector(
        offset_m      = 0.05,    # cross arm length (m) – distance from centre to outer light
        cant_deg      = 5.0,     # outward cant angle of the four outer lights
        spot_size_deg = 3.0,     # half-angle of each spot cone
        energy        = 500.0,   # light power (W)
    )
    sl.set_color(r=1.0, g=0.0, b=0.0)   # red by default
    sl.setup(State)                       # creates lights in the Blender scene

    for idx in range(n_img):
        ENV.PositionAll(State, index=idx)
        sl.process_one(State, index=idx)

    sl.teardown()   # removes lights from scene (optional, call at end)

Notes
-----
- setup() must be called once after the Blender scene is loaded and
  before the rendering loop starts.
- The lights are parented to bpy.context.scene.camera so they inherit
  every camera pose update from ENV.PositionAll() automatically.
- process_one() does NOT call ENV.RenderOne() – it renders directly via
  bpy.ops.render.render() with the output path overridden, so it is
  fully independent of the standard CORTO image render.
- If you want BOTH a standard image AND a structured-light image for the
  same frame, call ENV.RenderOne() first (lights off), then
  sl.process_one() (lights on).
"""

from __future__ import annotations

import os
import math
import numpy as np
import bpy
import mathutils

class StructuredLight:
    """Simulated structured-light projector + camera sensor.

    The projector consists of five Blender spot lights arranged in a cross
    and rigidly parented to the scene camera.

    Parameters are set via set_* methods after construction.
    Call setup() once to create the Blender objects, then process_one()
    inside the rendering loop.
    """

    # Names used for the five Blender light objects
    _LIGHT_NAMES = [
        "SL_centre",
        "SL_top",
        "SL_bottom",
        "SL_left",
        "SL_right",
    ]

    _DEFAULTS = dict(
        offset_m      = 0.05,    # m – cross arm length (centre → outer light)
        cant_deg      = 5.0,     # deg – outward cant of the four outer lights
        spot_size_deg = 3.0,     # deg – half-angle of spot cone
        energy        = 1000.0,   # W  – light power
        color         = (1.0, 0.0, 0.0),  # RGB – red
        projector_distance_m    = 0.0,    # 0 = at camera origin
        projector_distance_frac = None,   # None = use projector_distance_m   
        )

    def __init__(self, state):
        for k, v in self._DEFAULTS.items():
            setattr(self, k, v)
        if hasattr(state, "structured_light") and isinstance(
            state.structured_light, dict
        ):
            self._load_from_dict(state.structured_light)
        self._lights_created = False
        self._target_name    = None
    # ------------------------------------------------------------------
    # Configuration helpers
    # ------------------------------------------------------------------

    def set_projector(
        self,
        offset_m:      float = 0.05,
        cant_deg:      float = 5.0,
        spot_size_deg: float = 3.0,
        energy:        float = 500.0,
        projector_distance_m:    float = 0.0,
        projector_distance_frac: float | None = None,
    ):
        """Set the geometric and photometric properties of the projector.

        Args:
            offset_m (float): distance from the centre light to each of the
                four outer lights, in metres (the cross arm length).
                Larger values spread the cross pattern more at close range.
            cant_deg (float): outward cant angle of the four outer spot lights
                (degrees).  At cant_deg=0 all beams are parallel.  At
                cant_deg=5 the outer beams diverge 5 deg from the axis,
                so the cross pattern grows linearly with target distance.
            spot_size_deg (float): half-angle of each spot cone (degrees).
                Controls the width of each dot/line on the target surface.
                Blender's minimum is ~0.87 deg; use projector_distance_m
                Typical: 1–10 deg.
                or projector_distance_frac to achieve narrower footprints.
            energy (float): light power (Watts). Increase when lights are
                targets or low-albedo surfaces.  Typical: 100–2000 W.
                far from the target or the surface albedo is low.
            projector_distance_m (float): distance along the camera optical
                axis (-Z local) at which the lights are placed (metres).
                0.0 = coincident with camera. Larger values move lights
                toward the target, shrinking the illuminated footprint.
                Ignored if projector_distance_frac is set.
            projector_distance_frac (float | None): if set (0–1), the
                light distance is computed each frame as this fraction of
                the camera-to-target distance. Requires target_name to be
                passed to setup(). Overrides projector_distance_m.
        """
        self.offset_m      = offset_m
        self.cant_deg      = cant_deg
        self.spot_size_deg = spot_size_deg
        self.energy        = energy
        self.projector_distance_m    = projector_distance_m
        self.projector_distance_frac = projector_distance_frac

    def set_color(self, r: float = 1.0, g: float = 0.0, b: float = 0.0):
        """Set the light colour (default: red).
        Args:
            r, g, b (float): RGB components in [0, 1].
                Default is pure red (1, 0, 0), typical for structured-light
                systems that use a bandpass filter on the camera side.
        """
        self.color = (float(r), float(g), float(b))

    # ------------------------------------------------------------------
    # Scene setup / teardown
    # ------------------------------------------------------------------

 
    def setup(self, state, cam, target_name: str | None = None):
        """Create or update the five structured-light spot lights.
 
        On the first call the lights are created and parented to the camera.
        On subsequent calls (e.g. after set_projector() with new parameters)
        the existing lights are updated in-place — no objects are deleted
        and no other scene lights are touched.
 
        Args:
            state: corto State object (kept for API consistency).
            cam:   corto Camera object. cam.name must match the name of the
                   Blender camera object in the scene (e.g. "Camera").
        """
        import bpy
        self._target_name = target_name
        # ── Resolve the Blender camera object from cam.name ───────────
        cam_obj = bpy.data.objects.get(cam.name)
        if cam_obj is None:
            raise RuntimeError(
                f"[StructuredLight] No Blender object named '{cam.name}' "
                f"found in the scene. Available objects: "
                f"{[o.name for o in bpy.data.objects]}"
            )
        if cam_obj.type != "CAMERA":
            raise RuntimeError(
                f"[StructuredLight] Object '{cam.name}' is of type "
                f"'{cam_obj.type}', expected 'CAMERA'."
            )
 
        spot_size_rad = math.radians(self.spot_size_deg)
 
        # Each entry: (name, local_pos (x,y,z), local_rot_euler (rx,ry,rz) deg)
        # Camera local axes: +X right, +Y up, -Z into scene.
        # Outer lights are offset in the local XY plane and canted outward.
        offset_m = self.offset_m
        cant_deg = self.cant_deg
        light_specs = [
            ("SL_centre", ( 0,  0, 0), ( 0,  0, 0)),
            ("SL_top",    ( 0,  offset_m, 0), (-cant_deg,  0, 0)),  # pitch beam upward
            ("SL_bottom", ( 0, -offset_m, 0), ( cant_deg,  0, 0)),  # pitch beam downward
            ("SL_right",  ( offset_m,  0, 0), ( 0,  cant_deg, 0)),  # yaw beam rightward
            ("SL_left",   (-offset_m,  0, 0), ( 0, -cant_deg, 0)),  # yaw beam leftward
        ]
 
        for name, (lx, ly, lz), (rx, ry, rz) in light_specs:
 
            existing_obj  = bpy.data.objects.get(name)
            existing_data = bpy.data.lights.get(name)
 
            if existing_obj is not None and existing_data is not None:
                # ── Update in-place ───────────────────────────────────
                existing_data.color    = self.color
                existing_data.energy   = self.energy
                existing_data.spot_size  = spot_size_rad
                existing_data.spot_blend = 0.05
 
                existing_obj.location       = (lx, ly, lz)
                existing_obj.rotation_euler = (
                    math.radians(rx),
                    math.radians(ry),
                    math.radians(rz),
                )
                # Re-apply parent in case it changed
                if existing_obj.parent != cam_obj:
                    existing_obj.parent = cam_obj
                    existing_obj.matrix_parent_inverse = (
                        cam_obj.matrix_world.inverted()
                    )
 
            else:
                # ── Create from scratch ───────────────────────────────
                light_data             = bpy.data.lights.new(name=name, type="SPOT")
                light_data.color       = self.color
                light_data.energy      = self.energy
                light_data.spot_size   = spot_size_rad
                light_data.spot_blend  = 0.05
                light_data.use_shadow  = True
 
                light_obj              = bpy.data.objects.new(name, light_data)
                bpy.context.scene.collection.objects.link(light_obj)
 
                light_obj.location       = (lx, ly, lz)
                light_obj.rotation_euler = (
                    math.radians(rx),
                    math.radians(ry),
                    math.radians(rz),
                )
                light_obj.parent                = cam_obj
                light_obj.matrix_parent_inverse = cam_obj.matrix_world.inverted()
 
                # Start hidden – enabled only during process_one()
                light_obj.hide_render   = True
                light_obj.hide_viewport = True
 
        self._lights_created = True
        print(f"[StructuredLight] Lights ready, parented to '{cam_obj.name}'.")
 
    # ------------------------------------------------------------------
    # Corrected teardown()  –  only removes the five SL_ objects
    # ------------------------------------------------------------------
 
    def teardown(self):
        """Remove only the five SL_ light objects from the scene.
 
        All other scene lights are left completely untouched.
        """
        import bpy
        removed = []
        for name in self._LIGHT_NAMES:
            obj = bpy.data.objects.get(name)
            if obj is not None:
                bpy.data.objects.remove(obj, do_unlink=True)
                removed.append(name)
            ld = bpy.data.lights.get(name)
            if ld is not None:
                bpy.data.lights.remove(ld)
        self._lights_created = False
        print(f"[StructuredLight] Removed: {removed}")
    # ------------------------------------------------------------------
    # Main per-frame entry point
    # ------------------------------------------------------------------

    def process_one(self, state, index: int):
        """Render one structured-light image for the current frame.

        Enables the projector lights, renders the scene, saves the image,
        then disables the lights again so they do not affect other sensors.

        Call this after ENV.PositionAll() – the lights inherit the updated
        camera pose automatically via Blender's parent relationship.

        Args:
            state: corto State object (carries output_path).
            index (int): frame index used to name the output file.
        """
        if not self._lights_created:
            raise RuntimeError(
                "[StructuredLight] Call setup() before process_one()."
            )

        import bpy

        out_dir = os.path.join(state.path["output_path"], "structured_light", "images")
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, f"{index:06d}.png")

        try:
            # ── Enable lights ─────────────────────────────────────────
            self._set_lights_visible(True)

            # ── Override render output path ───────────────────────────
            scene = bpy.context.scene
            prev_path        = scene.render.filepath
            prev_format      = scene.render.image_settings.file_format
            prev_use_file    = scene.render.use_file_extension

            scene.render.filepath                      = out_path
            scene.render.image_settings.file_format   = "PNG"
            scene.render.use_file_extension            = False

            # ── Render ────────────────────────────────────────────────
            bpy.ops.render.render(write_still=True)

            # ── Restore render settings ───────────────────────────────
            scene.render.filepath                    = prev_path
            scene.render.image_settings.file_format  = prev_format
            scene.render.use_file_extension          = prev_use_file

        finally:
            # Always disable lights even if render raised an exception
            self._set_lights_visible(True)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _resolve_z_offset(self) -> float:
        """Return the current projector Z offset in metres.

        Uses fractional mode if projector_distance_frac is set and a
        target object is available; otherwise uses projector_distance_m.
        """
        if self.projector_distance_frac is not None and self._target_name:
            return self._cam_target_distance() * self.projector_distance_frac
        return self.projector_distance_m

    def _cam_target_distance(self) -> float:
        """Return the current Euclidean distance from camera to target (metres)."""

        cam_obj    = bpy.data.objects.get(self._cam_name)
        target_obj = bpy.data.objects.get(self._target_name)

        if cam_obj is None or target_obj is None:
            return 0.0

        cam_pos    = cam_obj.matrix_world.translation
        target_pos = target_obj.matrix_world.translation
        return (target_pos - cam_pos).length

    def _update_fractional_positions(self):
        """Reposition all SL_ lights along the optical axis for this frame."""
        cam_obj  = bpy.data.objects.get(self._cam_name)
        if cam_obj is None:
            return
        z_offset = self._resolve_z_offset()
        for name, (lx, ly, lz), (rx, ry, rz) in self._light_specs(z_offset):
            obj = bpy.data.objects.get(name)
            if obj is not None:
                obj.location       = (lx, ly, lz)
                obj.rotation_euler = (
                    math.radians(rx),
                    math.radians(ry),
                    math.radians(rz),
                )
                
    def _set_lights_visible(self, visible: bool):
        """Enable or disable all structured-light objects in the scene."""
        for name in self._LIGHT_NAMES:
            obj = bpy.data.objects.get(name)
            if obj is not None:
                obj.hide_render   = not visible
                obj.hide_viewport = not visible

    def _remove_lights(self):
        """Delete all structured-light objects and their data blocks."""
        for name in self._LIGHT_NAMES:
            obj = bpy.data.objects.get(name)
            if obj is not None:
                bpy.data.objects.remove(obj, do_unlink=True)
            ld = bpy.data.lights.get(name)
            if ld is not None:
                bpy.data.lights.remove(ld)

    def _load_from_dict(self, d: dict):
        for k in self._DEFAULTS:
            if k in d:
                setattr(self, k, d[k])