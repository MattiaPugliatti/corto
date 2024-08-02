
from __future__ import annotations

import numpy as np
import bpy 
import mathutils

from typing import (Any, List, Mapping, Optional, Tuple, Union, overload)
from cortopy import Rendering
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
        composite_node = Compositing.composite_node(tree, (400,0))
        # Create a viewer node
        viewer_node = Compositing.viewer_node(tree,(400,-200))
        # Link nodes toghether
        Compositing.link_nodes(tree, render_node.outputs["Image"], composite_node.inputs["Image"])
        Compositing.link_nodes(tree, render_node.outputs["Image"], viewer_node.inputs["Image"])
        '''
        # Optional: Add a Gamma node to adjust gamma (example of additional node)
        gamma_node = tree.nodes.new(type='CompositorNodeGamma')
        gamma_node.location = (200, 0)
        gamma_node.inputs['Gamma'].default_value = 1.0  # Adjust gamma value
        # Link Gamma node between Render Layers and Composite nodes
        tree.links.new(render_node.outputs['Image'], gamma_node.inputs['Image'])
        tree.links.new(gamma_node.outputs['Image'], composite_node.inputs['Image'])
        tree.links.new(gamma_node.outputs['Image'], viewer_node.inputs['Image'])
        '''

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
        node = Compositing.create_node('CompositorNodeOutputFile', tree, location)
        
        '''
        Debug this
        n_paths = 3 #TODO: move this into settings
        for ii in range(0,n_paths):
            node.output_file_add_socket()
            node.base_path = str(ii)
        '''
        return Compositing.create_node('CompositorNodeOutputFile', tree, location)

    # Recquires activation of denoise data 
    def denoise_node(tree,location):
        """Create denoise node"""
        # Rendering.activate_denoise_data(active = True)
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