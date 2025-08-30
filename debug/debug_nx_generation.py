#!/usr/bin/env python3
"""
Debug the NX generation to find where the 5" is added.
"""

import sys
import os
import tempfile

# Add autocrate to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'autocrate'))

# Import and patch the desktop generator
import autocrate.nx_expressions_generator as nx_gen

# Store original function
original_generate = nx_gen.generate_crate_expressions_logic

def patched_generate(**kwargs):
    """Patched version with debug output."""
    # Get initial values
    product_length = kwargs.get('product_length_in', 0)
    clearance = kwargs.get('clearance_each_side_in', 0)
    
    print(f"\nDEBUG: Input product_length = {product_length}")
    print(f"DEBUG: Input clearance = {clearance}")
    print(f"DEBUG: Expected initial crate_length = {product_length + 2*clearance}")
    
    # Call original with debug
    result = original_generate(**kwargs)
    
    return result

# Patch the module
nx_gen.generate_crate_expressions_logic = patched_generate

# Now import the function normally
from autocrate.nx_expressions_generator import generate_crate_expressions_logic

# Test parameters
params = {
    'product_weight_lbs': 1000,
    'product_length_in': 96,
    'product_width_in': 48,
    'clearance_each_side_in': 2,
    'allow_3x4_skids_bool': True,
    'panel_thickness_in': 0.75,
    'cleat_thickness_in': 1.5,
    'cleat_member_actual_width_in': 3.5,
    'product_actual_height_in': 30,
    'clearance_above_product_in': 2,
    'ground_clearance_in': 4,
    'floorboard_actual_thickness_in': 1.5,
    'selected_std_lumber_widths': [6.0, 4.0, 2.0],
    'max_allowable_middle_gap_in': 6,
    'min_custom_lumber_width_in': 1.5,
    'force_small_custom_board_bool': False
}

# Create temp output file
with tempfile.NamedTemporaryFile(mode='w', suffix='.exp', delete=False) as f:
    output_file = f.name

print("Starting NX generation with debug...")
success, message = generate_crate_expressions_logic(
    **params,
    output_filename=output_file,
    plywood_panel_selections=None
)

if success:
    # Read the generated file and find key values
    with open(output_file, 'r') as f:
        for line in f:
            if 'crate_overall_length_OD' in line and '=' in line:
                print(f"\nFINAL OUTPUT: {line.strip()}")
                break
    os.remove(output_file)
else:
    print(f"Generation failed: {message}")
