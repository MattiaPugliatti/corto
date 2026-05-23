'''
This tutorial is an example of a closed-loop setup in which your script and CORTO are cooperating. 
CIL stands for CORTO in the loop.
NOTE: (CLOSE-LOOP) this setup assumes you have an iterative process and you are generating the poses of the partecipating bodies on the go.
NOTE: (COOPERATIVE) this setup assumes you don't have any conflicts between your libraries and CORTO libraries.
'''

import sys
import os
sys.path.append(os.getcwd())
import cortopy as corto
import numpy as np

def corto_scene_setup():
    '''
    Function to setup the scene in CORTO for a closed-loop rendering: 
    '''
    ## Clean all existing/Default objects in the scene 
    corto.Utils.clean_scene()

    ### (1) DEFINE INPUT ### 
    scenario_name = "S01_Eros" # Name of the scenario folder
    scene_name = "scene_EEVEE.json" # name of the scene input, fast rendering setup
    body_name = "433_Eros_512ICQ.obj" # name of the body input

    # Load inputs and settings into the State object
    State = corto.State(scene = scene_name, geometry = None, body = body_name, scenario = scenario_name)
    # Add extra inputs 
    State.add_path('albedo_path',os.path.join(State.path["input_path"],'body','albedo','Eros grayscale.jpg'))
    State.add_path('uv_data_path',os.path.join(State.path["input_path"],'body','uv data','uv_data.json'))

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
    material = corto.Shading.create_new_material('corto shading test')
    corto.Shading.create_branch_albedo_mix(material, State)
    corto.Shading.load_uv_data(body,State)
    corto.Shading.assign_material_to_object(material, body)

    ### (4) GENERATION OF IMG-LBL PAIRS ###
    body.set_scale(np.array([0.1, 0.1, 0.1])) # adjust body scale for better test renderings

    return ENV, State, cam

## ---------- #
# MAIN SCRIPT 
## ---------- #

# 00. Download the necessary data for the scenario you want to run and put it into the "input" folder

# 01. SETUP CORTO SCENE 

ENV, State, cam = corto_scene_setup()

# 02. DO YOUR THING and GENERATE A NEW Sun-Body-Camera information

idx = 0 

# Partecipating bodies poses at idx = 0
camera_pos = np.array([-3.880436735865625,9.436275094557633,0.2122852153592106])
camera_orientation = np.array([-0.13848248126035184, -0.13563116230823927, 0.6864425350546722, 0.7008733382449409])
body_pos = np.array([0.0, 0.0, 0.0])
body_orientation = np.array([0.016352521502461803, 0.0, 0.0, 0.999866288580884])
sun_pos = np.array([0.0, 30000.0, 0.0])

poses_input = [camera_pos, camera_orientation, body_pos, body_orientation,sun_pos]

# 04. GENERATE THE IMAGES SEQUENTIALLY
ENV.PositionAll(State,index = None, poses = poses_input)
ENV.RenderOne(cam, State, index=idx)


corto.Utils.save_blend(State)

