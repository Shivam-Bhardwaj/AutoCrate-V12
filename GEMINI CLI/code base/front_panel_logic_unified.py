"""
Unified Front Panel Logic Module

This module consolidates the best features from all front panel logic variants:
- Sophisticated tie-breaking logic from base version
- Adaptive strategy selection from hybrid approach
- Complete metadata reporting for debugging
- Preserved variable names for NX expressions compatibility

Combines:
- front_panel_logic.py (base implementation)
- front_panel_logic_hybrid.py (hybrid approach)
- front_panel_logic_with_dimension_adjustment.py (dimension adjustment)
- improved_front_panel_logic.py (improved tie-breaking)
"""

import math

TARGET_INTERMEDIATE_CLEAT_SPACING = 24.0  # inches C-C target

def calculate_front_panel_components(
    front_panel_assembly_width: float,
    front_panel_assembly_height: float,
    panel_sheathing_thickness: float,
    cleat_material_thickness: float,
    cleat_material_member_width: float,
    strategy: str = "hybrid",
    adjustment_threshold: float = 2.0,
    adjustment_increment: float = 0.25,
    debug: bool = False
) -> dict:
    """
    Unified front panel calculation with adaptive strategy selection.
    
    Strategies:
    - "hybrid": Adaptive selection based on adjustment threshold (default)
    - "dimension": Pure dimension adjustment approach
    - "position": Position adjustment approach (deprecated)
    
    Args:
        front_panel_assembly_width: Overall width of the front panel assembly.
        front_panel_assembly_height: Overall height of the front panel assembly.
        panel_sheathing_thickness: Thickness of the plywood/sheathing.
        cleat_material_thickness: Thickness of the cleat lumber.
        cleat_material_member_width: Actual face width of the cleat lumber.
        strategy: Splice coverage strategy ("hybrid", "dimension", or "position")
        adjustment_threshold: Threshold for hybrid strategy switching (default 2.0")
        adjustment_increment: Increment for height adjustments (default 0.25")
        debug: Enable debug output for troubleshooting
    
    Returns:
        A dictionary containing the dimensions of the front panel components.
    """
    
    if strategy == "hybrid":
        return _calculate_hybrid_approach(
            front_panel_assembly_width, front_panel_assembly_height,
            panel_sheathing_thickness, cleat_material_thickness, cleat_material_member_width,
            adjustment_threshold, adjustment_increment, debug
        )
    elif strategy == "dimension":
        return _calculate_dimension_adjustment(
            front_panel_assembly_width, front_panel_assembly_height,
            panel_sheathing_thickness, cleat_material_thickness, cleat_material_member_width,
            adjustment_increment, debug
        )
    else:  # position or fallback
        return _calculate_base_approach(
            front_panel_assembly_width, front_panel_assembly_height,
            panel_sheathing_thickness, cleat_material_thickness, cleat_material_member_width,
            debug
        )


def _calculate_hybrid_approach(
    front_panel_assembly_width: float,
    front_panel_assembly_height: float,
    panel_sheathing_thickness: float,
    cleat_material_thickness: float,
    cleat_material_member_width: float,
    adjustment_threshold: float,
    adjustment_increment: float,
    debug: bool
) -> dict:
    """
    Hybrid approach: adaptive strategy selection based on adjustment size.
    Small adjustments use dimension adjustment, large adjustments use position adjustment.
    """
    
    # Store original dimensions
    original_width = front_panel_assembly_width
    original_height = front_panel_assembly_height
    
    # Calculate horizontal splice positions based on original dimensions
    horizontal_splice_positions = calculate_horizontal_splice_positions(
        front_panel_assembly_width, front_panel_assembly_height, debug
    )
    
    # Determine adjustment strategy
    adjustment_needed = calculate_required_panel_height_for_splice_coverage(
        horizontal_splice_positions, cleat_material_member_width, front_panel_assembly_height
    )
    
    if debug:
        print(f"Hybrid Strategy - Adjustment needed: {adjustment_needed}")
        print(f"Threshold: {adjustment_threshold}")
    
    if adjustment_needed <= adjustment_threshold:
        # Small adjustment: use dimension adjustment
        strategy_used = "dimension_adjustment"
        
        # Round up to nearest increment
        if adjustment_needed > 0:
            adjustment_increments = math.ceil(adjustment_needed / adjustment_increment)
            front_panel_assembly_height += adjustment_increments * adjustment_increment
        
        # Recalculate with adjusted height
        horizontal_splice_positions = calculate_horizontal_splice_positions(
            front_panel_assembly_width, front_panel_assembly_height, debug
        )
        
        # Filter out splices covered by edge cleats
        filtered_splice_positions = _filter_splice_positions(
            horizontal_splice_positions, cleat_material_member_width, front_panel_assembly_height
        )
        
    else:
        # Large adjustment: use position adjustment
        strategy_used = "position_adjustment"
        
        # Filter out splices covered by edge cleats
        filtered_splice_positions = _filter_splice_positions(
            horizontal_splice_positions, cleat_material_member_width, front_panel_assembly_height
        )
        
        # Adjust positions for clearance
        filtered_splice_positions = _adjust_cleat_positions_for_clearance(
            filtered_splice_positions, cleat_material_member_width, front_panel_assembly_height
        )
    
    # Calculate base components
    result = _calculate_base_components(
        front_panel_assembly_width, front_panel_assembly_height,
        panel_sheathing_thickness, cleat_material_thickness, cleat_material_member_width,
        filtered_splice_positions, debug
    )
    
    # Add metadata
    result.update({
        'strategy_used': strategy_used,
        'adjustment_needed': adjustment_needed,
        'adjustment_threshold': adjustment_threshold,
        'height_adjustment': front_panel_assembly_height - original_height,
        'original_width': original_width,
        'original_height': original_height,
        'splice_positions_count': len(filtered_splice_positions)
    })
    
    return result


def _calculate_dimension_adjustment(
    front_panel_assembly_width: float,
    front_panel_assembly_height: float,
    panel_sheathing_thickness: float,
    cleat_material_thickness: float,
    cleat_material_member_width: float,
    adjustment_increment: float,
    debug: bool
) -> dict:
    """
    Pure dimension adjustment approach: always extends panel height when needed.
    """
    
    original_height = front_panel_assembly_height
    
    # Calculate horizontal splice positions
    horizontal_splice_positions = calculate_horizontal_splice_positions(
        front_panel_assembly_width, front_panel_assembly_height, debug
    )
    
    # Calculate required height adjustment
    adjustment_needed = calculate_required_panel_height_for_splice_coverage(
        horizontal_splice_positions, cleat_material_member_width, front_panel_assembly_height
    )
    
    # Apply dimension adjustment
    if adjustment_needed > 0:
        adjustment_increments = math.ceil(adjustment_needed / adjustment_increment)
        front_panel_assembly_height += adjustment_increments * adjustment_increment
        
        # Recalculate with adjusted height
        horizontal_splice_positions = calculate_horizontal_splice_positions(
            front_panel_assembly_width, front_panel_assembly_height, debug
        )
    
    # Calculate base components
    result = _calculate_base_components(
        front_panel_assembly_width, front_panel_assembly_height,
        panel_sheathing_thickness, cleat_material_thickness, cleat_material_member_width,
        horizontal_splice_positions, debug
    )
    
    # Add metadata
    result.update({
        'strategy_used': 'dimension_adjustment',
        'adjustment_needed': adjustment_needed,
        'height_adjustment': front_panel_assembly_height - original_height,
        'original_height': original_height,
        'splice_positions_count': len(horizontal_splice_positions)
    })
    
    return result


def _calculate_base_approach(
    front_panel_assembly_width: float,
    front_panel_assembly_height: float,
    panel_sheathing_thickness: float,
    cleat_material_thickness: float,
    cleat_material_member_width: float,
    debug: bool
) -> dict:
    """
    Base approach: uses the original logic with improved tie-breaking.
    """
    
    # Calculate horizontal splice positions
    horizontal_splice_positions = calculate_horizontal_splice_positions(
        front_panel_assembly_width, front_panel_assembly_height, debug
    )
    
    # Calculate base components
    result = _calculate_base_components(
        front_panel_assembly_width, front_panel_assembly_height,
        panel_sheathing_thickness, cleat_material_thickness, cleat_material_member_width,
        horizontal_splice_positions, debug
    )
    
    # Add metadata
    result.update({
        'strategy_used': 'base_approach',
        'splice_positions_count': len(horizontal_splice_positions)
    })
    
    return result


def _calculate_base_components(
    front_panel_assembly_width: float,
    front_panel_assembly_height: float,
    panel_sheathing_thickness: float,
    cleat_material_thickness: float,
    cleat_material_member_width: float,
    horizontal_splice_positions: list,
    debug: bool
) -> dict:
    """
    Calculate base panel components with given splice positions.
    """
    
    # 1. Plywood Board (Sheathing)
    plywood_width = front_panel_assembly_width
    plywood_height = front_panel_assembly_height
    plywood_thickness = panel_sheathing_thickness

    # 2. Horizontal Cleats (Top & Bottom) - Edge Cleats
    horizontal_cleat_length = plywood_width

    # 3. Vertical Cleats (Left & Right) - Edge Cleats
    vertical_cleat_length = plywood_height - (2 * cleat_material_member_width)
    
    # Ensure cleat lengths are not negative
    if vertical_cleat_length < 0:
        vertical_cleat_length = 0

    # 4. Intermediate Vertical Cleats
    edge_vertical_cleats_cc_width = plywood_width - cleat_material_member_width
    
    if edge_vertical_cleats_cc_width > TARGET_INTERMEDIATE_CLEAT_SPACING:
        # For symmetric spacing, find the MINIMUM number of cleats needed to keep spacing ≤ 24"
        min_segments_needed = math.ceil(edge_vertical_cleats_cc_width / TARGET_INTERMEDIATE_CLEAT_SPACING)
        num_intermediate_cleats = max(0, min_segments_needed - 1)
        
        if num_intermediate_cleats > 0:
            # For TRUE symmetry, we need to calculate equal gaps between ALL elements
            num_cc_segments = num_intermediate_cleats + 1
            
            # Calculate the uniform center-to-center spacing required for symmetry
            actual_cc_spacing = edge_vertical_cleats_cc_width / num_cc_segments
            
            intermediate_cleat_positions = [
                round((cleat_material_member_width / 2.0) + ((i + 1) * actual_cc_spacing), 4)
                for i in range(num_intermediate_cleats)
            ]
        else:
            intermediate_cleat_positions = []
            num_intermediate_cleats = 0
    else:
        num_intermediate_cleats = 0
        intermediate_cleat_positions = []

    # 5. Horizontal Cleat Sections
    horizontal_cleat_sections = calculate_horizontal_cleat_sections(
        horizontal_splice_positions, intermediate_cleat_positions, plywood_width, debug
    )

    if debug:
        print(f"Base Components - Intermediate cleats: {num_intermediate_cleats}")
        print(f"Horizontal cleat sections: {len(horizontal_cleat_sections)}")

    return {
        'plywood_width': plywood_width,
        'plywood_height': plywood_height,
        'plywood_thickness': plywood_thickness,
        'horizontal_cleat_length': horizontal_cleat_length,
        'vertical_cleat_length': vertical_cleat_length,
        'num_intermediate_cleats': num_intermediate_cleats,
        'intermediate_cleat_positions': intermediate_cleat_positions,
        'horizontal_splice_positions': horizontal_splice_positions,
        'horizontal_cleat_sections': horizontal_cleat_sections,
        'cleat_material_thickness': cleat_material_thickness,
        'cleat_material_member_width': cleat_material_member_width
    }


def calculate_horizontal_splice_positions(
    front_panel_assembly_width: float,
    front_panel_assembly_height: float,
    debug: bool = False
) -> list:
    """
    Calculate horizontal splice positions using improved tie-breaking logic.
    Prioritizes: fewer sheets → fewer horizontal splices → better aspect ratio → more square arrangement
    """
    
    PLYWOOD_WIDTH = 48.0  # Standard plywood width
    PLYWOOD_HEIGHT = 96.0  # Standard plywood height
    
    if debug:
        print(f"Calculating splice positions for {front_panel_assembly_width} x {front_panel_assembly_height}")
    
    # Generate possible arrangements
    arrangements = []
    
    # Try different widths (horizontal sheets)
    for width_sheets in range(1, 10):
        arrangement_width = width_sheets * PLYWOOD_WIDTH
        if arrangement_width >= front_panel_assembly_width:
            # Try different heights (vertical sheets)
            for height_sheets in range(1, 10):
                arrangement_height = height_sheets * PLYWOOD_HEIGHT
                if arrangement_height >= front_panel_assembly_height:
                    total_sheets = width_sheets * height_sheets
                    horizontal_splices = height_sheets - 1
                    vertical_splices = width_sheets - 1
                    
                    # Calculate aspect ratio match (closer to panel aspect ratio is better)
                    panel_aspect = front_panel_assembly_width / front_panel_assembly_height
                    arrangement_aspect = arrangement_width / arrangement_height
                    aspect_ratio_diff = abs(panel_aspect - arrangement_aspect)
                    
                    # Calculate "squareness" (closer to 1.0 is more square)
                    squareness = min(arrangement_aspect, 1.0 / arrangement_aspect)
                    
                    arrangements.append({
                        'width_sheets': width_sheets,
                        'height_sheets': height_sheets,
                        'total_sheets': total_sheets,
                        'horizontal_splices': horizontal_splices,
                        'vertical_splices': vertical_splices,
                        'arrangement_width': arrangement_width,
                        'arrangement_height': arrangement_height,
                        'aspect_ratio_diff': aspect_ratio_diff,
                        'squareness': squareness
                    })
    
    if not arrangements:
        return []
    
    # Sort by improved tie-breaking criteria
    arrangements.sort(key=lambda x: (
        x['total_sheets'],           # Fewer sheets first
        x['horizontal_splices'],     # Fewer horizontal splices
        x['aspect_ratio_diff'],      # Better aspect ratio match
        -x['squareness']             # More square arrangement (negative for reverse order)
    ))
    
    best_arrangement = arrangements[0]
    
    if debug:
        print(f"Best arrangement: {best_arrangement['width_sheets']}x{best_arrangement['height_sheets']} sheets")
        print(f"Total sheets: {best_arrangement['total_sheets']}")
        print(f"Horizontal splices: {best_arrangement['horizontal_splices']}")
    
    # Calculate splice positions
    horizontal_splice_positions = []
    if best_arrangement['horizontal_splices'] > 0:
        for i in range(1, best_arrangement['height_sheets']):
            splice_position = i * PLYWOOD_HEIGHT
            horizontal_splice_positions.append(splice_position)
    
    return horizontal_splice_positions


def calculate_required_panel_height_for_splice_coverage(
    horizontal_splice_positions: list,
    cleat_material_member_width: float,
    current_height: float
) -> float:
    """
    Calculate the height adjustment needed for splice coverage, checking both top and bottom cleats.
    """
    if not horizontal_splice_positions:
        return 0.0

    # Check bottom cleat
    first_splice_position = horizontal_splice_positions[0]
    bottom_edge_cleat_coverage = cleat_material_member_width
    if first_splice_position <= bottom_edge_cleat_coverage:
        # If the first splice is covered by the bottom cleat, no adjustment is needed for it.
        pass
    else:
        # If not covered, this is the adjustment needed for the bottom.
        return first_splice_position - bottom_edge_cleat_coverage

    # Check top cleat if there are more splices
    if len(horizontal_splice_positions) > 1:
        last_splice_position = horizontal_splice_positions[-1]
        top_cleat_start = current_height - cleat_material_member_width
        if last_splice_position >= top_cleat_start:
            pass # Covered by top cleat
        else:
            return top_cleat_start - last_splice_position

    return 0.0


def _filter_splice_positions(
    splice_positions: list,
    cleat_material_member_width: float,
    panel_height: float
) -> list:
    """
    Filter out splice positions that are already covered by edge cleats.
    """
    
    if not splice_positions:
        return []
    
    filtered_positions = []
    
    for position in splice_positions:
        # Check if covered by bottom edge cleat
        if position <= cleat_material_member_width:
            continue
        
        # Check if covered by top edge cleat
        if position >= panel_height - cleat_material_member_width:
            continue
        
        filtered_positions.append(position)
    
    return filtered_positions


def _adjust_cleat_positions_for_clearance(
    splice_positions: list,
    cleat_material_member_width: float,
    panel_height: float,
    minimum_clearance: float = 0.25
) -> list:
    """
    Adjust cleat positions to maintain minimum clearance from edge cleats.
    """
    
    if not splice_positions:
        return []
    
    adjusted_positions = []
    
    for position in splice_positions:
        # Ensure minimum clearance from bottom edge cleat
        min_position = cleat_material_member_width + minimum_clearance
        
        # Ensure minimum clearance from top edge cleat
        max_position = panel_height - cleat_material_member_width - minimum_clearance
        
        # Adjust position if needed
        adjusted_position = max(min_position, min(position, max_position))
        adjusted_positions.append(adjusted_position)
    
    return adjusted_positions


def calculate_horizontal_cleat_sections(
    horizontal_splice_positions: list,
    intermediate_cleat_positions: list,
    panel_width: float,
    debug: bool = False
) -> list:
    """
    Calculate horizontal cleat sections between vertical cleats.
    """
    
    if not horizontal_splice_positions:
        return []
    
    # Create list of vertical cleat positions (including edge cleats)
    vertical_positions = [0, panel_width]  # Left and right edges
    vertical_positions.extend(intermediate_cleat_positions)
    vertical_positions.sort()
    
    # Calculate sections between each pair of vertical cleats
    sections = []
    for i in range(len(vertical_positions) - 1):
        start_x = vertical_positions[i]
        end_x = vertical_positions[i + 1]
        section_width = end_x - start_x
        
        # Create sections for each horizontal splice position
        for splice_y in horizontal_splice_positions:
            sections.append({
                'start_x': start_x,
                'end_x': end_x,
                'width': section_width,
                'y_position': splice_y
            })
    
    if debug:
        print(f"Horizontal cleat sections: {len(sections)}")
        for i, section in enumerate(sections):
            print(f"  Section {i+1}: {section['start_x']:.1f} to {section['end_x']:.1f}, width={section['width']:.1f}, y={section['y_position']:.1f}")
    
    return sections


# Legacy function for backward compatibility
def calculate_front_panel_components_hybrid(
    front_panel_assembly_width: float,
    front_panel_assembly_height: float,
    panel_sheathing_thickness: float,
    cleat_material_thickness: float,
    cleat_material_member_width: float,
    adjustment_threshold: float = 2.0,
    adjustment_increment: float = 0.25
) -> dict:
    """
    Legacy wrapper for hybrid approach - maintains backward compatibility.
    """
    return calculate_front_panel_components(
        front_panel_assembly_width, front_panel_assembly_height,
        panel_sheathing_thickness, cleat_material_thickness, cleat_material_member_width,
        strategy="hybrid", adjustment_threshold=adjustment_threshold,
        adjustment_increment=adjustment_increment
    )


# Legacy function for backward compatibility
def calculate_front_panel_components_with_dimension_adjustment(
    front_panel_assembly_width: float,
    front_panel_assembly_height: float,
    panel_sheathing_thickness: float,
    cleat_material_thickness: float,
    cleat_material_member_width: float,
    adjustment_increment: float = 0.25
) -> dict:
    """
    Legacy wrapper for dimension adjustment - maintains backward compatibility.
    """
    return calculate_front_panel_components(
        front_panel_assembly_width, front_panel_assembly_height,
        panel_sheathing_thickness, cleat_material_thickness, cleat_material_member_width,
        strategy="dimension", adjustment_increment=adjustment_increment
    )


if __name__ == "__main__":
    # Test the unified module
    test_width = 100.0
    test_height = 100.0
    test_thickness = 0.75
    test_cleat_thickness = 1.5
    test_cleat_width = 3.5
    
    print("=== Testing Unified Front Panel Logic ===")
    print()
    
    # Test hybrid approach
    print("1. Hybrid Approach:")
    result = calculate_front_panel_components(
        test_width, test_height, test_thickness, test_cleat_thickness, test_cleat_width,
        strategy="hybrid", debug=True
    )
    print(f"Strategy used: {result['strategy_used']}")
    print(f"Height adjustment: {result.get('height_adjustment', 0.0)}")
    print()
    
    # Test dimension adjustment
    print("2. Dimension Adjustment:")
    result = calculate_front_panel_components(
        test_width, test_height, test_thickness, test_cleat_thickness, test_cleat_width,
        strategy="dimension", debug=True
    )
    print(f"Strategy used: {result['strategy_used']}")
    print(f"Height adjustment: {result.get('height_adjustment', 0.0)}")
    print()
    
    # Test base approach
    print("3. Base Approach:")
    result = calculate_front_panel_components(
        test_width, test_height, test_thickness, test_cleat_thickness, test_cleat_width,
        strategy="position", debug=True
    )
    print(f"Strategy used: {result['strategy_used']}")
    print()
