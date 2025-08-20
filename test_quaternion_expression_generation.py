"""
Test script to generate a new expression file with quaternion system integration.
This will create a new expression file and verify that quaternion variables are included.
"""

import sys
import os
import datetime

# Add the autocrate directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'autocrate'))

try:
    # Import the main generation function
    from autocrate.nx_expressions_generator import generate_crate_expressions_logic
    
    print("Testing quaternion integration with a new expression file...")
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
        'output_filename': f"test_quaternions_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.exp"
    }
    
    print("Generation parameters:")
    for key, value in test_params.items():
        print(f"  {key}: {value}")
    
    print("\nGenerating expression file with quaternion system...")
    
    # Generate the expressions
    result, message = generate_crate_expressions_logic(**test_params)
    
    print(f"Generation result: {result}")
    print(f"Message: {message}")
    
    if result:
        # Check the generated file (it's created in the root directory)
        exp_file = test_params['output_filename']
        
        if os.path.exists(exp_file):
            print(f"\nSuccess! Expression file created: {exp_file}")
            
            # Read and analyze the file
            with open(exp_file, 'r') as f:
                content = f.read()
            
            lines = content.split('\n')
            print(f"Total lines in file: {len(lines)}")
            
            # Look for quaternion variables
            quaternion_lines = [line for line in lines if '_Q_' in line and not line.strip().startswith('//')]
            unit_vector_lines = [line for line in lines if '_DIR_' in line and not line.strip().startswith('//')]
            axis_angle_lines = [line for line in lines if ('_AXIS_' in line or '_ANGLE' in line) and not line.strip().startswith('//')]
            kl_lines = [line for line in lines if line.strip().startswith('KL_') and not line.strip().startswith('//')]
            
            print(f"Found {len(kl_lines)} KL variables total")
            print(f"Found {len(quaternion_lines)} quaternion variables (_Q_)")
            print(f"Found {len(unit_vector_lines)} unit vector variables (_DIR_)")
            print(f"Found {len(axis_angle_lines)} axis-angle variables (_AXIS_, _ANGLE)")
            
            if quaternion_lines:
                print("\n*** SUCCESS! Quaternion variables found! ***")
                print("Sample quaternion variables:")
                for line in quaternion_lines[:12]:
                    print(f"  {line.strip()}")
                
                # Verify the expected structure
                q_w_lines = [line for line in quaternion_lines if '_Q_W' in line]
                q_x_lines = [line for line in quaternion_lines if '_Q_X' in line]
                q_y_lines = [line for line in quaternion_lines if '_Q_Y' in line]
                q_z_lines = [line for line in quaternion_lines if '_Q_Z' in line]
                
                print(f"\nQuaternion component breakdown:")
                print(f"  W (scalar) components: {len(q_w_lines)}")
                print(f"  X (i) components: {len(q_x_lines)}")
                print(f"  Y (j) components: {len(q_y_lines)}")
                print(f"  Z (k) components: {len(q_z_lines)}")
                
                # Should have 30 klimps * 4 quaternion components = 120 quaternion variables
                expected_quaternions = 30 * 4
                print(f"  Expected total: {expected_quaternions}")
                print(f"  Actual total: {len(quaternion_lines)}")
                
                if len(quaternion_lines) == expected_quaternions:
                    print("\n*** PERFECT! All expected quaternion variables are present! ***")
                else:
                    print(f"\n*** WARNING: Expected {expected_quaternions} but found {len(quaternion_lines)} quaternion variables ***")
                
                # Check that unit vectors are still included (for compatibility)
                if unit_vector_lines:
                    print(f"\n*** EXCELLENT! Unit vectors also included for compatibility ({len(unit_vector_lines)} variables)***")
                
                # Check axis-angle representation
                if axis_angle_lines:
                    print(f"\n*** GREAT! Axis-angle representation also included ({len(axis_angle_lines)} variables)***")
                
                # Show some sample values to verify they look reasonable
                print(f"\nSample quaternion values:")
                klimp_1_quaternions = [line for line in quaternion_lines if 'KL_1_Q_' in line]
                for line in klimp_1_quaternions:
                    print(f"  {line.strip()}")
                
            else:
                print("\n*** ERROR: No quaternion variables found in the generated file ***")
                print("This suggests the quaternion integration may not be working correctly.")
                
                # Show some KL variables to verify the file structure
                if kl_lines:
                    print("\nFound these KL variables instead:")
                    for line in kl_lines[:15]:
                        print(f"  {line.strip()}")
        else:
            print(f"*** ERROR: Expression file {exp_file} was not created ***")
    else:
        print("*** ERROR: Expression generation failed ***")
        print("The quaternion integration may have caused an error.")

except Exception as e:
    print(f"*** CRITICAL ERROR: {e} ***")
    import traceback
    traceback.print_exc()
    print("\nThis error suggests there may be an issue with the quaternion integration.")