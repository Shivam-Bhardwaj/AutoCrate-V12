"""
Module for calculating the placement of Klimp fasteners on the AutoCrate Front Panel.

Places klimps on panel edges at 16-24 inch intervals for structural strength,
while avoiding interference with vertical cleats.
"""
from typing import List, Dict, Any, Optional
import math

def calculate_klimp_placements(
    panel_width: float = 48.0,  # Default panel width
    cleat_member_width: float = 3.5,
    intermediate_cleat_positions: List[float] = None
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Calculates klimp positions on the top edge of the front panel.
    Places multiple klimps at 16-24 inch intervals for structural strength.
    
    Coordinate system:
    - X=0 is at the left edge of the front panel
    - Left edge vertical cleat centerline is at X = cleat_member_width/2
    - Right edge vertical cleat centerline is at X = panel_width - cleat_member_width/2
    - Intermediate cleats are positioned at calculated centerlines
    
    Args:
        panel_width: Width of the panel (default 48.0")
        cleat_member_width: Width of cleat members (default 3.5")
        intermediate_cleat_positions: List of intermediate cleat centerline positions
    
    Returns:
        A dictionary containing klimp definitions for top edge.
    """
    # Constants for structural requirements
    MIN_SPACING_FROM_CLEAT = 0.25  # 0.25 inches minimum gap from cleat edge
    MIN_KLIMP_SPACING = 16.0  # Minimum spacing between klimps (inches)
    MAX_KLIMP_SPACING = 24.0  # Maximum spacing between klimps (inches)
    TARGET_KLIMP_SPACING = 20.0  # Target optimal spacing (inches)
    KLIMP_WIDTH = 1.0  # Approximate width of klimp fastener
    
    CLEAT_HALF_WIDTH = cleat_member_width / 2.0
    
    klimps = []
    
    # Build list of all vertical cleat positions (edges + intermediates)
    cleat_zones = []
    
    # Left edge cleat
    left_cleat_centerline = CLEAT_HALF_WIDTH
    cleat_zones.append({
        'left': left_cleat_centerline - CLEAT_HALF_WIDTH,
        'right': left_cleat_centerline + CLEAT_HALF_WIDTH,
        'center': left_cleat_centerline
    })
    
    # Intermediate cleats
    if intermediate_cleat_positions:
        for cleat_pos in intermediate_cleat_positions:
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
    
    # Calculate available zones for klimp placement (between cleats)
    available_zones = []
    for i in range(len(cleat_zones) - 1):
        zone_start = cleat_zones[i]['right'] + MIN_SPACING_FROM_CLEAT
        zone_end = cleat_zones[i + 1]['left'] - MIN_SPACING_FROM_CLEAT
        
        # Only add zone if there's enough space for at least one klimp
        if zone_end - zone_start >= KLIMP_WIDTH:
            available_zones.append({
                'start': zone_start,
                'end': zone_end,
                'width': zone_end - zone_start
            })
    
    # Place klimps in each available zone
    for zone in available_zones:
        zone_width = zone['width']
        zone_start = zone['start']
        zone_end = zone['end']
        
        # Calculate number of klimps that can fit in this zone
        if zone_width < MIN_KLIMP_SPACING:
            # Zone is too small for multiple klimps, place one in center
            klimp_x = (zone_start + zone_end) / 2.0
            klimps.append({
                "side": "top",
                "position": klimp_x,
                "angle": 0  # Horizontal orientation
            })
        else:
            # Calculate optimal number of klimps for this zone
            # Try to maintain spacing between MIN and MAX
            num_klimps = max(1, int(zone_width / TARGET_KLIMP_SPACING))
            
            # Adjust if spacing would be outside acceptable range
            if num_klimps > 1:
                spacing = zone_width / (num_klimps - 1)
                
                # If spacing is too large, add more klimps
                while spacing > MAX_KLIMP_SPACING and num_klimps < 15:
                    num_klimps += 1
                    spacing = zone_width / (num_klimps - 1) if num_klimps > 1 else zone_width
                
                # If spacing is too small, reduce klimps
                while spacing < MIN_KLIMP_SPACING and num_klimps > 1:
                    num_klimps -= 1
                    spacing = zone_width / (num_klimps - 1) if num_klimps > 1 else zone_width
            
            # Place klimps evenly in the zone
            if num_klimps == 1:
                # Single klimp in center of zone
                klimp_x = (zone_start + zone_end) / 2.0
                klimps.append({
                    "side": "top",
                    "position": klimp_x,
                    "angle": 0
                })
            else:
                # Multiple klimps evenly spaced
                spacing = zone_width / (num_klimps - 1)
                for i in range(num_klimps):
                    klimp_x = zone_start + (i * spacing)
                    klimps.append({
                        "side": "top",
                        "position": klimp_x,
                        "angle": 0
                    })
    
    # Limit to maximum allowed klimps (15 per side)
    if len(klimps) > 15:
        # Keep the most evenly distributed 15 klimps
        # Sort by position and take every nth klimp to maintain distribution
        klimps.sort(key=lambda k: k['position'])
        step = len(klimps) / 15.0
        selected_klimps = []
        for i in range(15):
            index = int(i * step)
            selected_klimps.append(klimps[index])
        klimps = selected_klimps
    
    return {"klimps": klimps}