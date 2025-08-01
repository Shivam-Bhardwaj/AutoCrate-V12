"""
Klimp Placement Logic Module

Calculates optimal positioning for klimps (clamps/fasteners) on front panels.
Klimps are placed with 16-24 inch spacing and maintain 2-inch clearance from cleats.

Requirements:
- Klimps should be 16 to 24 inches apart (center-to-center)
- Klimps should be at least 2 inches from the nearest cleat
- Klimps are placed on the front panel surface for accessibility
"""

import math
from typing import Dict, List, Tuple

# Constants for klimp placement
MIN_KLIMP_SPACING = 16.0  # inches C-C minimum
MAX_KLIMP_SPACING = 24.0  # inches C-C maximum
TARGET_KLIMP_SPACING = 20.0  # inches C-C preferred
MIN_CLEAT_CLEARANCE = 2.0  # inches minimum clearance from cleats
MIN_EDGE_CLEARANCE = 3.0  # inches minimum clearance from panel edges


def calculate_klimp_positions(
    panel_width: float,
    panel_height: float,
    cleat_member_width: float,
    vertical_cleats_data: Dict,
    horizontal_cleats_data: Dict = None,
    klimp_diameter: float = 1.0
) -> Dict:
    """
    Calculate optimal positions for klimps on the front panel.
    
    Args:
        panel_width: Width of the panel in inches
        panel_height: Height of the panel in inches
        cleat_member_width: Width of cleat members (typically 3.5")
        vertical_cleats_data: Data about vertical cleats and positions
        horizontal_cleats_data: Data about horizontal cleats and positions
        klimp_diameter: Diameter of klimp hardware (default 1.0")
        
    Returns:
        Dictionary containing klimp positions and metadata
    """
    
    # Calculate exclusion zones (areas where klimps cannot be placed)
    exclusion_zones = _calculate_exclusion_zones(
        panel_width, panel_height, cleat_member_width,
        vertical_cleats_data, horizontal_cleats_data
    )
    
    # Calculate available placement zones
    placement_zones = _calculate_placement_zones(
        panel_width, panel_height, exclusion_zones
    )
    
    # Calculate klimp positions in each zone
    klimp_positions = []
    total_klimps = 0
    
    for zone in placement_zones:
        zone_klimps = _calculate_klimps_in_zone(zone, klimp_diameter)
        klimp_positions.extend(zone_klimps)
        total_klimps += len(zone_klimps)
    
    # Optimize klimp distribution for even spacing
    optimized_positions = _optimize_klimp_distribution(
        klimp_positions, panel_width, panel_height
    )
    
    return {
        'klimps': {
            'count': len(optimized_positions),
            'positions': optimized_positions,
            'diameter': klimp_diameter,
            'material_clearance': MIN_CLEAT_CLEARANCE,
            'edge_clearance': MIN_EDGE_CLEARANCE
        },
        'placement_zones': placement_zones,
        'exclusion_zones': exclusion_zones,
        'spacing_analysis': _analyze_spacing(optimized_positions)
    }


def _calculate_exclusion_zones(
    panel_width: float,
    panel_height: float,
    cleat_member_width: float,
    vertical_cleats_data: Dict,
    horizontal_cleats_data: Dict = None
) -> List[Dict]:
    """
    Calculate zones where klimps cannot be placed due to cleat interference.
    
    Returns:
        List of exclusion zone dictionaries with x_min, x_max, y_min, y_max
    """
    exclusion_zones = []
    
    # Edge cleat exclusion zones with clearance
    clearance = MIN_CLEAT_CLEARANCE
    
    # Bottom horizontal cleat exclusion zone
    exclusion_zones.append({
        'type': 'horizontal_edge_cleat',
        'description': 'Bottom edge cleat',
        'x_min': 0,
        'x_max': panel_width,
        'y_min': 0,
        'y_max': cleat_member_width + clearance
    })
    
    # Top horizontal cleat exclusion zone
    exclusion_zones.append({
        'type': 'horizontal_edge_cleat',
        'description': 'Top edge cleat',
        'x_min': 0,
        'x_max': panel_width,
        'y_min': panel_height - cleat_member_width - clearance,
        'y_max': panel_height
    })
    
    # Left vertical cleat exclusion zone
    exclusion_zones.append({
        'type': 'vertical_edge_cleat',
        'description': 'Left edge cleat',
        'x_min': 0,
        'x_max': cleat_member_width + clearance,
        'y_min': 0,
        'y_max': panel_height
    })
    
    # Right vertical cleat exclusion zone
    exclusion_zones.append({
        'type': 'vertical_edge_cleat',
        'description': 'Right edge cleat',
        'x_min': panel_width - cleat_member_width - clearance,
        'x_max': panel_width,
        'y_min': 0,
        'y_max': panel_height
    })
    
    # Intermediate vertical cleat exclusion zones
    intermediate_positions = vertical_cleats_data.get('positions_x_centerline', [])
    for i, pos_x in enumerate(intermediate_positions):
        exclusion_zones.append({
            'type': 'intermediate_vertical_cleat',
            'description': f'Intermediate vertical cleat {i+1}',
            'x_min': pos_x - (cleat_member_width / 2.0) - clearance,
            'x_max': pos_x + (cleat_member_width / 2.0) + clearance,
            'y_min': 0,
            'y_max': panel_height
        })
    
    # Horizontal cleat exclusion zones (if any)
    if horizontal_cleats_data and horizontal_cleats_data.get('sections'):
        for i, section in enumerate(horizontal_cleats_data['sections']):
            y_center = section.get('y_pos_centerline', 0)
            exclusion_zones.append({
                'type': 'intermediate_horizontal_cleat',
                'description': f'Intermediate horizontal cleat section {i+1}',
                'x_min': section['x_pos'] - clearance,
                'x_max': section['x_pos'] + section['width'] + clearance,
                'y_min': y_center - (cleat_member_width / 2.0) - clearance,
                'y_max': y_center + (cleat_member_width / 2.0) + clearance
            })
    
    return exclusion_zones


def _calculate_placement_zones(
    panel_width: float,
    panel_height: float,
    exclusion_zones: List[Dict]
) -> List[Dict]:
    """
    Calculate available rectangular zones for klimp placement.
    
    Returns:
        List of placement zone dictionaries
    """
    # Start with the full panel as one zone
    zones = [{
        'x_min': MIN_EDGE_CLEARANCE,
        'x_max': panel_width - MIN_EDGE_CLEARANCE,
        'y_min': MIN_EDGE_CLEARANCE,
        'y_max': panel_height - MIN_EDGE_CLEARANCE,
        'width': panel_width - (2 * MIN_EDGE_CLEARANCE),
        'height': panel_height - (2 * MIN_EDGE_CLEARANCE)
    }]
    
    # Subtract exclusion zones to create valid placement areas
    for exclusion in exclusion_zones:
        zones = _subtract_exclusion_from_zones(zones, exclusion)
    
    # Filter out zones that are too small for klimps
    min_zone_size = MIN_KLIMP_SPACING / 2.0
    valid_zones = []
    
    for zone in zones:
        if zone['width'] >= min_zone_size and zone['height'] >= min_zone_size:
            valid_zones.append(zone)
    
    return valid_zones


def _subtract_exclusion_from_zones(zones: List[Dict], exclusion: Dict) -> List[Dict]:
    """
    Subtract an exclusion zone from existing placement zones.
    This creates new rectangular zones around the exclusion.
    """
    new_zones = []
    
    for zone in zones:
        # Check if exclusion overlaps with this zone
        if not _zones_overlap(zone, exclusion):
            new_zones.append(zone)
            continue
        
        # Split zone around the exclusion
        split_zones = _split_zone_around_exclusion(zone, exclusion)
        new_zones.extend(split_zones)
    
    return new_zones


def _zones_overlap(zone1: Dict, zone2: Dict) -> bool:
    """Check if two rectangular zones overlap."""
    return not (
        zone1['x_max'] <= zone2['x_min'] or
        zone2['x_max'] <= zone1['x_min'] or
        zone1['y_max'] <= zone2['y_min'] or
        zone2['y_max'] <= zone1['y_min']
    )


def _split_zone_around_exclusion(zone: Dict, exclusion: Dict) -> List[Dict]:
    """
    Split a placement zone around an exclusion zone.
    Creates up to 4 rectangular zones around the exclusion.
    """
    zones = []
    
    # Left zone (if space exists)
    if zone['x_min'] < exclusion['x_min']:
        zones.append({
            'x_min': zone['x_min'],
            'x_max': min(exclusion['x_min'], zone['x_max']),
            'y_min': zone['y_min'],
            'y_max': zone['y_max'],
            'width': min(exclusion['x_min'], zone['x_max']) - zone['x_min'],
            'height': zone['y_max'] - zone['y_min']
        })
    
    # Right zone (if space exists)
    if zone['x_max'] > exclusion['x_max']:
        zones.append({
            'x_min': max(exclusion['x_max'], zone['x_min']),
            'x_max': zone['x_max'],
            'y_min': zone['y_min'],
            'y_max': zone['y_max'],
            'width': zone['x_max'] - max(exclusion['x_max'], zone['x_min']),
            'height': zone['y_max'] - zone['y_min']
        })
    
    # Bottom zone (if space exists)
    if zone['y_min'] < exclusion['y_min']:
        zones.append({
            'x_min': max(zone['x_min'], exclusion['x_min']),
            'x_max': min(zone['x_max'], exclusion['x_max']),
            'y_min': zone['y_min'],
            'y_max': min(exclusion['y_min'], zone['y_max']),
            'width': min(zone['x_max'], exclusion['x_max']) - max(zone['x_min'], exclusion['x_min']),
            'height': min(exclusion['y_min'], zone['y_max']) - zone['y_min']
        })
    
    # Top zone (if space exists)
    if zone['y_max'] > exclusion['y_max']:
        zones.append({
            'x_min': max(zone['x_min'], exclusion['x_min']),
            'x_max': min(zone['x_max'], exclusion['x_max']),
            'y_min': max(exclusion['y_max'], zone['y_min']),
            'y_max': zone['y_max'],
            'width': min(zone['x_max'], exclusion['x_max']) - max(zone['x_min'], exclusion['x_min']),
            'height': zone['y_max'] - max(exclusion['y_max'], zone['y_min'])
        })
    
    # Filter out zones with non-positive dimensions
    valid_zones = []
    for zone in zones:
        if zone['width'] > 0 and zone['height'] > 0:
            valid_zones.append(zone)
    
    return valid_zones


def _calculate_klimps_in_zone(zone: Dict, klimp_diameter: float) -> List[Dict]:
    """
    Calculate klimp positions within a specific placement zone.
    Uses a grid-based approach to ensure even spacing.
    """
    klimps = []
    
    # Calculate how many klimps can fit in each direction
    available_width = zone['width']
    available_height = zone['height']
    
    # Account for klimp diameter in spacing calculations
    effective_spacing_x = TARGET_KLIMP_SPACING
    effective_spacing_y = TARGET_KLIMP_SPACING
    
    # Calculate number of klimps that can fit
    num_klimps_x = max(1, int(available_width / effective_spacing_x) + 1)
    num_klimps_y = max(1, int(available_height / effective_spacing_y) + 1)
    
    # If zone is too narrow or short, place klimps along the longer dimension
    if available_width < MIN_KLIMP_SPACING:
        num_klimps_x = 1
    if available_height < MIN_KLIMP_SPACING:
        num_klimps_y = 1
    
    # Calculate actual spacing for even distribution
    if num_klimps_x > 1:
        actual_spacing_x = available_width / (num_klimps_x - 1)
    else:
        actual_spacing_x = 0
    
    if num_klimps_y > 1:
        actual_spacing_y = available_height / (num_klimps_y - 1)
    else:
        actual_spacing_y = 0
    
    # Validate spacing is within acceptable range
    if actual_spacing_x > 0 and (actual_spacing_x < MIN_KLIMP_SPACING or actual_spacing_x > MAX_KLIMP_SPACING):
        # Adjust number of klimps to get acceptable spacing
        num_klimps_x = max(1, int(available_width / TARGET_KLIMP_SPACING))
        if num_klimps_x > 1:
            actual_spacing_x = available_width / (num_klimps_x - 1)
    
    if actual_spacing_y > 0 and (actual_spacing_y < MIN_KLIMP_SPACING or actual_spacing_y > MAX_KLIMP_SPACING):
        # Adjust number of klimps to get acceptable spacing
        num_klimps_y = max(1, int(available_height / TARGET_KLIMP_SPACING))
        if num_klimps_y > 1:
            actual_spacing_y = available_height / (num_klimps_y - 1)
    
    # Generate klimp positions
    for i in range(num_klimps_x):
        for j in range(num_klimps_y):
            if num_klimps_x == 1:
                x_pos = zone['x_min'] + (available_width / 2.0)
            else:
                x_pos = zone['x_min'] + (i * actual_spacing_x)
            
            if num_klimps_y == 1:
                y_pos = zone['y_min'] + (available_height / 2.0)
            else:
                y_pos = zone['y_min'] + (j * actual_spacing_y)
            
            klimps.append({
                'x_pos': round(x_pos, 4),
                'y_pos': round(y_pos, 4),
                'zone_id': f"zone_{len(klimps)}",
                'grid_position': (i, j)
            })
    
    return klimps


def _optimize_klimp_distribution(
    klimp_positions: List[Dict],
    panel_width: float,
    panel_height: float
) -> List[Dict]:
    """
    Optimize klimp distribution for better spacing and coverage.
    Removes klimps that are too close together and adjusts positions.
    """
    if not klimp_positions:
        return []
    
    # Sort klimps by position for processing
    klimps = sorted(klimp_positions, key=lambda k: (k['y_pos'], k['x_pos']))
    
    # Remove klimps that are too close together
    optimized_klimps = []
    
    for klimp in klimps:
        too_close = False
        
        for existing in optimized_klimps:
            distance = math.sqrt(
                (klimp['x_pos'] - existing['x_pos'])**2 + 
                (klimp['y_pos'] - existing['y_pos'])**2
            )
            
            if distance < MIN_KLIMP_SPACING:
                too_close = True
                break
        
        if not too_close:
            optimized_klimps.append(klimp)
    
    # Add sequential IDs for NX expressions
    for i, klimp in enumerate(optimized_klimps):
        klimp['id'] = i + 1
        klimp['nx_variable_suffix'] = f"_{i + 1}"
    
    return optimized_klimps


def _analyze_spacing(klimp_positions: List[Dict]) -> Dict:
    """
    Analyze spacing between klimps for quality assessment.
    """
    if len(klimp_positions) < 2:
        return {
            'min_spacing': 0,
            'max_spacing': 0,
            'avg_spacing': 0,
            'spacing_quality': 'N/A'
        }
    
    spacings = []
    
    for i, klimp1 in enumerate(klimp_positions):
        for j, klimp2 in enumerate(klimp_positions[i+1:], i+1):
            distance = math.sqrt(
                (klimp1['x_pos'] - klimp2['x_pos'])**2 + 
                (klimp1['y_pos'] - klimp2['y_pos'])**2
            )
            spacings.append(distance)
    
    min_spacing = min(spacings)
    max_spacing = max(spacings)
    avg_spacing = sum(spacings) / len(spacings)
    
    # Assess quality
    if min_spacing >= MIN_KLIMP_SPACING and max_spacing <= MAX_KLIMP_SPACING:
        quality = "Excellent"
    elif min_spacing >= MIN_KLIMP_SPACING:
        quality = "Good"
    else:
        quality = "Needs Review"
    
    return {
        'min_spacing': round(min_spacing, 2),
        'max_spacing': round(max_spacing, 2),
        'avg_spacing': round(avg_spacing, 2),
        'spacing_quality': quality,
        'total_pairs': len(spacings)
    }


def run_example():
    """Example usage and testing of klimp placement logic."""
    
    # Test case 1: Basic panel with intermediate vertical cleats
    print("=== Test Case 1: 60x40 panel with intermediate cleats ===")
    
    vertical_cleats_data = {
        'count': 2,
        'positions_x_centerline': [20.0, 40.0],
        'orientation': 'Vertical'
    }
    
    klimp_data = calculate_klimp_positions(
        panel_width=60.0,
        panel_height=40.0,
        cleat_member_width=3.5,
        vertical_cleats_data=vertical_cleats_data
    )
    
    print(f"Klimp count: {klimp_data['klimps']['count']}")
    print(f"Spacing quality: {klimp_data['spacing_analysis']['spacing_quality']}")
    print(f"Average spacing: {klimp_data['spacing_analysis']['avg_spacing']} inches")
    
    for i, klimp in enumerate(klimp_data['klimps']['positions']):
        print(f"  Klimp {i+1}: X={klimp['x_pos']}, Y={klimp['y_pos']}")
    
    print(f"Placement zones: {len(klimp_data['placement_zones'])}")
    print(f"Exclusion zones: {len(klimp_data['exclusion_zones'])}")
    
    # Test case 2: Small panel
    print("\n=== Test Case 2: 30x24 panel (minimal cleats) ===")
    
    small_vertical_cleats = {
        'count': 0,
        'positions_x_centerline': [],
        'orientation': 'None'
    }
    
    small_klimp_data = calculate_klimp_positions(
        panel_width=30.0,
        panel_height=24.0,
        cleat_member_width=3.5,
        vertical_cleats_data=small_vertical_cleats
    )
    
    print(f"Klimp count: {small_klimp_data['klimps']['count']}")
    print(f"Spacing quality: {small_klimp_data['spacing_analysis']['spacing_quality']}")
    
    for i, klimp in enumerate(small_klimp_data['klimps']['positions']):
        print(f"  Klimp {i+1}: X={klimp['x_pos']}, Y={klimp['y_pos']}")


if __name__ == '__main__':
    run_example()