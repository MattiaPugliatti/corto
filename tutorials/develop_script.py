import sys
import numpy as np
sys.path.append('./cortopy')

import cortopy as corto
#import bpy 

# These should be read from .txt, prototyping in python ad properties dictionary
properties = {
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

cam_1 = corto.Camera('WFOV_1', properties)

print('-----')
print(cam_1.get_name())
print(cam_1.get_position())
print(cam_1.get_orientation())
print(cam_1.get_fov())
print(cam_1.get_res())
print(cam_1.get_Tint())
print(cam_1.get_sensor())
print(cam_1.get_K())

cam_1.set_position(np.array([1,0,0]))
print(cam_1.get_position())


