
from __future__ import annotations
from typing import (Any, List, Mapping, Optional, Tuple, Union, overload)

import bpy 
import os
from cortopy import Rendering
from cortopy import State
class Compositing:
    """
    Compositing class
    """
    # *************************************************************************
    # *     Constructors & Destructors
    # *************************************************************************

    def __init__(self) -> None:
        """
        Constructor for the compositing class
        """
    # Istance methods
    def create_compositing():
        """Creata a new empty compositing

        Returns:
            tree (bpy.context.scene.node_tree): compositing tree
        """
        # Enable compositing
        bpy.context.scene.use_nodes = True
        # Get the node tree
        tree = bpy.context.scene.node_tree
        # Clear any existing nodes
        for node in tree.nodes:
            tree.nodes.remove(node)
        return tree
    
    def create_simple_compositing(tree):
        """ method to create a very simple rendering tree in the compositing

        Args:
            tree (bpy.context.scene.node_tree): empty tree to build the simple compositing on
        """
        # Create Render  node
        render_node = Compositing.rendering_node(tree, (0,0))
        # Create Composite node
        composite_node = Compositing.composite_node(tree, (800,0))
        # Create a viewer node
        viewer_node = Compositing.viewer_node(tree,(400,-200))
        # Create gamma  node
        gamma_node = Compositing.gamma_node(tree,(400,0))
        # Link nodes toghether
        Compositing.link_nodes(tree, render_node.outputs["Image"], gamma_node.inputs["Image"])
        Compositing.link_nodes(tree, gamma_node.outputs["Image"], composite_node.inputs["Image"])
        Compositing.link_nodes(tree, render_node.outputs["Image"], viewer_node.inputs["Image"])

    def composite_node(tree, location=(0, 0)):
        """method to create a compositor node

        Args:
            tree (bpy.context.scene.node_tree): compositing tree in which the node is generated
            location (node.location, optional): location in the node tree. Defaults to (0, 0).

        Returns:
            node: node in the shading tree
        """ 
        return Compositing.create_node('CompositorNodeComposite', tree, location)
    
    def rendering_node(tree, location=(0, 0)):
        """method to create a rendering node

        Args:
            tree (bpy.context.scene.node_tree): compositing tree in which the node is generated
            location (node.location, optional): location in the node tree. Defaults to (0, 0).

        Returns:
            node: node in the shading tree
        """ 
        return Compositing.create_node('CompositorNodeRLayers', tree, location)

    def viewer_node(tree, location = (0,0)):
        """method to create a viewer node

        Args:
            tree (bpy.context.scene.node_tree): compositing tree in which the node is generated
            location (node.location, optional): location in the node tree. Defaults to (0, 0).

        Returns:
            node: node in the shading tree
        """ 
        return Compositing.create_node('CompositorNodeViewer', tree, location)
    
    def gamma_node(tree,location = (0,0)):
        """method to create a gamma correction node

        Args:
            tree (bpy.context.scene.node_tree): compositing tree in which the node is generated
            location (node.location, optional): location in the node tree. Defaults to (0, 0).

        Returns:
            node: node in the shading tree
        """ 
        return Compositing.create_node('CompositorNodeGamma', tree, location)

    def file_output_node(tree, location = (0,0)):
        """method to create a file output node

        Args:
            tree (bpy.context.scene.node_tree): compositing tree in which the node is generated
            location (node.location, optional): location in the node tree. Defaults to (0, 0).

        Returns:
            node: node in the shading tree
        """ 
        return Compositing.create_node('CompositorNodeOutputFile', tree, location)

    def denoise_node(tree,location = (0,0)):
        """method to create a denoise node

        Args:
            tree (bpy.context.scene.node_tree): compositing tree in which the node is generated
            location (node.location, optional): location in the node tree. Defaults to (0, 0).

        Returns:
            node: node in the shading tree
        """ 
        Rendering.activate_denoise_data()
        return Compositing.create_node('CompositorNodeDenoise', tree, location)
    
    def maskID_node(tree, location = (0,0)): 
        """method to create a ID mask node

        Args:
            tree (bpy.context.scene.node_tree): compositing tree in which the node is generated
            location (node.location, optional): location in the node tree. Defaults to (0, 0).

        Returns:
            node: node in the shading tree
        """ 
        Rendering.activate_id_mask()
        Rendering.activate_pass_shadow()
        Rendering.activate_pass_diffuse_direct()
        return Compositing.create_node('CompositorNodeIDMask', tree, location)

    def depth_node(tree, location = (0,0)):
        """method to create a depth node

        Args:
            tree (bpy.context.scene.node_tree): compositing tree in which the node is generated
            location (node.location, optional): location in the node tree. Defaults to (0, 0).

        Returns:
            node: node in the shading tree
        """ 
        Rendering.activate_depth_pass()
        return Compositing.file_output_node(tree, location)

    def normal_node(tree,location = (0,0)):
        """method to create a normal node

        Args:
            tree (bpy.context.scene.node_tree): compositing tree in which the node is generated
            location (node.location, optional): location in the node tree. Defaults to (0, 0).

        Returns:
            node: node in the shading tree
        """ 
        Rendering.activate_pass_normal()
        return Compositing.create_node('CompositorNodeOutputFile', tree, location)

    def math_node(tree,location = (0,0)):
        """method to create a math node

        Args:
            tree (bpy.context.scene.node_tree): compositing tree in which the node is generated
            location (node.location, optional): location in the node tree. Defaults to (0, 0).

        Returns:
            node: node in the shading tree
        """ 
        return Compositing.create_node('CompositorNodeMath', tree, location)
    
    def create_node(name:str, tree, location = (0,0)):
        """method to create a generic node

        Args:
            name (str): name of the node
            tree (bpy.context.scene.node_tree): compositing tree in which the node is generated
            location (node.location, optional): location in the node tree. Defaults to (0, 0).

        Returns:
            node: node in the shading tree
        """ 
        node = tree.nodes.new(type=name)
        node.location = (location)
        return node

    def link_nodes(tree,node_output,node_input):
        """Generic method to link two nodes toghether

        Args:
            tree (bpy.context.scene.node_tree): compositing tree in which the node is generated
            node_output (tree.nodes): value from output node 
            node_input (tree.nodes): value from input node  
        """          
        tree.links.new(node_output,node_input)

    def create_img_denoise_branch(tree,render_node):
        """method to create a simple image denoise tree

        Args:
            tree (Compositing.tree): tree
            render_node (Compositing.node): render node to link 
        """
        # Create a denoise node
        denoise_node = Compositing.denoise_node(tree,(400,0))
        # Create a gamma node
        gamma_node = Compositing.gamma_node(tree,(600,0))
        # Create Composite node
        composite_node = Compositing.composite_node(tree,(800,0))
        # Denoised image branch
        Compositing.link_nodes(tree, render_node.outputs["Noisy Image"], denoise_node.inputs["Image"])
        Compositing.link_nodes(tree, denoise_node.outputs["Image"], gamma_node.inputs["Image"])
        Compositing.link_nodes(tree, gamma_node.outputs["Image"], composite_node.inputs["Image"])

    def create_img_branch(tree,render_node, state:State):
        """method to create a simple image tree (for EEVEE)

        Args:
            tree (Compositing.tree): tree
            render_node (Compositing.node): render node to link 
        """
        # Create Composite node
        composite_node = Compositing.composite_node(tree,(800,0))
        # Link nodes toghether
        Compositing.link_nodes(tree, render_node.outputs["Image"], composite_node.inputs["Image"])

    def create_depth_branch(tree,render_node,state:State):
        """method to create a simple depth tree 

        Args:
            tree (Compositing.tree): tree
            render_node (Compositing.node): render node to link 
        """
        # Create a depth node
        depth_node = Compositing.depth_node(tree,(400,200))
        depth_node.name = 'OpenEXR Depth'
        depth_node.format.file_format = 'OPEN_EXR'  # Set file format to OpenEXR
        depth_node.format.color_mode = 'RGBA'  
        depth_node.format.color_depth = '32'  # Use 32-bit float precision
        depth_node.base_path = os.path.join(state.path["output_path"], "depth_exr")
        depth_node.file_slots[0].path = "######"  # Filename pattern
        # Depth branch
        Compositing.link_nodes(tree, render_node.outputs["Depth"], depth_node.inputs["Image"])

    def create_slopes_branch(tree,render_node,state:State):
        """method to create a slopes tree

        Args:
            tree (Compositing.tree): tree
            render_node (Compositing.node): render node to link 
            state (corto.State): corto state, for path handling
        """
        # Create an output node
        normal_node = Compositing.normal_node(tree,(400,-200))
        normal_node.format.color_depth = '16'
        normal_node.base_path = os.path.join(state.path["output_path"])
        normal_node.file_slots[0].path = "\slopes\######"
        # Normal branch 
        Compositing.link_nodes(tree, render_node.outputs["Normal"], normal_node.inputs["Image"])

    def create_maskID_branch(tree,render_node,state:State):
        """method to create a ID mask tree

        Args:
            tree (Compositing.tree): tree
            render_node (Compositing.node): render node to link 
            state (corto.State): corto state, for path handling
        """
        maskID_node = Compositing.maskID_node(tree,(200,-400))
        index = 1 #TODO: This is hard-coded now, link it with BODY properties
        maskID_node.index = index
        math_node = Compositing.math_node(tree,(400,-400))
        math_node.operation = 'SIGN'
        output_node_1 = Compositing.file_output_node(tree,(600,-400))
        output_node_1.format.color_mode = 'BW'
        output_node_1.format.color_depth = '8'
        output_node_1.base_path = os.path.join(state.path["output_path"])
        output_node_1.file_slots[0].path = "\mask_ID_shadow_" + str(index) + "\######"
        output_node_2 = Compositing.file_output_node(tree,(600,-400))
        output_node_2.format.color_mode = 'BW'
        output_node_2.format.color_depth = '8'
        output_node_2.base_path = os.path.join(state.path["output_path"])
        output_node_2.file_slots[0].path = "\mask_ID_" + str(index) + "\######"
        Compositing.link_nodes(tree, render_node.outputs["DiffDir"], math_node.inputs[0])
        Compositing.link_nodes(tree, math_node.outputs["Value"], output_node_1.inputs[0])
        Compositing.link_nodes(tree, render_node.outputs["IndexOB"], maskID_node.inputs["ID value"])
        Compositing.link_nodes(tree, maskID_node.outputs["Alpha"], output_node_2.inputs[0])

    def create_lunar_tile_labels(tree,render_node, state:State):
        """method to create a lunar tile tree

        Args:
            tree (Compositing.tree): tree
            render_node (Compositing.node): render node to link 
            state (corto.State): corto state, for path handling
        """

        # Step 2: Enable UV Pass in Rendering
        # Enable UV pass on the active view layer
        bpy.context.view_layer.use_pass_uv = True  # Ensure UV pass is enabled for the active view layer
        Rendering.activate_depth_pass()

        # Step 3: Add Crater Mask Input Node
        latlon_mask_node = Compositing.create_node("CompositorNodeImage", tree, (-400, 350))
        latlon_mask_node.image = bpy.data.images.load(state.path["LatLonMask_path"])  # Load crater mask image

        # Step 3: Add Crater Mask Input Node
        crater_mask_node = Compositing.create_node("CompositorNodeImage", tree, (-400, 0))
        crater_mask_node.image = bpy.data.images.load(state.path["CraterMask_path"])  # Load crater mask image
        #crater_mask_node.colorspace_settings.name = 'Non-Color'

        value_node1 = Compositing.create_node("CompositorNodeValue", tree, (-400, -400))
        value_node1.outputs[0].default_value = 20

        value_node2 = Compositing.create_node("CompositorNodeValue", tree, (-400, -500))

        divide_node = Compositing.math_node(tree, (-250,-350))
        divide_node.operation = 'DIVIDE'

        value_node3 = Compositing.create_node("CompositorNodeValue", tree, (-250, -500))
        value_node3.outputs[0].default_value = 0.01

        multiply_node = Compositing.math_node(tree, (-50,-400))
        multiply_node.operation = 'MULTIPLY'

        # Step 4: Add Map UV Node
        map_uv_node = Compositing.create_node("CompositorNodeMapUV", tree, (-200, 0))
        map_uv_node2 = Compositing.create_node("CompositorNodeMapUV", tree, (-200, 350))
        map_uv_node2.filter_type = 'NEAREST'

        compare_node = Compositing.math_node(tree, (-50,200))
        compare_node.operation = 'GREATER_THAN'
        #compare_node.inputs[1].default_value = 0.01

        # Step 5: Add Map to mask
        add_node = Compositing.create_node("CompositorNodeMixRGB", tree, (100, 200))
        add_node.blend_type = 'ADD'

        # Step 6: Add File Output Node
        output_node = Compositing.file_output_node(tree, (400, 0))
        output_node.format.color_mode = 'BW' 
        output_node.format.color_depth = '8'  # Use 8-bit 
        output_node.base_path = os.path.join(state.path["output_path"], "crater_masks_png")
        output_node.file_slots[0].path = "######"

        output_node2 = Compositing.file_output_node(tree, (400, -200))
        output_node2.format.file_format = 'OPEN_EXR'  # Set file format to OpenEXR
        output_node2.format.color_mode = 'RGBA'  # Use Black & White (single channel)
        output_node2.format.color_depth = '32'  # Use 32-bit float precision
        output_node2.base_path = os.path.join(state.path["output_path"], "depth_exr")
        output_node2.file_slots[0].path = "######"  # Filename pattern

        output_node3 = Compositing.file_output_node(tree, (400, 200))
        output_node3.format.file_format = 'OPEN_EXR'  # Set file format to OpenEXR
        output_node3.format.color_mode = 'RGBA'  # Use Black & White (single channel)
        output_node3.format.color_depth = '32'  # Use 32-bit float precision
        output_node3.base_path = os.path.join(state.path["output_path"], "lat_lon_exr")
        output_node3.file_slots[0].path = "######"  # Filename pattern

        # Step 7: Link Nodes
        Compositing.link_nodes(tree, render_node.outputs["UV"], map_uv_node.inputs["UV"])  # Link UV output to Map UV
        Compositing.link_nodes(tree, crater_mask_node.outputs["Image"], map_uv_node.inputs["Image"])  # Link crater mask to Map UV
        Compositing.link_nodes(tree, map_uv_node.outputs["Image"], compare_node.inputs[0])  
        Compositing.link_nodes(tree, value_node1.outputs[0], divide_node.inputs[0])
        Compositing.link_nodes(tree, value_node2.outputs[0], divide_node.inputs[1])
        Compositing.link_nodes(tree, divide_node.outputs[0], multiply_node.inputs[0])
        Compositing.link_nodes(tree, value_node3.outputs[0], multiply_node.inputs[1])
        Compositing.link_nodes(tree, multiply_node.outputs[0], compare_node.inputs[1])
        Compositing.link_nodes(tree, compare_node.outputs["Value"], add_node.inputs[1])  
        Compositing.link_nodes(tree, render_node.outputs["Image"], add_node.inputs[2])
        Compositing.link_nodes(tree, add_node.outputs["Image"], output_node.inputs[0])
        Compositing.link_nodes(tree, render_node.outputs["Depth"], output_node2.inputs[0])
        Compositing.link_nodes(tree, render_node.outputs["UV"], map_uv_node2.inputs["UV"])  # Link UV output to Map UV
        Compositing.link_nodes(tree, latlon_mask_node.outputs["Image"], map_uv_node2.inputs["Image"])  # Link crater mask to Map UV
        Compositing.link_nodes(tree, map_uv_node2.outputs["Image"], output_node3.inputs[0])     

