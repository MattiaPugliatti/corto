
from __future__ import annotations

import numpy as np
import bpy 
import mathutils

from typing import (Any, List, Mapping, Optional, Tuple, Union, overload)

class Sun:
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
        # SUN name
        self.name = name
        # SUN pose
        self.position = np.array([0,0,0])
        self.orientation = np.array([1,0,0,0])
        # SUN properties
        self.sun_angle = properties['angle']*np.pi/180# [rad]
        self.sun_energy = properties['energy'] # [W]
        
        # Generate the Blender object
        # Add a sun lamp
        bpy.ops.object.light_add(type='SUN', radius=1, align='WORLD', location=self.position, scale=(1, 1, 1))
        SUN = bpy.data.objects[self.name]
        SUN.data.energy = self.sun_energy # [W]
        SUN.data.angle = self.sun_angle # [rad]
        SUN.location = self.position # [BU]
        SUN.rotation_mode = 'QUATERNION'
        SUN.rotation_quaternion = self.orientation # [-]
        self.SUN_Blender = SUN

        #def __init__(self, *args, **kwargs) -> None: # version that actually implements the different args checks and implementation

    # Instance methods
    def get_name(self):
        print(self)
        return self.name

    def get_position(self):
        return self.position
    
    def get_orientation(self):
        return self.orientation

    def get_energy(self):
        return self.sun_energy
    
    def get_angle(self):
        return self.sun_angle
        
    def set_position(self, position:np.array):
        direction = mathutils.Vector(position/np.linalg.norm(position))
        rot_quat = direction.to_track_quat('-Z', 'Y')
        self.position = position
        self.orientation = rot_quat
        self.SUN_Blender.location = self.position
        self.SUN_Blender.rotation_mode = 'QUATERNION'
        self.SUN_Blender.rotation_quaternion = self.orientation 

    def set_energy(self, energy):
        self.sun_energy = energy
        self.SUN_Blender.data.energy = self.sun_energy

    def set_angle(self, angle):
        self.sun_angle = angle
        self.SUN_Blender.data.angle = self.sun_angle
 
