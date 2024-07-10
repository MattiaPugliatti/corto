
from __future__ import annotations

import numpy as np
import bpy 
import mathutils

from typing import (Any, List, Mapping, Optional, Tuple, Union, overload)

class Rendering:
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

    def __init__(self, properties: dict) -> None:
        """
        Constructor for the class RENDERING defining Blender rendering enginer properties

        Args:
            properties: properties of the rendering engine, including
                - engine
                - device
                - samples
                - preview_samples
        """
        # Ren properties
        self.engine = properties['engine']
        self.device = properties['device']
        self.samples = properties['samples']
        self.preview_samples = properties['preview_samples']
        # Generate the Blender object
        self.toBlender()

        #def __init__(self, *args, **kwargs) -> None: # version that actually implements the different args checks and implementation

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
            engine : name of the RENDERING engine
        """
        self.engine = engine
        bpy.context.scene.render.engine = self.engine

    def set_device(self, device: str) -> None:
        """
        Set device to run rendering

        Args:
            device : name of the RENDERING device
        """
        self.device = device
        bpy.context.scene.cycles.device = self.device

    def set_sample(self, samples: int) -> None:
        """
        Set number of samples used to render the scene

        Args:
            samples : number of samples used to render the scene
        """
        self.samples = samples
        bpy.context.scene.cycles.samples = self.samples
    
    def set_preview_sample(self, preview_samples: int) -> None:
        """
        Set number of samples used to preview the scene

        Args:
            preview_samples : number of samples used to preview the scene
        """
        self.preview_samples = preview_samples
        bpy.context.scene.cycles.preview_samples = self.preview_samples
