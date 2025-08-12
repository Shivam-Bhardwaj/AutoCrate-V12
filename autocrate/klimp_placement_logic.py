"""
Module for calculating the placement of Klimp fasteners on the AutoCrate Front Panel.

Places klimps on panel edges, positioned to avoid intermediate cleats with proper clearance.
"""
from typing import List, Dict, Any, Optional

def calculate_klimp_placements(
    panel_width: float = 48.0,  # Default panel width
    cleat_member_width: float = 3.5,
    intermediate_cleat_positions: List[float] = None
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Calculates klimp position on the top edge of the front panel.
    Places a single klimp between the left edge cleat and first intermediate cleat.
    
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
    # Constants
    MIN_SPACING_FROM_CLEAT = 2.0  # 2 inches minimum from cleat edge
    CLEAT_HALF_WIDTH = cleat_member_width / 2.0
    
    klimps = []
    
    # Calculate left edge cleat position
    # The left vertical cleat's centerline is at cleat_member_width/2 from the left edge
    left_cleat_centerline = CLEAT_HALF_WIDTH
    left_cleat_right_edge = left_cleat_centerline + CLEAT_HALF_WIDTH  # Right edge of left cleat
    
    # Determine the left boundary for klimp placement (2" from left cleat)
    klimp_left_boundary = left_cleat_right_edge + MIN_SPACING_FROM_CLEAT
    
    # Determine the right boundary based on first intermediate cleat or right edge cleat
    if intermediate_cleat_positions and len(intermediate_cleat_positions) > 0:
        # First intermediate cleat exists
        first_intermediate_centerline = intermediate_cleat_positions[0]
        first_intermediate_left_edge = first_intermediate_centerline - CLEAT_HALF_WIDTH
        klimp_right_boundary = first_intermediate_left_edge - MIN_SPACING_FROM_CLEAT
    else:
        # No intermediate cleats, use right edge cleat
        right_cleat_centerline = panel_width - CLEAT_HALF_WIDTH
        right_cleat_left_edge = right_cleat_centerline - CLEAT_HALF_WIDTH
        klimp_right_boundary = right_cleat_left_edge - MIN_SPACING_FROM_CLEAT
    
    # Calculate klimp position - place it in the center of the available space
    if klimp_right_boundary > klimp_left_boundary:
        # There's enough space for a klimp
        klimp_x_position = (klimp_left_boundary + klimp_right_boundary) / 2.0
    else:
        # Not enough space, place at minimum distance from left cleat
        klimp_x_position = klimp_left_boundary
    
    # Convert to front panel coordinate system if needed
    # For now, using the position as calculated from left edge (X=0)
    
    # Top edge klimp - single placement
    klimps.append({
        "side": "top", 
        "position": klimp_x_position,
        "angle": 0  # Horizontal orientation
    })
    
    return {"klimps": klimps}