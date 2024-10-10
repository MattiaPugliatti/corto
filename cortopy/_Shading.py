
from __future__ import annotations

import numpy as np
import bpy 
import mathutils
import os
import json

from typing import (Any, List, Mapping, Optional, Tuple, Union, overload)
from cortopy import State
from cortopy import Body

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
        '''
        nodes = material.node_tree.nodes
        # Create diffuse node
        shader = nodes.new(type='ShaderNodeBsdfDiffuse')
        shader.location = (0, 0)
        # Create material output node
        output_node = nodes.new(type='ShaderNodeOutputMaterial')
        output_node.location = (200, 0)
        # Create texture node
        texture_node = nodes.new(type = 'ShaderNodeTexImage')
        texture_node.location(-200,0)

        texture_path = "/Users/mattia/develop - CORTO/corto/input/S01_Eros/body/Texture/Eros Grayscale.jpg"
        try:
            img = bpy.data.images.load(texture_path)
        except:
            raise Exception(f"Failed to load image from {texture_path}")
        texture_node.image = img
        # Connect the Diffuse BSDF node to the Material Output node
        material.node_tree.links.new(shader.outputs['BSDF'], output_node.inputs['Surface'])
        material.node_tree.links.new(texture_node.outputs['Color'], output_node.inputs['Color'])
        # Set the diffuse color
        #shader.inputs['Color'].default_value = (BSDF_color_RGB[0], BSDF_color_RGB[1], BSDF_color_RGB[2], 1)  # RGBA
        '''

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

    def displace_node(material, location):
        return Shading.create_node('ShaderNodeDisplacement', material, location)

    def mix_node(material, location):
        return Shading.create_node('ShaderNodeMixShader', material, location)

    def diffuse_BSDF(material, location):
        return Shading.create_node('ShaderNodeBsdfDiffuse', material, location)
    
    def principled_BSDF(material, location):
        return Shading.create_node('ShaderNodeBsdfPrincipled', material, location)
    
    def material_output(material, location):
        return Shading.create_node('ShaderNodeOutputMaterial', material, location)
    
    def uv_map(material, location):
        return Shading.create_node('ShaderNodeUVMap', material, location)

    def create_branch_texture_mix(material,state:State):
        texture_node = Shading.texture_node(material,(-400,0))
        try:
            texture_node.image = bpy.data.images.load(state.path['texture_path'])
        except:
            raise Exception(f"Failed to load image from {state.path['texture_path']}")
        mix_node = Shading.mix_node(material,(400,0))
        mix_node.inputs[0].default_value = 0.95
        diffuse_BSDF_node = Shading.diffuse_BSDF(material,(0,200))
        principled_BSDF_node = Shading.principled_BSDF(material,(0,0))
        material_node = Shading.material_output(material,(600,0))
        uv_map_node = Shading.uv_map(material,(-600,0))
        #uv_map_node.uv_map = obj.data.uv_layers.active.name

        Shading.link_nodes(material, texture_node.outputs["Color"], principled_BSDF_node.inputs["Base Color"])
        Shading.link_nodes(material, diffuse_BSDF_node.outputs["BSDF"], mix_node.inputs[1])
        Shading.link_nodes(material, principled_BSDF_node.outputs["BSDF"], mix_node.inputs[2])
        Shading.link_nodes(material, mix_node.outputs["Shader"], material_node.inputs["Surface"])
        Shading.link_nodes(material, uv_map_node.outputs["UV"], texture_node.inputs["Vector"])

    def create_branch_texture_and_displace_mix(material,state:State):
        texture_node = Shading.texture_node(material,(-400,0))
        displace_texture = Shading.texture_node(material,(500,-200))
        try:
            texture_node.image = bpy.data.images.load(state.path['texture_path'])
        except:
            raise Exception(f"Failed to load image from {state.path['texture_path']}")
        
        try:
            displace_texture.image = bpy.data.images.load(state.path['displace_path'])
        except:
            raise Exception(f"Failed to load image from {state.path['displace_path']}")
        #TODO: adjust scale, midlevel, and Color space
        mix_node = Shading.mix_node(material,(400,0))
        mix_node.inputs[0].default_value = 0.95
        diffuse_BSDF_node = Shading.diffuse_BSDF(material,(0,200))
        principled_BSDF_node = Shading.principled_BSDF(material,(0,0))
        material_node = Shading.material_output(material,(600,0))
        uv_map_node = Shading.uv_map(material,(-600,0))
        displace_node = Shading.displace_node(material,(700,-200))
        #uv_map_node.uv_map = obj.data.uv_layers.active.name

        Shading.link_nodes(material, texture_node.outputs["Color"], principled_BSDF_node.inputs["Base Color"])
        Shading.link_nodes(material, diffuse_BSDF_node.outputs["BSDF"], mix_node.inputs[1])
        Shading.link_nodes(material, principled_BSDF_node.outputs["BSDF"], mix_node.inputs[2])
        Shading.link_nodes(material, mix_node.outputs["Shader"], material_node.inputs["Surface"])
        Shading.link_nodes(material, displace_texture.outputs["Color"], displace_node.inputs["Height"])
        Shading.link_nodes(material, displace_node.outputs["Displacement"], material_node.inputs["Displacement"])
        Shading.link_nodes(material, uv_map_node.outputs["UV"], texture_node.inputs["Vector"])

    def uv_unwrap(uv_unwrap_method : int, aux_input: list, body: Body):
        #TODO: add error check for aux_input
        # Ensure the object exists in the scene
        if body.name not in bpy.data.objects:
            raise Exception(f"Object '{body.name}' not found in the scene.")
        # Select the object
        obj = bpy.data.objects[body.name]
        # Select the object
        obj = bpy.context.active_object
        # Make the object active
        bpy.context.view_layer.objects.active = obj

        # Apply scale, rotation, and location transformations
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        # Clear existing UVs if needed (optional, but can help reset the UV map)
        bpy.ops.uv.reset()
        # Clear existing seams
        bpy.ops.mesh.clear_seam()

        # Ensure we are in Object mode
        if bpy.context.object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        # Switch to Edit mode to UV unwrap
        bpy.ops.object.mode_set(mode='EDIT')
        # Select all the mesh's faces in Edit mode
        bpy.ops.mesh.select_all(action='SELECT')
        if uv_unwrap_method == 1: # Standard unwrap
            bpy.ops.uv.unwrap(method=aux_input[0], margin=aux_input[1])
        elif uv_unwrap_method == 2: # Cylinder unwrap
            bpy.ops.uv.cylinder_project(direction=aux_input[0], align=aux_input[1])
        elif uv_unwrap_method == 3: # Spherical unwrap
            #bpy.ops.uv.sphere_project(clip_to_bounds=aux_input[0], scale_to_bounds=aux_input[1], correct_aspect=False, direction=aux_input[2], align = aux_input[3])
            bpy.ops.uv.sphere_project(seam=False, correct_aspect=False, clip_to_bounds=False, scale_to_bounds=False, direction='VIEW_ON_POLES', align = 'POLAR_ZX')
        elif uv_unwrap_method == 4: # Cubic unwrap
            bpy.ops.uv.cube_project(cube_size=aux_input[0], correct_aspect=aux_input[1], clip_to_bounds=aux_input[2], scale_to_bounds=aux_input[3])
        elif uv_unwrap_method == 5: # Camera unwrap
            bpy.ops.uv.project_from_view(camera_bounds=aux_input[0], scale_to_bounds=aux_input[1])
        # Pack UV Islands to minimize texture stretching
        bpy.ops.uv.pack_islands(margin=0.01)
        # Switch back to Object mode
        bpy.ops.object.mode_set(mode='OBJECT')
        print("UV Unwrapping and texture application completed!")

    def load_material(material_name:str, state: State):
        """ This function load a shading tree saved in a .json format and stores it into a new material
        Args:
            material_name (str): _description_

        Returns:
            _type_: _description_
        """
        # Path to the JSON file that contains the node group data
        json_path = state.path["material_name"]
        # Load the JSON data
        with open(json_path, 'r') as json_file:
            node_data = json.load(json_file)

        # Create a new material (or use an existing one)
        if material_name not in bpy.data.materials:
            material = bpy.data.materials.new(name=material_name)
        else:
            material = bpy.data.materials[material_name]

        material.use_nodes = True
        node_tree = material.node_tree

        # Clear any existing nodes (if any)
        nodes = node_tree.nodes
        nodes.clear()
        # Dictionary to hold the created nodes by their names for linking purposes
        node_map = {}
        # Function to recreate nodes from JSON data
        def create_node(node_info):
            # Create a new node in the node tree
            new_node = node_tree.nodes.new(type=node_info["type"])
            new_node.name = node_info["name"]
            new_node.location = node_info["location"]
            # Restore inputs
            for input_name, input_value in node_info["inputs"].items():
                if input_name in new_node.inputs and input_value is not None:
                    new_node.inputs[input_name].default_value = input_value
            # Add the node to the node_map for future linking
            node_map[new_node.name] = new_node
        # Recreate all nodes from the JSON data
        for node_info in node_data["nodes"]:
            create_node(node_info)
        # Function to recreate links between nodes
        def create_link(link_info):
            from_node = node_map[link_info["from_node"]]
            to_node = node_map[link_info["to_node"]]
            from_socket = from_node.outputs.get(link_info["from_socket"])
            to_socket = to_node.inputs.get(link_info["to_socket"])
            if from_socket and to_socket:
                node_tree.links.new(from_socket, to_socket)
        # Recreate all links from the JSON data
        for link_info in node_data["links"]:
            create_link(link_info)
    
        print(f"Shading tree successfully imported into the material '{material_name}'.")
        return material