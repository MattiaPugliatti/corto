import os, sys
import numpy as np
import matplotlib.patches as patches
import cv2
from matplotlib import pyplot as plt

sys.path.append(os.getcwd())
import cortopy as corto
import scipy

'''
PostProcessing script (PART-2) that performs randomized paddin to the images in 'img_folder'
'''

### Set image path ###
data_folder = "/Users/mapu7335/Repos/equilibrium/Data/Images/PipelineTest"
# data_folder = "/Users/mapu7335/Repos/equilibrium/Data/Images/R1_2025_06_11_11_09_08"
# data_folder = "/Users/mapu7335/Repos/equilibrium/Data/Images/R2_2025_06_11_11_09_17"
# data_folder = "/Users/mapu7335/Repos/equilibrium/Data/Images/R3_2025_06_11_11_09_24"
# data_folder = "/Users/mapu7335/Repos/equilibrium/Data/Images/R4_2025_06_11_11_09_31"

mask_folder = os.path.join(data_folder, "mask_ID_1") # Folder with image masks
img_folder = os.path.join(data_folder, "img") # Folder with input images
img_noise_folder = os.path.join(data_folder, "img_S0") # Folder with noisy images

img_names = corto.DataProcessing.find_images(img_folder, "*.png")
N = len(img_names)  # or any number you need

# Define output folder for S2 (cropped + resize)
output_folder_S2 = os.path.join(data_folder, "img_S2") 
corto.Utils.mkdir(output_folder_S2)

# Define the input folder for S2 (to compute BB)
# input_folder_S2 = img_noise_folder # Take as input for the random padding the images with noise
# input_folder_S2 = img_folder # Take as input for the random padding the images withouth noise
input_folder_S2 = mask_folder # Take as input for the random padding the masks of the images
#NOTE: the cropped and resized images always come from the img_noise_folder

# Define settings for random padding + resize
target_img_size_S1 = np.array([2048, 1024, 512, 256, 128]) # Size (square) of the target BBs (or image size in S1)
img_size_S0 = 2048 # Size (square) of the initial image in S0
img_size_S2 = 128 # Size (square) of the final image in S2
label_S0 = {'CoM': (1024,1024)} # Labels of interest for the images in S0

img_tensor = np.zeros((N, 128, 128), dtype=np.uint8)
label_CoM = np.zeros((N, 2), dtype=np.float32) # The CoM coordinate
label_originalBB = np.zeros((N, 4), dtype=np.float32) # The coordinates of the original BB (the one in S0)
label_finalBB = np.zeros((N, 4), dtype=np.float32) # The coordinates of the final BB (the one in S2)
label_delta1234 = np.zeros((N, 4), dtype=np.float32) # The randomized padding around the original BB
for ii in range(0,N):
    img_path = os.path.join(input_folder_S2,img_names[ii]) # The one to consider for the BB computation
    img_output_path = os.path.join(img_noise_folder,img_names[ii]) # The on on which to compute the random padding
    # Initialize the DataProcessing object
    data = corto.DataProcessing(img_path = img_path, label = label_S0 )    
    # Perform the ProceduralRandomPadding processing on the data-label pairs
    _, _, original_BB, final_BB, delta_1234,label_S2  = data.ProceduralRandomPadding(target_img_size_S1, img_size_S0, img_size_S2)
    # Crop the image with BB
    img_out_S0 = cv2.imread(img_output_path)
    img_cropped = corto.DataProcessing.crop_img_by_BB_float(img_out_S0[:,:,0],final_BB)
    # Reduce the image to final resolution 
    img_resized = corto.DataProcessing.resize_image(img_cropped,img_size_S2,'INTER_AREA')
    corto.DataProcessing.imsave(os.path.join(output_folder_S2,img_names[ii]),img_resized)
    # Package the images
    img_tensor[ii,:,:] = img_resized
    # Package the labels
    label_CoM[ii,:] = label_S2["CoM_S2"]
    label_originalBB[ii,:] = original_BB
    label_finalBB[ii,:] = final_BB
    label_delta1234[ii,:] = delta_1234

corto.DataProcessing.tensave_mat(os.path.join(data_folder,'T_data.mat'),img_tensor)
# corto.DataProcessing.matsave_mat(os.path.join(output_folder_S2,'L_data.mat'),label_CoM,label_originalBB,label_finalBB,label_delta1234)
scipy.io.savemat(os.path.join(data_folder,'L_data.mat'), {'T_lbl': label_CoM,'originalBB':label_originalBB,'finalBB':label_finalBB,'delta1234':label_delta1234})

### Plots

# All labels
# 1 Image
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

plt.show()