
import bpy
import json

def export_uv(obj_name, file_path):
    obj = bpy.data.objects[obj_name]
    
    # Ensure the object has UV data
    if obj.data.uv_layers.active is None:
        raise Exception(f"Object '{obj_name}' does not have a UV map.")
    
    uv_data = []
    
    # Get the active UV layer
    uv_layer = obj.data.uv_layers.active.data
    
    # Iterate over each face's UV coordinates and store them
    for poly in obj.data.polygons:
        poly_uvs = []
        for loop_index in poly.loop_indices:
            uv = uv_layer[loop_index].uv
            poly_uvs.append([uv.x, uv.y])
        uv_data.append(poly_uvs)
    
    # Save UV data to a JSON file
    with open(file_path, 'w') as file:
        json.dump(uv_data, file, indent=4)
    
    print(f"UV data exported to {file_path}")

# Example usage:
export_uv('SourceObjectName', '/path/to/your/uv_data.json')


import bpy
import json

def import_uv(obj_name, file_path):
    obj = bpy.data.objects[obj_name]
    
    # Ensure the object has UV data
    if obj.data.uv_layers.active is None:
        obj.data.uv_layers.new(name='ImportedUV')
    
    uv_layer = obj.data.uv_layers.active.data
    
    # Load the UV data from the file
    with open(file_path, 'r') as file:
        uv_data = json.load(file)
    
    # Ensure the number of faces matches
    if len(uv_data) != len(obj.data.polygons):
        raise Exception("The number of polygons in the target object does not match the source UV data.")
    
    # Apply UV data
    for poly, poly_uvs in zip(obj.data.polygons, uv_data):
        for loop_index, uv in zip(poly.loop_indices, poly_uvs):
            uv_layer[loop_index].uv = (uv[0], uv[1])
    
    print(f"UV data imported to {obj_name}")

# Example usage:
import_uv('TargetObjectName', '/path/to/your/uv_data.json')