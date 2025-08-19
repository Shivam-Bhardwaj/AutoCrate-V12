"""
Quaternion-based Klimp Orientation System for AutoCrate

This module implements a quaternion-based orientation system for klimps,
providing the most mathematically robust and efficient representation for
3D rotations. Quaternions eliminate gimbal lock, provide smooth interpolation,
and are computationally efficient.

Key advantages of quaternions:
- No gimbal lock
- Compact representation (4 values vs 9 for rotation matrices)
- Smooth interpolation (SLERP)
- Numerically stable
- Efficient composition of rotations
- Industry standard for 3D graphics and robotics
"""

import math
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass


@dataclass
class Quaternion:
    """
    Represents a quaternion for 3D rotations.
    
    Uses the convention: q = w + xi + yj + zk
    where w is the scalar (real) part and (x, y, z) is the vector (imaginary) part.
    
    For unit quaternions representing rotations:
    - w = cos(θ/2) where θ is the rotation angle
    - (x, y, z) = sin(θ/2) * (axis unit vector)
    """
    w: float  # Scalar (real) component
    x: float  # i component
    y: float  # j component  
    z: float  # k component
    
    def __post_init__(self):
        """Ensure the quaternion is normalized for rotation representation."""
        self.normalize()
    
    def normalize(self) -> 'Quaternion':
        """Normalize the quaternion to unit length."""
        magnitude = math.sqrt(self.w**2 + self.x**2 + self.y**2 + self.z**2)
        if magnitude > 1e-10:  # Avoid division by zero
            self.w /= magnitude
            self.x /= magnitude
            self.y /= magnitude
            self.z /= magnitude
        else:
            # Degenerate case - set to identity quaternion
            self.w, self.x, self.y, self.z = 1.0, 0.0, 0.0, 0.0
        return self
    
    def magnitude(self) -> float:
        """Calculate the magnitude (norm) of the quaternion."""
        return math.sqrt(self.w**2 + self.x**2 + self.y**2 + self.z**2)
    
    def conjugate(self) -> 'Quaternion':
        """Return the conjugate of the quaternion (w, -x, -y, -z)."""
        return Quaternion(self.w, -self.x, -self.y, -self.z)
    
    def inverse(self) -> 'Quaternion':
        """Return the inverse of the quaternion (conjugate for unit quaternions)."""
        # For unit quaternions, inverse = conjugate
        mag_sq = self.w**2 + self.x**2 + self.y**2 + self.z**2
        if mag_sq > 1e-10:
            conj = self.conjugate()
            return Quaternion(conj.w/mag_sq, conj.x/mag_sq, conj.y/mag_sq, conj.z/mag_sq)
        else:
            return Quaternion(1.0, 0.0, 0.0, 0.0)  # Identity
    
    def multiply(self, other: 'Quaternion') -> 'Quaternion':
        """
        Multiply this quaternion by another quaternion.
        
        Quaternion multiplication: q1 * q2
        Result represents the composition of rotations (q2 followed by q1).
        """
        w = self.w * other.w - self.x * other.x - self.y * other.y - self.z * other.z
        x = self.w * other.x + self.x * other.w + self.y * other.z - self.z * other.y
        y = self.w * other.y - self.x * other.z + self.y * other.w + self.z * other.x
        z = self.w * other.z + self.x * other.y - self.y * other.x + self.z * other.w
        return Quaternion(w, x, y, z)
    
    def rotate_vector(self, vector: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """
        Rotate a 3D vector using this quaternion.
        
        Uses the formula: v' = q * v * q*
        where v is treated as a pure quaternion (0, vx, vy, vz).
        """
        vx, vy, vz = vector
        
        # Convert vector to pure quaternion
        v_quat = Quaternion(0, vx, vy, vz)
        
        # Perform rotation: q * v * q*
        result = self.multiply(v_quat).multiply(self.conjugate())
        
        return (result.x, result.y, result.z)
    
    def to_axis_angle(self) -> Tuple[Tuple[float, float, float], float]:
        """
        Convert quaternion to axis-angle representation.
        
        Returns:
            Tuple of (axis_vector, angle_radians)
        """
        # Ensure w is positive to get the shorter rotation
        q = self if self.w >= 0 else Quaternion(-self.w, -self.x, -self.y, -self.z)
        
        # Calculate angle
        angle = 2.0 * math.acos(min(1.0, abs(q.w)))  # Clamp for numerical stability
        
        # Calculate axis
        sin_half_angle = math.sqrt(1.0 - q.w**2)
        if sin_half_angle > 1e-10:
            axis = (q.x / sin_half_angle, q.y / sin_half_angle, q.z / sin_half_angle)
        else:
            # Near zero rotation - axis is arbitrary
            axis = (1.0, 0.0, 0.0)
        
        return axis, angle
    
    def to_euler_angles(self, order: str = 'ZYX') -> Tuple[float, float, float]:
        """
        Convert quaternion to Euler angles.
        
        Args:
            order: Rotation order (default 'ZYX' for aerospace/CAD)
            
        Returns:
            Tuple of (rx, ry, rz) in radians
        """
        if order == 'ZYX':
            # Extract rotation matrix elements needed for ZYX Euler angles
            w, x, y, z = self.w, self.x, self.y, self.z
            
            # Rotation matrix elements
            r11 = 1 - 2*(y**2 + z**2)
            r12 = 2*(x*y + w*z)
            r13 = 2*(x*z - w*y)
            r23 = 2*(y*z + w*x)
            r33 = 1 - 2*(x**2 + y**2)
            
            # Extract Euler angles
            # Handle singularity at ±90° Y rotation
            if abs(r13) < 0.99999:
                ry = -math.asin(r13)
                rx = math.atan2(r23, r33)
                rz = math.atan2(r12, r11)
            else:
                # Gimbal lock case
                ry = -math.pi/2 if r13 > 0 else math.pi/2
                rx = 0.0
                rz = math.atan2(-2*(x*y - w*z), 1 - 2*(y**2 + z**2))
            
            return (rx, ry, rz)
        else:
            raise NotImplementedError(f"Euler order {order} not implemented")
    
    def to_rotation_matrix(self) -> List[List[float]]:
        """
        Convert quaternion to 3x3 rotation matrix.
        
        Returns:
            3x3 rotation matrix as list of lists
        """
        w, x, y, z = self.w, self.x, self.y, self.z
        
        # Calculate rotation matrix elements
        matrix = [
            [1 - 2*(y**2 + z**2), 2*(x*y - w*z), 2*(x*z + w*y)],
            [2*(x*y + w*z), 1 - 2*(x**2 + z**2), 2*(y*z - w*x)],
            [2*(x*z - w*y), 2*(y*z + w*x), 1 - 2*(x**2 + y**2)]
        ]
        
        return matrix
    
    def to_unit_vectors(self) -> Tuple[Tuple[float, float, float], 
                                      Tuple[float, float, float], 
                                      Tuple[float, float, float]]:
        """
        Convert quaternion to orthogonal unit vectors (X, Y, Z axes).
        
        Returns:
            Tuple of (x_axis, y_axis, z_axis) unit vectors
        """
        # Standard basis vectors
        x_basis = (1.0, 0.0, 0.0)
        y_basis = (0.0, 1.0, 0.0)
        z_basis = (0.0, 0.0, 1.0)
        
        # Rotate basis vectors to get the orientation axes
        x_axis = self.rotate_vector(x_basis)
        y_axis = self.rotate_vector(y_basis)
        z_axis = self.rotate_vector(z_basis)
        
        return x_axis, y_axis, z_axis
    
    @classmethod
    def identity(cls) -> 'Quaternion':
        """Create an identity quaternion (no rotation)."""
        return cls(1.0, 0.0, 0.0, 0.0)
    
    @classmethod
    def from_axis_angle(cls, axis: Tuple[float, float, float], angle_radians: float) -> 'Quaternion':
        """
        Create a quaternion from axis-angle representation.
        
        Args:
            axis: Rotation axis as (x, y, z) unit vector
            angle_radians: Rotation angle in radians
            
        Returns:
            Quaternion representing the rotation
        """
        # Normalize the axis
        ax, ay, az = axis
        axis_length = math.sqrt(ax**2 + ay**2 + az**2)
        if axis_length > 1e-10:
            ax, ay, az = ax/axis_length, ay/axis_length, az/axis_length
        else:
            # Degenerate axis - return identity
            return cls.identity()
        
        half_angle = angle_radians / 2.0
        sin_half = math.sin(half_angle)
        cos_half = math.cos(half_angle)
        
        return cls(cos_half, ax * sin_half, ay * sin_half, az * sin_half)
    
    @classmethod
    def from_euler_angles(cls, rx: float, ry: float, rz: float, order: str = 'ZYX') -> 'Quaternion':
        """
        Create a quaternion from Euler angles.
        
        Args:
            rx, ry, rz: Rotation angles in radians
            order: Rotation order (default 'ZYX')
            
        Returns:
            Quaternion representing the rotation
        """
        if order == 'ZYX':
            # Convert to quaternion using half-angles
            cx = math.cos(rx / 2.0)
            sx = math.sin(rx / 2.0)
            cy = math.cos(ry / 2.0)
            sy = math.sin(ry / 2.0)
            cz = math.cos(rz / 2.0)
            sz = math.sin(rz / 2.0)
            
            # Quaternion composition for ZYX order
            w = cx*cy*cz + sx*sy*sz
            x = sx*cy*cz - cx*sy*sz
            y = cx*sy*cz + sx*cy*sz
            z = cx*cy*sz - sx*sy*cz
            
            return cls(w, x, y, z)
        else:
            raise NotImplementedError(f"Euler order {order} not implemented")
    
    @classmethod
    def from_rotation_matrix(cls, matrix: List[List[float]]) -> 'Quaternion':
        """
        Create a quaternion from a 3x3 rotation matrix.
        
        Args:
            matrix: 3x3 rotation matrix as list of lists
            
        Returns:
            Quaternion representing the rotation
        """
        m = matrix
        trace = m[0][0] + m[1][1] + m[2][2]
        
        if trace > 0:
            s = math.sqrt(trace + 1.0) * 2  # s = 4 * qw
            w = 0.25 * s
            x = (m[2][1] - m[1][2]) / s
            y = (m[0][2] - m[2][0]) / s
            z = (m[1][0] - m[0][1]) / s
        elif m[0][0] > m[1][1] and m[0][0] > m[2][2]:
            s = math.sqrt(1.0 + m[0][0] - m[1][1] - m[2][2]) * 2  # s = 4 * qx
            w = (m[2][1] - m[1][2]) / s
            x = 0.25 * s
            y = (m[0][1] + m[1][0]) / s
            z = (m[0][2] + m[2][0]) / s
        elif m[1][1] > m[2][2]:
            s = math.sqrt(1.0 + m[1][1] - m[0][0] - m[2][2]) * 2  # s = 4 * qy
            w = (m[0][2] - m[2][0]) / s
            x = (m[0][1] + m[1][0]) / s
            y = 0.25 * s
            z = (m[1][2] + m[2][1]) / s
        else:
            s = math.sqrt(1.0 + m[2][2] - m[0][0] - m[1][1]) * 2  # s = 4 * qz
            w = (m[1][0] - m[0][1]) / s
            x = (m[0][2] + m[2][0]) / s
            y = (m[1][2] + m[2][1]) / s
            z = 0.25 * s
        
        return cls(w, x, y, z)
    
    def slerp(self, other: 'Quaternion', t: float) -> 'Quaternion':
        """
        Spherical linear interpolation between two quaternions.
        
        Args:
            other: Target quaternion
            t: Interpolation parameter (0.0 to 1.0)
            
        Returns:
            Interpolated quaternion
        """
        # Ensure we take the shorter path
        dot = self.w*other.w + self.x*other.x + self.y*other.y + self.z*other.z
        
        if dot < 0:
            other = Quaternion(-other.w, -other.x, -other.y, -other.z)
            dot = -dot
        
        # If quaternions are very close, use linear interpolation
        if dot > 0.9995:
            result = Quaternion(
                self.w + t * (other.w - self.w),
                self.x + t * (other.x - self.x),
                self.y + t * (other.y - self.y),
                self.z + t * (other.z - self.z)
            )
            return result.normalize()
        
        # Calculate angle between quaternions
        theta_0 = math.acos(abs(dot))
        sin_theta_0 = math.sin(theta_0)
        
        theta = theta_0 * t
        sin_theta = math.sin(theta)
        
        s0 = math.cos(theta) - dot * sin_theta / sin_theta_0
        s1 = sin_theta / sin_theta_0
        
        return Quaternion(
            s0 * self.w + s1 * other.w,
            s0 * self.x + s1 * other.x,
            s0 * self.y + s1 * other.y,
            s0 * self.z + s1 * other.z
        )


@dataclass
class KlimpQuaternionOrientation:
    """
    Represents a klimp's complete orientation using quaternions.
    
    This provides the most mathematically robust representation of orientation
    that is compact, efficient, and free from singularities.
    """
    position_x: float
    position_y: float
    position_z: float
    quaternion: Quaternion
    suppress: bool = False
    
    @classmethod
    def identity(cls, pos_x: float, pos_y: float, pos_z: float) -> 'KlimpQuaternionOrientation':
        """Create identity orientation (no rotation)."""
        return cls(pos_x, pos_y, pos_z, Quaternion.identity())
    
    @classmethod
    def from_euler_angles(cls, pos_x: float, pos_y: float, pos_z: float,
                         rx_deg: float, ry_deg: float, rz_deg: float) -> 'KlimpQuaternionOrientation':
        """Create orientation from Euler angles."""
        rx_rad = math.radians(rx_deg)
        ry_rad = math.radians(ry_deg)
        rz_rad = math.radians(rz_deg)
        
        quat = Quaternion.from_euler_angles(rx_rad, ry_rad, rz_rad)
        return cls(pos_x, pos_y, pos_z, quat)
    
    @classmethod
    def from_axis_angle(cls, pos_x: float, pos_y: float, pos_z: float,
                       axis: Tuple[float, float, float], angle_deg: float) -> 'KlimpQuaternionOrientation':
        """Create orientation from axis-angle representation."""
        angle_rad = math.radians(angle_deg)
        quat = Quaternion.from_axis_angle(axis, angle_rad)
        return cls(pos_x, pos_y, pos_z, quat)
    
    @classmethod
    def top_panel_orientation(cls, pos_x: float, pos_y: float, pos_z: float) -> 'KlimpQuaternionOrientation':
        """Standard orientation for top panel klimps (no rotation)."""
        return cls.identity(pos_x, pos_y, pos_z)
    
    @classmethod
    def left_panel_orientation(cls, pos_x: float, pos_y: float, pos_z: float) -> 'KlimpQuaternionOrientation':
        """Standard orientation for left panel klimps (-90° rotation about Z)."""
        return cls.from_euler_angles(pos_x, pos_y, pos_z, 0.0, 0.0, -90.0)
    
    @classmethod
    def right_panel_orientation(cls, pos_x: float, pos_y: float, pos_z: float) -> 'KlimpQuaternionOrientation':
        """Standard orientation for right panel klimps (+90° rotation about Z)."""
        return cls.from_euler_angles(pos_x, pos_y, pos_z, 0.0, 0.0, 90.0)
    
    def to_euler_angles(self) -> Tuple[float, float, float]:
        """Convert to Euler angles in degrees."""
        rx, ry, rz = self.quaternion.to_euler_angles()
        return (math.degrees(rx), math.degrees(ry), math.degrees(rz))
    
    def to_unit_vectors(self) -> Tuple[Tuple[float, float, float], 
                                      Tuple[float, float, float], 
                                      Tuple[float, float, float]]:
        """Convert to orthogonal unit vectors."""
        return self.quaternion.to_unit_vectors()
    
    def to_axis_angle(self) -> Tuple[Tuple[float, float, float], float]:
        """Convert to axis-angle representation (angle in degrees)."""
        axis, angle_rad = self.quaternion.to_axis_angle()
        return axis, math.degrees(angle_rad)
    
    def to_nx_expressions(self, klimp_number: int) -> Dict[str, Any]:
        """
        Generate NX expression variables for this klimp orientation.
        
        Generates:
        - Position variables (KL_XX_X, KL_XX_Y, KL_XX_Z)
        - Quaternion variables (KL_XX_Q_W, KL_XX_Q_X, KL_XX_Q_Y, KL_XX_Q_Z)
        - Unit vector variables (for compatibility)
        - Legacy Euler angle variables (for backward compatibility)
        - Suppress flag
        
        Args:
            klimp_number: Klimp identifier (1-30)
            
        Returns:
            Dictionary with all NX expression variables
        """
        # Get derived representations
        rx_deg, ry_deg, rz_deg = self.to_euler_angles()
        x_axis, y_axis, z_axis = self.to_unit_vectors()
        axis, angle_deg = self.to_axis_angle()
        
        return {
            # Position variables
            f"KL_{klimp_number}_X": self.position_x,
            f"KL_{klimp_number}_Y": self.position_y,
            f"KL_{klimp_number}_Z": self.position_z,
            
            # Quaternion variables (primary orientation representation)
            f"KL_{klimp_number}_Q_W": self.quaternion.w,
            f"KL_{klimp_number}_Q_X": self.quaternion.x,
            f"KL_{klimp_number}_Q_Y": self.quaternion.y,
            f"KL_{klimp_number}_Q_Z": self.quaternion.z,
            
            # Unit vector direction variables (derived from quaternion)
            f"KL_{klimp_number}_X_DIR_X": x_axis[0],
            f"KL_{klimp_number}_X_DIR_Y": x_axis[1],
            f"KL_{klimp_number}_X_DIR_Z": x_axis[2],
            
            f"KL_{klimp_number}_Y_DIR_X": y_axis[0],
            f"KL_{klimp_number}_Y_DIR_Y": y_axis[1],
            f"KL_{klimp_number}_Y_DIR_Z": y_axis[2],
            
            f"KL_{klimp_number}_Z_DIR_X": z_axis[0],
            f"KL_{klimp_number}_Z_DIR_Y": z_axis[1],
            f"KL_{klimp_number}_Z_DIR_Z": z_axis[2],
            
            # Axis-angle representation
            f"KL_{klimp_number}_AXIS_X": axis[0],
            f"KL_{klimp_number}_AXIS_Y": axis[1],
            f"KL_{klimp_number}_AXIS_Z": axis[2],
            f"KL_{klimp_number}_ANGLE": angle_deg,
            
            # Legacy Euler angle variables (for backward compatibility)
            f"KL_{klimp_number}_RX": rx_deg,
            f"KL_{klimp_number}_RY": ry_deg,
            f"KL_{klimp_number}_RZ": rz_deg,
            
            # Legacy simple rotation variable
            f"KL_{klimp_number}_ROTATE": rz_deg,  # Simple Z-rotation for legacy
            
            # Suppress flag
            f"KL_{klimp_number}_SUPPRESS": 0 if self.suppress else 1
        }


def validate_quaternion(quaternion: Quaternion, tolerance: float = 0.001) -> bool:
    """
    Validate that a quaternion is properly normalized.
    
    Args:
        quaternion: Quaternion to validate
        tolerance: Numerical tolerance for validation
        
    Returns:
        True if quaternion is valid, False otherwise
    """
    magnitude = quaternion.magnitude()
    return abs(magnitude - 1.0) < tolerance


def interpolate_klimp_orientations(
    start: KlimpQuaternionOrientation, 
    end: KlimpQuaternionOrientation, 
    t: float
) -> KlimpQuaternionOrientation:
    """
    Interpolate between two klimp orientations using SLERP for rotation.
    
    Args:
        start: Starting orientation
        end: Ending orientation
        t: Interpolation parameter (0.0 to 1.0)
        
    Returns:
        Interpolated orientation
    """
    # Linear interpolation for position
    pos_x = start.position_x + t * (end.position_x - start.position_x)
    pos_y = start.position_y + t * (end.position_y - start.position_y)
    pos_z = start.position_z + t * (end.position_z - start.position_z)
    
    # Spherical linear interpolation for orientation
    interp_quat = start.quaternion.slerp(end.quaternion, t)
    
    return KlimpQuaternionOrientation(pos_x, pos_y, pos_z, interp_quat)


# Predefined standard quaternions for common klimp orientations
STANDARD_QUATERNIONS = {
    "identity": Quaternion.identity(),
    "top_panel": Quaternion.identity(),
    "left_panel": Quaternion.from_euler_angles(0.0, 0.0, math.radians(-90.0)),
    "right_panel": Quaternion.from_euler_angles(0.0, 0.0, math.radians(90.0)),
    "inverted": Quaternion.from_euler_angles(math.radians(180.0), 0.0, 0.0),
    "face_inward": Quaternion.from_euler_angles(0.0, math.radians(180.0), 0.0)
}