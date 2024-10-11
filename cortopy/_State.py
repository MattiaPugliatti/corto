from __future__ import annotations
from typing import Any, List, Mapping, Optional, Tuple, Union, overload

import json
import numpy as np
import bpy
import os
from pathlib import Path


class State:
    """
    State class: manages scene settings such as environment properties, geometry, and input models.
    """

    # *************************************************************************
    # *     Constructors & Destructors
    # *************************************************************************

    # @overload
    def __init__(
        self,
        scene: str = None,
        geometry: str = None,
        body: str = None,
        scenario: str = None,
    ) -> None:
        """
        Constructor for the class STATE defining scene parameters

        Args:
            scene (str): path to json file with scene settings
            geometry (str): path to json file with geometry settings
            body (str): path to file with body .blend model?
        """

        # Get the directory where the script is located
        corto_path = Path("__file__").resolve().parent
        print(f"Script is running in: {corto_path}")

        scene_file = os.path.join("input", scenario, "scene", scene)
        geometry_file = os.path.join("input", scenario, "geometry", geometry)
        body_file = os.path.join("input", scenario, "body", "shape", body)

        # deal with scene first
        self.import_scene(scene_file)
        self.import_geometry(geometry_file)
        self.import_body(body_file)
        self.path = {}
        self.add_path("corto_path", corto_path)
        self.add_path("input_path", os.path.join(corto_path, "input", scenario))
        self.add_path("output_path", os.path.join(corto_path, "output", scenario))

    def import_geometry(self, geometry: str) -> None:
        """
        Import scene geometry configuration

        Args:
            geometry (str): path to json file with geometry settings
        """
        try:
            with open(geometry, "r") as json_file:
                self.geometry = json.load(json_file)
            # Sun
            self.geometry["sun"]["position"] = np.array(
                self.geometry["sun"]["position"]
            )
            # Body
            self.geometry["body"]["position"] = np.array(
                self.geometry["body"]["position"]
            )
            self.geometry["body"]["orientation"] = np.array(
                self.geometry["body"]["orientation"]
            )
            # Camera
            self.geometry["camera"]["position"] = np.array(
                self.geometry["camera"]["position"]
            )
            self.geometry["camera"]["orientation"] = np.array(
                self.geometry["camera"]["orientation"]
            )

        except:
            self.geometry = {}

    def import_scene(self, scene: str) -> None:
        """
        Import scene settings

        Args:
            scene (str): path to json file with scene settings
        """
        try:
            with open(scene, "r") as json_file:
                settings_json = json.load(json_file)
                self.properties_cam = settings_json["camera_settings"]
                self.properties_cam["K"] = eval(self.properties_cam["K"]) # TODO: generalize handling of these type of variables from json
                self.properties_sun = settings_json["sun_settings"]
                self.properties_body = settings_json["body_settings"]
                self.properties_rendering = settings_json["rendering_settings"]
        except:
            self.properties_cam = {}
            self.properties_sun = {}
            self.properties_body = {}
            self.properties_rendering = {}

    def import_body(self, body_filepath: str, load_mode: str = "obj") -> None:
        """Import body

        Args:
            body_filepath (str): filepath of the body
            load_mode (str, optional): loading mode flag. Defaults to 'obj'.
        """
        if load_mode == "obj":
            bpy.ops.wm.obj_import(filepath=body_filepath)
            print(f"Imported .obj file from {body_filepath}")
        elif load_mode == ".blend":
            print("Not implemented")

    def add_path(self, name: str, path: str) -> None:
        """add path into the State dictionary containing all relevant paths

        Args:
            name (str): name of the key in the dictionary
            path (str): associated path
        """        
        if self.path:
            # Update the dictionary with the new name and path
            self.path.update({name: path})
        else:
            # Initialize the dictionary with the new name and path
            self.path = {name: path}
