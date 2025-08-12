#!/usr/bin/env python
"""
Test the new klimp placement logic with 16-24 inch spacing
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'autocrate'))

from nx_expressions_generator import generate_crate_expressions_logic

# Test with a larger panel to see multiple klimps
params = {
    'product_weight_lbs': 2000.0,
    'product_length_in': 96.0,  # Large crate
    'product_width_in': 72.0,   # Large crate
    'clearance_each_side_in': 2.0,
    'allow_3x4_skids_bool': False,
    'panel_thickness_in': 0.25,
    'cleat_thickness_in': 2.0,
    'cleat_member_actual_width_in': 3.5,
    'product_actual_height_in': 48.0,
    'clearance_above_product_in': 2.0,
    'ground_clearance_in': 3.5,
    'floorboard_actual_thickness_in': 0.75,
    'selected_lumber_str': [3.5, 5.5],  # Use actual widths
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
output_file = f"expressions/test_klimp_spacing_{timestamp}.exp"

print("Testing klimp placement with 16-24 inch spacing...")
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
        
        # Check the klimp positions
        with open(output_file, 'r') as f:
            content = f.read()
            
        # Count klimps
        klimp_count = 0
        klimp_positions = []
        
        for line in content.split('\n'):
            if 'FP_Top_Klimp_' in line and '_X_Pos' in line:
                parts = line.split('=')
                if len(parts) == 2:
                    try:
                        pos = float(parts[1].strip())
                        if pos > 0:  # Non-zero position means klimp is active
                            klimp_positions.append(pos)
                            klimp_count += 1
                    except:
                        pass
            elif '[Inch]KL_1_X' in line:
                print(f"\nKL_1_X: {line.strip()}")
        
        print(f"\nKlimp placement results:")
        print(f"  Total klimps placed: {klimp_count}")
        
        if klimp_count > 1:
            klimp_positions.sort()
            print(f"  Klimp positions: {klimp_positions}")
            
            # Calculate spacings
            spacings = []
            for i in range(len(klimp_positions) - 1):
                spacings.append(klimp_positions[i+1] - klimp_positions[i])
            
            if spacings:
                print(f"  Spacings between klimps:")
                for i, spacing in enumerate(spacings):
                    status = "OK" if 16 <= spacing <= 24 else "WARNING"
                    print(f"    Klimp {i+1} to {i+2}: {spacing:.2f}\" [{status}]")
                
                print(f"  Min spacing: {min(spacings):.2f}\"")
                print(f"  Max spacing: {max(spacings):.2f}\"")
                print(f"  Avg spacing: {sum(spacings)/len(spacings):.2f}\"")
        
    else:
        print(f"FAILED: {message}")
        
except Exception as e:
    print(f"ERROR: {str(e)}")
    import traceback
    traceback.print_exc()