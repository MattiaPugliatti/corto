from __future__ import annotations
from typing import Any, List, Mapping, Optional, Tuple, Union, overload
from pathlib import Path

import warnings
from glob import glob
import cv2
import numpy as np 
from matplotlib import pyplot as plt
import scipy 

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
            img_path (str): path of the image
            label (dict): label dictionary associated to the image
        """

        self.img = self.imread(img_path)
        self.label = label

    @staticmethod
    def find_images(input_folder: str, extension: str = "*.png"):
        """
        Finds and returns a sorted list of relative image paths with the given extension.

        Args:
            input_folder (str): Folder to search for image files.
            extension (str): File extension pattern (e.g., '*.png', '*.jpg').

        Returns:
            List[str]: Sorted relative paths of image files.
        """
        folder = Path(input_folder)
        paths = sorted(folder.glob(extension))  # sort ensures consistent order
        return [str(p.relative_to(folder)) for p in paths]

    @staticmethod
    def imread(path:str):
        """
        Reads an image from a given file path using OpenCV.

        Args:
            path (str): Path to the image file.

        Returns:
            np.ndarray or None: The image as a NumPy array (in BGR format), or None if the file could not be read.

        Raises:
            FileNotFoundError: If the image could not be read from the given path.
        """
        # Read the image
        img_read = cv2.imread(path)
        if img_read is None:
            raise FileNotFoundError(f"Image not found or unreadable at path: {path}")
        return img_read

    @staticmethod
    def imsave(path:str,img:np.ndarray):
        """
        Saves an image to the specified file path using OpenCV.

        Args:
            path (str): Destination file path where the image will be saved.
            img (np.ndarray): Image data as a NumPy array (BGR or grayscale).

        Raises:
            IOError: If the image could not be saved to the specified path.
        """

        # Save the image using OpenCV
        img_saved = cv2.imwrite(path, img)
        # Check for succesfful saving
        if not img_saved:
            raise IOError(f"Failed to save image to {path}")

    @staticmethod
    def tensave_mat(path:str,tens:np.ndarray):
        """
        Saves a 3D tensor to a .mat file.

        Args:
            path (str): Destination file path where the .mat file will be saved.
            tens (np.ndarray): A 3D NumPy array of shape (n, n, M) representing a tensor.

        Raises:
            ValueError: If the input tensor is not 3-dimensional.
        """
        if tens.ndim != 3:
            raise ValueError("Input tensor must be 3D (n x n x M)")
        scipy.io.savemat(path, {'T_img': tens})

    def crop_img_by_BB(img:np.ndarray, BB):
        """
        Crops a region from an image based on the given bounding box.

        Args:
            img (np.ndarray): The input image as a NumPy array.
            BB (tuple or list): Bounding box defined as (x, y, w, h), where:
                x (int): Top-left x-coordinate.
                y (int): Top-left y-coordinate.
                w (int): Width of the bounding box.
                h (int): Height of the bounding box.

        Returns:
            np.ndarray: Cropped image region corresponding to the bounding box.
        """
        x, y, w, h = BB
        return img[y:y+h, x:x+w]
    
    @ staticmethod
    def resize_image(img:np.ndarray,target_res:int, method:str = 'INTER_NEAREST'):
        """
        Resizes an image to a square of target resolution using a specified interpolation method.

        Args:
            img (np.ndarray): Input image as a NumPy array.
            target_res (int): Target resolution for both width and height (e.g., 128 → output is 128x128).
            method (str): Interpolation method to use. Options include:
                - 'INTER_NEAREST'
                - 'INTER_LINEAR'
                - 'INTER_CUBIC'
                - 'INTER_LANCZOS4'
                - 'INTER_AREA'

        Returns:
            np.ndarray: The resized image.

        Raises:
            ValueError: If an unsupported interpolation method is specified.
        """
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
        """
        Displays the image stored in the object using matplotlib.
        
        If a label is available and contains a 'CoM' (center of mass) key,
        it overlays the CoM as a red 'x' on the image.
        """
        plt.figure()
        plt.imshow(self.img)
        if self.label is not None:
            if "CoM" in self.label:
                plt.plot(self.label["CoM"][0],self.label["CoM"][1],'rx')
        plt.show()
    
    def find_body_bbox(self):
        """
        Detects the bounding box of the largest external contour in the image,
        which is assumed to represent the main body.

        Returns:
            np.ndarray or None: Bounding box as a NumPy array [x, y, w, h],
            or None if no contours are found.
        """
        #TODO: improve the robustness of this function, needs to work with multiple blobs and at different values of noise. Maybe have it working on the labels instead
        img = self.img
        # Convert to grayscale if image is in color     
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
        # Apply binary threshold to isolate bright regions
        _, thresh = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
        # Find external contours (outer edges only)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # If no contours are found, return None
        if not contours:
            return None
        # Find the largest contour (assumed to be the body)
        largest = max(contours, key=cv2.contourArea)
        # Get the bounding box [x, y, w, h] of the largest contour
        x, y, w, h = cv2.boundingRect(largest)
        return np.array([x, y, w, h])

    @staticmethod
    def determine_max_BB(source_BB:np.ndarray,target_BB:np.ndarray):
        """
        Determines the smallest bounding box size from a list of candidates that can
        fully contain the given source bounding box.

        Args:
            source_BB (np.ndarray): The original bounding box defined as (x, y, w, h).
            target_BB (np.ndarray): 1D array of candidate bounding box sizes (e.g., [2048, 1024, ...]).

        Returns:
            float: The smallest valid bounding box size that fits the object.

        Raises:
            ValueError: If no candidate size in target_BB is large enough to fit the source bounding box.
        """

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
    def BB_random_padding(source_BB:np.ndarray,selected_target_size:int, img_res:tuple, max_selected_target_size:int):
        """
        Applies random padding to a rectangular bounding box in order to expand it into a square
        bounding box of a specified target size, while ensuring the object remains fully visible
        within the image boundaries.

        Args:
            source_BB (np.ndarray): Original bounding box defined as (x, y, w, h).
            selected_target_size (int): Desired square size of the output bounding box.
            img_res (tuple): Resolution of the image as (width, height).
            max_selected_target_size (int): Maximum allowable target size (used to bypass padding logic).

        Returns:
            new_BB (np.ndarray): New padded bounding box as (x_new, y_new, w_new, h_new).
            delta_1234 (np.ndarray): Padding values as (left, right, top, bottom).
            error_index (int): Error indicator:
                - 0 if no error
                - 1 if width > selected target size
                - 2 if height > selected target size

        Raises:
            UserWarning: If width or height of the bounding box exceeds the selected target size.
        """
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

    def ProceduralRandomPadding(self, target_BB_sizes:np.ndarray, original_img_size:int, final_img_size:int):
        """
        Applies procedural random padding to the original image to create a square bounding box 
        around the detected body, followed by cropping and resizing the image and its labels.

        This function represent a fully functioning DataProcessing pipelinea, performing the following steps:
            1. Detects the bounding box of the body in the original image.
            2. Selects the smallest valid target bounding box size that fits the object.
            3. Applies random padding to center the object within a square region.
            4. Crops the image using the padded bounding box.
            5. Resizes the cropped image to the final target resolution.
            6. Adjusts the CoM (center of mass) label coordinates across all transformations.

        Args:
            target_BB_sizes (np.ndarray): Array of candidate square bounding box sizes (e.g., [2048, 1024, 512, ...]).
            original_img_size (int): Original image resolution (assumed square).
            final_img_size (int): Desired final output image resolution (e.g., 128, 256, etc.).

        Returns:
            img_resized (np.ndarray): Final resized image of shape (final_img_size, final_img_size). This is the image in S2
            img_cropped (np.ndarray): Cropped image corresponding to the padded bounding box. This is the image in S1
            original_BB (np.ndarray): Original bounding box around the detected body. This is BB0
            final_BB (np.ndarray): Bounding box after padding to selected target size. This is BB1
            delta_1234 (np.ndarray): Padding values [left, right, top, bottom] applied to the original BB.
            label_resized (dict): Dictionary containing center of mass coordinates across stages:
                - 'CoM_S0': in original image (S0)
                - 'CoM_S1': in cropped image (S1)
                - 'CoM_S2': in final resized image (S2)
        """

        # Determine the Bounding Box (BB) in the body in the image
        original_BB = self.find_body_bbox() # Call this img_BB
        # Determine the target BB size
        target_BB_size = self.determine_max_BB(original_BB,target_BB_sizes)
        # Perform random padding
        final_BB,delta_1234, error_index = self.BB_random_padding(original_BB, target_BB_size, (original_img_size,original_img_size), original_img_size)
        # Crop the image with BB
        img_cropped = DataProcessing.crop_img_by_BB(self.img,final_BB)
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
                'CoM_S0': (CoM_u_S0,CoM_v_S0), 
                'CoM_S1': (CoM_u_S1,CoM_v_S1), 
                'CoM_S2': (CoM_u_S2,CoM_v_S2), 
            }
        return img_resized, img_cropped, original_BB, final_BB, delta_1234, label_resized