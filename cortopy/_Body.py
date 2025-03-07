from __future__ import annotations
from typing import Any, List, Mapping, Optional, Tuple, Union, overload

import numpy as np
import bpy
import math

class Body:
    """
    Body class
    """

    # *************************************************************************
    # *     Constructors & Destructors
    # *************************************************************************

    def __init__(self, name: str, properties: dict) -> None:
        """
        Constructor for the BODY class defining a Blender object

        Args:
            name (str): name of the BODY object
            properties (dict): properties dictionary of the BODY object

        Raises:
            TypeError : object pass index must be expressed with integer values
            TypeError : number of bounces must have integer values

        """
        # BODY name
        self.name = name

        # BODY properties
        self.pass_index = properties["pass_index"]
        if type(self.pass_index) != int:
            raise TypeError("Pass index must have integer values.")

        self.diffuse_bounces = properties["diffuse_bounces"]
        if type(self.diffuse_bounces) != int:
            raise TypeError("Number of bounces must have integer values.")

        # BODY pose
        self.position = np.array([0, 0, 0])
        self.orientation = np.array([1, 0, 0, 0])
        self.scale = np.array([1, 1, 1])

        # Generate the Blender object
        BODY = bpy.data.objects[self.name]
        BODY.location = self.position  # [BU]
        BODY.rotation_mode = "QUATERNION"
        BODY.rotation_quaternion = self.orientation  # [-]
        BODY.pass_index = self.pass_index  # [-]
        BODY.scale = self.scale  # [-]
        bpy.context.scene.cycles.diffuse_bounces = (
            self.diffuse_bounces
        )  # [-] # TODO: workout if this property should be in body or in scene

        # Link the corto and blender objects
        self.BODY_Blender = BODY

    # *************************************************************************
    # *     Instance Methods
    # *************************************************************************

    def get_name(self) -> str:
        """
        Get name of the BODY instance

        Raises:
            NameError : BODY instance has mismatching name

        Returns:
            name : name of the BODY object
        """

        if self.BODY_Blender.name != self.name:
            raise NameError("Naming mismatch between workspaces.")

        return self.name

    def get_position(self) -> np.array:
        """
        Get position of the BODY instance

        Raises:
            ValueError : BODY instance has mismatching location

        Returns:
            position : vector containing the location of the BODY object
        """

        if not all(
            np.float32(np.array(self.BODY_Blender.location))
            == np.float32(self.position)
        ):
            raise ValueError("Position mismatch between workspaces.")

        return self.position

    def get_orientation(self) -> np.array:
        """
        Get orientation of the BODY instance

        Raises:
            ValueError : BODY instance has mismatching orientation

        Returns:
            orientation : vector containing the quaternion representing the orientation of the BODY object
        """

        if not all(
            np.float32(np.array(self.BODY_Blender.rotation_quaternion))
            == np.float32(self.orientation)
        ):
            raise ValueError("orientation mismatch between workspaces.")

        return self.orientation

    def get_scale(self) -> float:
        """
        Get scale of the BODY instance

        Raises:
            ValueError : BODY instance has mismatching scale

        Returns:
            scale : scale of the BODY object
        """
        if not all(np.float32(self.BODY_Blender.scale) == np.float32(self.scale)):
            raise ValueError("scale mismatch between workspaces.")

        return self.scale

    def get_passID(self) -> int:
        """
        Get pass index of the BODY instance

        Raises:
            ValueError : BODY instance has mismatching pass index

        Returns:
            pass index : pass index of the BODY object
        """

        if self.BODY_Blender.pass_index != self.pass_index:
            raise ValueError("pass index mismatch between workspaces.")

        return self.pass_index

    def get_diffuse_bounces(self) -> int:
        """
        Get diffuse bounces setting for the BODY instance

        Raises:
            ValueError : BODY instance has mismatching property

        Returns:
            diffuse bounces :  setting of diffuse bounces property
        """

        if bpy.context.scene.cycles.diffuse_bounces != self.diffuse_bounces:
            raise ValueError("parameter mismatch between workspaces.")
        return self.diffuse_bounces

    def set_position(self, position: np.array) -> None:
        """
        Set position of the BODY instance

        Args:
            position (np.array) : array containing 3d coordinates for the BODY object
        """
        self.position = position
        self.BODY_Blender.location = self.position

    def set_orientation(self, orientation: np.array) -> None:
        """
        Set orientation of the BODY instance

        Args:
            orientation (np.array) : array containing quaternion expressing the orientation of the BODY object

        Raises:
            ValueError : Provided quaternion is not a unit vector, it does not represent a rotation
        """

        if not math.isclose(np.linalg.norm(orientation), 1.0, rel_tol=1e-4):
            raise ValueError("Provided quaternion is not a unit vector")

        self.orientation = orientation
        self.BODY_Blender.rotation_mode = "QUATERNION"
        self.BODY_Blender.rotation_quaternion = self.orientation

    def set_scale(self, scale: np.array) -> None:
        """
        Set scale of the BODY instance

        Args:
            scale (np.array): array containing scaling factors in 3 directions for the BODY object
        """
        self.scale = scale
        self.BODY_Blender.scale = self.scale

    def set_passID(self, ID: int) -> None:
        """
        Set pass index of the BODY instance

        Args:
            ID (int) : scalar pass index value for the BODY object

        Raises:
            TypeError : object pass index must be expressed with integer values
        """

        if type(ID) != int:
            raise TypeError("Pass index must have integer values.")

        self.pass_index = ID
        self.BODY_Blender.pass_index = self.pass_index

    def set_diffuse_bounces(self, par: int) -> None: #TODO: workout the location of this function here or in scene
        """
        Set diffuse bounces property for the BODY instance

        Args:
            par (int) : scalar value for diffuse bounces property

        Raises:
            TypeError : number of bounces must have integer values
        """

        if type(par) != int:
            raise TypeError("Number of bounces must have integer values.")
        self.diffuse_bounces = par
        bpy.context.scene.cycles.diffuse_bounces = self.diffuse_bounces  # [-]
