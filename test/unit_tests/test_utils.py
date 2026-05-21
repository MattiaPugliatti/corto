"""
Unit tests for Utils methods that have no real bpy logic.
bpy and related Blender modules are stubbed via sys.modules before import.
"""
from __future__ import annotations

import os
import re
import sys
from unittest.mock import MagicMock

# Stub every Blender-only module so the import chain succeeds.
for _mod in ("bpy", "mathutils", "imageio", "imageio.v3"):
    sys.modules.setdefault(_mod, MagicMock())

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from cortopy._Utils import Utils


# ---------------------------------------------------------------------------
# GenerateTimestamp
# ---------------------------------------------------------------------------

class TestGenerateTimestamp:
    _PATTERN = re.compile(r"^\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}$")

    def test_returns_string(self):
        assert isinstance(Utils.GenerateTimestamp(), str)

    def test_matches_expected_format(self):
        ts = Utils.GenerateTimestamp()
        assert self._PATTERN.match(ts), f"Unexpected format: {ts!r}"

    def test_two_calls_are_strings(self):
        # Both calls should succeed without error
        t1 = Utils.GenerateTimestamp()
        t2 = Utils.GenerateTimestamp()
        assert isinstance(t1, str)
        assert isinstance(t2, str)


# ---------------------------------------------------------------------------
# mkdir
# ---------------------------------------------------------------------------

class TestMkdir:
    def test_creates_directory(self, tmp_path):
        new_dir = str(tmp_path / "new_folder")
        assert not os.path.exists(new_dir)
        Utils.mkdir(new_dir)
        assert os.path.isdir(new_dir)

    def test_no_error_if_already_exists(self, tmp_path):
        existing = str(tmp_path / "exists")
        os.makedirs(existing)
        Utils.mkdir(existing)  # should not raise
        assert os.path.isdir(existing)

    def test_creates_nested_directories(self, tmp_path):
        nested = str(tmp_path / "a" / "b" / "c")
        Utils.mkdir(nested)
        assert os.path.isdir(nested)


# ---------------------------------------------------------------------------
# move_files_by_type
# ---------------------------------------------------------------------------

class TestMoveFilesByType:
    def _populate(self, directory, names):
        for name in names:
            (directory / name).write_bytes(b"x")

    def test_moves_matching_files(self, tmp_path):
        src = tmp_path / "src"
        dst = tmp_path / "dst"
        src.mkdir()
        self._populate(src, ["frame_0001.png", "frame_0002.png"])
        Utils.move_files_by_type(str(src), str(dst), startwith="frame", endswith=".png")
        assert len(list(dst.iterdir())) == 2
        assert len(list(src.iterdir())) == 0

    def test_leaves_non_matching_files(self, tmp_path):
        src = tmp_path / "src"
        dst = tmp_path / "dst"
        src.mkdir()
        self._populate(src, ["frame_0001.png", "depth_0001.exr"])
        Utils.move_files_by_type(str(src), str(dst), startwith="frame", endswith=".png")
        assert (src / "depth_0001.exr").exists()
        assert not (src / "frame_0001.png").exists()

    def test_max_n_files_cap(self, tmp_path):
        src = tmp_path / "src"
        dst = tmp_path / "dst"
        src.mkdir()
        self._populate(src, [f"img_{i:04d}.png" for i in range(10)])
        Utils.move_files_by_type(str(src), str(dst), startwith="img", endswith=".png", max_n_files=3)
        assert len(list(dst.iterdir())) == 3

    def test_empty_source_does_not_raise(self, tmp_path):
        src = tmp_path / "src"
        dst = tmp_path / "dst"
        src.mkdir()
        Utils.move_files_by_type(str(src), str(dst), startwith="", endswith=".png")
        # dst may or may not be created, but no exception should propagate

    def test_creates_dest_if_missing(self, tmp_path):
        src = tmp_path / "src"
        src.mkdir()
        dst = tmp_path / "new_dst"
        self._populate(src, ["img_0001.png"])
        assert not dst.exists()
        Utils.move_files_by_type(str(src), str(dst), startwith="img", endswith=".png")
        assert dst.exists()
