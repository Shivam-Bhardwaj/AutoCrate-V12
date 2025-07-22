"""
AutoCrate V10.1.7 - CAD Automation System
==========================================

This package provides automated generation of NX expressions for crate manufacturing.

Core Components:
- nx_expressions_generator.py: Main NX expression generator
- front_panel_logic_unified.py: Unified front panel calculations
- *_panel_logic.py: Panel-specific calculation modules
- skid_logic.py: Skid parameter calculations
- plywood_layout_generator.py: Plywood layout optimization

Key Features:
- Adaptive splice coverage strategies
- Optimized cleat positioning
- Comprehensive CAD automation
- Preserved variable names for NX compatibility
"""

__version__ = "10.1.7"
__author__ = "AutoCrate Development Team"

# Core modules
from . import nx_expressions_generator
from . import front_panel_logic_unified
from . import front_panel_logic
from . import back_panel_logic
from . import end_panel_logic
from . import left_panel_logic
from . import right_panel_logic
from . import top_panel_logic
from . import skid_logic
from . import plywood_layout_generator

# Main entry points
from .nx_expressions_generator import generate_crate_expressions_logic, DEFAULT_AVAILABLE_STD_LUMBER_WIDTHS
from .front_panel_logic_unified import calculate_front_panel_components

__all__ = [
    'nx_expressions_generator',
    'front_panel_logic_unified',
    'front_panel_logic',
    'back_panel_logic',
    'end_panel_logic',
    'left_panel_logic',
    'right_panel_logic',
    'top_panel_logic',
    'skid_logic',
    'plywood_layout_generator',
    'generate_crate_expressions_logic',
    'calculate_front_panel_components',
    'DEFAULT_AVAILABLE_STD_LUMBER_WIDTHS'
]