import json
import numpy as np
from typing import (Any, List, Mapping, Optional, Tuple, Union, overload)
import bpy

class State:
    """
    State class: manages scene settings such as environment properties, geometry, and input models.
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

    #@overload
    def __init__(self, scene: str = None, geometry: str = None, body: str = None) -> None:
        """
        Constructor for the class STATE defining scene parameters

        Args:
            scene: path to json file with scene settings
            geometry: path to json file with geometry settings 
            body: path to file with body .blend model? 
        """
        # deal with scene first
        self.import_scene(scene)
        self.import_geometry(geometry)
        self.import_body(body)

        
    def import_geometry(self, geometry: str) -> None:
        """
        Import scene geometry configuration

        Args:
            geometry: path to json file with geometry settings 
        """
        try:
            with open(geometry, 'r') as json_file:
                self.geometry = json.load(json_file)

            self.geometry['sun']['position'] = np.array(self.geometry['sun']['position'])

            self.geometry['body']['position'] = np.array(self.geometry['body']['position'])
            self.geometry['body']['orientation'] = np.array(self.geometry['body']['orientation'])

            self.geometry['camera']['position'] = np.array(self.geometry['camera']['position'])
            self.geometry['camera']['orientation'] = np.array(self.geometry['camera']['orientation'])
            
        except:
            self.geometry = {}

    def import_scene(self, scene: str) -> None:
        """
        Import scene settings 

        Args:
            scene: path to json file with scene settings
        """
        try:
            with open(scene, 'r') as json_file:
                settings_json = json.load(json_file)
                self.properties_cam = settings_json["camera_settings"]
                self.properties_cam["K"] = eval(self.properties_cam["K"])
                self.properties_sun = settings_json["sun_settings"]
                self.properties_body = settings_json["body_settings"]
                self.properties_rendering = settings_json["rendering_settings"]
        except:
            self.properties_cam = {}
            self.properties_sun = {}
            self.properties_body = {}
            self.properties_rendering = {}

    def import_body(self, body_filepath: str, load_mode:str = 'obj') -> None:
        """Import body 

        Args:
            body_filepath (str): filepath of the body
            load_mode (str, optional): loading mode flag. Defaults to 'obj'.
        """
        if load_mode =='obj':
            bpy.ops.wm.obj_import(filepath=body_filepath)
            print(f"Imported .obj file from {body_filepath}")        
        elif load_mode == '.blend':
            print('Not implemented')
