"""
Integration module for klimp unit vector system with existing placement logic.

This module bridges the existing klimp placement algorithms with the new
unit vector orientation system, providing seamless integration while
maintaining backward compatibility.
"""

from typing import Dict, List, Any, Tuple
import math
from .klimp_unit_vector_system import KlimpOrientation, UnitVector
from .klimp_placement_logic_all_sides import calculate_all_klimp_placements


def calculate_klimp_unit_vectors(
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
) -> List[KlimpOrientation]:
    """
    Calculate klimp positions and orientations using unit vector system.
    
    This function integrates the existing placement logic with the new
    unit vector orientation system.
    
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
        List of KlimpOrientation objects for all 30 possible klimps
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
            
            orientation = KlimpOrientation.top_panel_orientation(abs_x, abs_y, abs_z)
            orientation.suppress = False
        else:
            # Suppressed klimp with zero position
            orientation = KlimpOrientation.top_panel_orientation(0.0, 0.0, 0.0)
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
            
            orientation = KlimpOrientation.left_panel_orientation(abs_x, abs_y, abs_z)
            orientation.suppress = False
        else:
            # Suppressed klimp with zero position  
            orientation = KlimpOrientation.left_panel_orientation(0.0, 0.0, 0.0)
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
            
            orientation = KlimpOrientation.right_panel_orientation(abs_x, abs_y, abs_z)
            orientation.suppress = False
        else:
            # Suppressed klimp with zero position
            orientation = KlimpOrientation.right_panel_orientation(0.0, 0.0, 0.0)
            orientation.suppress = True
        
        orientations.append(orientation)
    
    return orientations


def generate_klimp_nx_expressions(orientations: List[KlimpOrientation]) -> List[str]:
    """
    Generate NX expression strings for klimp unit vectors.
    
    Args:
        orientations: List of KlimpOrientation objects
        
    Returns:
        List of formatted NX expression strings
    """
    expressions = []
    
    # Header comments
    expressions.extend([
        "",
        "// ========================================",
        "// KLIMP UNIT VECTOR ORIENTATION SYSTEM",
        "// ========================================",
        "// Each klimp is defined by:",
        "// - Position: KL_XX_X, KL_XX_Y, KL_XX_Z",
        "// - X-Axis Direction: KL_XX_X_DIR_X, KL_XX_X_DIR_Y, KL_XX_X_DIR_Z",
        "// - Y-Axis Direction: KL_XX_Y_DIR_X, KL_XX_Y_DIR_Y, KL_XX_Y_DIR_Z", 
        "// - Z-Axis Direction: KL_XX_Z_DIR_X, KL_XX_Z_DIR_Y, KL_XX_Z_DIR_Z",
        "// - Legacy Compatibility: KL_XX_RX, KL_XX_RY, KL_XX_RZ, KL_XX_ROTATE",
        "// - Suppress Flag: KL_XX_SUPPRESS (0=hide, 1=show)",
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
        
        # Unit vector direction variables
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


def verify_unit_vector_consistency(orientations: List[KlimpOrientation]) -> Dict[str, Any]:
    """
    Verify that all unit vectors are properly normalized and orthogonal.
    
    Args:
        orientations: List of KlimpOrientation objects to verify
        
    Returns:
        Dictionary with verification results
    """
    from .klimp_unit_vector_system import validate_orthogonality
    
    results = {
        "total_klimps": len(orientations),
        "valid_klimps": 0,
        "invalid_klimps": [],
        "errors": []
    }
    
    for i, orientation in enumerate(orientations):
        klimp_number = i + 1
        
        try:
            if validate_orthogonality(orientation):
                results["valid_klimps"] += 1
            else:
                results["invalid_klimps"].append(klimp_number)
                results["errors"].append(f"KL_{klimp_number}: Failed orthogonality validation")
        
        except Exception as e:
            results["invalid_klimps"].append(klimp_number)
            results["errors"].append(f"KL_{klimp_number}: Validation error - {str(e)}")
    
    results["success"] = len(results["invalid_klimps"]) == 0
    results["success_rate"] = results["valid_klimps"] / results["total_klimps"] * 100.0
    
    return results


def create_test_klimp_configuration() -> List[KlimpOrientation]:
    """
    Create a test configuration with known klimp orientations for validation.
    
    Returns:
        List of test KlimpOrientation objects
    """
    test_orientations = []
    
    # Test top panel klimps (identity orientation)
    for i in range(5):
        x_pos = -20.0 + (i * 10.0)  # Spread across top
        orientation = KlimpOrientation.top_panel_orientation(x_pos, 0.0, 50.0)
        test_orientations.append(orientation)
    
    # Test left panel klimps (-90° Z rotation)
    for i in range(3):
        y_pos = -10.0 + (i * 10.0)  # Spread along left side
        z_pos = 20.0 + (i * 10.0)   # Spread vertically
        orientation = KlimpOrientation.left_panel_orientation(-25.0, y_pos, z_pos)
        test_orientations.append(orientation)
    
    # Test right panel klimps (+90° Z rotation)
    for i in range(3):
        y_pos = -10.0 + (i * 10.0)  # Spread along right side
        z_pos = 20.0 + (i * 10.0)   # Spread vertically
        orientation = KlimpOrientation.right_panel_orientation(25.0, y_pos, z_pos)
        test_orientations.append(orientation)
    
    # Fill remaining slots with suppressed klimps
    while len(test_orientations) < 30:
        orientation = KlimpOrientation.identity(0.0, 0.0, 0.0)
        orientation.suppress = True
        test_orientations.append(orientation)
    
    return test_orientations


def compare_legacy_and_unit_vector_systems(
    panel_width: float = 48.0,
    panel_length: float = 48.0,
    panel_height: float = 48.0
) -> Dict[str, Any]:
    """
    Compare results between legacy Euler angle system and new unit vector system.
    
    Returns:
        Dictionary with comparison results and differences
    """
    # Generate unit vector orientations
    unit_vector_orientations = calculate_klimp_unit_vectors(
        panel_width=panel_width,
        panel_length=panel_length,
        panel_height=panel_height
    )
    
    comparison = {
        "klimp_count": len(unit_vector_orientations),
        "position_differences": [],
        "rotation_differences": [],
        "max_position_diff": 0.0,
        "max_rotation_diff": 0.0
    }
    
    # Analyze each klimp
    for i, orientation in enumerate(unit_vector_orientations):
        klimp_number = i + 1
        
        # Convert back to Euler angles for comparison
        rx, ry, rz = orientation.to_euler_angles()
        
        # Expected rotations based on klimp position
        if klimp_number <= 10:  # Top panel
            expected_rz = 0.0
        elif klimp_number <= 20:  # Left panel
            expected_rz = -90.0
        else:  # Right panel
            expected_rz = 90.0
        
        rotation_diff = abs(rz - expected_rz)
        comparison["rotation_differences"].append({
            "klimp": klimp_number,
            "expected_rz": expected_rz,
            "actual_rz": rz,
            "difference": rotation_diff
        })
        
        comparison["max_rotation_diff"] = max(comparison["max_rotation_diff"], rotation_diff)
    
    return comparison