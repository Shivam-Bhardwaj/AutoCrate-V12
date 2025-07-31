#!/usr/bin/env python
"""
Test script to verify the horizontal splice cleat fix for edge cases.
Specifically tests the 20x20x100 (tall, thin product) scenario where
horizontal splices occur but no vertical intermediate cleats are needed.
"""

import sys
import os
import json

# Add the legacy directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'legacy'))

from front_panel_logic import (
    calculate_front_panel_components,
    calculate_horizontal_splice_positions,
    calculate_horizontal_cleat_sections
)

def test_edge_case_scenario():
    """
    Test the 20x20x100 edge case where:
    - Product is very tall but thin
    - Panel height will be > 48" requiring horizontal splices
    - Panel width is narrow enough that no intermediate vertical cleats are needed
    """
    print("=" * 80)
    print("Testing Edge Case: Tall, Thin Product (20x20x100)")
    print("=" * 80)
    
    # Typical parameters for a 20x20x100 product with standard clearances
    # Front panel might be approximately 30" wide x 106" tall
    test_cases = [
        {
            "name": "Narrow Panel (No Intermediate Vertical Cleats)",
            "width": 30.0,  # Narrow enough to not need intermediate vertical cleats
            "height": 106.0  # Tall enough to require horizontal splices
        },
        {
            "name": "Very Narrow Panel",
            "width": 24.0,  # Even narrower
            "height": 106.0
        },
        {
            "name": "Comparison: Wide Panel (Has Intermediate Vertical Cleats)",
            "width": 60.0,  # Wide enough to need intermediate vertical cleats
            "height": 106.0
        }
    ]
    
    panel_thickness = 0.75
    cleat_thickness = 1.5
    cleat_member_width = 3.5
    
    for test_case in test_cases:
        print(f"\n{'-' * 60}")
        print(f"Test Case: {test_case['name']}")
        print(f"Panel Dimensions: {test_case['width']}\" W x {test_case['height']}\" H")
        print(f"{'-' * 60}")
        
        # Calculate panel components
        panel_data = calculate_front_panel_components(
            test_case['width'],
            test_case['height'],
            panel_thickness,
            cleat_thickness,
            cleat_member_width
        )
        
        # Extract relevant data
        inter_vert_cleats = panel_data.get('intermediate_vertical_cleats', {})
        inter_horiz_cleats = panel_data.get('intermediate_horizontal_cleats', {})
        
        vert_cleat_count = inter_vert_cleats.get('count', 0)
        horiz_cleat_sections = inter_horiz_cleats.get('sections', [])
        horiz_cleat_count = inter_horiz_cleats.get('count', 0)
        
        # Calculate horizontal splice positions
        horiz_splices = calculate_horizontal_splice_positions(
            test_case['width'],
            test_case['height']
        )
        
        print(f"\nVertical Cleats:")
        print(f"  - Edge cleats: 2 (always present)")
        print(f"  - Intermediate vertical cleats: {vert_cleat_count}")
        if vert_cleat_count > 0:
            print(f"  - Positions: {inter_vert_cleats.get('positions_x_centerline', [])}")
        
        print(f"\nHorizontal Splices:")
        print(f"  - Number of horizontal splices: {len(horiz_splices)}")
        if horiz_splices:
            print(f"  - Splice Y positions: {horiz_splices}")
        
        print(f"\nHorizontal Cleats:")
        print(f"  - Number of horizontal cleat sections: {horiz_cleat_count}")
        
        if horiz_cleat_sections:
            print(f"  - Horizontal cleat details:")
            for i, section in enumerate(horiz_cleat_sections):
                print(f"    Section {i+1}:")
                print(f"      - X position: {section['x_pos']:.2f}\"")
                print(f"      - Width: {section['width']:.2f}\"")
                print(f"      - Y centerline: {section['y_pos_centerline']:.2f}\"")
        
        # Verify the fix
        print(f"\nVerification:")
        if len(horiz_splices) > 0:
            if horiz_cleat_count > 0:
                print("  [PASS] Horizontal splices are properly supported with cleats")
            else:
                print("  [FAIL] Horizontal splices exist but NO cleats to support them!")
        else:
            print("  - No horizontal splices needed for this panel size")
        
        # Additional check: ensure cleats exist even without intermediate vertical cleats
        if vert_cleat_count == 0 and len(horiz_splices) > 0:
            if horiz_cleat_count > 0:
                print("  [PASS] Fix working - horizontal cleats created despite no intermediate vertical cleats")
            else:
                print("  [FAIL] Bug still present - no horizontal cleats when no intermediate vertical cleats")

def test_horizontal_cleat_calculation():
    """
    Directly test the calculate_horizontal_cleat_sections function
    """
    print("\n" + "=" * 80)
    print("Direct Test of calculate_horizontal_cleat_sections Function")
    print("=" * 80)
    
    panel_width = 30.0
    cleat_member_width = 3.5
    splice_y_position = 48.0
    
    # Test with no intermediate vertical cleats
    print("\nTest 1: No intermediate vertical cleats")
    vertical_cleats_data = {
        'count': 0,
        'positions_x_centerline': []
    }
    
    sections = calculate_horizontal_cleat_sections(
        panel_width,
        cleat_member_width,
        vertical_cleats_data,
        splice_y_position
    )
    
    print(f"Panel width: {panel_width}\"")
    print(f"Intermediate vertical cleats: {vertical_cleats_data['count']}")
    print(f"Horizontal cleat sections created: {len(sections)}")
    
    if sections:
        print("Section details:")
        for section in sections:
            print(f"  - X: {section['x_pos']:.2f}\", Width: {section['width']:.2f}\"")
    
    if len(sections) > 0:
        print("[PASS] Horizontal cleat section created between edge cleats")
    else:
        print("[FAIL] No horizontal cleat section created")
    
    # Test with intermediate vertical cleats
    print("\nTest 2: With intermediate vertical cleats")
    vertical_cleats_data = {
        'count': 1,
        'positions_x_centerline': [15.0]
    }
    
    sections = calculate_horizontal_cleat_sections(
        panel_width,
        cleat_member_width,
        vertical_cleats_data,
        splice_y_position
    )
    
    print(f"Panel width: {panel_width}\"")
    print(f"Intermediate vertical cleats: {vertical_cleats_data['count']} at {vertical_cleats_data['positions_x_centerline']}")
    print(f"Horizontal cleat sections created: {len(sections)}")
    
    if sections:
        print("Section details:")
        for i, section in enumerate(sections):
            print(f"  Section {i+1} - X: {section['x_pos']:.2f}\", Width: {section['width']:.2f}\"")

if __name__ == "__main__":
    test_edge_case_scenario()
    test_horizontal_cleat_calculation()
    print("\n" + "=" * 80)
    print("Test completed!")
    print("=" * 80)