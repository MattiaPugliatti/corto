# This script is used to render the Didymos scene from input transmitted by the milani-gnc prototype.
# This CORTO interface works by saving the rendered scene from the composite in the "output_path" and sending a ping
# by TCP to Simulink to close the loop. This model works with the NAVCAM_HF_1_a model, the actual image is not transmitted from Blender to Simulink,
# instead, it is saved in Blender and read in Simulink.

import socket
import struct
import time
import numpy as np
import bpy
import mathutils
import sys
import pickle
import os

#### (1) STATIC PARAMETERS ####

#NAVCAM
FOV_x = 21 # [deg], Horizontal FOV of the NAVCAM
FOV_y = 16 # [deg], Vertical FOV of the NAVCAM
sensor_size_x = 2048 #[pxl], Horizontal resolution of the images
sensor_size_y = 1536 #[pxl], Vertical resolution of the images
n_channels = 1 #[-], Number of channels of the images
bit_encoding = 8 #[-], Number of bit per pixel
compression = 15 #[-], Compression factor

#RENDERING ENGINE
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.device = 'CPU'
bpy.context.scene.cycles.samples = 4 # number of samples
bpy.context.scene.cycles.diffuse_bounces = 0 #To avoid diffused light from D1 to D2. (4) default
bpy.context.scene.render.tile_x = 64 # tile size(x)
bpy.context.scene.render.tile_y = 64 # tile size(y)

#OTHERS
#Path where the image get saved
output_path = 'C:\\Users\\Pugliatti Mattia\\Documents\\milaniGNC_BUFFER'


n_zfills = 6 #Number of digits used in the image name
model_name_1 = 'D1'
model_name_2 = 'D2'
sun_energy = 2 #Energy value of the sun-light in Blender
specular_factor = 0 #Specularity value for the sun-light in Blender
address = "0.0.0.0"
port_M2B = 51001 #  Port from Matlab to Blender
port_B2M = 30001 #  Port from Blender to Matlab

#### (2) SCENE SET UP ####
CAM = bpy.data.objects["Camera"]
SUN = bpy.data.objects["Light"]
BODY_1 = bpy.data.objects[model_name_1]
BODY_2 = bpy.data.objects[model_name_2]

# Camera parameters
CAM.data.type = 'PERSP'
CAM.data.lens_unit = 'FOV'
CAM.data.angle = FOV_x * np.pi / 180
CAM.data.clip_start = 0.5 # [m] in Blender, but scaled in km
CAM.data.clip_end = 100 # [m] in Blender, but scaled in km
bpy.context.scene.render.pixel_aspect_x = 1
bpy.context.scene.render.pixel_aspect_y = 1
bpy.context.scene.render.resolution_x = sensor_size_x # CAM resolution (x)
bpy.context.scene.render.resolution_y = sensor_size_y # CAM resolution (y)

# Light parameters
SUN.data.type = 'SUN'
SUN.data.energy = sun_energy  # To perform quantitative analysis
SUN.data.specular_factor = specular_factor

# Environment parameters
bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = (0, 0, 0, 1)

if n_channels == 1:
    bpy.context.scene.render.image_settings.color_mode = 'BW'
elif n_channels == 3:
    bpy.context.scene.render.image_settings.color_mode = 'RGB'
elif n_channels == 4:
    bpy.context.scene.render.image_settings.color_mode = 'RGBA'

bpy.context.scene.render.image_settings.color_depth = str(bit_encoding)
bpy.context.scene.render.image_settings.compression = compression

#### (3) DYNAMIC PARAMETERS ####
#Initialization of Bodies, Cam and Sun
BODY_1.location = [0, 0, 0]
BODY_2.location = [0, 0, 0]
CAM.location = [10, 0, 0]
SUN.location = [0, 0, 0]

BODY_1.rotation_mode = 'QUATERNION'
BODY_2.rotation_mode = 'QUATERNION'
CAM.rotation_mode = 'QUATERNION'
SUN.rotation_mode = 'QUATERNION'

BODY_1.rotation_quaternion = [1, 0, 0, 0]
BODY_2.rotation_quaternion = [1, 0, 0, 0]
CAM.rotation_quaternion = [1, 0, 0, 0]
SUN.rotation_quaternion = [1, 0, 0, 0]

#### (4) FUNCTION DEFINITIONS ####
def Render(ii):
    name = '\{}.png'.format(str(int(ii)).zfill(6))
    bpy.context.scene.render.filepath = output_path + '/' + name
    bpy.ops.render.render(write_still=1)
    return

def PositionAll(PQ_SC,PQ_Bodies,PQ_Sun):
    SUN.location = [0,0,0] # Because in Blender it is indifferent where the sun is located
    CAM.location = [PQ_SC[0], PQ_SC[1], PQ_SC[2]]
    BODY_1.location = [PQ_Bodies[0,0],PQ_Bodies[0,1],PQ_Bodies[0,2]]
    BODY_2.location = [PQ_Bodies[1,0],PQ_Bodies[1,1],PQ_Bodies[1,2]]
    SUN.rotation_quaternion = [PQ_Sun[3], PQ_Sun[4], PQ_Sun[5], PQ_Sun[6]]
    CAM.rotation_quaternion = [PQ_SC[3], PQ_SC[4], PQ_SC[5], PQ_SC[6]]
    BODY_1.rotation_quaternion = [PQ_Bodies[0,3], PQ_Bodies[0,4], PQ_Bodies[0,5], PQ_Bodies[0,6]]
    BODY_2.rotation_quaternion = [PQ_Bodies[1,3], PQ_Bodies[1,4], PQ_Bodies[1,5], PQ_Bodies[1,6]]
    return

#### (5) ESTABLISH UDP/TCP CONNECTION ####
r = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

r.bind((address, port_M2B))
s.bind((address, port_B2M))

s.listen(5)
(clientsocket, address) = s.accept()

print("Waiting for data...\n")

#### (6) RECEIVE DATA AND RENDERING ####

receiving_flag = 1
ii = 0
while receiving_flag:
    data, addr = r.recvfrom(512)
    numOfValues = int(len(data) / 8)
    data = struct.unpack('>' + 'd' * numOfValues, data)
    n_bodies = len(data)/7-2 #Number of bodies apart from CAM and SUN
    # Extract the PQ vectors from data received from cuborg
    PQ_Sun = data[0:7]
    PQ_SC = data[7:14]
    PQ_Bodies = data[14:]
    PQ_Bodies = np.reshape(PQ_Bodies,(int(n_bodies),7))
    # Print the PQ vector info
    print('SUN:   POS ' +  str(PQ_Sun[0:3]) + ' - Q ' + str(PQ_Sun[3:7]))
    print('SC:    POS ' +  str(PQ_SC[0:3]) + ' - Q ' + str(PQ_SC[3:7]))
    for jj in np.arange(0,n_bodies):
        print('BODY (' + str(jj) + '):   POS: ' +  str(PQ_Bodies[int(jj),0:3]) + ' - Q ' + str(PQ_Bodies[int(jj),3:7]))
    #Position all bodies in the scene
    #PQ_SC = [PQ_SC[0],PQ_SC[1],PQ_SC[2],1,0,0,0]
    PositionAll(PQ_SC,PQ_Bodies,PQ_Sun)
    #Take a picture
    Render(ii)
    #Send an aknowledgement signal to cuborg
    a = np.double(ii)
    data_string = pickle.dumps(a)
    clientsocket.send(data_string)
    ii = ii + 1
