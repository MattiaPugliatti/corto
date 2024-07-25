
from __future__ import annotations

import numpy as np
import bpy 
import mathutils

from typing import (Any, List, Mapping, Optional, Tuple, Union, overload)

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
        Constructor for the shading class
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
        # Create Render Layers node
        render_layers_node = tree.nodes.new(type='CompositorNodeRLayers')
        render_layers_node.location = (0, 0)
        # Create Composite node
        composite_node = tree.nodes.new(type='CompositorNodeComposite')
        composite_node.location = (400, 0)
        # Link Render Layers node to Composite node
        tree.links.new(render_layers_node.outputs['Image'], composite_node.inputs['Image'])
        # Optional: Create and link a Viewer node for preview
        viewer_node = tree.nodes.new(type='CompositorNodeViewer')
        viewer_node.location = (400, -200)
        tree.links.new(render_layers_node.outputs['Image'], viewer_node.inputs['Image'])
        # Optional: Add a Gamma node to adjust gamma (example of additional node)
        gamma_node = tree.nodes.new(type='CompositorNodeGamma')
        gamma_node.location = (200, 0)
        gamma_node.inputs['Gamma'].default_value = 1.2  # Adjust gamma value
        # Link Gamma node between Render Layers and Composite nodes
        tree.links.new(render_layers_node.outputs['Image'], gamma_node.inputs['Image'])
        tree.links.new(gamma_node.outputs['Image'], composite_node.inputs['Image'])
        tree.links.new(gamma_node.outputs['Image'], viewer_node.inputs['Image'])
        # Set the render output path
        bpy.context.scene.render.filepath = '/output/composited_image.png'