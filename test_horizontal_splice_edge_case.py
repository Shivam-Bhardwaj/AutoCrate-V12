#!/usr/bin/env python
"""
Test script specifically designed to trigger the edge case where:
- Panels need horizontal splices (height > 48")
- Panels don't need intermediate vertical cleats (width < ~48")
"""

import sys
import os

# Add the legacy directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'legacy'))

from nx_expressions_generator import generate_crate_expressions_logic

def test_edge_case_dimensions():
    """
    Test with dimensions specifically chosen to create the edge case.
    """
    print("=" * 80)
    print("Testing Edge Case: Horizontal Splices without Intermediate Vertical Cleats")
    print("=" * 80)
    
    # Parameters designed to create a panel that's:
    # - Narrow enough to not need intermediate vertical cleats
    # - Tall enough to need horizontal splices
    test_params = {
        # Product dimensions - tall and thin
        'product_weight_lbs': 1000.0,
        'product_length_in': 20.0,   # Short length
        'product_width_in': 20.0,     # Narrow width  
        'product_actual_height_in': 90.0,  # Very tall - this will create tall panels
        
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
        'output_filename': 'test_edge_case_output.exp',
        
        # Plywood panel selections (None = use defaults)
        'plywood_panel_selections': None
    }
    
    print("\nTest Parameters:")
    print(f"  Product: {test_params['product_width_in']}\" W x {test_params['product_length_in']}\" L x {test_params['product_actual_height_in']}\" H")
    print(f"  Expected panel height: ~{test_params['product_actual_height_in'] + test_params['floorboard_actual_thickness_in'] + test_params['clearance_above_product_in']}\" (needs horizontal splice)")
    print(f"  Expected panel width: ~{test_params['product_width_in'] + 2 * test_params['clearance_each_side_in'] + 2 * (test_params['panel_thickness_in'] + test_params['cleat_thickness_in'])}\" (no intermediate verticals)")
    
    # Generate expressions
    success, message = generate_crate_expressions_logic(**test_params)
    
    if success:
        print(f"\n[PASS] Expression generation successful!")
        
        # Read and analyze the output file
        with open(test_params['output_filename'], 'r') as f:
            content = f.read()
        
        # Check front and back panels specifically
        print("\nAnalyzing Front and Back Panels (most likely to show edge case):")
        
        for panel in ['FP', 'BP']:
            print(f"\n{panel} Panel Analysis:")
            
            # Get panel dimensions
            width_marker = f"[Inch]{panel}_Plywood_Width ="
            height_marker = f"[Inch]{panel}_Plywood_Height ="
            
            if width_marker in content and height_marker in content:
                # Extract width
                start = content.find(width_marker) + len(width_marker)
                end = content.find('\n', start)
                width = float(content[start:end].strip())
                
                # Extract height
                start = content.find(height_marker) + len(height_marker)
                end = content.find('\n', start)
                height = float(content[start:end].strip())
                
                print(f"  Dimensions: {width:.1f}\" W x {height:.1f}\" H")
                print(f"  Needs horizontal splice: {'Yes' if height > 48 else 'No'} (height > 48\")")
                print(f"  Needs intermediate vertical cleats: {'Yes' if width > 48 else 'Maybe'} (depends on spacing)")
            
            # Check cleat counts
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
                
                print(f"  Intermediate vertical cleats: {v_count}")
                print(f"  Horizontal cleat sections: {h_count}")
                
                # Check for active horizontal cleat instances
                active_h_instances = 0
                for i in range(1, 7):
                    suppress_marker = f"{panel}_Inter_HC_Inst_{i}_Suppress_Flag ="
                    if suppress_marker in content:
                        start = content.find(suppress_marker) + len(suppress_marker)
                        end = content.find('\n', start)
                        if int(content[start:end].strip()) == 1:
                            active_h_instances += 1
                
                print(f"  Active horizontal cleat instances: {active_h_instances}")
                
                # Check if this is the edge case
                if height > 48 and v_count == 0 and h_count > 0:
                    print(f"  [PASS] EDGE CASE CONFIRMED - Horizontal cleats without intermediate verticals!")
                elif height > 48 and v_count == 0 and h_count == 0:
                    print(f"  [FAIL] BUG DETECTED - Should have horizontal cleats but doesn't!")
                elif height <= 48:
                    print(f"  - Panel too short to need horizontal splices")
                else:
                    print(f"  - Has intermediate vertical cleats, not the edge case")
        
        return True
    else:
        print(f"\n[FAIL] Expression generation failed!")
        print(f"  Error: {message}")
        return False

if __name__ == "__main__":
    success = test_edge_case_dimensions()
    
    print("\n" + "=" * 80)
    if success:
        print("Test completed - check results above")
    else:
        print("Test failed - check error messages")
    print("=" * 80)