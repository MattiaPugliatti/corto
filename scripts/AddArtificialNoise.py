import os, sys
import numpy as np
import matplotlib.patches as patches
from matplotlib import pyplot as plt

import warnings
from glob import glob
import cv2

sys.path.append(os.getcwd())
import cortopy as corto


### Set image path ###
img_folder = "output/SXX_Double/img"  # Folder with input images
img_names = corto.DataProcessing.find_images(img_folder, "*.png")

### (PART-1) Add artificial noise ###

# Define output folder for N (Artificial Noise)
output_folder_noise = "output/SXX_Double/img_S0"

ii = 7 
img_path = os.path.join(img_folder,img_names[ii])

img = corto.DataProcessing.imread(img_path)

# Example noise dictionary
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
    # (3b) Generic noise (POISSON)
    # 'sensor_noise_type': 'poisson',
    # # (3c) Generic noise (SPECKLE)
    # 'sensor_noise_type': 'speckle',
    # 'variance': 1e-7,
    # # (3d) Generic noise (SPECKLE)
    # 'sensor_noise_type': 'salt_pepper',
    # 'ratio': 0.5,
    # 'amount': 0.1,
    # (4) Gamma-correction
    'bright': 1,
    # (5) Dead pixels
    'n_dead_px': 5,
    'dead_px_x': np.random.randint(0, 2048, 5),
    'dead_px_y': np.random.randint(0, 2048, 5),
    # (6) Saturated buckets
    'n_sat_buckets': 2,
    # (7) Blooming
    'blooms': 1,
    'sigma_blooms': 10,
    'blooms_val': 255,
    # (8) Radiation
    'rad': 1,
    'n_rad_strides': 50,
    'rad_linewidth': 1,
    'L_min_s': 2,
    'L_max_s': 20,
    'I_min_s': 1.0,
    'I_max_s': 1.0
}

img_noise,img_intermediate = corto.DataProcessing.add_artificial_noise(img[:,:,0], noise, True)

plt.figure()
plt.subplot(1,2,1)
plt.imshow(img[:,:,0], cmap='gray')
plt.subplot(1,2,2)
plt.imshow(img_noise, cmap='gray')

# ---- Plot intermediates ----
titles = [
    "1. Gaussian Blur", "2. Motion Blur", "3. Sensor Noise", "4. Gamma Correction",
    "5. Dead Pixels", "6. Sat Buckets", "7. Blooming", "8. Radiation"
]
keys = [
    'img_1_blur', 'img_2_motion_blur', 'img_3_sensor_noise',
    'img_4_gamma', 'img_5_dead_pixels', 'img_6_sat_buckets',
    'img_7_blooming', 'img_8_radiation'
]

fig, axes = plt.subplots(2, 4, figsize=(16, 8), sharex=True, sharey=True)
axes = axes.flatten()

for idx, (title, key) in enumerate(zip(titles, keys)):
    axes[idx].imshow(img_intermediate[key], cmap='gray', vmin=0, vmax=255)
    axes[idx].set_title(title)
    axes[idx].axis('off')

plt.tight_layout()
plt.show()

print('End DEMO')