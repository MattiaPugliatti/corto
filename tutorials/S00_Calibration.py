"""
Tutorial script to render images of a sphere with different shaders. 

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
scenario_name = "S00_Calibration" # Name of the scenario folder
scene_name = "scene_CYCLES.json" # name of the scene input, fast rendering setup
geometry_name = "geometry_calib.json" # name of the geometry input
body_name = "Sphere_HiRes.obj" # name of the body input

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


# All coefficients are taken as example from Golish et al. 2021 https://doi.org/10.1016/j.icarus.2020.113724. 
# All coefficients are taken for the pancromatic camera (646nm) but can be easily changed for the other cameras by looking at the tables in the paper.
# Comment and uncomment the scattering function and coefficients you want to test. 

scattering_function = "Lambertian"
geometric_albedo = 0.045
osl_coeffs = {"scattering_function": scattering_function}

# scattering_function = "McEwen"
# geometric_albedo = 0.045
# osl_coeffs = {"scattering_function": scattering_function}

# scattering_function = "LommelSeeliger"
# geometric_albedo = 0.2
# p0,p1,p2,p3 = 0.0270, -3.395e-2, 2.577e-4, -1.579e-6 # (A_LS, beta, gamma, delta)
# osl_coeffs = {"scattering_function": scattering_function, "p0": p0, "p1": p1, "p2": p2, "p3": p3}

# scattering_function = "SimplifiedHapke"
# geometric_albedo = 0.045
# p0 = 0.156 # (g) random coefficient!
# osl_coeffs = {"scattering_function": scattering_function, "p0": p0}

# scattering_function = "Hapke"
# geometric_albedo = 0.045
# p0,p1,p2 = 0.156, 2, 0.2 # (g, B0, h) random coefficients!
# osl_coeffs = {"scattering_function": scattering_function, "p0": p0, "p1": p1, "p2": p2}

# scattering_function = "ROLO"
# geometric_albedo = 0.045
# p0,p1,p2,p3,p4,p5,p6 = 0.0101, 2.729e-1, 7.936e-2, -2.191e-3, 3.691e-5, -3.854e-7, 1.671e-9 # (C0,C1, A0, A1, A2, A3, A4)
# osl_coeffs = {"scattering_function": scattering_function, "p0": p0, "p1": p1, "p2": p2, "p3": p3, "p4": p4, "p5": p5, "p6": p6}

# scattering_function = "Akimov"
# geometric_albedo = 0.043
# p0,p1,p2,p3 = 0.0136,  -3.38e-2, 3.025e-4, -1.898e-6 # (A_AK, beta, gamma, delta) 
# osl_coeffs = {"scattering_function": scattering_function, "p0": p0, "p1": p1, "p2": p2, "p3": p3}

# scattering_function = "Minnaert"
# geometric_albedo = 0.044
# p0,p1,p2,p3 = 0.0139,  3.807e-2, -3.408e-4, 1.977e-6 # (A_min, beta, gamma, delta)
# osl_coeffs = {"scattering_function": scattering_function, "p0": p0, "p1": p1, "p2": p2, "p3": p3}

material = corto.Shading.create_new_material('Apophis with OSL')
corto.Shading.create_osl_shader(material, scattering_function, geometric_albedo, disk_function_path, phase_function_path, osl_coeffs)
corto.Shading.assign_material_to_object(material, body)

# ### (4) GENERATION OF IMG-LBL PAIRS ###
body.set_scale(np.array([0.1, 0.1, 0.1])) # adjust body scale for better test renderings

osl_geometry_settings = {}

n_img = 25 # Render the first "n_img" images
for idx in range(0,n_img):
    ENV.PositionAll(State,index=idx)
    _, pos_cam, pos_sun = ENV.get_positions() # TODO: add a check on pos_bod such that the vectors are all body-referenced for the OSL shader
    osl_geometry_settings["cam_pos"] = pos_cam
    osl_geometry_settings["sun_pos"] = pos_sun
    corto.Shading.update_osl_geometry(material, osl_geometry_settings) # Update OSL shading properties
    ENV.RenderOne(cam, State, index=idx)

# Save .blend as debug
corto.Utils.save_blend(State)