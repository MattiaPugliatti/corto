
from __future__ import annotations

import bpy 
import os

from typing import (Any, List, Mapping, Optional, Tuple, Union, overload)

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
    def save_blend(name: str) -> None:
        """Method to save a .blend file

        Args:
            name (str): name of the .blend file
        """
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join('output', name + '.blend'))
        