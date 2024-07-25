
from __future__ import annotations

import numpy as np
import bpy 
import mathutils

from typing import (Any, List, Mapping, Optional, Tuple, Union, overload)

class Shading:
    """
    Shading class
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

    def __init__(self) -> None:
        """
        Constructor for the shading class
        """

    def create_new_material(name:str):
        """Creata a new empty material

        Args:
            name (str): name to assign to the material

        Returns:
            material (bpy.data.materials): New empty material
        """
        material = bpy.data.materials.new(name = name)
        material.use_nodes = True # Enable use nodes
        # Get the material's node tree
        node_tree = material.node_tree
        # Clear any existing nodes (if any)
        nodes = node_tree.nodes
        nodes.clear()
        return material
    
    def create_simple_diffuse_BSDF(material, color_RGB = np.array([1,0,0])):
        """Generate a simple diffuse BSDF shader.

        Args:
            material (bpy.data.materials): Material 
            color_RGB (np.array(3,), optional): . Defaults to np.array([1,0,0]).
        """
        nodes = material.node_tree.nodes
        # Create diffuse node
        diffuse_node = nodes.new(type='ShaderNodeBsdfDiffuse')
        diffuse_node.location = (0, 0)
        # Create material output node
        output_node = nodes.new(type='ShaderNodeOutputMaterial')
        output_node.location = (200, 0)
        # Connect the Diffuse BSDF node to the Material Output node
        material.node_tree.links.new(diffuse_node.outputs['BSDF'], output_node.inputs['Surface'])
        # Set the diffuse color
        diffuse_node.inputs['Color'].default_value = (color_RGB[0], color_RGB[1], color_RGB[2], 1)  # RGBA

    def assign_material_to_object(material, body):
        """Assign a material to a body object

        Args:
            material (bpy.data.materials): material
            body (corto.body): Body object to assign the material to
        """
        if bpy.context.object:
            obj = bpy.data.objects[body.name]
            if obj.data.materials:
                # Assign to the first material slot
                obj.data.materials[0] = material
            else:
                # Create a new material slot and assign
                obj.data.materials.append(material)
        print("Material created and assigned to the active object.")
