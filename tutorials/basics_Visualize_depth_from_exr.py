import sys
import os
sys.path.append(os.getcwd())
import cortopy as corto

print(os.getcwd())

# Define the path of your depth map (the .exr one). You could have generated it with one of the tutorials
depth_map_path = "output/S10_Spacecraft/depth_exr/000000.exr"

corto.Utils.visualize_depth_exr(depth_map_path)