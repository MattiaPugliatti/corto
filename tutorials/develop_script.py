import sys, os
import json
import numpy as np
import bpy 

sys.path.append(os.getcwd())

import cortopy as corto

## CLEAN all existing/Default objects in the scene 
corto.Utils.clean_scene()

# I/O 
# Input
scenario_path = os.path.join('input','S01_Eros')
scene_file = os.path.join(scenario_path,'scene','scene.json')
geometry_file = os.path.join(scenario_path,'geometry','geometry.json')
body_file = os.path.join(scenario_path,'body','Shape','433_Eros_512ICQ.obj')
# Output
output_path = os.path.join('output')

# Load inputs and settings into the State object
State = corto.State(scene = scene_file, geometry = geometry_file, body = body_file)
State.output_path(output_path)

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

# Automatic build
#corto.Compositing.create_simple_compositing(tree) # automatic-build of node-tree

# Create Render node
render_node = corto.Compositing.rendering_node(tree, (0,0))
# Create img_denoise branch
corto.Compositing.create_img_denoise_branch(tree,render_node,State)
# Create depth branch
corto.Compositing.create_depth_branch(tree,render_node,State)
# Create slopes branch
corto.Compositing.create_slopes_branch(tree,render_node,State)

#TODO: Create object ID branch
#TODO: Add depthmap method somewhere

body.set_scale(np.array([0.1, 0.1, 0.1])) # adjust body scale for better test renderings
sun.set_energy = 0.1 #TODO: This one is not working

# Render the first 10 images
for idx in range(0,2):
    ENV.PositionAll(State,index=idx)
    ENV.RenderOne(cam, State, index=idx)

corto.Utils.save_blend(State)
