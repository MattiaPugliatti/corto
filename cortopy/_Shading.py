from __future__ import annotations
from typing import Any, List, Mapping, Optional, Tuple, Union, overload

import numpy as np
import bpy
import json
import os
from cortopy import State
from cortopy import Body


class Shading:
    """
    Shading class
    """
    # *************************************************************************
    # *     Constructors & Destructors
    # *************************************************************************

    def __init__(self) -> None:
        """
        Constructor for the shading class
        """

    def create_new_material(name: str):
        """Creata a new empty material

        Args:
            name (str): name to assign to the material

        Returns:
            material (bpy.data.materials): New empty material
        """
        material = bpy.data.materials.new(name=name)
        material.use_nodes = True  # Enable use nodes
        # Get the material's node tree
        node_tree = material.node_tree
        # Clear any existing nodes (if any)
        nodes = node_tree.nodes
        nodes.clear()
        return material

    def create_simple_diffuse_BSDF(material, 
                                   BSDF_color_RGB=np.array([1, 0, 0])):
        """Generate a simple diffuse BSDF shader.

        Args:
            material (bpy.data.materials): Material
            color_RGB (np.array(3,), optional): . Defaults to np.array([1,0,0]).
        """

        #TODO: Debug
        """
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
        """

    def create_simple_principled_BSDF(
        material,
        PBSDF_color_RGB=np.array([1, 0, 0]),
        PBSDF_roughness:float=1,
        PBSDF_ior:float=180,
        PBSDF_coat_weight:float=0,
        PBSDF_coat_roughness:float=1,
        PBSDF_coat_tint=np.array([1, 0, 0]),
    ):
        """Generate a simple Principled BSDF shader.

        Args:
            material (bpy.data.materials): material 
            PBSDF_color_RGB (np.array, optional): color value. Defaults to np.array([1, 0, 0]).
            PBSDF_roughness (float, optional): roughness value. Defaults to 1.
            PBSDF_ior (float, optional): ior value. Defaults to 180.
            PBSDF_coat_weight (float, optional): _description_. Defaults to 0.
            PBSDF_coat_roughness (float, optional): coat weight value. Defaults to 1.
            PBSDF_coat_tint (np.array, optional): coat tint value. Defaults to np.array([1, 0, 0]).
        """
        nodes = material.node_tree.nodes
        # Create Principled BSDF node
        shader = nodes.new(type="ShaderNodeBsdfPrincipled") # TODO: update with new node method
        shader.location = (0, 0)
        # Create material output node
        output_node = nodes.new(type="ShaderNodeOutputMaterial") # TODO: update with new node method
        output_node.location = (200, 0)
        # Connect the Principled BSDF node to the Material Output node
        material.node_tree.links.new(
            shader.outputs["BSDF"], output_node.inputs["Surface"]
        )
        # Set the base color
        shader.inputs["Base Color"].default_value = (
            PBSDF_color_RGB[0],
            PBSDF_color_RGB[1],
            PBSDF_color_RGB[2],
            1,
        )  # RGBA
        # Set other PBSDF properties
        shader.inputs["Roughness"].default_value = PBSDF_roughness
        shader.inputs["IOR"].default_value = PBSDF_ior
        shader.inputs["Coat Weight"].default_value = PBSDF_coat_weight
        shader.inputs["Coat Roughness"].default_value = PBSDF_coat_roughness
        shader.inputs["Coat Tint"].default_value = (
            PBSDF_coat_tint[0],
            PBSDF_coat_tint[1],
            PBSDF_coat_tint[2],
            1,
        )  # RGBA

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

    def create_node(name: str, material, location=(0, 0)):
        """Generic method to create a node in the tree of a material

        Args:
            name (str): name of the node
            material (bpy.data.materials): material where to assign the node
            location (tuple, optional): location of the node in the nodetree. Defaults to (0, 0).

        Returns:
            node: node in the nodetree of the material
        """        
        
        node = material.node_tree.nodes.new(type=name)
        node.location = location
        return node

    def link_nodes(material, node_output, node_input):
        """Generic method to link two nodes toghether

        Args:
            material (bpy.data.materials):  material in which the two needs are contained
            node_output (material.node_tree.nodes): value from output node 
            node_input (material.node_tree.nodes): value from input node  
        """        
        material.node_tree.links.new(node_output, node_input)


    def texture_node(material, texture_path, colorspace_name='sRGB', location=(0, 0)):
        """method to create a texture node

        Args:
            material (bpy.data.materials): material in which the node is generated
            texture_path (string): filepath of the texture file
            colorspace_name (string, optional): colorspace of the texture map
            location (tuple, optional): location in the node tree. Defaults to (0, 0).

        Returns:
            node: node in the shading tree
        """        

        node = Shading.create_node("ShaderNodeTexImage", material, location)
        try:
            node.image = bpy.data.images.load(texture_path)
            bpy.data.images[os.path.basename(texture_path)].colorspace_settings.name = colorspace_name
        except:
            raise NameError(f"Failed to load image from {texture_path}")
       
        return node


    def displacement_node(material, location=(0, 0)):
        """method to create a displacement node

        Args:
            material (bpy.data.materials): material in which the node is generated
            location (tuple, optional): location in the node tree. Defaults to (0, 0).

        Returns:
            node: node in the shading tree
        """
        return Shading.create_node("ShaderNodeDisplacement", material, location)

    def mix_node(material, location=(0, 0)):
        """method to create a mix shader node

        Args:
            material (bpy.data.materials): material in which the node is generated
            location (tuple, optional): location in the node tree. Defaults to (0, 0).

        Returns:
            node: node in the shading tree
        """        
        return Shading.create_node("ShaderNodeMixShader", material, location)

    def diffuse_BSDF(material, location=(0, 0)):
        """method to create a diffuse BSDF node

        Args:
            material (bpy.data.materials): material in which the node is generated
            location (tuple, optional): location in the node tree. Defaults to (0, 0).

        Returns:
            node: node in the shading tree
        """        
        return Shading.create_node("ShaderNodeBsdfDiffuse", material, location)

    def principled_BSDF(material, location=(0, 0)):
        """method to create a principled BSDF node

        Args:
            material (bpy.data.materials): material in which the node is generated
            location (tuple, optional): location in the node tree. Defaults to (0, 0).

        Returns:
            node: node in the shading tree
        """
        return Shading.create_node("ShaderNodeBsdfPrincipled", material, location)

    def material_output(material, location=(0, 0)):
        """method to create a material output node

        Args:
            material (bpy.data.materials): material in which the node is generated
            location (tuple, optional): location in the node tree. Defaults to (0, 0).

        Returns:
            node: node in the shading tree
        """        
        return Shading.create_node("ShaderNodeOutputMaterial", material, location)

    def uv_map(material, location=(0, 0)):
        """method to create a uv mapping node

        Args:
            material (bpy.data.materials): material in which the node is generated
            location (tuple, optional): location in the node tree. Defaults to (0, 0).

        Returns:
            node: node in the shading tree
        """        
        return Shading.create_node("ShaderNodeUVMap", material, location)
        

    def lambert(material, state: State, settings, id_body: int = None):
        """method to create an Oren-Nayar shading tree with optional albedo and displacement textures

        Args:
            material (bpy.data.materials): material in which the node is generated
            state (corto.State): State object, used for paths handling

        Returns:
            node: node in the shading tree
        """     
        
        # Use an Oren-Nayar model with 0 roughness
        settings['albedo']['roughness'] = 0
        material = Shading.oren(material, state, settings, id_body)
        

    def oren(material, state: State, settings, id_body: int = None):
        """method to create an Oren-Nayar shading tree with optional albedo and displacement textures

        Args:
            material (bpy.data.materials): material in which the node is generated
            state (corto.State): State object, used for paths handling

        Returns:
            node: node in the shading tree
        """     

        if id_body is not None:
            # Convert id_body to string to concatenate with the path key
            albedo_path_key = f"albedo_path_{id_body}"
            displacement_path_key = f"displacement_path_{id_body}"
        else:
            # Default texture key if id_body is not provided
            albedo_path_key = "albedo_path"
            displacement_path_key = "displacement_path"

        # BSDF Node
        diffuse_BSDF_node = Shading.diffuse_BSDF(material, (0, 200))
        diffuse_BSDF_node.inputs[1].default_value = settings['albedo']['roughness']
        # Output node
        material_node = Shading.material_output(material, (600, 0))

        # From color to output
        Shading.link_nodes(material, 
            diffuse_BSDF_node.outputs["BSDF"], 
            material_node.inputs["Surface"]
        )

        if albedo_path_key in state.path:
            # Albedo texture node
            albedo_texture = Shading.texture_node(material, state.path["albedo_path"], settings['albedo']['colorspace_name'], (-400, 0))
            # From albedo texture to color
            Shading.link_nodes(material,
                albedo_texture.outputs["Color"],
                diffuse_BSDF_node.inputs["Color"],
            )

        if displacement_path_key in state.path:
            # Displacement texture node
            displacement_texture =  Shading.texture_node(material, state.path["displacement_path"], settings['displacement']['colorspace_name'], (500, -200))
            displacement_node = Shading.displacement_node(material, (700, -200))
            displacement_node.inputs[2].default_value = settings['displacement']['scale']
            displacement_node.inputs[1].default_value =  settings['displacement']['mid_level'] 
            # From displacement texture to displacement
            Shading.link_nodes(material, 
                displacement_texture.outputs["Color"],
                displacement_node.inputs["Height"]
            )
            # From displacement to output
            Shading.link_nodes(material,
                displacement_node.outputs["Displacement"],
                material_node.inputs["Displacement"],
            )


    def create_branch_albedo_mix(material, state: State, id_body: int = None):
        """method to create a complex shading tree with albedo texture and mix shaders

        Args:
            material (bpy.data.materials): material in which the node is generated
            state (corto.State): State object, used for paths handling
            id_body (int): extra input for multiple bodies case

        Returns:
            node: node in the shading tree
        """
        if id_body is not None:
            # Convert id_body to string to concatenate with the path key
            albedo_path_key = f"albedo_path_{id_body}"
        else:
            # Default texture key if id_body is not provided
            albedo_path_key = "albedo_path"
        if albedo_path_key not in state.path:
            raise Exception('No albedo texture found at the specified path')
        albedo_texture = Shading.texture_node(material, state.path[albedo_path_key], location=(-400, 0))
        mix_node = Shading.mix_node(material, (400, 0))
        mix_node.inputs[0].default_value = 0.95
        diffuse_BSDF_node = Shading.diffuse_BSDF(material, (0, 200))
        principled_BSDF_node = Shading.principled_BSDF(material, (0, 0))
        material_node = Shading.material_output(material, (600, 0))
        uv_map_node = Shading.uv_map(material, (-600, 0))

        Shading.link_nodes(
            material,
            albedo_texture.outputs["Color"],
            principled_BSDF_node.inputs["Base Color"],
        )
        Shading.link_nodes(
            material, diffuse_BSDF_node.outputs["BSDF"], mix_node.inputs[1]
        )
        Shading.link_nodes(
            material, principled_BSDF_node.outputs["BSDF"], mix_node.inputs[2]
        )
        Shading.link_nodes(
            material, mix_node.outputs["Shader"], material_node.inputs["Surface"]
        )
        Shading.link_nodes(
            material, uv_map_node.outputs["UV"], albedo_texture.inputs["Vector"]
        )

    def create_branch_albedo_and_displacement_mix(material, state: State, settings, id_body: int = None):
        """method to create a complex shading tree with albedo texture, displacement texture and mix shaders

        Args:
            material (bpy.data.materials): material in which the node is generated
            state (corto.State): State object, used for paths handling

        Raises:
            Exception: failure to load albedo texture
            Exception: failure to load displacement texture 
        """
        if id_body is not None:
            # Convert id_body to string to concatenate with the path key
            albedo_path_key = f"albedo_path_{id_body}"
            displacement_path_key = f"displacement_path_{id_body}"
        else:
            # Default texture key if id_body is not provided
            albedo_path_key = "albedo_path"
            displacement_path_key = "displacement_path"
        
        if albedo_path_key not in state.path:
            raise Exception('No albedo texture found at the specified path')
        if displacement_path_key not in state.path:
            raise Exception('No displacement texture found at the specified path')
        
        albedo_texture = Shading.texture_node(material, state.path[albedo_path_key], location=(-400, 0))
        displacement_texture = Shading.texture_node(material, state.path[displacement_path_key], settings['displacement']['colorspace_name'], location=(500, -200))
        
        mix_node = Shading.mix_node(material, (400, 0))
        mix_node.inputs[0].default_value = settings['albedo']['weight_diffuse']
        diffuse_BSDF_node = Shading.diffuse_BSDF(material, (0, 200))
        principled_BSDF_node = Shading.principled_BSDF(material, (0, 0))
        material_node = Shading.material_output(material, (600, 0))
        displacement_node = Shading.displacement_node(material, (700, -200))
        displacement_node.inputs[2].default_value = settings['displacement']['scale']
        displacement_node.inputs[1].default_value =  settings['displacement']['mid_level'] 

        Shading.link_nodes(
            material,
            albedo_texture.outputs["Color"],
            principled_BSDF_node.inputs["Base Color"],
        )
        Shading.link_nodes(
            material, diffuse_BSDF_node.outputs["BSDF"], mix_node.inputs[1]
        )
        Shading.link_nodes(
            material, principled_BSDF_node.outputs["BSDF"], mix_node.inputs[2]
        )
        Shading.link_nodes(
            material, mix_node.outputs["Shader"], material_node.inputs["Surface"]
        )
        Shading.link_nodes(
            material, displacement_texture.outputs["Color"], displacement_node.inputs["Height"]
        )
        Shading.link_nodes(
            material,
            displacement_node.outputs["Displacement"],
            material_node.inputs["Displacement"],
        )

    def uv_unwrap(uv_unwrap_method: int, aux_input: list, body: Body):
        """method to perform uv unwrapping

        Args:
            uv_unwrap_method (int): index for the unwrap method (1) standard, (2) cylinder, (3) spherical, (4) cubic, (5) camera
            aux_input (list): list of auxiliar inputs needed by the unwrapping method
            body (Body): corto Body object on which to perform the unwrap

        Raises:
            Exception: Object BODY not found in the scene
        """
        # TODO: add error check for aux_input
        # TODO: bpy bug, the settings of the uv-unwrap are automatically defaulted and not applied correctly to the texture
        # prefer serialization with .json instead

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
        if bpy.context.object.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        # Switch to Edit mode to UV unwrap
        bpy.ops.object.mode_set(mode="EDIT")
        # Select all the mesh's faces in Edit mode
        bpy.ops.mesh.select_all(action="SELECT")
        if uv_unwrap_method == 1:  # Standard unwrap
            bpy.ops.uv.unwrap(method=aux_input[0], margin=aux_input[1])
        elif uv_unwrap_method == 2:  # Cylinder unwrap
            bpy.ops.uv.cylinder_project(direction=aux_input[0], align=aux_input[1])
        elif uv_unwrap_method == 3:  # Spherical unwrap
            # bpy.ops.uv.sphere_project(clip_to_bounds=aux_input[0], scale_to_bounds=aux_input[1], correct_aspect=False, direction=aux_input[2], align = aux_input[3])
            bpy.ops.uv.sphere_project(
                seam=False,
                correct_aspect=False,
                clip_to_bounds=False,
                scale_to_bounds=False,
                direction="VIEW_ON_POLES",
                align="POLAR_ZX",
            )
        elif uv_unwrap_method == 4:  # Cubic unwrap
            bpy.ops.uv.cube_project(
                cube_size=aux_input[0],
                correct_aspect=aux_input[1],
                clip_to_bounds=aux_input[2],
                scale_to_bounds=aux_input[3],
            )
        elif uv_unwrap_method == 5:  # Camera unwrap
            bpy.ops.uv.project_from_view(
                camera_bounds=aux_input[0], scale_to_bounds=aux_input[1]
            )
        # Pack UV Islands to minimize texture stretching
        bpy.ops.uv.pack_islands(margin=0.01)
        # Switch back to Object mode
        bpy.ops.object.mode_set(mode="OBJECT")
        print("UV Unwrapping and texture application completed!")

    def load_material(material_name: str, state: State):
        """This method load a shading tree serialized in a .json format and stores it into a new material
        Args:
            material_name (str): name of the material 
            state (corto.State): State object, for path handling

        Returns:
            _type_: _description_
        """
        # TODO: add error check on existence of path in state.path[] dict

        # Path to the JSON file that contains the node group data
        json_path = state.path["material_name"]
        # Load the JSON data
        with open(json_path, "r") as json_file:
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

        print(
            f"Shading tree successfully imported into the material '{material_name}'."
        )
        return material

    def load_uv_data(body: Body, state: State, id_body: int = None):
        """This method load a shading tree serialized in a .json format and stores it into a new material
        Args:
            material_name (str): name of the material 
            state (corto.State): State object, for path handling
            id_body (int): extra input for multiple bodies case

        Returns:
            _type_: _description_
        """
        if id_body is not None:
            # Convert id_body to string to concatenate with the path key
            uv_key = f"uv_data_path_{id_body}"
        else:
            # Default uv key if id_body is not provided
            uv_key = "uv_data_path"

        obj = bpy.data.objects[body.name]
        # Ensure the object has UV data
        if obj.data.uv_layers.active is None:
            obj.data.uv_layers.new(name='ImportedUV')
        uv_layer = obj.data.uv_layers.active.data
        # Load the UV data from the file
        with open(state.path[uv_key], 'r') as file:
            uv_data = json.load(file)
        # Ensure the number of faces matches
        if len(uv_data) != len(obj.data.polygons):
            raise Exception("The number of polygons in the target object does not match the source UV data.")
        # Apply UV data
        for poly, poly_uvs in zip(obj.data.polygons, uv_data):
            for loop_index, uv in zip(poly.loop_indices, poly_uvs):
                uv_layer[loop_index].uv = (uv[0], uv[1])
        print(f"UV data imported to {body.name}")