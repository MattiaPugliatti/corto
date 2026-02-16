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
    NODE_TYPES = {
        # Textures
        "texture_magic_node": "ShaderNodeTexMagic",
        "texture_wave_node": "ShaderNodeTexWave",
        "texture_noise_node": "ShaderNodeTexNoise",
        "texture_coordinate_node": "ShaderNodeTexCoord",
        "uv_map_node": "ShaderNodeUVMap",

        # Converters / utilities
        "color_ramp_node": "ShaderNodeValToRGB",
        "map_range_node": "ShaderNodeMapRange",
        "blackbody_node": "ShaderNodeBlackbody",
        "math_node": "ShaderNodeMath",
        "vector_math_node": "ShaderNodeVectorMath",
        "normal_node": "ShaderNodeNormal",
        "value_node": "ShaderNodeValue",
        "mix_node": "ShaderNodeMix",
        "geometry_node": "ShaderNodeNewGeometry",
        "script_node": "ShaderNodeScript",
        
        # Shaders
        "diffuse_BSDF": "ShaderNodeBsdfDiffuse",
        "principled_BSDF": "ShaderNodeBsdfPrincipled",
        "transparent_shader": "ShaderNodeBsdfTransparent",
        "subsurface_shader": "ShaderNodeSubsurfaceScattering",
        "volume_shader": "ShaderNodeVolumeScatter",
        "mix_shader_node": "ShaderNodeMixShader",
        "displacement_node": "ShaderNodeDisplacement",

        # Outputs
        "material_output": "ShaderNodeOutputMaterial",
    }

    # *************************************************************************
    # *     Constructors & Destructors
    # *************************************************************************

    def __init__(self) -> None:
        """
        Constructor for the shading class
        """

    def create_new_material(name: str, displace_and_bump:str = None):
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
        # Toggle Displace and Bump property
        if displace_and_bump is not None:
            material.displacement_method = displace_and_bump #TODO: this does not really affect the final material properties!
        return material

    def print_material_node_tree(material):
        """Prints all nodes and their input sockets for a material's node tree.

        Args:
            material (bpy.types.Material): The material to inspect.
        """
        if not material.use_nodes:
            print(f"Material '{material.name}' does not use nodes.")
            return
        print(f"\nMaterial: {material.name} - Node Tree:")
        for node in material.node_tree.nodes:
            print(f"  Node: {node.name} ({node.bl_idname})")
            for input_socket in node.inputs:
                print(f"    Input: {input_socket.name} | Default: {getattr(input_socket, 'default_value', 'N/A')}")

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
        PBSDF_metallic: float = 0,
        PBSDF_roughness: float = 1,
        PBSDF_ior:float=180,
        PBSDF_coat_weight:float=0,
        PBSDF_coat_roughness:float=1,
        PBSDF_coat_tint=np.array([1, 0, 0]),
    ):
        """Generate a simple Principled BSDF shader.

        Args:
            material (bpy.data.materials): material 
            PBSDF_color_RGB (np.array, optional): color value. Defaults to np.array([1, 0, 0]).
            PBSDF_metallic (float, optional): metallic value. Defaults to 0.
            PBSDF_roughness (float, optional): roughness value. Defaults to 1.
            PBSDF_ior (float, optional): ior value. Defaults to 180.
            PBSDF_coat_weight (float, optional): _description_. Defaults to 0.
            PBSDF_coat_roughness (float, optional): coat weight value. Defaults to 1.
            PBSDF_coat_tint (np.array, optional): coat tint value. Defaults to np.array([1, 0, 0]).
        """
        ## Part 1 - Create all necessary nodes
        shader_node = Shading.principled_BSDF(material, (0, 0))
        output_node = Shading.material_output(material, (200, 0))

        ## Part 2 - Setup nodes properties
        shader_node.inputs["Base Color"].default_value = (
            PBSDF_color_RGB[0],
            PBSDF_color_RGB[1],
            PBSDF_color_RGB[2],
            1,
        ) 
        shader_node.inputs["Coat Tint"].default_value = (
            PBSDF_coat_tint[0],
            PBSDF_coat_tint[1],
            PBSDF_coat_tint[2],
            1,
        )
        shader_node.inputs["Metallic"].default_value = PBSDF_metallic
        shader_node.inputs["Roughness"].default_value = PBSDF_roughness
        shader_node.inputs["IOR"].default_value = PBSDF_ior
        shader_node.inputs["Coat Weight"].default_value = PBSDF_coat_weight
        shader_node.inputs["Coat Roughness"].default_value = PBSDF_coat_roughness

        ## Part 3 - Link nodes toghether
        Shading.link_nodes(material,shader_node.outputs["BSDF"],output_node.inputs["Surface"]) # PBSDF to output

    def create_randomized_texturePBSDF(
        material,
        wave_scale: float = 5, 
        wave_distortion: float = 0, 
        wave_detail: float = 2, 
        wave_detail_scale: float = 1, 
        wave_detail_roughness: float = 0.5, 
        magic_scale: float = 5, 
        magic_distortion: float = 1, 
        noise_scale: float = 5, 
        noise_detail: float = 2,
        noise_roughness: float = 0.5, 
        noise_lacunarity: float = 2, 
        noise_distortion: float = 0, 
        mix_1_fac: float = 0.5,
        mix_2_fac: float = 0.5,
        PBSDF_color_RGB = np.array([0, 0, 0]),
        PBSDF_metallic: float = 1,
        PBSDF_roughness: float = 1,
        PBSDF_ior: float = 180,
        PBSDF_coat_weight: float = 0,
        PBSDF_coat_roughness: float = 1,
        PBSDF_coat_tint = np.array([0, 0, 0]),
    ):
        """Generate a simple randomizd PBSDF shader.

        Args:
            material (bpy.data.materials): material 
            PBSDF_color_RGB (np.array, optional): color value. Defaults to np.array([1, 0, 0]).
            PBSDF_metallic (float, optional): metallic value. Defaults to 0.
            PBSDF_roughness (float, optional): roughness value. Defaults to 1.
            PBSDF_ior (float, optional): ior value. Defaults to 180.
            PBSDF_coat_weight (float, optional): _description_. Defaults to 0.
            PBSDF_coat_roughness (float, optional): coat weight value. Defaults to 1.
            PBSDF_coat_tint (np.array, optional): coat tint value. Defaults to np.array([1, 0, 0]).
        """
        ## Part 1 - Create all necessary nodes
        texture_coordinate_node = Shading.texture_coordinate_node(material,(0,0))
        texture_wave_node = Shading.texture_wave_node(material,(200,400))
        texture_magic_node = Shading.texture_magic_node(material,(200,0))
        texture_noise_node = Shading.texture_noise_node(material,(200,-400))
        color_ramp_node = Shading.color_ramp_node(material, (400, 200))
        mix_1_node = Shading.mix_node(material, (800, 200))
        mix_2_node = Shading.mix_node(material, (1200, 100))
        shader_node = Shading.principled_BSDF(material, (1600, 0))
        output_node = Shading.material_output(material, (2000, 0))

        ## Part 2 - Setup nodes properties
        # Wave node
        texture_wave_node.wave_type = 'RINGS'
        texture_wave_node.rings_direction = 'SPHERICAL'
        texture_wave_node.wave_profile = 'TRI'
        texture_wave_node.inputs["Scale"].default_value = wave_scale
        texture_wave_node.inputs["Distortion"].default_value = wave_distortion
        texture_wave_node.inputs["Detail"].default_value = wave_detail
        texture_wave_node.inputs["Detail Scale"].default_value = wave_detail_scale
        texture_wave_node.inputs["Detail Roughness"].default_value = wave_detail_roughness
        # Magic node
        texture_magic_node.inputs["Scale"].default_value = magic_scale
        texture_magic_node.inputs["Distortion"].default_value = magic_distortion
        # Noise node
        texture_noise_node.inputs["Scale"].default_value = noise_scale
        texture_noise_node.inputs["Detail"].default_value = noise_detail
        texture_noise_node.inputs["Roughness"].default_value = noise_roughness
        texture_noise_node.inputs["Lacunarity"].default_value = noise_lacunarity
        texture_noise_node.inputs["Distortion"].default_value = noise_distortion
        # Mix nodes
        mix_1_node.inputs["Factor"].default_value = mix_1_fac
        mix_2_node.inputs["Factor"].default_value = mix_2_fac
        # Color-Ramp node
        color_ramp_node.color_ramp.elements[0].position = 0.1
        color_ramp_node.color_ramp.color_mode = 'RGB'
        color_ramp_node.color_ramp.elements[0].color = (0.658, 0.658, 0.658, 1)
        # PBDSF node
        shader_node.inputs["Base Color"].default_value = (
            PBSDF_color_RGB[0],
            PBSDF_color_RGB[1],
            PBSDF_color_RGB[2],
            1,
        ) 
        shader_node.inputs["Coat Tint"].default_value = (
            PBSDF_coat_tint[0],
            PBSDF_coat_tint[1],
            PBSDF_coat_tint[2],
            1,
        )
        shader_node.inputs["Metallic"].default_value = PBSDF_metallic
        shader_node.inputs["Roughness"].default_value = PBSDF_roughness
        shader_node.inputs["IOR"].default_value = PBSDF_ior
        shader_node.inputs["Coat Weight"].default_value = PBSDF_coat_weight
        shader_node.inputs["Coat Roughness"].default_value = PBSDF_coat_roughness

        ## Part 3 - Link nodes toghether
        Shading.link_nodes(material,texture_wave_node.outputs["Fac"],color_ramp_node.inputs["Fac"]) 
        Shading.link_nodes(material,color_ramp_node.outputs["Color"],mix_1_node.inputs["A"]) 
        Shading.link_nodes(material,texture_magic_node.outputs["Fac"],mix_1_node.inputs["B"]) 
        Shading.link_nodes(material,texture_noise_node.outputs["Fac"],mix_2_node.inputs["B"]) 
        Shading.link_nodes(material,mix_1_node.outputs["Result"],mix_2_node.inputs["A"]) 
        Shading.link_nodes(material,mix_2_node.outputs["Result"],shader_node.inputs["Base Color"]) 
        Shading.link_nodes(material,shader_node.outputs["BSDF"],output_node.inputs["Surface"]) # PBSDF to output
        Shading.link_nodes(material,texture_coordinate_node.outputs["Object"],texture_wave_node.inputs["Vector"])
        Shading.link_nodes(material,texture_coordinate_node.outputs["Object"],texture_magic_node.inputs["Vector"])
        Shading.link_nodes(material,texture_coordinate_node.outputs["Object"],texture_noise_node.inputs["Vector"])

    def update_randomized_texturePBSDF(material, settings:dict):
        """Update properties of a simple randomizd PBSDF shader.

        Args:
            material (bpy.data.materials): Material
            settings (dict): Dictionary with settings for the update
        """
        # Update values in the "Wave Texture" node 
        material.node_tree.nodes["Wave Texture"].inputs["Scale"].default_value = settings["wave_scale"]
        material.node_tree.nodes["Wave Texture"].inputs["Distortion"].default_value = settings["wave_distortion"]
        material.node_tree.nodes["Wave Texture"].inputs["Detail"].default_value = settings["wave_detail"]
        material.node_tree.nodes["Wave Texture"].inputs["Detail Scale"].default_value = settings["wave_detail_scale"]
        material.node_tree.nodes["Wave Texture"].inputs["Detail Roughness"].default_value = settings["wave_detail_roughness"]
        # Update values in the "Magic Texture" node
        material.node_tree.nodes["Magic Texture"].inputs["Scale"].default_value = settings["magic_scale"]
        material.node_tree.nodes["Magic Texture"].inputs["Distortion"].default_value = settings["magic_distortion"]
        # Update values in the "Noise Texture" node
        material.node_tree.nodes["Noise Texture"].inputs["Scale"].default_value = settings["noise_scale"]
        material.node_tree.nodes["Noise Texture"].inputs["Detail"].default_value = settings["noise_detail"]
        material.node_tree.nodes["Noise Texture"].inputs["Roughness"].default_value = settings["noise_roughness"]
        material.node_tree.nodes["Noise Texture"].inputs["Lacunarity"].default_value = settings["noise_lacunarity"]
        material.node_tree.nodes["Noise Texture"].inputs["Distortion"].default_value = settings["noise_distortion"]
        # Update values in the "Mix" nodes (wave + magic) and ((wave + magic) + noise)
        material.node_tree.nodes["Mix"].inputs["Factor"].default_value = settings["mix_1_fac"]
        material.node_tree.nodes["Mix.001"].inputs["Factor"].default_value = settings["mix_2_fac"]

    def create_earth_shader(material, state:State, settings: dict = None):
        """Generate Earth-based PBSDF shader. This contains clouds, land-ocean map, nightlight, and atmospheric effects

        Args:
            material (bpy.data.materials): Material
            state (corto.State): CORTO state object
            settings (dict): Dictionary with settings for this particular shader
        """

        ## Part 1 - Create all necessary nodes
        # Create input image-texture nodes
        earth_color = Shading.texture_node(material, state.path["earth_color"], 'sRGB', (-400, 600))
        earth_landocean = Shading.texture_node(material, state.path["earth_landocean"], 'Non-Color', (-400, 200))
        earth_displacement = Shading.texture_node(material, state.path["earth_displacement"], 'Non-Color', (-400, -200))   
        earth_night = Shading.texture_node(material, state.path["earth_night"], 'Non-Color', (-400, -600))
        # Create principled BSDF node
        shader = Shading.principled_BSDF(material, location=(800, 0))
        # Create material output node
        output_node = Shading.material_output(material, location = (1200, -400))
        # Create Hue saturation node
        hueSaturation_node = Shading.hue_saturation_node(material, location = (200, 400))
        # Create Displacement node
        displacement_node = Shading.displacement_node(material, location =(200,-200))
        # Create texture coordinate node
        texture_coord_node = Shading.texture_coordinate_node(material, location =(-400,-1000))
        # Create Normal node
        normal_node = Shading.normal_node(material, location =(-200,-1000))
        # Create Map Range node
        map_range_node_land = Shading.map_range_node(material, location = (0,200))
        map_range_node_night = Shading.map_range_node(material, location = (0,-1000))
        # Create Map Range node
        blackbody_node = Shading.blackbody_node(material, location =(600,-400))
        # Create Multiply node
        math_node = Shading.math_node(material, location =(600,-600))

        ## Part 2 - Setup nodes properties

        # land-ocean props
        hueSaturation_node.inputs["Hue"].default_value = settings['albedo']['hue']
        hueSaturation_node.inputs["Saturation"].default_value = settings['albedo']['saturation']
        hueSaturation_node.inputs["Value"].default_value = settings['albedo']['hue_scale']
        map_range_node_land.inputs["From Min"].default_value = settings['albedo']['land_ocean_from_min']
        map_range_node_land.inputs["From Max"].default_value = settings['albedo']['land_ocean_from_max']
        map_range_node_land.inputs["To Min"].default_value = settings['albedo']['land_ocean_to_min']
        map_range_node_land.inputs["To Max"].default_value = settings['albedo']['land_ocean_to_max']
        # toplogy props
        displacement_node.inputs["Midlevel"].default_value = settings['displacement']['earth_midlevel']
        displacement_node.inputs["Scale"].default_value = settings['displacement']['earth_scale']
        # Nightlights props
        blackbody_node.inputs["Temperature"].default_value = settings['albedo']['night_temperature']
        math_node.operation = 'MULTIPLY'
        math_node.use_clamp = True
        texture_coord_node.object = bpy.data.objects["Sun"]
        map_range_node_night.inputs["From Min"].default_value = settings['albedo']['night_from_min']
        map_range_node_night.inputs["From Max"].default_value = settings['albedo']['night_from_max']
        map_range_node_night.inputs["To Min"].default_value = settings['albedo']['night_to_min']
        map_range_node_night.inputs["To Max"].default_value = settings['albedo']['night_to_max']

        ## Part 3 - Link nodes toghether

        # Land-Ocean pipeline
        Shading.link_nodes(material,earth_color.outputs["Color"],hueSaturation_node.inputs["Color"])
        Shading.link_nodes(material,earth_landocean.outputs["Color"],hueSaturation_node.inputs["Fac"])
        Shading.link_nodes(material,earth_landocean.outputs["Color"],map_range_node_land.inputs["Value"])
        Shading.link_nodes(material,map_range_node_land.outputs["Result"],shader.inputs["Roughness"])
        Shading.link_nodes(material,hueSaturation_node.outputs["Color"],shader.inputs["Base Color"])
        # Topology pipeline
        Shading.link_nodes(material,earth_displacement.outputs["Color"],displacement_node.inputs["Height"])
        Shading.link_nodes(material,displacement_node.outputs["Displacement"],output_node.inputs["Displacement"])
        # Nightlights pipeline
        Shading.link_nodes(material,earth_night.outputs["Color"],math_node.inputs[0])
        Shading.link_nodes(material,math_node.outputs["Value"],shader.inputs["Emission Strength"])
        Shading.link_nodes(material,texture_coord_node.outputs["Object"],normal_node.inputs["Normal"])
        Shading.link_nodes(material,normal_node.outputs["Dot"],map_range_node_night.inputs["Value"])
        Shading.link_nodes(material,map_range_node_night.outputs["Result"],math_node.inputs[1])
        Shading.link_nodes(material,blackbody_node.outputs["Color"],shader.inputs["Emission Color"])
        # PBSDF to output
        Shading.link_nodes(material,shader.outputs["BSDF"],output_node.inputs["Surface"])

    def create_atmosphere_shader(material, settings):
        """Generate Earth-based PBSDF shader. This contains volumetric scattering amtospheric effects

        Args:
            material (bpy.data.materials): Material
            settings (dict): Dictionary with settings for this particular shader
        """
        # Create principled BSDF node
        shader = Shading.volume_shader(material, location=(800, 0))
        # Create material output node
        output_node = Shading.material_output(material, location = (1200, -400))
        # Shader properties
        shader.inputs["Color"].default_value = settings['atm_color']
        shader.inputs["Density"].default_value = settings['atm_density']
        shader.inputs["Anisotropy"].default_value = settings['atm_anisotropy']

        Shading.link_nodes(material,shader.outputs["Volume"],output_node.inputs["Volume"])

    def create_clouds_shader(material, state:State, settings):
        """Generate Earth-based PBSDF shader. This contains clouds 

        Args:
            material (bpy.data.materials): Material
            state (corto.State): CORTO state object
            settings (dict): Dictionary with settings for this particular shader
        """

        ## Part 1 - Create all necessary nodes
        # Clouds shaders
        clouds_color = Shading.texture_node(material, state.path["earth_clouds"], 'Non-Color', (0, 0))
        subsurface_shader = Shading.subsurface_shader(material, location = (400, 400))
        transparent_shader = Shading.transparent_shader(material, location = (400, 800))
        mix_shader = Shading.mix_shader_node(material, location = (800,600))
        # Create material output node
        output_node = Shading.material_output(material, location = (1200, 0))
        displacement_node = Shading.displacement_node(material, location = (800, -400))

        ## Part 2 - Setup nodes properties
        # Subsurface props
        subsurface_shader.inputs["Radius"].default_value[0] = settings["albedo"]["radius_0"]
        subsurface_shader.inputs["Radius"].default_value[1] = settings["albedo"]["radius_1"]
        subsurface_shader.inputs["Radius"].default_value[2] = settings["albedo"]["radius_2"]
        subsurface_shader.inputs["Scale"].default_value = settings["albedo"]["subsurf_scale"]
        # Displace props
        displacement_node.inputs["Midlevel"].default_value = settings["displacement"]["clouds_midlevel"]
        displacement_node.inputs["Scale"].default_value =settings["displacement"]["clouds_scale"]

        ## Part 3 - Link nodes toghether
        Shading.link_nodes(material,clouds_color.outputs["Color"],displacement_node.inputs["Height"])
        Shading.link_nodes(material,subsurface_shader.outputs["BSSRDF"],mix_shader.inputs[2])
        Shading.link_nodes(material,transparent_shader.outputs["BSDF"],mix_shader.inputs[1])
        Shading.link_nodes(material,clouds_color.outputs["Color"],mix_shader.inputs["Fac"])
        Shading.link_nodes(material,mix_shader.outputs["Shader"],output_node.inputs["Surface"])
        Shading.link_nodes(material,displacement_node.outputs["Displacement"],output_node.inputs["Displacement"])

    def create_lunar_shader(material, 
                            state:State):
        ## Part 1 - Create all necessary nodes
        mix_shader1_node = Shading.mix_shader_node(material, location = (800,-400))
        mix_shader2_node = Shading.mix_shader_node(material, location = (1200,-400))
        output_node = Shading.material_output(material, location = (2000, -400))
        displacement_node = Shading.displacement_node(material, location = (1200, -600))
        texture_basecolor_node = Shading.texture_node(material, state.path["texture_path"], colorspace_name='sRGB', location=(0, 200))
        texture_dem_node = Shading.texture_node(material, state.path["DEM_path"], colorspace_name='Non-Color', location=(800, -200))
        diffuse_BSDF_node = Shading.diffuse_BSDF(material, location = (400, -200))
        principled_BSDF_node = Shading.principled_BSDF(material, location=(400, -600))
        ## Part 2 - Setup nodes properties
        texture_basecolor_node.interpolation = 'Cubic'
        texture_dem_node.interpolation = 'Cubic'
        diffuse_BSDF_node.inputs[1].default_value = 0.95
        mix_shader1_node.inputs[0].default_value = 0.65
        principled_BSDF_node.inputs['Roughness'].default_value = 0.25
        mix_shader2_node.inputs[0].default_value = 0.25
        displacement_node.inputs["Midlevel"].default_value = 0.5
        displacement_node.inputs["Scale"].default_value = 3.5

        ## Part 3 - Link nodes toghether
        Shading.link_nodes(material,texture_basecolor_node.outputs["Color"],diffuse_BSDF_node.inputs["Color"])
        Shading.link_nodes(material,texture_basecolor_node.outputs["Color"],principled_BSDF_node.inputs["Base Color"])
        Shading.link_nodes(material,diffuse_BSDF_node.outputs["BSDF"],mix_shader1_node.inputs[1])
        Shading.link_nodes(material,principled_BSDF_node.outputs["BSDF"],mix_shader1_node.inputs[2])
        Shading.link_nodes(material,mix_shader1_node.outputs["Shader"],mix_shader2_node.inputs[2])
        Shading.link_nodes(material,mix_shader2_node.outputs["Shader"],output_node.inputs["Surface"])
        Shading.link_nodes(material,texture_dem_node.outputs["Color"],displacement_node.inputs["Height"])
        Shading.link_nodes(material,displacement_node.outputs["Displacement"],output_node.inputs["Displacement"])

    def create_osl_shader(
        material,
        function: str, 
        geometric_albedo: float,
        disk_function_path: str, 
        phase_function_path: str,
        osl_coeffs: dict = None,
    ):
        """Generate a shader with OSL

        Args:
            material (bpy.data.materials): material 

        """
        bpy.context.scene.render.engine = 'CYCLES'
        bpy.context.scene.cycles.shading_system = True  # Enable OSL

        ## Part 1 - Create all necessary nodes
        output_node = Shading.material_output(material, (2000, 0))
        dot_product_node_1 =  Shading.vector_math_node(material, (800, +200))
        dot_product_node_2 =  Shading.vector_math_node(material, (800, -200))
        arcosine_node_1 = Shading.math_node(material, (1000, +200))
        arcosine_node_2 = Shading.math_node(material, (1000, -200))
        subtract_node_1 = Shading.vector_math_node(material, (400, 200))
        subtract_node_2 = Shading.vector_math_node(material, (400, -200))
        normalize_node_2 = Shading.vector_math_node(material, (600, -200))
        normalize_node_1 = Shading.vector_math_node(material, (600, 200))
        geometry_node = Shading.geometry_node(material, (200,0))
        disk_function_node = Shading.script_node(material, (1200,0))
        phase_function_node = Shading.script_node(material, (1400,0))
        diffuse_bsdf = Shading.diffuse_BSDF(material, (1800,0))
        ## Part 2 - Setup nodes properties
        subtract_node_1.operation = 'SUBTRACT'
        subtract_node_1.name = 'subtract_node_1' # assign name to be able to update 
        subtract_node_1.inputs[0].default_value = (0,1,2) # SUN position
        subtract_node_2.operation = 'SUBTRACT'
        subtract_node_2.name = 'subtract_node_2' # assign name to be able to update 
        subtract_node_2.inputs[0].default_value = (3,4,5) # CAM position
        dot_product_node_1.operation = 'DOT_PRODUCT'
        dot_product_node_2.operation = 'DOT_PRODUCT'
        arcosine_node_1.operation = 'ARCCOSINE'
        arcosine_node_2.operation = 'ARCCOSINE'
        normalize_node_1.operation = 'NORMALIZE'
        normalize_node_2.operation = 'NORMALIZE'
        disk_function_node.mode = 'EXTERNAL'
        phase_function_node.mode = 'EXTERNAL'
        disk_function_node.filepath = bpy.path.abspath(disk_function_path)
        phase_function_node.filepath = bpy.path.abspath(phase_function_path)

        # Setup scattering function choice in the OSL nodes
        if function == "Lambertian":
            function_id = 1
        elif function == "LommelSeeliger":
            function_id = 2
        elif function == "McEwen":
            function_id = 3
        elif function == "SimplifiedHapke":
            function_id = 4
        elif function == "Hapke":
            function_id = 5
        elif function == "ROLO":
            function_id = 6
        elif function == "Akimov":
            function_id = 7
        elif function == "Minnaert":
            function_id = 8
        else:
            raise ValueError(f"Unknown scattering function: {function}")
        
        disk_function_node.inputs["function"].default_value = function_id
        phase_function_node.inputs["function"].default_value = function_id

        # Setup albedo input for disk function
        disk_function_node.inputs["albedo"].default_value = geometric_albedo

        # Setup OSL coefficients (if any)
        if function != osl_coeffs["scattering_function"]:
            raise ValueError(
                f"OSL coefficients provided for {osl_coeffs['scattering_function']}, "
                f"but shader function is {function}"
            )
        
        PHASE_FUNCTION_PARAMETERS = {
            "Lambertian":       (),
            "McEwen":           (),
            "LommelSeeliger":   ("p0", "p1", "p2", "p3"),
            "SimplifiedHapke":  ("p0",),
            "Hapke":            ("p0", "p1", "p2"),
            "ROLO":             ("p0", "p1", "p2", "p3", "p4", "p5", "p6"),
            "Akimov":           ("p0", "p1", "p2", "p3"),
            "Minnaert":         ("p0", "p1", "p2", "p3"),
        }
        
        # Assign coefficients to input of the phase function OSL node
        for p in PHASE_FUNCTION_PARAMETERS[function]:
            phase_function_node.inputs[p].default_value = osl_coeffs[p]

        ## Part 3 - Link nodes toghether
        Shading.link_nodes(material,diffuse_bsdf.outputs["BSDF"],output_node.inputs["Surface"]) # PBSDF to output
        # Compute emission angle (e) from camera position (input[0] to subtract_node_2)
        Shading.link_nodes(material,geometry_node.outputs["Position"],subtract_node_2.inputs[1]) # Geometry to subtract node
        Shading.link_nodes(material,subtract_node_2.outputs["Vector"],normalize_node_2.inputs["Vector"]) # subtract to normalize
        Shading.link_nodes(material,normalize_node_2.outputs["Vector"],dot_product_node_2.inputs[0]) # normalize to dot_product_2
        Shading.link_nodes(material,geometry_node.outputs["True Normal"],dot_product_node_2.inputs[1]) # geometry to dot_product_2
        Shading.link_nodes(material,dot_product_node_2.outputs["Value"],arcosine_node_2.inputs["Value"]) # dot_product_2 to arcosine_2
        Shading.link_nodes(material,arcosine_node_2.outputs["Value"],disk_function_node.inputs["e"]) # arcosine_node_2 to disk_function

        # Compute incident angle (i) from Sun position
        Shading.link_nodes(material,geometry_node.outputs["Position"],subtract_node_1.inputs[1]) # Geometry to subtract node
        Shading.link_nodes(material,subtract_node_1.outputs["Vector"],normalize_node_1.inputs["Vector"]) # subtract to normalize
        Shading.link_nodes(material,normalize_node_1.outputs["Vector"],dot_product_node_1.inputs[0]) # normalize to dot_product_2
        Shading.link_nodes(material,geometry_node.outputs["True Normal"],dot_product_node_1.inputs[1]) # geometry to dot_product_2
        Shading.link_nodes(material,dot_product_node_1.outputs["Value"],arcosine_node_1.inputs["Value"]) # dot_product_2 to arcosine_2
        Shading.link_nodes(material,arcosine_node_1.outputs["Value"],disk_function_node.inputs["i"]) # arcosine_node_2 to disk_function

        Shading.link_nodes(material,disk_function_node.outputs["Value"],phase_function_node.inputs["DiskFunction"]) # disk_function_node to phase_function_node
        Shading.link_nodes(material,disk_function_node.outputs["Alpha"],phase_function_node.inputs["Alpha"]) # disk_function_node to phase_function_node
        Shading.link_nodes(material,phase_function_node.outputs["Output"],diffuse_bsdf.inputs["Color"]) # phase_function_node to diffuse BSDF

    def update_osl_geometry(material, settings:dict):
        """Update geometric properties of an OSL shader.

        Args:
            material (bpy.data.materials): Material
            settings (dict): Dictionary with settings for the update
        """
        # Update values in the camera and sun positions 
        material.node_tree.nodes["subtract_node_1"].inputs[0].default_value = settings["sun_pos"]
        material.node_tree.nodes["subtract_node_2"].inputs[0].default_value = settings["cam_pos"]
       
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

    @classmethod
    def node(cls, key_or_bl_idname: str, material: bpy.types.Material, location=(0, 0)):
        """
        Create a node by alias or by raw Blender bl_idname.
        """
        """Generic method to create a node in the tree of a material

        Args:
            name (str): name of the node
            material (bpy.data.materials): material where to assign the node
            location (tuple, optional): location of the node in the nodetree. Defaults to (0, 0).

        Returns:
            node: node in the nodetree of the material
        """        

        bl_idname = cls.NODE_TYPES.get(key_or_bl_idname, key_or_bl_idname)
        n = material.node_tree.nodes.new(type=bl_idname)
        n.location = location
        return n
    
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

        node = Shading.node("ShaderNodeTexImage", material, location)
        try:
            node.image = bpy.data.images.load(texture_path)
            bpy.data.images[os.path.basename(texture_path)].colorspace_settings.name = colorspace_name
        except:
            raise NameError(f"Failed to load image from {texture_path}")
       
        return node
    
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


    def create_branch_albedo_mix(material, state: State, settings:dict = None , id_body: int = None):
        """method to create a complex shading tree with albedo texture and mix shaders

        Args:
            material (bpy.data.materials): material in which the node is generated
            state (corto.State): State object, used for paths handling
            settings (dict): Dictionary with settings for this particular shader
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
        mix_node = Shading.mix_shader_node(material, (400, 0))
        mix_node.inputs[0].default_value = 0.95
        diffuse_BSDF_node = Shading.diffuse_BSDF(material, (0, 200))
        principled_BSDF_node = Shading.principled_BSDF(material, (0, 0))
        material_node = Shading.material_output(material, (600, 0))
        uv_map_node = Shading.uv_map_node(material, (-600, 0))

        # SETUP properties of the nodes
        if settings:
            principled_BSDF_node.inputs['Roughness'].default_value = settings["pbsdf"]["roughness"]

        # LINK nodes
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
        
        mix_node = Shading.mix_shader_node(material, (400, 0))
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


def _make_helper(alias):
    def _helper(cls, material, location=(0, 0)):
        return cls.node(alias, material, location)
    _helper.__name__ = alias
    return classmethod(_helper)

for alias in Shading.NODE_TYPES.keys():
    # create a clean python-friendly name (optional; here we keep alias as-is)
    py_name = alias
    setattr(Shading, py_name, _make_helper(alias))
