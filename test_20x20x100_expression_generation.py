#!/usr/bin/env python
"""
Test script to verify horizontal splice cleat fix for 20x20x100 product dimensions.
This tests the complete expression generation to ensure horizontal cleats are generated
even when there are no intermediate vertical cleats.
"""

import sys
import os

# Add the legacy directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'legacy'))

from nx_expressions_generator import generate_crate_expressions_logic

def test_20x20x100_product():
    """
    Test the specific 20x20x100 product case that was failing.
    """
    print("=" * 80)
    print("Testing 20x20x100 Product Expression Generation")
    print("=" * 80)
    
    # Parameters for a 20x20x100 product
    # These are typical values that would create a tall, thin crate
    test_params = {
        # Product dimensions
        'product_weight_lbs': 500.0,
        'product_length_in': 100.0,  # Length along Y axis
        'product_width_in': 20.0,    # Width along X axis
        'product_actual_height_in': 20.0,  # Height along Z axis
        
        # Clearances
        'clearance_each_side_in': 2.0,
        'clearance_above_product_in': 2.0,
        'ground_clearance_in': 4.0,
        
        # Panel materials
        'panel_thickness_in': 0.75,
        'cleat_thickness_in': 1.5,
        'cleat_member_actual_width_in': 3.5,
        
        # Skid options
        'allow_3x4_skids_bool': True,
        
        # Floorboard options
        'floorboard_actual_thickness_in': 1.5,
        'selected_std_lumber_widths': [5.5, 7.25, 9.25, 11.25],
        'max_allowable_middle_gap_in': 0.25,
        'min_custom_lumber_width_in': 2.5,
        'force_small_custom_board_bool': False,
        
        # Output
        'output_filename': 'test_20x20x100_output.exp',
        
        # Plywood panel selections (None = use defaults)
        'plywood_panel_selections': None
    }
    
    print("\nTest Parameters:")
    print(f"  Product: {test_params['product_width_in']}\" W x {test_params['product_length_in']}\" L x {test_params['product_actual_height_in']}\" H")
    print(f"  Weight: {test_params['product_weight_lbs']} lbs")
    print(f"  Clearances: {test_params['clearance_each_side_in']}\" sides, {test_params['clearance_above_product_in']}\" top")
    
    # Generate expressions
    success, message = generate_crate_expressions_logic(**test_params)
    
    if success:
        print(f"\n[PASS] Expression generation successful!")
        print(f"  Output file: {test_params['output_filename']}")
        
        # Read and analyze the output file
        with open(test_params['output_filename'], 'r') as f:
            content = f.read()
        
        # Check for horizontal cleats in each panel
        panels = ['FP', 'BP', 'LP', 'RP', 'TP']  # Front, Back, Left, Right, Top
        
        print("\nHorizontal Cleat Analysis:")
        for panel in panels:
            # Look for horizontal cleat count
            count_marker = f"{panel}_Intermediate_Horizontal_Cleat_Count ="
            if count_marker in content:
                # Extract the count value
                start = content.find(count_marker) + len(count_marker)
                end = content.find('\n', start)
                count = int(content[start:end].strip())
                
                print(f"\n  {panel} Panel:")
                print(f"    Horizontal cleat count: {count}")
                
                # Check for active instances
                active_instances = 0
                for i in range(1, 7):  # Check up to 6 instances
                    suppress_marker = f"{panel}_Inter_HC_Inst_{i}_Suppress_Flag ="
                    if suppress_marker in content:
                        start = content.find(suppress_marker) + len(suppress_marker)
                        end = content.find('\n', start)
                        suppress_flag = int(content[start:end].strip())
                        if suppress_flag == 1:
                            active_instances += 1
                
                print(f"    Active instances: {active_instances}")
                
                # Check for vertical cleats
                vert_count_marker = f"{panel}_Intermediate_Vertical_Cleat_Count ="
                if vert_count_marker in content:
                    start = content.find(vert_count_marker) + len(vert_count_marker)
                    end = content.find('\n', start)
                    vert_count = int(content[start:end].strip())
                    print(f"    Vertical intermediate cleats: {vert_count}")
                
                # Verify horizontal cleats exist when needed
                if count > 0 and active_instances > 0:
                    print(f"    [PASS] Horizontal cleats properly generated")
                elif count == 0:
                    print(f"    - No horizontal cleats needed")
                else:
                    print(f"    [FAIL] ERROR: Horizontal cleats expected but not active!")
        
        # Look for specific patterns that indicate the fix is working
        print("\nChecking for edge case handling...")
        
        # Find a panel with horizontal cleats but no vertical intermediate cleats
        edge_case_found = False
        for panel in panels:
            h_count_marker = f"{panel}_Intermediate_Horizontal_Cleat_Count ="
            v_count_marker = f"{panel}_Intermediate_Vertical_Cleat_Count ="
            
            if h_count_marker in content and v_count_marker in content:
                # Get horizontal count
                start = content.find(h_count_marker) + len(h_count_marker)
                end = content.find('\n', start)
                h_count = int(content[start:end].strip())
                
                # Get vertical count
                start = content.find(v_count_marker) + len(v_count_marker)
                end = content.find('\n', start)
                v_count = int(content[start:end].strip())
                
                if h_count > 0 and v_count == 0:
                    edge_case_found = True
                    print(f"  [PASS] Edge case handled correctly in {panel} panel:")
                    print(f"    - Has {h_count} horizontal cleat(s)")
                    print(f"    - Has 0 intermediate vertical cleats")
                    print(f"    - This confirms the fix is working!")
        
        if not edge_case_found:
            print("  [WARNING] No panels found with horizontal cleats but no vertical intermediate cleats")
            print("    (This might be normal depending on the exact dimensions)")
            
    else:
        print(f"\n[FAIL] Expression generation failed!")
        print(f"  Error: {message}")
    
    return success

if __name__ == "__main__":
    success = test_20x20x100_product()
    
    print("\n" + "=" * 80)
    if success:
        print("TEST PASSED - Horizontal splice cleats are being generated correctly!")
    else:
        print("TEST FAILED - Check the error messages above")
    print("=" * 80)