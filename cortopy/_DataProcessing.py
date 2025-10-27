from __future__ import annotations
from typing import Any, List, Mapping, Optional, Tuple, Union, overload
from pathlib import Path

import warnings
from glob import glob
import cv2
import numpy as np 
from matplotlib import pyplot as plt
import scipy 
from skimage import exposure

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
        self.img = cv2.cvtColor(self.img, cv2.COLOR_RGB2GRAY)#TODO: remove this, just hotfix for non-grayscale images

        if len(self.img.shape) != 2:
            raise ValueError("Only grayscale images are currently supported in the DataProcessing pipeline. RGB images are not allowed.")        
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

    @staticmethod
    def matsave_mat(path:str,tens:np.ndarray):
        """
        Saves a 2D matrix to a .mat file.

        Args:
            path (str): Destination file path where the .mat file will be saved.
            tens (np.ndarray): A 2D NumPy array of shape (n, n, M) representing a tensor.

        Raises:
            ValueError: If the input tensor is not 3-dimensional.
        """
        if tens.ndim != 2:
            raise ValueError("Input tensor must be 3D (n x n x M)")
        scipy.io.savemat(path, {'T_lbl': tens})

    def crop_img_by_BB_int(img:np.ndarray, BB):
        """
        Crops a region from an image based on the given bounding box.
        NOTE: The bounding box has to be defined with integer values.

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
    
    def crop_img_by_BB_float(img: np.ndarray, BB):
        """
        Crops a region from an image based on a float-defined bounding box,
        using subpixel precision.
        NOTE: The bounding box has to be defined with float values.

        Args:
            img (np.ndarray): The input image as a NumPy array.
            BB (tuple or list): Bounding box defined as (x, y, w, h), where:
                x (float): Top-left x-coordinate.
                y (float): Top-left y-coordinate.
                w (float): Width of the bounding box.
                h (float): Height of the bounding box.

        Returns:
            np.ndarray: Cropped image region corresponding to the bounding box
                        using float precision.
        """
        x, y, w, h = BB

        # Compute center of bounding box
        center = (x + w / 2.0, y + h / 2.0)
        size = (int(round(w)), int(round(h)))  # Output size must be integers

        # Use cv2.getRectSubPix for subpixel-accurate cropping
        cropped = cv2.getRectSubPix(img, patchSize=size, center=center)
        return cropped

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
        img = self.img
        # Convert to grayscale if image is in color     
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img # Remove this once the image is assumed to be grayscale only
        # Apply binary threshold to isolate bright regions
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
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
    
    def find_body_bbox_noise(self, min_area_frac=0.0003, pad=4):
        """
        Robustly detect the bounding box of the largest blob in a noisy image.

        Args:
            img (np.ndarray): grayscale or BGR image.
            min_area_frac (float): minimum blob area as a fraction of image area to accept.
            pad (int): pixels to pad around the bbox (clamped to image bounds).

        Returns:
            np.ndarray | None: [x, y, w, h] or None if nothing usable is found.
        """
        def _ensure_odd(n, lo=3):
            n = int(max(lo, n))
            return n if n % 2 == 1 else n + 1

        img = self.img
        # 0) Grayscale
        g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img.copy()
        H, W = g.shape[:2]
        min_area_px = max(1, int(min_area_frac * H * W))

        # 1) Contrast + denoise
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        g = clahe.apply(g)
        k = _ensure_odd(int(min(H, W) * 0.01))       # ~1% of min dim, odd, >=3
        g = cv2.medianBlur(g, k)

        # Helper: build bbox from a single-component label in `labels`
        def bbox_for_label(stats, label):
            x = int(stats[label, cv2.CC_STAT_LEFT])
            y = int(stats[label, cv2.CC_STAT_TOP])
            w = int(stats[label, cv2.CC_STAT_WIDTH])
            h = int(stats[label, cv2.CC_STAT_HEIGHT])
            return x, y, w, h

        # Try both polarities; keep the one with bigger final component
        best = (None, 0)  # (bbox, area)
        for bright_foreground in (True, False):
            gg = g if bright_foreground else 255 - g

            # 2a) Tight core: very bright pixels (seed)
            p = np.percentile(gg, 99)  # core threshold
            tight = (gg >= p).astype(np.uint8) * 255
            # remove tiny specks
            ks = _ensure_odd(int(min(H, W) * 0.008))  # ~0.8% size
            ker = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (ks, ks))
            tight = cv2.morphologyEx(tight, cv2.MORPH_OPEN, ker)

            num_t, labels_t, stats_t, centroids_t = cv2.connectedComponentsWithStats(tight, connectivity=8)
            if num_t <= 1:
                continue  # no seed found in this polarity

            # take largest seed
            areas_t = stats_t[1:, cv2.CC_STAT_AREA]
            seed_label_rel = int(np.argmax(areas_t))  # 0-based among foreground only
            seed_label = seed_label_rel + 1
            if areas_t[seed_label_rel] < 5:
                continue
            cx, cy = centroids_t[seed_label]

            # 2b) Loose mask: Otsu (or adaptive) so we include dimmer parts but not background
            thr, _ = cv2.threshold(gg, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            loose = (gg >= max(10, thr)).astype(np.uint8) * 255
            # clean & connect
            loose = cv2.morphologyEx(loose, cv2.MORPH_OPEN, ker)
            loose = cv2.morphologyEx(loose, cv2.MORPH_CLOSE, ker)

            # 3) Keep only the connected component in `loose` that contains the seed point
            num_l, labels_l, stats_l, _ = cv2.connectedComponentsWithStats(loose, connectivity=8)
            if num_l <= 1:
                continue

            sx, sy = int(round(cx)), int(round(cy))
            sx = np.clip(sx, 0, W - 1); sy = np.clip(sy, 0, H - 1)
            seed_comp = int(labels_l[sy, sx])
            if seed_comp == 0:
                # seed not inside loose foreground; skip this polarity
                continue

            area = int(stats_l[seed_comp, cv2.CC_STAT_AREA])
            if area < min_area_px:
                continue

            x, y, w, h = bbox_for_label(stats_l, seed_comp)

            # Optional padding
            x = max(0, x - pad); y = max(0, y - pad)
            w = min(W - x, w + 2 * pad); h = min(H - y, h + 2 * pad)
            if area > best[1]:
                best = (np.array([x, y, w, h]), area)

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
        return float(selected_size)

    @staticmethod
    def BB_random_padding(source_BB:np.ndarray,selected_target_size:int, img_res:tuple, max_selected_target_size:int, equal_flag = False):
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
                    # delta_1 = np.random.randint(0, max(max_delta_1, 1))
                    if max_delta_1 == 0:
                        delta_1 = 0 
                        delta_2 = 0
                    else:
                        delta_1 = np.random.uniform(0, max(max_delta_1, 1))
                        if equal_flag:
                            delta_1 = max_delta_1/2, # hard-coded fix for the equal-cropped case
                        else:
                            delta_1 = np.random.uniform(0, max(max_delta_1, 1))
                        delta_2 = delta_all[0] - delta_1
                if check_2:
                    # delta_3 = np.random.randint(0, max(max_delta_3, 1))
                    if max_delta_3 == 0:
                        delta_3 = 0 
                        delta_4 = 0
                    else:
                        if equal_flag:
                            delta_3 = max_delta_3/2  # hard-coded fix for the equal-cropped case
                        else:
                            delta_3 = np.random.uniform(0, max(max_delta_3, 1))
                        delta_4 = delta_all[1] - delta_3
                if (delta_1 <= max_delta_1 and delta_2 <= max_delta_2 and
                    delta_3 <= max_delta_3 and delta_4 <= max_delta_4):
                    check = False
            # Pack all delta's (left, right, top, bottom) of the final bounding box            
            # delta_1234 = np.array([int(delta_1), int(delta_2), int(delta_3), int(delta_4)])
            delta_1234 = np.array([delta_1, delta_2, delta_3, delta_4])
            # Generate the new bounding box
            x_new = source_BB[0] - delta_1234[0]
            y_new = source_BB[1] - delta_1234[2]
        # new_BB = np.array([int(x_new), int(y_new), int(w_new), int(h_new)])
        new_BB = np.array([x_new, y_new, w_new, h_new])
        # Activate warnings for I's
        if error_index == 1: 
            warnings.warn(f"Width of bounding box ({w}) exceeds selected target size ({selected_target_size}).")
        elif error_index == 2:
            warnings.warn(f"Width of bounding box ({h}) exceeds selected target size ({selected_target_size}).")
        
        return new_BB, delta_1234, error_index

    def ProceduralRandomPadding(self, target_BB_sizes:np.ndarray, original_img_size:int, final_img_size:int, equal_flag = False, suggested_BB = 0 ):
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
        # original_BB = suggested_BB
        # Determine the target BB size
        target_BB_size = self.determine_max_BB(original_BB,target_BB_sizes)
        # if int(target_BB_size) == 2048:
        #     target_BB_size = 128
        #     original_BB = np.array([1023,1023,64,64])
        # original_BB = np.array([1023,1023,64,64])     
        # Perform random padding
        final_BB,delta_1234, error_index = self.BB_random_padding(original_BB, target_BB_size, (original_img_size,original_img_size), original_img_size,equal_flag)

        # final_BB = np.array([1024-128/2, 1024-128/2,128,128])
        # delta_1234 = np.array([0,0,0,0])
        # target_BB_size = 128
        # Crop the image with BB
        img_cropped = DataProcessing.crop_img_by_BB_float(self.img,final_BB)
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

    def ProceduralRandomPadding_v2(self, target_BB_sizes:np.ndarray, original_img_size:int, final_img_size:int):
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
        original_BB = 0 
        final_BB = np.array([1024-target_BB_sizes/2, 1024-target_BB_sizes/2,target_BB_sizes,target_BB_sizes])
        delta_1234 = np.array([0,0,0,0])
        target_BB_size = target_BB_sizes

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
        return 0,0,original_BB, final_BB, delta_1234, label_resized

    def add_artificial_noise(img_input: np.ndarray, noise: dict, return_intermediates: bool = False) -> np.ndarray:
        """
        Applies a chain of synthetic noise effects to a grayscale image. The chain applied follows the one specificied in the PhD Thesis
        "Data-Driven Image Processing for Enhanced Vision-Based Applications Around Small Bodies With Machine Learning", by Mattia Pugliatti.

        Args:
            img_input (np.ndarray): Input image (grayscale, uint8).
            noise (dict): Dictionary of noise parameters (see below).
            return_intermediates (bool): Whether to return all intermediate outputs.

        Returns:
            np.ndarray: Output noisy image (uint8).
        """
        
        # --- Input validation ---
        if img_input.dtype != np.uint8:
            raise TypeError("Input image must be of type uint8.")

        if img_input.ndim != 2:
            raise ValueError("Input image must be a single-channel grayscale image (2D).")

        img_shape = img_input.shape
        intermediates = {}

        # --- 1. Gaussian Blur ---
        img_1 = cv2.GaussianBlur(img_input, (0, 0), sigmaX=noise['sigma_blur'])

        # --- 2. Motion Blur ---
        length = int(noise['motion_length'])
        if length > 0:
            angle = noise['motion_theta']
            k = np.zeros((length, length), dtype=np.float32)
            cv2.line(k, (0, length // 2), (length, length // 2), 1, thickness=noise.get('rad_linewidth', 1))
            M = cv2.getRotationMatrix2D((length // 2, length // 2), angle, 1)
            k = cv2.warpAffine(k, M, (length, length))
            k /= np.sum(k)
            img_2 = cv2.filter2D(img_1, -1, k)

        # --- 3. Sensor Noise ---
        img_3 = DataProcessing.SensorNoise(img_input, noise)

        # --- 4. Gamma Correction ---
        img_4 = (exposure.adjust_gamma(img_3 / 255.0, noise['bright']) * 255).astype(np.uint8)

        # --- 5. Dead Pixels ---
        # Simulated always on (255)
        img_5 = img_4.copy()
        for i in range(noise['n_dead_px']):
            x = noise['dead_px_x'][i]
            y = noise['dead_px_y'][i]
            if 0 <= x < img_shape[1] and 0 <= y < img_shape[0]:
                img_5[y, x] = 255

        # --- 6. Saturated Buckets ---
        # Simulated always on (255)
        img_6 = img_5.copy()

        for _ in range(noise['n_sat_buckets']):
            if np.random.random() <= 0.5:
                row =  np.random.randint(0, img_shape[0] - 1)
                img_6[row, :] = 255
            else:
                col =  np.random.randint(0, img_shape[1] - 1)
                img_6[:, col] = 255

        # --- 7. Blooming ---
        img_7 = img_6.copy()
        if noise['blooms'] == 1:
            # Find the maximum blooming spot from img_3
            mask = (img_3 == noise['blooms_val']).astype(np.uint8)
            if np.any(mask):
                bloom = cv2.GaussianBlur(mask * 255, (0, 0), noise['sigma_blooms'])
                bloom = (bloom / bloom.max() * 255).astype(np.uint8)
                img_7 = np.clip(img_6.astype(np.uint16) + bloom.astype(np.uint16), 0, 255).astype(np.uint8)

        # --- 8. Radiation ---
        img_8 = img_7.copy()
        if noise['rad'] == 1:
            for _ in range(noise['n_rad_strides']):
                L = np.random.randint(noise['L_min_s'], noise['L_max_s'])
                I = int(np.random.uniform(noise['I_min_s'], noise['I_max_s']) * 255)
                theta = np.deg2rad(np.random.uniform(0, 360))
                x0 = np.random.randint(0, img_shape[1] - 1)
                y0 = np.random.randint(0, img_shape[0] - 1)
                x1 = int(np.clip(x0 + L * np.cos(theta), 0, img_shape[1] - 1))
                y1 = int(np.clip(y0 + L * np.sin(theta), 0, img_shape[0] - 1))
                cv2.line(img_8, (x0, y0), (x1, y1), I, thickness=noise['rad_linewidth'])

        # Save all intermediate output (for debug)
        intermediates['img_1_blur'] = img_1.copy()
        intermediates['img_2_motion_blur'] = img_2.copy()
        intermediates['img_3_sensor_noise'] = img_3.copy()
        intermediates['img_4_gamma'] = img_4.copy()
        intermediates['img_5_dead_pixels'] = img_5.copy()
        intermediates['img_6_sat_buckets'] = img_6.copy()
        intermediates['img_7_blooming'] = img_7.copy()  
        intermediates['img_8_radiation'] = img_8.copy()

        if return_intermediates:
            return img_8, intermediates
        else:
            return img_8
        
    @staticmethod
    def SensorNoise(img_input:np.ndarray, noise:dict) -> np.ndarray:
        """
        Applies simulated sensor noise to a grayscale image based on the specified noise type.

        Supported noise types:
            - 'gaussian': Additive Gaussian noise (models thermal/electronic noise).
            - 'poisson': Poisson noise (models photon shot noise).
            - 'speckle': Multiplicative noise (common in coherent imaging).
            - 'salt_pepper': Random impulse noise (bit flips, corrupted memory, dead pixels).

        Args:
            img_input (np.ndarray): Grayscale input image (2D, uint8).
            noise (dict): Dictionary with parameters:
                - sensor_noise_type (str): Type of noise ('gaussian', 'poisson', 'speckle', 'salt_pepper')
                - mean (float): Mean for Gaussian noise (only if type is 'gaussian')
                - variance (float): Variance for Gaussian or Speckle noise
                - amount (float): Proportion of image affected (only if type is 'salt_pepper')
                - ratio (float): Salt-to-pepper ratio (only if type is 'salt_pepper')

        Returns:
            np.ndarray: Image with simulated sensor noise, in uint8 format.
        
        Raises:
            ValueError: If an unsupported sensor noise type is specified.
        """
        # --- 3. Sensor Noise Injection ---
        img_3 = img_input.copy().astype(np.float32)
        # Read the noise type
        noise_type = noise["sensor_noise_type"]
        # Add noise accordingly
        if noise_type == 'gaussian':
            mean = noise["mean"] * 255
            sigma =  np.sqrt(noise["variance"]) * 255
            gauss = np.random.normal(mean, sigma, img_input.shape)
            img_3 += gauss
        elif noise_type == 'poisson':
            # Poisson noise is signal-dependent
            img_3 = np.random.poisson(img_3.clip(0, 255)).astype(np.float32)
        elif noise_type == 'speckle':
            sigma =  np.sqrt(noise["variance"]) * 255
            noise_map = np.random.normal(0, sigma, img_input.shape)
            img_3 += img_3 * noise_map  # multiplicative noise
        elif noise_type == 'salt_pepper':
            s_vs_p = noise["ratio"]
            amount = noise["amount"]
            num_salt = np.ceil(amount * img_3.size * s_vs_p)
            num_pepper = np.ceil(amount * img_3.size * (1.0 - s_vs_p))
            # Salt noise (white pixels)
            coords = [np.random.randint(0, i, int(num_salt)) for i in img_input.shape]
            img_3[tuple(coords)] = 255
            # Pepper noise (black pixels)
            coords = [np.random.randint(0, i, int(num_pepper)) for i in img_input.shape]
            img_3[tuple(coords)] = 0
        else:
            raise ValueError(f"Unsupported sensor_noise_type: {noise_type}")

        # Return to uint8 image
        img_3 = np.clip(img_3, 0, 255).astype(np.uint8)

        return img_3