#!/usr/bin/env python
"""
Test with a very narrow product to ensure we get a panel without intermediate vertical cleats.
"""

import sys
import os

# Add the legacy directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'legacy'))

from nx_expressions_generator import generate_crate_expressions_logic

def test_very_narrow_case():
    """
    Test with a very narrow product (10" wide).
    """
    print("=" * 80)
    print("Testing Very Narrow Product Case")
    print("=" * 80)
    
    # Very narrow product
    test_params = {
        # Product dimensions - very narrow and tall
        'product_weight_lbs': 500.0,
        'product_length_in': 10.0,   # Very short
        'product_width_in': 10.0,     # Very narrow
        'product_actual_height_in': 80.0,  # Tall
        
        # Clearances
        'clearance_each_side_in': 1.0,  # Minimal clearance
        'clearance_above_product_in': 1.0,
        'ground_clearance_in': 4.0,
        
        # Panel materials
        'panel_thickness_in': 0.75,
        'cleat_thickness_in': 1.5,
        'cleat_member_actual_width_in': 3.5,
        
        # Skid options
        'allow_3x4_skids_bool': True,
        
        # Floorboard options
        'floorboard_actual_thickness_in': 1.5,
        'selected_std_lumber_widths': [5.5, 7.25],
        'max_allowable_middle_gap_in': 0.25,
        'min_custom_lumber_width_in': 2.5,
        'force_small_custom_board_bool': False,
        
        # Output
        'output_filename': 'test_very_narrow_output.exp',
        
        # Plywood panel selections
        'plywood_panel_selections': None
    }
    
    print("\nTest Parameters:")
    print(f"  Product: {test_params['product_width_in']}\" W x {test_params['product_length_in']}\" L x {test_params['product_actual_height_in']}\" H")
    
    # Calculate expected panel dimensions
    panel_thickness = test_params['panel_thickness_in'] + test_params['cleat_thickness_in']
    expected_width = test_params['product_width_in'] + 2 * test_params['clearance_each_side_in'] + 2 * panel_thickness
    expected_height = test_params['product_actual_height_in'] + test_params['floorboard_actual_thickness_in'] + test_params['clearance_above_product_in']
    
    print(f"  Expected front/back panel: ~{expected_width:.1f}\" W x {expected_height:.1f}\" H")
    
    # Generate expressions
    success, message = generate_crate_expressions_logic(**test_params)
    
    if not success:
        print(f"\n[FAIL] Expression generation failed: {message}")
        return False
    
    print(f"\n[PASS] Expression generation successful!")
    
    # Read output
    with open(test_params['output_filename'], 'r') as f:
        content = f.read()
    
    # Analyze each panel type
    print("\nPanel Analysis:")
    print("-" * 60)
    
    edge_case_found = False
    bug_found = False
    
    for panel_prefix, panel_name in [('FP', 'Front'), ('BP', 'Back'), ('LP', 'Left'), ('RP', 'Right')]:
        # Get dimensions
        if panel_prefix in ['FP', 'BP']:
            width_marker = f"[Inch]{panel_prefix}_Plywood_Width ="
            height_marker = f"[Inch]{panel_prefix}_Plywood_Height ="
        else:  # Left/Right panels
            width_marker = f"[Inch]{panel_prefix}_Plywood_Length ="
            height_marker = f"[Inch]{panel_prefix}_Plywood_Height ="
        
        width = height = 0
        if width_marker in content:
            start = content.find(width_marker) + len(width_marker)
            end = content.find('\n', start)
            width = float(content[start:end].strip())
        
        if height_marker in content:
            start = content.find(height_marker) + len(height_marker)
            end = content.find('\n', start)
            height = float(content[start:end].strip())
        
        # Get cleat counts
        v_count = h_count = 0
        v_marker = f"{panel_prefix}_Intermediate_Vertical_Cleat_Count ="
        h_marker = f"{panel_prefix}_Intermediate_Horizontal_Cleat_Count ="
        
        if v_marker in content:
            start = content.find(v_marker) + len(v_marker)
            end = content.find('\n', start)
            v_count = int(content[start:end].strip())
        
        if h_marker in content:
            start = content.find(h_marker) + len(h_marker)
            end = content.find('\n', start)
            h_count = int(content[start:end].strip())
        
        # Count active horizontal instances
        active_h = 0
        for i in range(1, 7):
            marker = f"{panel_prefix}_Inter_HC_Inst_{i}_Suppress_Flag ="
            if marker in content:
                start = content.find(marker) + len(marker)
                end = content.find('\n', start)
                if int(content[start:end].strip()) == 1:
                    active_h += 1
        
        print(f"\n{panel_name} Panel ({panel_prefix}):")
        print(f"  Size: {width:.1f}\" x {height:.1f}\"")
        print(f"  Vertical intermediate cleats: {v_count}")
        print(f"  Horizontal cleat sections: {h_count} (active: {active_h})")
        
        # Check for horizontal splices
        needs_h_splice = height > 48
        print(f"  Needs horizontal splice: {'Yes' if needs_h_splice else 'No'}")
        
        # Determine status
        if needs_h_splice and v_count == 0:
            if h_count > 0 and active_h > 0:
                print(f"  STATUS: [PASS] Edge case handled correctly!")
                edge_case_found = True
            else:
                print(f"  STATUS: [FAIL] BUG - No horizontal cleats despite splice!")
                bug_found = True
        elif needs_h_splice and v_count > 0:
            if h_count > 0:
                print(f"  STATUS: Normal case (has both cleat types)")
            else:
                print(f"  STATUS: [WARNING] Has splice but no horizontal cleats")
        else:
            print(f"  STATUS: Panel too short for horizontal splice")
    
    print("\n" + "-" * 60)
    print("Summary:")
    if bug_found:
        print("  [FAIL] Bug detected - horizontal cleats missing in edge case!")
    elif edge_case_found:
        print("  [PASS] Edge case handled correctly - fix is working!")
    else:
        print("  [INFO] No edge case panels found in this configuration")
    
    return not bug_found

if __name__ == "__main__":
    success = test_very_narrow_case()
    print("\n" + "=" * 80)
    print("TEST", "PASSED" if success else "FAILED")
    print("=" * 80)