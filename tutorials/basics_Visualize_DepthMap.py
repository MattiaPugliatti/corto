import sys
import os
sys.path.append(os.getcwd())
import cortopy as corto

# Define the path of your depth map (the .txt one). You could have generated it with one of the tutorials
depth_map_path = "/Users/mapu7335/Repos/corto/corto/output/S01a_Eros/depth_txt/000001.txt"
# depth_map_path = "/Users/mapu7335/Repos/corto/corto/output/S02_Itokawa/depth_txt/000001.txt"
# depth_map_path = "/Users/mapu7335/Repos/corto/corto/output/S04_Bennu/depth_txt/000001.txt"
# depth_map_path = "/Users/mapu7335/Repos/corto/corto/output/S05_Didymos/depth_txt/000001.txt"
# depth_map_path = "/Users/mapu7335/Repos/corto/corto/output/S05_Didymos_Milani/depth_txt/000001.txt"
# depth_map_path = "/Users/mapu7335/Repos/corto/corto/output/S06_Moon/depth_txt/000001.txt"
# depth_map_path = "/Users/mapu7335/Repos/corto/corto/output/S07_Mars_Phobos_Deimos/depth_txt/000001.txt"

corto.Utils.visualize_depth_map(depth_map_path)