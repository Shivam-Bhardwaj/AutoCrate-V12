import pytest
from legacy.front_panel_logic import (
    calculate_front_panel_components,
    calculate_horizontal_splice_positions,
    calculate_horizontal_cleat_sections
)
import legacy.front_panel_logic as front_panel_logic
from unittest.mock import patch

# Test cases for calculate_front_panel_components focusing on intermediate vertical cleats
# Each tuple contains: (width, height, cleat_width, expected_intermediate_count, expected_positions)
front_panel_vertical_cleats_test_cases = [
    # Case 1: Width is large enough to require 2 intermediate cleats
    (60.0, 40.0, 3.5, 2, [20.5833, 39.4167]),
    # Case 2: Width requires 1 intermediate cleat
    (30.0, 40.0, 3.5, 1, [15.0]),
    # Case 3: Width is just under the threshold, no intermediate cleats needed
    (27.0, 40.0, 3.5, 0, []),
    # Case 4: Width is exactly at a point where C-C spacing is <= 24, no cleats needed
    (27.5, 40.0, 3.5, 0, []),
    # Case 5: Width is just over the threshold where 1 cleat is needed
    (27.6, 40.0, 3.5, 1, [13.8]),
]

@pytest.mark.parametrize("width, height, cleat_width, expected_count, expected_positions", front_panel_vertical_cleats_test_cases)
def test_calculate_front_panel_intermediate_vertical_cleats(width, height, cleat_width, expected_count, expected_positions):
    """
    Tests the calculation of intermediate vertical cleats in the front panel.
    """
    components = calculate_front_panel_components(
        front_panel_assembly_width=width,
        front_panel_assembly_height=height,
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

# Test cases for horizontal splice positions from the legacy logic
horizontal_splice_test_cases = [
    (100, 50, []), # Legacy logic does not produce splices for this case
    (40, 100, [4.0]),
    (100, 100, [4.0]),
    (200, 40, []),
]

@pytest.mark.parametrize("panel_width, panel_height, expected_splices", horizontal_splice_test_cases)
def test_calculate_horizontal_splice_positions(panel_width, panel_height, expected_splices):
    """
    Tests the logic for determining where horizontal splices in plywood should occur.
    """
    splices = calculate_horizontal_splice_positions(panel_width, panel_height)
    assert splices == expected_splices

@patch('builtins.print')
def test_front_panel_logic_main_block(mock_print):
    """
    Tests the main execution block of the front_panel_logic script.
    """
    front_panel_logic.run_example()
    assert mock_print.called