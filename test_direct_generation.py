#!/usr/bin/env python
"""
Direct test of expression generation to verify KL_1_X and KL_1_Z
"""

import sys
import os
from datetime import datetime

# Add autocrate to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'autocrate'))

# Import the generator
from nx_expressions_generator import generate_crate_expressions_logic

def test_generation():
    # Test parameters
    params = {
        'product_weight_lbs': 1000.0,
        'product_length_in': 48.0,
        'product_width_in': 36.0,
        'clearance_each_side_in': 2.0,
        'allow_3x4_skids_bool': True,
        'panel_thickness_in': 0.25,
        'cleat_thickness_in': 2.0,
        'cleat_member_actual_width_in': 2.0,
        'product_actual_height_in': 30.0,
        'clearance_above_product_in': 2.0,
        'ground_clearance_in': 3.5,
        'floorboard_actual_thickness_in': 0.75,
        'selected_lumber_str': "2x4",  # Use standard lumber size
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
    
    # Generate output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"expressions/test_KL_{timestamp}.exp"
    
    # Make sure expressions directory exists
    os.makedirs("expressions", exist_ok=True)
    
    print("Generating expression file with KL_1_X and KL_1_Z variables...")
    print("Parameters:")
    print(f"  Product: {params['product_length_in']} x {params['product_width_in']} x {params['product_actual_height_in']} inches")
    print(f"  Weight: {params['product_weight_lbs']} lbs")
    print(f"  Cleat member width: {params['cleat_member_actual_width_in']} inches")
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
            print(f"SUCCESS: Expression file generated: {output_file}")
            
            # Read and check for variables
            with open(output_file, 'r') as f:
                content = f.read()
            
            print("\nChecking for KL variables:")
            print("-" * 60)
            
            # Find KL_1_Z
            for line in content.split('\n'):
                if '[Inch]KL_1_Z' in line:
                    print(f"KL_1_Z: {line.strip()}")
                    break
            
            # Find KL_1_X
            for line in content.split('\n'):
                if '[Inch]KL_1_X' in line:
                    print(f"KL_1_X: {line.strip()}")
                    break
            
            # Calculate expected values
            print("\nExpected calculations:")
            print("-" * 60)
            
            # Panel width calculation
            panel_total_thickness = params['cleat_thickness_in'] + params['panel_thickness_in']
            front_panel_width = params['product_width_in'] + (2 * params['clearance_each_side_in']) + (2 * panel_total_thickness)
            
            # Expected KL_1_X: -(panel_width/2) + cleat_member_width/2 + 2.0
            expected_kl_x = -(front_panel_width/2) + params['cleat_member_actual_width_in']/2 + 2.0
            
            print(f"Front panel width: {front_panel_width:.3f} inches")
            print(f"Expected KL_1_X: {expected_kl_x:.3f} inches")
            print(f"  Formula: -(panel_width/2) + cleat_member_width/2 + 2.0")
            print(f"  = -({front_panel_width:.3f}/2) + {params['cleat_member_actual_width_in']:.3f}/2 + 2.0")
            print(f"  = {-(front_panel_width/2):.3f} + {params['cleat_member_actual_width_in']/2:.3f} + 2.0")
            print(f"  = {expected_kl_x:.3f}")
            
        else:
            print(f"FAILED: {message}")
            
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_generation()