"""
Tutorial script to render images of the S09_Frankenstein scenario. 
This tutorial exemplify a way in which a complex simulation scenario can be setup and run with CORTO. 
This is my personal setup, it might not be the most efficient one!

NOTE: this is the script used in [1] "Navigating the Unknown: Data-Driven Image Processing and Simplified Renderings for Small Body Flybys" by 
M. Pugliatti and J. W. McMahon, presented at the 2025 AAS/AIAA Conference, Boston Massachusetts. 

Dataset link: https://zenodo.org/records/17039466
Paper link: https://www.researchgate.net/publication/395195173_Navigating_the_Unknown_Data-Driven_Image_Processing_and_simplified_renderings_for_small_body_flybys
Presentation link: https://www.researchgate.net/publication/395199302_PresentationUploadPPTorPDF_877_0812101413pptx

NOTE: To render the dataset in [1], CYCLES has been used as rendering engine

To run this tutorial, you first need to put data in the input folder. 
You can download the tutorial data from:

https://drive.google.com/drive/folders/1K3e5MyQin6T9d_EXLG_gFywJt3I18r6H?usp=sharing

"""

import sys
import os
sys.path.append(os.getcwd())
import cortopy as corto
import json

## Clean all existing/Default objects in the scene 
corto.Utils.clean_scene()

### (1) INPUT DEFINITION ### 
scenario_name = "S09_Frankenstein_Asteroids" # Name of the scenario folder
scene_name = "scene_EEVEE.json" # name of the scene input, use this for simplified renderings (faster)
# scene_name = "scene.json" # name of the scene input, use this if you want more labels, realism (slower)
dataset_setup = "D0b" # Names as in [1]: "D0",'D0b","D1",...., "D15", "D16", "D17"

# Uncomment this portion if you need to overun this in a long-run
# Also, remember to uncomment line 119

'''
# --- CLI override for idx range (works with Blender's "--" as well) ---
import sys, argparse
def _override_range_via_cli(default_start, default_end):
    # Blender passes script args after a literal "--".
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = argv[1:]
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--start", type=int, dest="start")
    parser.add_argument("--end",   type=int, dest="end")
    # parse_known_args so we ignore any extra scenario flags you may add later
    ns, _ = parser.parse_known_args(argv)
    s = default_start if ns.start is None else ns.start
    e = default_end   if ns.end   is None else ns.end
    if e < s:
        raise ValueError(f"--end ({e}) must be >= --start ({s})")
    print(f"[S09] render range: idx_start={s}, idx_end={e}")
    return s, e
'''

if dataset_setup == "D0":
    geometry_name = "R5_2025_06_13_10_21_51.json" # Training & Validation (D0)
    body_dyn_name = "R5_16k_body_settings.json" # Training & Validation (D0)
    idx_start, idx_end = 0, 16000 # Render the images between idx_start and idx_end (D0)
if dataset_setup == "D0b":
    geometry_name = "R5_2025_09_30_11_05_37_160k.json" # Training & Validation (D0b)
    body_dyn_name = "R5_160k_body_settings.json" # Training & Validation (D0b)
    idx_start, idx_end = 0, 160000 # Render the images between idx_start and idx_end (D0b)
elif dataset_setup in ("D1", "D2", "D3", "D4", "D5"):
    body_dyn_name = "R12345_1k_body_settings.json" # 
    idx_start, idx_end = 0, 1000 # Render the images between idx_start and idx_end
    if dataset_setup == "D1":
        geometry_name = "R5_2025_06_13_10_16_22.json"
    elif dataset_setup == "D2":
        geometry_name = "R1_2025_06_11_11_09_08.json"
    elif dataset_setup == "D3":
        geometry_name = "R2_2025_06_11_11_09_17.json"
    elif dataset_setup == "D4":
        geometry_name = "R3_2025_06_11_11_09_24.json"
    elif dataset_setup == "D5":
        geometry_name = "R4_2025_06_11_11_09_31.json"
elif dataset_setup == "D6":
    body_dyn_name = "R6_AllReal_5k_body_settings.json" # Te
    geometry_name = "R6_2025_06_18_15_06_22.json" # Te
    idx_start, idx_end = 0, 5000 # Render the images between idx_start and idx_end
elif dataset_setup in ("D7", "D8", "D9", "D10", "D11"):
    geometry_name = "R6_2025_06_18_15_05_36.json" # Te
    idx_start, idx_end = 0, 1000 # Render the images between idx_start and idx_end
    if dataset_setup == "D7":
        body_dyn_name = "" # TODO: add this JSON from McBookAIR
    elif dataset_setup == "D8":
        body_dyn_name = "" # TODO: add this JSON from McBookAIR
    elif dataset_setup == "D9":
        body_dyn_name = "R6_Steins_1k_body_settings.json" # Te
    elif dataset_setup == "D10":
        body_dyn_name = "R6_Eros_1k_body_settings.json" # Te
    elif dataset_setup == "D11":
        body_dyn_name = "R6_Itokawa_1k_body_settings.json" # Te
elif dataset_setup == "D15":
    body_dyn_name = "67P_range_test.json" # Te
    geometry_name = "R7_2025_07_23_22_05_17.json" # Te
    idx_start, idx_end = 0, 100 # Render the images between idx_start and idx_end
elif dataset_setup == "D16":
    body_dyn_name = "flyby_67P.json" # Te
    geometry_name = "flyby_2025_10_19_13_32_41.json" # Te
    idx_start, idx_end = 0, 4000 # Render the images between idx_start and idx_end
elif dataset_setup == "D17":
    body_dyn_name = "flyby_apophis.json" # Te
    geometry_name = "flyby_2025_10_19_13_32_41.json" # Te
    idx_start, idx_end = 0, 4000 # Render the images between idx_start and idx_end
elif dataset_setup == "D18":
    body_dyn_name = "flyby_67P.json" # Te
    geometry_name = "range_test_R1_2025_10_20_17_15_40.json" # Te
    idx_start, idx_end = 0, 4000 # Render the images between idx_start and idx_end
else:
    raise ValueError(f"Unknown dataset_setup: {dataset_setup}")

# apply overrides on idx
# idx_start, idx_end = _override_range_via_cli(idx_start, idx_end)

### (2) PREPARE STRUCTURES ###

# Open and read the JSON file with dynamic body's parameters
with open(os.path.join("input/S09_Frankenstein_Asteroids/body/material", body_dyn_name ), "r") as f:
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
        if scene_name == "scene.json": # Activate these labels if you are using CYCLES instead of EEVEE
            corto.Compositing.create_img_denoise_branch(tree,render_node) # Create img_denoise branch
            corto.Compositing.create_maskID_branch(tree,render_node,State_ii_body) # Create ID mask branch
        elif scene_name == "scene_EEVEE.json":
            corto.Compositing.create_img_branch(tree,render_node, State_ii_body) # Create img branch
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

# Override for test rendering
idx_start, idx_end = 0, 5 #NOTE: REMOVE THIS TO RENDER THE FULL DATASET, THIS IS JUST FOR TESTING PURPOSES

for idx in range(idx_start,idx_end):
    id_body = body_name_list.index(settings_body_dyn[idx]["body_name"]) # Get the body's index from the body's name list
    # Extract dedicated env, body, and state objects
    env_idx = env_list[id_body]
    body_idx = body_list[id_body]
    state_idx = state_list[id_body]
    if body_idx.name != settings_body_dyn[idx]["body_name"][0:-4]:
        print(body_idx.name)
        print(settings_body_dyn[idx]["body_name"][0:-4])
        break
    # Setup rendering scene
    env_idx.PositionAll(state_idx,index=idx)
    body_idx.visible(True) # Make body_idx visible for the rendering
    corto.Shading.update_randomized_texturePBSDF(material, settings_body_dyn[idx]) # Update shading properties
    env_idx.RenderOne(cam, state_idx, index=idx, depth_flag = False) # Render the image-label pairs
    body_idx.visible(False) # Remove body visibility for next rendering

# Save .blend as debug
corto.Utils.save_blend(state_idx)
