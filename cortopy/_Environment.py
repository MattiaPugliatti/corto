
from __future__ import annotations
from typing import (Any, List, Mapping, Optional, Tuple, Union, overload)

import numpy as np
import bpy 
import os
import cortopy as corto

class Environment:
    """
    Sun class
    """
    # *************************************************************************
    # *     Constructors & Destructors
    # *************************************************************************

    #@overload
    def __init__(self, CAM: corto.Camera, BODY: Union[list, corto.Body], SUN: corto.Sun, RENDERING: corto.Rendering) -> None:
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
        # Generate a n_bodies flag
        if isinstance(BODY, corto.Body):
            n_bodies = 1
        elif isinstance(BODY, list):
            n_bodies = len(BODY)

        # ENV setup 
        self.camera = CAM
        if n_bodies == 1:
            self.body = BODY
        else: 
            for ii, body in enumerate(BODY, start=1):
                setattr(self, f"body_{ii}", body)
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
        # Unpack relative poses from the state
        position_cam = state.geometry['camera']['position'][index]
        orientation_cam = state.geometry['camera']['orientation'][index]
        if state.n_bodies==1:
            position_body = state.geometry['body']['position'][index]
            orientation_body = state.geometry['body']['orientation'][index]
        else:
            position_body = []
            orientation_body = []
            for ii in range(0,state.n_bodies):
                position_body.append(state.geometry[f"body_{ii+1}"]['position'][index])
                orientation_body.append(state.geometry[f"body_{ii+1}"]['orientation'][index])     
        position_sun = state.geometry['sun']['position'][index]

        # Set bodies positions and orientations
        self.camera.set_position(position_cam)
        self.camera.set_orientation(orientation_cam)
        if state.n_bodies==1:
            self.body.set_position(position_body)
            self.body.set_orientation(orientation_body)
        else:
            for ii in range(state.n_bodies):
                body_attr = getattr(self, f"body_{ii + 1}")  # Get the body dynamically (e.g., body_1, body_2, ...)
                body_attr.set_position(position_body[ii])    # Set position for each body
                body_attr.set_orientation(orientation_body[ii])  # Set orientation for each body
        self.sun.set_position(position_sun)
        return self

    def RenderOne(self, camera:corto.Camera, state:corto.State, index: int = 0, depth_flag: bool =False) -> None :
        """_summary_

        Args:
            camera (corto.Camera): camera object
            state (corto.State): state object
            index (int, optional): index of the geometry to render. Defaults to 0.
            depth_flag (bool, optional): flag to enable depth label generation. Defaults to False.
        """        
        corto.Camera.select_camera(camera.name)
        rendering_name = '{}.png'.format(str(int(index)).zfill(6))
        bpy.context.scene.render.filepath = os.path.join(state.path["output_path"],'img',rendering_name)
        bpy.context.scene.frame_current = index
        bpy.ops.render.render(write_still = True)
        
        if depth_flag: # TODO: debug while its not saving anything in output
            z = bpy.data.images['Viewer Node']#TODO: does this work with multiple viewer nodes?
            w, h = z.size
            dmap = np.array(z.pixels[:], dtype=np.float16)
            dmap = np.reshape(dmap, (h, w, 4))[:,:,0]
            dmap = np.rot90(dmap, k=2)
            dmap = np.fliplr(dmap)
            txtname = '{num:06d}'
            depth_dir = os.path.join(state.path["output_path"],'depth')
            if not os.path.exists(depth_dir):
                os.makedirs(depth_dir)
            np.savetxt(os.path.join(state.path["output_path"],'depth', txtname.format(num=(index+0)) + '.txt'), dmap, delimiter=' ',fmt='%.5f')    
        return