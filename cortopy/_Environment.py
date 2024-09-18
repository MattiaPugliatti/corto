
from __future__ import annotations

import numpy as np
import bpy 
import mathutils
import os
import cortopy as corto

from typing import (Any, List, Mapping, Optional, Tuple, Union, overload)

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
    def __init__(self, CAM: corto.Camera, BODY: corto.Body, SUN: corto.Sun, RENDERING: corto.Rendering) -> None:
        """
        Constructor for the class CAM defining Blender camera

        Args:
            CAM       : instance of CAM class describing a camera
            BODY      : instance of the class describing an object
            SUN       : instance of SUN class describing a light source
            RENDERING : instance of RENDERING class describing the rendering engine
            
        See also:
        corto.Camera
        corto.Body
        corto.Sun
        corto.Rendering

        """
        # ENV setup 
        self.camera = CAM
        self.body = BODY
        self.sun = SUN
        self.rendering = RENDERING
        # Set background to black (default)
        #TODO: temporarily set to white background for debugging witouith shading
        bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = (0, 0, 0, 1)


    # Instance methods
    def get_positions(self) -> Tuple[np.array, np.array, np.array]:
        """
        Get position of the BODY, CAM, and SUN instances in the scene

        Returns:
            tuple containing the vector of location of the BODY, CAM, and SUN instances in the scene

        See also:
        corto.Body.get_position()
        corto.Camera.get_position()
        corto.Sun.get_position()
        """
        pos_body = self.body.get_position()
        pos_cam = self.camera.get_position()
        pos_sun = self.sun.get_position()
        return pos_body, pos_cam, pos_sun

    def get_orientations(self) -> Tuple[np.array, np.array] :
        """
        Get orientation of the BODY and CAM instances in the scene

        Returns:
            tuple containing the quaternion describing the orientation of the BODY and CAM instances in the scene

        See also:
        corto.Body.get_orientation()
        corto.Camera.get_orientation()
        """
        quat_body = self.body.get_orientation()
        quat_cam = self.camera.get_orientation()
        return quat_body, quat_cam
    
    def PositionAll(self, state: corto.State, index: int = 0) -> None :
        """
        Set position and orientation of BODY, CAM, and SUN instances in the scene

        Args:
            state: instance of cortopy.State class containing scene, geometry, and body settings
            index: (optional) geometry config file may contain multiple configurations, this index selects a specific sample, by default it gathers the first one available.
        """
        #TODO: add multi-body capability
        # Unpack relative poses from the state
        position_cam = state.geometry['camera']['position'][index]
        orientation_cam = state.geometry['camera']['orientation'][index]
        position_body = state.geometry['body']['position'][index]
        orientation_body = state.geometry['body']['orientation'][index]
        position_sun = state.geometry['sun']['position'][index]

        # Set bodies positions and orientations
        self.camera.set_position(position_cam)
        self.camera.set_orientation(orientation_cam)
        self.body.set_position(position_body)
        self.body.set_orientation(orientation_body)
        self.sun.set_position(position_sun)
        return self

    def RenderOne(self, camera, state:corto.State, index: int = 0, depth_flag: bool =False) -> None :
        """
        Render the scene given a state and an index 
        
        Args:
            state: instance of cortopy.State class containing scene, geometry, and body settings
            index: (optional) geometry config file may contain multiple configurations, this index selects a specific sample, by default it gathers the first one available.
        """
        corto.Camera.select_camera(camera.name)
        rendering_name = '{}.png'.format(str(int(index)).zfill(6))
        bpy.context.scene.render.filepath = os.path.join(state.output_path,'img',rendering_name)
        bpy.context.scene.frame_current = index
        bpy.ops.render.render(write_still = True)
        
        import time

        if depth_flag: 
            time.sleep(2)
            z = bpy.data.images['Viewer Node']#TODO does this work with multipel viewer nodes?
            w, h = z.size
            print(z.pixels[:])
            dmap = np.array(z.pixels[:], dtype=np.float16) # convert to numpy array
            dmap = np.reshape(dmap, (h, w, 4))[:,:,0]
            dmap = np.rot90(dmap, k=2)
            dmap = np.fliplr(dmap)
            txtname = '{num:06d}'
            depth_dir = os.path.join(state.output_path,'depth')
            if not os.path.exists(depth_dir):
                os.makedirs(depth_dir)
            np.savetxt(os.path.join(state.output_path,'depth', txtname.format(num=(index+0)) + '.txt'), dmap, delimiter=' ',fmt='%.5f')    
        return