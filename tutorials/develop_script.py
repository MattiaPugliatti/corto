import sys, os
import json
import numpy as np

sys.path.append(os.getcwd())

import cortopy as corto

import bpy

## CLEAN all existing/Default objects in the scene 
#TODO: think this through with the body class
# Deselect all objects
bpy.ops.object.select_all(action='DESELECT')
# Select all objects
bpy.ops.object.select_all(action='SELECT')
# Delete all selected objects
bpy.ops.object.delete()

# I/O 
scenario_path = os.path.join('input','S01_Eros')
scene_file = os.path.join(scenario_path,'scene','scene.json')
geometry_file = os.path.join(scenario_path,'geometry','geometry.json')
body_file = os.path.join(scenario_path,'body','Shape','433_Eros_512ICQ.obj')

# Load inputs and settings into the State object
State = corto.State(scene = scene_file, geometry = geometry_file, body = body_file)

### SETUP THE SCENE ###
# Setup bodies
cam = corto.Camera('WFOV_Camera', State.properties_cam)
sun = corto.Sun('Sun',State.properties_sun)
body = corto.Body('433_Eros_512ICQ',State.properties_body)

# Setup rendering engine
rendering_engine = corto.Rendering(State.properties_rendering)
# Setup environmen
ENV = corto.Environment(cam, body, sun, rendering_engine)

# Setup shading 
material = corto.Shading.create_new_material('corto shading test')
#corto.Shading.create_simple_diffuse_BSDF(material, BSDF_color_RGB= np.array([np.random.rand(),np.random.rand(),np.random.rand()]))
corto.Shading.create_simple_principled_BSDF(material, PBSDF_color_RGB= np.array([np.random.rand(),np.random.rand(),np.random.rand()]))
corto.Shading.assign_material_to_object(material, body)

# Setup compositing
tree = corto.Compositing.create_compositing()
corto.Compositing.create_simple_compositing(tree)

body.set_scale(np.array([0.1, 0.1, 0.1])) # adjust body scale for better test renderings
sun.set_energy = 0.1 #TODO: THis one is not working

# Render the first 10 images
for idx in range(0,10):
    ENV.PositionAll(State,index=idx)
    ENV.RenderOne(cam, os.path.join('output','ìmg'), index=idx)

corto.State.save_blend(os.path.join('blend','debug'))
