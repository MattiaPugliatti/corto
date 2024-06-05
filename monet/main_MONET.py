import os
import sys
#file_dir = os.path.dirname(__file__)
#print(file_dir)
#sys.path.append(file_dir)

import MONET_v1# import initialization, run
import random
import os
#body_name = "suzanne"
#category = 2
#rock_size_small = 0.005
#rock_size_medium = 0.002
#rock_size_large = 0.03
#rock_count_small = 0
#rock_count_medium = 20
#rock_count_large = 2
#roughLevel = 20
#SmallCratersNum = 10
#BigCratersNum = 4
#color1 = False
#color2 = False

category = 1

rock_size_small = 0.001
rock_size_medium = 0.008
rock_size_large = 0.03

rock_count_small_Vec = [0]*100
rock_count_small_Vec[:10] = [100000]*10
rock_count_small_Vec[20:23] = [300000]*3

rock_count_medium_Vec = [0, 100, 400, 800]
rock_count_large_Vec = [0, 2, 4, 6, 8]
roughLevel_Int = [0.1, 15]
SmallCratersNum_Int = [4, 32]
BigCratersNum_Int = [0, 3]
color1 = False
color2 = False

# Get the current working directory
current_directory = os.getcwd()

astName = 'Ast.obj'
folder = os.path.join(current_directory,'monet','input','obj')
outputFolder = os.path.join(current_directory,'monet','output','obj')

# Get the current working directory
folder_path = os.path.join(current_directory, folder)

data = []
# Check if the path is a directory
if os.path.isdir(folder_path):
    # Iterate over the elements in the folder
    for element in os.listdir(folder_path):
        # Construct the full path to the element
        element_path = os.path.join(folder_path, element)
        obj_path = os.path.join(element_path, astName)

        body_name = element
        rock_count_small = random.choice(rock_count_small_Vec)
        rock_count_medium = random.choice(rock_count_medium_Vec)
        rock_count_large = random.choice(rock_count_large_Vec)
        roughLevel = random.uniform(roughLevel_Int[0], roughLevel_Int[1])
        SmallCratersNum = random.uniform(SmallCratersNum_Int[0], SmallCratersNum_Int[1])
        BigCratersNum = random.uniform(BigCratersNum_Int[0], BigCratersNum_Int[1])


        if category == 1:
            blendName = "MaterialNodeTree"
        elif category == 2:
            blendName = "MaterialNodeTreeComet"

        MONET_v1.run(rock_count_small, rock_size_small, rock_count_large, rock_count_medium, rock_size_large, rock_size_medium, body_name, category, blendName, roughLevel, SmallCratersNum, BigCratersNum, color1, color2, obj_path, outputFolder)
        vec = [rock_count_small, rock_count_medium, rock_count_large, roughLevel, SmallCratersNum, BigCratersNum]
        data.append(vec)

else:
    print(f'The specified path is not a directory: {folder_path}')

matrix_string = ""
for row in data:
    row_string = ", ".join(map(str, row))
    matrix_string += row_string + "\n"

# Write the matrix to a text file
file_path = 'matrix_output.txt'
with open(file_path, 'w') as file:
    file.writelines(matrix_string)
