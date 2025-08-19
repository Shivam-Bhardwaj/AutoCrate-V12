"""
Unit Vector System for Klimp Orientation in AutoCrate

This module implements a unit vector based orientation system for klimps,
treating each klimp as a point object with xyz coordinates and orthogonal
direction vectors. This eliminates gimbal lock issues and provides intuitive
orientation control.

Each klimp is defined by:
- Position: 3D coordinates (x, y, z)
- Orientation: Three orthogonal unit vectors (X-axis, Y-axis, Z-axis)
- Legacy support: Euler angles for backward compatibility
"""

import math
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass


@dataclass
class UnitVector:
    """Represents a 3D unit vector with x, y, z components."""
    x: float
    y: float
    z: float
    
    def __post_init__(self):
        """Normalize the vector to unit length."""
        magnitude = math.sqrt(self.x**2 + self.y**2 + self.z**2)
        if magnitude > 0.0001:  # Avoid division by zero
            self.x /= magnitude
            self.y /= magnitude
            self.z /= magnitude
    
    def normalize(self) -> 'UnitVector':
        """Return a normalized copy of this vector."""
        magnitude = math.sqrt(self.x**2 + self.y**2 + self.z**2)
        if magnitude > 0.0001:
            return UnitVector(self.x / magnitude, self.y / magnitude, self.z / magnitude)
        return UnitVector(1.0, 0.0, 0.0)  # Default to X-axis
    
    def cross(self, other: 'UnitVector') -> 'UnitVector':
        """Calculate cross product with another vector."""
        return UnitVector(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )
    
    def dot(self, other: 'UnitVector') -> float:
        """Calculate dot product with another vector."""
        return self.x * other.x + self.y * other.y + self.z * other.z


@dataclass
class KlimpOrientation:
    """
    Represents a klimp's complete orientation using orthogonal unit vectors.
    
    This provides a gimbal-lock-free representation of orientation that is
    intuitive for engineers and CAD systems.
    """
    position_x: float
    position_y: float
    position_z: float
    x_axis: UnitVector  # Primary direction vector
    y_axis: UnitVector  # Secondary direction vector
    z_axis: UnitVector  # Tertiary direction vector (computed from x × y)
    suppress: bool = False
    
    def __post_init__(self):
        """Ensure orthogonality and right-handed coordinate system."""
        # Normalize input vectors
        self.x_axis = self.x_axis.normalize()
        self.y_axis = self.y_axis.normalize()
        
        # Compute Z-axis as cross product of X and Y
        self.z_axis = self.x_axis.cross(self.y_axis).normalize()
        
        # Recompute Y-axis to ensure perfect orthogonality
        # Y = Z × X to maintain right-handed system
        self.y_axis = self.z_axis.cross(self.x_axis).normalize()
    
    @classmethod
    def from_euler_angles(cls, pos_x: float, pos_y: float, pos_z: float,
                         rx_deg: float, ry_deg: float, rz_deg: float) -> 'KlimpOrientation':
        """
        Create KlimpOrientation from Euler angles (for backward compatibility).
        
        Args:
            pos_x, pos_y, pos_z: Position coordinates
            rx_deg, ry_deg, rz_deg: Rotation angles in degrees
        
        Returns:
            KlimpOrientation with computed unit vectors
        """
        # Convert degrees to radians
        rx = math.radians(rx_deg)
        ry = math.radians(ry_deg)
        rz = math.radians(rz_deg)
        
        # Compute rotation matrix elements for ZYX Euler sequence
        # This matches the convention used in many CAD systems
        cos_x, sin_x = math.cos(rx), math.sin(rx)
        cos_y, sin_y = math.cos(ry), math.sin(ry)
        cos_z, sin_z = math.cos(rz), math.sin(rz)
        
        # Rotation matrix for ZYX Euler angles
        # X-axis direction after rotation
        x_axis = UnitVector(
            cos_y * cos_z,
            cos_y * sin_z,
            -sin_y
        )
        
        # Y-axis direction after rotation
        y_axis = UnitVector(
            sin_x * sin_y * cos_z - cos_x * sin_z,
            sin_x * sin_y * sin_z + cos_x * cos_z,
            sin_x * cos_y
        )
        
        # Z-axis direction after rotation
        z_axis = UnitVector(
            cos_x * sin_y * cos_z + sin_x * sin_z,
            cos_x * sin_y * sin_z - sin_x * cos_z,
            cos_x * cos_y
        )
        
        return cls(pos_x, pos_y, pos_z, x_axis, y_axis, z_axis)
    
    @classmethod
    def identity(cls, pos_x: float, pos_y: float, pos_z: float) -> 'KlimpOrientation':
        """Create identity orientation (no rotation)."""
        return cls(
            pos_x, pos_y, pos_z,
            UnitVector(1.0, 0.0, 0.0),  # X-axis
            UnitVector(0.0, 1.0, 0.0),  # Y-axis
            UnitVector(0.0, 0.0, 1.0)   # Z-axis
        )
    
    @classmethod
    def top_panel_orientation(cls, pos_x: float, pos_y: float, pos_z: float) -> 'KlimpOrientation':
        """Standard orientation for top panel klimps (no rotation)."""
        return cls.identity(pos_x, pos_y, pos_z)
    
    @classmethod
    def left_panel_orientation(cls, pos_x: float, pos_y: float, pos_z: float) -> 'KlimpOrientation':
        """Standard orientation for left panel klimps (-90° rotation about Z)."""
        return cls.from_euler_angles(pos_x, pos_y, pos_z, 0.0, 0.0, -90.0)
    
    @classmethod
    def right_panel_orientation(cls, pos_x: float, pos_y: float, pos_z: float) -> 'KlimpOrientation':
        """Standard orientation for right panel klimps (+90° rotation about Z)."""
        return cls.from_euler_angles(pos_x, pos_y, pos_z, 0.0, 0.0, 90.0)
    
    def to_euler_angles(self) -> Tuple[float, float, float]:
        """
        Convert unit vectors back to Euler angles for legacy compatibility.
        
        Returns:
            Tuple of (rx_deg, ry_deg, rz_deg) in degrees
        """
        # Extract Euler angles from rotation matrix formed by unit vectors
        # Using ZYX sequence to match CAD conventions
        
        # Rotation matrix from unit vectors
        r11, r12, r13 = self.x_axis.x, self.x_axis.y, self.x_axis.z
        r21, r22, r23 = self.y_axis.x, self.y_axis.y, self.y_axis.z
        r31, r32, r33 = self.z_axis.x, self.z_axis.y, self.z_axis.z
        
        # Extract Euler angles (ZYX sequence)
        # Handle singularity at ±90° Y rotation
        if abs(r13) < 0.99999:
            ry = -math.asin(r13)
            rx = math.atan2(r23, r33)
            rz = math.atan2(r12, r11)
        else:
            # Gimbal lock case - set one angle to zero
            ry = -math.pi/2 if r13 > 0 else math.pi/2
            rx = 0.0
            rz = math.atan2(-r21, r22)
        
        # Convert to degrees
        return (math.degrees(rx), math.degrees(ry), math.degrees(rz))
    
    def to_nx_expressions(self, klimp_number: int) -> Dict[str, Any]:
        """
        Generate NX expression variables for this klimp orientation.
        
        Args:
            klimp_number: Klimp identifier (1-30)
            
        Returns:
            Dictionary with all NX expression variables
        """
        rx_deg, ry_deg, rz_deg = self.to_euler_angles()
        
        return {
            # Position variables
            f"KL_{klimp_number}_X": self.position_x,
            f"KL_{klimp_number}_Y": self.position_y,
            f"KL_{klimp_number}_Z": self.position_z,
            
            # Unit vector direction variables (primary system)
            f"KL_{klimp_number}_X_DIR_X": self.x_axis.x,
            f"KL_{klimp_number}_X_DIR_Y": self.x_axis.y,
            f"KL_{klimp_number}_X_DIR_Z": self.x_axis.z,
            
            f"KL_{klimp_number}_Y_DIR_X": self.y_axis.x,
            f"KL_{klimp_number}_Y_DIR_Y": self.y_axis.y,
            f"KL_{klimp_number}_Y_DIR_Z": self.y_axis.z,
            
            f"KL_{klimp_number}_Z_DIR_X": self.z_axis.x,
            f"KL_{klimp_number}_Z_DIR_Y": self.z_axis.y,
            f"KL_{klimp_number}_Z_DIR_Z": self.z_axis.z,
            
            # Legacy Euler angle variables (for backward compatibility)
            f"KL_{klimp_number}_RX": rx_deg,
            f"KL_{klimp_number}_RY": ry_deg,
            f"KL_{klimp_number}_RZ": rz_deg,
            
            # Legacy rotation variable
            f"KL_{klimp_number}_ROTATE": rz_deg,  # Simple Z-rotation for legacy
            
            # Suppress flag
            f"KL_{klimp_number}_SUPPRESS": 0 if self.suppress else 1
        }


def create_klimp_orientations_from_placement_data(
    klimp_placement_data: Dict[str, Any]
) -> List[KlimpOrientation]:
    """
    Convert klimp placement data to KlimpOrientation objects.
    
    Args:
        klimp_placement_data: Output from klimp_placement_logic modules
        
    Returns:
        List of KlimpOrientation objects for all klimps
    """
    orientations = []
    
    # Process top klimps (KL_1 to KL_10)
    if "top_klimps" in klimp_placement_data:
        for klimp in klimp_placement_data["top_klimps"]:
            orientation = KlimpOrientation.top_panel_orientation(
                klimp.get("position_x", 0.0),
                klimp.get("position_y", 0.0),
                klimp.get("position_z", 0.0)
            )
            orientations.append(orientation)
    
    # Process left klimps (KL_11 to KL_20)
    if "left_klimps" in klimp_placement_data:
        for klimp in klimp_placement_data["left_klimps"]:
            orientation = KlimpOrientation.left_panel_orientation(
                klimp.get("position_x", 0.0),
                klimp.get("position_y", 0.0),
                klimp.get("position_z", 0.0)
            )
            orientations.append(orientation)
    
    # Process right klimps (KL_21 to KL_30)
    if "right_klimps" in klimp_placement_data:
        for klimp in klimp_placement_data["right_klimps"]:
            orientation = KlimpOrientation.right_panel_orientation(
                klimp.get("position_x", 0.0),
                klimp.get("position_y", 0.0),
                klimp.get("position_z", 0.0)
            )
            orientations.append(orientation)
    
    return orientations


def validate_orthogonality(orientation: KlimpOrientation, tolerance: float = 0.001) -> bool:
    """
    Validate that the orientation vectors are orthogonal and unit length.
    
    Args:
        orientation: KlimpOrientation to validate
        tolerance: Numerical tolerance for validation
        
    Returns:
        True if orientation is valid, False otherwise
    """
    # Check unit length
    x_mag = math.sqrt(orientation.x_axis.x**2 + orientation.x_axis.y**2 + orientation.x_axis.z**2)
    y_mag = math.sqrt(orientation.y_axis.x**2 + orientation.y_axis.y**2 + orientation.y_axis.z**2)
    z_mag = math.sqrt(orientation.z_axis.x**2 + orientation.z_axis.y**2 + orientation.z_axis.z**2)
    
    if abs(x_mag - 1.0) > tolerance or abs(y_mag - 1.0) > tolerance or abs(z_mag - 1.0) > tolerance:
        return False
    
    # Check orthogonality
    xy_dot = orientation.x_axis.dot(orientation.y_axis)
    xz_dot = orientation.x_axis.dot(orientation.z_axis)
    yz_dot = orientation.y_axis.dot(orientation.z_axis)
    
    if abs(xy_dot) > tolerance or abs(xz_dot) > tolerance or abs(yz_dot) > tolerance:
        return False
    
    # Check right-handed system: z = x × y
    computed_z = orientation.x_axis.cross(orientation.y_axis)
    z_diff = math.sqrt(
        (computed_z.x - orientation.z_axis.x)**2 +
        (computed_z.y - orientation.z_axis.y)**2 +
        (computed_z.z - orientation.z_axis.z)**2
    )
    
    return z_diff < tolerance


# Predefined standard orientations for common klimp configurations
STANDARD_ORIENTATIONS = {
    "identity": (UnitVector(1.0, 0.0, 0.0), UnitVector(0.0, 1.0, 0.0), UnitVector(0.0, 0.0, 1.0)),
    "top_panel": (UnitVector(1.0, 0.0, 0.0), UnitVector(0.0, 1.0, 0.0), UnitVector(0.0, 0.0, 1.0)),
    "left_panel": (UnitVector(0.0, 1.0, 0.0), UnitVector(-1.0, 0.0, 0.0), UnitVector(0.0, 0.0, 1.0)),
    "right_panel": (UnitVector(0.0, -1.0, 0.0), UnitVector(1.0, 0.0, 0.0), UnitVector(0.0, 0.0, 1.0)),
    "face_inward": (UnitVector(-1.0, 0.0, 0.0), UnitVector(0.0, 1.0, 0.0), UnitVector(0.0, 0.0, -1.0))
}