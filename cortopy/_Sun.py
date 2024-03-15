"""
# NAME, URL AND DETAIL OF LICENSE, SAME FOR EACH FILE
"""

from __future__ import annotations

# useful for type-hinting
from typing import (Any, List, Mapping, Optional, Tuple, Union, overload)

from ._PrettyType import PrettyType

#class name (what is indicated in __init__.py)
class Sun(metaclass=PrettyType):

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