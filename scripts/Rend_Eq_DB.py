import sys
import os
sys.path.append(os.getcwd())
import cortopy as corto
import numpy as np 
import json

## Clean all existing/Default objects in the scene 
corto.Utils.clean_scene()

### (1) DEFINE INPUT ### 
scenario_name = "SXX_Double" # Name of the scenario folder
scene_name = "scene.json" # name of the scene input
geometry_name = "R5_2025_05_25_15_16_44.json" # name of the geometry input
body_dyn_name = "R5_50k_body_settings.json" # name of the json for the dynamic body's settings

# Open and read the JSON file with dynamic body's parameters
with open(os.path.join("input/SXX_Double/body/material", body_dyn_name ), "r") as f:
    settings_body_dyn = json.load(f)

# Identify the unique set of body names
unique_body_names = set()
for ii in range(len(settings_body_dyn)):
    unique_body_names.add(settings_body_dyn[ii]["body_name"])
unique_body_names = list(unique_body_names) # Convert to list if needed

# Generate list of body, env, state objects for each shape model
body_list = []
env_list = []
state_list = []
body_name_list = []
for ii_body in range(len(unique_body_names)):
    body_name_ii_body = unique_body_names[ii_body] # Get the name of the unique body to work on
    State_ii_body = corto.State(scene = scene_name, geometry = geometry_name, body = body_name_ii_body, scenario = scenario_name)
    name, _ = os.path.splitext(body_name_ii_body)
    body_ii_body = corto.Body(name,State_ii_body.properties_body)
    body_ii_body.visible(False) # Set body's visibility to False
    if ii_body == 0: # Generate the single set of variables independet of the body (for ii_body == 0 only)
        ### (2) CAM-SUN-RENDERING PROPERTIES ###
        cam = corto.Camera('5deg_CAM', State_ii_body.properties_cam)
        sun = corto.Sun('Sun',State_ii_body.properties_sun)
        rendering_engine = corto.Rendering(State_ii_body.properties_rendering)
        ### (3) MATERIAL PROPERTIES ###
        material = corto.Shading.create_new_material('BodySurfaceRand')
        corto.Shading.create_randomized_texturePBSDF(material)
        ### (4) COMPOSITING PROPERTIES ###
        tree = corto.Compositing.create_compositing()
        render_node = corto.Compositing.rendering_node(tree) # Create Render node
        corto.Compositing.create_img_denoise_branch(tree,render_node) # Create img_denoise branch
        corto.Compositing.create_maskID_branch(tree,render_node,State_ii_body) # Create ID mask branch
    # Assign the same material to each body (properties are updated in the rendering loop)
    corto.Shading.assign_material_to_object(material, body_ii_body)
    # Setup environment object
    ENV_ii_body = corto.Environment(cam, body_ii_body, sun, rendering_engine)
    # Append state, body, and env objects in a list 
    body_list.append(body_ii_body)
    env_list.append(ENV_ii_body)
    state_list.append(State_ii_body)
    body_name_list.append(body_name_ii_body)

### (5) GENERATE IMG-LBL PAIRS ###

idx_start = 0
idx_end = 2 # Render the images between idx_start and idx_end
for idx in range(idx_start,idx_end):
    id_body = body_name_list.index(settings_body_dyn[idx]["body_name"]) # Get the body's index from the body's name list
    # Extract dedicated env, body, and state objects
    env_idx = env_list[id_body]
    body_idx = body_list[id_body]
    state_idx = state_list[id_body]
    if body_idx.name != settings_body_dyn[idx]["body_name"][0:-5]:
        print(body_idx.name)
        print(settings_body_dyn[idx]["body_name"][0:-5])
        break
    # Setup rendering scene
    env_idx.PositionAll(state_idx,index=idx)
    body_idx.visible(True) # Make body_idx visible for the rendering
    corto.Shading.update_randomized_texturePBSDF(material, settings_body_dyn[idx]) # Update shading properties
    env_idx.RenderOne(cam, state_idx, index=idx, depth_flag = False) # Render the image-label pairs
    body_idx.visible(False) # Remove body visibility for next rendering

# Save .blend as debug
corto.Utils.save_blend(state_idx)
