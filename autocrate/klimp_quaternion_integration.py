"""
Quaternion Integration Module for AutoCrate Klimp System

This module integrates the quaternion-based orientation system with the existing
klimp placement logic, providing seamless quaternion-based orientation while
maintaining full backward compatibility.
"""

from typing import Dict, List, Any, Tuple
import math
from .klimp_quaternion_system import (
    KlimpQuaternionOrientation, Quaternion, validate_quaternion,
    interpolate_klimp_orientations, STANDARD_QUATERNIONS
)
from .klimp_placement_logic_all_sides import calculate_all_klimp_placements


def calculate_klimp_quaternion_orientations(
    panel_width: float = 48.0,
    panel_length: float = 48.0,
    panel_height: float = 48.0,
    cleat_member_width: float = 3.5,
    cleat_thickness: float = 2.0,
    panel_thickness: float = 0.25,
    intermediate_vertical_cleats: List[float] = None,
    horizontal_splice_positions: List[float] = None,
    crate_center_x: float = 0.0,
    crate_center_y: float = 0.0,
    ground_level_z: float = 0.0
) -> List[KlimpQuaternionOrientation]:
    """
    Calculate klimp positions and orientations using quaternion system.
    
    This function integrates the existing placement logic with the new
    quaternion orientation system, providing compact and robust rotation
    representation.
    
    Args:
        panel_width: Width of front/back panels (X direction)
        panel_length: Length of left/right panels (Y direction)  
        panel_height: Height of side panels (Z direction)
        cleat_member_width: Width of cleat members
        cleat_thickness: Thickness of cleats
        panel_thickness: Thickness of plywood panels
        intermediate_vertical_cleats: Positions of intermediate vertical cleats
        horizontal_splice_positions: Z positions of horizontal splices
        crate_center_x: X coordinate of crate center
        crate_center_y: Y coordinate of crate center
        ground_level_z: Z coordinate of ground level
        
    Returns:
        List of KlimpQuaternionOrientation objects for all 30 possible klimps
    """
    
    # Get placement data from existing logic
    placement_data = calculate_all_klimp_placements(
        panel_width=panel_width,
        panel_length=panel_length,
        panel_height=panel_height,
        cleat_member_width=cleat_member_width,
        cleat_thickness=cleat_thickness,
        panel_thickness=panel_thickness,
        intermediate_vertical_cleats=intermediate_vertical_cleats,
        horizontal_splice_positions=horizontal_splice_positions
    )
    
    orientations = []
    
    # Calculate absolute positioning parameters
    half_width = panel_width / 2.0
    half_length = panel_length / 2.0
    top_z = ground_level_z + panel_height + panel_thickness + cleat_thickness + cleat_member_width
    left_x = crate_center_x - half_width - panel_thickness - cleat_thickness
    right_x = crate_center_x + half_width + panel_thickness + cleat_thickness
    
    # Process top klimps (KL_1 to KL_10)
    top_klimps = placement_data.get("top_klimps", [])
    for i in range(10):  # Always generate 10 slots for NX compatibility
        if i < len(top_klimps):
            klimp = top_klimps[i]
            abs_x = crate_center_x + klimp.get("position_x", 0.0) - half_width
            abs_y = crate_center_y + klimp.get("position_y", 0.0)
            abs_z = top_z
            
            orientation = KlimpQuaternionOrientation.top_panel_orientation(abs_x, abs_y, abs_z)
            orientation.suppress = False
        else:
            # Suppressed klimp with zero position
            orientation = KlimpQuaternionOrientation.top_panel_orientation(0.0, 0.0, 0.0)
            orientation.suppress = True
        
        orientations.append(orientation)
    
    # Process left klimps (KL_11 to KL_20)
    left_klimps = placement_data.get("left_klimps", [])
    for i in range(10):  # Always generate 10 slots for NX compatibility
        if i < len(left_klimps):
            klimp = left_klimps[i]
            abs_x = left_x
            abs_y = crate_center_y + klimp.get("position_y", 0.0)
            abs_z = ground_level_z + klimp.get("position_z", 0.0)
            
            orientation = KlimpQuaternionOrientation.left_panel_orientation(abs_x, abs_y, abs_z)
            orientation.suppress = False
        else:
            # Suppressed klimp with zero position  
            orientation = KlimpQuaternionOrientation.left_panel_orientation(0.0, 0.0, 0.0)
            orientation.suppress = True
        
        orientations.append(orientation)
    
    # Process right klimps (KL_21 to KL_30)
    right_klimps = placement_data.get("right_klimps", [])
    for i in range(10):  # Always generate 10 slots for NX compatibility
        if i < len(right_klimps):
            klimp = right_klimps[i]
            abs_x = right_x
            abs_y = crate_center_y + klimp.get("position_y", 0.0)
            abs_z = ground_level_z + klimp.get("position_z", 0.0)
            
            orientation = KlimpQuaternionOrientation.right_panel_orientation(abs_x, abs_y, abs_z)
            orientation.suppress = False
        else:
            # Suppressed klimp with zero position
            orientation = KlimpQuaternionOrientation.right_panel_orientation(0.0, 0.0, 0.0)
            orientation.suppress = True
        
        orientations.append(orientation)
    
    return orientations


def generate_klimp_quaternion_nx_expressions(orientations: List[KlimpQuaternionOrientation]) -> List[str]:
    """
    Generate NX expression strings for klimp quaternion orientations.
    
    Args:
        orientations: List of KlimpQuaternionOrientation objects
        
    Returns:
        List of formatted NX expression strings
    """
    expressions = []
    
    # Header comments
    expressions.extend([
        "",
        "// ========================================",
        "// KLIMP QUATERNION ORIENTATION SYSTEM",
        "// ========================================",
        "// Each klimp is defined by:",
        "// - Position: KL_XX_X, KL_XX_Y, KL_XX_Z",
        "// - Quaternion: KL_XX_Q_W, KL_XX_Q_X, KL_XX_Q_Y, KL_XX_Q_Z (primary)",
        "// - Unit Vectors: KL_XX_X_DIR_*, KL_XX_Y_DIR_*, KL_XX_Z_DIR_* (derived)",
        "// - Axis-Angle: KL_XX_AXIS_*, KL_XX_ANGLE (derived)",
        "// - Legacy Compatibility: KL_XX_RX, KL_XX_RY, KL_XX_RZ, KL_XX_ROTATE",
        "// - Suppress Flag: KL_XX_SUPPRESS (0=hide, 1=show)",
        "",
        "// Quaternion advantages:",
        "// - Compact representation (4 values vs 9 for rotation matrices)",
        "// - No gimbal lock",
        "// - Smooth interpolation (SLERP)",
        "// - Numerically stable",
        "// - Efficient composition of rotations",
        "",
        "// KL_1 to KL_10: Top panel klimps",
        "// KL_11 to KL_20: Left panel klimps", 
        "// KL_21 to KL_30: Right panel klimps",
        ""
    ])
    
    # Generate expressions for each klimp
    for i, orientation in enumerate(orientations[:30]):  # Limit to 30 klimps
        klimp_number = i + 1
        nx_vars = orientation.to_nx_expressions(klimp_number)
        
        # Add section header
        if klimp_number == 1:
            expressions.append("// --- TOP PANEL KLIMPS (KL_1 to KL_10) ---")
        elif klimp_number == 11:
            expressions.append("// --- LEFT PANEL KLIMPS (KL_11 to KL_20) ---")
        elif klimp_number == 21:
            expressions.append("// --- RIGHT PANEL KLIMPS (KL_21 to KL_30) ---")
        
        # Position variables
        expressions.extend([
            f"[Inch]KL_{klimp_number}_X = {nx_vars[f'KL_{klimp_number}_X']:.3f} // Position X coordinate",
            f"[Inch]KL_{klimp_number}_Y = {nx_vars[f'KL_{klimp_number}_Y']:.3f} // Position Y coordinate", 
            f"[Inch]KL_{klimp_number}_Z = {nx_vars[f'KL_{klimp_number}_Z']:.3f} // Position Z coordinate"
        ])
        
        # Quaternion variables (primary orientation representation)
        expressions.extend([
            f"KL_{klimp_number}_Q_W = {nx_vars[f'KL_{klimp_number}_Q_W']:.6f} // Quaternion W (scalar) component",
            f"KL_{klimp_number}_Q_X = {nx_vars[f'KL_{klimp_number}_Q_X']:.6f} // Quaternion X (i) component",
            f"KL_{klimp_number}_Q_Y = {nx_vars[f'KL_{klimp_number}_Q_Y']:.6f} // Quaternion Y (j) component",
            f"KL_{klimp_number}_Q_Z = {nx_vars[f'KL_{klimp_number}_Q_Z']:.6f} // Quaternion Z (k) component"
        ])
        
        # Unit vector direction variables (derived from quaternion)
        expressions.extend([
            f"KL_{klimp_number}_X_DIR_X = {nx_vars[f'KL_{klimp_number}_X_DIR_X']:.6f} // X-axis direction X component",
            f"KL_{klimp_number}_X_DIR_Y = {nx_vars[f'KL_{klimp_number}_X_DIR_Y']:.6f} // X-axis direction Y component",
            f"KL_{klimp_number}_X_DIR_Z = {nx_vars[f'KL_{klimp_number}_X_DIR_Z']:.6f} // X-axis direction Z component",
            
            f"KL_{klimp_number}_Y_DIR_X = {nx_vars[f'KL_{klimp_number}_Y_DIR_X']:.6f} // Y-axis direction X component",
            f"KL_{klimp_number}_Y_DIR_Y = {nx_vars[f'KL_{klimp_number}_Y_DIR_Y']:.6f} // Y-axis direction Y component", 
            f"KL_{klimp_number}_Y_DIR_Z = {nx_vars[f'KL_{klimp_number}_Y_DIR_Z']:.6f} // Y-axis direction Z component",
            
            f"KL_{klimp_number}_Z_DIR_X = {nx_vars[f'KL_{klimp_number}_Z_DIR_X']:.6f} // Z-axis direction X component",
            f"KL_{klimp_number}_Z_DIR_Y = {nx_vars[f'KL_{klimp_number}_Z_DIR_Y']:.6f} // Z-axis direction Y component",
            f"KL_{klimp_number}_Z_DIR_Z = {nx_vars[f'KL_{klimp_number}_Z_DIR_Z']:.6f} // Z-axis direction Z component"
        ])
        
        # Axis-angle representation (derived from quaternion)
        expressions.extend([
            f"KL_{klimp_number}_AXIS_X = {nx_vars[f'KL_{klimp_number}_AXIS_X']:.6f} // Rotation axis X component",
            f"KL_{klimp_number}_AXIS_Y = {nx_vars[f'KL_{klimp_number}_AXIS_Y']:.6f} // Rotation axis Y component",
            f"KL_{klimp_number}_AXIS_Z = {nx_vars[f'KL_{klimp_number}_AXIS_Z']:.6f} // Rotation axis Z component",
            f"KL_{klimp_number}_ANGLE = {nx_vars[f'KL_{klimp_number}_ANGLE']:.3f} // Rotation angle (degrees)"
        ])
        
        # Legacy compatibility variables
        expressions.extend([
            f"KL_{klimp_number}_RX = {nx_vars[f'KL_{klimp_number}_RX']:.3f} // Legacy Euler angle X rotation (degrees)",
            f"KL_{klimp_number}_RY = {nx_vars[f'KL_{klimp_number}_RY']:.3f} // Legacy Euler angle Y rotation (degrees)",
            f"KL_{klimp_number}_RZ = {nx_vars[f'KL_{klimp_number}_RZ']:.3f} // Legacy Euler angle Z rotation (degrees)",
            f"KL_{klimp_number}_ROTATE = {nx_vars[f'KL_{klimp_number}_ROTATE']:.0f} // Legacy simple rotation",
            f"KL_{klimp_number}_SUPPRESS = {nx_vars[f'KL_{klimp_number}_SUPPRESS']} // Suppress flag (0=hide, 1=show)"
        ])
        
        # Add spacing between klimps
        expressions.append("")
    
    return expressions


def verify_quaternion_consistency(orientations: List[KlimpQuaternionOrientation]) -> Dict[str, Any]:
    """
    Verify that all quaternions are properly normalized and mathematically valid.
    
    Args:
        orientations: List of KlimpQuaternionOrientation objects to verify
        
    Returns:
        Dictionary with verification results
    """
    results = {
        "total_klimps": len(orientations),
        "valid_quaternions": 0,
        "invalid_quaternions": [],
        "errors": []
    }
    
    for i, orientation in enumerate(orientations):
        klimp_number = i + 1
        
        try:
            if validate_quaternion(orientation.quaternion):
                results["valid_quaternions"] += 1
                
                # Additional checks
                # Verify unit vectors are orthogonal
                x_axis, y_axis, z_axis = orientation.to_unit_vectors()
                
                # Check orthogonality (dot products should be ~0)
                xy_dot = sum(a*b for a, b in zip(x_axis, y_axis))
                xz_dot = sum(a*b for a, b in zip(x_axis, z_axis))
                yz_dot = sum(a*b for a, b in zip(y_axis, z_axis))
                
                if abs(xy_dot) > 0.01 or abs(xz_dot) > 0.01 or abs(yz_dot) > 0.01:
                    results["invalid_quaternions"].append(klimp_number)
                    results["errors"].append(f"KL_{klimp_number}: Unit vectors not orthogonal")
            else:
                results["invalid_quaternions"].append(klimp_number)
                results["errors"].append(f"KL_{klimp_number}: Quaternion not normalized")
        
        except Exception as e:
            results["invalid_quaternions"].append(klimp_number)
            results["errors"].append(f"KL_{klimp_number}: Validation error - {str(e)}")
    
    results["success"] = len(results["invalid_quaternions"]) == 0
    results["success_rate"] = results["valid_quaternions"] / results["total_klimps"] * 100.0
    
    return results


def create_test_quaternion_configuration() -> List[KlimpQuaternionOrientation]:
    """
    Create a test configuration with known quaternion orientations for validation.
    
    Returns:
        List of test KlimpQuaternionOrientation objects
    """
    test_orientations = []
    
    # Test top panel klimps (identity quaternion)
    for i in range(5):
        x_pos = -20.0 + (i * 10.0)  # Spread across top
        orientation = KlimpQuaternionOrientation.top_panel_orientation(x_pos, 0.0, 50.0)
        test_orientations.append(orientation)
    
    # Test left panel klimps (-90° Z rotation quaternion)
    for i in range(3):
        y_pos = -10.0 + (i * 10.0)  # Spread along left side
        z_pos = 20.0 + (i * 10.0)   # Spread vertically
        orientation = KlimpQuaternionOrientation.left_panel_orientation(-25.0, y_pos, z_pos)
        test_orientations.append(orientation)
    
    # Test right panel klimps (+90° Z rotation quaternion)
    for i in range(3):
        y_pos = -10.0 + (i * 10.0)  # Spread along right side
        z_pos = 20.0 + (i * 10.0)   # Spread vertically
        orientation = KlimpQuaternionOrientation.right_panel_orientation(25.0, y_pos, z_pos)
        test_orientations.append(orientation)
    
    # Test interpolation between orientations
    start_orient = KlimpQuaternionOrientation.top_panel_orientation(0.0, 0.0, 0.0)
    end_orient = KlimpQuaternionOrientation.left_panel_orientation(0.0, 0.0, 0.0)
    
    for i in range(3):
        t = (i + 1) / 4.0  # 0.25, 0.5, 0.75
        interp_orient = interpolate_klimp_orientations(start_orient, end_orient, t)
        interp_orient.position_x = t * 30.0  # Move position during interpolation
        test_orientations.append(interp_orient)
    
    # Fill remaining slots with suppressed klimps
    while len(test_orientations) < 30:
        orientation = KlimpQuaternionOrientation.identity(0.0, 0.0, 0.0)
        orientation.suppress = True
        test_orientations.append(orientation)
    
    return test_orientations


def compare_quaternion_and_unit_vector_systems(
    panel_width: float = 48.0,
    panel_length: float = 48.0,
    panel_height: float = 48.0
) -> Dict[str, Any]:
    """
    Compare results between quaternion system and unit vector system.
    
    Returns:
        Dictionary with comparison results and differences
    """
    # Generate quaternion orientations
    quaternion_orientations = calculate_klimp_quaternion_orientations(
        panel_width=panel_width,
        panel_length=panel_length,
        panel_height=panel_height
    )
    
    comparison = {
        "klimp_count": len(quaternion_orientations),
        "quaternion_magnitudes": [],
        "euler_angle_comparisons": [],
        "unit_vector_comparisons": [],
        "max_euler_diff": 0.0,
        "max_unit_vector_diff": 0.0
    }
    
    # Analyze each klimp
    for i, orientation in enumerate(quaternion_orientations):
        klimp_number = i + 1
        
        # Check quaternion magnitude (should be 1.0)
        quat_magnitude = orientation.quaternion.magnitude()
        comparison["quaternion_magnitudes"].append({
            "klimp": klimp_number,
            "magnitude": quat_magnitude,
            "normalized": abs(quat_magnitude - 1.0) < 0.001
        })
        
        # Compare with expected Euler angles
        rx, ry, rz = orientation.to_euler_angles()
        
        # Expected rotations based on klimp position
        if klimp_number <= 10:  # Top panel
            expected_rz = 0.0
        elif klimp_number <= 20:  # Left panel
            expected_rz = -90.0
        else:  # Right panel
            expected_rz = 90.0
        
        euler_diff = abs(rz - expected_rz)
        comparison["euler_angle_comparisons"].append({
            "klimp": klimp_number,
            "expected_rz": expected_rz,
            "actual_rz": rz,
            "difference": euler_diff
        })
        
        comparison["max_euler_diff"] = max(comparison["max_euler_diff"], euler_diff)
        
        # Check unit vector orthogonality
        x_axis, y_axis, z_axis = orientation.to_unit_vectors()
        
        # Check that unit vectors are actually unit length
        x_len = math.sqrt(sum(a**2 for a in x_axis))
        y_len = math.sqrt(sum(a**2 for a in y_axis))
        z_len = math.sqrt(sum(a**2 for a in z_axis))
        
        unit_vector_error = max(abs(x_len - 1.0), abs(y_len - 1.0), abs(z_len - 1.0))
        comparison["unit_vector_comparisons"].append({
            "klimp": klimp_number,
            "x_length": x_len,
            "y_length": y_len,
            "z_length": z_len,
            "max_error": unit_vector_error
        })
        
        comparison["max_unit_vector_diff"] = max(comparison["max_unit_vector_diff"], unit_vector_error)
    
    return comparison