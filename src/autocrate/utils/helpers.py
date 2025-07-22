"""
Helper functions and utilities for AutoCrate.

This module contains common utility functions used throughout
the application for validation, formatting, and calculations.
"""

import math
import re
from typing import Union, List, Tuple, Optional
from .constants import TOLERANCES, ERROR_MESSAGES
from ..exceptions import ValidationError


def validate_dimensions(
    width: Union[float, int],
    height: Union[float, int],
    depth: Optional[Union[float, int]] = None,
    min_value: float = 0.1,
    max_value: float = 1000.0
) -> Tuple[float, float, Optional[float]]:
    """
    Validate and normalize dimension inputs.
    
    Args:
        width: Width dimension
        height: Height dimension  
        depth: Optional depth dimension
        min_value: Minimum allowable value
        max_value: Maximum allowable value
        
    Returns:
        Tuple of validated dimensions
        
    Raises:
        ValidationError: If dimensions are invalid
    """
    def _validate_single_dimension(value: Union[float, int], name: str) -> float:
        try:
            val = float(value)
        except (ValueError, TypeError):
            raise ValidationError(f"{name} must be a valid number")
        
        if val <= 0:
            raise ValidationError(f"{name} {ERROR_MESSAGES['invalid_dimension']}")
        
        if val < min_value:
            raise ValidationError(f"{name} {ERROR_MESSAGES['dimension_too_small']}")
            
        if val > max_value:
            raise ValidationError(f"{name} {ERROR_MESSAGES['dimension_too_large']}")
        
        return val
    
    validated_width = _validate_single_dimension(width, "Width")
    validated_height = _validate_single_dimension(height, "Height")
    validated_depth = None
    
    if depth is not None:
        validated_depth = _validate_single_dimension(depth, "Depth")
    
    return validated_width, validated_height, validated_depth


def format_dimension(value: float, precision: int = 3) -> str:
    """
    Format a dimension value for display.
    
    Args:
        value: Numeric value to format
        precision: Number of decimal places
        
    Returns:
        Formatted string representation
    """
    if abs(value) < TOLERANCES['calculation_epsilon']:
        return "0"
    
    # Remove trailing zeros and decimal point if not needed
    formatted = f"{value:.{precision}f}".rstrip('0').rstrip('.')
    
    # Handle very small numbers
    if formatted == '' or formatted == '-':
        return "0"
    
    return formatted


def calculate_lumber_count(
    total_length: float,
    lumber_length: float,
    waste_factor: float = 0.05
) -> int:
    """
    Calculate the number of lumber pieces needed.
    
    Args:
        total_length: Total length needed
        lumber_length: Length of each lumber piece
        waste_factor: Waste factor (default 5%)
        
    Returns:
        Number of lumber pieces required
    """
    if lumber_length <= 0:
        raise ValidationError("Lumber length must be positive")
    
    # Account for waste
    adjusted_length = total_length * (1 + waste_factor)
    
    # Calculate pieces needed, rounding up
    pieces_needed = math.ceil(adjusted_length / lumber_length)
    
    return max(1, pieces_needed)  # At least 1 piece


def round_to_increment(value: float, increment: float) -> float:
    """
    Round a value to the nearest increment.
    
    Args:
        value: Value to round
        increment: Increment to round to
        
    Returns:
        Rounded value
    """
    if increment <= 0:
        return value
    
    return round(value / increment) * increment


def calculate_area(width: float, height: float) -> float:
    """
    Calculate area from width and height.
    
    Args:
        width: Width dimension
        height: Height dimension
        
    Returns:
        Area in square units
    """
    return width * height


def calculate_perimeter(width: float, height: float) -> float:
    """
    Calculate perimeter from width and height.
    
    Args:
        width: Width dimension
        height: Height dimension
        
    Returns:
        Perimeter in linear units
    """
    return 2 * (width + height)


def is_within_tolerance(value1: float, value2: float, tolerance: float = None) -> bool:
    """
    Check if two values are within tolerance of each other.
    
    Args:
        value1: First value
        value2: Second value
        tolerance: Tolerance value (defaults to calculation epsilon)
        
    Returns:
        True if values are within tolerance
    """
    if tolerance is None:
        tolerance = TOLERANCES['calculation_epsilon']
    
    return abs(value1 - value2) <= tolerance


def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    Clamp a value between min and max bounds.
    
    Args:
        value: Value to clamp
        min_val: Minimum bound
        max_val: Maximum bound
        
    Returns:
        Clamped value
    """
    return max(min_val, min(max_val, value))


def parse_lumber_size_string(size_string: str) -> Optional[float]:
    """
    Parse lumber size string and extract numeric value.
    
    Args:
        size_string: String like "2x6 (5.5 in)"
        
    Returns:
        Numeric value or None if parsing fails
    """
    # Look for pattern like "(5.5 in)" or just "5.5"
    patterns = [
        r'\(([\d.]+)\s*in\)',  # "(5.5 in)"
        r'\(([\d.]+)\)',       # "(5.5)"
        r'^([\d.]+)$',         # "5.5"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, size_string)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                continue
    
    return None


def calculate_weight(
    length: float,
    width: float, 
    height: float,
    density: float
) -> float:
    """
    Calculate weight from dimensions and material density.
    
    Args:
        length: Length dimension
        width: Width dimension
        height: Height/thickness dimension
        density: Material density in appropriate units
        
    Returns:
        Weight in appropriate units
    """
    volume = length * width * height
    return volume * density


def optimize_cuts(
    required_lengths: List[float],
    stock_length: float,
    kerf_width: float = 0.125
) -> List[List[float]]:
    """
    Optimize cutting patterns to minimize waste.
    
    Args:
        required_lengths: List of required cut lengths
        stock_length: Length of stock material
        kerf_width: Width of saw cut (waste per cut)
        
    Returns:
        List of cutting patterns (each pattern is a list of lengths)
    """
    # Sort lengths in descending order for better packing
    sorted_lengths = sorted(required_lengths, reverse=True)
    
    cutting_patterns = []
    remaining_lengths = sorted_lengths.copy()
    
    while remaining_lengths:
        current_pattern = []
        current_length = 0
        
        # Try to fit pieces in current stock piece
        i = 0
        while i < len(remaining_lengths):
            piece_length = remaining_lengths[i]
            needed_length = piece_length + (kerf_width if current_pattern else 0)
            
            if current_length + needed_length <= stock_length:
                current_pattern.append(piece_length)
                current_length += needed_length
                remaining_lengths.pop(i)
            else:
                i += 1
        
        if current_pattern:
            cutting_patterns.append(current_pattern)
        else:
            # If we can't fit any remaining piece, there's an error
            break
    
    return cutting_patterns