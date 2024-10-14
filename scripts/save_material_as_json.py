"""
Script to serialize and save a shading tree as a .json file

"""

import bpy
import json

# Define output path

output_path = '/put_your_own_path/shading_output.json'

# Function to serialize node links
def serialize_link(link):
    return {
        "from_node": link.from_node.name,
        "from_socket": link.from_socket.name,
        "to_node": link.to_node.name,
        "to_socket": link.to_socket.name
    }

# Function to convert bpy_prop_array to a list
def convert_value(value):
    if isinstance(value, bpy.types.bpy_prop_array):
        return list(value)
    return value

# Function to serialize nodes
def serialize_node(node):
    return {
        "name": node.name,
        "type": node.bl_idname,
        "location": list(node.location),  # Convert location (a Vector) to a list
        "inputs": {
            input.name: convert_value(input.default_value) if hasattr(input, 'default_value') else None
            for input in node.inputs
        },
        "outputs": {
            output.name: convert_value(output.default_value) if hasattr(output, 'default_value') else None
            for output in node.outputs
        }
    }

# Get the node tree of the material
material_name = "Surface_D2"
material = bpy.data.materials.get(material_name)

if not material:
    raise ValueError(f"Material '{material_name}' not found in the current file.")

if not material.use_nodes:
    raise ValueError(f"Material '{material_name}' does not use nodes.")

node_tree = material.node_tree

# Export the nodes and links to a dictionary
node_data = {
    "nodes": [serialize_node(node) for node in node_tree.nodes],
    "links": [serialize_link(link) for link in node_tree.links]
}

# Write the node data to the JSON file
with open(output_path, 'w') as json_file:
    json.dump(node_data, json_file, indent=4)

print("Node data successfully saved.")