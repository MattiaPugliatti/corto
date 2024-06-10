
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
        # Setup its properties
        CAM.data.type = 'PERSP'
        CAM.data.lens_unit = 'FOV'
        CAM.data.angle = self.fov # [rad]
        CAM.data.clip_start = self.clip_start # [BU]
        CAM.data.clip_end = self.clip_end # [BU]
        # Setup related properties
        bpy.context.scene.cycles.film_exposure = self.film_exposure
        bpy.context.scene.view_settings.view_transform = self.viewtransform
        bpy.context.scene.render.pixel_aspect_x = 1 # TODO: generalize for different sensor aspect ratios
        bpy.context.scene.render.pixel_aspect_y = 1 # TODO: generalize for different sensor aspect ratios
        bpy.context.scene.render.resolution_x = self.res[0]
        bpy.context.scene.render.resolution_y = self.res[1]
        bpy.context.scene.render.image_settings.color_mode = self.sensor
        bpy.context.scene.render.image_settings.color_depth = self.bit_encoding
        self.CAM_Blender = CAM

    # Instance methods
    def get_name(self):
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

    def get_position(self):
        """
        Get position of the CAM instance

        Raises:
            ValueError : CAM instance has mismatching location

        Returns:
            position : vector containing the location of the CAM
        """

        if not all(self.CAM_Blender.location == self.position):
            raise ValueError("Position mismatch between workspaces.")
        
        return self.position
    
    def get_orientation(self):
        """
        Get orientation of the CAM instance

        Raises:
            ValueError : CAM instance has mismatching orientation

        Returns:
            orientation : vector containing the quaternion representing the orientation of the CAM
        """
        
        if not all(self.CAM_Blender.rotation_quaternion == self.orientation):
            raise ValueError("orientation mismatch between workspaces.")
        
        return self.orientation

    def get_fov(self):
        """
        Get fov property of the CAM instance

        Raises:
            ValueError : CAM instance has mismatching fov property

        Returns:
            fov : scalar containing the fov of the CAM
        """
        
        if self.CAM_Blender.data.angle != self.fov:
            raise ValueError("property mismatch between workspaces.")
        
        return self.fov
    
    def get_res(self):
        # TBD: resolution seems to be a property of the renderer.
        # as a consequence 2 cameras with different resolution cannot coexhist
        return self.res

    def get_film_exposure(self):
        # TBD: film exposure seems to be a property of the renderer.
        # as a consequence 2 cameras with different exposures cannot coexhist
        return self.film_exposure

    def get_K(self):
        """
        Get K matrix of the CAM instance

        Returns:
            K : K matrix of the CAM
        """
        return self.K

    def get_sensor(self):
        # TBD: sensor type seems to be a property of the renderer.
        # as a consequence 2 different sensor types cannot coexhist
        return self.sensor

    def get_clip_start(self):
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

    def get_clip_end(self):
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

    def get_bit_encoding(self):
        # TBD: bit encoding seems to be a property of the renderer.
        # as a consequence 2 cameras with different bit encoding cannot coexhist
        return self.bit_encoding

    def get_viewtransform(self):
        # TBD: viewtransform seems to be a property of the environment.
        # as a consequence 2 cameras with different viewtransform cannot coexhist
        return self.viewtransform
        
    def set_position(self, position:np.array):
        """
        Set position of the CAM instance

        Args:
            position : array containing 3d coordinates for the CAM
        """
        self.position = position
        self.CAM_Blender.location = self.position

    def set_orientation(self, orientation:np.array):
        """
        Set orientation of the CAM instance

        Args:
            orientation : array containing quaternion expressing the orientation of the CAM
        """
        self.orientation = orientation
        self.CAM_Blender.rotation_mode = 'QUATERNION'
        self.CAM_Blender.rotation_quaternion = self.orientation

    def set_film_exposure(self, film_exposure:float):
        # TBD: film exposure seems to be a property of the renderer.
        # as a consequence 2 cameras with different exposures cannot coexhist
        self.film_exposure = film_exposure
        bpy.context.scene.cycles.film_exposure = self.film_exposure
