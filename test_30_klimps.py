#!/usr/bin/env python
"""
Test the new 30-klimp system with rotation parameters
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'autocrate'))

from nx_expressions_generator import generate_crate_expressions_logic

# Medium-sized crate to test all klimp types
params = {
    'product_weight_lbs': 1000.0,
    'product_length_in': 48.0,
    'product_width_in': 48.0,
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
output_file = f"expressions/test_30_klimps_{timestamp}.exp"

print("Testing NEW 30-klimp system with rotation parameters...")
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
        
        # Read the file and check for new klimp variables
        with open(output_file, 'r') as f:
            lines = f.readlines()
        
        print("Checking for 30-klimp system with rotation:")
        print("-" * 60)
        
        # Check for rotation parameters
        found_rotations = []
        found_y_coords = []
        found_klimps = []
        
        for line in lines:
            # Check for rotation parameters
            if '_ROTATE' in line:
                found_rotations.append(line.strip())
            # Check for Y coordinates
            if 'KL_' in line and '_Y' in line and '[Inch]' in line:
                found_y_coords.append(line.strip())
            # Check for klimps 11-30
            if 'KL_11' in line or 'KL_21' in line or 'KL_30' in line:
                found_klimps.append(line.strip())
        
        # Display results
        print(f"Found {len(found_rotations)} rotation parameters")
        if found_rotations:
            print("\nSample rotation parameters:")
            for rot in found_rotations[:5]:
                print(f"  {rot}")
        
        print(f"\nFound {len(found_y_coords)} Y-coordinate parameters")
        if found_y_coords:
            print("\nSample Y-coordinates:")
            for y in found_y_coords[:5]:
                print(f"  {y}")
        
        print(f"\nFound references to side klimps (11-30):")
        if found_klimps:
            for klimp in found_klimps[:10]:
                print(f"  {klimp}")
        
        print("\n" + "-" * 60)
        print("30-Klimp System Test Complete!")
        
    else:
        print(f"FAILED: {message}")
        
except Exception as e:
    print(f"ERROR: {str(e)}")
    import traceback
    traceback.print_exc()