"""
Tutorial script to render images of the S01_Eros scenario. 
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
scenario_name = "S07_Mars_Phobos_Deimos" # Name of the scenario folder
scene_name = "scene_mmx.json" # name of the scene input
geometry_name = "geometry_mmx.json" # name of the geometry input
body_name = ["g_phobos_287m_spc_0000n00000_v002.obj",
             "Mars_65k.obj",
             "g_deimos_162m_spc_0000n00000_v001.obj"] # name of the body input

# Load inputs and settings into the State object
State = corto.State(scene = scene_name, geometry = geometry_name, body = body_name, scenario = scenario_name)
# Add extra inputs 
State.add_path('albedo_path_1',os.path.join(State.path["input_path"],'body','albedo','Phobos grayscale.jpg'))
State.add_path('uv_data_path_1',os.path.join(State.path["input_path"],'body','uv data','g_phobos_287m_spc_0000n00000_v002.json'))
State.add_path('albedo_path_2',os.path.join(State.path["input_path"],'body','albedo','mars_1k_color.jpg'))
State.add_path('uv_data_path_2',os.path.join(State.path["input_path"],'body','uv data','Mars_65k.json'))
State.add_path('albedo_path_3',os.path.join(State.path["input_path"],'body','albedo','Deimos grayscale.jpg'))
State.add_path('uv_data_path_3',os.path.join(State.path["input_path"],'body','uv data','g_deimos_162m_spc_0000n00000_v001.json'))

### (2) SETUP THE SCENE ###
# Setup bodies
cam = corto.Camera('WFOV_Camera', State.properties_cam)
sun = corto.Sun('Sun',State.properties_sun)
name_1, _ = os.path.splitext(body_name[0])
body_1 = corto.Body(name_1,State.properties_body_1)
name_2, _ = os.path.splitext(body_name[1])
body_2 = corto.Body(name_2,State.properties_body_2)
name_3, _ = os.path.splitext(body_name[2])
body_3 = corto.Body(name_3,State.properties_body_3)

# Setup rendering engine
rendering_engine = corto.Rendering(State.properties_rendering)
# Setup environment
ENV = corto.Environment(cam, [body_1,body_2,body_3], sun, rendering_engine)

### (3) MATERIAL PROPERTIES ###
material_1 = corto.Shading.create_new_material('properties body 1')
material_2 = corto.Shading.create_new_material('properties body 2')
material_3 = corto.Shading.create_new_material('properties body 3')

corto.Shading.create_branch_albedo_mix(material_1, State,1)
corto.Shading.create_branch_albedo_mix(material_2, State,2)
corto.Shading.create_branch_albedo_mix(material_3, State,3)

corto.Shading.load_uv_data(body_1,State,1)
corto.Shading.assign_material_to_object(material_1, body_1)
corto.Shading.load_uv_data(body_2,State,2)
corto.Shading.assign_material_to_object(material_2, body_2)
corto.Shading.load_uv_data(body_3,State,3)
corto.Shading.assign_material_to_object(material_3, body_3)

### (4) COMPOSITING PROPERTIES ###
# Build image-label pairs pipeline
tree = corto.Compositing.create_compositing()
render_node = corto.Compositing.rendering_node(tree, (0,0)) # Create Render node
corto.Compositing.create_img_denoise_branch(tree,render_node) # Create img_denoise branch
corto.Compositing.create_depth_branch(tree,render_node) # Create depth branch
corto.Compositing.create_slopes_branch(tree,render_node,State) # Create slopes branch
corto.Compositing.create_maskID_branch(tree,render_node,State) # Create ID mask branch

### (5) GENERATION OF IMG-LBL PAIRS ###
body_1.set_scale(np.array([1, 1, 1])) # adjust body scale for better test renderings
body_2.set_scale(np.array([1e3, 1e3, 1e3])) # adjust body scale for better test renderings
body_3.set_scale(np.array([1, 1, 1])) # adjust body scale for better test renderings

n_img = 1 # Render the first "n_img" images
for idx in range(0,n_img):
    ENV.PositionAll(State,index=idx)
    ENV.RenderOne(cam, State, index=idx, depth_flag = True)

# Save .blend as debug
corto.Utils.save_blend(State)