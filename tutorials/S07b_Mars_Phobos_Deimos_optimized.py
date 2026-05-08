"""Tutorial script: S07_Mars_Phobos_Deimos — Optimized Render

To run this tutorial, you first need to put data in the input folder. 
You can download the tutorial data from:

https://drive.google.com/drive/folders/1K3e5MyQin6T9d_EXLG_gFywJt3I18r6H?usp=sharing
"""

# TODO: move the shading tree as a method in the Shading class instead
# TODO: atmosphere loading standardized 

import sys
import os
sys.path.append(os.getcwd())
import cortopy as corto
import numpy as np
import json
import math

## Clean all existing/Default objects in the scene 
corto.Utils.clean_scene()

### (1) DEFINE INPUT ### 
scenario_name = "S07_Mars_Phobos_Deimos" # Name of the scenario folder
scene_name = "scene_optimized.json" # name of the scene input
geometry_name = "geometry_optimized.json" # name of the geometry input
setup_fidelity = 'lowres' # "lowres" or "hires"

if setup_fidelity == 'lowres': # LOW-RES setup
    body_name = ["g_phobos_287m_spc_0000n00000_v002.obj",
                "Mars_65k.obj",
                "g_deimos_162m_spc_0000n00000_v001.obj"] # name of the body input
    # Load inputs and settings into the State object
    State = corto.State(scene = scene_name, geometry = geometry_name, body = body_name, scenario = scenario_name)
    # Add extra inputs 
    State.add_path('albedo_path_1',os.path.join(State.path["input_path"],'body','albedo','Phobos grayscale.jpg'))
    State.add_path('uv_data_path_1',os.path.join(State.path["input_path"],'body','uv data','g_phobos_287m_spc_0000n00000_v002.json'))
    State.add_path('albedo_path_2',os.path.join(State.path["input_path"],'body','albedo','Mars_MOC_f32.tif'))
    State.add_path('uv_data_path_2',os.path.join(State.path["input_path"],'body','uv data','Mars_65k.json'))
    State.add_path('displacement_path_2', os.path.join(State.path["input_path"], 'body', 'displacement', 'Mars_MOLA_DEM_f32.tif'))
    State.add_path('albedo_path_3',os.path.join(State.path["input_path"],'body','albedo','Deimos Grayscale.jpg'))
    State.add_path('uv_data_path_3',os.path.join(State.path["input_path"],'body','uv data','g_deimos_162m_spc_0000n00000_v001.json'))
elif setup_fidelity == 'hires': # HIGH-RES setup (run at your own risk)
    body_name = ["g_phobos_018m_spc_0000n00000_v002.obj",
                "Mars_65k.obj",
                "g_deimos_020m_spc_0000n00000_v001.obj"] # name of the body input
    # Load inputs and settings into the State object
    State = corto.State(scene = scene_name, geometry = geometry_name, body = body_name, scenario = scenario_name)
    # Add extra inputs 
    State.add_path('albedo_path_1',os.path.join(State.path["input_path"],'body','albedo','Phobos grayscale.jpg'))
    State.add_path('uv_data_path_1',os.path.join(State.path["input_path"],'body','uv data','g_phobos_018m_spc_0000n00000_v002.json'))
    State.add_path('albedo_path_2',os.path.join(State.path["input_path"],'body','albedo','Mars_MOC_f32.tif'))
    State.add_path('uv_data_path_2',os.path.join(State.path["input_path"],'body','uv data','Mars_65k.json'))
    State.add_path('displacement_path_2', os.path.join(State.path["input_path"], 'body', 'displacement', 'Mars_MOLA_DEM_f32.tif'))
    State.add_path('albedo_path_3',os.path.join(State.path["input_path"],'body','albedo','Deimos Grayscale.jpg'))
    State.add_path('uv_data_path_3',os.path.join(State.path["input_path"],'body','uv data','g_deimos_020m_spc_0000n00000_v001.json'))

### (2) SETUP THE SCENE ###
cam = corto.Camera('WFOV_Camera', State.properties_cam)
sun = corto.Sun('Sun', State.properties_sun)
name_1, _ = os.path.splitext(body_name[0])
name_2, _ = os.path.splitext(body_name[1])
name_3, _ = os.path.splitext(body_name[2])
body_1 = corto.Body(name_1, State.properties_body_1)
body_2 = corto.Body(name_2, State.properties_body_2)
body_3 = corto.Body(name_3, State.properties_body_3)
# Setup rendering engine
rendering_engine = corto.Rendering(State.properties_rendering)
# Setup environment
ENV = corto.Environment(cam, [body_1, body_2, body_3], sun, rendering_engine)

### (3) MATERIAL PROPERTIES ###
settings_phobos_shader = {
    "base_gray": 0.5854006741991221,
    "tex_mix": 0.8253680350717726,
    "oren_rough": 0.9541235132345137,
    "princ_rough": 0.49655068351162784,
    "shader_mix": 0.5531372578612878,
    "ior": 1.330575673667888
    }

settings_mars_shader = {
    "displacement": {
        'scale': 0.001, 
        'mid_level': 6690.0, 
        'colorspace_name': 'Non-Color'
        },
    "albedo": {
        'weight_diffuse': 0.95
        },
    "base_gray": 0.5468756598827581,
    "tex_mix": 0.05593282890485482,
    "oren_rough": 0.9998320451129385,
    "princ_rough": 0.7399105387301975,
    "shader_mix": 0.08013107968798325,
    "ior": 2.382993288552901,
    "albedo_mul": 4.282003588146343,
    "contrast": 0.1567607232962447
    }

settings_thr_val ={
    "threshold_value": 0.002319883899697151
    }

material_1 = corto.Shading.create_new_material('Phobos_Optimized')
material_2 = corto.Shading.create_new_material('Mars_Standard')
material_3 = corto.Shading.create_new_material('Deimos_Standard')

### --- Phobos --- ###
corto.Shading.create_phobos_opt_shader(material_1, State, settings_phobos_shader, 1)
# corto.Shading.load_uv_data(body_1, State, 1) # TODO: RUN THIS AFTER DOWNLOADING UV DATA
corto.Shading.assign_material_to_object(material_1, body_1)

### --- Mars --- ###
corto.Shading.create_mars_opt_shader(material_2, State, settings_mars_shader, 2)
# corto.Shading.load_uv_data(body_2, State, 2) # TODO: RUN THIS AFTER DOWNLOADING UV DATA
corto.Shading.assign_material_to_object(material_2, body_2)

### --- Deimos --- ###
corto.Shading.create_branch_albedo_mix(material_3, State, settings = None, id_body = 3)
# corto.Shading.load_uv_data(body_3, State, 3) # TODO: RUN THIS AFTER DOWNLOADING UV DATA
corto.Shading.assign_material_to_object(material_3, body_3)

corto.Utils.save_blend(State)

### (4) COMPOSITING PROPERTIES ###

tree = corto.Compositing.create_compositing()
render_node = corto.Compositing.rendering_node(tree, (0, 0)) # Create Render node
corto.Compositing.create_img_denoise_branch(tree, render_node) # Create img_denoise branch
corto.Compositing.create_maskID_branch(tree, render_node, State) # Create ID mask branch

### (5) GENERATION OF IMG-LBL PAIRS ###
body_1.set_scale(np.array([1, 1, 1]))
body_2.set_scale(np.array([1, 1, 1]))
body_3.set_scale(np.array([1, 1, 1]))

def set_sun_energy_idx(sun):
    """Calculate Sun lamp energy from Sun position (inverse-square law)."""
    AU_KM = 149597870.7
    W_1AU = 427.815 # Solar irradiance at 1 AU in Blender units
    SUN_BLENDER_SCALER = 1.0
    # geom = json.load(open(os.path.join('input', scenario_name, 'geometry', geometry_name)))
    # sun_pos = np.array(geom['sun']['position'][idx])
    sun_pos = sun.get_position()    
    solar_dist_km = float(np.linalg.norm(sun_pos))
    dist_au = solar_dist_km / AU_KM if solar_dist_km > 0 else 1.0
    irradiance = W_1AU / (dist_au ** 2)
    energy = SUN_BLENDER_SCALER * irradiance
    sun.set_energy(energy)

# OSIRIS NAC camera config (from mission_config.py)
OSIRIS_FOV_DEG = 2.0 * math.degrees(math.atan(27.648 / (2.0 * 712.4)))  # 2.2226 deg # TODO, bring it into config file of the scene
HRSC_FOV = cam.CAM_Blender.data.angle  # save original HRSC FOV 

n_img = 8 # 0-5: HRSC, 6-7: OSIRIS
for idx in range(0, n_img):
    # Camera handling (SWAP BETWEEN HRSC and OSIRIS)
    if idx == 6:
        # Switch to OSIRIS NAC camera
        cam.CAM_Blender.data.angle = math.radians(OSIRIS_FOV_DEG)
    # Set Sun energy per frame
    set_sun_energy_idx(sun)
    # Position and Render
    ENV.PositionAll(State, index=idx)
    ENV.RenderOne(cam, State, index=idx, depth_flag=True)

# Save .blend as debug
corto.Utils.save_blend(State)