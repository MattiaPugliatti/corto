"""
Tutorial script to render images of the S03_Apophis scenario. 

In this tutorial an example of an OSL shader is used to illustrated rendering capabilities with CYCLES and different BRDF mathematical formulations.

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
scenario_name = "S03_Apophis" # Name of the scenario folder
# scene_name = "scene_EEVEE.json" # name of the scene input, fast rendering setup
scene_name = "scene_CYCLES.json" # name of the scene input, fast rendering setup
geometry_name = "geometry.json" # name of the geometry input
body_name = "apophis.obj" # name of the body input

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

disk_function_path = os.path.join(os.getcwd(),"cortopy/corto_diskFunctions.osl")
phase_function_path = os.path.join(os.getcwd(),"cortopy/corto_phaseFunctions.osl")

albedo = 0.2
scattering_function = "LommelSeeliger"

material = corto.Shading.create_new_material('Apophis with OSL')
corto.Shading.create_osl_shader(material, scattering_function, albedo, disk_function_path, phase_function_path)
corto.Shading.assign_material_to_object(material, body)

# ### (4) GENERATION OF IMG-LBL PAIRS ###
body.set_scale(np.array([3, 3, 3])) # adjust body scale for better test renderings

settings_osl = {}

n_img = 5 # Render the first "n_img" images
for idx in range(0,n_img):
    ENV.PositionAll(State,index=idx)
    _, pos_cam, pos_sun = ENV.get_positions() # TODO: add a check on pos_bod such that the vectors are all body-referenced for the OSL shader
    settings_osl['cam_pos'] = pos_cam
    settings_osl["sun_pos"] = pos_sun
    corto.Shading.update_osl_shader(material, settings_osl) # Update OSL shading properties
    ENV.RenderOne(cam, State, index=idx)

# Save .blend as debug
corto.Utils.save_blend(State)