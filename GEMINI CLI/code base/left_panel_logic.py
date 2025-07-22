import math

TARGET_INTERMEDIATE_CLEAT_SPACING = 24.0  # inches C-C target for cleats
MAX_INTERMEDIATE_CLEATS = 7               # matches the hard-coded instances available in NX

# Import horizontal cleat functions from front panel logic
from front_panel_logic import (
    calculate_horizontal_splice_positions,
    calculate_horizontal_cleat_sections
)

# Constants for plywood layout
MAX_PLYWOOD_DIMS = (96, 48)  # inches (width, height)

def calculate_plywood_layout_for_panel(panel_width: float, panel_height: float) -> list:
    """
    Calculate the optimal layout of plywood sheets for the given panel dimensions.
    
    Args:
        panel_width: Width of the panel in inches
        panel_height: Height of the panel in inches
        
    Returns:
        List of dictionaries containing position and dimensions of each plywood sheet
    """
    # Determine how many sheets needed in each direction
    sheets_across = math.ceil(panel_width / MAX_PLYWOOD_DIMS[0])
    sheets_down = math.ceil(panel_height / MAX_PLYWOOD_DIMS[1])
    
    # Calculate total sheets needed for horizontal and vertical arrangements
    horizontal_priority_count = sheets_across * sheets_down
    
    # Try vertical arrangement (rotate sheets 90 degrees)
    rotated_sheets_across = math.ceil(panel_width / MAX_PLYWOOD_DIMS[1])
    rotated_sheets_down = math.ceil(panel_height / MAX_PLYWOOD_DIMS[0])
    vertical_priority_count = rotated_sheets_across * rotated_sheets_down
    
    # Choose the arrangement with fewer sheets, preferring vertical splices if tied
    sheets = []
    
    if vertical_priority_count <= horizontal_priority_count:
        # Use vertical arrangement (rotated sheets)
        for row in range(rotated_sheets_down):
            for col in range(rotated_sheets_across):
                x_pos = col * MAX_PLYWOOD_DIMS[1]
                y_pos = row * MAX_PLYWOOD_DIMS[0]
                
                # Calculate actual sheet dimensions (may be smaller at edges)
                sheet_width = min(MAX_PLYWOOD_DIMS[1], panel_width - x_pos)
                sheet_height = min(MAX_PLYWOOD_DIMS[0], panel_height - y_pos)
                
                # Only add if the sheet has positive dimensions
                if sheet_width > 0 and sheet_height > 0:
                    sheets.append({
                        'x': x_pos,
                        'y': y_pos,
                        'width': sheet_width,
                        'height': sheet_height,
                        'rotated': True
                    })
    else:
        # Use standard arrangement
        for row in range(sheets_down):
            for col in range(sheets_across):
                x_pos = col * MAX_PLYWOOD_DIMS[0]
                y_pos = row * MAX_PLYWOOD_DIMS[1]
                
                # Calculate actual sheet dimensions (may be smaller at edges)
                sheet_width = min(MAX_PLYWOOD_DIMS[0], panel_width - x_pos)
                sheet_height = min(MAX_PLYWOOD_DIMS[1], panel_height - y_pos)
                
                # Only add if the sheet has positive dimensions
                if sheet_width > 0 and sheet_height > 0:
                    sheets.append({
                        'x': x_pos,
                        'y': y_pos,
                        'width': sheet_width,
                        'height': sheet_height,
                        'rotated': False
                    })
    
    return sheets

def extract_vertical_splice_positions_for_panel(plywood_sheets: list) -> list:
    """
    Extract vertical splice positions from plywood layout.
    Vertical splices occur where plywood sheets meet side-by-side.
    """
    splice_positions = []
    
    # Group sheets by row (same Y position)
    rows = {}
    for sheet in plywood_sheets:
        y_pos = sheet['y']
        if y_pos not in rows:
            rows[y_pos] = []
        rows[y_pos].append(sheet)
    
    # For each row, find splice positions
    for y_pos, sheets_in_row in rows.items():
        # Sort sheets by X position
        sheets_in_row.sort(key=lambda s: s['x'])
        
        # Splice occurs at the right edge of each sheet (except the last one)
        for i in range(len(sheets_in_row) - 1):
            splice_x = sheets_in_row[i]['x'] + sheets_in_row[i]['width']
            splice_positions.append(splice_x)
    
    # Remove duplicates and sort
    unique_splices = sorted(list(set(splice_positions)))
    return unique_splices

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

def calculate_vertical_splice_positions_for_panel(panel_width: float, panel_height: float) -> list:
    """
    Calculate the X-positions where vertical splices occur in the plywood layout.
    
    Args:
        panel_width: Width of the panel in inches (horizontal dimension)
        panel_height: Height of the panel in inches (vertical dimension)
        
    Returns:
        List of X-coordinates where vertical splices occur
    """
    # Constants for plywood dimensions
    MAX_PLYWOOD_WIDTH = 96  # inches
    MAX_PLYWOOD_HEIGHT = 48  # inches
    
    # For side panels, check if width needs splicing
    # Standard orientation
    sheets_across_std = math.ceil(panel_width / MAX_PLYWOOD_WIDTH)
    sheets_down_std = math.ceil(panel_height / MAX_PLYWOOD_HEIGHT)
    
    # Rotated orientation
    sheets_across_rot = math.ceil(panel_width / MAX_PLYWOOD_HEIGHT)
    sheets_down_rot = math.ceil(panel_height / MAX_PLYWOOD_WIDTH)
    
    # Calculate total sheets
    total_std = sheets_across_std * sheets_down_std
    total_rot = sheets_across_rot * sheets_down_rot
    
    splice_positions = []
    
    # Choose orientation with fewer sheets
    if total_rot < total_std:
        # Use rotated sheets
        if sheets_across_rot > 1:
            for i in range(1, sheets_across_rot):
                splice_x = i * MAX_PLYWOOD_HEIGHT
                if splice_x < panel_width:
                    splice_positions.append(splice_x)
    else:
        # Use standard sheets
        if sheets_across_std > 1:
            for i in range(1, sheets_across_std):
                splice_x = i * MAX_PLYWOOD_WIDTH
                if splice_x < panel_width:
                    splice_positions.append(splice_x)
    
    return splice_positions


def calculate_left_panel_components(
    left_panel_assembly_length: float,   # Along crate length (X direction on plywood)
    left_panel_assembly_height: float,   # Vertical height  (Y direction on plywood)
    panel_sheathing_thickness: float,
    cleat_material_thickness: float,
    cleat_material_member_width: float,
) -> dict:
    """
    Compute plywood, edge cleats and up-to-seven intermediate vertical cleats for a **left-hand** crate panel.

    Notes on geometry
    -----------------
    1. Two *horizontal* cleats (top & bottom) are sandwiched between the vertical edge cleats.
       Their thickness sticks out of the panel; their *member width* occupies space on the sheet.
    2. Two *vertical* edge cleats (front & back edges) run the full height of the plywood sheet.
    3. Up to seven *vertical* intermediate cleats also fit between the edge vertical cleats. They are 
       distributed so the clear centre-to-centre pitch is never greater than 
       ``TARGET_INTERMEDIATE_CLEAT_SPACING``.
    4. Because each intermediate cleat is sandwiched between the horizontal cleats, its length is::

           left_panel_assembly_height - (2 * cleat_material_member_width)

    Returns
    -------
    dict
        Top-level keys: "plywood", "horizontal_cleats", "vertical_cleats",
        "intermediate_vertical_cleats".

        The ``intermediate_vertical_cleats`` sub-dict contains extra, NX-friendly fields:
        count, positions_x_centerline, positions_x_left_edge, edge_to_edge_distances and
        suppress_flags (list[int] length == MAX_INTERMEDIATE_CLEATS).  0 = suppressed, 1 = keep.
    """

    # ---------------------------------------------------------------------
    # Plywood (sheathing)
    # ---------------------------------------------------------------------
    plywood_length = left_panel_assembly_length
    plywood_height = left_panel_assembly_height
    plywood_thickness = panel_sheathing_thickness

    # ---------------------------------------------------------------------
    # Derived cleat lengths
    # ---------------------------------------------------------------------
    # Horizontal cleats run between the two vertical edge cleats, so subtract
    # the *member width* of those edge cleats from the overall panel length.
    horizontal_cleat_length = left_panel_assembly_length - (2 * cleat_material_member_width)
    if horizontal_cleat_length < 0:
        horizontal_cleat_length = 0

    # Vertical edge cleats span the full height of the panel.
    vertical_cleat_length = left_panel_assembly_height

    # Intermediate vertical cleats sit between the horizontal top/bottom cleats,
    # so their length is reduced by two times the cleat member width.
    intermediate_vertical_cleat_length = left_panel_assembly_height - (2 * cleat_material_member_width)

    # ---------------------------------------------------------------------
    # Intermediate vertical cleats
    # ---------------------------------------------------------------------
    inter_cleats = {
        "count": 0,
        "length": intermediate_vertical_cleat_length,
        "material_thickness": cleat_material_thickness,
        "material_member_width": cleat_material_member_width,
        "positions_x_centerline": [],
        "positions_x_left_edge": [],
        "edge_to_edge_distances": [],
        "suppress_flags": [0] * MAX_INTERMEDIATE_CLEATS,
        "orientation": "Vertical",
    }

    # Centre-to-centre span between edge vertical cleats
    span_cc = plywood_length - cleat_material_member_width

    if span_cc > TARGET_INTERMEDIATE_CLEAT_SPACING and plywood_length > (2 * cleat_material_member_width):
        # Use the comprehensive plywood layout and cleat positioning system
        plywood_sheets = calculate_plywood_layout_for_panel(plywood_length, plywood_height)
        vertical_splice_positions = extract_vertical_splice_positions_for_panel(plywood_sheets)
        
        # If no vertical splices, optimize for uniform spacing for symmetry
        if not vertical_splice_positions:
            # For symmetric spacing, find the MINIMUM number of cleats needed to keep spacing ≤ 24"
            # Then use symmetric positioning
            
            # Find minimum number of segments needed to keep spacing ≤ 24"
            min_segments_needed = math.ceil(span_cc / TARGET_INTERMEDIATE_CLEAT_SPACING)
            min_inter_count = max(0, min_segments_needed - 1)  # subtract 1 because segments = intermediate_count + 1
            
            # Make sure we don't exceed maximum allowed cleats
            inter_count = min(min_inter_count, MAX_INTERMEDIATE_CLEATS)

            if inter_count > 0:
                # For TRUE symmetry, we need to calculate equal gaps between ALL elements
                # Total gaps = inter_count + 1 (gaps between all cleats including edges)
                num_cc_segments = inter_count + 1
                
                # Calculate the uniform center-to-center spacing required for symmetry
                actual_cc = span_cc / num_cc_segments
                
                # Generate positions with truly uniform gaps
                prev_right_edge = 0.0  # plywood left-edge initially
                
                for k in range(1, inter_count + 1):
                    # Position the centerline of this cleat
                    cx = (cleat_material_member_width / 2.0) + (k * actual_cc)
                    lx = cx - (cleat_material_member_width / 2.0)

                    inter_cleats["positions_x_centerline"].append(round(cx, 4))
                    inter_cleats["positions_x_left_edge"].append(round(lx, 4))

                    # Calculate the gap that was just created
                    gap_edge_to_edge = round(lx - prev_right_edge, 4)
                    inter_cleats["edge_to_edge_distances"].append(gap_edge_to_edge)
                    
                    # Update for next iteration
                    prev_right_edge = lx + cleat_material_member_width

                inter_cleats["count"] = inter_count
                for i in range(inter_count):
                    inter_cleats["suppress_flags"][i] = 1  # mark as active
        else:
            # Use the sophisticated cleat positioning system for panels with vertical splices
            cleat_positions = calculate_vertical_cleat_positions_for_panel(
                plywood_length, 
                vertical_splice_positions, 
                cleat_material_member_width
            )
            
            # Limit to maximum allowed cleats
            cleat_positions = cleat_positions[:MAX_INTERMEDIATE_CLEATS]
            inter_count = len(cleat_positions)
            
            if inter_count > 0:
                prev_right_edge = 0.0  # plywood left-edge initially
                
                for cx in cleat_positions:
                    lx = cx - (cleat_material_member_width / 2.0)

                    inter_cleats["positions_x_centerline"].append(round(cx, 4))
                    inter_cleats["positions_x_left_edge"].append(round(lx, 4))

                    gap_edge_to_edge = round(lx - prev_right_edge, 4)
                    inter_cleats["edge_to_edge_distances"].append(gap_edge_to_edge)
                    prev_right_edge = lx + cleat_material_member_width

                inter_cleats["count"] = inter_count
                for i in range(inter_count):
                    inter_cleats["suppress_flags"][i] = 1  # mark as active

    # ---------------------------------------------------------------------
    # Pack and return
    # ---------------------------------------------------------------------
    components = {
        "plywood": {
            "length": plywood_length,
            "height": plywood_height,
            "thickness": plywood_thickness,
        },
        "horizontal_cleats": {
            "length": horizontal_cleat_length,
            "material_thickness": cleat_material_thickness,
            "material_member_width": cleat_material_member_width,
            "count": 2,
        },
        "vertical_cleats": {
            "length": vertical_cleat_length,
            "material_thickness": cleat_material_thickness,
            "material_member_width": cleat_material_member_width,
            "count": 2,
        },
        "intermediate_vertical_cleats": inter_cleats,
    }

    # Calculate horizontal splice positions for intermediate horizontal cleats
    horizontal_splice_positions = calculate_horizontal_splice_positions(
        left_panel_assembly_length, 
        left_panel_assembly_height
    )
    
    # Calculate horizontal cleat sections if splices exist
    if horizontal_splice_positions:
        horizontal_cleat_sections = []
        for splice_y in horizontal_splice_positions:
            sections = calculate_horizontal_cleat_sections(
                panel_width=left_panel_assembly_length,
                cleat_member_width=cleat_material_member_width,
                vertical_cleats_data=inter_cleats,
                splice_y_position=splice_y
            )
            horizontal_cleat_sections.extend(sections)
        
        # Calculate pattern count based on number of horizontal splices
        # Count: 1 if only 1 splice, 2 if more than 1 splice
        horizontal_splice_count = len(horizontal_splice_positions)
        pattern_count = 1 if horizontal_splice_count == 1 else (2 if horizontal_splice_count > 1 else 1)
        
        # Add horizontal cleat data to components
        components["intermediate_horizontal_cleats"] = {
            "count": len(horizontal_cleat_sections),
            "sections": horizontal_cleat_sections,
            "material_thickness": cleat_material_thickness,
            "material_member_width": cleat_material_member_width,
            "orientation": "Horizontal",
            "horizontal_splice_count": horizontal_splice_count,
            "pattern_count": pattern_count
        }
    else:
        # No horizontal splices needed
        components["intermediate_horizontal_cleats"] = {
            "count": 0,
            "sections": [],
            "material_thickness": cleat_material_thickness,
            "material_member_width": cleat_material_member_width,
            "orientation": "None",
            "horizontal_splice_count": 0,
            "pattern_count": 1
        }

    return components


# ---------------------------------------------------------------------------
# Simple self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    demo_data = calculate_left_panel_components(
        left_panel_assembly_length=96.0,
        left_panel_assembly_height=48.0,
        panel_sheathing_thickness=0.75,
        cleat_material_thickness=1.50,
        cleat_material_member_width=3.50,
    )

    import json
    print(json.dumps(demo_data, indent=4)) 