from __future__ import annotations
from typing import Any, List, Mapping, Optional, Tuple, Union, overload

import bpy

class Rendering:
    """
    Rendering class
    """

    # *************************************************************************
    # *     Constructors & Destructors
    # *************************************************************************

    def __init__(self, properties: dict) -> None:
        """
        Constructor for the class RENDERING defining Blender rendering enginer properties

        Args:
            properties: properties of the rendering engine, including
                - engine
                - device
                - samples
                - preview_samples

        Raises:
            TypeError: number of preview samples must be integer
            TypeError: number of rendering samples must be integer
        """
        # Ren properties
        self.engine = properties["engine"]
        self.device = properties["device"]
        self.samples = properties["samples"]
        self.preview_samples = properties["preview_samples"]
        if type(self.preview_samples) != int:
            raise TypeError("Number of preview samples must be integer.")
        if type(self.samples) != int:
            raise TypeError("Number of rendering samples must be integer.")
        # Generate the Blender object
        self.toBlender()

        # def __init__(self, *args, **kwargs) -> None: # version that actually implements the different args checks and implementation

    # Instance methods
    def toBlender(self) -> None:
        """
        Push parameters of this instance of Engine to Blender environment.
        Useful to load in Blender parameters of an instance of Engine class without having to reinitialize it.

        """
        # Generate the Blender object
        bpy.context.scene.render.engine = self.engine
        bpy.context.scene.cycles.device = self.device
        bpy.context.scene.cycles.samples = self.samples
        bpy.context.scene.cycles.preview_samples = self.preview_samples

    def get_engine(self) -> str:
        """
        Get name of the RENDERING engine

        Raises:
            NameError : RENDERING instance has mismatching name

        Returns:
            name : name of the RENDERING engine
        """
        if bpy.context.scene.render.engine != self.engine:
            raise NameError("Naming mismatch between workspaces.")

        return self.engine

    def get_device(self) -> str:
        """
        Get device type set for rendering the scene

        Raises:
            NameError : mismatching device

        Returns:
            name : name of the rendering device
        """
        if bpy.context.scene.cycles.device != self.device:
            raise NameError("device mismatch between workspaces.")

        return self.device

    def get_sample(self) -> int:
        """
        Get number of samples set to render the scene

        Raises:
            ValueError : number of samples used for rendereing has mismatching value between workspaces

        Returns:
            samples : numer of samples set to render the scene
        """
        if bpy.context.scene.cycles.samples != self.samples:
            raise ValueError("samples mismatch between workspaces.")

        return self.samples

    def get_preview_sample(self) -> int:
        """
        Get number of samples set to preview the scene

        Raises:
            ValueError : number of samples used for preview has mismatching value between workspaces

        Returns:
            samples : numer of samples set to preview the scene
        """
        if bpy.context.scene.cycles.preview_samples != self.preview_samples:
            raise ValueError("samples mismatch between workspaces.")

        return self.preview_samples

    def set_engine(self, engine: str) -> None:
        """
        Set name of the RENDERING engine

        Args:
            engine (str) : name of the RENDERING engine
        """
        self.engine = engine
        bpy.context.scene.render.engine = self.engine

    def set_device(self, device: str) -> None:
        """
        Set device to run rendering

        Args:
            device (str) : name of the RENDERING device
        """
        self.device = device
        bpy.context.scene.cycles.device = self.device

    def set_sample(self, samples: int) -> None:
        """
        Set number of samples used to render the scene

        Args:
            samples (int): number of samples used to render the scene

        Raises:
            TypeError: number of rendering samples must be integer
        """

        if type(samples) != int:
            raise TypeError("Number of rendering samples must be integer.")
        self.samples = samples
        bpy.context.scene.cycles.samples = self.samples

    def set_preview_sample(self, preview_samples: int) -> None:
        """
        Set number of samples used to preview the scene

        Args:
            preview_samples (int): number of samples used to preview the scene

        Raises:
            TypeError: number of preview samples must be integer
        """
        if type(preview_samples) != int:
            raise TypeError("Number of preview samples must be integer.")
        self.preview_samples = preview_samples
        bpy.context.scene.cycles.preview_samples = self.preview_samples

    def activate_depth_pass(active: bool = True) -> None:
        """activate depth pass option

        Args:
            active (bool, optional): flag. Defaults to True.
        """        
        bpy.context.scene.view_layers["ViewLayer"].use_pass_z = active

    def activate_id_mask(active: bool = True) -> None:
        """activate id mask option

        Args:
            active (bool, optional): flag. Defaults to True.
        """     
        bpy.context.scene.view_layers["ViewLayer"].use_pass_object_index = active

    def activate_pass_shadow(active: bool = True) -> None:
        """activate pass shadow option

        Args:
            active (bool, optional): flag. Defaults to True.
        """     
        bpy.context.scene.view_layers["ViewLayer"].use_pass_shadow = active

    def activate_pass_diffuse_direct(active: bool = True) -> None:
        """activate direct diffuse pass option

        Args:
            active (bool, optional): flag. Defaults to True.
        """     
        bpy.context.scene.view_layers["ViewLayer"].use_pass_diffuse_direct = active

    def activate_pass_normal(active: bool = True) -> None:
        """activate normal pass option

        Args:
            active (bool, optional): flag. Defaults to True.
        """     
        bpy.context.scene.view_layers["ViewLayer"].use_pass_normal = active

    def activate_denoise_data(active: bool = True) -> None:
        """activate denoise data option

        Args:
            active (bool, optional): flag. Defaults to True.
        """     
        bpy.context.scene.cycles.use_denoising = (
            active  # TODO: add check between cycles and evee here
        )
        # TODO: Check bpy version
        # bpy.context.scene.view_layers["ViewLayer"].use_pass_denoising_data = True # TODO: not working
        # bpy.context.scene.view_layers["ViewLayer"].use_pass_noisy = True #TODO: not working
