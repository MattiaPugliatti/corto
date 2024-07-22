import json
import numpy as np



data = np.loadtxt('input/S01_Eros/geometry/Cloud_2023_12_06_20_16_48.txt', delimiter=' ').tolist()

# [0] ID or ET
# [1,2,3] Body pos [BU] and [4,5,6,7] orientation [-]
# [8,9,10] Camera pos [BU] and [11,12,13,14] orientation [-]
# [15,16,17] Sun pos [BU]

GEOM = {"sun" : {"position" : [row[15:18] for row in data]}, "camera" : {"position" :  [row[8:11] for row in data], "orientation" :  [row[11:15] for row in data]}, "body" : {"position" :  [row[1:4] for row in data], "orientation" :  [row[4:8] for row in data]}}
# Convert the dictionary to a JSON string
json_data = json.dumps(GEOM, indent = 4)

# Write the JSON string to a file
with open('input/S01_Eros/geometry/geometry.json', 'w') as json_file:
    json_file.write(json_data)

f = open('input/S01_Eros/geometry/geometry.json')
settings_json = json.load(f)

for row in settings_json['sun']['position']:
    row=np.array(row)

print('ciao')

