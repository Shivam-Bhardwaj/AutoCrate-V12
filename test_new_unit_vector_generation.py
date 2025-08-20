"""
Test script to generate a new expression file with unit vector system integration.
This will create a new expression file and verify that unit vector variables are included.
"""

import sys
import os
import datetime

# Add the autocrate directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'autocrate'))

try:
    # Import the main generation function
    from autocrate.nx_expressions_generator import generate_crate_expressions_logic
    
    print("Testing unit vector integration with a new expression file...")
    print("=" * 60)
    
    # Test parameters - small crate for quick generation
    test_params = {
        'product_weight_lbs': 500,
        'product_length_in': 24.0,
        'product_width_in': 24.0,
        'clearance_each_side_in': 2.0,
        'allow_3x4_skids_bool': True,
        'panel_thickness_in': 0.25,
        'cleat_thickness_in': 2.0,
        'cleat_member_actual_width_in': 3.5,
        'product_actual_height_in': 20.0,
        'clearance_above_product_in': 2.0,
        'ground_clearance_in': 6.0,
        'floorboard_actual_thickness_in': 1.5,
        'selected_std_lumber_widths': [3.5, 5.5, 7.25, 9.25, 11.25],
        'max_allowable_middle_gap_in': 4.0,
        'min_custom_lumber_width_in': 2.0,
        'force_small_custom_board_bool': False,
        'output_filename': f"test_unit_vectors_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.exp"
    }
    
    print("Generation parameters:")
    for key, value in test_params.items():
        print(f"  {key}: {value}")
    
    print("\nGenerating expression file...")
    
    # Generate the expressions
    result, message = generate_crate_expressions_logic(**test_params)
    
    print(f"Generation result: {result}")
    print(f"Message: {message}")
    
    if result:
        # Check the generated file
        exp_file = f"expressions/{test_params['output_filename']}"
        
        if os.path.exists(exp_file):
            print(f"\nSuccess! Expression file created: {exp_file}")
            
            # Read and analyze the file
            with open(exp_file, 'r') as f:
                content = f.read()
            
            lines = content.split('\n')
            print(f"Total lines in file: {len(lines)}")
            
            # Look for unit vector variables
            unit_vector_lines = [line for line in lines if '_DIR_' in line and not line.strip().startswith('//')]
            kl_lines = [line for line in lines if line.strip().startswith('KL_') and not line.strip().startswith('//')]
            
            print(f"Found {len(kl_lines)} KL variables")
            print(f"Found {len(unit_vector_lines)} unit vector direction variables")
            
            if unit_vector_lines:
                print("\n*** SUCCESS! Unit vector variables found! ***")
                print("Sample unit vector variables:")
                for line in unit_vector_lines[:10]:
                    print(f"  {line.strip()}")
                
                # Verify the structure
                x_dir_lines = [line for line in unit_vector_lines if '_X_DIR_' in line]
                y_dir_lines = [line for line in unit_vector_lines if '_Y_DIR_' in line]
                z_dir_lines = [line for line in unit_vector_lines if '_Z_DIR_' in line]
                
                print(f"\nUnit vector breakdown:")
                print(f"  X-direction vectors: {len(x_dir_lines)}")
                print(f"  Y-direction vectors: {len(y_dir_lines)}")
                print(f"  Z-direction vectors: {len(z_dir_lines)}")
                
                # Should have 30 klimps * 3 axes * 3 components = 270 direction variables
                expected_total = 30 * 3 * 3
                print(f"  Expected total: {expected_total}")
                print(f"  Actual total: {len(unit_vector_lines)}")
                
                if len(unit_vector_lines) == expected_total:
                    print("\n*** PERFECT! All expected unit vector variables are present! ***")
                else:
                    print(f"\n*** WARNING: Expected {expected_total} but found {len(unit_vector_lines)} unit vector variables ***")
                
            else:
                print("\n*** ERROR: No unit vector variables found in the generated file ***")
                print("This suggests the integration may not be working correctly.")
                
                # Show some KL variables to verify the file structure
                if kl_lines:
                    print("\nFound these KL variables instead:")
                    for line in kl_lines[:10]:
                        print(f"  {line.strip()}")
        else:
            print(f"*** ERROR: Expression file {exp_file} was not created ***")
    else:
        print("*** ERROR: Expression generation failed ***")
        print("The unit vector integration may have caused an error.")

except Exception as e:
    print(f"*** CRITICAL ERROR: {e} ***")
    import traceback
    traceback.print_exc()
    print("\nThis error suggests there may be an issue with the unit vector integration.")