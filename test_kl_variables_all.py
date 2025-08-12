#!/usr/bin/env python
"""
Test KL_1 through KL_9 variables for all klimp positions
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'autocrate'))

from nx_expressions_generator import generate_crate_expressions_logic

# Test with a large panel to get multiple klimps
params = {
    'product_weight_lbs': 3000.0,
    'product_length_in': 120.0,  # Very large crate
    'product_width_in': 96.0,    # Very large crate  
    'clearance_each_side_in': 2.0,
    'allow_3x4_skids_bool': False,
    'panel_thickness_in': 0.25,
    'cleat_thickness_in': 2.0,
    'cleat_member_actual_width_in': 3.5,
    'product_actual_height_in': 60.0,
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
output_file = f"expressions/test_KL_all_{timestamp}.exp"

print("Testing KL_1 through KL_9 variables...")
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
        
        # Read and display all KL variables
        with open(output_file, 'r') as f:
            content = f.read()
        
        print("\nKL Variables Found:")
        print("-" * 60)
        
        kl_variables = []
        for line in content.split('\n'):
            if line.startswith('[Inch]KL_'):
                kl_variables.append(line)
                print(line)
        
        # Count active klimps (non-zero positions)
        active_klimps = 0
        x_positions = []
        z_position = None
        
        for var in kl_variables:
            if '_X' in var and '0.000' not in var:
                active_klimps += 1
                # Extract position value
                parts = var.split('=')
                if len(parts) == 2:
                    try:
                        x_val = float(parts[1].split('//')[0].strip())
                        if x_val != 0:
                            x_positions.append(x_val)
                    except:
                        pass
            elif '_Z' in var and '0.000' not in var and z_position is None:
                parts = var.split('=')
                if len(parts) == 2:
                    try:
                        z_position = float(parts[1].split('//')[0].strip())
                    except:
                        pass
        
        print("\n" + "-" * 60)
        print(f"Summary:")
        print(f"  Active klimps: {active_klimps}")
        print(f"  Z position (height): {z_position:.3f} inches" if z_position else "  Z position: Not found")
        
        if len(x_positions) > 1:
            x_positions.sort()
            print(f"  X positions from center: {[f'{x:.3f}' for x in x_positions]}")
            
            # Calculate spacings
            spacings = []
            for i in range(len(x_positions) - 1):
                spacings.append(x_positions[i+1] - x_positions[i])
            
            print(f"  Spacings between klimps: {[f'{s:.2f}\"' for s in spacings]}")
            print(f"  Min spacing: {min(spacings):.2f}\"")
            print(f"  Max spacing: {max(spacings):.2f}\"")
            print(f"  Avg spacing: {sum(spacings)/len(spacings):.2f}\"")
        
    else:
        print(f"FAILED: {message}")
        
except Exception as e:
    print(f"ERROR: {str(e)}")
    import traceback
    traceback.print_exc()