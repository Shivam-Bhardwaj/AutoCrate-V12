#!/usr/bin/env python3
"""
Trace desktop calculation to understand the exact values.
"""

import sys
import os
import math

# Add autocrate to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'autocrate'))

# Import desktop functions
from autocrate.plywood_layout_generator import calculate_plywood_layout, extract_vertical_splice_positions

def calculate_vertical_cleat_material_needed(panel_width, panel_height, cleat_member_width):
    """Desktop version of the function."""
    MIN_CLEAT_SPACING = 0.25
    
    # Generate plywood layout
    plywood_sheets = calculate_plywood_layout(panel_width, panel_height)
    
    # Extract vertical splice positions
    vertical_splices = extract_vertical_splice_positions(plywood_sheets)
    
    if not vertical_splices:
        return 0.0
    
    # Calculate edge cleat positions
    left_edge_cleat_centerline = cleat_member_width / 2.0
    right_edge_cleat_centerline = panel_width - (cleat_member_width / 2.0)
    
    # Check if any splice is too close to the right edge
    material_needed = 0.0
    for splice_x in vertical_splices:
        # Check clearance from right edge cleat
        right_clearance = right_edge_cleat_centerline - splice_x - cleat_member_width
        
        # If splice cleat would be too close to right edge cleat, calculate material needed
        if right_clearance < MIN_CLEAT_SPACING:
            # Calculate how much we need to extend the panel
            extension_needed = MIN_CLEAT_SPACING - right_clearance + cleat_member_width
            # Round up to nearest 0.25"
            extension_needed = math.ceil(extension_needed / 0.25) * 0.25
            material_needed = max(material_needed, extension_needed)
    
    return material_needed

# Test parameters
product_width = 48
product_length = 96
product_height = 30
clearance = 2
panel_thickness = 0.75
cleat_thickness = 1.5
cleat_member_width = 3.5
clearance_above = 2
ground_clearance = 4
floorboard_thickness = 1.5
skid_height = 3.5

print("="*60)
print("TRACING DESKTOP CALCULATION LOGIC")
print("="*60)
print()

# Initial crate dimensions
crate_overall_width_od = product_width + (2 * clearance)
skid_model_length = product_length + (2 * clearance)
crate_overall_length_od = skid_model_length

print(f"Initial crate_overall_width_od: {crate_overall_width_od}")
print(f"Initial crate_overall_length_od: {crate_overall_length_od}")
print()

# Panel assembly calculations
panel_assembly_overall_thickness = panel_thickness + cleat_thickness
print(f"panel_assembly_overall_thickness: {panel_assembly_overall_thickness}")

# Front/Back panels
front_panel_calc_depth = panel_assembly_overall_thickness
back_panel_calc_depth = panel_assembly_overall_thickness

# End panels (sandwiched between front and back)
end_panel_calc_length = crate_overall_length_od - front_panel_calc_depth - back_panel_calc_depth
end_panel_calc_height_base = floorboard_thickness + product_height + clearance_above
end_panel_calc_height = skid_height + floorboard_thickness + product_height + clearance_above - ground_clearance
end_panel_calc_depth = panel_assembly_overall_thickness

print(f"end_panel_calc_length (initial): {end_panel_calc_length}")
print(f"end_panel_calc_height: {end_panel_calc_height}")
print()

# Front/Back panel width calculation
panel_total_thickness = cleat_thickness + panel_thickness
front_panel_calc_width = product_width + (2 * clearance) + (2 * panel_total_thickness)
front_panel_calc_height = end_panel_calc_height_base

print(f"front_panel_calc_width (initial): {front_panel_calc_width}")
print(f"front_panel_calc_height: {front_panel_calc_height}")
print()

# Vertical cleat material calculations
print("VERTICAL CLEAT MATERIAL CALCULATIONS:")
print("-" * 40)

# Step 1: Front/Back panels
print(f"Checking front/back panels ({front_panel_calc_width}\" x {front_panel_calc_height}\")...")
front_back_material_needed = calculate_vertical_cleat_material_needed(
    front_panel_calc_width, front_panel_calc_height, cleat_member_width
)
print(f"  Material needed: {front_back_material_needed}\"")

# Update dimensions
front_panel_calc_width += front_back_material_needed
back_panel_calc_width = front_panel_calc_width
crate_overall_width_od += front_back_material_needed

print(f"  Updated front_panel_calc_width: {front_panel_calc_width}")
print(f"  Updated crate_overall_width_od: {crate_overall_width_od}")
print()

# Step 2: Left/Right panels
print(f"Checking left/right panels ({end_panel_calc_length}\" x {end_panel_calc_height}\")...")
left_right_material_needed = calculate_vertical_cleat_material_needed(
    end_panel_calc_length, end_panel_calc_height, cleat_member_width
)
print(f"  Material needed: {left_right_material_needed}\"")

# Update dimensions (matching desktop logic exactly)
if left_right_material_needed > 0:
    crate_overall_length_od += left_right_material_needed
    # Recalculate end panel length from updated overall length
    end_panel_calc_length = crate_overall_length_od - front_panel_calc_depth - back_panel_calc_depth

print(f"  Updated crate_overall_length_od: {crate_overall_length_od}")
print(f"  Updated end_panel_calc_length: {end_panel_calc_length}")
print()

print("="*60)
print("FINAL DIMENSIONS:")
print("="*60)
print(f"Overall Width OD: {crate_overall_width_od}")
print(f"Overall Length OD: {crate_overall_length_od}")
print(f"Front Panel Width: {front_panel_calc_width}")
print(f"Front Panel Height: {front_panel_calc_height}")
print(f"End Panel Length: {end_panel_calc_length}")
print(f"End Panel Height: {end_panel_calc_height}")