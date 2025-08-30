import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from autocrate.nx_expressions_generator import calculate_vertical_cleat_material_needed

# Test parameters
product_length = 96.0
product_width = 48.0 
product_height = 30.0
clearance = 2.0
panel_thickness = 0.75
cleat_thickness = 1.5
cleat_width = 3.5
clearance_above = 2.0
ground_clearance = 4.0
skid_height = 3.5
floorboard_thickness = 1.5

print("="*60)
print("TRACING MATERIAL ADDITIONS")
print("="*60)

# Step 1: Initial dimensions
skid_model_length = product_length + (2 * clearance)
crate_overall_width_od = product_width + (2 * clearance)
crate_overall_length_od = skid_model_length  # Start with 100"
panel_assembly_thickness = panel_thickness + cleat_thickness

print(f"\nSTEP 1 - Initial:")
print(f"  Crate Width OD: {crate_overall_width_od}")
print(f"  Crate Length OD: {crate_overall_length_od}")

# Step 2: Front/Back panels
panel_height = skid_height + floorboard_thickness + product_height + clearance_above - ground_clearance
front_panel_width = crate_overall_width_od + 2 * panel_assembly_thickness
front_back_material = calculate_vertical_cleat_material_needed(
    front_panel_width, panel_height, cleat_width
)

print(f"\nSTEP 2 - Front/Back Panels:")
print(f"  Panel Width: {front_panel_width}")
print(f"  Material Needed: {front_back_material}")

if front_back_material > 0:
    crate_overall_width_od += front_back_material

# Step 3: Left/Right panels  
end_panel_length = crate_overall_length_od - 2 * panel_assembly_thickness
left_right_material = calculate_vertical_cleat_material_needed(
    end_panel_length, panel_height, cleat_width
)

print(f"\nSTEP 3 - Left/Right Panels:")
print(f"  Panel Length: {end_panel_length}")
print(f"  Material Needed: {left_right_material}")

if left_right_material > 0:
    crate_overall_length_od += left_right_material
    end_panel_length = crate_overall_length_od - 2 * panel_assembly_thickness

# Step 4: Top Panel (THIS IS KEY!)
top_panel_width = crate_overall_width_od + 2 * panel_assembly_thickness
top_panel_length = crate_overall_length_od

print(f"\nSTEP 4 - Top Panel:")
print(f"  Initial Width: {top_panel_width}")
print(f"  Initial Length: {top_panel_length}")

# Top panel checks BOTH directions for material needs
top_width_material = calculate_vertical_cleat_material_needed(
    top_panel_width, top_panel_length, cleat_width
)
top_length_material = calculate_vertical_cleat_material_needed(
    top_panel_length, top_panel_width, cleat_width  # Note: swapped parameters!
)

print(f"  Width Material Needed: {top_width_material}")
print(f"  Length Material Needed: {top_length_material}")

if top_width_material > 0:
    crate_overall_width_od += top_width_material
    top_panel_width += top_width_material

if top_length_material > 0:
    end_panel_length += top_length_material
    crate_overall_length_od += top_length_material
    top_panel_length += top_length_material

print(f"\nFINAL DIMENSIONS:")
print(f"  Crate Width OD: {crate_overall_width_od}")
print(f"  Crate Length OD: {crate_overall_length_od}")
print(f"  End Panel Length: {end_panel_length}")
print(f"  Top Panel Width: {top_panel_width}")
print(f"  Top Panel Length: {top_panel_length}")

if crate_overall_length_od == 105.0:
    print(f"\n✓ MATCH! Desktop value of 105\" achieved")
    print(f"  The {top_length_material}\" was added for top panel vertical cleats")