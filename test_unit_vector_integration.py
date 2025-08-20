"""
Test integration of unit vector system with the main AutoCrate application.
"""

import sys
import os

# Add the autocrate directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'autocrate'))

try:
    from autocrate.nx_expressions_generator import generate_crate_expressions_logic
    
    print("Testing unit vector integration with AutoCrate...")
    
    # Test with standard parameters
    result, message = generate_crate_expressions_logic(
        product_weight_lbs=1000,
        product_length_in=48.0,
        product_width_in=48.0,
        product_height_in=30.0,
        x_clearance_in=2.0,
        y_clearance_in=2.0,
        z_clearance_in=2.0,
        panel_thickness_in=0.25,
        cleat_thickness_in=2.0,
        cleat_member_width_in=3.5,
        output_filename="test_unit_vector_integration.exp",
        logger=None
    )
    
    print(f"Generation result: {result}")
    print(f"Message: {message}")
    
    if result:
        # Check if the file was created and contains unit vector variables
        exp_file = "expressions/test_unit_vector_integration.exp"
        if os.path.exists(exp_file):
            with open(exp_file, 'r') as f:
                content = f.read()
            
            # Look for unit vector variables
            unit_vector_lines = [line for line in content.split('\n') if '_DIR_' in line]
            print(f"Found {len(unit_vector_lines)} unit vector direction variables")
            
            if unit_vector_lines:
                print("Sample unit vector variables:")
                for line in unit_vector_lines[:5]:
                    print(f"  {line}")
                
                print("\n*** UNIT VECTOR INTEGRATION SUCCESSFUL! ***")
            else:
                print("*** WARNING: No unit vector variables found in output ***")
        else:
            print(f"*** ERROR: Output file {exp_file} not found ***")
    else:
        print("*** ERROR: Expression generation failed ***")

except Exception as e:
    print(f"*** ERROR: {e} ***")
    import traceback
    traceback.print_exc()