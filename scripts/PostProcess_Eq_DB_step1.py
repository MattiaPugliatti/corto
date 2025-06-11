import os, sys
import numpy as np
import math
import random

sys.path.append(os.getcwd())
import cortopy as corto

'''
PostProcessing script (PART-1) that adds artificial noise to the images in 'img_folder'
'''
### Set image path ###
img_folder = "/Users/mapu7335/Repos/equilibrium/Data/Images/Test/img/" # Folder with input images
img_names = corto.DataProcessing.find_images(img_folder, "*.png")
N = len(img_names)  # or any number you need

# Define output folder for S0 (Artificial Noise)
output_folder_noise = "/Users/mapu7335/Repos/equilibrium/Data/Images/Test/img_S0"
corto.Utils.mkdir(output_folder_noise)

def uniform_log(min_val, max_val):
    log_min = math.log10(min_val)
    log_max = math.log10(max_val)
    return 10 ** random.uniform(log_min, log_max)

noise = {
    # (1) Generic blur
    'sigma_blur': 0.5, # Placeholder, changed dynamically 
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

for ii in range(0,N):
    # Change noise settings dynamically
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
    corto.DataProcessing.imsave(os.path.join(output_folder_noise,img_names[ii]), img_noise)