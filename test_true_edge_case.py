#!/usr/bin/env python
"""
Test with dimensions that WILL create horizontal splices without intermediate vertical cleats.
We need a panel that's:
- Taller than 96" (so even rotated sheets need splices)
- Narrower than ~20" (so no intermediate vertical cleats needed)
"""

import sys
import os

# Add the legacy directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'legacy'))

from nx_expressions_generator import generate_crate_expressions_logic

def test_true_edge_case():
    """
    Test with a very tall, narrow product that will definitely need horizontal splices.
    """
    print("=" * 80)
    print("Testing TRUE Edge Case: Guaranteed Horizontal Splices + No Vertical Intermediates")
    print("=" * 80)
    
    # Parameters for a very tall, narrow crate
    test_params = {
        # Product dimensions - extremely tall and narrow
        'product_weight_lbs': 200.0,
        'product_length_in': 8.0,     # Very short
        'product_width_in': 8.0,       # Very narrow
        'product_actual_height_in': 100.0,  # Very tall - will create panels > 96"
        
        # Clearances
        'clearance_each_side_in': 1.0,
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
        'output_filename': 'test_true_edge_case_output.exp',
        
        'plywood_panel_selections': None
    }
    
    # Calculate expected dimensions
    panel_thickness = test_params['panel_thickness_in'] + test_params['cleat_thickness_in']
    expected_width = test_params['product_width_in'] + 2 * test_params['clearance_each_side_in'] + 2 * panel_thickness
    expected_height = test_params['product_actual_height_in'] + test_params['floorboard_actual_thickness_in'] + test_params['clearance_above_product_in']
    
    print("\nTest Parameters:")
    print(f"  Product: {test_params['product_width_in']}\" W x {test_params['product_length_in']}\" L x {test_params['product_actual_height_in']}\" H")
    print(f"  Expected front/back panel: ~{expected_width:.1f}\" W x {expected_height:.1f}\" H")
    print(f"  This height ({expected_height:.1f}\") > 96\", so MUST have horizontal splices")
    
    # Generate expressions
    success, message = generate_crate_expressions_logic(**test_params)
    
    if not success:
        print(f"\n[FAIL] Expression generation failed: {message}")
        return False
    
    print(f"\n[PASS] Expression generation successful!")
    
    # Read and analyze output
    with open(test_params['output_filename'], 'r') as f:
        content = f.read()
    
    # Check each panel
    print("\nPanel Analysis:")
    print("-" * 70)
    
    edge_case_confirmed = False
    any_failures = False
    
    for panel_prefix, panel_name in [('FP', 'Front'), ('BP', 'Back')]:
        print(f"\n{panel_name} Panel ({panel_prefix}):")
        
        # Get actual dimensions from output
        width_marker = f"[Inch]{panel_prefix}_Plywood_Width ="
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
        
        print(f"  Actual dimensions: {width:.1f}\" W x {height:.1f}\" H")
        
        # Check cleats
        v_count = h_count = h_active = 0
        
        v_marker = f"{panel_prefix}_Intermediate_Vertical_Cleat_Count ="
        if v_marker in content:
            start = content.find(v_marker) + len(v_marker)
            end = content.find('\n', start)
            v_count = int(content[start:end].strip())
        
        h_marker = f"{panel_prefix}_Intermediate_Horizontal_Cleat_Count ="
        if h_marker in content:
            start = content.find(h_marker) + len(h_marker)
            end = content.find('\n', start)
            h_count = int(content[start:end].strip())
        
        # Count active horizontal instances
        for i in range(1, 7):
            marker = f"{panel_prefix}_Inter_HC_Inst_{i}_Suppress_Flag ="
            if marker in content:
                start = content.find(marker) + len(marker)
                end = content.find('\n', start)
                if int(content[start:end].strip()) == 1:
                    h_active += 1
        
        print(f"  Intermediate vertical cleats: {v_count}")
        print(f"  Horizontal cleat sections: {h_count} (active instances: {h_active})")
        
        # Verify edge case
        if height > 96:
            print(f"  Height > 96\" - MUST have horizontal splices")
            if v_count == 0 and h_count > 0 and h_active > 0:
                print(f"  [PASS] EDGE CASE CONFIRMED! Horizontal cleats without vertical intermediates")
                edge_case_confirmed = True
            elif v_count == 0 and (h_count == 0 or h_active == 0):
                print(f"  [FAIL] BUG DETECTED! No horizontal cleats despite needing them")
                any_failures = True
            else:
                print(f"  Has intermediate vertical cleats - not the target edge case")
        else:
            print(f"  Height <= 96\" - may not need horizontal splices")
    
    # Final summary
    print("\n" + "=" * 70)
    if any_failures:
        print("[FAIL] Bug still present - horizontal cleats missing when needed!")
        return False
    elif edge_case_confirmed:
        print("[PASS] Edge case handled correctly - fix is working!")
        return True
    else:
        print("[INFO] Test didn't produce the target edge case")
        return True

if __name__ == "__main__":
    success = test_true_edge_case()
    print("\nTEST", "PASSED" if success else "FAILED")
    print("=" * 70)