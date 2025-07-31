#!/usr/bin/env python
"""
Debug script to understand why horizontal splice positions aren't being calculated.
"""

import sys
import os
import math

# Add the legacy directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'legacy'))

from front_panel_logic import calculate_horizontal_splice_positions

def debug_splice_calculation(panel_width, panel_height):
    """
    Debug the splice calculation with detailed output.
    """
    print(f"\nDebug splice calculation for {panel_width}\" x {panel_height}\" panel:")
    print("-" * 60)
    
    # Constants
    MAX_PLYWOOD_WIDTH = 96
    MAX_PLYWOOD_HEIGHT = 48
    
    # Standard arrangement (sheets not rotated)
    sheets_across = math.ceil(panel_width / MAX_PLYWOOD_WIDTH)
    sheets_down = math.ceil(panel_height / MAX_PLYWOOD_HEIGHT)
    standard_count = sheets_across * sheets_down
    standard_h_splices = max(0, sheets_down - 1)
    
    print(f"Standard arrangement (48\" tall sheets):")
    print(f"  Sheets across: {sheets_across}")
    print(f"  Sheets down: {sheets_down}")
    print(f"  Total sheets: {standard_count}")
    print(f"  Horizontal splices: {standard_h_splices}")
    
    # Rotated arrangement (sheets rotated 90 degrees)
    rotated_sheets_across = math.ceil(panel_width / MAX_PLYWOOD_HEIGHT)
    rotated_sheets_down = math.ceil(panel_height / MAX_PLYWOOD_WIDTH)
    rotated_count = rotated_sheets_across * rotated_sheets_down
    rotated_h_splices = max(0, rotated_sheets_down - 1)
    
    print(f"\nRotated arrangement (96\" tall sheets):")
    print(f"  Sheets across: {rotated_sheets_across}")
    print(f"  Sheets down: {rotated_sheets_down}")
    print(f"  Total sheets: {rotated_count}")
    print(f"  Horizontal splices: {rotated_h_splices}")
    
    # Get actual splice positions
    splice_positions = calculate_horizontal_splice_positions(panel_width, panel_height)
    
    print(f"\nCalculated splice positions: {splice_positions}")
    
    # Manual calculation to verify
    if rotated_count <= standard_count:
        print("\nUsing ROTATED arrangement (96\" tall sheets)")
        if rotated_sheets_down > 1:
            # Calculate actual splice positions for rotated arrangement
            manual_splices = []
            # Place smaller panel at bottom
            remainder_height = panel_height - ((rotated_sheets_down - 1) * MAX_PLYWOOD_WIDTH)
            # First splice is at the top of the bottom (remainder) panel
            manual_splices.append(remainder_height)
            # Additional splices every 96" after that
            for i in range(1, rotated_sheets_down - 1):
                manual_splices.append(remainder_height + i * MAX_PLYWOOD_WIDTH)
            print(f"Manual calculation: {manual_splices}")
    else:
        print("\nUsing STANDARD arrangement (48\" tall sheets)")
        if sheets_down > 1:
            # Calculate actual splice positions for standard arrangement
            manual_splices = []
            # Place smaller panel at bottom
            remainder_height = panel_height - ((sheets_down - 1) * MAX_PLYWOOD_HEIGHT)
            # First splice is at the top of the bottom (remainder) panel
            manual_splices.append(remainder_height)
            # Additional splices every 48" after that
            for i in range(1, sheets_down - 1):
                manual_splices.append(remainder_height + i * MAX_PLYWOOD_HEIGHT)
            print(f"Manual calculation: {manual_splices}")
    
    return splice_positions

# Test various panel sizes
test_cases = [
    (16.5, 82.5),  # The failing case
    (30.0, 106.0), # From earlier test
    (24.0, 50.0),  # Just over 48"
    (48.0, 96.0),  # Exactly one sheet each dimension
    (50.0, 100.0), # Slightly over one sheet
]

print("=" * 80)
print("Debugging Horizontal Splice Position Calculations")
print("=" * 80)

for width, height in test_cases:
    debug_splice_calculation(width, height)