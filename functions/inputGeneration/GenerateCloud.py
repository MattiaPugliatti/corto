import numpy as np
import matplotlib.pyplot as plt

from numpy.random import rand
from datetime import datetime

# This script generate a cloud of camera positions (defined by R,theta, phi exursions), pointing toward the target body

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
  v_norm = rand(nPoints)
  v_rand = min + (v_norm * (max - min))
  return v_rand

def sph2cart(az, el, r):
    rcos_theta = r * np.cos(el)
    x = rcos_theta * np.cos(az)
    y = rcos_theta * np.sin(az)
    z = r * np.sin(el)
    return x, y, z

def GenerateTimestamp():
    timestamp = datetime.now()
    formatted_timestamp = timestamp.strftime("%Y_%m_%d_%H_%M_%S")
    return formatted_timestamp

# Generate random distribution of camera positions in polar coordinates
R_dist = GenerateRandP(R_min,R_max,nPoints) # [BU]
theta_dist = GenerateRandP(theta_min,theta_max,nPoints) # [deg]
phi_dist = GenerateRandP(phi_min,phi_max,nPoints) # [deg]
# Transform from polar to cartesian coordinates
[x_dist,y_dist,z_dist] = sph2cart(theta_dist*np.pi/180,phi_dist*np.pi/180,R_dist) # [BU]
# Generate pointing quaternions 
# WIP
# Generate Sun's positions (Assumed on Y-axis in this example)
x_Sun_dist = np.zeros((nPoints,1)) # [BU]
y_Sun_dist = np.ones((nPoints,1))*R_max*1e3 # [BU]
z_Sun_dist = np.zeros((nPoints,1)) # [BU]
# Generate output timestamp
output_timestamp = GenerateTimestamp()

# Display camera positions
plt.figure()
ax = plt.axes(projection='3d')
ax.scatter(x_dist,y_dist,z_dist, c=theta_dist, cmap='viridis', linewidth=0.1);
plt.axis('equal')
plt.xlabel('X axis [BU]')
plt.ylabel('Y axis [BU]')

# Generate LABEL matrix for export as .txt
LABEL = np.zeros((nPoints,15))
for ii in range(0,nPoints,1):
  # [0] ID or ET
  LABEL[ii,0] = ii
  # [4,5,6] Sun pos [BU]
  LABEL[ii,4] = x_Sun_dist[ii]
  LABEL[ii,5] = y_Sun_dist[ii]
  LABEL[ii,6] = z_Sun_dist[ii] 
  # [8,9,10] Camera pos [BU]
  LABEL[ii,8] = x_dist[ii] 
  LABEL[ii,9] = y_dist[ii]
  LABEL[ii,10] = z_dist[ii] 
  # [11,12,13,14] Camera orientation [-]
  LABEL[ii,11] = 0 
  LABEL[ii,12] = 0
  LABEL[ii,13] = 0 
  LABEL[ii,14] = 0 
# Export the LABEL matrix for rendering in CORTO
np.savetxt(output_timestamp + '.txt', LABEL)

#WIP: add BODY pose and change indexing accordingly