import bpy
import random
import shutil
import os
#v 1.0
#  
# This function assigns values to the main variables accordingly to the
# model's dimension.
def initialization(file_path = False):

    # Define the file path
    if not file_path:
        current_directory = os.getcwd()
        file_path = bpy.path.abspath(os.path.join(current_directory, "monet","input","Input_file.txt"))
        #file_path = bpy.path.abspath("//Input_file.txt")

    # Create empty dictionaries to store the variable assignments
    variables = {}

    # Read the file and parse the lines
    with open(file_path, 'r') as file:
        for line in file:
            # Split the line into key and value parts based on '='
            key, value = line.strip().split('=')

            # Remove leading and trailing spaces and store in the dictionary
            variables[key.strip()] = value.strip()

    # Assign the values to the variables
    body_name = str(variables['body_name'])
    default = str(variables['default'])
    category = int(variables['category'])
    rock_size = float(variables['rock_size_small'])
    rock_size_medium = float(variables['rock_size_medium'])
    rock_size_big = float(variables['rock_size_large'])
    rock_count = float(variables['rock_count_small'])
    rock_count_medium = float(variables['rock_count_medium'])
    rock_count_big = float(variables['rock_count_large'])


    if default == 'no':
        color1 = eval(variables['color1'])
        color2 = eval(variables['color2'])
        roughLevel = float(variables['roughLevel'])
        SmallCratersNum = float(variables['SmallCratersNum'])
        BigCratersNum = float(variables['BigCratersNum'])
    else:
        color1 = False
        color2 = False
        roughLevel = False
        SmallCratersNum = False
        BigCratersNum = False

    if category == 1 and default == 'yes':
        rock_size = 0.001
        rock_size_medium = 0.008
        rock_size_big = 0.03
        rock_count = 300000
        rock_count_medium = 800
        rock_count_big = random.randint(1,8)
        blendName = "MaterialNodeTree"
    elif category == 2 and default == 'yes':
        rock_size = 0.001
        rock_size_medium = 0.004
        rock_size_big = 0.001
        rock_count = 1000
        rock_count_medium = 100
        rock_count_big = 1
        blendName = "MaterialNodeTreeComet"
    elif category == 1 and default == 'no':
        blendName = "MaterialNodeTree"
    elif category == 2 and default == 'no':
        blendName = "MaterialNodeTreeComet"
    return rock_count, rock_size, rock_count_big, rock_count_medium, rock_size_big, rock_size_medium, body_name, category, blendName, roughLevel, SmallCratersNum, BigCratersNum, color1, color2

# This function selects and activates the desired object in the scene.
def element_selection(name):
    ob = bpy.context.scene.objects[name]       # Get the object
    bpy.ops.object.select_all(action='DESELECT') # Deselect all objects
    bpy.context.view_layer.objects.active = ob   # Activate the desired object
    ob.select_set(True)                          # Select the desired object

# This function applies the sub-surface modifier and the smooth shading.
def surface_refinement(obs, render_levels, view_levels):
    for ob in obs:
        if not ob.type == 'MESH':
            continue
        # Select modifier
        ssm = ob.modifiers.new("SubbyO", type='SUBSURF')
        # Change parameters
        ssm.render_levels = render_levels
        ssm.levels = view_levels
        me = ob.data
        # Smooth shading
        me.polygons.foreach_set("use_smooth", (True,) * len(me.polygons))

# This function is needed to slightly modify the surface of the model exploiting
# a displacement modifier.
def surface_roughness(obs,noise_scale,weight,strength,texture):
    for ob in obs:
        if not ob.type == 'MESH':
            continue
        # Generate the texture and set the attributes
        voronoi_tex = bpy.data.textures.new("displace_voronoi", texture)
        voronoi_tex.noise_scale = noise_scale
        # Displacement modifier
        disp_mod = None
        for modifier in ob.modifiers:
            if modifier.type == 'DISPLACE':
                disp_mod = modifier
        if not disp_mod:
            disp_mod = ob.modifiers.new(name='MyVoronoiDisplace', type='DISPLACE')
        # Assign the texture
        disp_mod.texture = voronoi_tex
        disp_mod.strength = strength
        disp_mod.vertex_group = "Group"
        if texture == 'VORONOI':
            # Assign the weights of the Voronoi texture
            voronoi_tex.weight_1 = 2
            voronoi_tex.weight_2 = 2
            voronoi_tex.weight_3 = 2
            voronoi_tex.weight_4 = 2

# This function creates a particle system.
def particles_system(obj, count, crater_size, random_size, collection):
    if len(obj.particle_systems) < 3:
        # Define the new particle system
        obj.modifiers.new("part"+str(len(obj.particle_systems)), type='PARTICLE_SYSTEM')
        print(40*"=")
        print(len(obj.particle_systems))
        part = obj.particle_systems[len(obj.particle_systems)-1]
        # Change the parameters (number, size, orientation, etc.)
        settings = part.settings
        settings.type = 'HAIR'
        settings.count = int(count)
        settings.render_type = 'COLLECTION'
        settings.instance_collection = bpy.data.collections[collection]
        settings.use_rotation_instance = True
        settings.particle_size = crater_size
        settings.size_random = random_size
        settings.use_advanced_hair = True
        settings.use_rotations = True
        settings.phase_factor_random = 2
        settings.phase_factor = 0.5
        bpy.context.object.particle_systems.active.seed = random.randint(0,100)

# Function to evaluate the average model dimension.
def create_collection():
    # Delete of the collection called "Rocks"
    name = "Rocks_small"
    name1 = "Rocks_big"
    name2 = "Rocks_medium"
    name3 = "Collection"
    remove_collection_objects = True
    coll = bpy.data.collections.get(name)
    coll1 = bpy.data.collections.get(name1)
    coll2 = bpy.data.collections.get(name2)
    coll3 = bpy.data.collections.get(name3)
    if coll:
        if remove_collection_objects:
            obs = [o for o in coll.objects if o.users == 1]
            while obs:
                bpy.data.objects.remove(obs.pop())
        bpy.data.collections.remove(coll)
    if coll1:
        if remove_collection_objects:
            obs = [o for o in coll1.objects if o.users == 1]
            while obs:
                bpy.data.objects.remove(obs.pop())
        bpy.data.collections.remove(coll1)
    if coll2:
        if remove_collection_objects:
            obs = [o for o in coll2.objects if o.users == 1]
            while obs:
                bpy.data.objects.remove(obs.pop())
        bpy.data.collections.remove(coll2)
    if coll3:
        if remove_collection_objects:
            obs = [o for o in coll3.objects if o.users == 1]
            while obs:
                bpy.data.objects.remove(obs.pop())
        bpy.data.collections.remove(coll3)
    bpy.ops.collection.create(name  = "Collection")
    bpy.context.scene.collection.children.link(bpy.data.collections["Collection"])
    # Creation of a new collection called "Rocks"
    bpy.ops.collection.create(name  = "Rocks_small")
    bpy.context.scene.collection.children.link(bpy.data.collections["Rocks_small"])
    # Set the "Rocks" collection active
    collections = bpy.context.view_layer.layer_collection.children
    for collection in collections:
        if collection.name == "Rocks_small":
            bpy.context.view_layer.active_layer_collection = collection
    # Hide the elements present in the active collection
    bpy.context.view_layer.active_layer_collection.hide_viewport = False
    # Creation of a new collection called "Rocks_big"
    bpy.ops.collection.create(name  = "Rocks_big")
    bpy.context.scene.collection.children.link(bpy.data.collections["Rocks_big"])
    # Set the "Rocks" collection active
    collections = bpy.context.view_layer.layer_collection.children
    for collection in collections:
        if collection.name == "Rocks_big":
            bpy.context.view_layer.active_layer_collection = collection
    # Hide the elements present in the active collection
    bpy.context.view_layer.active_layer_collection.hide_viewport = False
    # Creation of a new collection called "Rocks_big"
    bpy.ops.collection.create(name  = "Rocks_medium")
    bpy.context.scene.collection.children.link(bpy.data.collections["Rocks_medium"])
    # Set the "Rocks" collection active
    collections = bpy.context.view_layer.layer_collection.children
    for collection in collections:
        if collection.name == "Rocks_medium":
            bpy.context.view_layer.active_layer_collection = collection
    # Hide the elements present in the active collection
    bpy.context.view_layer.active_layer_collection.hide_viewport = False
    # Select and delete all the objects in the scene
    bpy.ops.object.select_all(action = "SELECT")
    bpy.ops.object.delete(use_global = False)
    # Set the main collection active
    for collection in collections:
        if collection.name == "Collection":
            bpy.context.view_layer.active_layer_collection = collection

# Generation of the rocks that will be placed on the model surface thanks to the
# particle system.
def rock_generation(rock_count, rock_size, rock_random_size, coll_name):
    # Set the rocks collection active
    collections = bpy.context.view_layer.layer_collection.children
    for collection in collections:
        if collection.name == coll_name:
            bpy.context.view_layer.active_layer_collection = collection
    # Generation of 50 random rocks
    bpy.ops.mesh.add_mesh_rock(num_of_rocks=50, scale_fac=(1,1,1))

    # The material is assigned to each generated rock
    col = bpy.data.collections.get(coll_name)
    if col:
        for obj in col.objects:
            obj.select_set(True)
            # Activate the i-th rock in the collection "Rocks"
            bpy.context.view_layer.objects.active = bpy.data.objects[obj.name]
            ob = bpy.context.active_object
            ob.pass_index = 2

            # Initialize a new material
            mat = bpy.data.materials.new(name="rock_mat")
            if ob.data.materials:
                ob.data.materials[0] = mat
            else:
                ob.data.materials.append(mat)
            bpy.context.object.active_material.use_nodes = True
            # Creation of the new material through the node tree
            rockMaterial(mat)

    # Set the primary model active
    element_selection("asteroid")
    obj = bpy.context.active_object
    # Apply the rocks with the particle system
    particles_system(obj, rock_count, rock_size, rock_random_size, coll_name)
    # To hide the mother rocks (rocks previously randomly generated)
    bpy.context.view_layer.active_layer_collection.hide_viewport = True

def rockMaterial(mat):
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear() # Clear the nodes

    appended_node_group = bpy.data.node_groups.get("RockTree") # TextureMap
    group_node = bpy.context.active_object.active_material.node_tree.nodes.new('ShaderNodeGroup')
    group_node.node_tree = appended_node_group

    group_node.location = (100, 0)
    #############################################
    bpy.data.node_groups["Roughness"].nodes["Mapping"].inputs[1].default_value[0] = random.randint(0, 1000)
    bpy.data.node_groups["Roughness"].nodes["Mapping"].inputs[1].default_value[1] = random.randint(0, 1000)
    bpy.data.node_groups["Roughness"].nodes["Mapping"].inputs[1].default_value[2] = random.randint(0, 1000)

    bpy.data.node_groups["Noise"].nodes["Mapping.001"].inputs[1].default_value[0] = random.randint(0, 1000)
    bpy.data.node_groups["Noise"].nodes["Mapping.001"].inputs[1].default_value[0] = random.randint(0, 1000)
    bpy.data.node_groups["Noise"].nodes["Mapping.001"].inputs[1].default_value[0] = random.randint(0, 1000)
    #################################################

    '''
    shader = nodes.new(type="ShaderNodeBsdfPrincipled")
    shader.location = (500, 0)

    output = nodes.new(type="ShaderNodeOutputMaterial")
    output.location = (900, 0)

    shader.inputs[5].default_value = 0
    shader.inputs[7].default_value = 1
    shader.inputs[14].default_value = 180
    shader.inputs[15].default_value = 1

    link_col_shad = links.new(group_node.outputs[0], shader.inputs[0])
    link_shad_out = links.new(shader.outputs[0], output.inputs[0])
    link_vect_shad = links.new(group_node.outputs[1], shader.inputs[19])
    '''

def astMaterial(roughLevel = False, SmallCratersNum = False, BigCratersNum = False, color1 = False, color2 = False):
    bpy.context.object.active_material.name = "asteroid_material"
    # get the material
    mat = bpy.data.materials['asteroid_material']
    # get the nodes
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear() # Clear the nodes

    appended_node_group = bpy.data.node_groups.get("TextureMap") # TextureMap
    group_node = bpy.context.active_object.active_material.node_tree.nodes.new('ShaderNodeGroup')
    group_node.node_tree = appended_node_group

    group_node.location = (100, 0)

    #############################################
    bpy.data.node_groups["Roughness"].nodes["Mapping"].inputs[1].default_value[0] = random.randint(0, 1000)
    bpy.data.node_groups["Roughness"].nodes["Mapping"].inputs[1].default_value[1] = random.randint(0, 1000)
    bpy.data.node_groups["Roughness"].nodes["Mapping"].inputs[1].default_value[2] = random.randint(0, 1000)

    bpy.data.node_groups["Noise"].nodes["Mapping.001"].inputs[1].default_value[0] = random.randint(0, 1000)
    bpy.data.node_groups["Noise"].nodes["Mapping.001"].inputs[1].default_value[0] = random.randint(0, 1000)
    bpy.data.node_groups["Noise"].nodes["Mapping.001"].inputs[1].default_value[0] = random.randint(0, 1000)

    bpy.data.node_groups["Small_craters"].nodes["Mapping.002"].inputs[1].default_value[0] = random.randint(0, 1000)
    bpy.data.node_groups["Small_craters"].nodes["Mapping.002"].inputs[1].default_value[0] = random.randint(0, 1000)
    bpy.data.node_groups["Small_craters"].nodes["Mapping.002"].inputs[1].default_value[0] = random.randint(0, 1000)

    bpy.data.node_groups["Big_craters"].nodes["Mapping.003"].inputs[1].default_value[0] = random.randint(0, 1000)
    bpy.data.node_groups["Big_craters"].nodes["Mapping.003"].inputs[1].default_value[0] = random.randint(0, 1000)
    bpy.data.node_groups["Big_craters"].nodes["Mapping.003"].inputs[1].default_value[0] = random.randint(0, 1000)
    #################################################

    # Roughness level
    #bpy.data.node_groups["TextureMap"].nodes["Bump_texture"].inputs[1].default_value = roughLevel
    bpy.data.node_groups["Roughness"].nodes["Noise Texture"].inputs[2].default_value = roughLevel

    # Small craters number
    bpy.data.node_groups["Small_craters"].nodes["Voronoi Texture.001"].inputs[2].default_value = SmallCratersNum
    # Big craters number
    bpy.data.node_groups["Big_craters"].nodes["Voronoi Texture.002"].inputs[2].default_value = BigCratersNum
    if color1:
        # Asteroid color
        bpy.data.node_groups["Roughness"].nodes["ColorRamp"].color_ramp.elements[0].color = color1 #(0.00727795, 0.00727795, 0.00727795, 1)
        bpy.data.node_groups["Roughness"].nodes["ColorRamp"].color_ramp.elements[1].color = color2 #(0.0253952, 0.0253952, 0.0253952, 1)

def smooth(obs):
    for ob in obs:
        if not ob.type == 'MESH':
            continue
        me = ob.data
        # Smooth shading
        me.polygons.foreach_set("use_smooth", (True,) * len(me.polygons))

def scale():
    obj = bpy.context.object
    dimension = obj.dimensions
    norm = max(dimension)
    obj.dimensions = [dimension[0]/norm, dimension[1]/norm, dimension[2]/norm]

# This function applies all the modification of the surface and of the material
def main(category = 1):
    render = 2
    view = 2
    render_2 = 2
    view_2 = 2
    scale()
    vertex_number = len(bpy.context.object.data.vertices)
    if vertex_number < 10000:
        surface_refinement(bpy.context.selected_objects, render, view)
        surface_refinement(bpy.context.selected_objects, render_2, view_2)
    else:
        smooth(bpy.context.selected_objects)

def loadTree(blendName):
    # Load material trees
    current_directory = os.getcwd()
    blendfile = os.path.join(current_directory, 'monet','input','NodeTrees', blendName+".blend")
    #blendfile = os.path.join(bb, blendName+".blend")
    section   = "NodeTree"

    if blendName == "MaterialNodeTree" or blendName == "MaterialNodeTreeComet":
        object    = "TextureMap"
    elif blendName == "MaterialNodeTreeRocks":
        object = "RockTree"

    filepath  = os.path.join(blendfile, section, object)
    directory = os.path.join(blendfile, section)
    filename  = os.path.join(object)

    bpy.ops.wm.append(
        filepath=filepath,
        filename=filename,
        directory=directory)

############################### MAIN ###########################
################################################################
def clean():
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)
    for block in bpy.data.textures:
        if block.users == 0:
            bpy.data.textures.remove(block)
    for block in bpy.data.images:
        if block.users == 0:
            bpy.data.images.remove(block)
    for block in bpy.data.curves:
        if block.users == 0:
            bpy.data.curves.remove(block)
    for block in bpy.data.lights:
        if block.users == 0:
            bpy.data.lights.remove(block)
    for block in bpy.data.cameras:
        if block.users == 0:
            bpy.data.cameras.remove(block)
    for block in bpy.data.actions:
        if block.users == 0:
            bpy.data.actions.remove(block)
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.object.delete(use_global = False)
    create_collection()

    # Clear loaded node groups
    all_node_groups = bpy.data.node_groups
    for g in all_node_groups:
        if g.use_fake_user == False:
            bpy.data.node_groups.remove(g)
############################################################
############################################################

def run(rock_count, rock_size, rock_count_big, rock_count_medium, rock_size_big, rock_size_medium, body_name, category, blendName, roughLevel, SmallCratersNum, BigCratersNum, color1, color2, pathObj = False, outputFolder = False):
    clean()

    loadTree("MaterialNodeTreeRocks")
    loadTree(blendName)

    if pathObj == False:
        current_directory = os.getcwd()
        path = bpy.path.abspath(os.path.join(current_directory,"monet","input","obj", body_name+".obj"))
        #path = bpy.path.abspath("//input\\"+body_name+".obj")
    else:
        path = pathObj

    if outputFolder == False:
        outputFolder = "BlendFiles"
        #path = bpy.path.abspath("//input\\"+body_name+".obj")

    # category = 1 --> asteroid with big boulders and a lot of them
    # category = 2 --> asteroid with rough and smooth surface
    #category = 2
    # Model loading
    full_path_to_file = path

    print(path)

    bpy.ops.wm.obj_import(filepath=path)
    # Changing the name of the loaded model
    bpy.context.selected_objects[0].name = 'asteroid'
    bpy.context.selected_objects[0].data.name = 'asteroid'
    bpy.context.selected_objects[0].pass_index = 1
    # Select the model
    element_selection("asteroid")
    rock_random_size = 1 # Set to the maximum value
    # Parameters initialization
    #rock_count, rock_size, rock_count_big, rock_count_medium, rock_size_big, rock_size_medium  = initialization(category)
    # Modification of the minor body surface
    main(category)

    element_selection("asteroid")

    # Ensure there is an active object
    if bpy.context.object is not None:
        obj = bpy.context.object
    
        # Ensure the active object has an active material
        if obj.active_material is not None:
            print(f"Renamed material")
        else:
            print("The active object does not have an active material.")
            # Create a new material
            new_material = bpy.data.materials.new(name="prova")
        
            # Assign the new material to the active object
            if len(obj.data.materials):
                # If the object has material slots, replace the first one
                obj.data.materials[0] = new_material
            else:
                # If the object has no material slots, add a new one
                obj.data.materials.append(new_material)

            # Enable 'Use nodes'
        new_material.use_nodes = True
    else:
        print("There is no active object.")

    astMaterial(roughLevel, SmallCratersNum, BigCratersNum, color1, color2)

    # Generation of boulders thanks to the particle system
    rock_generation(rock_count, rock_size, rock_random_size, 'Rocks_small')
    rock_generation(rock_count_big, rock_size_big, rock_random_size, 'Rocks_big')
    rock_generation(rock_count_medium, rock_size_medium, rock_random_size, 'Rocks_medium')
    
    # Exclution of the Rocks collection to avoid their rendering
    bpy.data.collections['Rocks_small'].hide_render = True
    bpy.data.collections['Rocks_big'].hide_render = True
    bpy.data.collections['Rocks_medium'].hide_render = True   

    # Get the current blend file path
    current_file =os.getcwd() # bpy.data.filepath
    current_file = os.path.join(current_file,'monet', 'blendFile.blend')

    print(40*"#")
    print(current_file)
    print(40*"#")

    # Set the new file name
    new_file_name = body_name+".blend"

    # Get the directory of the current blend file
    directory = os.path.join(os.path.dirname(current_file), outputFolder)

    # Construct the new file path
    new_file_path = os.path.join(directory, new_file_name)

    # Save the current file with a new name
    bpy.ops.wm.save_as_mainfile(filepath=new_file_path)


# Parameters initialization
if __name__ == "__main__":
    rock_count, rock_size, rock_count_big, rock_count_medium, rock_size_big, rock_size_medium, body_name, category, blendName, roughLevel, SmallCratersNum, BigCratersNum, color1, color2 = initialization()
    run(rock_count, rock_size, rock_count_big, rock_count_medium, rock_size_big, rock_size_medium, body_name, category, blendName, roughLevel, SmallCratersNum, BigCratersNum, color1, color2)

    data = []
    vec = [rock_count, rock_count_medium, rock_count_big, roughLevel, SmallCratersNum, BigCratersNum]
    data.append(vec)

    matrix_string = ""
    for row in data:
        row_string = ", ".join(map(str, row))
        matrix_string += row_string + "\n"

    # Write the matrix to a text file
    file_path = 'matrix_output.txt'
    with open(file_path, 'w') as file:
        file.writelines(matrix_string)
