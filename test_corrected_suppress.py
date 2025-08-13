#!/usr/bin/env python
"""
Test corrected KL suppression flags (0=suppress, 1=show)
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'autocrate'))

from nx_expressions_generator import generate_crate_expressions_logic

# Small crate to test with few klimps
params = {
    'product_weight_lbs': 500.0,
    'product_length_in': 30.0,
    'product_width_in': 24.0,
    'clearance_each_side_in': 2.0,
    'allow_3x4_skids_bool': True,
    'panel_thickness_in': 0.25,
    'cleat_thickness_in': 2.0,
    'cleat_member_actual_width_in': 3.5,
    'product_actual_height_in': 20.0,
    'clearance_above_product_in': 2.0,
    'ground_clearance_in': 3.5,
    'floorboard_actual_thickness_in': 0.75,
    'selected_lumber_str': [3.5, 5.5],
    'max_gap_for_lumber_in': 8.0,
    'min_size_for_custom_lumber_in': 2.0,
    'force_small_custom_board_bool': False,
    'plywood_selections': {
        "front_panel": "5-Ply OSB",
        "back_panel": "5-Ply OSB",
        "left_panel": "5-Ply OSB",
        "right_panel": "5-Ply OSB",
        "top_panel": "5-Ply OSB"
    }
}

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = f"expressions/test_corrected_suppress_{timestamp}.exp"

print("Testing CORRECTED KL suppression flags (0=suppress, 1=show)...")
print("-" * 60)

try:
    success, message = generate_crate_expressions_logic(
        params['product_weight_lbs'],
        params['product_length_in'],
        params['product_width_in'],
        params['clearance_each_side_in'],
        params['allow_3x4_skids_bool'],
        params['panel_thickness_in'],
        params['cleat_thickness_in'],
        params['cleat_member_actual_width_in'],
        params['product_actual_height_in'],
        params['clearance_above_product_in'],
        params['ground_clearance_in'],
        params['floorboard_actual_thickness_in'],
        params['selected_lumber_str'],
        params['max_gap_for_lumber_in'],
        params['min_size_for_custom_lumber_in'],
        params['force_small_custom_board_bool'],
        output_file,
        params['plywood_selections']
    )
    
    if success:
        print(f"SUCCESS: Generated {output_file}\n")
        
        # Read the file and check suppression flags
        with open(output_file, 'r') as f:
            lines = f.readlines()
        
        print("KL Suppression Flags (Corrected: 0=suppress, 1=show):")
        print("-" * 60)
        
        for i in range(1, 10):
            # Find the three lines for each klimp
            suppress_line = None
            x_line = None
            z_line = None
            
            for line in lines:
                if f'KL_{i}_SUPPRESS' in line:
                    suppress_line = line.strip()
                elif f'[Inch]KL_{i}_X' in line:
                    x_line = line.strip()
                elif f'[Inch]KL_{i}_Z' in line:
                    z_line = line.strip()
            
            if suppress_line:
                # Extract the flag value
                if '= 1' in suppress_line:
                    status = "SHOW   "
                elif '= 0' in suppress_line:
                    status = "SUPPRESS"
                else:
                    status = "ERROR  "
                
                print(f"KL_{i}: {status} - {suppress_line}")
                
                # Verify consistency
                if '= 1' in suppress_line:  # Should show
                    if x_line and '0.000' in x_line and '0.000' in z_line:
                        print(f"       WARNING: Active klimp has zero position!")
                elif '= 0' in suppress_line:  # Should suppress
                    if x_line and '0.000' not in x_line:
                        print(f"       WARNING: Suppressed klimp has non-zero X position!")
        
        print("\n" + "-" * 60)
        print("Verification Complete!")
        
    else:
        print(f"FAILED: {message}")
        
except Exception as e:
    print(f"ERROR: {str(e)}")
    import traceback
    traceback.print_exc()