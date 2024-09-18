
from __future__ import annotations

import numpy as np
import bpy 
import mathutils
import os

from typing import (Any, List, Mapping, Optional, Tuple, Union, overload)
from cortopy import Rendering
from cortopy import State

class Compositing:
    """
    Compositing class
    """
    @classmethod
    def exampleClass(cls, arg1: int, arg2: int) -> Tuple[int, int]: # type hinting
        """
        Description of the method

        Args:
            arg 1: description
            arg 2: description

        Raises:
            which kind of exceptions
        
        Returns:
            arg 1: descritpion
            arg 2: description

        See also:
            additional function and modules imported

        """

    @staticmethod # decorator for static methods
    def exampleStatic(arg1: int, arg2: int) -> Tuple[int, int]: # type hinting
        """
        Description of the method

        Args:
            arg 1: description
            arg 2: description

        Raises:
            which kind of exceptions
        
        Returns:
            arg 1: descritpion
            arg 2: description

        See also:
            additional function and modules imported

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
        # Enable compositing
        bpy.context.scene.use_nodes = True
        # Get the node tree
        tree = bpy.context.scene.node_tree
        # Clear any existing nodes
        for node in tree.nodes:
            tree.nodes.remove(node)
        return tree
    
    def create_simple_compositing(tree):
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

    def composite_node(tree, location):
        """Create composite node"""
        return Compositing.create_node('CompositorNodeComposite', tree, location)
    
    def rendering_node(tree, location):
        """Create rendering node"""
        return Compositing.create_node('CompositorNodeRLayers', tree, location)

    def viewer_node(tree, location):
        """Create viewer node"""
        return Compositing.create_node('CompositorNodeViewer', tree, location)
    
    def gamma_node(tree,location, settings = None):
        """Create a gamma-node"""
        return Compositing.create_node('CompositorNodeGamma', tree, location)

    def file_output_node(tree, location, settings = None):
        """Create a file-output node"""
        '''
        n_paths = 3 #TODO: move this into settings
        for ii in range(0,n_paths):
            node.output_file_add_socket()
            node.base_path = str(ii)
        '''
        return Compositing.create_node('CompositorNodeOutputFile', tree, location)

    # Recquires activation of denoise data 
    def denoise_node(tree,location):
        """Create denoise node"""
        Rendering.activate_denoise_data(active = True)
        return Compositing.create_node('CompositorNodeDenoise', tree, location)
    
    # Require activation of ID-mask
    def maskID_node(tree, location): 
        """Create a mask-ID node"""
        Rendering.activate_id_mask(active = True)
        Rendering.activate_pass_shadow(active = True)
        return Compositing.create_node('CompositorNodeIDMask', tree, location)

    # Requires activation of depth-pass
    def depth_node(tree, location):
       """Create a depth-saving node"""
       Rendering.activate_depth_pass(active = True)
       return Compositing.create_node('CompositorNodeViewer', tree, location)

    # Requires activation of normal-pass
    def normal_node(tree,location):
        """Create a depth-saving node"""
        Rendering.activate_pass_normal(active = True)
        return Compositing.create_node('CompositorNodeViewer', tree, location)

    '''
    bpy.ops.node.add_node(use_transform=True, type="CompositorNodeIDMask")
    bpy.data.scenes["Scene"].node_tree.nodes["ID Mask"].inputs[0].default_value = 1
    bpy.data.scenes["Scene"].node_tree.nodes["ID Mask"].index = 1
    '''
    
    def create_node(name:str, tree, location = (0,0)):
        """Create node"""
        node = tree.nodes.new(type=name)
        node.location = (location)
        return node

    def link_nodes(tree,node_output,node_input):
        """Link output from node a to input to node b"""
        tree.links.new(node_output,node_input)

    def create_img_denoise_branch(tree,render_node,state:State):
        """Create branch for image denoise"""
        # Create a denoise node
        denoise_node = Compositing.denoise_node(tree,(400,0))
        # Create a gamma node
        gamma_node = Compositing.gamma_node(tree,(600,0))
        # Create Composite node
        composite_node = Compositing.composite_node(tree,(800,0))
        # Denoised image branch
        Compositing.link_nodes(tree, render_node.outputs["Noisy Image"], denoise_node.inputs["Image"])
        Compositing.link_nodes(tree, render_node.outputs["Normal"], denoise_node.inputs["Normal"])
        Compositing.link_nodes(tree, denoise_node.outputs["Image"], gamma_node.inputs["Image"])
        Compositing.link_nodes(tree, gamma_node.outputs["Image"], composite_node.inputs["Image"])

    def create_depth_branch(tree,render_node,state:State):
        """Create branch for depth label"""
        # Create a depth node
        depth_node = Compositing.depth_node(tree,(400,200))
        depth_node.name = 'Viewer Depth'
        # Depth branch
        Compositing.link_nodes(tree, render_node.outputs["Depth"], depth_node.inputs["Image"])

    def create_slopes_branch(tree,render_node,state:State):
        """Create branch for slopes label"""
        # Create an output node
        output_node = Compositing.file_output_node(tree,(400,-200))
        output_node.format.color_depth = '16'
        output_node.base_path = os.path.join(state.output_path)
        output_node.file_slots[0].path = "\slopes\######"
        # Normal branch 
        Compositing.link_nodes(tree, render_node.outputs["Normal"], output_node.inputs["Image"])
