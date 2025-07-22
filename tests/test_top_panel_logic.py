import pytest
from legacy.top_panel_logic import calculate_top_panel_components

# Test cases for the top panel's intermediate cleats (which run across the width)
# Each tuple contains: (width, length, cleat_width, expected_intermediate_count, expected_positions)
top_panel_intermediate_cleats_test_cases = [
    # Case 1: Width is large enough to require 2 intermediate cleats
    (60.0, 120.0, 3.5, 2, [20.5833, 39.4167]),
    # Case 2: Width requires 1 intermediate cleat. Position should be exactly in the middle.
    (48.0, 96.0, 3.5, 1, [24.0]),
    # Case 3: Width is just under the threshold, no intermediate cleats needed
    (27.0, 80.0, 3.5, 0, []),
]

@pytest.mark.parametrize("width, length, cleat_width, expected_count, expected_positions", top_panel_intermediate_cleats_test_cases)
def test_calculate_top_panel_intermediate_cleats(width, length, cleat_width, expected_count, expected_positions):
    """
    Tests the calculation of intermediate cleats for the top panel.
    """
    components = calculate_top_panel_components(
        top_panel_assembly_width=width,
        top_panel_assembly_length=length,
        panel_sheathing_thickness=0.75,
        cleat_material_thickness=1.5,
        cleat_material_member_width=cleat_width
    )

    intermediate_cleats = components['intermediate_cleats']
    
    assert intermediate_cleats['count'] == expected_count
    
    # Check positions with a tolerance for floating point comparisons
    assert len(intermediate_cleats['positions_x_centerline']) == len(expected_positions)
    for i, pos in enumerate(intermediate_cleats['positions_x_centerline']):
        assert pos == pytest.approx(expected_positions[i], rel=1e-3)

def test_calculate_top_panel_small_width():
    """
    Tests that for a very small width, the secondary cleat length is correctly calculated as 0.
    """
    components = calculate_top_panel_components(
        top_panel_assembly_width=5.0,
        top_panel_assembly_length=100.0,
        panel_sheathing_thickness=0.75,
        cleat_material_thickness=1.5,
        cleat_material_member_width=3.5
    )
    
    # Secondary cleats fit between primary cleats, so length should be 5.0 - (2 * 3.5) = -2.0, which gets corrected to 0.
    assert components['secondary_cleats']['length'] == 0
