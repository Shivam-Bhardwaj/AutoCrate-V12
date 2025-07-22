"""
AutoCrate - Automated CAD Design Tool for Custom Shipping Crates

A sophisticated CAD automation tool that generates parametric design data 
for Siemens NX CAD software, enabling automated creation of detailed 3D 
models and technical drawings for shipping crates.
"""

__version__ = "12.0.2"
__author__ = "AutoCrate Development Team"
__license__ = "Proprietary"

from .core import *
from .gui import AutoCrateApp

__all__ = [
    "AutoCrateApp",
]