"""
# NAME URL AND LICENSE OF PROJECT
"""


class PrettyType(type):
    """
    This class is used to have a better representation
    when type() is called on a CORTO object or the __module__ is accessed.
    """

    def __new__(cls, name, bases, classdict):
        t = super().__new__(cls, name, bases, classdict)
        t.__module__ = "cortopy"
        return t

    def __repr__(self):
        return "cortopy." + self.__name__
