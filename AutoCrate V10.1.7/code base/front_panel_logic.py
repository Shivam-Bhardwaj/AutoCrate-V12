"""
Front Panel Logic Module

Calculates dimensions for front panel components including plywood sheathing,
edge cleats, and intermediate cleats. This is the legacy module maintained
for backward compatibility. New code should use front_panel_logic_unified.py.

All variable names are preserved for NX expressions compatibility.
"""

import math
from typing import Dict, List

TARGET_INTERMEDIATE_CLEAT_SPACING = 24.0  # inches C-C target

def calculate_front_panel_components(
    front_panel_assembly_width: float,
    front_panel_assembly_height: float,
    panel_sheathing_thickness: float,
    cleat_material_thickness: float,
    cleat_material_member_width: float
) -> Dict[str, float]:
    """
    Calculates the dimensions for the front panel components:
    plywood sheathing, edge horizontal cleats, edge vertical cleats,
    and intermediate vertical cleats if needed.

    Args:
        front_panel_assembly_width: Overall width of the front panel assembly.
        front_panel_assembly_height: Overall height of the front panel assembly.
        panel_sheathing_thickness: Thickness of the plywood/sheathing.
        cleat_material_thickness: Thickness of the cleat lumber.
        cleat_material_member_width: Actual face width of the cleat lumber.

    Returns:
        A dictionary containing the dimensions of the front panel components.
    """

    # 1. Plywood Board (Sheathing)
    plywood_width = front_panel_assembly_width
    plywood_height = front_panel_assembly_height
    plywood_thickness = panel_sheathing_thickness

    # 2. Horizontal Cleats (Top & Bottom) - Edge Cleats
    # These run the full width of the panel assembly.
    horizontal_cleat_length = plywood_width
    # Their "width" on the panel face is cleat_material_member_width
    # Their "thickness" off the panel face is cleat_material_thickness

    # 3. Vertical Cleats (Left & Right) - Edge Cleats
    # These fit between the Top and Bottom Horizontal Cleats.
    # Their length is the panel assembly height minus the width of the two horizontal cleats.
    vertical_cleat_length = plywood_height - (2 * cleat_material_member_width)
    # Their "width" on the panel face is cleat_material_member_width
    # Their "thickness" off the panel face is cleat_material_thickness
    
    # Ensure cleat lengths are not negative
    if vertical_cleat_length < 0:
        vertical_cleat_length = 0
    
    # 4. Intermediate Vertical Cleats
    intermediate_vertical_cleats_data = {
        'count': 0,
        'length': 0,
        'material_thickness': cleat_material_thickness,
        'material_member_width': cleat_material_member_width,
        'positions_x_centerline': [],
        'orientation': "None"
    }

    # Calculate C-C distance of edge vertical cleats
    # Edge vertical cleats are at the extremities of the plywood_width
    edge_vertical_cleats_cc_width = plywood_width - cleat_material_member_width

    if edge_vertical_cleats_cc_width > TARGET_INTERMEDIATE_CLEAT_SPACING and plywood_width > (2 * cleat_material_member_width):
        intermediate_vertical_cleats_data['orientation'] = "Vertical"
        
        # For symmetric spacing, find the MINIMUM number of cleats needed to keep spacing ≤ 24"
        min_segments_needed = math.ceil(edge_vertical_cleats_cc_width / TARGET_INTERMEDIATE_CLEAT_SPACING)
        intermediate_cleat_count = max(0, min_segments_needed - 1)

        if intermediate_cleat_count > 0:
            intermediate_vertical_cleats_data['count'] = intermediate_cleat_count
            intermediate_vertical_cleats_data['length'] = vertical_cleat_length # Same length as edge vertical cleats

            # For TRUE symmetry, we need to calculate equal gaps between ALL elements
            num_cc_segments = intermediate_cleat_count + 1
            
            # Calculate the uniform center-to-center spacing required for symmetry
            actual_cc_spacing = edge_vertical_cleats_cc_width / num_cc_segments
            
            positions = []
            for i in range(intermediate_cleat_count):
                # k is the index of the intermediate cleat (1-based for calculation clarity)
                k_intermediate = i + 1 
                # Position of the centerline of the (k_intermediate)-th intermediate cleat
                centerline_pos = (cleat_material_member_width / 2.0) + (k_intermediate * actual_cc_spacing)
                positions.append(round(centerline_pos, 4))
            intermediate_vertical_cleats_data['positions_x_centerline'] = positions

    # 5. Intermediate Horizontal Cleats (sections between vertical cleats)
    intermediate_horizontal_cleats_data = {
        'count': 0,
        'sections': [],  # List of cleat sections with position and width data
        'material_thickness': cleat_material_thickness,
        'material_member_width': cleat_material_member_width,
        'orientation': "None"
    }

    # Calculate horizontal splice positions based on plywood layout
    horizontal_splice_positions = calculate_horizontal_splice_positions(
        front_panel_assembly_width, 
        front_panel_assembly_height
    )

    if horizontal_splice_positions:
        # Check and adjust splice position to avoid overlap with edge cleats
        adjusted_splice_y = check_and_adjust_splice_position(
            horizontal_splice_positions[0],  # Use first splice position
            front_panel_assembly_height,
            cleat_material_member_width
        )
        
        # Calculate horizontal cleat sections between vertical cleats
        cleat_sections = calculate_horizontal_cleat_sections(
            front_panel_assembly_width,
            cleat_material_member_width,
            intermediate_vertical_cleats_data,
            adjusted_splice_y  # Use adjusted Y position
        )
        
        # Calculate pattern count based on number of horizontal splices
        # Count: 1 if only 1 splice, 2 if more than 1 splice
        horizontal_splice_count = len(horizontal_splice_positions)
        pattern_count = 1 if horizontal_splice_count == 1 else (2 if horizontal_splice_count > 1 else 1)
        
        intermediate_horizontal_cleats_data['orientation'] = "Horizontal"
        intermediate_horizontal_cleats_data['count'] = len(cleat_sections)
        intermediate_horizontal_cleats_data['sections'] = cleat_sections
        intermediate_horizontal_cleats_data['horizontal_splice_count'] = horizontal_splice_count
        intermediate_horizontal_cleats_data['pattern_count'] = pattern_count

    components = {
        'plywood': {
            'width': plywood_width,
            'height': plywood_height,
            'thickness': plywood_thickness
        },
        'horizontal_cleats': { # Edge cleats
            'length': horizontal_cleat_length,
            'material_thickness': cleat_material_thickness,
            'material_member_width': cleat_material_member_width,
            'count': 2
        },
        'vertical_cleats': { # Edge cleats
            'length': vertical_cleat_length,
            'material_thickness': cleat_material_thickness,
            'material_member_width': cleat_material_member_width,
            'count': 2
        },
        'intermediate_vertical_cleats': intermediate_vertical_cleats_data,
        'intermediate_horizontal_cleats': intermediate_horizontal_cleats_data  # Add horizontal cleats
    }
    return components


def calculate_horizontal_splice_positions(panel_width: float, panel_height: float) -> list:
    """
    Calculate the Y-positions where horizontal splices occur in the plywood layout.
    
    Args:
        panel_width: Width of the panel in inches
        panel_height: Height of the panel in inches
        
    Returns:
        List of Y-coordinates where horizontal cleats should be placed (centerline positions)
    """
    # Constants for plywood dimensions
    MAX_PLYWOOD_WIDTH = 96  # inches
    MAX_PLYWOOD_HEIGHT = 48  # inches
    
    # Determine how many sheets needed in each direction
    sheets_across = math.ceil(panel_width / MAX_PLYWOOD_WIDTH)
    sheets_down = math.ceil(panel_height / MAX_PLYWOOD_HEIGHT)
    
    # Try vertical arrangement (rotate sheets 90 degrees)
    rotated_sheets_across = math.ceil(panel_width / MAX_PLYWOOD_HEIGHT)
    rotated_sheets_down = math.ceil(panel_height / MAX_PLYWOOD_WIDTH)
    
    # Calculate total sheets needed for each arrangement
    horizontal_priority_count = sheets_across * sheets_down
    vertical_priority_count = rotated_sheets_across * rotated_sheets_down
    
    splice_positions = []
    
    # IMPROVED DECISION LOGIC with tie-breaking
    use_rotated = False
    
    if vertical_priority_count < horizontal_priority_count:
        # Rotated is clearly better (fewer sheets)
        use_rotated = True
    elif vertical_priority_count > horizontal_priority_count:
        # Standard is clearly better (fewer sheets)
        use_rotated = False
    else:
        # TIE-BREAKING LOGIC for equal sheet counts
        # Calculate splice counts for each arrangement
        standard_h_splices = max(0, sheets_down - 1)
        rotated_h_splices = max(0, rotated_sheets_down - 1)
        
        # Prefer fewer horizontal splices (they're harder to support structurally)
        if rotated_h_splices < standard_h_splices:
            use_rotated = True
        elif standard_h_splices < rotated_h_splices:
            use_rotated = False
        else:
            # Still tied - use aspect ratio criteria
            # Calculate panel aspect ratio
            panel_aspect_ratio = panel_width / panel_height
            
            # Calculate grid aspect ratios
            standard_grid_aspect = sheets_across / sheets_down
            rotated_grid_aspect = rotated_sheets_across / rotated_sheets_down
            
            # Calculate how close each grid aspect is to the panel aspect
            standard_aspect_diff = abs(standard_grid_aspect - panel_aspect_ratio)
            rotated_aspect_diff = abs(rotated_grid_aspect - panel_aspect_ratio)
            
            # Prefer the arrangement that better matches the panel's aspect ratio
            if rotated_aspect_diff < standard_aspect_diff:
                use_rotated = True
            elif standard_aspect_diff < rotated_aspect_diff:
                use_rotated = False
            else:
                # Final tie-breaker: prefer more square arrangement
                if rotated_grid_aspect > standard_grid_aspect:
                    use_rotated = True
                else:
                    use_rotated = False
    
    # Execute the chosen arrangement
    if use_rotated:
        # Use vertical arrangement (rotated sheets) - MAX_PLYWOOD_WIDTH becomes height
        if rotated_sheets_down > 1:
            # Calculate remainder height for splice positioning
            total_full_rows = rotated_sheets_down - 1
            remainder_height = panel_height - (total_full_rows * MAX_PLYWOOD_WIDTH)
            
            # Bottom row uses remainder height, upper rows use full sheet height
            current_y = remainder_height  # First splice at top of bottom row
            
            # Add splice positions between rows
            for row in range(1, rotated_sheets_down):
                splice_positions.append(current_y)
                if row < rotated_sheets_down - 1:  # Not the last row
                    current_y += MAX_PLYWOOD_WIDTH
    else:
        # Use horizontal arrangement (standard orientation)
        if sheets_down > 1:
            # Calculate remainder height for splice positioning
            total_full_rows = sheets_down - 1
            remainder_height = panel_height - (total_full_rows * MAX_PLYWOOD_HEIGHT)
            
            # Bottom row uses remainder height, upper rows use full sheet height
            current_y = remainder_height  # First splice at top of bottom row
            
            # Add splice positions between rows
            for row in range(1, sheets_down):
                splice_positions.append(current_y)
                if row < sheets_down - 1:  # Not the last row
                    current_y += MAX_PLYWOOD_HEIGHT
    
    return splice_positions


def calculate_required_panel_height_for_splice_coverage(
    original_panel_height: float, 
    splice_positions: list, 
    cleat_member_width: float,
    adjustment_increment: float = 0.25
) -> float:
    """
    Calculate the minimum panel height needed to ensure the first splice is covered by the bottom edge cleat.
    Only the first (lowest) splice needs to be covered by extending the bottom cleat.
    Higher splices can be covered by intermediate cleats.
    
    Args:
        original_panel_height: Original panel height
        splice_positions: List of splice Y positions that need coverage
        cleat_member_width: Width of cleat member (3.5")
        adjustment_increment: Increment for height adjustments (0.25")
        
    Returns:
        Adjusted panel height that ensures the first splice is covered by bottom cleat
    """
    if not splice_positions:
        return original_panel_height
    
    # Sort splice positions to get the lowest one
    sorted_splices = sorted(splice_positions)
    first_splice_y = sorted_splices[0]
    
    # Calculate bottom cleat coverage
    bottom_cleat_top = cleat_member_width
    
    # Check if first splice is already covered by bottom cleat
    if first_splice_y <= bottom_cleat_top:
        return original_panel_height  # No adjustment needed
    
    # Calculate minimum height adjustment needed
    gap = first_splice_y - bottom_cleat_top
    height_adjustment = gap + adjustment_increment
    
    # Return adjusted height
    adjusted_height = original_panel_height + height_adjustment
    return adjusted_height


def check_and_adjust_splice_position(splice_y_position: float, panel_height: float, cleat_member_width: float) -> float:
    """
    DEPRECATED: Check if horizontal cleat at splice position would overlap with edge cleats and adjust if needed.
    This function is now deprecated in favor of dimension adjustment approach.
    
    Args:
        splice_y_position: Original splice Y position
        panel_height: Total panel height
        cleat_member_width: Width of cleat member (3.5")
        
    Returns:
        Adjusted splice Y position that avoids overlap
    """
    # Calculate where intermediate cleat would be placed
    cleat_bottom = splice_y_position - (cleat_member_width / 2.0)
    cleat_top = splice_y_position + (cleat_member_width / 2.0)
    
    # Bottom edge cleat occupies: Y = 0 to cleat_member_width
    # Top edge cleat occupies: Y = (panel_height - cleat_member_width) to panel_height
    
    # Check overlap with bottom edge cleat
    if cleat_bottom < cleat_member_width:
        # Adjust splice position to clear bottom edge cleat
        adjusted_splice_y = cleat_member_width + (cleat_member_width / 2.0)
        return adjusted_splice_y
    
    # Check overlap with top edge cleat
    top_cleat_start = panel_height - cleat_member_width
    if cleat_top > top_cleat_start:
        # Adjust splice position to clear top edge cleat
        adjusted_splice_y = top_cleat_start - (cleat_member_width / 2.0)
        return adjusted_splice_y
    
    # No overlap, return original position
    return splice_y_position


def calculate_horizontal_cleat_sections(
    panel_width: float,
    cleat_member_width: float,
    vertical_cleats_data: dict,
    splice_y_position: float,
    min_cleat_width: float = 0.25
) -> list:
    """
    Calculate horizontal cleat sections that fit between vertical cleats.
    Each section has a different width based on the actual gap between adjacent vertical cleats.
    FIXED: Now checks for overlap with edge cleats and adjusts position accordingly.
    
    Args:
        panel_width: Width of the panel in inches
        cleat_member_width: Width of cleat member (3.5")
        vertical_cleats_data: Data about vertical cleats and their positions
        splice_y_position: Y position where horizontal splice occurs
        min_cleat_width: Minimum cleat section width (default 0.25")
        
    Returns:
        List of cleat section dictionaries with x_pos, width, y_pos data
    """
    sections = []
    
    # Get vertical cleat positions (edge cleats + intermediate cleats)
    vertical_positions = []
    
    # Add edge vertical cleats (left and right)
    # Left edge cleat centerline at cleat_member_width/2 from left edge
    vertical_positions.append(cleat_member_width / 2.0)
    
    # Add intermediate vertical cleats if any
    intermediate_positions = vertical_cleats_data.get('positions_x_centerline', [])
    vertical_positions.extend(intermediate_positions)
    
    # Right edge cleat centerline at (panel_width - cleat_member_width/2)
    vertical_positions.append(panel_width - (cleat_member_width / 2.0))
    
    # Sort positions to ensure proper order
    vertical_positions.sort()
    
    # Calculate sections between adjacent vertical cleats
    for i in range(len(vertical_positions) - 1):
        left_cleat_center = vertical_positions[i]
        right_cleat_center = vertical_positions[i + 1]
        
        # Calculate the gap between cleats
        # Left edge of section = right edge of left cleat
        section_left_edge = left_cleat_center + (cleat_member_width / 2.0)
        # Right edge of section = left edge of right cleat  
        section_right_edge = right_cleat_center - (cleat_member_width / 2.0)
        
        # Calculate section width
        section_width = section_right_edge - section_left_edge
        
        # Only add section if it meets minimum width requirement
        if section_width >= min_cleat_width:
            sections.append({
                'x_pos': section_left_edge,  # Left edge position
                'width': section_width,
                'y_pos_centerline': splice_y_position,
                'y_pos_bottom_edge': splice_y_position - (cleat_member_width / 2.0)
            })
    
    return sections

if __name__ == '__main__':
    # Example usage for testing
    test_fp_width = 60.0  # inches
    test_fp_height = 40.0 # inches
    test_sheathing_thick = 0.75 # inches
    test_cleat_thick = 1.5 # inches
    test_cleat_member_width = 3.5 # inches

    print(f"--- Test Case 1: Width={test_fp_width}, Height={test_fp_height} ---")
    front_panel_data = calculate_front_panel_components(
        test_fp_width, 
        test_fp_height, 
        test_sheathing_thick, 
        test_cleat_thick, 
        test_cleat_member_width
    )
    import json
    print(json.dumps(front_panel_data, indent=4))
    # Expected: edge_cc = 60-3.5 = 56.5 > 24.
    # num_cc_segments = ceil(56.5 / 24) = ceil(2.35) = 3.
    # num_total_vertical_cleats = 3 + 1 = 4.
    # intermediate_cleat_count = 4 - 2 = 2.
    # actual_cc_spacing = 56.5 / 3 = 18.8333
    # Pos1_center = (3.5/2) + 1*18.8333 = 1.75 + 18.8333 = 20.5833
    # Pos2_center = (3.5/2) + 2*18.8333 = 1.75 + 37.6666 = 39.4166

    print(f"\n--- Test Case 2: Width=30.0, Height={test_fp_height} ---")
    front_panel_data_2 = calculate_front_panel_components(
        30.0, 
        test_fp_height, 
        test_sheathing_thick, 
        test_cleat_thick, 
        test_cleat_member_width
    )
    print(json.dumps(front_panel_data_2, indent=4))
    # Expected: edge_cc = 30-3.5 = 26.5 > 24.
    # num_cc_segments = ceil(26.5 / 24) = ceil(1.10) = 2.
    # num_total_vertical_cleats = 2 + 1 = 3.
    # intermediate_cleat_count = 3 - 2 = 1.
    # actual_cc_spacing = 26.5 / 2 = 13.25
    # Pos1_center = (3.5/2) + 1*13.25 = 1.75 + 13.25 = 15.0

    print(f"\n--- Test Case 3: Width=24.0, Height={test_fp_height} (Edge case, edge_cc <= 24) ---")
    # Plywood width = 24. Cleat width = 3.5. Edge C-C = 24 - 3.5 = 20.5. Should be NO intermediate.
    front_panel_data_3 = calculate_front_panel_components(
        24.0, 
        test_fp_height, 
        test_sheathing_thick, 
        test_cleat_thick, 
        test_cleat_member_width
    )
    print(json.dumps(front_panel_data_3, indent=4))
    # Expected: intermediate_cleat_count = 0

    print(f"\n--- Test Case 4: Width=27.0, Height={test_fp_height} (Edge case, edge_cc slightly > 24) ---")
    # Plywood width = 27. Cleat width = 3.5. Edge C-C = 27 - 3.5 = 23.5. Should be NO intermediate.
    # My condition is edge_vertical_cleats_cc_width > TARGET_INTERMEDIATE_CLEAT_SPACING
    # 23.5 is NOT > 24. So, 0 intermediate. Correct.
    front_panel_data_4 = calculate_front_panel_components(
        27.0, 
        test_fp_height, 
        test_sheathing_thick, 
        test_cleat_thick, 
        test_cleat_member_width
    )
    print(json.dumps(front_panel_data_4, indent=4))

    print(f"\n--- Test Case 5: Width=27.5 + 3.5 = 31, Height={test_fp_height} (Edge case, edge_cc slightly > 24) ---")
    # Plywood width = 31. Cleat width = 3.5. Edge C-C = 31 - 3.5 = 27.5. > 24.
    # num_cc_segments = ceil(27.5 / 24) = ceil(1.14) = 2.
    # num_total_vertical_cleats = 3.
    # intermediate_cleat_count = 1.
    front_panel_data_5 = calculate_front_panel_components(
        31.0,
        test_fp_height,
        test_sheathing_thick,
        test_cleat_thick,
        test_cleat_member_width
    )
    print(json.dumps(front_panel_data_5, indent=4))