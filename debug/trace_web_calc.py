#!/usr/bin/env python3
"""
Trace through the web calculation logic step by step to identify discrepancies.
"""

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

print("="*60)
print("TRACING WEB CALCULATION LOGIC")
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
end_panel_calc_height = 3.5 + floorboard_thickness + product_height + clearance_above - ground_clearance  # 3.5 is skid height
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

# For a 56.5" x 33.5" panel, we need to check if vertical splices occur
# Plywood is 48" x 96", so for 56.5" width, we need 2 sheets across
# This creates a vertical splice at x=48"
print("Front/Back panels (56.5\" x 33.5\"):")
print("  - Need 2 sheets across (48\" + 8.5\")")
print("  - Vertical splice at x=48\"")
print("  - Right edge cleat centerline: 56.5 - 3.5/2 = 54.75\"")
print("  - Splice cleat would be at x=48\"")
print("  - Clearance: 54.75 - 48 - 3.5 = 3.25\" (OK, > 0.25\")")
print("  - No material needed for front/back panels")
front_back_material_needed = 0

# Update dimensions
front_panel_calc_width += front_back_material_needed
updated_crate_overall_width_od = crate_overall_width_od + front_back_material_needed

print()
print(f"front_panel_calc_width (after step 1): {front_panel_calc_width}")
print(f"updated_crate_overall_width_od (after step 1): {updated_crate_overall_width_od}")
print()

# Left/Right panels
print("Left/Right panels (100.5\" x 33\"):")
print("  - Need 3 sheets across (48\" + 48\" + 4.5\")")
print("  - Vertical splices at x=48\" and x=96\"")
print("  - Right edge cleat centerline: 100.5 - 3.5/2 = 98.75\"")
print("  - Second splice at x=96\"")
print("  - Clearance: 98.75 - 96 - 3.5 = -0.75\" (CONFLICT!)")
print("  - Need to extend by: 0.25 - (-0.75) + 3.5 = 4.5\"")
print("  - Round up to nearest 0.25\": 4.5\" (already on 0.25\" boundary)")
left_right_material_needed = 4.5

# Update dimensions
updated_end_panel_calc_length = end_panel_calc_length + left_right_material_needed
updated_crate_overall_length_od = crate_overall_length_od + left_right_material_needed

print()
print(f"left_right_material_needed: {left_right_material_needed}")
print(f"updated_end_panel_calc_length: {updated_end_panel_calc_length}")
print(f"updated_crate_overall_length_od: {updated_crate_overall_length_od}")
print()

print("="*60)
print("FINAL DIMENSIONS:")
print("="*60)
print(f"Overall Width OD: {updated_crate_overall_width_od}")
print(f"Overall Length OD: {updated_crate_overall_length_od}")
print(f"Front Panel Width: {front_panel_calc_width}")
print(f"Front Panel Height: {front_panel_calc_height}")
print(f"End Panel Length: {updated_end_panel_calc_length}")
print(f"End Panel Height: {end_panel_calc_height}")
print()

print("="*60)
print("COMPARISON WITH DESKTOP:")
print("="*60)
print("Desktop Values:")
print("  Overall Width OD: 52.0")
print("  Overall Length OD: 105.0")
print("  Front Panel Width: 56.5")
print("  Front Panel Height: 33.5")
print("  End Panel Length: 100.5")
print("  End Panel Height: 33.0")
print()
print("Calculated Values:")
print(f"  Overall Width OD: {updated_crate_overall_width_od}")
print(f"  Overall Length OD: {updated_crate_overall_length_od}")
print(f"  Front Panel Width: {front_panel_calc_width}")
print(f"  Front Panel Height: {front_panel_calc_height}")
print(f"  End Panel Length: {updated_end_panel_calc_length}")
print(f"  End Panel Height: {end_panel_calc_height}")