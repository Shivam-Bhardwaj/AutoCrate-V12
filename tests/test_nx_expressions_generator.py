import pytest
import os
from autocrate.nx_expressions_generator import generate_crate_expressions_logic

# A helper function to parse the generated .exp file
def parse_exp_file(filepath):
    """Parses an NX expression file and returns a dictionary of key-value pairs."""
    values = {}
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('//'):
                # Store comments with a unique key if needed, e.g., by line number
                # For this test, we'll just grab the skid callout specifically
                if "Skid Lumber Callout:" in line:
                    values["// Skid Lumber Callout:"] = line.split(':')[1].strip()
            elif '=' in line:
                # Handle comments on the same line
                if '//' in line:
                    line = line.split('//')[0].strip()
                
                key, value = line.split('=', 1)
                key = key.strip()
                # Try to convert value to a number, otherwise keep as string
                try:
                    values[key] = float(value.strip())
                except ValueError:
                    values[key] = value.strip()
    return values

@pytest.fixture
def standard_inputs():
    """Provides a standard set of inputs for testing the main logic."""
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
        "plywood_panel_selections": {"FP": True, "BP": True, "LP": True, "RP": True, "TP": True}
    }

def test_generate_crate_expressions_logic_integration(standard_inputs):
    """
    An integration test for the main logic function. It generates an expression file
    and verifies several key calculated values.
    """
    output_filename = "test_crate_output.exp"
    standard_inputs["output_filename"] = output_filename
    
    success, message = generate_crate_expressions_logic(**standard_inputs)
    
    assert success is True, f"Logic generation failed with message: {message}"
    assert os.path.exists(output_filename), "Output file was not created."
    
    # Parse the output file and check key values
    exp_values = parse_exp_file(output_filename)
    
    # Check final crate dimensions
    assert exp_values.get("[Inch]crate_overall_width_OD") == pytest.approx(104.0)
    assert exp_values.get("[Inch]crate_overall_length_OD") == pytest.approx(107.0)
    
    # Check skid calculations
    assert exp_values.get("CALC_Skid_Count") == 5
    assert exp_values.get("// Skid Lumber Callout:") == "4x6"
    
    # Check floorboard calculations (count active instances)
    active_floorboards = sum(1 for k, v in exp_values.items() if k.startswith('FB_Inst_') and k.endswith('_Suppress_Flag') and v == 1)
    assert active_floorboards == 10
    
    # Check front panel intermediate cleat count
    assert exp_values.get("FP_Intermediate_Vertical_Cleat_Count") == 4
    
    # Check if plywood layout data is present
    assert "FP_Plywood_1_Active" in exp_values
    
    # Clean up the generated file
    os.remove(output_filename)
