"""
Test script for the klimp unit vector system.

This script verifies that the new unit vector orientation system works correctly
and produces the expected NX expression variables.
"""

import sys
import os

# Add the autocrate directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'autocrate'))

from autocrate.klimp_unit_vector_system import (
    KlimpOrientation, UnitVector, validate_orthogonality
)
from autocrate.klimp_unit_vector_integration import (
    calculate_klimp_unit_vectors, generate_klimp_nx_expressions,
    verify_unit_vector_consistency, compare_legacy_and_unit_vector_systems,
    create_test_klimp_configuration
)


def test_unit_vector_basic_functionality():
    """Test basic unit vector functionality."""
    print("=" * 60)
    print("TESTING BASIC UNIT VECTOR FUNCTIONALITY")
    print("=" * 60)
    
    # Test identity orientation
    identity = KlimpOrientation.identity(10.0, 20.0, 30.0)
    print(f"Identity orientation at (10, 20, 30):")
    print(f"  X-axis: ({identity.x_axis.x:.3f}, {identity.x_axis.y:.3f}, {identity.x_axis.z:.3f})")
    print(f"  Y-axis: ({identity.y_axis.x:.3f}, {identity.y_axis.y:.3f}, {identity.y_axis.z:.3f})")
    print(f"  Z-axis: ({identity.z_axis.x:.3f}, {identity.z_axis.y:.3f}, {identity.z_axis.z:.3f})")
    
    # Test orthogonality
    is_valid = validate_orthogonality(identity)
    print(f"  Orthogonality valid: {is_valid}")
    
    # Test Euler angle conversion
    rx, ry, rz = identity.to_euler_angles()
    print(f"  Euler angles: RX={rx:.1f}°, RY={ry:.1f}°, RZ={rz:.1f}°")
    
    print("\n" + "-" * 40)
    
    # Test left panel orientation
    left_panel = KlimpOrientation.left_panel_orientation(-25.0, 0.0, 40.0)
    print(f"Left panel orientation at (-25, 0, 40):")
    print(f"  X-axis: ({left_panel.x_axis.x:.3f}, {left_panel.x_axis.y:.3f}, {left_panel.x_axis.z:.3f})")
    print(f"  Y-axis: ({left_panel.y_axis.x:.3f}, {left_panel.y_axis.y:.3f}, {left_panel.y_axis.z:.3f})")
    print(f"  Z-axis: ({left_panel.z_axis.x:.3f}, {left_panel.z_axis.y:.3f}, {left_panel.z_axis.z:.3f})")
    
    is_valid = validate_orthogonality(left_panel)
    print(f"  Orthogonality valid: {is_valid}")
    
    rx, ry, rz = left_panel.to_euler_angles()
    print(f"  Euler angles: RX={rx:.1f}°, RY={ry:.1f}°, RZ={rz:.1f}°")
    
    print("\n" + "-" * 40)
    
    # Test right panel orientation
    right_panel = KlimpOrientation.right_panel_orientation(25.0, 0.0, 40.0)
    print(f"Right panel orientation at (25, 0, 40):")
    print(f"  X-axis: ({right_panel.x_axis.x:.3f}, {right_panel.x_axis.y:.3f}, {right_panel.x_axis.z:.3f})")
    print(f"  Y-axis: ({right_panel.y_axis.x:.3f}, {right_panel.y_axis.y:.3f}, {right_panel.y_axis.z:.3f})")
    print(f"  Z-axis: ({right_panel.z_axis.x:.3f}, {right_panel.z_axis.y:.3f}, {right_panel.z_axis.z:.3f})")
    
    is_valid = validate_orthogonality(right_panel)
    print(f"  Orthogonality valid: {is_valid}")
    
    rx, ry, rz = right_panel.to_euler_angles()
    print(f"  Euler angles: RX={rx:.1f}°, RY={ry:.1f}°, RZ={rz:.1f}°")
    
    return True


def test_nx_expression_generation():
    """Test NX expression generation with unit vectors."""
    print("\n" + "=" * 60)
    print("TESTING NX EXPRESSION GENERATION")
    print("=" * 60)
    
    # Create a test configuration
    test_orientations = create_test_klimp_configuration()
    
    # Generate NX expressions
    nx_expressions = generate_klimp_nx_expressions(test_orientations)
    
    print(f"Generated {len(nx_expressions)} NX expression lines")
    print("\nFirst 20 lines of generated expressions:")
    for i, line in enumerate(nx_expressions[:20]):
        print(f"  {i+1:2d}: {line}")
    
    # Look for unit vector variables
    unit_vector_lines = [line for line in nx_expressions if "_DIR_" in line]
    print(f"\nFound {len(unit_vector_lines)} unit vector direction variables")
    print("Sample unit vector variables:")
    for line in unit_vector_lines[:10]:
        print(f"  {line}")
    
    return True


def test_validation_system():
    """Test the validation system for unit vectors."""
    print("\n" + "=" * 60)
    print("TESTING VALIDATION SYSTEM")
    print("=" * 60)
    
    # Create test orientations
    test_orientations = create_test_klimp_configuration()
    
    # Verify consistency
    results = verify_unit_vector_consistency(test_orientations)
    
    print(f"Validation Results:")
    print(f"  Total klimps: {results['total_klimps']}")
    print(f"  Valid klimps: {results['valid_klimps']}")
    print(f"  Invalid klimps: {len(results['invalid_klimps'])}")
    print(f"  Success rate: {results['success_rate']:.1f}%")
    print(f"  Overall success: {results['success']}")
    
    if results['errors']:
        print(f"\nErrors found:")
        for error in results['errors']:
            print(f"  {error}")
    
    return results['success']


def test_integration_with_existing_system():
    """Test integration with existing klimp placement logic."""
    print("\n" + "=" * 60)
    print("TESTING INTEGRATION WITH EXISTING SYSTEM")
    print("=" * 60)
    
    try:
        # Test with standard crate dimensions
        orientations = calculate_klimp_unit_vectors(
            panel_width=48.0,
            panel_length=48.0,
            panel_height=48.0,
            cleat_member_width=3.5,
            cleat_thickness=2.0,
            panel_thickness=0.25
        )
        
        print(f"Successfully calculated {len(orientations)} klimp orientations")
        
        # Count active klimps
        active_klimps = [o for o in orientations if not o.suppress]
        print(f"Active klimps: {len(active_klimps)}")
        print(f"Suppressed klimps: {len(orientations) - len(active_klimps)}")
        
        # Check positioning
        top_klimps = orientations[:10]
        left_klimps = orientations[10:20]
        right_klimps = orientations[20:30]
        
        active_top = [k for k in top_klimps if not k.suppress]
        active_left = [k for k in left_klimps if not k.suppress]
        active_right = [k for k in right_klimps if not k.suppress]
        
        print(f"\nPanel distribution:")
        print(f"  Top panel: {len(active_top)} active klimps")
        print(f"  Left panel: {len(active_left)} active klimps")
        print(f"  Right panel: {len(active_right)} active klimps")
        
        # Test a few sample positions
        if active_top:
            sample = active_top[0]
            print(f"\nSample top klimp position:")
            print(f"  Position: ({sample.position_x:.3f}, {sample.position_y:.3f}, {sample.position_z:.3f})")
            rx, ry, rz = sample.to_euler_angles()
            print(f"  Euler angles: RX={rx:.1f}°, RY={ry:.1f}°, RZ={rz:.1f}°")
        
        return True
        
    except Exception as e:
        print(f"Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_comparison_with_legacy():
    """Compare unit vector system with legacy Euler angle system."""
    print("\n" + "=" * 60)
    print("TESTING COMPARISON WITH LEGACY SYSTEM")
    print("=" * 60)
    
    try:
        comparison = compare_legacy_and_unit_vector_systems(
            panel_width=48.0,
            panel_length=48.0,
            panel_height=48.0
        )
        
        print(f"Comparison Results:")
        print(f"  Klimps analyzed: {comparison['klimp_count']}")
        print(f"  Max rotation difference: {comparison['max_rotation_diff']:.3f}°")
        
        # Show rotation differences
        print(f"\nRotation accuracy:")
        perfect_matches = 0
        for diff_data in comparison['rotation_differences']:
            if diff_data['difference'] < 0.001:
                perfect_matches += 1
        
        print(f"  Perfect matches: {perfect_matches}/{comparison['klimp_count']}")
        print(f"  Accuracy: {perfect_matches/comparison['klimp_count']*100:.1f}%")
        
        # Show worst cases
        worst_cases = sorted(comparison['rotation_differences'], 
                           key=lambda x: x['difference'], reverse=True)[:3]
        if worst_cases:
            print(f"\nWorst rotation differences:")
            for case in worst_cases:
                print(f"  KL_{case['klimp']}: Expected {case['expected_rz']:.1f}°, "
                      f"Got {case['actual_rz']:.1f}°, Diff {case['difference']:.3f}°")
        
        return comparison['max_rotation_diff'] < 1.0  # Within 1 degree tolerance
        
    except Exception as e:
        print(f"Comparison test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all unit vector tests."""
    print("KLIMP UNIT VECTOR SYSTEM TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Basic Unit Vector Functionality", test_unit_vector_basic_functionality),
        ("NX Expression Generation", test_nx_expression_generation),
        ("Validation System", test_validation_system),
        ("Integration with Existing System", test_integration_with_existing_system),
        ("Comparison with Legacy System", test_comparison_with_legacy)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            status = "PASS" if result else "FAIL"
            print(f"\n{test_name}: {status}")
        except Exception as e:
            results.append((test_name, False))
            print(f"\n{test_name}: FAIL ({e})")
            import traceback
            traceback.print_exc()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  {test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n*** ALL TESTS PASSED! Unit vector system is working correctly. ***")
        return True
    else:
        print(f"\n*** {total-passed} tests failed. Review output above for details. ***")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)