"""
Tutorial script to render images of the S06b_Moon scenario. 

In this scenario, a high-resolution tile of the Moon surface with improved texture is rendered, which is useful for close navigation regimes such as low lunar orbits or landing trajectories

To run this tutorial, you first need to put data in the input folder. 
You can download the tutorial data from: 

https://drive.google.com/drive/folders/1K3e5MyQin6T9d_EXLG_gFywJt3I18r6H?usp=sharing

"""
import sys
import os
sys.path.append(os.getcwd())

import cortopy as corto
import numpy as np 

## Clean all existing/Default objects in the scene 
corto.Utils.clean_scene()

### (1) DEFINE INPUT ### 
# scenario_name = "S06b_Moon/moon_0_10E_0_10N" # Scenario A
# scenario_name = "S06b_Moon/moon_0_10E_10_20N" # Scenario B
# scenario_name = "S06b_Moon/moon_10_20E_0_10N" # Scenario C
scenario_name = "S06b_Moon/moon_10_20E_10_20N" # Scenario D
# scenario_name = "S06b_Moon/moon_20_30E_0_10N" # Scenario E

scene_name = "scene.json" # name of the scene input
geometry_name = "geometry.json" # name of the geometry input
body_name = "lunar_terrain_model.obj" # name of the body input

# Load inputs and settings into the State object
State = corto.State(scene = scene_name, geometry = geometry_name, body = body_name, scenario = scenario_name)
# Add extra inputs 
State.add_path('texture_path', os.path.join(State.path["input_path"],'Utils','Texture.png'))
State.add_path('CraterMask_path', os.path.join(State.path["input_path"],'Utils','crater_mask.png'))
State.add_path('DEM_path',os.path.join(State.path["input_path"],'Utils','DEM.tif'))
State.add_path('info_path',os.path.join(State.path["input_path"],'Utils','info.txt'))
State.add_path('LatLonMask_path',os.path.join(State.path["input_path"],'Utils','lat_lon_mask.exr'))
State.add_path('filteredcraters_path',os.path.join(State.path["input_path"],'Utils','FilteredCraters.csv'))
State.add_path('material_path',os.path.join(State.path["input_path"],'body','material'))

#TODO: complete labels from compositing with YOLO labels and crater labels
# depth_dir = os.path.join(State.path["output_path"],'depth_txt')
# if not os.path.exists(depth_dir):
#     os.makedirs(depth_dir)
# altimeter_dir = os.path.join(State.path["output_path"],'altimeter')
# if not os.path.exists(altimeter_dir):
#     os.makedirs(altimeter_dir)
# YOLO1_dir = os.path.join(State.path["output_path"],'YOLO1_labels')
# if not os.path.exists(YOLO1_dir):
#     os.makedirs(YOLO1_dir)
# YOLO2_dir = os.path.join(State.path["output_path"],'YOLO2_labels')
# if not os.path.exists(YOLO2_dir):
#     os.makedirs(YOLO2_dir)

### (2) SETUP THE SCENE ###
# Setup bodies
cam = corto.Camera('WFOV_Camera', State.properties_cam)
sun = corto.Sun('Sun',State.properties_sun)
name, extension = os.path.splitext(body_name)
body = corto.Body("Lunar_Tile", State.properties_body)

# Setup rendering engine
rendering_engine = corto.Rendering(State.properties_rendering)
# Setup environment
ENV = corto.Environment(cam, body, sun, rendering_engine)

### (3) MATERIAL PROPERTIES ###
material = corto.Shading.create_new_material('Lunar tile material')
corto.Shading.create_lunar_shader(material,State)#TODO: missing OSL component!
corto.Shading.assign_material_to_object(material, body)

### (4) COMPOSITING PROPERTIES ###
# Build image-label pairs pipeline
tree = corto.Compositing.create_compositing()
render_node = corto.Compositing.rendering_node(tree, (-400, -200))  # Render Layers node
corto.Compositing.create_lunar_tile_labels(tree,render_node, State)

### (5) GENERATION OF IMG-LBL PAIRS ###
n_img = 5 # Render the first "n_img" images
for idx in range(0,n_img):
    ENV.PositionAll(State,index=idx)
    ENV.RenderOne(cam, State, index=idx, depth_flag = True)

# Save .blend as debug
corto.Utils.save_blend(State)