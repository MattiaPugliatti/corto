"""
# NAME, URL AND DETAIL OF LICENSE, SAME FOR EACH FILE
"""

from __future__ import annotations

# useful for type-hinting
from typing import (Any, List, Mapping, Optional, Tuple, Union, overload)

class Camera():

    @classmethod # decorator for class methods
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

    @overload # decorator for functions that can be defined in multiple ways depending on their argument (similar to virtual functions in c++)
    def __init__(self, arg1: int, arg2: int) -> None: #first possible version
        """
        Description of the method

        Args:
            arg 1: description
            arg 2: description

        Raises:
            which kind of exceptions

        See also:
            additional function and modules imported

        """
        ... # implementation is left blank

    @overload
    def __init__(self, arg1: float) -> float: # second possible version
        """
        Description of the method

        Args:
            arg 1: description

        Raises:
            which kind of exceptions
        
        Returns:
            arg 1: descritpion

        See also:
            additional function and modules imported

        """
        ...


    def __init__(self, *args, **kwargs) -> None: # version that actually implements the different args checks and implementation
        ...

'''
import numpy as np

class camera:
    """
    Camera class
    """
    ### Constructor ###
    ### ----------- ###
    def __init__(self, name:str, properties:dict):
        """
        Camera constructor
        """

        self.name = name
        
        self.location = np.array([0,0,0])
        self.orientation = np.array([0,0,0,0])

        self.fov = properties['fov']*np.pi/180# [rad]
        self.res_x = properties['res_x'] # [-]
        self.res_y = properties['res_y'] # [-]
        self.res = np.array([self.res_x, self.res_y]) #[-]
        self.t_int = properties['T_int'] # [s]
        self.sensor = properties['sensor'] # (str)
        self.K = properties['K'] # [px]

    ### Methods ###
    ### ------- ###
    
    # Instance methods
    def get_name(self):
        return self.name

    def get_location(self):
        return self.location
    
    def get_orientation(self):
        return self.orientation

    def get_fov(self):
        return self.fov
    
    def get_res(self):
        return self.res

    def get_Tint(self):
        return self.t_int

    def get_K(self):
        return self.K
               
    def get_sensor(self):
        return self.sensor
    
    def set_position(self, location:np.array):
        self.location = location

    def set_orientation(self, orientation:np.array):
        self.location = orientation
    
    # Class methods
'''