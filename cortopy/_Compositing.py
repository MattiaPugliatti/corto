
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
        return Compositing.create_node('CompositorNodeViewer', tree, location)

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

    def create_depth_branch(tree,render_node):
        """method to create a simple depth tree 

        Args:
            tree (Compositing.tree): tree
            render_node (Compositing.node): render node to link 
        """
        # Create a depth node
        depth_node = Compositing.depth_node(tree,(400,200))
        depth_node.name = 'Viewer Depth'
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

