#!/usr/bin/env python3
"""
Simple trace of the calculation values to identify the discrepancy.
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
skid_height = 3.5

print("="*60)
print("MANUAL CALCULATION TRACE")
print("="*60)
print()

# Initial dimensions
crate_width = product_width + 2 * clearance  # 52
crate_length = product_length + 2 * clearance  # 100
assembly_thickness = panel_thickness + cleat_thickness  # 2.25

print(f"Initial crate width: {crate_width}")
print(f"Initial crate length: {crate_length}")
print(f"Panel assembly thickness: {assembly_thickness}")
print()

# End panel initial dimensions
end_panel_length_initial = crate_length - 2 * assembly_thickness  # 100 - 4.5 = 95.5
print(f"End panel length (initial): {end_panel_length_initial}")

# For 95.5" x 33" panel, we need 2 sheets across (48" + 47.5")
# Vertical splice at x=48"
# Right edge cleat centerline: 95.5 - 1.75 = 93.75"
# Splice would be at x=48"
# Clearance: 93.75 - 48 - 3.5 = 42.25" (plenty of clearance)
print("  For 95.5\" x 33\" panel: No material needed (splice at 48\" has 42.25\" clearance)")
print()

# But wait, let me check 100.5" (which is what desktop seems to calculate)
# The desktop seems to be starting with a different initial end panel length
# Let me recalculate...

print("Checking if desktop adds 5\" somewhere...")
print("Desktop shows end panel = 100.5\", overall length = 105\"")
print()

# Ah! The discrepancy might be in how the vertical splice calculation works
# Let me check a 100.5" panel
end_panel_check = 100.5
print(f"Checking {end_panel_check}\" x 33\" panel:")
print(f"  Need sheets: {end_panel_check / 48:.1f} sheets across")
print(f"  Sheets: 48\" + 48\" + 4.5\" = 100.5\"")
print(f"  Vertical splices at: x=48\" and x=96\"")
print(f"  Right edge cleat centerline: {end_panel_check - cleat_member_width/2:.2f}\"")
print(f"  Second splice at x=96\"")
clearance_check = (end_panel_check - cleat_member_width/2) - 96 - cleat_member_width
print(f"  Clearance: {clearance_check:.2f}\" (CONFLICT if < 0.25\")")

if clearance_check < 0.25:
    material_needed = 0.25 - clearance_check + cleat_member_width
    import math
    material_needed = math.ceil(material_needed / 0.25) * 0.25
    print(f"  Material needed: {material_needed}\"")
    new_length = crate_length + material_needed
    print(f"  New overall length: {new_length}\"")
    new_end_panel = new_length - 2 * assembly_thickness
    print(f"  New end panel length: {new_end_panel}\"")
else:
    print("  No material needed")
print()

# Now the mystery: why does desktop start with 100.5" for end panel?
# Let me check the calculation again...

print("WAIT - Let me recheck the desktop code...")
print("The issue might be in the initial calculation!")
print()

# Actually, I think I found it! The desktop uses 105" initial length, not 100"
print("HYPOTHESIS: Desktop might be adding 5\" somewhere initially")
print("Let me check if there's a skid-related adjustment...")
print()

# Or maybe there's a rounding issue?
actual_initial_length = 100  # What we calculated
print(f"Our initial crate length: {actual_initial_length}")
print(f"Desktop shows: 105")
print(f"Difference: {105 - actual_initial_length}\"")
print()

print("This 5\" difference is the root cause!")
print("Need to find where desktop adds this 5\" initially.")