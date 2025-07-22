import math

TARGET_INTERMEDIATE_CLEAT_SPACING = 24.0  # inches C-C target for cleats
MAX_INTERMEDIATE_CLEATS = 7               # matches the hard-coded instances available in NX

MAX_INTERMEDIATE_HORIZONTAL_CLEATS = 6  # Maximum number of horizontal cleat instances

# Import horizontal cleat functions from front panel logic
from front_panel_logic import (
    calculate_horizontal_splice_positions,
    calculate_horizontal_cleat_sections
)

def calculate_vertical_splice_positions(panel_width: float, panel_length: float) -> list:
    """
    Calculate the X-positions where vertical splices occur in the plywood layout.
    
    Args:
        panel_width: Width of the panel in inches
        panel_length: Length of the panel in inches
        
    Returns:
        List of X-coordinates where vertical cleats should be placed (centerline positions)
    """
    # Constants for plywood dimensions
    MAX_PLYWOOD_WIDTH = 96  # inches
    MAX_PLYWOOD_HEIGHT = 48  # inches
    
    # Determine how many sheets needed in each direction
    sheets_across = math.ceil(panel_width / MAX_PLYWOOD_WIDTH)
    sheets_down = math.ceil(panel_length / MAX_PLYWOOD_HEIGHT)
    
    # Try vertical arrangement (rotate sheets 90 degrees)
    rotated_sheets_across = math.ceil(panel_width / MAX_PLYWOOD_HEIGHT)
    rotated_sheets_down = math.ceil(panel_length / MAX_PLYWOOD_WIDTH)
    
    # Calculate total sheets needed for each arrangement
    horizontal_priority_count = sheets_across * sheets_down
    vertical_priority_count = rotated_sheets_across * rotated_sheets_down
    
    splice_positions = []
    
    # Use same decision logic as horizontal splices but for vertical direction
    use_rotated = False
    
    if vertical_priority_count < horizontal_priority_count:
        use_rotated = True
    elif vertical_priority_count > horizontal_priority_count:
        use_rotated = False
    else:
        # Tie-breaking logic
        standard_v_splices = max(0, sheets_across - 1)
        rotated_v_splices = max(0, rotated_sheets_across - 1)
        
        if rotated_v_splices < standard_v_splices:
            use_rotated = True
        elif standard_v_splices < rotated_v_splices:
            use_rotated = False
        else:
            # Still tied - prefer standard orientation
            use_rotated = False
    
    # Calculate vertical splice positions
    if use_rotated:
        # Using rotated sheets (48" wide)
        if rotated_sheets_across > 1:
            for sheet in range(1, rotated_sheets_across):
                splice_x = sheet * MAX_PLYWOOD_HEIGHT
                if splice_x < panel_width:
                    splice_positions.append(splice_x)
    else:
        # Using standard sheets (96" wide) 
        if sheets_across > 1:
            for sheet in range(1, sheets_across):
                splice_x = sheet * MAX_PLYWOOD_WIDTH
                if splice_x < panel_width:
                    splice_positions.append(splice_x)
    
    return splice_positions

def calculate_vertical_cleat_positions_for_panel(panel_width: float, vertical_splices: list, 
                                               cleat_member_width: float) -> list:
    """
    Calculate vertical cleat positions based on splices and 24" spacing requirements.
    Ensures no overlap with edge cleats.
    """
    TARGET_SPACING = 24.0
    MIN_EDGE_CLEARANCE = cleat_member_width  # Minimum clearance from edge cleats
    
    # Calculate edge cleat positions (centerlines)
    left_edge_cleat_centerline = cleat_member_width / 2.0
    right_edge_cleat_centerline = panel_width - (cleat_member_width / 2.0)
    
    # Available width for intermediate cleats (between edge cleats)
    available_width = right_edge_cleat_centerline - left_edge_cleat_centerline
    
    cleat_positions = []
    
    # Add cleats at ALL vertical splice positions - structural integrity is mandatory
    for splice_x in vertical_splices:
        # Only exclude if splice would be exactly on an edge cleat centerline
        if (abs(splice_x - left_edge_cleat_centerline) > 0.1 and 
            abs(splice_x - right_edge_cleat_centerline) > 0.1):
            cleat_positions.append(splice_x)
    
    # Sort splice-based cleat positions
    cleat_positions.sort()
    
    # Fill gaps larger than TARGET_SPACING with additional intermediate cleats
    final_positions = []
    last_pos = left_edge_cleat_centerline
    
    for cleat_pos in cleat_positions:
        # Fill gap before this cleat if needed
        gap = cleat_pos - last_pos
        while gap > TARGET_SPACING:
            new_cleat_pos = last_pos + TARGET_SPACING
            # Ensure new cleat doesn't conflict with edge cleats
            if (new_cleat_pos - left_edge_cleat_centerline >= MIN_EDGE_CLEARANCE and 
                right_edge_cleat_centerline - new_cleat_pos >= MIN_EDGE_CLEARANCE):
                final_positions.append(new_cleat_pos)
            last_pos = new_cleat_pos
            gap = cleat_pos - last_pos
        
        final_positions.append(cleat_pos)
        last_pos = cleat_pos
    
    # Fill remaining gap to right edge if needed
    gap = right_edge_cleat_centerline - last_pos
    while gap > TARGET_SPACING:
        new_cleat_pos = last_pos + TARGET_SPACING
        # Ensure new cleat doesn't conflict with right edge cleat
        if right_edge_cleat_centerline - new_cleat_pos >= MIN_EDGE_CLEARANCE:
            final_positions.append(new_cleat_pos)
            last_pos = new_cleat_pos
            gap = right_edge_cleat_centerline - last_pos
        else:
            break  # Can't fit more cleats
    
    return final_positions

def calculate_top_panel_components(
    top_panel_assembly_width: float,
    top_panel_assembly_length: float,
    panel_sheathing_thickness: float,
    cleat_material_thickness: float,
    cleat_material_member_width: float
) -> dict:
    """
    Calculates dimensions for top panel components: sheathing, primary, 
    secondary (end), and mid-span intermediate cleats.
    """
    plywood_width = top_panel_assembly_width
    plywood_length = top_panel_assembly_length
    plywood_thickness = panel_sheathing_thickness

    primary_cleat_length = top_panel_assembly_length
    
    secondary_cleat_length = top_panel_assembly_width - (2 * cleat_material_member_width)
    if secondary_cleat_length < 0:
        secondary_cleat_length = 0

    # Intermediate cleats run along Y (length), spaced along X (width)
    intermediate_cleat_length = top_panel_assembly_length - (2 * cleat_material_member_width)
    if intermediate_cleat_length < 0:
        intermediate_cleat_length = 0

    intermediate_cleats = {
        "count": 0,
        "length": intermediate_cleat_length,
        "material_thickness": cleat_material_thickness,
        "material_member_width": cleat_material_member_width,
        "positions_x_centerline": [],
        "positions_x_left_edge": [],
        "edge_to_edge_distances": [],
        "suppress_flags": [0] * MAX_INTERMEDIATE_CLEATS,
        "orientation": "Vertical",  # Cleats run along Y
    }

    # Spacing and count are based on panel width (X)
    span_cc = top_panel_assembly_width - cleat_material_member_width
    if span_cc > TARGET_INTERMEDIATE_CLEAT_SPACING and top_panel_assembly_width > (2 * cleat_material_member_width):
        # Check if vertical splices will be needed (affects cleat placement strategy)
        vertical_splice_positions_check = calculate_vertical_splice_positions(
            top_panel_assembly_width, 
            top_panel_assembly_length
        )
        
        # If no vertical splices, optimize for symmetric spacing
        if not vertical_splice_positions_check:
            # For symmetric spacing, find the MINIMUM number of cleats needed to keep spacing ≤ 24"
            # Then use symmetric positioning
            
            # Find minimum number of segments needed to keep spacing ≤ 24"
            min_segments_needed = math.ceil(span_cc / TARGET_INTERMEDIATE_CLEAT_SPACING)
            min_inter_count = max(0, min_segments_needed - 1)  # subtract 1 because segments = intermediate_count + 1
            
            # Make sure we don't exceed maximum allowed cleats
            inter_count = min(min_inter_count, MAX_INTERMEDIATE_CLEATS)
            
            if inter_count > 0:
                num_cc_segments = inter_count + 1
                
                # Calculate the uniform center-to-center spacing required for symmetry
                actual_cc = span_cc / num_cc_segments
                
                # Generate positions with truly uniform gaps
                prev_right_edge = 0.0
                for k in range(1, inter_count + 1):
                    # Position the centerline of this cleat
                    cx = (cleat_material_member_width / 2.0) + (k * actual_cc)
                    lx = cx - (cleat_material_member_width / 2.0)
                    intermediate_cleats["positions_x_centerline"].append(round(cx, 4))
                    intermediate_cleats["positions_x_left_edge"].append(round(lx, 4))
                    gap_edge_to_edge = round(lx - prev_right_edge, 4)
                    intermediate_cleats["edge_to_edge_distances"].append(gap_edge_to_edge)
                    prev_right_edge = lx + cleat_material_member_width
                intermediate_cleats["count"] = inter_count
                for i in range(MAX_INTERMEDIATE_CLEATS):
                    intermediate_cleats["suppress_flags"][i] = 1 if i < inter_count else 0
        else:
            # Use the sophisticated cleat positioning system for panels with vertical splices
            cleat_positions = calculate_vertical_cleat_positions_for_panel(
                plywood_width, 
                vertical_splice_positions_check, 
                cleat_material_member_width
            )
            
            # Limit to maximum allowed cleats
            cleat_positions = cleat_positions[:MAX_INTERMEDIATE_CLEATS]
            inter_count = len(cleat_positions)
            
            if inter_count > 0:
                prev_right_edge = 0.0  # plywood left-edge initially
                
                for cx in cleat_positions:
                    lx = cx - (cleat_material_member_width / 2.0)

                    intermediate_cleats["positions_x_centerline"].append(round(cx, 4))
                    intermediate_cleats["positions_x_left_edge"].append(round(lx, 4))

                    gap_edge_to_edge = round(lx - prev_right_edge, 4)
                    intermediate_cleats["edge_to_edge_distances"].append(gap_edge_to_edge)
                    prev_right_edge = lx + cleat_material_member_width

                intermediate_cleats["count"] = inter_count
                for i in range(inter_count):
                    intermediate_cleats["suppress_flags"][i] = 1  # mark as active

    # Calculate intermediate horizontal cleats (at plywood splice positions)
    intermediate_horizontal_cleats = {
        "count": 0,
        "material_thickness": cleat_material_thickness,
        "material_member_width": cleat_material_member_width,
        "orientation": "None",
        "instances": [],
        "suppress_flags": [0] * MAX_INTERMEDIATE_HORIZONTAL_CLEATS
    }

    # Calculate horizontal splice positions based on plywood layout
    horizontal_splice_positions = calculate_horizontal_splice_positions(
        top_panel_assembly_width, 
        top_panel_assembly_length
    )

    if horizontal_splice_positions:
        # Calculate horizontal splice count and pattern count
        horizontal_splice_count = len(horizontal_splice_positions)
        pattern_count = 1 if horizontal_splice_count == 1 else (2 if horizontal_splice_count > 1 else 1)
        
        # Use the first splice position (there should typically be one for horizontal splices)
        splice_y_position = horizontal_splice_positions[0]
        
        # Create compatible vertical cleats data structure for horizontal cleat calculation
        vertical_cleats_data_compatible = {
            "count": intermediate_cleats["count"],
            "positions_x_centerline": intermediate_cleats["positions_x_centerline"]
        }
        
        # Calculate horizontal cleat sections between vertical cleats at splice position
        cleat_sections = calculate_horizontal_cleat_sections(
            panel_width=top_panel_assembly_width,
            cleat_member_width=cleat_material_member_width,
            vertical_cleats_data=vertical_cleats_data_compatible,
            splice_y_position=splice_y_position
        )
        
        if cleat_sections:
            # Create 6 fixed instances, suppressing unused ones
            instances = []
            for i in range(MAX_INTERMEDIATE_HORIZONTAL_CLEATS):
                if i < len(cleat_sections):
                    # Use actual cleat section data
                    section = cleat_sections[i]
                    instance = {
                        "suppress_flag": 1,
                        "height": cleat_material_member_width,
                        "width": section["width"],
                        "length": cleat_material_thickness,
                        "x_pos": section["x_pos"],
                        "y_pos": section["y_pos_bottom_edge"],
                        "y_pos_centerline": section["y_pos_centerline"]
                    }
                    intermediate_horizontal_cleats["suppress_flags"][i] = 1
                else:
                    # Create suppressed instance with small but valid dimensions
                    instance = {
                        "suppress_flag": 0,
                        "height": cleat_material_member_width,
                        "width": 0.25,
                        "length": cleat_material_thickness,
                        "x_pos": 0.25,
                        "y_pos": 0.25,
                        "y_pos_centerline": 0.375
                    }
                    intermediate_horizontal_cleats["suppress_flags"][i] = 0
                
                instances.append(instance)
            
            intermediate_horizontal_cleats["count"] = len(cleat_sections)
            intermediate_horizontal_cleats["instances"] = instances
            intermediate_horizontal_cleats["orientation"] = "Horizontal"
            intermediate_horizontal_cleats["horizontal_splice_count"] = horizontal_splice_count
            intermediate_horizontal_cleats["pattern_count"] = pattern_count

    components = {
        'plywood': {
            'width': plywood_width,
            'length': plywood_length,
            'thickness': plywood_thickness
        },
        'primary_cleats': {
            'length': primary_cleat_length,
            'material_thickness': cleat_material_thickness,
            'material_member_width': cleat_material_member_width,
            'count': 2
        },
        'secondary_cleats': {
            'length': secondary_cleat_length,
            'material_thickness': cleat_material_thickness,
            'material_member_width': cleat_material_member_width,
            'count': 2 # The two end cleats
        },
        'intermediate_cleats': intermediate_cleats,
        'intermediate_horizontal_cleats': intermediate_horizontal_cleats
    }
    return components

if __name__ == '__main__':
    # Example usage for testing
    test_tp_width = 48.0
    test_tp_length = 120.0
    test_sheathing_thick = 0.75
    test_cleat_thick = 1.5
    test_cleat_member_width = 3.5

    top_panel_data = calculate_top_panel_components(
        test_tp_width,
        test_tp_length,
        test_sheathing_thick,
        test_cleat_thick,
        test_cleat_member_width
    )
    print("Top Panel Components Data:")
    import json
    print(json.dumps(top_panel_data, indent=4))

    # Test case where secondary cleats might be problematic
    test_tp_width_small = 5.0
    top_panel_data_small = calculate_top_panel_components(
        test_tp_width_small,
        test_tp_length,
        test_sheathing_thick,
        test_cleat_thick,
        test_cleat_member_width
    )
    print("\nTop Panel Components Data (Small Width):")
    print(json.dumps(top_panel_data_small, indent=4))