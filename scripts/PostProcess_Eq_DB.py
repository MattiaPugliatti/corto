import os, sys
import numpy as np
import matplotlib.patches as patche
from matplotlib import pyplot as plt

import warnings
from glob import glob
import cv2


sys.path.append(os.getcwd())
import cortopy as corto


#TODO: Move this functions into the PostProcessing class
def find_body_bbox(image):
    """
    Detects the bounding box of the largest contour (assumed to be the body).
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    _, thresh = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    largest = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest)
    return x, y, w, h

def determine_max_BB(source_BB,target_BB):
    x, y, w, h = source_BB
    # Find the smallest target_bb that fits max(w, h)
    max_size = max(w,h)
    # Filter values that are >= size_needed
    valid_sizes = target_BB[target_BB >= max_size]
    if len(valid_sizes) == 0:
        raise ValueError("No bounding box size can fit the object!")
    # Take the minimum among valid sizes
    selected_size = np.min(valid_sizes) # Save this one
    print(f"Selected bounding box size: {selected_size}")
    return float(selected_size)

def BB_random_padding(source_BB,selected_target_size, img_res, max_selected_target_size):
    # Extract BB coordinates
    x, y, w, h = source_BB
    # Initialize error index to 0
    error_index = 0
    # Compute the horizontal and vertical padding needed to go from a rectangular source_BB to a square target_BB
    delta_all = selected_target_size - np.array([w, h])  # [Δx, Δy]
    # Determine maximum left-right paddings in the horizontal direction
    check_1 = check_2 = 0
    if delta_all[0] >= 0:
        max_delta_1 = min(delta_all[0], x)  # left
        max_delta_2 = min(delta_all[0], img_res[0] - x - w)  # right
        check_1 = 1
    else:
        error_index = 1
    # Determine maximum top-bottomw paddings in the vertical direction
    if delta_all[1] >= 0:
        max_delta_3 = min(delta_all[1], y)  # top
        max_delta_4 = min(delta_all[1], img_res[1] - y - h)  # bottom
        check_2 = 1
    else:
        error_index = 2
    # Initialize the values of the four random padding values
    delta_1 = delta_2 = delta_3 = delta_4 = 0
    check = True
    # Determine coherent values for all delta's
    w_new = selected_target_size
    h_new = selected_target_size
    if selected_target_size == max_selected_target_size:
        x_new, y_new = 1, 1
    else:
        while check:
            if check_1:
                delta_1 = np.random.randint(0, max(max_delta_1, 1))
                delta_2 = delta_all[0] - delta_1
            if check_2:
                delta_3 = np.random.randint(0, max(max_delta_3, 1))
                delta_4 = delta_all[1] - delta_3
            if (delta_1 <= max_delta_1 and delta_2 <= max_delta_2 and
                delta_3 <= max_delta_3 and delta_4 <= max_delta_4):
                check = False
        # Pack all delta's (left, right, top, bottom) of the final bounding box            
        delta_1234 = np.array([int(delta_1), int(delta_2), int(delta_3), int(delta_4)])
        # Generate the new bounding box
        x_new = source_BB[0] - delta_1234[0]
        y_new = source_BB[1] - delta_1234[2]
    new_BB = np.array([int(x_new), int(y_new), int(w_new), int(h_new)])
    # Activate warnings for I's
    if error_index == 1: 
        warnings.warn(f"Width of bounding box ({w}) exceeds selected target size ({selected_target_size}).")
    elif error_index == 2:
        warnings.warn(f"Width of bounding box ({h}) exceeds selected target size ({selected_target_size}).")
    return new_BB, delta_1234, error_index

# Crop function
def crop_image_by_BB(img, BB):
    x, y, w, h = BB
    return img[y:y+h, x:x+w]

# Main script
input_folder = "output/SXX_Double/img"  # Folder with input images
image_paths = glob(os.path.join(input_folder, "*.png"))  # or .jpg, etc.
file_names = [os.path.basename(path) for path in image_paths]

target_BB = np.array([2048, 1024, 512, 256, 128])

for ii in range(0,21):
ii = 10
image = cv2.imread(input_folder + '/' + file_names[ii])
print(ii)
plt.imshow(image)
plt.show()

source_BB = find_body_bbox(image) # Save these 4
# Determine the selected target size
selected_target_size = determine_max_BB(source_BB,target_BB)
# Perform random padding
a,b,c = BB_random_padding(source_BB, selected_target_size, (2048,2048), 2048)
# Crop the image with BB
img_cropped = crop_image_by_BB(image, a)
# Reduce image size to 128x128
img_resized = cv2.resize(img_cropped, (128, 128), interpolation=cv2.INTER_AREA)
# Plot image with bounding boxes
fig, ax = plt.subplots(1)
ax.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
# Draw bounding boxes
for bb, color in zip([source_BB, a], ['red', 'blue']):
    rect = patches.Rectangle((bb[0], bb[1]), bb[2], bb[3], linewidth=2, edgecolor=color, facecolor='none')
    ax.add_patch(rect)
plt.title("Image with Two Bounding Boxes")
plt.axis('off')
plt.show()
