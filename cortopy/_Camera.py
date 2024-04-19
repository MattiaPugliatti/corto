
from __future__ import annotations

import numpy as np
#import bpy 

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
        Description of the method

        Args:
            name: name of the CAM object 
            properties: properties of the CAM object

        Raises:
            which kind of exceptions

        See also:
            additional function and modules imported

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
        '''
        # Generate the Blende object
        bpy.ops.object.camera_add(enter_editmode=False, align='VIEW', location=self.position, rotation=(0, 0, 0), scale=(1, 1, 1))
        CAM = bpy.context.object
        CAM.name = self.name
        # Setup FOV
        CAM.data.type = 'PERSP'
        CAM.data.lens_unit = 'FOV'
        CAM.data.angle = self.fov * np.pi / 180
        CAM.data.clip_start = self.clip_start # [m]
        CAM.data.clip_end = self.clip_end # [m]
        bpy.context.scene.cycles.film_exposure = self.film_exposure
        bpy.context.scene.view_settings.view_transform = self.viewtransform
        bpy.context.scene.render.pixel_aspect_x = 1 # TODO: generalize for different sensor aspect ratios
        bpy.context.scene.render.pixel_aspect_y = 1 # TODO: generalize for different sensor aspect ratios
        bpy.context.scene.render.resolution_x = self.res[0]
        bpy.context.scene.render.resolution_y = self.res[1]
        bpy.context.scene.render.image_settings.color_mode = self.sensor
        bpy.context.scene.render.image_settings.color_depth = self.bit_encoding
        self.CAM_Blender = CAM
        '''
    #def __init__(self, *args, **kwargs) -> None: # version that actually implements the different args checks and implementation

    # Instance methods
    def get_name(self):
        print(self)
        return self.name

    def get_position(self):
        return self.position
    
    def get_orientation(self):
        return self.orientation

    def get_fov(self):
        return self.fov
    
    def get_res(self):
        return self.res

    def get_film_exposure(self):
        return self.film_exposure

    def get_K(self):
        return self.K
               
    def get_sensor(self):
        return self.sensor

    def get_clip_start(self):
        return self.clip_start

    def get_clip_end(self):
        return self.clip_end

    def get_bit_encoding(self):
        return self.bit_encoding

    def get_viewtransform(self):
        return self.viewtransform
    
    def set_position(self, position:np.array):
        self.position = position
        #self.CAM_Blender.location = self.position

    def set_orientation(self, orientation:np.array):
        self.orientation = orientation
        #self.CAM_Blender.rotation_mode = 'QUATERNION'
        #self.CAM_Blender.rotation_quaternion = self.orientation

    def set_film_exposure(self, film_exposure:float):
        self.film_exposure = film_exposure
        #self.CAM_Blender.film_exposure = self.film_exposure
    


 