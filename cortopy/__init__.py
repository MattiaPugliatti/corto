"""
# CORTO - cortopy (da sostituire con nome per pip install)

INSERT NAME AND URL OF THE PROJECT
------------------------------------------------------------------------------
INSERT DETAILS OF THE LICENSE HERE
------------------------------------------------------------------------------
"""

__all__ = (
    # should contain name of things that you can import from the module
    # just some dummy examples are provided here
    "__version__",
    "Camera",
    "Sun",
    "Model",
    "Renderer",
)

from ._version import __version__
from ._Camera import Camera, AdditionalExampleClass
from ._Sun import Sun
from ._Model import Model
from ._Renderer import Renderer

# here you can add additional istructions that will be called when module
# is imported: e.g., global variables declaration