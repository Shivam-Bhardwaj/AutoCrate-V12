"""
Module for calculating the placement of Klimp fasteners on all sides of AutoCrate.

Places klimps on top, left, and right panels at 16-24 inch intervals for structural strength,
while avoiding interference with cleats.

Klimp numbering:
- KL_1 to KL_10: Top panel (rotation = 0°)
- KL_11 to KL_20: Left panel (rotation = -90°)
- KL_21 to KL_30: Right panel (rotation = +90°)
"""
from typing import List, Dict, Any, Optional, Tuple
import math

def calculate_all_klimp_placements(
    panel_width: float = 48.0,  # Front/back panel width
    panel_length: float = 48.0,  # Left/right panel length (depth of crate)
    panel_height: float = 48.0,  # Height of side panels
    cleat_member_width: float = 3.5,
    cleat_thickness: float = 2.0,
    panel_thickness: float = 0.25,
    intermediate_vertical_cleats: List[float] = None,
    horizontal_splice_positions: List[float] = None
) -> Dict[str, Any]:
    """
    Calculates klimp positions on all three sides (top, left, right).
    
    Coordinate system (from center of crate):
    - X-axis: left(-) to right(+) from center plane
    - Y-axis: front(-) to back(+) from center plane  
    - Z-axis: bottom(0) to top(+) from ground
    
    Args:
        panel_width: Width of front/back panels (X direction)
        panel_length: Length of left/right panels (Y direction)
        panel_height: Height of side panels (Z direction)
        cleat_member_width: Width of cleat members
        cleat_thickness: Thickness of cleats
        panel_thickness: Thickness of plywood panels
        intermediate_vertical_cleats: Positions of intermediate vertical cleats on front/back
        horizontal_splice_positions: Z positions of horizontal splices on side panels
    
    Returns:
        Dictionary with klimp definitions for all three sides
    """
    # Constants for structural requirements
    MIN_SPACING_FROM_CLEAT = 0.25  # Minimum gap from cleat edge
    MIN_KLIMP_SPACING = 16.0  # Minimum spacing between klimps
    MAX_KLIMP_SPACING = 24.0  # Maximum spacing between klimps
    TARGET_KLIMP_SPACING = 20.0  # Target optimal spacing
    KLIMP_WIDTH = 1.0  # Approximate width of klimp fastener
    
    result = {
        "top_klimps": [],
        "left_klimps": [],
        "right_klimps": []
    }
    
    # ========== TOP PANEL KLIMPS (KL_1 to KL_10) ==========
    top_klimps = calculate_top_klimps(
        panel_width, cleat_member_width, intermediate_vertical_cleats,
        MIN_SPACING_FROM_CLEAT, MIN_KLIMP_SPACING, MAX_KLIMP_SPACING,
        TARGET_KLIMP_SPACING, KLIMP_WIDTH
    )
    result["top_klimps"] = top_klimps[:10]  # Limit to 10
    
    # ========== LEFT PANEL KLIMPS (KL_11 to KL_20) ==========
    left_klimps = calculate_side_klimps(
        panel_length, panel_height, cleat_member_width, 
        horizontal_splice_positions, "left",
        MIN_SPACING_FROM_CLEAT, MIN_KLIMP_SPACING, MAX_KLIMP_SPACING,
        TARGET_KLIMP_SPACING, KLIMP_WIDTH
    )
    result["left_klimps"] = left_klimps[:10]  # Limit to 10
    
    # ========== RIGHT PANEL KLIMPS (KL_21 to KL_30) ==========
    right_klimps = calculate_side_klimps(
        panel_length, panel_height, cleat_member_width,
        horizontal_splice_positions, "right",
        MIN_SPACING_FROM_CLEAT, MIN_KLIMP_SPACING, MAX_KLIMP_SPACING,
        TARGET_KLIMP_SPACING, KLIMP_WIDTH
    )
    result["right_klimps"] = right_klimps[:10]  # Limit to 10
    
    return result


def calculate_top_klimps(
    panel_width: float,
    cleat_member_width: float,
    intermediate_vertical_cleats: List[float],
    MIN_SPACING_FROM_CLEAT: float,
    MIN_KLIMP_SPACING: float,
    MAX_KLIMP_SPACING: float,
    TARGET_KLIMP_SPACING: float,
    KLIMP_WIDTH: float
) -> List[Dict[str, Any]]:
    """Calculate klimp positions for top panel."""
    
    CLEAT_HALF_WIDTH = cleat_member_width / 2.0
    klimps = []
    
    # Build list of all vertical cleat positions
    cleat_zones = []
    
    # Left edge cleat
    left_cleat_centerline = CLEAT_HALF_WIDTH
    cleat_zones.append({
        'left': left_cleat_centerline - CLEAT_HALF_WIDTH,
        'right': left_cleat_centerline + CLEAT_HALF_WIDTH,
        'center': left_cleat_centerline
    })
    
    # Intermediate cleats
    if intermediate_vertical_cleats:
        for cleat_pos in intermediate_vertical_cleats:
            cleat_zones.append({
                'left': cleat_pos - CLEAT_HALF_WIDTH,
                'right': cleat_pos + CLEAT_HALF_WIDTH,
                'center': cleat_pos
            })
    
    # Right edge cleat
    right_cleat_centerline = panel_width - CLEAT_HALF_WIDTH
    cleat_zones.append({
        'left': right_cleat_centerline - CLEAT_HALF_WIDTH,
        'right': right_cleat_centerline + CLEAT_HALF_WIDTH,
        'center': right_cleat_centerline
    })
    
    # Sort cleat zones by position
    cleat_zones.sort(key=lambda x: x['center'])
    
    # Calculate available zones for klimp placement
    available_zones = []
    for i in range(len(cleat_zones) - 1):
        zone_start = cleat_zones[i]['right'] + MIN_SPACING_FROM_CLEAT
        zone_end = cleat_zones[i + 1]['left'] - MIN_SPACING_FROM_CLEAT
        
        if zone_end - zone_start >= KLIMP_WIDTH:
            available_zones.append({
                'start': zone_start,
                'end': zone_end,
                'width': zone_end - zone_start
            })
    
    # Place klimps in each available zone
    for zone in available_zones:
        zone_klimps = place_klimps_in_zone(
            zone, MIN_KLIMP_SPACING, MAX_KLIMP_SPACING,
            TARGET_KLIMP_SPACING, KLIMP_WIDTH
        )
        for klimp_pos in zone_klimps:
            klimps.append({
                "position_x": klimp_pos,  # Position along width
                "position_y": 0,  # Centered on top panel
                "rotation": 0  # No rotation for top klimps
            })
    
    return klimps


def calculate_side_klimps(
    panel_length: float,
    panel_height: float,
    cleat_member_width: float,
    horizontal_splice_positions: List[float],
    side: str,
    MIN_SPACING_FROM_CLEAT: float,
    MIN_KLIMP_SPACING: float,
    MAX_KLIMP_SPACING: float,
    TARGET_KLIMP_SPACING: float,
    KLIMP_WIDTH: float
) -> List[Dict[str, Any]]:
    """Calculate klimp positions for left or right side panel."""
    
    klimps = []
    rotation = -90 if side == "left" else 90
    
    # For side panels, we place klimps vertically
    # avoiding horizontal cleats at splice positions
    
    # Build list of horizontal cleat zones
    cleat_zones = []
    
    # Bottom edge (always has support structure)
    cleat_zones.append({
        'bottom': 0,
        'top': cleat_member_width,
        'center': cleat_member_width / 2
    })
    
    # Horizontal cleats at splice positions
    if horizontal_splice_positions:
        for splice_z in horizontal_splice_positions:
            cleat_zones.append({
                'bottom': splice_z - cleat_member_width / 2,
                'top': splice_z + cleat_member_width / 2,
                'center': splice_z
            })
    
    # Top edge (always has cleat)
    cleat_zones.append({
        'bottom': panel_height - cleat_member_width,
        'top': panel_height,
        'center': panel_height - cleat_member_width / 2
    })
    
    # Sort cleat zones by vertical position
    cleat_zones.sort(key=lambda x: x['center'])
    
    # Calculate available zones for klimp placement
    available_zones = []
    for i in range(len(cleat_zones) - 1):
        zone_start = cleat_zones[i]['top'] + MIN_SPACING_FROM_CLEAT
        zone_end = cleat_zones[i + 1]['bottom'] - MIN_SPACING_FROM_CLEAT
        
        if zone_end - zone_start >= KLIMP_WIDTH:
            available_zones.append({
                'start': zone_start,
                'end': zone_end,
                'width': zone_end - zone_start
            })
    
    # Place klimps in each available zone
    # For side panels, we also distribute along the Y-axis (front to back)
    y_positions = calculate_y_distribution(panel_length, 3)  # 3 rows along Y
    
    for zone in available_zones:
        zone_klimps = place_klimps_in_zone(
            zone, MIN_KLIMP_SPACING, MAX_KLIMP_SPACING,
            TARGET_KLIMP_SPACING, KLIMP_WIDTH
        )
        
        # For each Z position, pick a Y position
        for i, klimp_z in enumerate(zone_klimps):
            y_pos = y_positions[i % len(y_positions)]
            klimps.append({
                "position_y": y_pos,  # Position along length (front-back)
                "position_z": klimp_z,  # Vertical position
                "rotation": rotation  # -90 for left, +90 for right
            })
    
    return klimps


def place_klimps_in_zone(
    zone: Dict[str, float],
    MIN_KLIMP_SPACING: float,
    MAX_KLIMP_SPACING: float,
    TARGET_KLIMP_SPACING: float,
    KLIMP_WIDTH: float
) -> List[float]:
    """Place klimps optimally within a zone."""
    
    zone_width = zone['width']
    zone_start = zone['start']
    zone_end = zone['end']
    klimp_positions = []
    
    if zone_width < MIN_KLIMP_SPACING:
        # Zone is too small for multiple klimps, place one in center
        klimp_pos = (zone_start + zone_end) / 2.0
        klimp_positions.append(klimp_pos)
    else:
        # Calculate optimal number of klimps for this zone
        num_klimps = max(1, int(zone_width / TARGET_KLIMP_SPACING))
        
        # Adjust if spacing would be outside acceptable range
        if num_klimps > 1:
            spacing = zone_width / (num_klimps - 1)
            
            # If spacing is too large, add more klimps
            while spacing > MAX_KLIMP_SPACING and num_klimps < 10:
                num_klimps += 1
                spacing = zone_width / (num_klimps - 1) if num_klimps > 1 else zone_width
            
            # If spacing is too small, reduce klimps
            while spacing < MIN_KLIMP_SPACING and num_klimps > 1:
                num_klimps -= 1
                spacing = zone_width / (num_klimps - 1) if num_klimps > 1 else zone_width
        
        # Place klimps evenly in the zone
        if num_klimps == 1:
            klimp_pos = (zone_start + zone_end) / 2.0
            klimp_positions.append(klimp_pos)
        else:
            spacing = zone_width / (num_klimps - 1)
            for i in range(num_klimps):
                klimp_pos = zone_start + (i * spacing)
                klimp_positions.append(klimp_pos)
    
    return klimp_positions


def calculate_y_distribution(panel_length: float, num_rows: int) -> List[float]:
    """Calculate Y positions for distributing klimps along panel length."""
    
    # Place klimps at strategic positions along Y-axis
    # Avoid edges, distribute evenly
    edge_offset = 6.0  # 6 inches from front/back edges
    
    if num_rows == 1:
        return [0.0]  # Center
    elif num_rows == 2:
        return [-panel_length/4, panel_length/4]
    elif num_rows == 3:
        # Front, center, back positions
        return [
            -panel_length/2 + edge_offset,
            0.0,
            panel_length/2 - edge_offset
        ]
    else:
        # Distribute evenly
        positions = []
        spacing = (panel_length - 2*edge_offset) / (num_rows - 1)
        for i in range(num_rows):
            y = -panel_length/2 + edge_offset + (i * spacing)
            positions.append(y)
        return positions