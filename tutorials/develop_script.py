import sys, os
import json
import numpy as np

sys.path.append(os.getcwd())

import cortopy as corto

#TODO: put scene properties into State class
# These should be read from .txt, prototyping in python ad properties dictionary
print(os.getcwd())
# Opening JSON file
f = open('./tutorials/scene.json')
# returns JSON object as 
# a dictionary
settings_json = json.load(f)

# check lenght of input data, if less than 4 not all structures were initialized.
properties_cam = settings_json["camera_settings"]
properties_cam["K"] = eval(properties_cam["K"])
properties_sun = settings_json["sun_settings"]
properties_body = settings_json["body_settings"]
properties_rendering = settings_json["rendering_settings"]

### SETUP THE SCENE ###
# Setup bodies
cam_1 = corto.Camera('WFOV_1', properties_cam)
sun = corto.Sun('Sun',properties_sun)
body = corto.Body('Cube',properties_body)
# Setup rendering engine
rendering_engine = corto.Rendering(properties_rendering)
# Setup environmen
ENV = corto.Environment(cam_1,body,sun, rendering_engine)

print('---Camera--')
print(cam_1.get_name())
print(cam_1.get_position())
print(cam_1.get_orientation())
print(cam_1.get_fov())
print(cam_1.get_res())
print(cam_1.get_film_exposure())
print(cam_1.get_sensor())
print(cam_1.get_K())

print('Previous position: \n')
print(cam_1.get_position())
print('Next position: \n')
cam_1.set_position(np.array([1,0,0]))
print(cam_1.get_position())

print('---Sun--')
print(sun.get_name())
print(sun.get_position())
print(sun.get_orientation())

sun.set_position(np.array([10,25,0]))

print(sun.get_position())
print(sun.get_orientation())

print('---Body--')
print(body.get_name())
print(body.get_position())
print(body.get_orientation())

body.set_orientation(np.array([0.707107,0.707107,0,0]))

print(body.get_orientation())

print('---Rendering engine--')
print(rendering_engine.get_engine())
print(rendering_engine.get_device())
print(rendering_engine.get_sample())
print(rendering_engine.get_preview_sample())

rendering_engine.set_sample(64)
print(rendering_engine.get_sample())

print(ENV.get_positions())
print(ENV.get_orientations())

state_cam = np.array([1,1,1,1,0,0,0])
state_body = np.array([2,2,2,1,0,0,0])
state_sun = np.array([3,3,3])

state_env = np.concatenate((state_cam,state_body,state_sun))

'''

### SHADING AND COMPOSITING ###

corto.shading
corto.compositing

### GENERATE DATASET ###

for ii in range(0,len(states.n_images)):
    ENV.Position_all(states[0])
    ENV.render()

# or 
    
ENV.generate_ds(states)       
'''