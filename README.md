# corto v.1.0
The Celestial Object Rendering TOol (CORTO) is a library that can be used to generate synthetic images-label pairs of celestial and artificial bodies.

At the current stage, the tool is made available in version (v.1.0) with some toy-problem tutorials for rendering image-label pairs of Eros, Itokawa, Bennu, Didymos, and The Moon. The scenarios are set with the possibility to generate both images and labels. In the current version, corto uses Blender 4.0 and Python 3.11.0

# Setup
To install the library you have two options: 

1) git clone 
2) pip install

Then you can install a virtual environment in VSC with the modules listed in the requirements.txt

If you have problems installing the bpy library into VSC, contact the authors. 

To run a tutorial, you need to populate the input folder with one of the scenarios from:

https://drive.google.com/drive/folders/1K3e5MyQin6T9d_EXLG_gFywJt3I18r6H?usp=sharing

Download the scenario of interest, and then locate it in the input folder. Then run the corresponding script within the "tutorials" folder. For example, if you want to generate some image-label pairs of Didymos, after cloning/pip-installing the repository and downloading the folder, your directory should look like this: 

- cortopy
	- __init__.py
	- _Body.py
	- ...
- input 
	- S05_Didymos_Milani (from GDrive)
- monet
	- input
	- output
	- main_MONET.py
- scripts 
- tutorials
	- ...
	- S06_Didymos_Milani.py
- .gitignore
- LICENSE
- requirements.txt
- README.md (from GitHub)	

# Folders descriptions
(cortopy) all classes of the corto library are included in this folder

(input) input folder, here is where you need to position all necessary input to run a scenario

(monet) this folder contains the monet tool. Refer to the specific readme within this folder to run monet and generate procedural asteroid models

(scripts) all sorts of useful scripts are grouped here

(tutorials) the tutorial scripts for Eros, Itokawa, Bennu, Didymos, and the Moon are contained here

# How to run a tutorial script (Visual Studio Code recommended)

1) Install/clone the repository 

2) Install the bpy extension in Visual Studio Code

3) Create a virtual environment in VSC using the requirements.txt (Use Python 3.11.0)
   
4) Download the input data for a specific tutorial from https://drive.google.com/drive/folders/1K3e5MyQin6T9d_EXLG_gFywJt3I18r6H?usp=sharing (For example, download the folder S05_Didymos)

5) Run the script from the "tutorial" folder (For example, the S05_Didymos.py)

6) You should see images and labels generated in an output folder


The installation of Blender is optional and facilitates opening the final .blend file generated with corto for visual and debugging purposes. If you want to install Blender, please use Blender 4.0, which you can download here (https://download.blender.org/release/Blender4.0/) 


# How to run your own script 

To shape your own scenario, you can imitate the ones provided in the tutorials. If you are happy with one of the scenarios, you can always change the inputs and/or the tutorial script. Otherwise, if you want to use this library for a different target, you can also imitate how the tutorial script builds on it. 
