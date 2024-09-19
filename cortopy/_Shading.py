
from __future__ import annotations

import numpy as np
import bpy 
import mathutils
import os

from typing import (Any, List, Mapping, Optional, Tuple, Union, overload)
from cortopy import State

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
    
    def create_simple_diffuse_BSDF(material, BSDF_color_RGB = np.array([1,0,0])):
        """Generate a simple diffuse BSDF shader.

        Args:
            material (bpy.data.materials): Material 
            color_RGB (np.array(3,), optional): . Defaults to np.array([1,0,0]).
        """
        nodes = material.node_tree.nodes
        # Create diffuse node
        shader = nodes.new(type='ShaderNodeBsdfDiffuse')
        shader.location = (0, 0)
        # Create material output node
        output_node = nodes.new(type='ShaderNodeOutputMaterial')
        output_node.location = (200, 0)
        # Connect the Diffuse BSDF node to the Material Output node
        material.node_tree.links.new(shader.outputs['BSDF'], output_node.inputs['Surface'])
        # Set the diffuse color
        shader.inputs['Color'].default_value = (BSDF_color_RGB[0], BSDF_color_RGB[1], BSDF_color_RGB[2], 1)  # RGBA

    def create_simple_principled_BSDF(material, 
                                      PBSDF_color_RGB = np.array([1, 0, 0]),
                                      PBSDF_roughness = 1, 
                                      PBSDF_ior = 180,
                                      PBSDF_coat_weight = 0, 
                                      PBSDF_coat_roughness = 1, 
                                      PBSDF_coat_tint = np.array([1, 0, 0])
                                      ):
        """Generate a simple Principled BSDF shader.

        Args:
            material (bpy.data.materials): Material 
            PBSDF_color_RGB (np.array(3,), optional): . Defaults to np.array([1, 0, 0]).
        """
        nodes = material.node_tree.nodes
        # Create Principled BSDF node
        shader = nodes.new(type='ShaderNodeBsdfPrincipled')
        shader.location = (0, 0)
        # Create material output node
        output_node = nodes.new(type='ShaderNodeOutputMaterial')
        output_node.location = (200, 0)
        # Connect the Principled BSDF node to the Material Output node
        material.node_tree.links.new(shader.outputs['BSDF'], output_node.inputs['Surface'])
        # Set the base color
        shader.inputs['Base Color'].default_value = (PBSDF_color_RGB[0], PBSDF_color_RGB[1], PBSDF_color_RGB[2], 1) # RGBA
        # Set other PBSDF properties
        shader.inputs['Roughness'].default_value = PBSDF_roughness
        shader.inputs['IOR'].default_value = PBSDF_ior
        shader.inputs['Coat Weight'].default_value = PBSDF_coat_weight
        shader.inputs['Coat Roughness'].default_value = PBSDF_coat_roughness
        shader.inputs['Coat Tint'].default_value = (PBSDF_coat_tint[0], PBSDF_coat_tint[1], PBSDF_coat_tint[2], 1) # RGBA
    
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

    def create_node(name:str, material, location = (0,0)):
        """Create node"""
        node = material.node_tree.nodes.new(type=name)
        node.location = (location)
        return node

    def link_nodes(material,node_output,node_input):
        """Link output from node a to input to node b"""
        material.node_tree.links.new(node_output,node_input)

    def texture_node(material, location):
        return Shading.create_node('ShaderNodeTexImage', material, location)

    def mix_node(material, location):
        return Shading.create_node('ShaderNodeMixShader', material, location)

    def diffuse_BSDF(material, location):
        return Shading.create_node('ShaderNodeBsdfDiffuse', material, location)
    
    def principled_BSDF(material, location):
        return Shading.create_node('ShaderNodeBsdfPrincipled', material, location)
    
    def material_output(material, location):
        return Shading.create_node('ShaderNodeOutputMaterial', material, location)
    
    def create_branch_texture_mix(material,state:State):
        texture_node = Shading.texture_node(material,(-400,0))
        texture_node.image = bpy.data.images.load(os.path.join(state.path['input_path'],'body','Texture',state.path['texture_name']))
        mix_node = Shading.mix_node(material,(400,0))
        mix_node.inputs[0].default_value = 0.95
        diffuse_BSDF_node = Shading.diffuse_BSDF(material,(0,200))
        principled_BSDF_node = Shading.principled_BSDF(material,(0,0))
        material_node = Shading.material_output(material,(600,0))

        Shading.link_nodes(material, texture_node.outputs["Color"], principled_BSDF_node.inputs["Base Color"])
        Shading.link_nodes(material, diffuse_BSDF_node.outputs["BSDF"], mix_node.inputs[1])
        Shading.link_nodes(material, principled_BSDF_node.outputs["BSDF"], mix_node.inputs[2])
        Shading.link_nodes(material, mix_node.outputs["Shader"], material_node.inputs["Surface"])

        Shading.assign_material_to_object(material, body)