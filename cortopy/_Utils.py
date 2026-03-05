from __future__ import annotations
import sys
from typing import Any, List, Mapping, Optional, Tuple, Union, overload

import bpy
import os
import numpy as np
import matplotlib.pyplot as plt
import subprocess
import shutil
import cortopy as corto
from datetime import datetime

class Utils:
    """
    Utils class
    """
    # *************************************************************************
    # *     Constructors & Destructors
    # *************************************************************************

    def __init__(self) -> None:
        """
        Constructor for the Utility class
        """

    # Istance methods
    @staticmethod
    def clean_scene(): #TODO: workout if this should be a static method of Environment class
        """
        Delete all existing objects from a scene
        """
        # Deselect all objects
        bpy.ops.object.select_all(action="DESELECT")
        # Select all objects
        bpy.ops.object.select_all(action="SELECT")
        # Delete all selected objects
        bpy.ops.object.delete()

    @staticmethod
    def GenerateTimestamp() -> None:
        """Generate a timestamp string as Year-Month-Day-HH-MM-SS, for random saving purposes

        Returns:
            str: timestamp string
        """        
        timestamp = datetime.now()
        formatted_timestamp = timestamp.strftime("%Y_%m_%d_%H_%M_%S")
        return formatted_timestamp

    @staticmethod
    def save_blend(state: corto.State, blend_name = 'debug') -> None:
        """Method to save a .blend file

        Args:
            state (corto.State): name of the .blend file
            name (str, optional): name of the .blend file to save. Defaults to 'debug'.
        """
        #TODO: Add the automatic disabling of the backup .blend1 files
        bpy.context.preferences.filepaths.save_version = 0
        blend_dir = os.path.join(state.path["output_path"], "blend")
        if not os.path.exists(blend_dir):
            os.makedirs(blend_dir)
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(blend_dir, blend_name + ".blend"))

    @staticmethod
    def mkdir(folder_path):
        """
        Creates a folder at the specified path if it doesn't already exist.
        
        Args:
            folder_path (str): The path of the folder to be created.
        """
        try:
            os.makedirs(folder_path, exist_ok=True)
            print(f"Folder created at: {folder_path}")
        except Exception as e:
            print(f"Error creating folder: {e}")   

    @staticmethod
    def visualize_depth_map(path: str):
        """
        Visualize a depth map saved as a .txt 
        
        Args:
            path (str): The path of the .txt depth map
        """
        depth = np.loadtxt(path)
        # Define a threshold above which values are invalid
        invalid_threshold = 0   # e.g., anything >= 1e9 is "no data"
        # Mask the depth map
        masked_depth = np.ma.masked_where(depth == invalid_threshold, depth)
        # Compute min and max of the masked depth
        dmin = np.min(masked_depth)
        dmax = np.max(masked_depth)

        plt.figure()
        plt.imshow(masked_depth, vmin = dmin, vmax = dmax, cmap="inferno", origin="lower")
        plt.colorbar()
        plt.show()
        return plt
    
    @staticmethod
    def long_run_override(idx_start:int, idx_end:int, script_path: str):
        """
        This method is used to override the run for a rendering script to allow for batch running. 
        
        Args:
            idx_start (int): first index to be used in the renderings
            idx_end (int): last index to be used in the renderings
            script_path (str): path of the script to run (e.g. "tutorials/S09_Frankenstein_Asteroids.py")

        NOTE: in order for this method to be effective, you need to put the following function and override the idx_start and idx_end used for the renderings

        import sys, argparse
        def _override_range_via_cli(default_start, default_end):
            argv = sys.argv
            if "--" in argv: # Blender passes script args after a literal "--".
                argv = argv[argv.index("--") + 1:]
            else:
                argv = argv[1:]
            parser = argparse.ArgumentParser(add_help=False)
            parser.add_argument("--start", type=int, dest="start")
            parser.add_argument("--end",   type=int, dest="end")
            # parse_known_args so we ignore any extra scenario flags you may add later
            ns, _ = parser.parse_known_args(argv)
            s = default_start if ns.start is None else ns.start
            e = default_end   if ns.end   is None else ns.end
            if e < s:
                raise ValueError(f"--end ({e}) must be >= --start ({s})")
            print(f" Render range: idx_start={s}, idx_end={e}")
        return s, e

        """
        print(f"Rendering {idx_start}..{idx_end}")
        cmd = ["python", script_path,
            "--start", str(idx_start), "--end", str(idx_end)]

        r = subprocess.run(" ".join(cmd), shell=True)
        if r.returncode != 0:
            raise SystemExit(f"Batch failed: {idx_start}-{idx_end}")

    @staticmethod

    @staticmethod
    def move_files_by_type(src_dir:str, dest_dir:str, startwith: str, endswith:str = ".png", max_n_files:float = 1e8):
        """ 
        Detect all .png files in src_dir and move them to dest_dir.
        Prints progress updates and the total number of files moved.

        Args:
            src_dir (str): source directory
            dest_dir (str): last index to be used in the renderings
            extension (str): file extension to search for

        """
        # Create destination directory if it doesn't exist
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        # Collect all .png files
        if startwith:
            png_files = [f for f in os.listdir(src_dir) if f.lower().endswith(endswith) and f.lower().startswith(startwith)]
        else:
            png_files = [f for f in os.listdir(src_dir) if f.lower().endswith(endswith)]

        # Add a ceiling on the number of files to move (the first max_n_files)
        png_files = png_files[0:int(max_n_files)]
        total = len(png_files)
        if total == 0:
            print("No {extension} files found.")
            return
        
        png_files = png_files[0:int(max_n_files)]
        # Move files with progress index
        for idx, filename in enumerate(png_files, start=1):
            src_path = os.path.join(src_dir, filename)
            dest_path = os.path.join(dest_dir, filename)
            shutil.move(src_path, dest_path)
            print(f"[{idx}/{total}] Moved: {filename} -> {dest_dir}")
        print(f"\n✅ Done! {total} .png files moved to '{dest_dir}'")

    def run_script(script_name: str):

        env = os.environ.copy()
        env["MPLBACKEND"] = "Agg"   # disables GUI plots

        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            env=env
        )

        assert result.returncode == 0, (
            f"\nScript failed: {script_name}"
            f"\nSTDOUT:\n{result.stdout}"
            f"\nSTDERR:\n{result.stderr}"
        )