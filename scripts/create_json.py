"""
This script shows how to generate a .json geometry file out of a .txt with all relevant body, camera, and sun poses
The data structure of the pointcloud is: 

[0] ID or ET
[1,2,3] Body pos [BU] and [4,5,6,7] orientation [-]
[8,9,10] Camera pos [BU] and [11,12,13,14] orientation [-]
[15,16,17] Sun pos [BU]

"""

import json
import numpy as np

## Load data ##
data = np.loadtxt(
    "input/S01_Eros/geometry/Cloud_2023_12_06_20_16_48.txt", delimiter=" "
).tolist()

# Generate GEOM dictionary
GEOM = {
    "sun": {
        "position": [row[15:18] for row in data]},
    "camera": {
        "position": [row[8:11] for row in data],
        "orientation": [row[11:15] for row in data],
    },
    "body": {
        "position": [row[1:4] for row in data],
        "orientation": [row[4:8] for row in data],
    },
}

# Convert the GEOM dictionary to a JSON string
json_data = json.dumps(GEOM, indent=4)

# Write the JSON string to a file
with open("input/S01_Eros/geometry/geometry.json", "w") as json_file:
    json_file.write(json_data)

print("JSON file successfully generated!")

# Try reading the file and access it
f = open("input/S01_Eros/geometry/geometry.json")
settings_json = json.load(f)

for row in settings_json["sun"]["position"]:
    row = np.array(row)
