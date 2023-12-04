import bpy
import mathutils
import numpy as np
import csv
import os
import time
import math

from random import randint
from datetime import datetime

def read_and_parse_config(filename):
    body = {}
    geometry = {}
    scene = {}
    corto = {}
    with open(filename, 'r') as file:
        for line in file:
            # Skip comments and empty lines
            if line.strip() == '' or line.startswith('#'):
                continue
            # Split the line at the '=' sign
            key, value = map(str.strip, line.split('='))
            # Extract the first word before the underscore
            category = key.split('_')[0]
            # Convert the value to the appropriate type (int or float if possible)
            try:
                value = int(value)
            except ValueError:
                try:
                    value = float(value)
                except ValueError:
                    pass  # Keep it as a string if it can't be converted
            # Save the variable to the corresponding dictionary
            if category == 'body':
                body[key.split('_')[1]] = value
            elif category == 'geometry':
                geometry[key.split('_')[1]] = value
            elif category == 'scene':
                scene[key.split('_')[1]] = value
            elif category == 'corto':
                corto[key.split('_')[1]] = value
    # Display the loaded variables
    for key, value in body.items():
        print(f"{key}: {value}")
    print('')
    for key, value in geometry.items():
        print(f"{key}: {value}")
    print('')
    for key, value in scene.items():
        print(f"{key}: {value}")
    print('')
    for key, value in corto.items():
        print(f"{key}: {value}")
    print('')
    return body, geometry, scene, corto

######[1]  (START) INPUT SECTION (START) [1]######
filename = 'G:\\My Drive\\OneDrive - Politecnico di Milano\\09-Code\\052-NavigationRegimes\\Rendering Models\\DeployCORTO\\input\\ALL.txt'
filename = 'ENTER THE PATH where your "ALL.txt" is saved '
######[1]  (END) INPUT SECTION (END) [1]######

body, geometry, scene, corto = read_and_parse_config(filename)


######[2]  SETUP OBJ PROPERTIES [2]######
# Set object names
CAM = bpy.data.objects["Camera"]
SUN = bpy.data.objects["Sun"]
if body['name'] == 'S1_Eros':
    albedo = 0.15 # TBD
    SUN_energy = 7 # TBD
    BODY = bpy.data.objects["Eros"]
    scale_BU = 10
    texture_name = 'Eros Grayscale'
elif body['name'] == 'S2_Itokawa':
    albedo = 0.15 # TBD
    SUN_energy = 5 # TBD
    BODY = bpy.data.objects["Itokawa"]
    scale_BU = 1
    texture_name = 'Itokawa Grayscale'
elif body['name'] == 'S4_Bennu':
    albedo = 0.15 # TBD
    SUN_energy = 7 # TBD
    BODY = bpy.data.objects["Bennu"]
    scale_BU = 1
    texture_name = 'Bennu_global_FB34_FB56_ShapeV28_GndControl_MinnaertPhase30_PAN_8bit'
elif body['name'] == 'S5_Didymos':
    albedo = 0.15 # TBD
    SUN_energy = 7 # TBD
    BODY = bpy.data.objects["Didymos"]
    BODY_Secondary = bpy.data.objects["Dimorphos"]
    scale_BU = 1
elif body['name'] == 'S5_Didymos_Milani':
    albedo = 0.15 # TBD
    SUN_energy = 7 # TBD
    BODY = bpy.data.objects["Didymos"]
    BODY_Secondary = bpy.data.objects["Dimorphos"]
    scale_BU = 1
elif body['name'] == 'S6_Moon':
    albedo = 0.169 # TBD
    SUN_energy = 30 # TBD
    BODY = bpy.data.objects["Moon"]
    scale_BU = 1e-3
    displacemenet_name = 'ldem_16'
    texture_name = 'lroc_color_poles_32k'

#I/O paths
home_path = bpy.path.abspath("//")
txt_path = os.path.join(home_path, geometry['name'] + '.txt')

# CAM properties
CAM.data.type = 'PERSP'
CAM.data.lens_unit = 'FOV'
CAM.data.angle = scene['fov'] * np.pi / 180
CAM.data.clip_start = 0.1 # [m]
CAM.data.clip_end = 10000 # [m]
bpy.context.scene.render.pixel_aspect_x = 1
bpy.context.scene.render.pixel_aspect_y = 1
bpy.context.scene.render.resolution_x = scene['resx'] # CAM resolution (x)
bpy.context.scene.render.resolution_y = scene['resy'] # CAM resolution (y)
bpy.context.scene.render.image_settings.color_mode = 'BW'
bpy.context.scene.render.image_settings.color_depth = str(scene['encoding'])
if body['name'] == 'S5_Didymos' or body['name'] == 'S5_Didymos_Milani':
    bpy.context.scene.cycles.diffuse_bounces = 0 

# SUN properties
SUN.data.type = 'SUN'
SUN.data.energy = SUN_energy  # To perform quantitative analysis
SUN.data.angle = 0.53*np.pi/180

# BODY properties
BODY.location = [0,0,0]
BODY.rotation_mode = 'XYZ'
BODY.rotation_euler = [0,0,0]
if body['name'] == 'S5_Didymos' or body['name'] == 'S5_Didymos_Milani':
    bpy.context.scene.cycles.diffuse_bounces = 0 
    BODY.pass_index = 1
    BODY_Secondary.pass_index = 2
    BODY_Secondary.location = [1.2,0,0]
    BODY_Secondary.rotation_mode = 'XYZ'
    BODY_Secondary.rotation_euler = [0,0,0]
    if body['name'] == 'S5_Didymos_Milani':
        BODY.scale = [1,1,0.78]
        BODY_Secondary.scale = [0.850, 1.080, 0.840]     
# WORLD properties
bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = (0, 0, 0, 1)

# RENDERING ENGINE properties 
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.device = 'CPU'
bpy.context.scene.cycles.samples = scene['rendSamples']
bpy.context.scene.cycles.preview_samples = scene['viewSamples']

######[3]  EXTRACT DATA FROM TXT [3]######

n_rows = len(open(os.path.join(txt_path)).readlines())
n_col = 15

from_txt = np.zeros((n_rows,n_col))

file = open(os.path.join(txt_path),'r',newline = '')
ii=0
for line in file:
    fields = line.split(" ")
    for jj in range(0,n_col,1):
        from_txt[ii,jj] = float(fields[jj])
    ii = ii+1
    
file.close()

et_SC = from_txt[:,0]
R_pos_SUN = from_txt[:,4:7] # (km) 
R_pos_SC = from_txt[:,8:11]*scale_BU # (km) 
R_q_SC = from_txt[:,11:15] # (-) 

######[4] FUNCTIONS DEFINITIONS [4]######

def PositionAll(ii):
    POS_SC_ii = R_pos_SC[ii,:]
    OR_SC_ii = R_q_SC[ii,:]
    POS_SUN_ii = -R_pos_SUN[ii,:]
    # CAM position
    CAM.location[0] = POS_SC_ii[0]
    CAM.location[1] = POS_SC_ii[1]
    CAM.location[2] = POS_SC_ii[2]
    # CAM orientaion
    CAM.rotation_mode = 'QUATERNION'
    CAM.rotation_quaternion[0] = OR_SC_ii[0]
    CAM.rotation_quaternion[1] = OR_SC_ii[1]
    CAM.rotation_quaternion[2] = OR_SC_ii[2]
    CAM.rotation_quaternion[3] = OR_SC_ii[3]
    # SUN position 
    SunVector = POS_SUN_ii
    direction = mathutils.Vector(SunVector/np.linalg.norm(SunVector))
    rot_quat = direction.to_track_quat('-Z', 'Y')
    SUN.location[0] = POS_SUN_ii[0]
    SUN.location[1] = POS_SUN_ii[1]
    SUN.location[2] = POS_SUN_ii[2]
    SUN.rotation_mode = 'QUATERNION'
    SUN.rotation_quaternion = rot_quat# Camera
    return

def ApplyScattering(SG_name,POS_camera_ii, POS_SUN_ii, function, albedo):
    SG_name.nodes["CAM_X"].outputs[0].default_value = POS_camera_ii[0]
    SG_name.nodes["CAM_Y"].outputs[0].default_value = POS_camera_ii[1]
    SG_name.nodes["CAM_Z"].outputs[0].default_value = POS_camera_ii[2]
    SG_name.nodes["SUN_X"].outputs[0].default_value = POS_SUN_ii[0]
    SG_name.nodes["SUN_Y"].outputs[0].default_value = POS_SUN_ii[1]
    SG_name.nodes["SUN_Z"].outputs[0].default_value = POS_SUN_ii[2]
    SG_name.nodes["P_PHFunction"].outputs[0].default_value = function
    SG_name.nodes["P_Albedo"].outputs[0].default_value = albedo

def Render(ii):
    name = '{}.png'.format(str(int(ii+1)).zfill(6))
    bpy.context.scene.render.filepath = os.path.join(output_img_savepath,name)
    bpy.ops.render.render(write_still = 1)    
    return

def MakeDir(path):
    try:
        os.mkdir(path)
    except OSError:
        print ('Creation of the directory %s failed' % path)
    else:
        print ('Successfully created the directory %s ' % path)

# Set the keyframe
def SetKeyframe(ii):
    bpy.context.scene.frame_current = ii

def SaveDepth(ii):
    """Obtains depth map from Blender render.
    return: The depth map of the rendered camera view as a numpy array of size (H,W).
    """
    z = bpy.data.images['Viewer Node']
    w, h = z.size
    dmap = np.array(z.pixels[:], dtype=np.float16) # convert to numpy array
    dmap = np.reshape(dmap, (h, w, 4))[:,:,0]
    dmap = np.rot90(dmap, k=2)
    dmap = np.fliplr(dmap)
    txtname = '{num:06d}'
    np.savetxt(os.path.join(depth_path, txtname.format(num=(ii+1)) + '.txt'), dmap, delimiter=' ',fmt='%.5f')
    return

def GenerateTimestamp():
    timestamp = datetime.now()
    formatted_timestamp = timestamp.strftime("%Y_%m_%d_%H_%M_%S")
    return formatted_timestamp

### CYCLIC RENDERINGS ###

output_timestamp = GenerateTimestamp()
output_folderName = body['name'] + '_' + output_timestamp

output_savepath = os.path.join(corto['savepath'],output_folderName)
output_img_savepath = os.path.join(output_savepath,'img')
output_label_savepath = os.path.join(output_savepath,'label')

MakeDir(output_savepath)
MakeDir(output_img_savepath)
if scene['labelDepth'] == 1 or scene['labelID'] == 1 or scene['labelSlopes'] == 1:
    MakeDir(output_label_savepath)
    if scene['labelDepth'] == 1:
        MakeDir(os.path.join(output_label_savepath,'depth'))
    if scene['labelID'] == 1:
        MakeDir(os.path.join(output_label_savepath,'IDmask'))
        bpy.data.scenes["Scene"].node_tree.nodes["MaskOutput"].base_path = output_label_savepath
        bpy.data.scenes["Scene"].node_tree.nodes['MaskOutput'].file_slots[0].path="\IDmask\Mask_1\######" 
        bpy.data.scenes["Scene"].node_tree.nodes['MaskOutput'].file_slots[1].path="\IDmask\Mask_1_shadow\######" 
        bpy.data.scenes["Scene"].node_tree.nodes['MaskOutput'].file_slots[2].path="\IDmask\Mask_2\######"
        bpy.data.scenes["Scene"].node_tree.nodes['MaskOutput'].file_slots[3].path="\IDmask\Mask_2_shadow\######"
    if scene['labelSlopes'] == 1:
        MakeDir(os.path.join(output_label_savepath,'slopes'))
        bpy.data.scenes["Scene"].node_tree.nodes["SlopeOutput"].base_path = output_label_savepath
        bpy.data.scenes["Scene"].node_tree.nodes['SlopeOutput'].file_slots[0].path="\slopes\######" 

## Cyclic rendering
SetKeyframe(1)
for ii in range(0, n_rows,1):
    SetKeyframe(ii+1)
    print('---------------Preparing for case: ',ii,'---------------')
    print('Position bodies')
    PositionAll(ii)
    bpy.context.view_layer.update()
    if ii<geometry['ii0']:
        print('--------------Not rendering---------------')
    else:
        bpy.context.view_layer.update()
        print('Apply scattering body')
        #ApplyScattering(bpy.data.node_groups["ScatteringGroup_D1"],R_pos_SC[ii],R_pos_SUN[ii],scene['scattering'],albedo)
        bpy.context.view_layer.update()
        time.sleep(2) # For contingency
        print('--------------Rendering---------------')
        Render(ii)
        if scene['labelDepth'] == 1:
            SaveDepth(ii)
