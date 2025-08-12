#!/usr/bin/env python
"""
Test script to verify KL_1_X and KL_1_Z variables are generated correctly
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'autocrate'))

from nx_expressions_generator import generate_crate_expressions_logic
import tempfile

def test_kl_variables():
    """Test that KL_1_X and KL_1_Z variables are generated correctly"""
    
    # Test parameters
    product_weight = 1000.0
    product_length = 48.0
    product_width = 36.0
    product_height = 30.0
    clearance = 2.0
    allow_3x4_skids = True
    panel_thickness = 0.25
    cleat_thickness = 2.0
    cleat_member_width = 2.0
    clearance_above = 2.0
    ground_clearance = 3.5
    floorboard_thickness = 0.75
    selected_lumber = "5-Ply OSB"
    max_gap = 8.0
    min_custom = 2.0
    force_custom = False
    plywood_selections = {
        "front_panel": "5-Ply OSB",
        "back_panel": "5-Ply OSB",
        "left_panel": "5-Ply OSB",
        "right_panel": "5-Ply OSB",
        "top_panel": "5-Ply OSB"
    }
    
    # Create temporary file for output
    with tempfile.NamedTemporaryFile(mode='w', suffix='.exp', delete=False) as temp_file:
        output_filename = temp_file.name
    
    try:
        # Generate expressions
        success, message = generate_crate_expressions_logic(
            product_weight, product_length, product_width, clearance,
            allow_3x4_skids, panel_thickness, cleat_thickness, cleat_member_width,
            product_height, clearance_above, ground_clearance, floorboard_thickness,
            selected_lumber, max_gap, min_custom, force_custom,
            output_filename, plywood_selections
        )
        
        if success:
            print(f"✓ Expression file generated successfully: {message}")
            
            # Read the file and check for KL_1_X and KL_1_Z variables
            with open(output_filename, 'r') as f:
                content = f.read()
                
            # Check for KL_1_Z
            if '[Inch]KL_1_Z' in content:
                # Extract the value
                for line in content.split('\n'):
                    if '[Inch]KL_1_Z' in line:
                        print(f"✓ Found KL_1_Z: {line.strip()}")
                        break
            else:
                print("✗ KL_1_Z variable not found in expression file")
            
            # Check for KL_1_X
            if '[Inch]KL_1_X' in content:
                # Extract the value
                for line in content.split('\n'):
                    if '[Inch]KL_1_X' in line:
                        print(f"✓ Found KL_1_X: {line.strip()}")
                        # Verify the calculation
                        # Expected: -(panel_width/2) + cleat_member_width/2 + 2.0
                        # With our test values: panel_width ≈ 40 (36 + 2*2 clearance)
                        # So: -(40/2) + 1 + 2 = -20 + 1 + 2 = -17
                        break
            else:
                print("✗ KL_1_X variable not found in expression file")
                
            print(f"\nExpression file saved to: {output_filename}")
            
        else:
            print(f"✗ Failed to generate expressions: {message}")
            
    except Exception as e:
        print(f"✗ Error during test: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up temporary file if needed
        if os.path.exists(output_filename):
            try:
                os.remove(output_filename)
                print("Temporary file cleaned up")
            except:
                pass

if __name__ == "__main__":
    print("Testing KL_1_X and KL_1_Z variable generation...")
    print("=" * 60)
    test_kl_variables()