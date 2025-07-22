import pytest
from right_panel_logic import calculate_right_panel_components
from left_panel_logic import calculate_left_panel_components
import right_panel_logic
from unittest.mock import patch

def test_calculate_right_panel_components_mirrors_left_panel():
    """
    Tests that the right panel calculation produces the same output as the left panel
    calculation, as it is designed to be a direct pass-through.
    """
    # Define a common set of inputs
    length = 96.0
    height = 48.0
    sheathing_thick = 0.5
    cleat_thick = 1.25
    cleat_width = 3.5

    # Calculate components using both left and right panel functions
    right_panel_data = calculate_right_panel_components(
        left_panel_assembly_length=length,
        left_panel_assembly_height=height,
        panel_sheathing_thickness=sheathing_thick,
        cleat_material_thickness=cleat_thick,
        cleat_material_member_width=cleat_width
    )

    left_panel_data = calculate_left_panel_components(
        left_panel_assembly_length=length,
        left_panel_assembly_height=height,
        panel_sheathing_thickness=sheathing_thick,
        cleat_material_thickness=cleat_thick,
        cleat_material_member_width=cleat_width
    )

    # Assert that the entire dictionary output is identical
    assert right_panel_data == left_panel_data

@patch('builtins.print')
def test_right_panel_logic_main_block(mock_print):
    """
    Tests the main execution block of the right_panel_logic script.
    """
    right_panel_logic.run_example()
    assert mock_print.called