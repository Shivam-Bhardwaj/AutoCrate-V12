#!/usr/bin/env python
"""
Test KL_1_X position to verify it's 2 inches from cleat edge, not overlapping
"""

import glob
import os

# Find most recent expression file
expression_files = glob.glob("expressions/quick_test/*.exp")
if expression_files:
    expression_files.sort(key=os.path.getmtime, reverse=True)
    latest_file = expression_files[0]
    
    print(f"Checking: {os.path.basename(latest_file)}")
    print("=" * 60)
    
    with open(latest_file, 'r') as f:
        lines = f.readlines()
    
    # Extract relevant values
    panel_width = None
    cleat_member_width = None
    kl_1_x = None
    
    for line in lines:
        if '[Inch]PANEL_Front_Assy_Overall_Width' in line:
            panel_width = float(line.split('=')[1].strip())
        elif '[Inch]FP_Vertical_Cleat_Material_Member_Width' in line:
            cleat_member_width = float(line.split('=')[1].strip())
        elif '[Inch]KL_1_X' in line:
            kl_1_x_line = line
            kl_1_x = float(line.split('=')[1].split('//')[0].strip())
    
    if panel_width and cleat_member_width and kl_1_x is not None:
        print(f"Panel Width: {panel_width:.3f} inches")
        print(f"Cleat Member Width: {cleat_member_width:.3f} inches")
        print(f"KL_1_X from expression: {kl_1_x:.3f} inches")
        print("")
        
        # Calculate expected positions
        left_edge_of_panel = -(panel_width / 2)
        left_cleat_centerline = left_edge_of_panel + (cleat_member_width / 2)
        left_cleat_right_edge = left_cleat_centerline + (cleat_member_width / 2)
        expected_kl_1_x = left_cleat_right_edge + 2.0
        
        print("Position calculations:")
        print(f"  Left edge of panel: {left_edge_of_panel:.3f}")
        print(f"  Left cleat centerline: {left_cleat_centerline:.3f}")
        print(f"  Left cleat right edge: {left_cleat_right_edge:.3f}")
        print(f"  Expected KL_1_X (2\" from edge): {expected_kl_1_x:.3f}")
        print("")
        
        # Check for overlap
        distance_from_cleat_edge = kl_1_x - left_cleat_right_edge
        
        print("Verification:")
        print(f"  Distance from cleat edge: {distance_from_cleat_edge:.3f} inches")
        
        if distance_from_cleat_edge < 0:
            print(f"  ERROR: Klimp overlaps cleat by {abs(distance_from_cleat_edge):.3f} inches!")
        elif distance_from_cleat_edge < 2.0:
            print(f"  WARNING: Klimp is only {distance_from_cleat_edge:.3f} inches from cleat (should be 2.0)")
        else:
            print(f"  OK: Klimp is properly spaced {distance_from_cleat_edge:.3f} inches from cleat edge")
            
        # Show the expression line
        print("\nExpression line:")
        print(f"  {kl_1_x_line.strip()}")
    else:
        print("Could not find all required values in expression file")
else:
    print("No expression files found")