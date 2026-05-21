"""
Before running this script, you must have generated a depth map from one of the tutorials.
"""

import sys
import os
sys.path.append(os.getcwd())
import cortopy as corto

# Define the path of your depth map (the .exr one). You could have generated it with one of the tutorials
depth_map_path = "output/S01_Eros/depth_exr/000000.exr"
# depth_map_path = "output/S02_Itokawa/depth_exr/000000.exr"
# depth_map_path = "output/S04_Bennu/depth_exr/000000.exr"
# depth_map_path = "output/S05a_Didymos_Milani/depth_exr/000000.exr"
# depth_map_path = "output/S05b_Didymos/depth_exr/000000.exr"
# depth_map_path = "output/S06a_Moon/depth_exr/000000.exr"
# depth_map_path = "output/S06b_Moon/moon_10_20E_10_20N/depth_exr/000000.exr"
# depth_map_path = "output/S10_Spacecraft/depth_exr/000000.exr"

corto.Utils.visualize_depth_exr(depth_map_path)