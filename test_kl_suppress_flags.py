#!/usr/bin/env python
"""
Test KL suppression flags
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'autocrate'))

from nx_expressions_generator import generate_crate_expressions_logic

# Test with medium size to get partial klimp usage
params = {
    'product_weight_lbs': 1500.0,
    'product_length_in': 60.0,  # Medium crate
    'product_width_in': 48.0,   # Medium crate  
    'clearance_each_side_in': 2.0,
    'allow_3x4_skids_bool': True,
    'panel_thickness_in': 0.25,
    'cleat_thickness_in': 2.0,
    'cleat_member_actual_width_in': 3.5,
    'product_actual_height_in': 36.0,
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
output_file = f"expressions/test_KL_suppress_{timestamp}.exp"

print("Testing KL suppression flags...")
print(f"Product size: {params['product_length_in']} x {params['product_width_in']} x {params['product_actual_height_in']} inches")
print(f"Output: {output_file}")
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
        print(f"\nSUCCESS: {message}")
        
        # Read and display KL variables with suppression flags
        with open(output_file, 'r') as f:
            content = f.read()
        
        print("\nKL Variables with Suppression Flags:")
        print("-" * 60)
        
        # Track klimps and their states
        klimp_states = {}
        
        for i in range(1, 10):
            suppress_flag = None
            x_pos = None
            z_pos = None
            
            for line in content.split('\n'):
                if f'KL_{i}_SUPPRESS' in line:
                    # Extract suppress flag value
                    if '= 0' in line:
                        suppress_flag = 0
                    elif '= 1' in line:
                        suppress_flag = 1
                elif f'[Inch]KL_{i}_X' in line:
                    # Extract X position
                    parts = line.split('=')
                    if len(parts) == 2:
                        try:
                            x_pos = float(parts[1].split('//')[0].strip())
                        except:
                            pass
                elif f'[Inch]KL_{i}_Z' in line:
                    # Extract Z position
                    parts = line.split('=')
                    if len(parts) == 2:
                        try:
                            z_pos = float(parts[1].split('//')[0].strip())
                        except:
                            pass
            
            klimp_states[i] = {
                'suppress': suppress_flag,
                'x': x_pos,
                'z': z_pos
            }
            
            # Display status
            if suppress_flag == 0:
                print(f"KL_{i}: ACTIVE   (suppress=0) X={x_pos:7.3f}, Z={z_pos:7.3f}")
            elif suppress_flag == 1:
                print(f"KL_{i}: SUPPRESS (suppress=1) X={x_pos:7.3f}, Z={z_pos:7.3f}")
            else:
                print(f"KL_{i}: ERROR - No suppress flag found")
        
        # Summary
        print("\n" + "-" * 60)
        active_count = sum(1 for k in klimp_states.values() if k['suppress'] == 0)
        suppressed_count = sum(1 for k in klimp_states.values() if k['suppress'] == 1)
        
        print(f"Summary:")
        print(f"  Active klimps: {active_count}")
        print(f"  Suppressed klimps: {suppressed_count}")
        print(f"  Total: {active_count + suppressed_count}")
        
        # Verify active klimps have non-zero positions
        print("\nValidation:")
        all_valid = True
        for i, state in klimp_states.items():
            if state['suppress'] == 0:
                if state['x'] == 0 and state['z'] == 0:
                    print(f"  ERROR: KL_{i} is active but has zero position!")
                    all_valid = False
            elif state['suppress'] == 1:
                if state['x'] != 0 or state['z'] != 0:
                    print(f"  WARNING: KL_{i} is suppressed but has non-zero position")
        
        if all_valid:
            print("  ✓ All suppression flags are correctly set")
        
    else:
        print(f"FAILED: {message}")
        
except Exception as e:
    print(f"ERROR: {str(e)}")
    import traceback
    traceback.print_exc()