import sys
import os
sys.path.append(os.getcwd())
import cortopy as corto
import numpy as np 
#TODO: fix image generation to get uint8 grayscale instead of uint16-RGB

## Clean all existing/Default objects in the scene 
corto.Utils.clean_scene()

### (1) DEFINE INPUT ### 
scenario_name = "SXX_Double" # Name of the scenario folder
scene_name = "scene.json" # name of the scene input
geometry_name = "R5_2025_05_25_15_16_44.json" # name of the geometry input

# Select body #TODO: automatize this, for now assume we are working on one body only
body_name = "41458_X5Y4.obj" # name of the body input
body_name_2 = "X3.obj" 

# Load inputs and settings into the State object
State = corto.State(scene = scene_name, geometry = geometry_name, body = body_name, scenario = scenario_name)

### (2) SETUP THE SCENE ###
# Setup bodies
cam = corto.Camera('NAC_Camera', State.properties_cam)
sun = corto.Sun('Sun',State.properties_sun)
name, extension = os.path.splitext(body_name)
body = corto.Body(name,State.properties_body)
# Setup rendering engine
rendering_engine = corto.Rendering(State.properties_rendering)
# Setup environment
ENV = corto.Environment(cam, body, sun, rendering_engine)

### (3) MATERIAL PROPERTIES ###
material = corto.Shading.create_new_material('BodySurfaceRand')
corto.Shading.create_randomized_texturePBSDF(material)
corto.Shading.assign_material_to_object(material, body)

# corto.Shading.print_material_node_tree(material)

settings_body_dyn = {
    # Wave Texture
    "wave_scale": 0,
    "wave_distortion": 0,
    "wave_detail": 0,
    "wave_detail_scale": 0,
    "wave_detail_roughness": 0,
    # Magic Texture
    "magic_scale": 0,
    "magic_distortion": 0,
    # Noise Texture
    "noise_scale": 0,
    "noise_detail": 0,
    "noise_roughness": 0,
    "noise_lacunarity": 0,
    "noise_distortion": 0,
    # Mix 
    "mix_1_fac": 0, 
    "mix_2_fac": 0
}

corto.Shading.update_randomized_texturePBSDF(material, settings_body_dyn)

corto.Utils.save_blend(State)

### (4) COMPOSITING PROPERTIES ###

#TODO: Define output labels

# Build image-label pairs pipeline
tree = corto.Compositing.create_compositing()
render_node = corto.Compositing.rendering_node(tree, (0,0)) # Create Render node
corto.Compositing.create_img_denoise_branch(tree,render_node) # Create img_denoise branch
# corto.Compositing.create_depth_branch(tree,render_node) # Create depth branch
# corto.Compositing.create_slopes_branch(tree,render_node,State) # Create slopes branch
corto.Compositing.create_maskID_branch(tree,render_node,State) # Create ID mask branch

### (5) GENERATION OF IMG-LBL PAIRS ###

# n_img = 5000 # Render the first "n_img" images
# for idx in range(0,n_img):
#     ENV.PositionAll(State,index=idx)
#     ENV.RenderOne(cam, State, index=idx, depth_flag = False)

# Save .blend as debug
# corto.Utils.save_blend(State)
