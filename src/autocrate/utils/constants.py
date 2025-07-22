"""
Constants and material properties for AutoCrate.

This module contains all the material constants, lumber sizes,
and other configuration values used throughout the application.
"""

from typing import Dict

# Material Constants
MATERIAL_CONSTANTS = {
    'plywood_thickness': 0.75,  # inches
    'cleat_thickness': 1.5,     # inches
    'lumber_moisture_content': 0.19,  # 19% moisture content
    'wood_density_psf': 35,     # pounds per cubic foot for lumber
    'plywood_density_psf': 45,  # pounds per cubic foot for plywood
}

# Standard Lumber Sizes
LUMBER_SIZES = {
    "2x6 (5.5 in)": 5.5,
    "2x8 (7.25 in)": 7.25, 
    "2x10 (9.25 in)": 9.25,
    "2x12 (11.25 in)": 11.25
}

# Plywood Sizes
PLYWOOD_SIZES = {
    'standard_sheet': (96, 48),  # inches (width, height)
    'thickness_options': [0.25, 0.375, 0.5, 0.625, 0.75, 1.0],  # inches
}

# Layout Constants
LAYOUT_CONSTANTS = {
    'target_intermediate_cleat_spacing': 24.0,  # inches C-C target
    'max_allowable_middle_gap': 0.25,           # inches
    'min_forceable_custom_board_width': 0.25,   # inches
    'min_custom_lumber_width': 2.5,             # inches
}

# NX Instance Limits
NX_LIMITS = {
    'max_floorboard_instances': 20,
    'max_fp_intermediate_vertical_cleats': 7,
    'max_fp_intermediate_horizontal_cleats': 6,
    'max_bp_intermediate_vertical_cleats': 7,
    'max_bp_intermediate_horizontal_cleats': 6,
    'max_ep_intermediate_vertical_cleats': 5,
    'max_tp_intermediate_cleats': 7,
    'max_tp_intermediate_horizontal_cleats': 6,
    'max_lp_intermediate_vertical_cleats': 7,
    'max_lp_intermediate_horizontal_cleats': 6,
    'max_rp_intermediate_vertical_cleats': 7,
    'max_rp_intermediate_horizontal_cleats': 6,
    'max_plywood_instances': 10,
}

# Default Values
DEFAULTS = {
    'cleat_member_width': 3.5,      # inches
    'panel_sheathing_thickness': 0.75,  # inches
    'adjustment_threshold': 2.0,     # inches
    'adjustment_increment': 0.25,    # inches
    'clearance': 2.0,               # inches
}

# Tolerance and Precision
TOLERANCES = {
    'dimension_precision': 0.001,   # inches
    'angle_precision': 0.1,         # degrees
    'calculation_epsilon': 1e-10,   # for floating point comparisons
}

# UI Constants
UI_CONSTANTS = {
    'window_min_width': 800,
    'window_min_height': 600,
    'default_font_family': 'Segoe UI',
    'default_font_size': 9,
    'status_update_interval': 100,  # milliseconds
}

# File Extensions
FILE_EXTENSIONS = {
    'nx_expressions': '.exp',
    'configuration': '.json',
    'log_files': '.log',
    'backup_files': '.bak',
}

# Version Information
VERSION_INFO = {
    'major': 12,
    'minor': 0,
    'patch': 2,
    'build': None,
    'full_version': '12.0.2',
}

# Error Messages
ERROR_MESSAGES = {
    'invalid_dimension': "Dimension must be a positive number",
    'dimension_too_large': "Dimension exceeds maximum allowable size",
    'dimension_too_small': "Dimension is below minimum threshold",
    'calculation_failed': "Panel calculation failed - check input values",
    'file_not_found': "Required file not found",
    'invalid_configuration': "Configuration file is invalid or corrupted",
}

# Status Messages
STATUS_MESSAGES = {
    'ready': "Ready",
    'calculating': "Calculating panel components...",
    'generating': "Generating NX expressions...",
    'saving': "Saving file...",
    'complete': "Calculation complete",
    'error': "Error occurred during calculation",
}