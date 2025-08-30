#!/usr/bin/env python3
"""
Compare NX expression outputs between desktop and web versions.
This script identifies the exact differences in the generated expressions.
"""

import sys
import os
import json
import tempfile
from datetime import datetime

# Add autocrate to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'autocrate'))

# Import the desktop version
from autocrate.nx_expressions_generator import generate_crate_expressions_logic

def generate_desktop_nx(params):
    """Generate NX expressions using desktop version."""
    
    # Create temp output file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.exp', delete=False) as f:
        output_file = f.name
    
    try:
        # Generate expressions
        success, message = generate_crate_expressions_logic(
            **params,
            output_filename=output_file,
            plywood_panel_selections=None
        )
        
        if not success:
            print(f"Desktop generation failed: {message}")
            return None
            
        # Read the generated file
        with open(output_file, 'r') as f:
            content = f.read()
            
        return content
        
    finally:
        # Clean up temp file
        if os.path.exists(output_file):
            os.remove(output_file)

def parse_nx_expressions(content):
    """Parse NX expression file content to extract key values."""
    values = {}
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('//'):
            continue
            
        # Parse expression lines
        if '=' in line:
            parts = line.split('=')
            if len(parts) == 2:
                key = parts[0].strip()
                value = parts[1].strip()
                
                # Remove units and brackets
                if key.startswith('['):
                    bracket_end = key.find(']')
                    if bracket_end > 0:
                        key = key[bracket_end+1:].strip()
                        
                # Convert to float if possible
                try:
                    value = float(value)
                except ValueError:
                    pass
                    
                values[key] = value
    
    return values

def main():
    """Main comparison function."""
    print("="*80)
    print("NX Expression Generation Detailed Comparison")
    print("="*80)
    print()
    
    # Test parameters
    params = {
        'product_weight_lbs': 1000,
        'product_length_in': 96,
        'product_width_in': 48,
        'clearance_each_side_in': 2,
        'allow_3x4_skids_bool': True,
        'panel_thickness_in': 0.75,
        'cleat_thickness_in': 1.5,
        'cleat_member_actual_width_in': 3.5,
        'product_actual_height_in': 30,
        'clearance_above_product_in': 2,
        'ground_clearance_in': 4,
        'floorboard_actual_thickness_in': 1.5,
        'selected_std_lumber_widths': [6.0, 4.0, 2.0],
        'max_allowable_middle_gap_in': 6,
        'min_custom_lumber_width_in': 1.5,
        'force_small_custom_board_bool': False
    }
    
    # Generate desktop NX expressions
    print("Generating desktop NX expressions...")
    desktop_content = generate_desktop_nx(params)
    
    if desktop_content:
        desktop_values = parse_nx_expressions(desktop_content)
        
        # Key dimensions to display
        key_dimensions = [
            ('crate_overall_width_OD', 'Overall Width OD'),
            ('crate_overall_length_OD', 'Overall Length OD'),
            ('PANEL_Front_Assy_Overall_Width', 'Front Panel Width'),
            ('PANEL_Front_Assy_Overall_Height', 'Front Panel Height'),
            ('PANEL_Back_Assy_Overall_Width', 'Back Panel Width'),
            ('PANEL_Back_Assy_Overall_Height', 'Back Panel Height'),
            ('PANEL_End_Assy_Overall_Length_Face', 'End Panel Length'),
            ('PANEL_End_Assy_Overall_Height', 'End Panel Height'),
            ('CALC_Skid_Count', 'Skid Count'),
            ('CALC_Skid_Pitch', 'Skid Pitch'),
            ('FB_Board_Actual_Length', 'Floorboard Length'),
        ]
        
        print("\n" + "="*40)
        print("DESKTOP NX EXPRESSION VALUES:")
        print("="*40)
        for key, label in key_dimensions:
            value = desktop_values.get(key, 'N/A')
            print(f"{label:25s}: {value}")
        
        # Save full results
        output_file = f"desktop_nx_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(desktop_values, f, indent=2)
        print(f"\nFull desktop results saved to: {output_file}")
        
        # Also save the raw expression file for comparison
        exp_output_file = "desktop_nx_output.exp"
        with open(exp_output_file, 'w') as f:
            f.write(desktop_content)
        print(f"Desktop NX expressions saved to: {exp_output_file}")
        
        # Print instructions for web comparison
        print("\n" + "="*80)
        print("NEXT STEPS FOR COMPARISON:")
        print("="*80)
        print("1. Open the web app at http://localhost:3000")
        print("2. Enter these parameters:")
        print("   - Product Length: 96\"")
        print("   - Product Width: 48\"")
        print("   - Product Height: 30\"")
        print("   - Product Weight: 1000 lbs")
        print("   - Side Clearance: 2\"")
        print("3. Click 'Generate NX Expressions'")
        print("4. Download the generated .exp file")
        print("5. Compare the web .exp file with 'desktop_nx_output.exp'")
        print("\nExpected Desktop Values:")
        print(f"   - Overall Width OD: {desktop_values.get('crate_overall_width_OD', 'N/A')}\"")
        print(f"   - Overall Length OD: {desktop_values.get('crate_overall_length_OD', 'N/A')}\"")
        print(f"   - Front Panel Width: {desktop_values.get('PANEL_Front_Assy_Overall_Width', 'N/A')}\"")
        print(f"   - Front Panel Height: {desktop_values.get('PANEL_Front_Assy_Overall_Height', 'N/A')}\"")
        
    else:
        print("[ERROR] Desktop generation failed")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
