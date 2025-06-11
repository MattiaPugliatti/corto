import os, sys
import numpy as np
import matplotlib.patches as patches
import random 
import math
from matplotlib import pyplot as plt

sys.path.append(os.getcwd())
import cortopy as corto

def uniform_log(min_val, max_val):
    log_min = math.log10(min_val)
    log_max = math.log10(max_val)
    return 10 ** random.uniform(log_min, log_max)

### Set image path ###
mask_folder = "/Users/mapu7335/Repos/equilibrium/Data/Images/Test/mask_ID_1/" # Folder with image masks
img_folder = "/Users/mapu7335/Repos/equilibrium/Data/Images/Test/img/" # Folder with input images
img_names = corto.DataProcessing.find_images(img_folder, "*.png")

# Define output folder for S0 (Artificial Noise)
output_folder_noise = "/Users/mapu7335/Repos/equilibrium/Data/Images/Test/img_S0"
corto.Utils.mkdir(output_folder_noise)

### (PART-1) Add artificial noise ###

noise = {
    # (1) Generic blur
    'sigma_blur': 0.5,
    # (2) Motion blur
    'motion_length': 1.2,
    'motion_theta': 0,
    # (3a) Generic noise (GAUSSIAN)
    'sensor_noise_type': 'gaussian',
    'mean': 0.1,
    'variance': 0.0001,
    # (4) Gamma-correction
    'bright': 1,
    # (5) Dead pixels (disabled)s
    'n_dead_px': 0,
    'dead_px_x': np.random.randint(0, 2048, 5),
    'dead_px_y': np.random.randint(0, 2048, 5),
    # (6) Saturated buckets (disabled)
    'n_sat_buckets': 0,
    # (7) Blooming (disabled)
    'blooms': 0,
    'sigma_blooms': 10,
    'blooms_val': 255,
    # (8) RadiationN (disabled)
    'rad': 0,
    'n_rad_strides': 50,
    'rad_linewidth': 1,
    'L_min_s': 2,
    'L_max_s': 20,
    'I_min_s': 1.0,
    'I_max_s': 1.0
}

N = 10  # or any number you need

img_noise_all = np.zeros((128,128,N))
img_original_all = np.zeros((128,128,N))
for ii in range(0,N):
    # (1) Generic blur
    noise["sigma_blur"] = random.uniform(0.5,2)
    # (2) Motion blur
    noise["motion_length"] = random.uniform(1.2,3)
    noise["motion_theta"] = random.uniform(0,2*np.pi)
    # (3a) Generic noise (GAUSSIAN)
    noise["sensor_noise_type"] =  'gaussian'
    noise["mean"] = uniform_log(1e-3, 0.25)
    noise["variance"] = uniform_log(1e-5, 1e-3)
    # (4) Gamma-correction
    noise["bright"] = random.uniform(0.5,1.5)

    img_path = os.path.join(img_folder,img_names[ii])
    img_input = corto.DataProcessing.imread(img_path)
    img_noise = corto.DataProcessing.add_artificial_noise(img_input[:,:,0], noise)

    img_noise_all[:,:,ii] = img_noise[1024-64:1024+64, 1024-64:1024+64]
    img_original_all[:,:,ii] = img_input[1024-64:1024+64, 1024-64:1024+64,0]

plt.figure()
for ii in range(0,N):
    plt.subplot(2,5,ii +1)
    plt.imshow(img_original_all[:,:,ii], cmap = 'gray', vmin = 0, vmax = 255)
plt.title("Original images")
plt.axis('off')
    
plt.figure()
for ii in range(0,N):
    plt.subplot(2,5,ii +1)
    plt.imshow(img_noise_all[:,:,ii], cmap = 'gray', vmin = 0, vmax = 255)
plt.title("Images with noise")
plt.axis('off')


plt.show()
    