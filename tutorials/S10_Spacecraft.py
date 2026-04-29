"""
Tutorial script to render images of the S10_Spacecraft scenario. 

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
scenario_name = "S10_Spacecraft" # Name of the scenario folder
scene_name = "scene_CYCLES.json" # name of the scene input, slow rendering setup, high quality
# scene_name = "scene_EEVEE.json" # name of the scene input, fast rendering setup, lower quality
geometry_name = "geometry.json" # name of the geometry input
body_name = "Dawn.gltf" # name of the body input
# body_name = "mover.glb" # Lunar Gateway, #TODO, convert to gltf and save with proper name
# body_name = "SSREF_IGOAL.glb" # ISS, #TODO, convert to gltf and save with proper name

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
# Not needed for the spacecraft, already loaded wiht the gltf file

### (4) COMPOSITING PROPERTIES ###
# Build image-label pairs pipeline
tree = corto.Compositing.create_compositing()
render_node = corto.Compositing.rendering_node(tree, (0,0)) # Create Render node
corto.Compositing.create_img_denoise_branch(tree,render_node) # Create img_denoise branch
corto.Compositing.create_depth_branch(tree,render_node,State) # Create depth branch
corto.Compositing.create_slopes_branch(tree,render_node,State) # Create slopes branch

corto.Compositing.create_lidar_depth_branch(tree,render_node,State) # Create ID mask branch
corto.Compositing.create_lidar_normal_branch(tree,render_node,State) # Create ID mask branch

corto.Compositing.create_tof_branch(tree, render_node, State)

# corto.Compositing.create_maskID_branch(tree,render_node,State) # Create ID mask branch

fov_x_deg = 5.0 # FOV of the LiDAR and ToF sensors, should be smaller than the camera FOV to avoid edge artefacts

lidar = corto.LiDAR(State)
lidar.set_scan_pattern(n_channels=64, v_fov=(-fov_x_deg, fov_x_deg), h_fov=(-fov_x_deg, fov_x_deg), h_resolution=0.05)
lidar.set_noise(range_sigma=0.05, angle_sigma_deg=0.02)
lidar.set_range(max_range=200.0, range_bin_m=0.01)
lidar.set_returns(min_intensity=0.005, grazing_deg=80.0)
lidar.set_output(save_ply=True)  # optional saving

tof = corto.TimeOfFlight(State)
tof.set_sensor(width=640, height=480, fov_x_deg=70.0)
tof.set_range(max_range=12, range_bin_m=0.001)
tof.set_noise(sigma_thermal=0.005, sigma_wiggling_k=0.003)
tof.set_artefacts(multipath_strength=0.02, flying_pixel_radius=2)

sl = corto.StructuredLight(State)
sl.set_projector(offset_m=0.05, cant_deg=5.0, spot_size_deg=0.1, energy=1000.0, projector_distance_m = 10, pattern="triangle")
sl.set_color(r=1.0, g=0.0, b=0.0) # red
sl.setup(State, cam)


### (5) GENERATION OF IMG-LBL PAIRS ###
body.set_scale(np.array([0.1, 0.1, 0.1])) # adjust body scale for better test renderings

import bpy
n_img = 1 # Render the first "n_img" images
for idx in range(0,n_img):
    ENV.PositionAll(State,index=idx)
    ENV.RenderOne(cam, State, index=idx)

    # Structured Light projection
    #TODO: running process_one at the end messes up again the render and generate double depths exr etc. 
    #TODO: the light scaling according to distance to target is not working properly.
    sl.process_one(State, index=idx)

    # LiDAR processing
    cam_obj = bpy.data.objects['WFOV_Camera']
    R = np.array(cam_obj.matrix_world)[:3, :3].astype(np.float32)
    lidar.set_camera_rotation(R)
    lidar.process_one(State, index=idx, cam=cam)

    # ToF processing
    tof.set_camera_rotation(R)
    tof.process_one(State, index=idx, cam=cam)

# Save .blend as debug
corto.Utils.save_blend(State)