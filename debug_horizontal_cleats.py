#!/usr/bin/env python
"""
Debug script to trace through the horizontal cleat calculation logic.
"""

import sys
import os

# Add the legacy directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'legacy'))

from front_panel_logic import (
    calculate_front_panel_components,
    calculate_horizontal_splice_positions,
    calculate_horizontal_cleat_sections
)

def debug_panel_calculation():
    """
    Debug the panel calculation with a specific case.
    """
    # Panel dimensions that should trigger horizontal splices but no intermediate vertical cleats
    panel_width = 16.5
    panel_height = 82.5
    panel_thickness = 0.75
    cleat_thickness = 1.5
    cleat_member_width = 3.5
    
    print("=" * 80)
    print("Debug: Panel Calculation")
    print("=" * 80)
    print(f"Panel: {panel_width}\" W x {panel_height}\" H")
    print(f"Cleat member width: {cleat_member_width}\"")
    
    # Calculate components
    print("\n1. Calculating panel components...")
    components = calculate_front_panel_components(
        panel_width, panel_height, panel_thickness, cleat_thickness, cleat_member_width
    )
    
    # Extract intermediate cleat data
    vert_cleats = components.get('intermediate_vertical_cleats', {})
    horiz_cleats = components.get('intermediate_horizontal_cleats', {})
    
    print(f"\n2. Intermediate vertical cleats:")
    print(f"   Count: {vert_cleats.get('count', 0)}")
    print(f"   Positions: {vert_cleats.get('positions_x_centerline', [])}")
    
    print(f"\n3. Horizontal splice positions:")
    splice_positions = calculate_horizontal_splice_positions(panel_width, panel_height)
    print(f"   Splices: {splice_positions}")
    
    print(f"\n4. Intermediate horizontal cleats:")
    print(f"   Count: {horiz_cleats.get('count', 0)}")
    print(f"   Sections: {horiz_cleats.get('sections', [])}")
    
    # Manually test the horizontal cleat calculation
    print("\n5. Manual test of calculate_horizontal_cleat_sections:")
    if splice_positions:
        test_sections = calculate_horizontal_cleat_sections(
            panel_width,
            cleat_member_width,
            vert_cleats,  # Pass the actual vertical cleats data
            splice_positions[0]  # Use first splice
        )
        print(f"   Manual calculation result: {test_sections}")
        
        # Also test with empty vertical cleats explicitly
        print("\n6. Test with explicit empty vertical cleats:")
        empty_vert_cleats = {
            'count': 0,
            'positions_x_centerline': []
        }
        test_sections2 = calculate_horizontal_cleat_sections(
            panel_width,
            cleat_member_width,
            empty_vert_cleats,
            splice_positions[0]
        )
        print(f"   Result: {test_sections2}")
    
    # Check edge-to-edge spacing
    print(f"\n7. Edge-to-edge cleat spacing:")
    edge_to_edge = panel_width - cleat_member_width
    print(f"   Panel width: {panel_width}\"")
    print(f"   Edge-to-edge spacing: {edge_to_edge}\"")
    print(f"   Needs intermediate vertical cleats: {edge_to_edge > 24}")
    
    return components

if __name__ == "__main__":
    result = debug_panel_calculation()
    print("\n" + "=" * 80)
    print("Debug completed")
    print("=" * 80)