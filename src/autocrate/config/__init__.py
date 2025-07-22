"""
Configuration management for AutoCrate.

This package handles application settings, material properties,
and user preferences.
"""

from .settings import Settings
from .materials import MaterialConfig

__all__ = ["Settings", "MaterialConfig"]