from __future__ import annotations
from typing import (Any, List, Mapping, Optional, Tuple, Union, overload)

import numpy as np
import bpy 
import mathutils

class Sun:
    """
    Sun class
    """
    # *************************************************************************
    # *     Constructors & Destructors
    # *************************************************************************

    #@overload
    def __init__(self, name: str, properties: dict) -> None:
        """
        Constructor for the class SUN defining Blender light source

        Args:
            name (str): name of the SUN object 
            properties (dict): properties of the SUN object
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
        # Link the corto and blender objects
        self.SUN_Blender = SUN

    # Instance methods
    def get_name(self) -> str:
        """
        Get name of the SUN instance

        Raises:
            NameError : SUN instance has mismatching name

        Returns:
            name : name of the SUN object
        """
        print(self)
        return self.name

    def get_position(self) -> np.array:
        """
        Get position of the SUN instance

        Raises:
            ValueError : SUN instance has mismatching location

        Returns:
            position : vector containing the location of the SUN
        """

        if not all(np.float32(np.array(self.SUN_Blender.location)) == np.float32(self.position)):
            raise ValueError("Position mismatch between workspaces.")
        
        return self.position
    
    def get_orientation(self) -> np.array:
        """
        Get orientation of the SUN instance

        Raises:
            ValueError : SUN instance has mismatching orientation

        Returns:
            orientation : vector containing the quaternion representing the orientation of the SUN
        """

        if not all(np.float32(np.array(self.SUN_Blender.rotation_quaternion)) == np.float32(self.orientation)):
            raise ValueError("orientation mismatch between workspaces.")
        
        return self.orientation

    def get_energy(self) -> float:
        """
        Get energy property of the SUN instance

        Raises:
            ValueError : SUN instance has mismatching fov property

        Returns:
            energy : scalar containing the fov of the SUN
        """
        
        if self.SUN_Blender.data.energy != self.sun_energy:
            raise ValueError("property mismatch between workspaces.")
        
        return self.sun_energy
    
    def get_angle(self) -> float:
        """
        Get angle of the SUN instance

        Raises:
            ValueError : SUN instance has mismatching angle property

        Returns:
            angle : scalar containing the angle of the SUN instance
        """
        
        if self.SUN_Blender.data.angle != self.sun_angle:
            raise ValueError("property mismatch between workspaces.")
        
        return self.sun_angle
        
    def set_position(self, position:np.array) -> None:
        """
        Set position of the SUN instance

        Args:
            position (np.array) : array containing incoming direction of the light source
        """
        direction = mathutils.Vector(-position/np.linalg.norm(position))
        rot_quat = direction.to_track_quat('-Z', 'Y')
        self.position = position
        self.orientation = rot_quat
        self.SUN_Blender.location = self.position
        self.SUN_Blender.rotation_mode = 'QUATERNION'
        self.SUN_Blender.rotation_quaternion = self.orientation 

    def set_energy(self, energy: float) -> None:
        """
        Set energy of the SUN instance

        Args:
            energy (float): float describing intensity of the light source
        """
        self.sun_energy = energy
        self.SUN_Blender.data.energy = self.sun_energy

    def set_angle(self, angle: float) -> None:
        """
        Set angle of the SUN instance

        Args:
            angle (float): float describing angle of the light source
        """
        self.sun_angle = angle
        self.SUN_Blender.data.angle = self.sun_angle
