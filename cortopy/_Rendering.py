
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

    #@overload
    def __init__(self, properties: dict) -> None:
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
        # Ren properties
        self.engine = properties['engine']
        self.device = properties['device']
        self.samples = properties['samples']
        self.preview_samples = properties['preview_samples']
        # Generate the Blender object
        bpy.context.scene.render.engine = self.engine
        bpy.context.scene.cycles.device = self.device
        bpy.context.scene.cycles.samples = self.samples
        bpy.context.scene.cycles.preview_samples = self.preview_samples

        #def __init__(self, *args, **kwargs) -> None: # version that actually implements the different args checks and implementation

    # Instance methods
    def get_engine(self):
        return self.engine
    
    def get_device(self):
        return self.device

    def get_sample(self):
        return self.samples
    
    def get_preview_sample(self):
        return self.preview_samples
    
    def set_engine(self, engine):
        self.engine = engine
        bpy.context.scene.render.engine = self.engine

    def set_device(self, device):
        self.device = device
        bpy.context.scene.cycles.device = self.device

    def set_sample(self,samples):
        self.samples = samples
        bpy.context.scene.cycles.samples = self.samples
    
    def set_preview_sample(self,preview_samples):
        self.preview_samples = preview_samples
        bpy.context.scene.cycles.preview_samples = self.preview_samples
