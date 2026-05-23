import sys, os
sys.path.append(os.getcwd())
import cortopy as corto


def test_basics_GenerateCloud_input():
    corto.Utils.run_script("tutorials/basics_GenerateCloud_input.py")


def test_basics_GeneratePA_input():
    corto.Utils.run_script("tutorials/basics_GeneratePA_input.py")


def test_advanced_CIL_OpenLoop():
    corto.Utils.run_script("tutorials/advanced_CIL_OpenLoop.py")


def test_advanced_advanced_CIL_ClosedLoop():
    corto.Utils.run_script("tutorials/advanced_CIL_ClosedLoop.py")


def test_S00_Calibration():
    corto.Utils.run_script("tutorials/S00_Calibration.py")


def test_S01a_Eros():
    corto.Utils.run_script("tutorials/S01a_Eros.py")


def test_S01b_Eros():
    corto.Utils.run_script("tutorials/S01b_Eros.py")


def test_S02_Itokawa():
    corto.Utils.run_script("tutorials/S02_Itokawa.py")


def test_S03_Apophis():
    corto.Utils.run_script("tutorials/S03_Apophis.py")


def test_S04_Bennu():
    corto.Utils.run_script("tutorials/S04_Bennu.py")


def test_S05a_Didymos_Milani():
    corto.Utils.run_script("tutorials/S05a_Didymos_Milani.py")


def test_S05b_Didymos():
    corto.Utils.run_script("tutorials/S05b_Didymos.py")


def test_S06a_Moon():
    corto.Utils.run_script("tutorials/S06a_Moon.py")


def test_S06b_Moon():
    corto.Utils.run_script("tutorials/S06b_Moon.py")


def test_S07_Mars_Phobos_Deimos():
    corto.Utils.run_script("tutorials/S07a_Mars_Phobos_Deimos.py")


def test_S07_Mars_Phobos_Deimos():
    corto.Utils.run_script("tutorials/S07b_Mars_Phobos_Deimos_optimized.py")


def test_S08_Earth():
    corto.Utils.run_script("tutorials/S08_Earth.py")


def test_S09_Frankenstein_Asteroids():
    corto.Utils.run_script("tutorials/S09_Frankenstein_Asteroids.py")


def test_S10_Spacecraft():
    corto.Utils.run_script("tutorials/S10_Spacecraft.py")

## RUN THESE AFTER AN OUTPUT IS GENERATED FROM THE TUTORIALS

def test_basics_Visualize_depth_from_exr():
    corto.Utils.run_script("tutorials/basics_Visualize_depth_from_exr.py")


def test_basics_Visualize_depth_from_txt():
    corto.Utils.run_script("tutorials/basics_Visualize_depth_from_txt.py")


def test_basics_Visualize_lidar_out():
    corto.Utils.run_script("tutorials/basics_Visualize_lidar_out.py")


def test_basics_visualize_tof_out():
    corto.Utils.run_script("tutorials/basics_visualize_tof_out.py")
