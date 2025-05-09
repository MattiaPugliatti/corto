from __future__ import annotations
from typing import Any, List, Mapping, Optional, Tuple, Union, overload

import warnings
from glob import glob
import cv2
import numpy as np 
from matplotlib import pyplot as plt

class DataProcessing:
    """
    Data-Processing class
    """
    # *************************************************************************
    # *     Constructors & Destructors
    # *************************************************************************

    def __init__(self, img_path: str, label) -> None:
        """
        Constructor for the Data Processing class

        Args:
            name (str): name of the CAM object
            properties (dict): properties of the CAM object

        Raises:
            TypeError : resolution of the camera must be expressed with integer values
        """

        self.img = self.imread(img_path)
        self.label = label
    # Istance methods

    @staticmethod
    def imread(path):
        return cv2.imread(path)

    def crop_image_by_BB(img, BB):
        x, y, w, h = BB
        return img[y:y+h, x:x+w]
    
    @ staticmethod
    def resize_image(img,target_res, method:str = 'INTER_NEAREST'):
        if method == 'INTER_NEAREST':
            interp_method = cv2.INTER_NEAREST
        elif method == 'INTER_LINEAR':
            interp_method = cv2.INTER_LINEAR
        elif method == 'INTER_CUBIC':
            interp_method = cv2.INTER_CUBIC
        elif method == 'INTER_LANCZOS4':
            interp_method = cv2.INTER_LANCZOS4
        elif method == 'INTER_AREA':
            interp_method = cv2.INTER_AREA
        else:
            raise ValueError(f"Unknown interpolation method: {method}")
        
        img_resized = cv2.resize(img, (target_res, target_res), interpolation=interp_method)
        return img_resized

    def imshow(self):
        plt.imshow(self.img)
        plt.show()
    
    def find_body_bbox(self):
        """
        Detects the bounding box of the largest contour (assumed to be the body).
        """
        img = self.img

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
        _, thresh = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None
        largest = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest)
        return np.array([x, y, w, h])

    @staticmethod
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

    @staticmethod
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
        delta_1234 = np.zeros((1,4))
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

    def ProceduralRandomPadding(self, target_BB_sizes, original_img_size, final_img_size):

        ### ProceduralRandomPadding and resizing of the image
        # Determine the Bounding Box (BB) in the body in the image
        original_BB = self.find_body_bbox() # Call this img_BB
        # Determine the target BB size
        target_BB_size = self.determine_max_BB(original_BB,target_BB_sizes)
        # Perform random padding
        final_BB,delta_1234, error_index = self.BB_random_padding(original_BB, target_BB_size, (original_img_size,original_img_size), original_img_size)
        # Crop the image with BB
        img_cropped = DataProcessing.crop_image_by_BB(self.img,final_BB)
        # Reduce the image to final resolution 
        img_resized = self.resize_image(img_cropped,final_img_size,'INTER_AREA')

        ### ProceduralRandomPadding and resizing of the label        
        if "CoM" in self.label:
            CoM_u_S0, CoM_v_S0 = self.label["CoM"]
            # Compute CoM in S1 
            CoM_u_S1 = CoM_u_S0 - final_BB[0]
            CoM_v_S1 = CoM_v_S0 - final_BB[1]
            # Compute CoM in S2
            CoM_u_S2 = CoM_u_S1 * (final_img_size / target_BB_size)
            CoM_v_S2 = CoM_v_S1 * (final_img_size / target_BB_size)

            label_resized = {
                'CoM': (CoM_u_S0,CoM_v_S0), 
                'CoM_S1': (CoM_u_S1,CoM_v_S1), 
                'CoM_S2': (CoM_u_S2,CoM_v_S2), 
            }
        return img_resized, img_cropped, original_BB, final_BB, delta_1234, label_resized