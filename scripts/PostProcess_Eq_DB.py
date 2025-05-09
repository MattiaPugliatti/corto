import os, sys
import numpy as np
import matplotlib.patches as patches
from matplotlib import pyplot as plt

import warnings
from glob import glob
import cv2

sys.path.append(os.getcwd())
import cortopy as corto

# TODO: Path handling via database class

### Set image path ###
input_folder = "output/SXX_Double/img"  # Folder with input images

image_paths = glob(os.path.join(input_folder, "*.png"))  # or .jpg, etc.
file_names = [os.path.basename(path) for path in image_paths]

### (PART-1) Add artificial noise ###

# Define output folder for N (Artificial Noise)
output_folder_noise = "output/SXX_Double/img_S0"

# noise_settings = ...
# corto.DataProcessing.add_artificial(input_path, output_path_noise, noise_settings)

### (PART-2) Adaptive resizing ###

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
ii = 20 # Just analyze one image [# CRASH ON 5 and 20 (10% of the cases, multiple blobs)]

img_path = input_folder + '/' + file_names[ii]

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
