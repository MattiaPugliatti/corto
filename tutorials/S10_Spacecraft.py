"""
Tutorial script to render images of the S10_Spacecraft scenario. 

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
scenario_name = "S10_Spacecraft" # Name of the scenario folder
# scene_name = "scene_CYCLES.json" # name of the scene input, slow rendering setup, high quality
scene_name = "scene_EEVEE.json" # name of the scene input, fast rendering setup, lower quality
geometry_name = "geometry.json" # name of the geometry input
body_name = "Dawn.gltf" # name of the body input
# body_name = "mover.glb" # Lunar Gateway, #TODO, convert to gltf and save with proper name
# body_name = "SSREF_IGOAL.glb" # ISS, #TODO, convert to gltf and save with proper name

# Load inputs and settings into the State object
State = corto.State(scene = scene_name, geometry = geometry_name, body = body_name, scenario = scenario_name)

### (2) SETUP THE SCENE ###
# Setup bodies
cam = corto.Camera('WFOV_Camera', State.properties_cam)
sun = corto.Sun('Sun',State.properties_sun)
name, extension = os.path.splitext(body_name)
body = corto.Body(name,State.properties_body)

# Setup rendering engine
rendering_engine = corto.Rendering(State.properties_rendering)
# Setup environment
ENV = corto.Environment(cam, body, sun, rendering_engine)
### (3) MATERIAL PROPERTIES ###
# Not needed for the spacecraft, already loaded wiht the gltf file

### (4) GENERATION OF IMG-LBL PAIRS ###
body.set_scale(np.array([0.1, 0.1, 0.1])) # adjust body scale for better test renderings

n_img = 5 # Render the first "n_img" images
for idx in range(0,n_img):
    ENV.PositionAll(State,index=idx)
    ENV.RenderOne(cam, State, index=idx)

# Save .blend as debug
corto.Utils.save_blend(State)
