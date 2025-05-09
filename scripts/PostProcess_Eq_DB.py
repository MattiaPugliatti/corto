import os, sys
import numpy as np
import matplotlib.patches as patches
from matplotlib import pyplot as plt

import warnings
from glob import glob
import cv2

sys.path.append(os.getcwd())
import cortopy as corto

# TODO: add label change for the CoM after ProceduralRandomPadding

### Set image path ###
input_folder = "output/SXX_Double/img"  # Folder with input images
image_paths = glob(os.path.join(input_folder, "*.png"))  # or .jpg, etc.
file_names = [os.path.basename(path) for path in image_paths]

### (PART-1) Add artificial noise ###

# output_path_noise = "output/SXX_Double/img_noise"
# noise_settings = ...
# corto.DataProcessing.add_artificial(input_path, output_path_noise, noise_settings)

### (PART-2) Adaptive resizing ###

# Define target bounding boxes for the cropped-version of the images
target_BB_sizes = np.array([2048, 1024, 512, 256, 128])
target_img_size = 128
img_size = (2048,2048)
label = {
    'CoM': (1024,1024)
}

ii = 20 # Just analyze one image
# CRASH ON 5 and 20 (10% of the cases, multiple blobs)

# Initialize a DataProcessing object (defined by an img-label pair)

img_path = input_folder + '/' + file_names[ii]
data = corto.DataProcessing(img_path = img_path, label = label )

# data.imshow()

original_img_size = 2048
final_img_size = 128

img_resized, img_cropped, original_BB, final_BB, delta_1234,label_resized  = data.ProceduralRandomPadding(target_BB_sizes, original_img_size, final_img_size)

CoM_S0 = label_resized["CoM"]
CoM_S2 = label_resized["CoM_S2"]

# Plots

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

plt.show()
