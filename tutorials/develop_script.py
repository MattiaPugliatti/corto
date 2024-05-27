import sys, os
import numpy as np

sys.path.append(os.getcwd())

import cortopy as corto

# These should be read from .txt, prototyping in python ad properties dictionary
properties_cam = {
    'fov': 10, # [deg]]
    'res_x': 1024, # [px]
    'res_y': 1024, # [px]
    'film_exposure': 10, # [s]
    'sensor': 'RGB',
    'K': np.eye(3,dtype = float),
    'clip_start': 0.1, # [BU]
    'clip_end': 1e4, # [BU]
    'bit_encoding': '8',
    'viewtransform': 'Filmic',
}

properties_sun = {
    'angle': 0.53, # [deg]
    'energy': 7, # [W]
}

properties_body = {
    'pass_index': 1, # [-]
    'diffuse_bounces': 0, # [-]
}

properties_rendering = {
    'engine': 'CYCLES',
    'device': 'CPU',
    'samples': 32, # [-]
    'preview_samples': 4, # [-]
}

### SETUP THE SCENE ###
cam_1 = corto.Camera('WFOV_1', properties_cam)
sun = corto.Sun('Sun',properties_sun)
body = corto.Body('Cube',properties_body)
rendering_engine = corto.Rendering('R1',properties_rendering) # Rendering Engine

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
print(rendering_engine.get_name())
print(rendering_engine.get_engine())
print(rendering_engine.get_device())
print(rendering_engine.get_sample())
print(rendering_engine.get_preview_sample())

rendering_engine.set_sample(16)
print(rendering_engine.get_sample())

'''
#ENV = corto.environment.generate_environment(CAM1,BODY,SUN, REN,'Scene')

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