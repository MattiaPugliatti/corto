import sys
import os
sys.path.append(os.getcwd())
import cortopy as corto

## Clean all existing/Default objects in the scene 
corto.Utils.clean_scene()

### (1) DEFINE INPUT ### 
scenario_name = "S02_Itokawa" # Name of the scenario folder
scene_name = "scene.json" # name of the scene input
geometry_name = "geometry.json" # name of the geometry input
body_name = "25143_Itokawa_512ICQ.obj" # name of the body input

# Load inputs and settings into the State object
State = corto.State(scene = scene_name, geometry = geometry_name, body = body_name, scenario = scenario_name)
# Add extra inputs 
State.add_path('texture_path',os.path.join(State.path["input_path"],'body','texture','Itokawa Grayscale.jpg'))

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
import numpy as np
body.set_orientation(np.array([1,0,0,0]))
body.set_position(np.array([0,0,0]))
corto.Shading.uv_unwrap(uv_unwrap_method = 3, aux_input = [False, False, 'VIEW_ON_POLES','POLAR_ZX'], body = body)

material = corto.Shading.create_new_material('corto shading test')
corto.Shading.create_branch_texture_mix(material, State)
corto.Shading.assign_material_to_object(material, body)

corto.Utils.save_blend(State)

### (4) COMPOSITING PROPERTIES ###
# Build image-label pairs pipeline
tree = corto.Compositing.create_compositing()
render_node = corto.Compositing.rendering_node(tree, (0,0)) # Create Render node
corto.Compositing.create_img_denoise_branch(tree,render_node,State) # Create img_denoise branch
corto.Compositing.create_depth_branch(tree,render_node,State) # Create depth branch
corto.Compositing.create_slopes_branch(tree,render_node,State) # Create slopes branch
corto.Compositing.create_maskID_branch(tree,render_node,State) # Create ID mask branch

# 'VIEW_ON_EQUATOR': Project from the view along the equator.
# 'VIEW_ON_POLES': Project from the view along the poles.
### (5) GENERATION OF IMG-LBL PAIRS ###

body.set_scale(np.array([0.1, 0.1, 0.1])) # adjust body scale for better test renderings

n_img = 1 # Render the first "n_img" images
for idx in range(0,n_img):
    ENV.PositionAll(State,index=idx)
    ENV.RenderOne(cam, State, index=idx, depth_flag = True)

# Save .blend as debug
#corto.Utils.save_blend(State)