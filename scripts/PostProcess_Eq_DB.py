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
corto.Utils.mkdir(output_folder_noise)

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

ii = 3
img_path = os.path.join(img_folder,img_names[ii])

img_input = corto.DataProcessing.imread(img_path)
img_noise = corto.DataProcessing.add_artificial_noise(img_input[:,:,0], noise)
corto.DataProcessing.imsave(os.path.join(output_folder_noise,img_names[ii]), img_noise)

### (PART-2) Adaptive resizing ###

input_folder_S2 = output_folder_noise
# Define output folder for S2 (cropped + resize)
output_folder_S2 = "output/SXX_Double/img_S2"

# Define settings for random padding + resize

# Size (square) of the target BBs (or image size in S1)
target_img_size_S1 = np.array([2048, 1024, 512, 256, 128])
# Size (square) of the final image in S2
img_size_S2 = 128
# Size (square) of the initial image in S0
img_size_S0 = 2048
# Labels of interest for the images in S0
label_S0 = {
    'CoM': (1024,1024)
}

# TODO: loop through images here
# TODO: [# CRASH ON 5 and 20 (10% of the cases, multiple blobs)]
# TODO: crashes with noise! 
img_path = os.path.join(input_folder_S2,img_names[ii])
# Initialize the DataProcessing object
data = corto.DataProcessing(img_path = img_path, label = label_S0 )
# data.imshow() # Visualize the img

# Perform the ProceduralRandomPadding processing on the data-label pairs
img_resized, img_cropped, original_BB, final_BB, delta_1234,label_S2  = data.ProceduralRandomPadding(target_img_size_S1, img_size_S0, img_size_S2)

### Plots

CoM_S0 = label_S2["CoM_S0"]
CoM_S2 = label_S2["CoM_S2"]

fig, ax = plt.subplots(1)
ax.imshow(cv2.cvtColor(data.img, cv2.COLOR_BGR2RGB))
plt.plot(CoM_S0[0],CoM_S0[1],'rx')
# Draw bounding boxes
for bb, color in zip([original_BB, final_BB], ['red', 'blue']):
    rect = patches.Rectangle((bb[0], bb[1]), bb[2], bb[3], linewidth=2, edgecolor=color, facecolor='none')
    ax.add_patch(rect)
plt.title("Image with Two Bounding Boxes")
plt.axis('off')

plt.figure()
plt.imshow(img_resized)
plt.plot(CoM_S2[0],CoM_S2[1],'rx')

# corto.DataProcessing.imsave(,img_resized)
# corto.DataProcessing.tensave_mat(,img_resized_tens)

plt.show()