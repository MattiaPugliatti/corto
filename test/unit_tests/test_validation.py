"""
Unit tests for the input-validation guards in Camera and Body constructors.
bpy and related Blender modules are stubbed via sys.modules before import so
that the classes can be instantiated in a plain Python environment.
The TypeError checks fire before any bpy call, so the mocks never need
to behave like real Blender objects.
"""
from __future__ import annotations

import os
import sys
from unittest.mock import MagicMock

import pytest

for _mod in ("bpy", "mathutils", "imageio", "imageio.v3"):
    sys.modules.setdefault(_mod, MagicMock())

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import pytest
from cortopy._Camera import Camera
from cortopy._Body import Body


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _camera_props(**overrides) -> dict:
    base = {
        "res_x": 512,
        "res_y": 512,
        "fov": 60.0,
        "film_exposure": 1.0,
        "sensor": "BW",
        "K": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
        "clip_start": 0.1,
        "clip_end": 1000.0,
        "bit_encoding": "8",
        "viewtransform": "Standard",
    }
    base.update(overrides)
    return base


def _body_props(**overrides) -> dict:
    base = {
        "pass_index": 1,
        "total_bounces": 4,
        "diffuse_bounces": 4,
        "glossy_bounces": 4,
        "transmission_bounces": 4,
        "volume_bounces": 0,
        "transparent_bounces": 8,
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# Camera validation
# ---------------------------------------------------------------------------

class TestCameraValidation:
    def test_float_res_x_raises_type_error(self):
        with pytest.raises(TypeError, match="integer"):
            Camera("CAM", _camera_props(res_x=512.0))

    def test_float_res_y_raises_type_error(self):
        with pytest.raises(TypeError, match="integer"):
            Camera("CAM", _camera_props(res_y=512.0))

    def test_string_res_x_raises_type_error(self):
        with pytest.raises(TypeError, match="integer"):
            Camera("CAM", _camera_props(res_x="512"))

    def test_string_res_y_raises_type_error(self):
        with pytest.raises(TypeError, match="integer"):
            Camera("CAM", _camera_props(res_y="512"))

    def test_both_float_raises_type_error(self):
        with pytest.raises(TypeError, match="integer"):
            Camera("CAM", _camera_props(res_x=512.0, res_y=512.0))


# ---------------------------------------------------------------------------
# Body validation
# ---------------------------------------------------------------------------

class TestBodyValidation:
    def test_float_pass_index_raises_type_error(self):
        with pytest.raises(TypeError):
            Body("BODY", _body_props(pass_index=1.0))

    def test_float_total_bounces_raises_type_error(self):
        with pytest.raises(TypeError):
            Body("BODY", _body_props(total_bounces=4.0))

    def test_float_diffuse_bounces_raises_type_error(self):
        with pytest.raises(TypeError):
            Body("BODY", _body_props(diffuse_bounces=4.0))

    def test_float_glossy_bounces_raises_type_error(self):
        with pytest.raises(TypeError):
            Body("BODY", _body_props(glossy_bounces=4.0))

    def test_float_transmission_bounces_raises_type_error(self):
        with pytest.raises(TypeError):
            Body("BODY", _body_props(transmission_bounces=4.0))

    def test_float_volume_bounces_raises_type_error(self):
        with pytest.raises(TypeError):
            Body("BODY", _body_props(volume_bounces=0.0))

    def test_float_transparent_bounces_raises_type_error(self):
        with pytest.raises(TypeError):
            Body("BODY", _body_props(transparent_bounces=8.0))

    def test_string_pass_index_raises_type_error(self):
        with pytest.raises(TypeError):
            Body("BODY", _body_props(pass_index="1"))

    def test_missing_key_uses_default_and_prints(self, capsys):
        props = _body_props()
        del props["total_bounces"]
        body = Body("BODY", props)
        assert body.total_bounces == 12
        assert "total_bounces" in capsys.readouterr().out

    def test_all_keys_missing_uses_all_defaults(self, capsys):
        body = Body("BODY", {})
        assert body.pass_index == 0
        assert body.total_bounces == 12
        assert body.diffuse_bounces == 4
        assert body.glossy_bounces == 4
        assert body.transmission == 12
        assert body.volume_bounces == 0
        assert body.transparent_bounces == 8

    def test_partial_properties_fills_missing_with_defaults(self, capsys):
        body = Body("BODY", {"pass_index": 2, "diffuse_bounces": 8})
        assert body.pass_index == 2
        assert body.diffuse_bounces == 8
        assert body.total_bounces == 12
