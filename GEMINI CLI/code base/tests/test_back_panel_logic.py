import pytest
from back_panel_logic import calculate_back_panel_components
from front_panel_logic import calculate_front_panel_components
import back_panel_logic
from unittest.mock import patch

def test_calculate_back_panel_components_mirrors_front_panel():
    """
    Tests that the back panel calculation produces the same output as the front panel
    calculation, as it is designed to be a direct pass-through.
    """
    # Define a common set of inputs
    width = 60.0
    height = 40.0
    sheathing_thick = 0.75
    cleat_thick = 1.5
    cleat_width = 3.5

    # Calculate components using both front and back panel functions
    back_panel_data = calculate_back_panel_components(
        back_panel_assembly_width=width,
        back_panel_assembly_height=height,
        panel_sheathing_thickness=sheathing_thick,
        cleat_material_thickness=cleat_thick,
        cleat_material_member_width=cleat_width
    )

    front_panel_data = calculate_front_panel_components(
        front_panel_assembly_width=width,
        front_panel_assembly_height=height,
        panel_sheathing_thickness=sheathing_thick,
        cleat_material_thickness=cleat_thick,
        cleat_material_member_width=cleat_width
    )

    # Assert that the entire dictionary output is identical
    assert back_panel_data == front_panel_data

@patch('builtins.print')
def test_back_panel_logic_main_block(mock_print):
    """
    Tests the main execution block of the back_panel_logic script.
    """
    back_panel_logic.run_example()
    assert mock_print.called