% -------------------------------------------How to run MONET--------------------------------------------------------------------------
% Author: Carmine Buonagura

1) Download the Blend files from https://drive.google.com/drive/folders/1K3e5MyQin6T9d_EXLG_gFywJt3I18r6H?usp=sharing and put them in the "monet/input/NodeTrees" folder
2) Load the desired .obj file in the "obj" folder
3) Change the morphological features properties in "Input_file.txt" in the input folder. Do not forget to change the "body_name" in Input_file and set it equal to the loaded obj file in 2)
4) Run main_MONET.py
5) Enjoy your generated model :)


% -------------------------------------------Folders-----------------------------------------------------------------------------------
Description of the various folders

obj --> it contains the obj. models to be processed by MONET. Rename it properly in order to be compliant with the .py code
NodeTrees --> it contains the Blender files which embed the node trees for the default minor body families and the rocks. The blend 	       files are required to direcly load the trees, avoiding to generate them every time MONET is run.
	- MaterialNodeTree.blend --> Blender file containing the node tree of the rubble-pile like minor body
	- MaterialNodeTreeComet.blend --> Blender file containing the node tree of the comet like minor body
	- MaterialNodeTreeRocks.blend --> Blender file containing the node tree of the boulders scattered around the surface of the 					  minor body
	- MaterialNodeTree.py --> Python code for the generation of the node trees
BlendFiles --> Empty folder where the generated Blender files with the final model and material are saved. It will be generated after running the main_MONET.py

% -------------------------------------------Files-----------------------------------------------------------------------------------

Input_file.txt --> File from which it is possible to tune the morphological properties of the minor body. The inputs are the following:

body_name = NAME OF THE OBJ FILE IN FOLDER "Bodies"
category = 1: rubble-pile like 2: comet like
default = yes or no (if yes the morphological charateristics of the "category" field are used, the one below are not considered)
rock_size_small = size of small rocks (i.e. 0.001)
rock_size_medium = size of medium rocks (i.e. 0.008)
rock_size_large = size of large rocks (i.e. 0.03)
rock_count_small = number of small boulders
rock_count_medium = number of medium boulders
rock_count_large = number of large boulders
roughLevel = Surface roughness level (i.e. 2)
SmallCratersNum = number of small craters (i.e. 10)
BigCratersNum = number of large craters (i.e. 4)
color1 = RGBA color 1 (0.007845,0.007845,0.007845,1)
color2 = RGBA color 2 (0.023765,0.023765,0.023765,1)

matrix_output.txt --> Output file, containing relevant morphological properties (rock_count_small, rock_count_medium, rock_count_large,roughLevel, SmallCratersNum, BigCratersNum)

main_MONET --> python script to run MONET and generate the associated Blender file that will be saved in "BlendFiles"

% --------------------------------------------------------------------------------------------------------------------
