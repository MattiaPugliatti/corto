'''
This tutorial is an example of an open-loop setup in which your script and CORTO are cooperating. 
CIL stands for CORTO in the loop.
NOTE: (OPEN-LOOP)this setup assumes you have apriori information about all the poses of the partecipating bodies you want to generate the images of (e.g. this is an open-loop from the perspetcive of image generation).
NOTE: (COOPERATIVE) this setup assumes you don't have any conflicts between your libraries and CORTO libraries.
'''

import sys
import os
sys.path.append(os.getcwd())
import cortopy as corto
import numpy as np

def corto_scene_setup(
        geometry_name:str
        ):
    '''
    Function to setup the scene in CORTO for an open-loop rendering: 
    '''
    ## Clean all existing/Default objects in the scene 
    corto.Utils.clean_scene()

    ### (1) DEFINE INPUT ### 
    scenario_name = "S01_Eros" # Name of the scenario folder
    scene_name = "scene_EEVEE.json" # name of the scene input, fast rendering setup
    body_name = "433_Eros_512ICQ.obj" # name of the body input

    # Load inputs and settings into the State object
    State = corto.State(scene = scene_name, geometry = geometry_name, body = body_name, scenario = scenario_name)
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

# 01. DO YOUR THING

# 02. BASED ON THAT, GENERATE A NEW GEOMETRY FILE

# NOTE: save the geometry file in the "input" folder 
geometry_name = "geometry.json" # geometry file, pre-generated for this tutorial.
n_img = 1

# 03. SETUP CORTO SCENE 

ENV, State, cam = corto_scene_setup(geometry_name)

# 04. GENERATE THE IMAGES SEQUENTIALLY

for idx in range(0,n_img):
    ENV.PositionAll(State,index=idx)
    ENV.RenderOne(cam, State, index=idx)
corto.Utils.save_blend(State)

# 05. CONTINUE TO DO YOUR THING. Rinse and repeat from STEP 01 if you are in an iterative process (e.g. covariance analysis, batch estimation, etc.)
