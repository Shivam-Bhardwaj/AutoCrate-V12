import pytest
from legacy.end_panel_logic import calculate_end_panel_components
import legacy.end_panel_logic as end_panel_logic
from unittest.mock import patch

# Test cases for calculate_end_panel_components
# Each tuple contains: (width, height, sheathing_thick, cleat_thick, cleat_width, expected_horizontal_cleat_length)
end_panel_test_cases = [
    # Standard case
    (30.0, 60.0, 0.75, 1.5, 3.5, 23.0),
    # Case where horizontal cleats would be zero length
    (7.0, 60.0, 0.75, 1.5, 3.5, 0.0),
    # Case where horizontal cleats would have negative length, should be corrected to 0
    (5.0, 60.0, 0.75, 1.5, 3.5, 0.0),
    # Another standard case
    (48, 96, 0.5, 1.25, 3.5, 41.0),
]

@pytest.mark.parametrize("width, height, sheathing_thick, cleat_thick, cleat_width, expected_h_cleat_len", end_panel_test_cases)
def test_calculate_end_panel_components(width, height, sheathing_thick, cleat_thick, cleat_width, expected_h_cleat_len):
    """
    Tests the calculation of end panel components, focusing on the horizontal cleat length.
    """
    components = calculate_end_panel_components(
        end_panel_assembly_face_width=width,
        end_panel_assembly_height=height,
        panel_sheathing_thickness=sheathing_thick,
        cleat_material_thickness=cleat_thick,
        cleat_material_member_width=cleat_width
    )

    # Test plywood dimensions
    assert components['plywood']['width'] == width
    assert components['plywood']['height'] == height

    # Test vertical cleat length
    assert components['vertical_cleats']['length'] == height

    # Test horizontal cleat length calculation and handling of small panel widths
    assert components['horizontal_cleats']['length'] == expected_h_cleat_len

@patch('builtins.print')
def test_end_panel_logic_main_block(mock_print):
    """
    Tests the main execution block of the end_panel_logic script.
    """
    end_panel_logic.run_example()
    assert mock_print.called