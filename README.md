# corto v.0.1
The Celestial Object Rendering TOol (CORTO) is a bundle of codes that can be used to generate synthetic images-label pairs of celestial bodies.

At the current stage, the tool is made available as a beta version (v.0.1) with some toy-problem scenarios for rendering image-label pairs of Eros, Itokawa, Bennu, Didymos, and The Moon. The scenarios are set with the possibility to generate both image and label pairs. 

# Setup
The toy-problems shall be downloaded from the following link: 

https://drive.google.com/drive/folders/1K3e5MyQin6T9d_EXLG_gFywJt3I18r6H?usp=sharing

Once you pull the repository from GitHub and you get the data folder from Google Drive, its directory should look as follows: 

- corto
	- functions (from GitHub)
  		- rendering
    		- inputGeneration
      		- gnc
        - input (from GitHub)
        	- ALL.txt	 
	- data (downloaded from the above link on Google Drive)
  		-scenarios
 	- README.md (from GitHub)	

The "rendering" folder contains the main rendering Python function: RenderFromTxt.py. This function shall be run within the specific .blend of the scenario of interest (or from command), reading the setup expressed in the "All.txt" input file. The function position correctly positions the body, camera, and light in the scene for each setup defined within a geometry.txt file, which is contained in every scenario. For simplicity, a file is provided for all toy problems named "Cloud_2023_12_06_20_16_48.txt".

The "inputGeneration" folder contains an example of a Python function that can be used to generate the geometry txt to be used as input for the camera-body-Sun poses, creating a cloud of points with predefined conditions. The .txt with the poses have N rows (equal to the desired number of acquisitions) and 18 columns, each representing a specific quantity: 

- [0]: ID or ephemeris time
- [1,2,3]: Position of the body in BU (Blender units)
- [4,5,6,7]: Quaternion orientation of the body (in Blender notation W-XYZ)
- [8,9,10]: Position of the camera in BU
- [11,12,13,14]: Quaternion orientation of the camera (in Blender notation W-XYZ)
- [15,16,17]: Position of the Sun in BU

The "gnc" folder contains 4 examples of python functions that can be used to interface Blender-corto with a closed-loop GNC system. These are still WIP.

Lastly, the "scenarios" folder contains the .blend, texture, displacement, and .obj of all of the toy problems. 

# How to run

There are different ways to run a scenario. Let's say you generate your specific .txt with body-camera-Sun poses using the script within "inputGeneration". Then, you have to put your .txt in the folder of the specific scenario you want to render, and then modify the parameters of the "ALL.txt" accordingly. Lastly, you only need to specify the path of the "ALL.txt" in the rendering function.

To run the scenario, open the .blend file you are interested, go to the scripting tab in Blender, and run the "RenderFromTxt.py" function. Blender will start rendering the scene you have specified with the settings in "ALL.txt" and with the poses in "Cloud_2023_12_06_20_16_48.txt". Alternatively, you can also run the .blend from command window. 
