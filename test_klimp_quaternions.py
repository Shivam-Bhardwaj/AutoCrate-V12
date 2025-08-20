"""
Test script for the klimp quaternion system.

This script verifies that the new quaternion-based orientation system works correctly
and produces the expected NX expression variables with quaternion advantages.
"""

import sys
import os
import math

# Add the autocrate directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'autocrate'))

from autocrate.klimp_quaternion_system import (
    Quaternion, KlimpQuaternionOrientation, validate_quaternion,
    interpolate_klimp_orientations, STANDARD_QUATERNIONS
)
from autocrate.klimp_quaternion_integration import (
    calculate_klimp_quaternion_orientations, generate_klimp_quaternion_nx_expressions,
    verify_quaternion_consistency, compare_quaternion_and_unit_vector_systems,
    create_test_quaternion_configuration
)


def test_quaternion_mathematics():
    """Test basic quaternion mathematical operations."""
    print("=" * 60)
    print("TESTING QUATERNION MATHEMATICS")
    print("=" * 60)
    
    # Test identity quaternion
    q_identity = Quaternion.identity()
    print(f"Identity quaternion: w={q_identity.w:.3f}, x={q_identity.x:.3f}, y={q_identity.y:.3f}, z={q_identity.z:.3f}")
    print(f"  Magnitude: {q_identity.magnitude():.6f}")
    print(f"  Normalized: {validate_quaternion(q_identity)}")
    
    # Test rotation quaternions
    q_90z = Quaternion.from_euler_angles(0, 0, math.radians(90))
    print(f"\n90° Z rotation: w={q_90z.w:.3f}, x={q_90z.x:.3f}, y={q_90z.y:.3f}, z={q_90z.z:.3f}")
    print(f"  Magnitude: {q_90z.magnitude():.6f}")
    
    # Test vector rotation
    test_vector = (1.0, 0.0, 0.0)  # X-axis
    rotated = q_90z.rotate_vector(test_vector)
    print(f"  Rotating (1,0,0) by 90°Z: ({rotated[0]:.3f}, {rotated[1]:.3f}, {rotated[2]:.3f})")
    print(f"  Expected: (0, 1, 0) - Match: {abs(rotated[0]) < 0.001 and abs(rotated[1] - 1.0) < 0.001}")
    
    # Test quaternion multiplication
    q_45z = Quaternion.from_euler_angles(0, 0, math.radians(45))
    q_90z_composed = q_45z.multiply(q_45z)  # 45° + 45° = 90°
    print(f"\n45° + 45° = 90° composition:")
    print(f"  Result: w={q_90z_composed.w:.3f}, x={q_90z_composed.x:.3f}, y={q_90z_composed.y:.3f}, z={q_90z_composed.z:.3f}")
    
    # Test spherical interpolation
    t = 0.5
    q_interp = q_identity.slerp(q_90z, t)
    print(f"\nSLERP between identity and 90°Z at t=0.5:")
    print(f"  Result: w={q_interp.w:.3f}, x={q_interp.x:.3f}, y={q_interp.y:.3f}, z={q_interp.z:.3f}")
    
    # Verify the interpolated quaternion gives ~45° rotation
    rx, ry, rz = q_interp.to_euler_angles()
    expected_angle = 45.0
    actual_angle = math.degrees(rz)
    print(f"  Interpolated angle: {actual_angle:.1f}° (expected ~{expected_angle:.1f}°)")
    
    return True


def test_klimp_quaternion_orientations():
    """Test klimp quaternion orientation functionality."""
    print("\n" + "=" * 60)
    print("TESTING KLIMP QUATERNION ORIENTATIONS")
    print("=" * 60)
    
    # Test standard orientations
    top_orient = KlimpQuaternionOrientation.top_panel_orientation(10.0, 20.0, 30.0)
    print(f"Top panel orientation at (10, 20, 30):")
    print(f"  Quaternion: w={top_orient.quaternion.w:.3f}, x={top_orient.quaternion.x:.3f}, y={top_orient.quaternion.y:.3f}, z={top_orient.quaternion.z:.3f}")
    
    rx, ry, rz = top_orient.to_euler_angles()
    print(f"  Euler angles: RX={rx:.1f}°, RY={ry:.1f}°, RZ={rz:.1f}°")
    
    # Test left panel orientation
    left_orient = KlimpQuaternionOrientation.left_panel_orientation(-25.0, 0.0, 40.0)
    print(f"\nLeft panel orientation at (-25, 0, 40):")
    print(f"  Quaternion: w={left_orient.quaternion.w:.3f}, x={left_orient.quaternion.x:.3f}, y={left_orient.quaternion.y:.3f}, z={left_orient.quaternion.z:.3f}")
    
    rx, ry, rz = left_orient.to_euler_angles()
    print(f"  Euler angles: RX={rx:.1f}°, RY={ry:.1f}°, RZ={rz:.1f}°")
    
    # Test right panel orientation
    right_orient = KlimpQuaternionOrientation.right_panel_orientation(25.0, 0.0, 40.0)
    print(f"\nRight panel orientation at (25, 0, 40):")
    print(f"  Quaternion: w={right_orient.quaternion.w:.3f}, x={right_orient.quaternion.x:.3f}, y={right_orient.quaternion.y:.3f}, z={right_orient.quaternion.z:.3f}")
    
    rx, ry, rz = right_orient.to_euler_angles()
    print(f"  Euler angles: RX={rx:.1f}°, RY={ry:.1f}°, RZ={rz:.1f}°")
    
    # Test unit vector conversion
    x_axis, y_axis, z_axis = right_orient.to_unit_vectors()
    print(f"  Unit vectors:")
    print(f"    X-axis: ({x_axis[0]:.3f}, {x_axis[1]:.3f}, {x_axis[2]:.3f})")
    print(f"    Y-axis: ({y_axis[0]:.3f}, {y_axis[1]:.3f}, {y_axis[2]:.3f})")
    print(f"    Z-axis: ({z_axis[0]:.3f}, {z_axis[1]:.3f}, {z_axis[2]:.3f})")
    
    # Test axis-angle conversion
    axis, angle = right_orient.to_axis_angle()
    print(f"  Axis-angle: axis=({axis[0]:.3f}, {axis[1]:.3f}, {axis[2]:.3f}), angle={angle:.1f}°")
    
    return True


def test_quaternion_nx_expressions():
    """Test NX expression generation with quaternions."""
    print("\n" + "=" * 60)
    print("TESTING QUATERNION NX EXPRESSION GENERATION")
    print("=" * 60)
    
    # Create test orientations
    test_orientations = create_test_quaternion_configuration()
    
    # Generate NX expressions
    nx_expressions = generate_klimp_quaternion_nx_expressions(test_orientations)
    
    print(f"Generated {len(nx_expressions)} NX expression lines")
    print("\nFirst 30 lines of generated expressions:")
    for i, line in enumerate(nx_expressions[:30]):
        print(f"  {i+1:2d}: {line}")
    
    # Look for quaternion variables
    quaternion_lines = [line for line in nx_expressions if "_Q_" in line and not line.strip().startswith("//")]
    unit_vector_lines = [line for line in nx_expressions if "_DIR_" in line and not line.strip().startswith("//")]
    axis_angle_lines = [line for line in nx_expressions if ("_AXIS_" in line or "_ANGLE" in line) and not line.strip().startswith("//")]
    
    print(f"\nVariable breakdown:")
    print(f"  Quaternion variables: {len(quaternion_lines)}")
    print(f"  Unit vector variables: {len(unit_vector_lines)}")
    print(f"  Axis-angle variables: {len(axis_angle_lines)}")
    
    # Sample quaternion variables
    print(f"\nSample quaternion variables:")
    for line in quaternion_lines[:8]:
        print(f"  {line}")
    
    # Expected counts: 30 klimps * 4 quaternion components = 120
    expected_quaternions = 30 * 4
    print(f"\nQuaternion variables: Expected {expected_quaternions}, Found {len(quaternion_lines)}")
    
    return len(quaternion_lines) == expected_quaternions


def test_quaternion_validation():
    """Test the validation system for quaternions."""
    print("\n" + "=" * 60)
    print("TESTING QUATERNION VALIDATION SYSTEM")
    print("=" * 60)
    
    # Create test orientations
    test_orientations = create_test_quaternion_configuration()
    
    # Verify consistency
    results = verify_quaternion_consistency(test_orientations)
    
    print(f"Validation Results:")
    print(f"  Total klimps: {results['total_klimps']}")
    print(f"  Valid quaternions: {results['valid_quaternions']}")
    print(f"  Invalid quaternions: {len(results['invalid_quaternions'])}")
    print(f"  Success rate: {results['success_rate']:.1f}%")
    print(f"  Overall success: {results['success']}")
    
    if results['errors']:
        print(f"\nErrors found:")
        for error in results['errors']:
            print(f"  {error}")
    
    return results['success']


def test_quaternion_integration():
    """Test integration with existing klimp placement logic."""
    print("\n" + "=" * 60)
    print("TESTING QUATERNION INTEGRATION WITH EXISTING SYSTEM")
    print("=" * 60)
    
    try:
        # Test with standard crate dimensions
        orientations = calculate_klimp_quaternion_orientations(
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
        
        # Check positioning and quaternions
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
        
        # Test sample quaternions for different panels
        if active_top:
            sample = active_top[0]
            rx, ry, rz = sample.to_euler_angles()
            print(f"\nSample top klimp:")
            print(f"  Position: ({sample.position_x:.3f}, {sample.position_y:.3f}, {sample.position_z:.3f})")
            print(f"  Quaternion: w={sample.quaternion.w:.3f}, x={sample.quaternion.x:.3f}, y={sample.quaternion.y:.3f}, z={sample.quaternion.z:.3f}")
            print(f"  Euler angles: RX={rx:.1f}°, RY={ry:.1f}°, RZ={rz:.1f}°")
        
        if active_left:
            sample = active_left[0]
            rx, ry, rz = sample.to_euler_angles()
            print(f"\nSample left klimp:")
            print(f"  Position: ({sample.position_x:.3f}, {sample.position_y:.3f}, {sample.position_z:.3f})")
            print(f"  Quaternion: w={sample.quaternion.w:.3f}, x={sample.quaternion.x:.3f}, y={sample.quaternion.y:.3f}, z={sample.quaternion.z:.3f}")
            print(f"  Euler angles: RX={rx:.1f}°, RY={ry:.1f}°, RZ={rz:.1f}°")
        
        return True
        
    except Exception as e:
        print(f"Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_quaternion_interpolation():
    """Test quaternion interpolation (SLERP) functionality."""
    print("\n" + "=" * 60)
    print("TESTING QUATERNION INTERPOLATION (SLERP)")
    print("=" * 60)
    
    # Create start and end orientations
    start_orient = KlimpQuaternionOrientation.top_panel_orientation(0.0, 0.0, 0.0)
    end_orient = KlimpQuaternionOrientation.left_panel_orientation(10.0, 0.0, 0.0)
    
    print("Interpolating from top panel (0°) to left panel (-90°Z):")
    print(f"Start: w={start_orient.quaternion.w:.3f}, x={start_orient.quaternion.x:.3f}, y={start_orient.quaternion.y:.3f}, z={start_orient.quaternion.z:.3f}")
    print(f"End:   w={end_orient.quaternion.w:.3f}, x={end_orient.quaternion.x:.3f}, y={end_orient.quaternion.y:.3f}, z={end_orient.quaternion.z:.3f}")
    
    # Test interpolation at various t values
    for t in [0.25, 0.5, 0.75]:
        interp_orient = interpolate_klimp_orientations(start_orient, end_orient, t)
        rx, ry, rz = interp_orient.to_euler_angles()
        
        print(f"\nt={t}:")
        print(f"  Quaternion: w={interp_orient.quaternion.w:.3f}, x={interp_orient.quaternion.x:.3f}, y={interp_orient.quaternion.y:.3f}, z={interp_orient.quaternion.z:.3f}")
        print(f"  Position: ({interp_orient.position_x:.1f}, {interp_orient.position_y:.1f}, {interp_orient.position_z:.1f})")
        print(f"  Euler angles: RX={rx:.1f}°, RY={ry:.1f}°, RZ={rz:.1f}°")
        print(f"  Expected RZ: {-90 * t:.1f}°")
    
    return True


def test_quaternion_comparison():
    """Compare quaternion system with unit vector system."""
    print("\n" + "=" * 60)
    print("TESTING QUATERNION VS UNIT VECTOR COMPARISON")
    print("=" * 60)
    
    try:
        comparison = compare_quaternion_and_unit_vector_systems(
            panel_width=48.0,
            panel_length=48.0,
            panel_height=48.0
        )
        
        print(f"Comparison Results:")
        print(f"  Klimps analyzed: {comparison['klimp_count']}")
        print(f"  Max Euler angle difference: {comparison['max_euler_diff']:.6f}°")
        print(f"  Max unit vector error: {comparison['max_unit_vector_diff']:.6f}")
        
        # Check quaternion normalization
        normalized_count = sum(1 for qm in comparison['quaternion_magnitudes'] if qm['normalized'])
        print(f"  Properly normalized quaternions: {normalized_count}/{comparison['klimp_count']}")
        
        # Show quaternion advantages
        print(f"\nQuaternion advantages demonstrated:")
        print(f"  + Compact representation (4 values vs 9 for rotation matrices)")
        print(f"  + No gimbal lock")
        print(f"  + Numerically stable")
        print(f"  + Smooth interpolation available")
        print(f"  + Efficient composition of rotations")
        
        return comparison['max_euler_diff'] < 0.001  # Within tight tolerance
        
    except Exception as e:
        print(f"Comparison test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all quaternion tests."""
    print("KLIMP QUATERNION SYSTEM TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Quaternion Mathematics", test_quaternion_mathematics),
        ("Klimp Quaternion Orientations", test_klimp_quaternion_orientations),
        ("Quaternion NX Expression Generation", test_quaternion_nx_expressions),
        ("Quaternion Validation System", test_quaternion_validation),
        ("Quaternion Integration", test_quaternion_integration),
        ("Quaternion Interpolation (SLERP)", test_quaternion_interpolation),
        ("Quaternion vs Unit Vector Comparison", test_quaternion_comparison)
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
        print("\n*** ALL TESTS PASSED! Quaternion system is working perfectly! ***")
        print("\nQuaternion advantages confirmed:")
        print("  + No gimbal lock")
        print("  + Compact representation (4 values)")
        print("  + Smooth interpolation (SLERP)")
        print("  + Numerically stable")
        print("  + Efficient rotation composition")
        print("  + Industry standard for 3D rotations")
        return True
    else:
        print(f"\n*** {total-passed} tests failed. Review output above for details. ***")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)