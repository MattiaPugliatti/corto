
from __future__ import annotations

import numpy as np
import bpy 

from typing import (Any, List, Mapping, Optional, Tuple, Union, overload)

class Camera:
    """
    Camera class
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
        Constructor for the class CAM defining Blender camera

        Args:
            name: name of the CAM object 
            properties: properties of the CAM object
        """
        # CAM name
        self.name = name
        # CAM pose
        self.position = np.array([0,0,0])
        self.orientation = np.array([1,0,0,0])
        # CAM properties
        self.fov = properties['fov']*np.pi/180# [rad]
        self.res_x = properties['res_x'] # [-]
        self.res_y = properties['res_y'] # [-]
        self.res = np.array([self.res_x, self.res_y]) #[-]
        self.film_exposure = properties['film_exposure'] # [s]
        self.sensor = properties['sensor'] # (str)
        self.K = properties['K'] # [px]
        self.clip_start = properties['clip_start'] # [BU]
        self.clip_end = properties['clip_end'] # [BU]
        self.bit_encoding = properties['bit_encoding'] # [-]
        self.viewtransform = properties['viewtransform'] # [-]

        # TODO: transform self.orientation from quaternion to default rotation in Blender
        #self.CAM_Blender.rotation_mode = 'QUATERNION'
        
        # Generate the Blender object
        # Add a camera
        bpy.ops.object.camera_add(enter_editmode=False, align='VIEW', location=self.position, rotation=(0, 0, 0), scale=(1, 1, 1))
        CAM = bpy.context.object
        CAM.name = self.name
        CAM.location = self.position
        CAM.rotation_quaternion = self.orientation
        # Setup its properties
        CAM.data.type = 'PERSP'
        CAM.data.lens_unit = 'FOV'
        CAM.data.angle = self.fov # [rad]
        CAM.data.clip_start = self.clip_start # [BU]
        CAM.data.clip_end = self.clip_end # [BU]
        # Setup related properties
        self.toBlender()
        self.CAM_Blender = CAM

    # Instance methods
    def toBlender(self) -> None:
        """
        Push parameters of this instance of CAM to Blender environment. 
        Useful to load in Blender parameters of an instance of Camera class without having to reinitialize it.
        """
        # Setup related properties
        bpy.context.scene.cycles.film_exposure = self.film_exposure
        bpy.context.scene.view_settings.view_transform = self.viewtransform
        bpy.context.scene.render.pixel_aspect_x = 1 # TODO: generalize for different sensor aspect ratios
        bpy.context.scene.render.pixel_aspect_y = 1 # TODO: generalize for different sensor aspect ratios
        bpy.context.scene.render.resolution_x = self.res[0]
        bpy.context.scene.render.resolution_y = self.res[1]
        bpy.context.scene.render.image_settings.color_mode = self.sensor
        bpy.context.scene.render.image_settings.color_depth = self.bit_encoding


    def get_name(self) -> str:
        """
        Get name of the CAM instance

        Raises:
            NameError : CAM instance has mismatching name

        Returns:
            name : name of the CAM object
        """
        if self.CAM_Blender.name != self.name:
            raise NameError("Naming mismatch between workspaces.")

        print(self)
        return self.name

    def get_position(self) -> np.array:
        """
        Get position of the CAM instance

        Raises:
            ValueError : CAM instance has mismatching location

        Returns:
            position : vector containing the location of the CAM
        """

        if not all(np.array(self.CAM_Blender.location) == self.position):
            raise ValueError("Position mismatch between workspaces.")
        
        return self.position
    
    def get_orientation(self) -> np.array:
        """
        Get orientation of the CAM instance

        Raises:
            ValueError : CAM instance has mismatching orientation

        Returns:
            orientation : vector containing the quaternion representing the orientation of the CAM
        """
        
        if not all(np.array(self.CAM_Blender.rotation_quaternion) == self.orientation):
            raise ValueError("orientation mismatch between workspaces.")
        
        return self.orientation

    def get_fov(self) -> float:
        """
        Get fov property of the CAM instance

        Raises:
            ValueError : CAM instance has mismatching fov property

        Returns:
            fov : scalar containing the fov of the CAM
        """

        five_digits_fov_Blender = "{:.5f}".format(self.CAM_Blender.data.angle)
        five_digits_fov_corto = "{:.5f}".format(self.fov)
        if five_digits_fov_Blender != five_digits_fov_corto:
            raise ValueError("property mismatch between workspaces.")
        
        return self.fov
    
    def get_res(self) -> np.array:
        """
        Get resoultion of the CAM instance

        Raises:
            ValueError : CAM instance has mismatching resoultion

        Returns:
            resolution : vector containing the x-y resolution of the CAM
        """
        
        resolution = np.array([bpy.context.scene.render.resolution_x, bpy.context.scene.render.resolution_y]) 
        if not all(self.res == resolution):
            raise ValueError("resolution mismatch between workspaces.")
        
        return self.res

    def get_film_exposure(self) -> float:
        """
        Get exposure property of the CAM instance

        Raises:
            ValueError : CAM instance has mismatching exposure property

        Returns:
            exposure : scalar containing the exposure of the CAM
        """
        
        if bpy.context.scene.cycles.film_exposure != self.film_exposure:
            raise ValueError("property mismatch between workspaces.")
        
        return self.film_exposure

    def get_K(self) -> np.array:
        """
        Get K matrix of the CAM instance

        Returns:
            K : K matrix of the CAM
        """
        return self.K

    def get_sensor(self) -> str:
        """
        Get sensor type of the CAM instance

        Raises:
            ValueError : CAM instance has mismatching sensor type

        Returns:
            sensor : sensor type of the CAM object
        """
        if self.sensor != bpy.context.scene.render.image_settings.color_mode:
            raise NameError("sensor type mismatch between workspaces.")
        return self.sensor

    def get_clip_start(self) -> float:
        """
        Get clip_start property of the CAM instance

        Raises:
            ValueError : CAM instance has mismatching clip_start property

        Returns:
            clip_start : scalar containing the clip_start of the CAM
        """
        if self.CAM_Blender.data.clip_start != self.clip_start:
            raise ValueError("property mismatch between workspaces.")
        
        return self.clip_start

    def get_clip_end(self) -> float:
        """
        Get clip_end property of the CAM instance

        Raises:
            ValueError : CAM instance has mismatching clip_end property

        Returns:
            clip_end : scalar containing the clip_end of the CAM
        """
        if self.CAM_Blender.data.clip_end != self.clip_end:
            raise ValueError("property mismatch between workspaces.")
        
        return self.clip_end

    def get_bit_encoding(self) -> str:
        """
        Get sensor bit encording of the CAM instance

        Raises:
            ValueError : CAM instance has mismatching bit encoding

        Returns:
            bit_encoding : bit encoding of the CAM object
        """
        if self.bit_encoding != bpy.context.scene.render.image_settings.bit_encoding:
            raise NameError("sensor bit encoding mismatch between workspaces.")
        
        return self.bit_encoding

    def get_viewtransform(self) -> str:
        """
        Get viewtransform of the CAM instance

        Raises:
            ValueError : CAM instance has mismatching viewtransform

        Returns:
            viewtransform : viewtranform of the CAM object
        """
        if self.viewtransform != bpy.context.scene.view_settings.view_transform:
            raise NameError("sensor viewtransform mismatch between workspaces.")
        
        return self.viewtransform
        
    def set_position(self, position: np.array) -> None:
        """
        Set position of the CAM instance

        Args:
            position : array containing 3d coordinates for the CAM
        """
        self.position = position
        self.CAM_Blender.location = self.position

    def set_orientation(self, orientation: np.array) -> None:
        """
        Set orientation of the CAM instance

        Args:
            orientation : array containing quaternion expressing the orientation of the CAM
        """
        self.orientation = orientation
        self.CAM_Blender.rotation_mode = 'QUATERNION'
        self.CAM_Blender.rotation_quaternion = self.orientation

    def set_film_exposure(self, film_exposure: float) -> None:
        """
        Set exposure of the film

        Args:
            film_exposure : float describing film_exposure
        """
        self.film_exposure = film_exposure
        bpy.context.scene.cycles.film_exposure = self.film_exposure
