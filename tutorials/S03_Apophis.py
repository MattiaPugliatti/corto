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

#TODO: move albedo from Blender to OSL shader input of the disk function, so I can use it in Hapke
#TODO: Choose a strategy for the extra parameters in Hapke and in general for any coefficients we may want to have as input
## Clean all existing/Default objects in the scene 
corto.Utils.clean_scene()

### (1) DEFINE INPUT ### 
scenario_name = "S03_Apophis" # Name of the scenario folder
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

geometric_albedo = 0.2
#scattering_function = "Lambertian"
#scattering_function = "McEwen"

scattering_function = "LommelSeeliger"
p0,p1,p2,p3 = 0.0270, -3.395e-2, 2.577e-4, -1.579e-6 # (A_LS, beta, gamma, delta) coefficients for Bennu, Golish et al. 2021 https://doi.org/10.1016/j.icarus.2020.113724
osl_coeffs = {"scattering_function": scattering_function, "p0": p0, "p1": p1, "p2": p2, "p3": p3}

scattering_function = "SimplifiedHapke"
p0 = 0.156 # (g) random coefficient
osl_coeffs = {"scattering_function": scattering_function, "p0": p0}

scattering_function = "Hapke"
p0,p1,p2 = 0.156, 2, 0.2 # (g, B0, h) random coefficients
osl_coeffs = {"scattering_function": scattering_function, "p0": p0, "p1": p1, "p2": p2}


material = corto.Shading.create_new_material('Apophis with OSL')
corto.Shading.create_osl_shader(material, scattering_function, geometric_albedo, disk_function_path, phase_function_path, osl_coeffs)
corto.Shading.assign_material_to_object(material, body)

# ### (4) GENERATION OF IMG-LBL PAIRS ###
body.set_scale(np.array([3, 3, 3])) # adjust body scale for better test renderings

osl_geometry_settings = {}

n_img = 1 # Render the first "n_img" images
for idx in range(0,n_img):
    ENV.PositionAll(State,index=idx)
    _, pos_cam, pos_sun = ENV.get_positions() # TODO: add a check on pos_bod such that the vectors are all body-referenced for the OSL shader
    osl_geometry_settings["cam_pos"] = pos_cam
    osl_geometry_settings["sun_pos"] = pos_sun
    corto.Shading.update_osl_geometry(material, osl_geometry_settings) # Update OSL shading properties
    ENV.RenderOne(cam, State, index=idx)

# Save .blend as debug
corto.Utils.save_blend(State)