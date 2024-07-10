
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

    def __init__(self, name: str, properties: dict) -> None:
        """
        Constructor for the class BODY defining Blender object

        Args:
            name: name of the BODY object 
            properties: properties of the BODY object

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
        # questa proprietà non dovrebbe andare in scena? non mi sembra una cosa tipica del corpo 
        # i.e., cambiandola per uno la cambi per tutti e rimane settata quella dell'ultimo oggetto creato
        # bpy.context.scene.cycles.diffuse_bounces = self.diffuse_bounces # [-]
        
        self.BODY_Blender = BODY

        #def __init__(self, *args, **kwargs) -> None: # version that actually implements the different args checks and implementation

    # *************************************************************************
    # *     Instance Methods
    # *************************************************************************

    def get_name(self) -> str:
        """
        Get name of the BODY instance

        Raises:
            NameError : BODY instance has mismatching name

        Returns:
            name : name of the BODY object
        """
        
        if self.BODY_Blender.name != self.name:
            raise NameError("Naming mismatch between workspaces.")

        return self.name

    def get_position(self) -> np.array:
        """
        Get position of the BODY instance

        Raises:
            ValueError : BODY instance has mismatching location

        Returns:
            position : vector containing the location of the BODY object
        """

        if not all(self.BODY_Blender.location == self.position):
            raise ValueError("Position mismatch between workspaces.")
        
        return self.position
    
    def get_orientation(self) -> np.array:
        """
        Get orientation of the BODY instance

        Raises:
            ValueError : BODY instance has mismatching orientation

        Returns:
            orientation : vector containing the quaternion representing the orientation of the BODY object
        """
        
        if not all(self.BODY_Blender.rotation_quaternion == self.orientation):
            raise ValueError("orientation mismatch between workspaces.")
        
        return self.orientation

    def get_scale(self) -> float:
        """
        Get scale of the BODY instance

        Raises:
            ValueError : BODY instance has mismatching scale

        Returns:
            scale : scale of the BODY object
        """
        if not all(self.BODY_Blender.scale == self.scale):
            raise ValueError("scale mismatch between workspaces.")

        return self.scale
    
    def get_passID(self) -> int:
        """
        Get pass index of the BODY instance

        Raises:
            ValueError : BODY instance has mismatching pass index
        Returns:
            pass index : pass index of the BODY object
        """
        
        if self.BODY_Blender.pass_index != self.pass_index:
            raise ValueError("pass index mismatch between workspaces.")
        
        return self.pass_index
    
    def get_diffuse_bounces(self) -> int:
        """
        Get diffuse bounces setting for the BODY instance

        Raises:
            ValueError : BODY instance has mismatching property

        Returns:
            diffuse bounces :  setting of diffuse bounces property
        """
        
        if bpy.context.scene.cycles.diffuse_bounces != self.diffuse_bounces:
            raise ValueError("parameter mismatch between workspaces.")
        return self.diffuse_bounces
        
    def set_position(self, position: np.array) -> None:
        """
        Set position of the BODY instance

        Args:
            position : array containing 3d coordinates for the BODY object
        """
        self.position = position
        self.BODY_Blender.location = self.position

    def set_orientation(self, orientation: np.array) -> None:
        """
        Set orientation of the BODY instance

        Args:
            orientation : array containing quaternion expressing the orientation of the BODY object
        """
        self.orientation = orientation
        self.BODY_Blender.rotation_mode = 'QUATERNION'
        self.BODY_Blender.rotation_quaternion = self.orientation

    def set_scale(self, scale: np.array) -> None:
        """
        Set scale of the BODY instance

        Args:
            scale : array containing scaling factors in 3 directions for the BODY object
        """
        self.scale = scale
        self.BODY_Blender.scale = self.scale

    def set_passID(self, ID: int) -> None:
        """
        Set pass index of the BODY instance

        Args:
            ID : scalar pass index value for the BODY object
        """
        self.pass_index = ID
        self.BODY_Blender.pass_index = self.pass_index

# anche questa funzione da vedere imho
    def set_diffuse_bounces(self, par: int) -> None:
        """
        Set diffuse bounces property for the BODY instance

        Args:
            par : scalar value for diffuse bounces property
        """
        self.diffuse_bounces = par
        bpy.context.scene.cycles.diffuse_bounces = self.diffuse_bounces # [-]
