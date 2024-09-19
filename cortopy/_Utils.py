
from __future__ import annotations

import bpy 
import os
import cortopy as corto

from typing import (Any, List, Mapping, Optional, Tuple, Union, overload)
from datetime import datetime
class Utils:
    """
    Utils class
    """
    @classmethod
    def exampleClass(cls, arg1: int, arg2: int) -> Tuple[int, int]: # type hinting
        """
        Description of the method

        Args:
            arg 1: description
            arg 2: description

        Raises:
            which kind of exceptions
        
        Returns:
            arg 1: descritpion
            arg 2: description

        See also:
            additional function and modules imported

        """

    @staticmethod # decorator for static methods
    def exampleStatic(arg1: int, arg2: int) -> Tuple[int, int]: # type hinting
        """
        Description of the method

        Args:
            arg 1: description
            arg 2: description

        Raises:
            which kind of exceptions
        
        Returns:
            arg 1: descritpion
            arg 2: description

        See also:
            additional function and modules imported

        """

    # *************************************************************************
    # *     Constructors & Destructors
    # *************************************************************************

    def __init__(self) -> None:
        """
        Constructor for the Utility class
        """

    # Istance methods
    # imo this should be static method of Environment class
    @staticmethod
    def clean_scene():
        """
        Delete all existing objects from a scene
        """
        # Deselect all objects
        bpy.ops.object.select_all(action='DESELECT')
        # Select all objects
        bpy.ops.object.select_all(action='SELECT')
        # Delete all selected objects
        bpy.ops.object.delete()

    @staticmethod
    def GenerateTimestamp() -> None:
        timestamp = datetime.now()
        formatted_timestamp = timestamp.strftime("%Y_%m_%d_%H_%M_%S")
        return formatted_timestamp
    
    @staticmethod
    def save_blend(state:corto.State) -> None:
        """Method to save a .blend file

        Args:
            state (corto.St): name of the .blend file
        """
        # Disable the creation of backup files
        bpy.context.preferences.filepaths.save_version = 0
        blend_dir = os.path.join(state.path["output_path"],'blend')
        if not os.path.exists(blend_dir):
            os.makedirs(blend_dir)
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(blend_dir,'debug.blend'))
        