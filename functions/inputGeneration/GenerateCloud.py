import numpy as np
import matplotlib.pyplot as plt

from numpy.random import rand
from datetime import datetime
from scipy.spatial.transform import Rotation as R

######[1]  (START) INPUT SECTION (START) [1]######

nPoints = 5000 # [-]
R_min = 10 # [BU]
R_max = 40 # [BU]
theta_min = 0 # [deg]
theta_max = 180 # [deg]
phi_min = -30 # [deg]
phi_max = 30 # [deg]

######[1]  (END) INPUT SECTION (END) [1]######

# Define functions
def GenerateRandP(min,max,nPoints):
  '''
  This function generates nPoints random points uniformly distributed between 
  min and max

  # Arguments
      min: scalar, min value.
      max: scalar, max value.
      nPoints: scalar, number of points to generate.
  '''
  v_norm = rand(nPoints)
  v_rand = min + (v_norm * (max - min))
  return v_rand

def sph2cart(az, el, r):
    '''
    This function converts from spherical to cartesian coordinates

    # Arguments
        az: scalar, azimuth value. [rad]
        el: scalar, elevation value. [rad]
        r: scalar, range value. [-]
    '''
    rcos_theta = r * np.cos(el)
    x = rcos_theta * np.cos(az)
    y = rcos_theta * np.sin(az)
    z = r * np.sin(el)
    return x, y, z

def GenerateQSC_origin(camera_position):
    '''
    This function return a pointing quaternion to be used in Blender,
    given a camera position and assuming target to be positioned in the origin

    # Arguments
        camera_position: Numpy-array of length 3. Camera position.
    '''
    target_position = np.array([0,0,0])
    # compute camera-boresight
    camera_direction = camera_position - target_position
    camera_direction = camera_direction / np.linalg.norm(camera_direction)
    # compute camera-right
    camera_right = np.cross(np.array([0.0, 0.0, 1.0]), camera_direction)
    camera_right = camera_right / np.linalg.norm(camera_right)
    # compute camera-up
    camera_up = np.cross(camera_direction, camera_right)
    camera_up = camera_up / np.linalg.norm(camera_up)
    # Generate the quaternion for Blender [w,xyz]
    r_cam = R.from_matrix(np.transpose([camera_right,camera_up,camera_direction]))
    r_cam = r_cam.as_quat()
    r_blender = [r_cam[3],r_cam[0],r_cam[1],r_cam[2]]
    return r_blender

def GenerateTimestamp():
    '''
    This function generates a univoque timestamp for saving purposes
    '''
    timestamp = datetime.now()
    formatted_timestamp = timestamp.strftime("%Y_%m_%d_%H_%M_%S")
    return formatted_timestamp

# Generate random distribution of camera positions in polar coordinates
R_dist = GenerateRandP(R_min,R_max,nPoints) # [BU]
theta_dist = GenerateRandP(theta_min,theta_max,nPoints) # [deg]
phi_dist = GenerateRandP(phi_min,phi_max,nPoints) # [deg]
# Transform from polar to cartesian coordinates
[x_Cam_dist,y_Cam_dist,z_Cam_dist] = sph2cart(theta_dist*np.pi/180,phi_dist*np.pi/180,R_dist) # [BU]
# Generate camera orientations according to camera positions
q_Cam_dist = np.zeros((nPoints,4)) # [-]
for ii in range (0,nPoints,1):
  q_Cam_dist[ii,:] = GenerateQSC_origin(np.array([x_Cam_dist[ii],y_Cam_dist[ii],z_Cam_dist[ii]]))
# Generate Body poses 
x_Body_dist = np.zeros((nPoints,1)) # [BU]
y_Body_dist = np.zeros((nPoints,1)) # [BU]
z_Body_dist = np.zeros((nPoints,1)) # [BU]
rot_Body_x_dist = np.zeros((nPoints,1)) # [deg]
rot_Body_y_dist = np.zeros((nPoints,1)) # [deg]
rot_Body_z_dist = GenerateRandP(0,360,nPoints) # [deg]
q_Body_dist = np.zeros((nPoints,4)) # [-]
for ii in range (0,nPoints,1):
  r = R.from_euler('xyz',[rot_Body_x_dist[ii],rot_Body_y_dist[ii],rot_Body_z_dist[ii]],degrees=True)
  q = r.as_quat()
  q_Body_dist[ii,:] = [q[3],q[0],q[1],q[2]]
# Generate Sun's positions (Assumed on Y-axis in this example)
x_Sun_dist = np.zeros((nPoints,1)) # [BU]
y_Sun_dist = np.ones((nPoints,1))*R_max*1e3 # [BU]
z_Sun_dist = np.zeros((nPoints,1)) # [BU]
# Generate output timestamp
output_timestamp = GenerateTimestamp()

# Display camera positions
plt.figure()
ax = plt.axes(projection='3d')
ax.scatter(x_Cam_dist,y_Cam_dist,z_Cam_dist, c=theta_dist, cmap='viridis', linewidth=0.1);
plt.axis('equal')
plt.xlabel('X axis [BU]')
plt.ylabel('Y axis [BU]')

# Generate LABEL matrix for export as .txt
LABEL = np.zeros((nPoints,18))
for ii in range(0,nPoints,1):
  # [0] ID or ET
  LABEL[ii,0] = ii
  # [1,2,3] Body pos [BU] and [4,5,6,7] orientation [-]
  LABEL[ii,1] = x_Body_dist[ii]
  LABEL[ii,2] = y_Body_dist[ii]
  LABEL[ii,3] = z_Body_dist[ii] 
  LABEL[ii,4] = q_Body_dist[ii,0]
  LABEL[ii,5] = q_Body_dist[ii,1]
  LABEL[ii,6] = q_Body_dist[ii,2] 
  LABEL[ii,7] = q_Body_dist[ii,3] 
  # [8,9,10] Camera pos [BU] and [11,12,13,14] orientation [-]
  LABEL[ii,8] = x_Cam_dist[ii]
  LABEL[ii,9] = y_Cam_dist[ii]
  LABEL[ii,10] = z_Cam_dist[ii] 
  LABEL[ii,11] = q_Cam_dist[ii,0]
  LABEL[ii,12] = q_Cam_dist[ii,1]
  LABEL[ii,13] = q_Cam_dist[ii,2] 
  LABEL[ii,14] = q_Cam_dist[ii,3] 
  # [15,16,17] Sun pos [BU]
  LABEL[ii,15] = x_Sun_dist[ii]
  LABEL[ii,16] = y_Sun_dist[ii]
  LABEL[ii,17] = z_Sun_dist[ii] 

# Export the LABEL matrix for rendering in CORTO
np.savetxt(output_timestamp + '.txt', LABEL)