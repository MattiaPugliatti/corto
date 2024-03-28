
import sys
import numpy as np
sys.path.append("./src/")
from corto.rendering.camera import camera

properties = {}
# These should be reat from .txt
properties['fov'] = 10
properties['res_x'] = 1024
properties['res_y'] = 2048
properties['T_int'] = 10
properties['sensor'] = 'RGB'
properties['K'] = np.zeros((3,3),float)

cam_1 = camera('WFOV_1',properties)


print('-----')
print(cam_1.get_name())
print(cam_1.get_location())
print(cam_1.get_orientation())

cam_1.set_position(np.array([1,0,0]))
print(cam_1.get_location())
print(cam_1.get_fov())
print(cam_1.get_res())
print(cam_1.get_Tint())
print(cam_1.get_sensor())
print(cam_1.get_K())

