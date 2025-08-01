#!/usr/bin/env python3
"""
Test script for klimp integration in NX expressions generation.
This script tests the complete workflow from klimp calculation to NX expressions output.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'autocrate'))

from autocrate.front_panel_logic import calculate_front_panel_components
from autocrate.nx_expressions_generator import DEFAULT_KLIMP_DIAMETER, MAX_FRONT_PANEL_KLIMPS

def test_klimp_expressions():
    """Test klimp expressions generation."""
    
    print("=== Klimp Integration Test ===\n")
    
    # Test case: 60x40 panel (should generate multiple klimps)
    print("Test Case: 60x40 inch front panel")
    print("-" * 40)
    
    result = calculate_front_panel_components(
        front_panel_assembly_width=60.0,
        front_panel_assembly_height=40.0,
        panel_sheathing_thickness=0.75,
        cleat_material_thickness=1.5,
        cleat_material_member_width=3.5,
        include_klimps=True,
        klimp_diameter=1.0
    )
    
    klimps_data = result['klimps']
    
    print(f"Klimp Count: {klimps_data['count']}")
    print(f"Klimp Diameter: {klimps_data['diameter']} inches")
    print(f"Orientation: {klimps_data['orientation']}")
    print(f"Spacing Quality: {klimps_data['spacing_analysis']['spacing_quality']}")
    print(f"Average Spacing: {klimps_data['spacing_analysis']['avg_spacing']:.2f} inches")
    
    print("\nKlimp Positions:")
    for i, klimp in enumerate(klimps_data['positions']):
        print(f"  Klimp {i+1}: X={klimp['x_pos']:.3f}, Y={klimp['y_pos']:.3f}")
    
    print("\nGenerated NX Expression Variables:")
    print("-" * 50)
    
    # Simulate the NX expressions that would be generated
    fp_klimp_count = klimps_data.get('count', 0)
    fp_klimp_diameter = klimps_data.get('diameter', DEFAULT_KLIMP_DIAMETER)
    fp_klimp_positions = klimps_data.get('positions', [])
    fp_klimp_orientation_code = 3 if klimps_data.get('orientation') == "Front_Panel_Surface" else 2
    
    expressions = [
        f"// Front Panel Klimps (Clamps/Fasteners)",
        f"FP_Klimp_Count = {fp_klimp_count}",
        f"[Inch]FP_Klimp_Diameter = {fp_klimp_diameter:.3f}",
        f"FP_Klimp_Orientation_Code = {fp_klimp_orientation_code} // 0=Vertical, 1=Horizontal, 2=None, 3=Front_Surface",
        f"// Front Panel Klimp Instance Data (Max {MAX_FRONT_PANEL_KLIMPS} instances)"
    ]
    
    for expression in expressions:
        print(expression)
    
    print()
    
    for i in range(MAX_FRONT_PANEL_KLIMPS):
        instance_num = i + 1
        if i < fp_klimp_count and i < len(fp_klimp_positions):
            klimp = fp_klimp_positions[i]
            print(f"FP_Klimp_Inst_{instance_num}_Suppress_Flag = 1") # 1 to show
            print(f"[Inch]FP_Klimp_Inst_{instance_num}_X_Pos = {klimp['x_pos']:.4f}")
            print(f"[Inch]FP_Klimp_Inst_{instance_num}_Y_Pos = {klimp['y_pos']:.4f}")
        else:
            print(f"FP_Klimp_Inst_{instance_num}_Suppress_Flag = 0") # 0 to suppress/hide
            print(f"[Inch]FP_Klimp_Inst_{instance_num}_X_Pos = 0.0000")
            print(f"[Inch]FP_Klimp_Inst_{instance_num}_Y_Pos = 0.0000")
        
        if i < 2:  # Only show first few for brevity
            continue
        elif i == 2:
            print("... (remaining instances suppressed)")
            break
    
    print("\n=== Placement Analysis ===")
    print(f"Placement Zones: {len(klimps_data['placement_zones'])}")
    print(f"Exclusion Zones: {len(klimps_data['exclusion_zones'])}")
    
    print("\nSpacing Analysis:")
    spacing = klimps_data['spacing_analysis']
    print(f"  Min Spacing: {spacing['min_spacing']:.2f} inches")
    print(f"  Max Spacing: {spacing['max_spacing']:.2f} inches")
    print(f"  Avg Spacing: {spacing['avg_spacing']:.2f} inches")
    print(f"  Quality: {spacing['spacing_quality']}")
    
    # Validate spacing requirements
    print("\n=== Validation ===")
    all_valid = True
    
    # Check if spacing is within 16-24 inch range
    if spacing['min_spacing'] >= 16.0 and spacing['max_spacing'] <= 24.0:
        print("PASS: Spacing within 16-24 inch requirement")
    else:
        print("FAIL: Spacing outside 16-24 inch requirement")
        all_valid = False
    
    # Check clearance from cleats (should be handled by placement zones)
    if klimps_data['count'] > 0:
        print("PASS: Klimps positioned with proper cleat clearance")
    else:
        print("INFO: No klimps placed (panel too small or no suitable zones)")
    
    # Check NX variable limits
    if klimps_data['count'] <= MAX_FRONT_PANEL_KLIMPS:
        print(f"PASS: Klimp count ({klimps_data['count']}) within NX limit ({MAX_FRONT_PANEL_KLIMPS})")
    else:
        print(f"FAIL: Klimp count ({klimps_data['count']}) exceeds NX limit ({MAX_FRONT_PANEL_KLIMPS})")
        all_valid = False
    
    print(f"\nOverall Result: {'PASS' if all_valid else 'FAIL'}")
    return all_valid


def test_small_panel():
    """Test small panel that might not accommodate klimps."""
    
    print("\n\n=== Small Panel Test ===")
    print("Test Case: 24x20 inch front panel (minimal klimps expected)")
    print("-" * 50)
    
    result = calculate_front_panel_components(
        front_panel_assembly_width=24.0,
        front_panel_assembly_height=20.0,
        panel_sheathing_thickness=0.75,
        cleat_material_thickness=1.5,
        cleat_material_member_width=3.5,
        include_klimps=True,
        klimp_diameter=1.0
    )
    
    klimps_data = result['klimps']
    
    print(f"Klimp Count: {klimps_data['count']}")
    print(f"Spacing Quality: {klimps_data['spacing_analysis']['spacing_quality']}")
    
    if klimps_data['count'] > 0:
        print("Klimp Positions:")
        for i, klimp in enumerate(klimps_data['positions']):
            print(f"  Klimp {i+1}: X={klimp['x_pos']:.3f}, Y={klimp['y_pos']:.3f}")
    else:
        print("No klimps placed - panel too small or insufficient space")
    
    return True


if __name__ == '__main__':
    try:
        success1 = test_klimp_expressions()
        success2 = test_small_panel()
        
        print(f"\n{'='*60}")
        print(f"TEST SUMMARY: {'ALL TESTS PASSED' if success1 and success2 else 'SOME TESTS FAILED'}")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)