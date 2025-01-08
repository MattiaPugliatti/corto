# corto v.1.1
The Celestial Object Rendering TOol (CORTO) is a library that can be used to generate synthetic images-label pairs of celestial and artificial bodies.

At the current stage, the tool is made available with some toy-problem or tutorials for rendering image-label pairs of Eros, Itokawa, Bennu, Didymos, and The Moon. The scenarios are set with the possibility to generate both images and labels. In the current version, corto uses Blender 4.0 and Python 3.11.7

# Setup
To install the library you have two options: 

1) git clone https://github.com/MattiaPugliatti/corto.git
2) pip install cortopy

Then you can install a virtual environment in VSC with the modules listed in the requirements.txt

If you have problems installing the bpy library into VSC, contact the authors. 

To run a tutorial, you need to populate the input folder with one of the scenarios from:

https://drive.google.com/drive/folders/1K3e5MyQin6T9d_EXLG_gFywJt3I18r6H?usp=sharing

Download the scenario of interest, and then locate it into the input folder. Then run the corresponding script within the "tutorials" folder. For example, if you want to generate some image-label pairs of Didymos, after cloning/pip-installing the repository and downloading the folder, your directory should look like this: 

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

## Experimental Installation Fix (Not Recommended)

For certain combinations of OS and hardware (e.g., macOS 14.3 on first-generation Apple Silicon), the standard installation of `bpy` may fail due to missing distributions on PyPI. **This is only a workaround and is not the recommended approach. Your mileage may vary.**

To proceed with this workaround, first ensure the following compatibility requirements are met for the `bpy` release:

1. **Python Version** - Confirm compatibility with your Python version.
2. **Operating System** - Verify that your OS is supported.
3. **Architecture** - Check that your system’s architecture matches the package requirements.

These details can be confirmed by running the command below in the terminal with the correct Python version and checking compatibility tags:

```bash
python -m pip debug --verbose
```

If compatibility checks pass but `pip install bpy` still returns an error (e.g., `ERROR: No matching distribution found for bpy`), you may try the following steps:

1. Download the latest compatible `<version>.whl` distribution of `bpy` from PyPI.
2. Rename the downloaded `.whl` file to match one of the compatible tags shown in the compatibility check (e.g., `<compatible>.whl`).
3. Install the renamed `.whl` file by running:

   ```bash
   pip install <compatible>.whl
   ```
This should allow the installation to complete if all compatibility requirements are satisfied. 

# Folders descriptions
(cortopy) all classes of the corto library are included in this folder

(input) input folder, here is were you need to position all necessary input to run a scenario

(monet) this folder contains the monet tool. Refer to the specific readme within this folder to run monet and generate proceedural asteroid models

(scripts) all sorts of useful scripts are grouped here

(tutorials) the tutorial scripts for Eros, Itokawa, Bennu, Didymos, and the Moon are contained here

# How to run a tutorial script (Visual Studio Code reccomended)

1) Install the repository 

2) Install the bpy module in VSC

3) Install the other libraries listed in the requirements.txt into a virtual environment

4) Download the input data for a specific tutorial from https://drive.google.com/drive/folders/1K3e5MyQin6T9d_EXLG_gFywJt3I18r6H?usp=sharing (For example, download the folder S05_Didymos)

5) Run the script from the "tutorial" folder (For example, the S05_Didymos.py)

6) You should see images and labels generated in an output folder

# How to run your own script 
To shape your own scenario, you can imitate the ones provided in the tutorials. In case you are happy with one of the scenarios, you can always change the inputs and or the tutorial script. Otherwise, if you want to use this library for a different target, you can also imitate how the tutorials script build on it.

# Changelog

| Version | Changelog |
| ------ | ------ |
|    v1.1    |Added Lambert and Oren-Nayar; Added multi-body capability; Added scenario script for Mars-Phobos-Deimos; Fix bugs|


