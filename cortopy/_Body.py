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

        # BODY properties — all keys are optional; Blender Cycles defaults are used as fallback.
        _DEFAULTS = {
            "pass_index":          0,
            "total_bounces":       12,
            "diffuse_bounces":     4,
            "glossy_bounces":      4,
            "transmission_bounces": 12,
            "volume_bounces":      0,
            "transparent_bounces": 8,
        }

        def _get(key: str) -> int:
            if key not in properties:
                print(f"Body '{name}': '{key}' not found in properties, using default value {_DEFAULTS[key]}.")
                return _DEFAULTS[key]
            val = properties[key]
            if type(val) != int:
                raise TypeError(f"'{key}' must have an integer value, got {type(val).__name__}.")
            return val

        self.pass_index         = _get("pass_index")
        self.total_bounces      = _get("total_bounces")
        self.diffuse_bounces    = _get("diffuse_bounces")
        self.glossy_bounces     = _get("glossy_bounces")
        self.transmission       = _get("transmission_bounces")
        self.volume_bounces     = _get("volume_bounces")
        self.transparent_bounces = _get("transparent_bounces")

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

        # TODO: workout if these properties should be in body or in scene
        bpy.context.scene.cycles.max_bounces = self.total_bounces
        bpy.context.scene.cycles.diffuse_bounces = self.diffuse_bounces
        bpy.context.scene.cycles.glossy_bounces = self.glossy_bounces
        bpy.context.scene.cycles.transmission_bounces = self.transmission
        bpy.context.scene.cycles.volume_bounces = self.volume_bounces
        bpy.context.scene.cycles.transparent_max_bounces = self.transparent_bounces

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

    def visible(self, visibility_flag:bool = True) -> None: 
        """
        Make the body object visible in both the viewport and render
        """
        self.BODY_Blender.hide_viewport = not(visibility_flag)
        self.BODY_Blender.hide_render = not(visibility_flag)

    def get_total_bounces(self) -> int:
        """
        Get total bounces setting for the BODY instance

        Raises:
            ValueError : BODY instance has mismatching property

        Returns:
            total bounces : setting of total bounces property
        """
        if bpy.context.scene.cycles.max_bounces != self.total_bounces:
            raise ValueError("parameter mismatch between workspaces.")
        return self.total_bounces


    def set_total_bounces(self, par: int) -> None:
        """
        Set total bounces property for the BODY instance

        Args:
            par (int) : scalar value for total bounces property

        Raises:
            TypeError : number of bounces must have integer values
        """
        if type(par) != int:
            raise TypeError("Number of bounces must have integer values.")
        self.total_bounces = par
        bpy.context.scene.cycles.max_bounces = self.total_bounces


    def get_glossy_bounces(self) -> int:
        """
        Get glossy bounces setting for the BODY instance

        Raises:
            ValueError : BODY instance has mismatching property

        Returns:
            glossy bounces : setting of glossy bounces property
        """
        if bpy.context.scene.cycles.glossy_bounces != self.glossy_bounces:
            raise ValueError("parameter mismatch between workspaces.")
        return self.glossy_bounces


    def set_glossy_bounces(self, par: int) -> None:
        """
        Set glossy bounces property for the BODY instance

        Args:
            par (int) : scalar value for glossy bounces property

        Raises:
            TypeError : number of bounces must have integer values
        """
        if type(par) != int:
            raise TypeError("Number of bounces must have integer values.")
        self.glossy_bounces = par
        bpy.context.scene.cycles.glossy_bounces = self.glossy_bounces


    def get_transmission(self) -> int:
        """
        Get transmission bounces setting for the BODY instance

        Raises:
            ValueError : BODY instance has mismatching property

        Returns:
            transmission bounces : setting of transmission bounces property
        """
        if bpy.context.scene.cycles.transmission_bounces != self.transmission:
            raise ValueError("parameter mismatch between workspaces.")
        return self.transmission


    def set_transmission(self, par: int) -> None:
        """
        Set transmission bounces property for the BODY instance

        Args:
            par (int) : scalar value for transmission bounces property

        Raises:
            TypeError : number of bounces must have integer values
        """
        if type(par) != int:
            raise TypeError("Number of bounces must have integer values.")
        self.transmission = par
        bpy.context.scene.cycles.transmission_bounces = self.transmission


    def get_volume_bounces(self) -> int:
        """
        Get volume bounces setting for the BODY instance

        Raises:
            ValueError : BODY instance has mismatching property

        Returns:
            volume bounces : setting of volume bounces property
        """
        if bpy.context.scene.cycles.volume_bounces != self.volume_bounces:
            raise ValueError("parameter mismatch between workspaces.")
        return self.volume_bounces


    def set_volume_bounces(self, par: int) -> None:
        """
        Set volume bounces property for the BODY instance

        Args:
            par (int) : scalar value for volume bounces property

        Raises:
            TypeError : number of bounces must have integer values
        """
        if type(par) != int:
            raise TypeError("Number of bounces must have integer values.")
        self.volume_bounces = par
        bpy.context.scene.cycles.volume_bounces = self.volume_bounces


    def get_transparent_bounces(self) -> int:
        """
        Get transparent bounces setting for the BODY instance

        Raises:
            ValueError : BODY instance has mismatching property

        Returns:
            transparent bounces : setting of transparent bounces property
        """
        if bpy.context.scene.cycles.transparent_max_bounces != self.transparent_bounces:
            raise ValueError("parameter mismatch between workspaces.")
        return self.transparent_bounces


    def set_transparent_bounces(self, par: int) -> None:
        """
        Set transparent bounces property for the BODY instance

        Args:
            par (int) : scalar value for transparent bounces property

        Raises:
            TypeError : number of bounces must have integer values
        """
        if type(par) != int:
            raise TypeError("Number of bounces must have integer values.")
        self.transparent_bounces = par
        bpy.context.scene.cycles.transparent_max_bounces = self.transparent_bounces