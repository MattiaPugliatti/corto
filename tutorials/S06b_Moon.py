"""
Tutorial script to render images of the S06b_Moon scenario. 

In this scenario, a high-resolution tile of the Moon surface with improved texture is rendered, which is useful for close navigation regimes such as low lunar orbits or landing trajectories

To run this tutorial, you first need to put data in the input folder. 
You can download the tutorial data from: 

https://drive.google.com/drive/folders/1K3e5MyQin6T9d_EXLG_gFywJt3I18r6H?usp=sharing

"""
import sys
import os
sys.path.append(os.getcwd())

import cortopy as corto
import numpy as np 
import pandas as pd
import OpenEXR
import Imath

## Clean all existing/Default objects in the scene 
corto.Utils.clean_scene()

### (1) DEFINE INPUT ### 
# scenario_name = "S06b_Moon/moon_0_10E_0_10N" # Scenario A
# scenario_name = "S06b_Moon/moon_0_10E_10_20N" # Scenario B
# scenario_name = "S06b_Moon/moon_10_20E_0_10N" # Scenario C
scenario_name = "S06b_Moon/moon_10_20E_10_20N" # Scenario D
# scenario_name = "S06b_Moon/moon_20_30E_0_10N" # Scenario E

scene_name = "scene.json" # name of the scene input
geometry_name = "geometry.json" # name of the geometry input
body_name = "lunar_terrain_model.obj" # name of the body input

# Load inputs and settings into the State object
State = corto.State(scene = scene_name, geometry = geometry_name, body = body_name, scenario = scenario_name)
# Add extra inputs 
State.add_path('texture_path', os.path.join(State.path["input_path"],'Utils','Texture.png'))
State.add_path('CraterMask_path', os.path.join(State.path["input_path"],'Utils','crater_mask.png'))
State.add_path('DEM_path',os.path.join(State.path["input_path"],'Utils','DEM.tif'))
State.add_path('info_path',os.path.join(State.path["input_path"],'Utils','info.txt'))
State.add_path('LatLonMask_path',os.path.join(State.path["input_path"],'Utils','lat_lon_mask.exr'))
State.add_path('filteredcraters_path',os.path.join(State.path["input_path"],'Utils','FilteredCraters.csv'))
State.add_path('material_path',os.path.join(State.path["input_path"],'body','material'))
# Add extra outputs 
depth_dir = os.path.join(State.path["output_path"],'depth_txt')
altimeter_dir = os.path.join(State.path["output_path"],'altimeter')
YOLO1_dir = os.path.join(State.path["output_path"],'YOLO1_labels')
YOLO2_dir = os.path.join(State.path["output_path"],'YOLO2_labels')
corto.Utils.mkdir(depth_dir)
corto.Utils.mkdir(altimeter_dir)
corto.Utils.mkdir(YOLO1_dir)
corto.Utils.mkdir(YOLO2_dir)

### (2) SETUP THE SCENE ###
# Setup bodies
cam = corto.Camera('WFOV_Camera', State.properties_cam)
sun = corto.Sun('Sun',State.properties_sun)
name, extension = os.path.splitext(body_name)
body = corto.Body("Lunar_Tile", State.properties_body)

# Setup rendering engine
rendering_engine = corto.Rendering(State.properties_rendering)
# Setup environment
ENV = corto.Environment(cam, body, sun, rendering_engine)

### (3) MATERIAL PROPERTIES ###
disk_function_path = os.path.join(os.getcwd(),"cortopy/corto_diskFunctions.osl")
phase_function_path = os.path.join(os.getcwd(),"cortopy/corto_phaseFunctions.osl")

scattering_function = "McEwen"
geometric_albedo = 0.045
osl_coeffs = {"scattering_function": scattering_function}

material = corto.Shading.create_new_material('Lunar tile material')
corto.Shading.create_lunar_shader(material,State,scattering_function, geometric_albedo, disk_function_path, phase_function_path, osl_coeffs)
corto.Shading.assign_material_to_object(material, body)

### (4) COMPOSITING PROPERTIES ###
# Build image-label pairs pipeline
tree = corto.Compositing.create_compositing()
render_node = corto.Compositing.rendering_node(tree, (-400, -200))  # Render Layers node
corto.Compositing.create_lunar_tile_labels(tree,render_node, State)


# Load the lat/lon mask (EXR format)
def read_exr_lat_lon(exr_path):
    exr_file = OpenEXR.InputFile(exr_path)
    header = exr_file.header()
    dw = header['dataWindow']
    width = dw.max.x - dw.min.x + 1
    height = dw.max.y - dw.min.y + 1
    FLOAT = Imath.PixelType(Imath.PixelType.FLOAT)
    lat_data = np.frombuffer(exr_file.channel('R', FLOAT), dtype=np.float32).reshape(height, width)
    lon_data = np.frombuffer(exr_file.channel('G', FLOAT), dtype=np.float32).reshape(height, width)
    return lat_data, lon_data

def classify_crater_size(diameter_km):
    """Classify craters based on diameter."""
    if diameter_km < 5:
        return 0  # Small
    elif 5 <= diameter_km < 20:
        return 1  # Medium
    else:
        return 2  # Large

# Function to convert lat/lon to pixel coordinates using the mask
def latlon_to_pixel(lat, lon, lat_mask, lon_mask):
    """Finds the closest pixel for a given lat/lon using the precomputed mask."""
    lat_diff = np.abs(lat_mask - lat)
    lon_diff = np.abs(lon_mask - lon)
    distance = lat_diff + lon_diff  # Combined distance metric
    y, x = np.unravel_index(np.argmin(distance), distance.shape)  # Find closest pixel
    return x, y

def function_to_generate_labels(k, State, depth_dir, YOLO1_dir, YOLO2_dir):
    filtered_craters = pd.read_csv(State.path["filteredcraters_path"])
    # region depth map
    txtname = '{num:06d}'
    # Path to the saved EXR depth file
    exr_path = os.path.join(os.path.join(State.path["output_path"], "depth_exr"), txtname.format(num=(k+0)) + '.exr')
    # Open the EXR file
    exr = OpenEXR.InputFile(exr_path)
    # Get image resolution
    header = exr.header()
    dw = header['dataWindow']
    width = dw.max.x - dw.min.x + 1
    height = dw.max.y - dw.min.y + 1
    # Define pixel type
    pt = Imath.PixelType(Imath.PixelType.FLOAT)
    # Retrieve Blender object associated with the body
    with open(State.path["info_path"], "r") as file:
        lines = file.readlines()
    scale_factor_in_blender = float(lines[5].strip())
    # Read depth channel
    depth_str = exr.channel('V', pt)  # 'V' channel contains depth
    depth_np = np.frombuffer(depth_str, dtype=np.float32).reshape(height, width) * scale_factor_in_blender
    altimeter_data2 = np.sum(depth_np[int(np.round(width/2)-2):int(np.round(width/2)+2), int(np.round(height/2)-2):int(np.round(height/2)+2)]) / 16
    # Save as TXT
    txt_path = os.path.join(depth_dir, txtname.format(num=(k+0)) + '.txt') #exr_path.replace('.exr', '.txt')
    np.savetxt(txt_path, depth_np, fmt='%.5f', delimiter=' ')
    np.savetxt(os.path.join(State.path["output_path"],'altimeter', txtname.format(num=(k+0)) + '.txt'), [altimeter_data2], delimiter=' ',fmt='%.5f') 

    exr_path2 = os.path.join(os.path.join(State.path["output_path"], "lat_lon_exr"), txtname.format(num=(k+0)) + '.exr')
    lat_mask, lon_mask = read_exr_lat_lon(exr_path2)
    # Image size (same as lat-lon mask)
    height, width = lat_mask.shape
    km2pixel_scale = 512 / ((1737.4 * np.cos(np.radians((lat_mask.max() + lat_mask.min()) / 2)) * 2 * np.pi / 360) * (lon_mask.max() - lon_mask.min()))
    # Iterate over craters and save YOLO segmentation labels
    for _, crater in filtered_craters.iterrows():
        # Check if crater center is within render bounds
        crater_lat, crater_lon = crater['LAT_ELLI_IMG'], crater['LON_ELLI_IMG']
        if (crater_lat < lat_mask.min() or crater_lat > lat_mask.max() or
            crater_lon < lon_mask.min() or crater_lon > lon_mask.max()):
            continue  # Skip crater if outside render bounds
        # Convert crater center lat/lon to pixel coordinates
        center_x, center_y = latlon_to_pixel(crater['LAT_ELLI_IMG'], crater['LON_ELLI_IMG'], lat_mask, lon_mask)
        # Generate ellipse rim points
        num_points = 100  # Number of points along the ellipse
        theta = np.linspace(0, 2 * np.pi, num_points)
        # Compute ellipse axes in pixels
        semi_major_axis = int(km2pixel_scale * crater['DIAM_ELLI_MAJOR_IMG'] / 2)
        semi_minor_axis = int(km2pixel_scale * crater['DIAM_ELLI_MINOR_IMG'] / 2)
        angle = np.radians(-crater['DIAM_ELLI_ANGLE_IMG'])  # Convert to radians
        ellipse_x = semi_major_axis * np.cos(theta)
        ellipse_y = semi_minor_axis * np.sin(theta)
        # Rotate ellipse points
        rot_matrix = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
        rotated_points = np.dot(rot_matrix, np.vstack([ellipse_x, ellipse_y]))
        # Convert ellipse rim points to pixel coordinates
        final_x = rotated_points[0, :] + center_x
        final_y = rotated_points[1, :] + center_y
        # Normalize coordinates (0 to 1)
        yolo_coords = [f"{max(0, min(x/width, 1)):.6f} {max(0, min(y/height, 1)):.6f}" for x, y in zip(final_x, final_y)]
        # Format as YOLO segmentation: class_id x1 y1 x2 y2 ... xn yn
        yolo_label = f"0 {' '.join(yolo_coords)}"  # Class 0 (crater)
        yolo_label_classes = f"{classify_crater_size(crater['DIAM_ELLI_MAJOR_IMG'])} {' '.join(yolo_coords)}"  # Class 0 (crater)
        # Save to a text file
        output_label_path = os.path.join(YOLO1_dir, txtname.format(num=(k+0)) + '.txt')
        with open(output_label_path, "a") as f:  # ✅ Use "a" to append instead of "w"
            f.write(yolo_label + "\n")  # ✅ Add a newline after each crater
        output_label_classes_path = os.path.join(YOLO2_dir, txtname.format(num=(k+0)) + '.txt')
        with open(output_label_classes_path, "a") as f:  # ✅ Use "a" to append instead of "w"
            f.write(yolo_label_classes + "\n")  # ✅ Add a newline after each crater

### (5) GENERATION OF IMG-LBL PAIRS ###
osl_geometry_settings = {}
n_img = 5 # Render the first "n_img" images

for idx in range(0,n_img):
    ENV.PositionAll(State,index=idx)
    # Update OSL shading properties (CAM and SUN GEOMETRY)
    _, pos_cam, pos_sun = ENV.get_positions() # TODO: add a check on pos_bod such that the vectors are all body-referenced for the OSL shader
    osl_geometry_settings["cam_pos"] = pos_cam
    osl_geometry_settings["sun_pos"] = pos_sun
    corto.Shading.update_osl_geometry(material, osl_geometry_settings)
    ENV.RenderOne(cam, State, index=idx, depth_flag = True)
    function_to_generate_labels(idx, State, depth_dir, YOLO1_dir, YOLO2_dir)

# Save .blend as debug
corto.Utils.save_blend(State)