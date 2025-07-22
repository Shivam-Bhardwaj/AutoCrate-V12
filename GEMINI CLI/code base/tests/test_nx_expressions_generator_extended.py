import pytest
import tkinter as tk
from unittest.mock import MagicMock, patch
from nx_expressions_generator import (
    generate_crate_expressions_logic,
    CrateApp,
    calculate_plywood_layout,
    generate_plywood_nx_expressions,
    extract_vertical_splice_positions,
    calculate_vertical_cleat_positions,
    calculate_vertical_cleat_material_needed,
    update_panel_components_with_splice_cleats,
    calculate_horizontal_cleat_sections_from_vertical_positions
)

@pytest.fixture
def standard_inputs():
    """Provides a standard set of inputs for testing."""
    return {
        "product_weight_lbs": 8000.0,
        "product_length_in": 96.0,
        "product_width_in": 100.0,
        "clearance_each_side_in": 2.0,
        "allow_3x4_skids_bool": True,
        "panel_thickness_in": 0.25,
        "cleat_thickness_in": 0.75,
        "cleat_member_actual_width_in": 3.5,
        "product_actual_height_in": 30.0,
        "clearance_above_product_in": 2.0,
        "ground_clearance_in": 1.0,
        "floorboard_actual_thickness_in": 1.5,
        "selected_std_lumber_widths": [11.25, 9.25, 7.25, 5.5],
        "max_allowable_middle_gap_in": 0.25,
        "min_custom_lumber_width_in": 2.5,
        "force_small_custom_board_bool": True,
        "output_filename": "test_output.exp",
        "plywood_panel_selections": {"FP": True, "BP": True, "LP": True, "RP": True, "TP": True}
    }

def test_input_validation(standard_inputs):
    """Tests various input validation scenarios."""
    inputs = standard_inputs.copy()
    inputs["product_weight_lbs"] = -1
    success, message = generate_crate_expressions_logic(**inputs)
    assert not success and "negative" in message

    inputs = standard_inputs.copy()
    inputs["product_length_in"] = 0
    success, message = generate_crate_expressions_logic(**inputs)
    assert not success and "positive" in message

def test_calculate_plywood_layout():
    """Tests the plywood layout calculation."""
    sheets = calculate_plywood_layout(100, 50)
    assert len(sheets) > 0

def test_generate_plywood_nx_expressions():
    """Tests the generation of plywood NX expressions."""
    sheets = [{'x': 0, 'y': 0, 'width': 96, 'height': 48}]
    expressions = generate_plywood_nx_expressions(sheets, "FP_")
    assert len(expressions) > 0
    assert "FP_Plywood_1_Active = 1" in expressions

def test_extract_vertical_splice_positions():
    """Tests the extraction of vertical splice positions."""
    sheets = [{'x': 0, 'y': 0, 'width': 48, 'height': 96}, {'x': 48, 'y': 0, 'width': 48, 'height': 96}]
    splices = extract_vertical_splice_positions(sheets)
    assert splices == [48.0]

def test_calculate_vertical_cleat_positions():
    """Tests the calculation of vertical cleat positions."""
    positions = calculate_vertical_cleat_positions(100, [48], 3.5)
    assert len(positions) > 0

def test_calculate_vertical_cleat_material_needed():
    """Tests the calculation of vertical cleat material needed."""
    material_needed = calculate_vertical_cleat_material_needed(100, 50, 3.5)
    assert material_needed >= 0

def test_update_panel_components_with_splice_cleats():
    """Tests updating panel components with splice cleats."""
    panel_components = {
        'intermediate_vertical_cleats': {},
        'vertical_cleats': {'material_thickness': 1.5}
    }
    updated_components = update_panel_components_with_splice_cleats(panel_components, 100, 50, 3.5)
    assert updated_components is not None

def test_calculate_horizontal_cleat_sections_from_vertical_positions():
    """Tests the calculation of horizontal cleat sections."""
    sections = calculate_horizontal_cleat_sections_from_vertical_positions(100, 3.5, [50], 48)
    assert len(sections) > 0

@patch('tkinter.filedialog.asksaveasfilename', return_value="test.exp")
def test_crate_app_generate_expressions(mock_save, standard_inputs):
    """Tests the generate_expressions method of the CrateApp."""
    root = tk.Tk()
    app = CrateApp(root)
    
    # Mock the UI inputs
    app.weight_entry.insert(0, str(standard_inputs["product_weight_lbs"]))
    app.length_entry.insert(0, str(standard_inputs["product_length_in"]))
    app.width_entry.insert(0, str(standard_inputs["product_width_in"]))
    app.clearance_entry.insert(0, str(standard_inputs["clearance_each_side_in"]))
    app.panel_thickness_entry.insert(0, str(standard_inputs["panel_thickness_in"]))
    app.cleat_thickness_entry.insert(0, str(standard_inputs["cleat_thickness_in"]))
    app.cleat_member_width_entry.insert(0, str(standard_inputs["cleat_member_actual_width_in"]))
    app.product_height_entry.insert(0, str(standard_inputs["product_actual_height_in"]))
    app.clearance_above_entry.insert(0, str(standard_inputs["clearance_above_product_in"]))
    app.ground_clearance_entry.insert(0, str(standard_inputs["ground_clearance_in"]))
    app.floorboard_thickness_entry.insert(0, str(standard_inputs["floorboard_actual_thickness_in"]))
    app.max_gap_entry.insert(0, str(standard_inputs["max_allowable_middle_gap_in"]))
    app.min_custom_entry.insert(0, str(standard_inputs["min_custom_lumber_width_in"]))

    with patch('nx_expressions_generator.generate_crate_expressions_logic', return_value=(True, "Success")) as mock_logic:
        app.generate_expressions()
        mock_logic.assert_called_once()
    root.destroy()
