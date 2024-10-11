from __future__ import annotations
from typing import Any, List, Mapping, Optional, Tuple, Union, overload

import bpy
import os
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
