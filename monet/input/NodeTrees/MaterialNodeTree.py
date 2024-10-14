import bpy
import random

# Parameters coming from the GUI, in order: path where to save the rendering,
# path of the main body model, binary or not binary asteroid, path of the secondary
# model in case type == binary, name of the body and numner of cameras.
def starting_params():
    import test
    return test.path_to_save, test.path, test.type, test.path_2, test.body_name, test.Camera_num

# Parameter coming from the GUI.
# The flag parameter can assume two possible values 'predefinite' or 'modify'.
# With predefinite the program will run with the suggested parameters, while
# modify allows the user to change the body's surface properties.
def modify():
    import flag
    return flag.flag

# Parameters coming from the GUI.
# They are the parameters defining the surface properties, as number of craters,
# rocks and surface roughness.
def setParams():
    import test
    return test.rock_random_size, \
    test.scale_noise2, test.bump_roughness, test.crater_num, \
    test.crater_3, test.crater_4, test.multiply, test.rock_count, test.rock_size, \
    test.strength, test.scale_noise2_bin, test.bump_roughness_bin, test.crater_num_bin, \
    test.crater_3_bin, test.crater_4_bin, test.multiply_bin, test.rock_count_bin, \
    test.rock_size_bin, test.strength_bin

# This function assigns values to the main variables accordingly to the
# model's dimension.
def initialization(category):
    scale_noise2 = 8.3
    bump_roughness = 0.3
    crater_num = 7
    crater_3 = 0.328
    crater_4 = 0.383
    multiply = 1
    strength = 0.5
    if category == 1:
        rock_size = 0.001
        rock_size_medium = 0.008
        rock_size_big = 0.03
        rock_count = 0 #300000
        rock_count_medium = 0#800
        rock_count_big = 1#random.randint(1,8)
    else:
        rock_size = 0.001
        rock_size_medium = 0.004
        rock_size_big = 0.001
        rock_count = 1000
        rock_count_medium = 100
        rock_count_big = 1
    return scale_noise2, bump_roughness, crater_num, crater_3, crater_4, multiply, rock_count, rock_size, strength, rock_count_big, rock_count_medium, rock_size_big, rock_size_medium

# This function selects and activates the desired object in the scene.
def element_selection(name):
    ob = bpy.context.scene.objects[name]       # Get the object
    bpy.ops.object.select_all(action='DESELECT') # Deselect all objects
    bpy.context.view_layer.objects.active = ob   # Activate the desired object
    ob.select_set(True)                          # Select the desired object

# This function creates a node tree in the Shading Editor in order to generate
# a texture that is the most rocky possible.
def element_material(scale_noise2, bump_roughness, crater_num, crater_3, crater_4, multiply, element_name, category = 1):
    bpy.context.object.active_material.name = "asteroid_material"
    # get the material
    mat = bpy.data.materials['asteroid_material']
    # get the nodes
    nodes = mat.node_tree.nodes
    nodes.clear() # Clear the nodes
    links = mat.node_tree.links
    # First branch
    Noise_node = nodes.new(type='ShaderNodeTexNoise')
    Noise_node.location = (-1000,1000)
    if category == 1:
        Noise_node.inputs[2].default_value = 10 ########################################
    else:
        Noise_node.inputs[2].default_value = 40
    Noise_node.inputs[3].default_value = 8.8 # DA CAMBIARE
    mapping1 = nodes.new(type='ShaderNodeMapping')
    mapping1.location = (-1300, 0)
    mapping1.inputs[1].default_value[0] = random.randint(0, 1000)
    mapping1.inputs[1].default_value[1] = random.randint(0, 1000)
    mapping1.inputs[1].default_value[2] = random.randint(0, 1000)
    link_map1_noise = links.new(mapping1.outputs[0], Noise_node.inputs[0])
    tex1 = nodes.new(type = 'ShaderNodeTexCoord')
    tex1.location = (-1600, 0)
    link_tex1_map1 = links.new(tex1.outputs[3], mapping1.inputs[0])
    Ramp_node = nodes.new(type='ShaderNodeValToRGB')
    Ramp_node.location = (-450,0)
    Ramp_node.color_ramp.elements[0].position = 0.402      # EVERYTHING TO TUNE
    Ramp_node.color_ramp.elements[0].color = (0.007845,0.007845,0.007845,1)
    Ramp_node.color_ramp.elements[1].position = 0.811
    Ramp_node.color_ramp.elements[1].color = (0.023765,0.023765,0.023765,1)
    Ramp_node.inputs[0].default_value = 0.5 # NOT TO CHANGE
    Shade2RGB_node = nodes.new(type='ShaderNodeShaderToRGB')
    Shade2RGB_node.location = (1000, 0)
    link_noise_ramp = links.new(Noise_node.outputs[1], Ramp_node.inputs[0])
    link_ramp_RGB = links.new(Ramp_node.outputs[0], Shade2RGB_node.inputs[0])
    if element_name != 'rock':
        math0 = nodes.new(type='ShaderNodeMath')
        math0.location = (-800, -100)
        math0.operation = 'MULTIPLY'
        if category == 1:
            link_noise_mat0 = links.new(Noise_node.outputs[1], math0.inputs[0])
    else:
        bump_node = nodes.new(type = 'ShaderNodeBump')
        bump_node.location = (-100, -300)
        bump_node.inputs[0].default_value = 1.5
        bump_node.inputs[1].default_value = 7.5
        link_ramp_RGB = links.new(Ramp_node.outputs[0], bump_node.inputs[2])

        VectorOut_node = nodes.new(type = 'ShaderNodeVectorMath')
        VectorOut_node.location = (300,-300)
        link_bump_Vector = links.new(bump_node.outputs[0], VectorOut_node.inputs[0])

    # Integration for second category (alternation of smooth and rough regions) #################
    if category == 2:
        musgrave_node = nodes.new(type='ShaderNodeTexMusgrave')
        musgrave_node.inputs[2].default_value = 2
        musgrave_node.location = (-1000,1500)
        link_map1_mus = links.new(mapping1.outputs[0], musgrave_node.inputs[0])
        Noise_node_c21 = nodes.new(type='ShaderNodeTexNoise')
        Noise_node_c21.location = (-1000,500)
        Noise_node_c21.inputs[2].default_value = 40 ########################################
        Noise_node_c21.inputs[3].default_value = 8.8 # DA CAMBIARE
        link_map1_noisec21 = links.new(mapping1.outputs[0], Noise_node_c21.inputs[0])
        Noise_node_c22 = nodes.new(type='ShaderNodeTexNoise')
        Noise_node_c22.location = (-1000,0)
        Noise_node_c22.inputs[2].default_value = 40 ########################################
        Noise_node_c22.inputs[3].default_value = 8.8 # DA CAMBIARE
        link_map1_noisec22 = links.new(mapping1.outputs[0], Noise_node_c22.inputs[0])
        Mix_node_c21 = nodes.new(type = 'ShaderNodeMixRGB')
        Mix_node_c21.location = (-200, 750)
        Mix_node_c21.inputs[0].default_value = 1
        Mix_node_c21.blend_type = 'MULTIPLY'
        link_nc21_mix = links.new(Noise_node.outputs[0], Mix_node_c21.inputs[1])
        link_nc22_mix = links.new(Noise_node_c21.outputs[0], Mix_node_c21.inputs[2])
        Mix_node_c22 = nodes.new(type = 'ShaderNodeMixRGB')
        Mix_node_c22.location = (0, 250)
        Mix_node_c22.inputs[0].default_value = 1
        Mix_node_c22.blend_type = 'MULTIPLY'
        link_mix_mix = links.new(Mix_node_c21.outputs[0], Mix_node_c22.inputs[1])
        link_nc22_mix = links.new(Noise_node_c22.outputs[0], Mix_node_c22.inputs[2])
        Mix_node_c23 = nodes.new(type = 'ShaderNodeMixRGB')
        Mix_node_c23.location = (500, 750)
        Mix_node_c23.inputs[0].default_value = 1
        Mix_node_c23.blend_type = 'MULTIPLY'
        link_mus_mix = links.new(musgrave_node.outputs[0], Mix_node_c23.inputs[1])
        link_mix_mix2 = links.new(Mix_node_c22.outputs[0], Mix_node_c23.inputs[2])
        link_mix_mat0 = links.new(Mix_node_c23.outputs[0], math0.inputs[0])
    ################################################################################
    if element_name != 'rock':
        #Second branch
        Voronoi_node = nodes.new(type='ShaderNodeTexVoronoi')
        Voronoi_node.location = (-1000,-400)
        Voronoi_node.feature = 'SMOOTH_F1'
        Voronoi_node.inputs[2].default_value = 5
        Ramp_node2 = nodes.new(type='ShaderNodeValToRGB')
        Ramp_node2.location = (-700,-400)
        Ramp_node2.color_ramp.elements[0].position = 0.268 #0.243 reduce plastic
        Ramp_node2.color_ramp.elements[0].color = (1,1,1,1)
        Ramp_node2.color_ramp.elements[1].position = 0.333 #0.322 reduce plastic
        Ramp_node2.color_ramp.elements[1].color = (0.0648745, 0.0648745, 0.0648745, 1) #(0.0441528,0.0441528,0.0441528,1)
        Ramp_node2.color_ramp.elements.new(1)#(0.428)
        Ramp_node2.color_ramp.elements[2].color = (1,1,1,1)
        Ramp_node2.inputs[0].default_value = 0.5
        link_voronoi_ramp = links.new(Voronoi_node.outputs[1], Ramp_node2.inputs[0])
        Noise_node2 = nodes.new(type='ShaderNodeTexNoise')
        Noise_node2.location = (-1300,-400)
        Noise_node2.inputs[2].default_value = scale_noise2
        Noise_node2.inputs[3].default_value = 16
        mapping2 = nodes.new(type='ShaderNodeMapping')
        mapping2.location = (-1600, -400)
        mapping2.inputs[1].default_value[0] = random.randint(0, 1000)
        mapping2.inputs[1].default_value[1] = random.randint(0, 1000)
        mapping2.inputs[1].default_value[2] = random.randint(0, 1000)
        link_map2_noise = links.new(mapping2.outputs[0], Noise_node2.inputs[0])
        tex2 = nodes.new(type = 'ShaderNodeTexCoord')
        tex2.location = (-1900, -400)
        link_tex2_map2 = links.new(tex2.outputs[3], mapping2.inputs[0])
        link_noise_voronoi = links.new(Noise_node2.outputs["Color"],Voronoi_node.inputs["Scale"])
    # Third branch
# Small Craters
        small_hole_scale = 20
        #value2 = nodes.new(type = 'ShaderNodeValue')
        #value2.outputs[0].default_value = 0.5
        #value2.location = (-2000, -1200)
        #voronoi2 = nodes.new(type='ShaderNodeTexVoronoi')
        #voronoi2.inputs[2].default_value = small_hole_scale
        #voronoi2.location = (-1800,-800)
        voronoi3 = nodes.new(type='ShaderNodeTexVoronoi')
        voronoi3.inputs[2].default_value = 8
        voronoi3.location = (-1800,-1200)
        mapping3 = nodes.new(type='ShaderNodeMapping')
        mapping3.location = (-2000, -1200)
        mapping3.inputs[1].default_value[0] = random.randint(0, 1000)
        mapping3.inputs[1].default_value[1] = random.randint(0, 1000)
        mapping3.inputs[1].default_value[2] = random.randint(0, 1000)
        link_map3_vor3 = links.new(mapping3.outputs[0], voronoi3.inputs[0])
        tex3 = nodes.new(type = 'ShaderNodeTexCoord')
        tex3.location = (-2200, -1200)
        link_tex3_map3 = links.new(tex3.outputs[3], mapping3.inputs[0])
        #math1 = nodes.new(type='ShaderNodeMath')
        #math1.location = (-1600, -800)
        #math1.operation = 'LESS_THAN'
        #link_vor2_mat1 = links.new(voronoi2.outputs[1], math1.inputs[0])
        #link_val2_mat1 = links.new(value2.outputs[0], math1.inputs[1])
        math2 = nodes.new(type='ShaderNodeMath')
        math2.location = (-1600, -1200)
        math2.operation = 'MULTIPLY'
        link_vor3_mat2 = links.new(voronoi3.outputs[0], math2.inputs[0])
        link_vor3_mat2 = links.new(voronoi3.outputs[0], math2.inputs[1])
        Ramp_node3 = nodes.new(type='ShaderNodeValToRGB')
        Ramp_node3.location = (-1100,-1000)
        Ramp_node3.color_ramp.elements[0].position = 0
        Ramp_node3.color_ramp.elements[0].color = (0,0,0,1)
        Ramp_node3.color_ramp.elements[1].position = 0.092
        Ramp_node3.color_ramp.elements[1].color = (1,1,1,1)
        Ramp_node3.color_ramp.interpolation = 'LINEAR'
        link_mat2_ramp3 = links.new(math2.outputs[0], Ramp_node3.inputs[0])
        Mix_node3 = nodes.new(type = 'ShaderNodeMixRGB')
        Mix_node3.location = (-800, -1000)
        Mix_node3.inputs[1].default_value = (1,1,1,1)
        Mix_node3.inputs[0].default_value = 0
        link_ramp3_mix3 = links.new(Ramp_node3.outputs[0], Mix_node3.inputs[1])
        Mix_node4 = nodes.new(type = 'ShaderNodeMixRGB')
        Mix_node4.location = (-500, -1000)
        if category == 1:
            Mix_node4.inputs[0].default_value = 0.1
        else:
            Mix_node4.inputs[0].default_value = 0
        Mix_node4.blend_type = 'SUBTRACT'
        Mix_node5 = nodes.new(type = 'ShaderNodeMixRGB')
        Mix_node5.location = (-200, -1000)
        Mix_node5.inputs[0].default_value = 0.5
        Mix_node5.blend_type = 'SUBTRACT'
        Mix_node6 = nodes.new(type = 'ShaderNodeMixRGB')
        Mix_node6.location = (100, -1000)
        Mix_node6.inputs[0].default_value = 1
        Mix_node6.blend_type = 'MULTIPLY'
        Mix_node7 = nodes.new(type = 'ShaderNodeMixRGB')
        Mix_node7.location = (400, -1000)
        Mix_node7.inputs[0].default_value = 1
        Mix_node7.blend_type = 'MULTIPLY'
        link_mix3_mix4 = links.new(Mix_node3.outputs[0], Mix_node4.inputs[2])
        link_mix3_mix5 = links.new(Mix_node3.outputs[0], Mix_node5.inputs[2])
        link_mix3_mix7 = links.new(Mix_node3.outputs[0], Mix_node7.inputs[2])
        link_mix4_mix6 = links.new(Mix_node4.outputs[0], Mix_node6.inputs[2])
        link_mat0_mix4 = links.new(math0.outputs[0], Mix_node4.inputs[1])
        link_ramp2_mix5 = links.new(Ramp_node2.outputs[0], Mix_node5.inputs[1])
        link_mix5_mix6 = links.new(Mix_node5.outputs[0], Mix_node6.inputs[1])
        link_mix6_mix7 = links.new(Mix_node6.outputs[0], Mix_node7.inputs[1])
# BIG CRATERS
        large_hole_scale = 7
        #value2 = nodes.new(type = 'ShaderNodeValue')
        #value2.outputs[0].default_value = 0.45
        #value2.location = (-2000, -2200)
        #voronoi2 = nodes.new(type='ShaderNodeTexVoronoi')
        #voronoi2.inputs[2].default_value = large_hole_scale
        #voronoi2.location = (-1800,-1800)
        voronoi3 = nodes.new(type='ShaderNodeTexVoronoi')
        voronoi3.inputs[2].default_value = 4
        voronoi3.location = (-1800,-2200)
        mapping31 = nodes.new(type='ShaderNodeMapping')
        mapping31.location = (-2000, -2200)
        mapping31.inputs[1].default_value[0] = random.randint(0, 1000)
        mapping31.inputs[1].default_value[1] = random.randint(0, 1000)
        mapping31.inputs[1].default_value[2] = random.randint(0, 1000)
        link_map31_vor3 = links.new(mapping31.outputs[0], voronoi3.inputs[0])
        tex31 = nodes.new(type = 'ShaderNodeTexCoord')
        tex31.location = (-2200, -2200)
        link_tex31_map3 = links.new(tex31.outputs[3], mapping31.inputs[0])
        #math1 = nodes.new(type='ShaderNodeMath')
        #math1.location = (-1600, -1800)
        #math1.operation = 'LESS_THAN'
        #link_vor2_mat1 = links.new(voronoi2.outputs[1], math1.inputs[0])
        #link_val2_mat1 = links.new(value2.outputs[0], math1.inputs[1])
        math2 = nodes.new(type='ShaderNodeMath')
        math2.location = (-1600, -2200)
        math2.operation = 'MULTIPLY'
        link_vor3_mat2 = links.new(voronoi3.outputs[0], math2.inputs[0])
        link_vor3_mat2 = links.new(voronoi3.outputs[0], math2.inputs[1])
        Ramp_node3 = nodes.new(type='ShaderNodeValToRGB')
        Ramp_node3.location = (-1100,-2000)
        Ramp_node3.color_ramp.elements[0].position = 0.083
        Ramp_node3.color_ramp.elements[0].color = (0,0,0,1)
        Ramp_node3.color_ramp.elements[1].position = 0.161
        Ramp_node3.color_ramp.elements[1].color = (1,1,1,1)
        Ramp_node3.color_ramp.interpolation = 'B_SPLINE'
        link_mat2_ramp3 = links.new(math2.outputs[0], Ramp_node3.inputs[0])
        Mix_node31 = nodes.new(type = 'ShaderNodeMixRGB')
        Mix_node31.location = (-800, -2000)
        Mix_node31.inputs[1].default_value = (1,1,1,1)
        Mix_node31.inputs[0].default_value = 0
        link_ramp3_mix3 = links.new(Ramp_node3.outputs[0], Mix_node31.inputs[1])
        Mix_node41 = nodes.new(type = 'ShaderNodeMixRGB')
        Mix_node41.location = (-500, -2000)
        if category == 1:
            Mix_node41.inputs[0].default_value = 0.1
        else:
            Mix_node41.inputs[0].default_value = 0
        Mix_node41.blend_type = 'SUBTRACT'
        Mix_node51 = nodes.new(type = 'ShaderNodeMixRGB')
        Mix_node51.location = (-200, -2000)
        Mix_node51.inputs[0].default_value = 0.5
        Mix_node51.blend_type = 'SUBTRACT'
        Mix_node61 = nodes.new(type = 'ShaderNodeMixRGB')
        Mix_node61.location = (100, -2000)
        Mix_node61.inputs[0].default_value = 1
        Mix_node61.blend_type = 'MULTIPLY'
        Mix_node71 = nodes.new(type = 'ShaderNodeMixRGB')
        Mix_node71.location = (400, -2000)
        Mix_node71.inputs[0].default_value = 1
        Mix_node71.blend_type = 'MULTIPLY'
        link_mix3_mix4 = links.new(Mix_node31.outputs[0], Mix_node41.inputs[2])
        link_mix3_mix5 = links.new(Mix_node31.outputs[0], Mix_node51.inputs[2])
        link_mix3_mix7 = links.new(Mix_node31.outputs[0], Mix_node71.inputs[2])
        link_mix4_mix6 = links.new(Mix_node41.outputs[0], Mix_node61.inputs[2])
        link_mat0_mix4 = links.new(math0.outputs[0], Mix_node41.inputs[1])
        link_ramp2_mix5 = links.new(Ramp_node2.outputs[0], Mix_node51.inputs[1])
        link_mix5_mix6 = links.new(Mix_node51.outputs[0], Mix_node61.inputs[1])
        link_mix6_mix7 = links.new(Mix_node61.outputs[0], Mix_node71.inputs[1])
        Mix_node8 = nodes.new(type = 'ShaderNodeMixRGB')
        Mix_node8.location = (700, -1300)
        Mix_node8.inputs[0].default_value = 0.5
        Mix_node8.blend_type = 'MIX'
        Mix_node9 = nodes.new(type = 'ShaderNodeMixRGB')
        Mix_node9.location = (700, -1700)
        Mix_node9.inputs[0].default_value = 1
        Mix_node9.blend_type = 'ADD'
        link_mix7_mix8 = links.new(Mix_node7.outputs[0], Mix_node8.inputs[1])
        link_mix71_mix8 = links.new(Mix_node71.outputs[0], Mix_node8.inputs[2])
        link_mix3_mix9 = links.new(Mix_node3.outputs[0], Mix_node9.inputs[1])
        link_mix31_mix9 = links.new(Mix_node31.outputs[0], Mix_node9.inputs[2])
        Bump_node = nodes.new(type = 'ShaderNodeBump')
        Bump_node.location = (800,-1000)
        if element_name == 'rock':
            Bump_node.inputs[0].default_value = 0.58
        else:
            Bump_node.inputs[0].default_value = 1
        Bump_node.inputs[1].default_value = bump_roughness
        link_mix8_bump = links.new(Mix_node8.outputs[0], Bump_node.inputs[2])
        Vector1_node = nodes.new(type = 'ShaderNodeVectorMath')
        Vector1_node.location = (2000,-200)
        link_bump_Vector1 = links.new(Bump_node.outputs[0], Vector1_node.inputs[0])
        rgb2bw = nodes.new(type = 'ShaderNodeRGBToBW')
        rgb2bw.location = (900, -1700)
        displ = nodes.new(type = 'ShaderNodeDisplacement')
        displ.location = (1000, -1000)
        displ.inputs[2].default_value = 0.001
        Vector2_node = nodes.new(type = 'ShaderNodeVectorMath')
        Vector2_node.location = (2300,-200)
        link_mix9_rgb = links.new(Mix_node9.outputs[0], rgb2bw.inputs[0])
        link_rgb_displ = links.new(rgb2bw.outputs[0], displ.inputs[0])
        link_displ_Vector2 = links.new(displ.outputs[0], Vector2_node.inputs[0])

def deleteAllObjects():
    #Deletes all objects in the current scene
    deleteListObjects = ['MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'HAIR', 'POINTCLOUD', 'VOLUME', 'GPENCIL',
                     'ARMATURE', 'LATTICE', 'EMPTY', 'LIGHT', 'LIGHT_PROBE', 'CAMERA', 'SPEAKER']
    # Select all objects in the scene to be deleted:
    for o in bpy.context.scene.objects:
        for i in deleteListObjects:
            if o.type == i:
                o.select_set(False)
            else:
                o.select_set(True)
    # Deletes all selected objects in the scene:
    bpy.ops.object.delete()

############################### MAIN ###########################
############################################################
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
deleteAllObjects()
#########################################################ààà
############################################################

body_name = 'bennu_good'
path = bpy.path.abspath("//processed\\"+body_name+".obj")
# category = 1 --> asteroid with big boulders and a lot of them
# category = 2 --> asteroid with rough and smooth surface
category = 1
# type = 'ast' --> asteroid material
# type = 'rock' --> rocks material (on the asteroid surface)
type = 'rock'
bpy.ops.object.select_all(action="DESELECT")
# Model loading
full_path_to_file = path
bpy.ops.import_scene.obj(filepath=path)
# Changing the name of the loaded model
bpy.context.selected_objects[0].name = 'asteroid'
bpy.context.selected_objects[0].data.name = 'asteroid'
bpy.context.selected_objects[0].pass_index = 1
# Select the model
element_selection("asteroid")
# Parameters initialization
scale_noise2, bump_roughness, crater_num, crater_3, crater_4, multiply, rock_count, rock_size, strength, rock_count_big, rock_count_medium, rock_size_big, rock_size_medium  = initialization(category)
if type == 'ast':
    element_material(scale_noise2, bump_roughness, crater_num, crater_3, crater_4, multiply, type, category)
else:
    element_material(0,0,0,0,0,0, type)

'''
# Ensure you're in the Shader Editor workspace
for area in bpy.context.screen.areas:
    if area.type == 'NODE_EDITOR' and area.spaces.active.tree_type == 'ShaderNodeTree':
        shader_editor = area
        break
if shader_editor:
    # Deselect all nodes first (optional)
    for node in shader_editor.spaces.active.node_tree.nodes:
        node.select = False
    # Select all nodes in the Shader Editor
    for node in shader_editor.spaces.active.node_tree.nodes:
        node.select = True
    # Create a new group
    bpy.ops.node.new_node_tree(type='ShaderNodeTree')
    new_tree = bpy.context.space_data.node_tree
    # Rename the new tree (optional)
    new_tree.name = "MyShaderGroup"
    # Move the selected nodes to the new tree
    for node in shader_editor.spaces.active.node_tree.nodes:
        if node.select:
            new_node = new_tree.nodes.new(type=node.bl_idname)
            new_node.location = node.location
            new_node.parent = None
            new_node.select = False
            shader_editor.spaces.active.node_tree.nodes.remove(node)
    # Create a ShaderNodeGroup node to represent the new tree
    group_node = shader_editor.spaces.active.node_tree.nodes.new(type='ShaderNodeGroup')
    group_node.node_tree = new_tree
    group_node.location = (0, 0)
'''
