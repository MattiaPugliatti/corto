
from __future__ import annotations

import numpy as np
import bpy 
import mathutils

from typing import (Any, List, Mapping, Optional, Tuple, Union, overload)

class Body:
    """
    Body class
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
    def __init__(self, name: str, properties: dict) -> None:
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
        # BODY name
        self.name = name
        # BODY pose
        self.position = np.array([0,0,0])
        self.orientation = np.array([1,0,0,0])
        self.scale = np.array([1,1,1])
        # BODY properties
        self.pass_index = properties['pass_index']
        self.diffuse_bounces = properties['diffuse_bounces']
        # Generate the Blender object

        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', location=self.position, scale=self.scale)
        BODY = bpy.data.objects[self.name]
        BODY.location = self.position # [BU]
        BODY.rotation_mode = 'QUATERNION'
        BODY.rotation_quaternion = self.orientation # [-]
        BODY.pass_index = self.pass_index # [-]
        BODY.scale = self.scale # [-]
        bpy.context.scene.cycles.diffuse_bounces = self.diffuse_bounces # [-]
        self.BODY_Blender = BODY

        #def __init__(self, *args, **kwargs) -> None: # version that actually implements the different args checks and implementation

    # Instance methods
    def get_name(self):
        print(self)
        return self.name

    def get_position(self):
        return self.position
    
    def get_orientation(self):
        return self.orientation

    def get_scale(self):
        return self.scale
    
    def get_passID(self):
        return self.pass_index
    
    def get_diffuse_bounces(self):
        return self.diffuse_bounces
        
    def set_position(self, position:np.array):
        self.position = position
        self.BODY_Blender.location = self.position

    def set_orientation(self, orientation:np.array):
        self.orientation = orientation
        self.BODY_Blender.rotation_mode = 'QUATERNION'
        self.BODY_Blender.rotation_quaternion = self.orientation

    def set_scale(self, scale:np.array):
        self.scale = scale
        self.BODY_Blender.scale = self.pass_index

    def set_passID(self, ID):
        self.pass_index = ID
        self.BODY_Blender.pass_index = self.pass_index
 
    def set_diffuse_bounces(self, par):
        self.diffuse_bounces = par
        bpy.context.scene.cycles.diffuse_bounces = self.diffuse_bounces # [-]
