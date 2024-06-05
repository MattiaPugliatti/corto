
from __future__ import annotations

import numpy as np
import bpy 
import mathutils

from typing import (Any, List, Mapping, Optional, Tuple, Union, overload)
import cortopy as corto
class Environment:
    """
    Sun class
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

    #@overload
    def __init__(self, CAM:corto.Camera, BODY:corto.Body, SUN:corto.Sun, RENDERING:corto.Rendering) -> None:
        """
        Description of the method

        Args:
            name: name of the CAM object 
            properties: properties of the CAM object

        Raises:
            which kind of exceptions

        See also:
            additional function and modules imported

        """
        # ENV setup 
        self.camera = CAM
        self.body = BODY
        self.sun = SUN
        self.rendering = RENDERING
        # Set background to black (default)
        bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = (0, 0, 0, 1)


    # Instance methods
    def get_positions(self):
        pos_body = self.body.get_position()
        pos_cam = self.camera.get_position()
        pos_sun = self.sun.get_position()
        return pos_body, pos_cam, pos_sun

    def get_orientations(self):
        quat_body = self.body.get_orientation()
        quat_cam = self.camera.get_orientation()
        return quat_body, quat_cam
    
    def PositionAll(self, state:np.array):
        #TODO: add multi-body capability
        # Unpack relative poses from the state
        pose_cam = state[8:15]
        pose_body = state[1:8]
        pos_sun = state[15:18]
        # Set bodies positions and orientations
        self.camera.set_position = pose_cam[0:4]
        self.camera.set_orientation = pose_cam[4:8]
        self.body.set_position = pose_body[0:4]
        self.body.set_orientation = pose_body[4:8]
        self.sun.set_position = pos_sun[0:4]
        return
