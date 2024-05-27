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

cam_1 = corto.Camera('WFOV_1', properties_cam)

print('-----')
print(cam_1.get_name())
print(cam_1.get_position())
print(cam_1.get_orientation())
print(cam_1.get_fov())
print(cam_1.get_res())
print(cam_1.get_film_exposure())
print(cam_1.get_sensor())
print(cam_1.get_K())

print('-----')
print('Previous position: \n')
print(cam_1.get_position())
print('Next position: \n')
cam_1.set_position(np.array([1,0,0]))
print(cam_1.get_position())

print(cam_1)

properties_sun = {
    'angle': 0.53, # [deg]]
    'energy': 7, # [W]
}

sun = corto.Sun('Sun',properties_sun)
print('-----')
print(sun.get_name())
print(sun.get_position())
print(sun.get_orientation())

sun.set_position(np.array([10,25,0]))

print(sun.get_position())
print(sun.get_orientation())