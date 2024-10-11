from __future__ import annotations
from typing import Any, List, Mapping, Optional, Tuple, Union, overload

class Template:
    """
    Body class
    """

    @classmethod
    def exampleClass(cls, arg1: int, arg2: int) -> Tuple[int, int]:  # type hinting
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

    @staticmethod  # decorator for static methods
    def exampleStatic(arg1: int, arg2: int) -> Tuple[int, int]:  # type hinting
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