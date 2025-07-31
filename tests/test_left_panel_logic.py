import pytest
from autocrate.left_panel_logic import calculate_left_panel_components

# Test cases for the left panel's intermediate vertical cleats
# Each tuple contains: (length, height, cleat_width, expected_intermediate_count, expected_positions)
left_panel_intermediate_cleats_test_cases = [
    # Case 1: Length is large enough to require 2 intermediate cleats
    (60.0, 48.0, 3.5, 2, [20.5833, 39.4167]),
    # Case 2: Length requires 1 intermediate cleat. Position should be exactly in the middle.
    (48.0, 96.0, 3.5, 1, [24.0]),
    # Case 3: Length is just under the threshold, no intermediate cleats needed
    (27.0, 80.0, 3.5, 0, []),
]

@pytest.mark.parametrize("length, height, cleat_width, expected_count, expected_positions", left_panel_intermediate_cleats_test_cases)
def test_calculate_left_panel_intermediate_cleats(length, height, cleat_width, expected_count, expected_positions):
    """
    Tests the calculation of intermediate vertical cleats for the left panel.
    """
    components = calculate_left_panel_components(
        left_panel_assembly_length=length,
        left_panel_assembly_height=height,
        panel_sheathing_thickness=0.75,
        cleat_material_thickness=1.5,
        cleat_material_member_width=cleat_width
    )

    intermediate_cleats = components['intermediate_vertical_cleats']
    
    assert intermediate_cleats['count'] == expected_count
    
    # Check positions with a tolerance for floating point comparisons
    assert len(intermediate_cleats['positions_x_centerline']) == len(expected_positions)
    for i, pos in enumerate(intermediate_cleats['positions_x_centerline']):
        assert pos == pytest.approx(expected_positions[i], rel=1e-3)

def test_calculate_left_panel_small_length():
    """
    Tests that for a very small length, the horizontal cleat length is correctly calculated as 0.
    """
    components = calculate_left_panel_components(
        left_panel_assembly_length=5.0,
        left_panel_assembly_height=100.0,
        panel_sheathing_thickness=0.75,
        cleat_material_thickness=1.5,
        cleat_material_member_width=3.5
    )
    
    # Horizontal cleats fit between vertical cleats, so length should be 5.0 - (2 * 3.5) = -2.0, which gets corrected to 0.
    assert components['horizontal_cleats']['length'] == 0
