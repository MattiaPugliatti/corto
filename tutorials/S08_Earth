import sys
import os
sys.path.append(os.getcwd())
import cortopy as corto
import numpy as np

## Clean all existing/Default objects in the scene 
corto.Utils.clean_scene()

### (1) DEFINE INPUT ### 
scenario_name = "S08_Earth" # Name of the scenario folder
scene_name = "scene_earth.json" # name of the scene input
geometry_name = "geometry_earth.json" # name of the geometry input
body_name = ["Earth.obj","Atmosphere.obj","Clouds.obj","g_phobos_036m_spc_0000n00000_v002.obj"] # name of the bodies 

# Load inputs and settings into the State object
State = corto.State(scene = scene_name, geometry = geometry_name, body = body_name, scenario = scenario_name)
# LOW-RES setup
State.add_path('earth_color',os.path.join(State.path["input_path"],'body','albedo','earth_color_10K.tif')) 
State.add_path('earth_landocean',os.path.join(State.path["input_path"],'body','albedo','earth_landocean_4K.png'))
State.add_path('earth_night',os.path.join(State.path["input_path"],'body','albedo','earth_nightlights_10K.tif'))
State.add_path('earth_clouds',os.path.join(State.path["input_path"],'body','albedo','earth_clouds_8K.tif'))
State.add_path('earth_displacement',os.path.join(State.path["input_path"],'body','displacement','topography_5k.png'))

# HIGH-RES setup
#State.add_path('earth_color',os.path.join(State.path["input_path"],'body','albedo','earth_color_43K.tif'))
#State.add_path('earth_landocean',os.path.join(State.path["input_path"],'body','albedo','earth_landocean_16K.png'))
#State.add_path('earth_night',os.path.join(State.path["input_path"],'body','albedo','earth_nightlights_10K.tif'))
#State.add_path('earth_clouds',os.path.join(State.path["input_path"],'body','albedo','earth_clouds_43K.tif'))
#State.add_path('earth_displacement',os.path.join(State.path["input_path"],'body','displacement','topography_21K.png'))


State.add_path('albedo_path_4',os.path.join(State.path["input_path"],'body','albedo','Phobos grayscale.jpg'))
State.add_path('uv_data_path_4',os.path.join(State.path["input_path"],'body','uv data','g_phobos_036m_spc_0000n00000_v002.json'))


### (2) SETUP THE SCENE ###
# Setup bodies
cam = corto.Camera('WFOV_Camera', State.properties_cam)
sun = corto.Sun('Sun',State.properties_sun)
name_1, _ = os.path.splitext(body_name[0])
name_2, _ = os.path.splitext(body_name[1])
name_3, _ = os.path.splitext(body_name[2])
name_4, _ = os.path.splitext(body_name[3])


earth = corto.Body(name_1,State.properties_body_1)
atmosphere = corto.Body(name_2,State.properties_body_2)
clouds = corto.Body(name_3,State.properties_body_3)
apophis = corto.Body(name_4,State.properties_body_4)

# Setup rendering engine
rendering_engine = corto.Rendering(State.properties_rendering)
# Setup environment
ENV = corto.Environment(cam, [earth,atmosphere,clouds,apophis], sun, rendering_engine)

### (3) MATERIAL PROPERTIES ###
material_earth = corto.Shading.create_new_material('Earth Surface', displace_and_bump = "BOTH")
material_atmosphere = corto.Shading.create_new_material('Earth Atmosphere')
material_clouds = corto.Shading.create_new_material('Earth Clouds', displace_and_bump = "BOTH")
material_apophis = corto.Shading.create_new_material('Apophis')

# TODO: generalize and export these settings in the scene.json? 

# Earth land-ocean
albedo_earth = {'hue': 0.5, 'saturation': 0.5, 'hue_scale': 1,
                'land_ocean_from_min': 0, 'land_ocean_from_max': 1, 'land_ocean_to_min': 1, 'land_ocean_to_max': 0.1,
                'night_temperature': 3500, 
                'night_from_min': -0.1, 'night_from_max': -0.2, 'night_to_min': 0, 'night_to_max': 0.75,
                }
displacement_earth = {'earth_midlevel': 0, 'earth_scale': 0.01}

settings_earth_shader = {'displacement': displacement_earth, 'albedo': albedo_earth}
corto.Shading.create_earth_shader(material_earth, State, settings_earth_shader)
corto.Shading.assign_material_to_object(material_earth, earth)

# Atmosphere
settings_atmosphere_shader= {'atm_color': (0.316, 0.612, 1, 1), 'atm_density': 1, 'atm_anisotropy': 0}
corto.Shading.create_atmosphere_shader(material_atmosphere, settings_atmosphere_shader)
corto.Shading.assign_material_to_object(material_atmosphere, atmosphere)
# Clouds
albedo_clouds = {'radius_0': 1, 'radius_1': 1, 'radius_2': 1,'subsurf_scale': 7}
displacement_clouds = {'clouds_midlevel': 0, 'clouds_scale': 0.01}
settings_clouds_shader = {'displacement': displacement_clouds, 'albedo': albedo_clouds}
corto.Shading.create_clouds_shader(material_clouds, State, settings_clouds_shader)
corto.Shading.assign_material_to_object(material_clouds, clouds)
# Apophis
corto.Shading.create_branch_albedo_mix(material_apophis, State,4)
corto.Shading.load_uv_data(apophis,State,4)
corto.Shading.assign_material_to_object(material_apophis, apophis)

# adjust body scale for better test renderings
atmosphere.set_scale(np.array([0.95, 0.95, 0.95]))
apophis.set_scale(np.array([0.001, 0.001, 0.001]))

### (4) COMPOSITING PROPERTIES ###
# Build image-label pairs pipeline
tree = corto.Compositing.create_compositing()
render_node = corto.Compositing.rendering_node(tree, (0,0)) # Create Render node
corto.Compositing.create_img_denoise_branch(tree,render_node) # Create img_denoise branch
corto.Compositing.create_depth_branch(tree,render_node) # Create depth branch
corto.Compositing.create_slopes_branch(tree,render_node,State) # Create slopes branch
corto.Compositing.create_maskID_branch(tree,render_node,State) # Create ID mask branch

n_img = 6 # Render the first "n_img" images
for idx in range(0,n_img):
    ENV.PositionAll(State,index=idx)
    ENV.RenderOne(cam, State, index=idx, depth_flag = False)

# Save .blend as debug
corto.Utils.save_blend(State)