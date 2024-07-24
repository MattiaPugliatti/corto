import sys, os
import json
import numpy as np

sys.path.append(os.getcwd())

import cortopy as corto

# INPUT 
scenario_path = os.path.join('input','S01_Eros')
scene_file = os.path.join(scenario_path,'scene','scene.json')
geometry_file = os.path.join(scenario_path,'geometry','geometry.json')
body_file = os.path.join(scenario_path,'body')

# Load inputs and settings into the State object
State = corto.State(scene = scene_file, geometry = geometry_file, body = 'TBD')

# check lenght of input data, if less than 4 not all structures were initialized.
properties_cam = State.properties_cam
#properties_cam["K"] = eval(properties_cam["K"])
properties_sun = State.properties_sun
properties_body = State.properties_body
properties_rendering = State.properties_rendering

### SETUP THE SCENE ###
# Setup bodies
cam = corto.Camera('WFOV_Camera', properties_cam)
sun = corto.Sun('Sun',properties_sun)
body = corto.Body('Cube',properties_body)
# Setup rendering engine
rendering_engine = corto.Rendering(properties_rendering)
# Setup environmen
ENV = corto.Environment(cam, body, sun, rendering_engine)

idx = 0 
ENV.PositionAll(State,index=idx)
ENV.RenderOne(os.path.join('output'), index=idx)
print(ENV.get_positions())

idx = 1 
ENV.PositionAll(State,index=idx)
ENV.RenderOne(os.path.join('output'), index=idx)
print(ENV.get_positions())

### TEST GET and SET methods ###

print('---Camera--')
print(cam.get_name())
print(cam.get_position())
print(cam.get_orientation())
print(cam.get_fov())
print(cam.get_res())
print(cam.get_film_exposure())
print(cam.get_sensor())
print(cam.get_K())

print('Previous position: \n')
print(cam.get_position())

print('---Sun--')
print(sun.get_name())
print(sun.get_orientation())

#sun.set_position(np.array([10,25,0]))

print(sun.get_position())
print(sun.get_orientation())

print('---Body--')
print(body.get_name())
print(body.get_position())
print(body.get_orientation())

#body.set_orientation(np.array([0.707107,0.707107,0,0]))

print(body.get_orientation())

print('---Rendering engine--')
print(rendering_engine.get_engine())
print(rendering_engine.get_device())
print(rendering_engine.get_sample())
print(rendering_engine.get_preview_sample())

rendering_engine.set_sample(64)
print(rendering_engine.get_sample())
