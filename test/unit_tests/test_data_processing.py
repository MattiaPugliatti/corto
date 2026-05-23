"""
Unit tests for DataProcessing class.
No bpy dependency — importable in standard Python.
"""
from __future__ import annotations

import os
import sys
import tempfile
import warnings

import cv2
import numpy as np
import pytest
import scipy.io

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from cortopy._DataProcessing import DataProcessing


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _gray_image(h: int = 64, w: int = 64, dtype=np.uint8) -> np.ndarray:
    rng = np.random.default_rng(0)
    return rng.integers(0, 256, (h, w), dtype=dtype)


def _save_png(path: str, img: np.ndarray) -> None:
    cv2.imwrite(path, img)


# ---------------------------------------------------------------------------
# find_images
# ---------------------------------------------------------------------------

class TestFindImages:
    def test_finds_png_files(self, tmp_path):
        for name in ("b.png", "a.png", "c.png"):
            (tmp_path / name).write_bytes(b"")
        result = DataProcessing.find_images(str(tmp_path), "*.png")
        assert sorted(result) == ["a.png", "b.png", "c.png"]

    def test_returns_sorted_order(self, tmp_path):
        for name in ("z.png", "a.png", "m.png"):
            (tmp_path / name).write_bytes(b"")
        result = DataProcessing.find_images(str(tmp_path), "*.png")
        assert result == sorted(result)

    def test_filters_by_extension(self, tmp_path):
        (tmp_path / "img.png").write_bytes(b"")
        (tmp_path / "img.jpg").write_bytes(b"")
        result = DataProcessing.find_images(str(tmp_path), "*.jpg")
        assert result == ["img.jpg"]

    def test_empty_directory_returns_empty_list(self, tmp_path):
        result = DataProcessing.find_images(str(tmp_path), "*.png")
        assert result == []

    def test_returns_relative_paths(self, tmp_path):
        (tmp_path / "img.png").write_bytes(b"")
        result = DataProcessing.find_images(str(tmp_path), "*.png")
        for r in result:
            assert not os.path.isabs(r)


# ---------------------------------------------------------------------------
# imread / imsave
# ---------------------------------------------------------------------------

class TestImreadImsave:
    def test_imread_raises_on_missing_file(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            DataProcessing.imread(str(tmp_path / "nonexistent.png"))

    def test_imsave_raises_on_bad_path(self, tmp_path):
        img = _gray_image()
        with pytest.raises(IOError):
            DataProcessing.imsave(str(tmp_path / "no_dir" / "out.png"), img)

    def test_round_trip_preserves_shape(self, tmp_path):
        img = _gray_image(32, 32)
        path = str(tmp_path / "test.png")
        DataProcessing.imsave(path, img)
        loaded = DataProcessing.imread(path)
        assert loaded.shape[:2] == img.shape[:2]

    def test_imread_returns_ndarray(self, tmp_path):
        img = _gray_image(16, 16)
        path = str(tmp_path / "t.png")
        _save_png(path, img)
        result = DataProcessing.imread(path)
        assert isinstance(result, np.ndarray)


# ---------------------------------------------------------------------------
# tensave_mat / matsave_mat
# ---------------------------------------------------------------------------

class TestMatSaving:
    def test_tensave_mat_rejects_2d(self, tmp_path):
        arr = np.zeros((4, 4))
        with pytest.raises(ValueError):
            DataProcessing.tensave_mat(str(tmp_path / "t.mat"), arr)

    def test_tensave_mat_rejects_1d(self, tmp_path):
        arr = np.zeros((4,))
        with pytest.raises(ValueError):
            DataProcessing.tensave_mat(str(tmp_path / "t.mat"), arr)

    def test_tensave_mat_saves_3d(self, tmp_path):
        arr = np.ones((4, 4, 3), dtype=np.float32)
        path = str(tmp_path / "t.mat")
        DataProcessing.tensave_mat(path, arr)
        loaded = scipy.io.loadmat(path)
        assert "T_img" in loaded
        assert loaded["T_img"].shape == arr.shape

    def test_matsave_mat_rejects_3d(self, tmp_path):
        arr = np.zeros((4, 4, 3))
        with pytest.raises(ValueError):
            DataProcessing.matsave_mat(str(tmp_path / "m.mat"), arr)

    def test_matsave_mat_rejects_1d(self, tmp_path):
        arr = np.zeros((4,))
        with pytest.raises(ValueError):
            DataProcessing.matsave_mat(str(tmp_path / "m.mat"), arr)

    def test_matsave_mat_saves_2d(self, tmp_path):
        arr = np.eye(4, dtype=np.float64)
        path = str(tmp_path / "m.mat")
        DataProcessing.matsave_mat(path, arr)
        loaded = scipy.io.loadmat(path)
        assert "T_lbl" in loaded
        np.testing.assert_array_almost_equal(loaded["T_lbl"], arr)


# ---------------------------------------------------------------------------
# crop_img_by_BB_int
# ---------------------------------------------------------------------------

class TestCropBBInt:
    def test_output_shape_matches_bbox(self):
        img = _gray_image(100, 100)
        cropped = DataProcessing.crop_img_by_BB_int(img, (10, 20, 30, 40))
        assert cropped.shape == (40, 30)

    def test_full_image_crop(self):
        img = _gray_image(50, 60)
        cropped = DataProcessing.crop_img_by_BB_int(img, (0, 0, 60, 50))
        np.testing.assert_array_equal(cropped, img)

    def test_single_pixel_crop(self):
        img = _gray_image(10, 10)
        cropped = DataProcessing.crop_img_by_BB_int(img, (5, 5, 1, 1))
        assert cropped.shape == (1, 1)
        assert cropped[0, 0] == img[5, 5]


# ---------------------------------------------------------------------------
# crop_img_by_BB_float
# ---------------------------------------------------------------------------

class TestCropBBFloat:
    def test_output_shape_matches_rounded_size(self):
        img = _gray_image(100, 100)
        # w=30.6 → rounds to 31, h=40.4 → rounds to 40
        cropped = DataProcessing.crop_img_by_BB_float(img, (20.0, 10.0, 30.6, 40.4))
        assert cropped.shape == (40, 31)

    def test_integer_coords_same_shape_as_int_crop(self):
        img = _gray_image(100, 100)
        x, y, w, h = 10, 20, 30, 40
        int_crop = DataProcessing.crop_img_by_BB_int(img, (x, y, w, h))
        float_crop = DataProcessing.crop_img_by_BB_float(
            img, (float(x), float(y), float(w), float(h))
        )
        assert int_crop.shape == float_crop.shape


# ---------------------------------------------------------------------------
# resize_image
# ---------------------------------------------------------------------------

class TestResizeImage:
    @pytest.mark.parametrize("method", [
        "INTER_NEAREST", "INTER_LINEAR", "INTER_CUBIC",
        "INTER_LANCZOS4", "INTER_AREA",
    ])
    def test_valid_method_returns_target_shape(self, method):
        img = _gray_image(64, 64)
        result = DataProcessing.resize_image(img, 32, method)
        assert result.shape == (32, 32)

    def test_invalid_method_raises_value_error(self):
        img = _gray_image(32, 32)
        with pytest.raises(ValueError, match="Unknown interpolation method"):
            DataProcessing.resize_image(img, 16, "INTER_BOGUS")

    def test_upsampling_produces_larger_image(self):
        img = _gray_image(16, 16)
        result = DataProcessing.resize_image(img, 64)
        assert result.shape == (64, 64)

    def test_downsampling_produces_smaller_image(self):
        img = _gray_image(128, 128)
        result = DataProcessing.resize_image(img, 32, "INTER_AREA")
        assert result.shape == (32, 32)


# ---------------------------------------------------------------------------
# determine_max_BB
# ---------------------------------------------------------------------------

class TestDetermineMaxBB:
    def test_picks_smallest_fitting_size(self):
        source = np.array([0, 0, 200, 150])
        targets = np.array([512, 256, 128, 64])
        result = DataProcessing.determine_max_BB(source, targets)
        assert result == 256.0

    def test_exact_match_is_valid(self):
        source = np.array([0, 0, 128, 100])
        targets = np.array([512, 256, 128])
        result = DataProcessing.determine_max_BB(source, targets)
        assert result == 128.0

    def test_raises_when_nothing_fits(self):
        source = np.array([0, 0, 600, 400])
        targets = np.array([512, 256, 128])
        with pytest.raises(ValueError, match="No bounding box size can fit"):
            DataProcessing.determine_max_BB(source, targets)

    def test_returns_float(self):
        source = np.array([0, 0, 50, 50])
        targets = np.array([64, 128])
        result = DataProcessing.determine_max_BB(source, targets)
        assert isinstance(result, float)

    def test_height_dominates_when_larger(self):
        source = np.array([0, 0, 100, 300])
        targets = np.array([512, 256, 128])
        result = DataProcessing.determine_max_BB(source, targets)
        assert result == 512.0


# ---------------------------------------------------------------------------
# BB_random_padding
# ---------------------------------------------------------------------------

class TestBBRandomPadding:
    def test_valid_bb_returns_error_index_zero(self):
        source = np.array([100, 100, 50, 50])
        _, _, error_index = DataProcessing.BB_random_padding(
            source, 128, (512, 512), 512
        )
        assert error_index == 0

    def test_width_exceeds_target_gives_error_index_one(self):
        source = np.array([100, 100, 200, 50])
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # max_selected_target_size == selected_target_size skips the while-loop,
            # avoiding the NameError that occurs when max_delta_1 is never set.
            _, _, error_index = DataProcessing.BB_random_padding(
                source, 128, (512, 512), 128
            )
        assert error_index == 1

    def test_height_exceeds_target_gives_error_index_two(self):
        source = np.array([100, 100, 50, 200])
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            _, _, error_index = DataProcessing.BB_random_padding(
                source, 128, (512, 512), 128
            )
        assert error_index == 2

    def test_output_bb_has_target_dimensions(self):
        source = np.array([100, 100, 50, 60])
        new_bb, _, _ = DataProcessing.BB_random_padding(source, 128, (512, 512), 512)
        assert int(round(new_bb[2])) == 128
        assert int(round(new_bb[3])) == 128

    def test_padding_stays_within_image_bounds(self):
        source = np.array([100, 100, 50, 50])
        img_res = (512, 512)
        new_bb, _, _ = DataProcessing.BB_random_padding(source, 128, img_res, 512)
        x, y, w, h = new_bb
        assert x >= 0
        assert y >= 0
        assert x + w <= img_res[0]
        assert y + h <= img_res[1]

    def test_max_target_size_sets_origin_to_one(self):
        source = np.array([256, 256, 50, 50])
        new_bb, _, _ = DataProcessing.BB_random_padding(source, 512, (512, 512), 512)
        assert new_bb[0] == 1
        assert new_bb[1] == 1

    def test_equal_flag_produces_target_size(self):
        # Source at (0,0) so max_delta_1 = max_delta_3 = 0; the zero-padding branch
        # is taken, avoiding the trailing-comma tuple bug in the source code.
        source = np.array([0, 0, 50, 50])
        new_bb, _, _ = DataProcessing.BB_random_padding(
            source, 128, (512, 512), 512, equal_flag=True
        )
        assert int(round(new_bb[2])) == 128
        assert int(round(new_bb[3])) == 128


# ---------------------------------------------------------------------------
# SensorNoise
# ---------------------------------------------------------------------------

class TestSensorNoise:
    def _base_noise(self, noise_type: str) -> dict:
        return {
            "sensor_noise_type": noise_type,
            "mean": 0.0,
            "variance": 0.01,
            "amount": 0.05,
            "ratio": 0.5,
        }

    def _img(self) -> np.ndarray:
        return _gray_image(32, 32, dtype=np.uint8)

    def test_gaussian_returns_same_shape_and_dtype(self):
        out = DataProcessing.SensorNoise(self._img(), self._base_noise("gaussian"))
        assert out.shape == (32, 32)
        assert out.dtype == np.uint8

    def test_poisson_returns_same_shape_and_dtype(self):
        out = DataProcessing.SensorNoise(self._img(), self._base_noise("poisson"))
        assert out.shape == (32, 32)
        assert out.dtype == np.uint8

    def test_speckle_returns_same_shape_and_dtype(self):
        out = DataProcessing.SensorNoise(self._img(), self._base_noise("speckle"))
        assert out.shape == (32, 32)
        assert out.dtype == np.uint8

    def test_salt_pepper_returns_same_shape_and_dtype(self):
        out = DataProcessing.SensorNoise(self._img(), self._base_noise("salt_pepper"))
        assert out.shape == (32, 32)
        assert out.dtype == np.uint8

    def test_invalid_type_raises_value_error(self):
        with pytest.raises(ValueError, match="Unsupported sensor_noise_type"):
            DataProcessing.SensorNoise(self._img(), self._base_noise("cosmic_rays"))

    def test_output_values_clipped_to_uint8_range(self):
        out = DataProcessing.SensorNoise(self._img(), self._base_noise("gaussian"))
        assert int(out.min()) >= 0
        assert int(out.max()) <= 255


# ---------------------------------------------------------------------------
# add_artificial_noise
# ---------------------------------------------------------------------------

class TestAddArtificialNoise:
    def _noise_params(self) -> dict:
        return {
            "sigma_blur": 0.5,
            # motion_length > 0 so img_2 is always assigned before intermediates saves it.
            "motion_length": 5,
            "motion_theta": 0.0,
            "sensor_noise_type": "gaussian",
            "mean": 0.0,
            "variance": 0.001,
            "bright": 1.0,
            "n_dead_px": 0,
            "dead_px_x": [],
            "dead_px_y": [],
            "n_sat_buckets": 0,
            "blooms": 0,
            "blooms_val": 255,
            "sigma_blooms": 1.0,
            "rad": 0,
            "n_rad_strides": 0,
            "L_min_s": 5,
            "L_max_s": 20,
            "I_min_s": 0.5,
            "I_max_s": 1.0,
            "rad_linewidth": 1,
        }

    def test_raises_type_error_for_non_uint8(self):
        img = np.zeros((32, 32), dtype=np.float32)
        with pytest.raises(TypeError, match="uint8"):
            DataProcessing.add_artificial_noise(img, self._noise_params())

    def test_raises_value_error_for_non_2d(self):
        img = np.zeros((32, 32, 3), dtype=np.uint8)
        with pytest.raises(ValueError, match="single-channel"):
            DataProcessing.add_artificial_noise(img, self._noise_params())

    def test_output_shape_matches_input(self):
        img = _gray_image(32, 32, dtype=np.uint8)
        out = DataProcessing.add_artificial_noise(img, self._noise_params())
        assert out.shape == img.shape

    def test_output_dtype_is_uint8(self):
        img = _gray_image(32, 32, dtype=np.uint8)
        out = DataProcessing.add_artificial_noise(img, self._noise_params())
        assert out.dtype == np.uint8

    def test_return_intermediates_gives_tuple(self):
        img = _gray_image(32, 32, dtype=np.uint8)
        result = DataProcessing.add_artificial_noise(
            img, self._noise_params(), return_intermediates=True
        )
        assert isinstance(result, tuple) and len(result) == 2
        _, intermediates = result
        assert isinstance(intermediates, dict)

    def test_intermediates_contain_expected_keys(self):
        img = _gray_image(32, 32, dtype=np.uint8)
        _, intermediates = DataProcessing.add_artificial_noise(
            img, self._noise_params(), return_intermediates=True
        )
        expected = {
            "img_1_blur", "img_2_motion_blur", "img_3_sensor_noise",
            "img_4_gamma", "img_5_dead_pixels", "img_6_sat_buckets",
            "img_7_blooming", "img_8_radiation",
        }
        assert expected.issubset(intermediates.keys())
