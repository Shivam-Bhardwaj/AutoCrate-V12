import pytest
from front_panel_logic_unified import (
    calculate_front_panel_components,
    _calculate_base_components,
    _filter_splice_positions,
    _adjust_cleat_positions_for_clearance,
    calculate_horizontal_cleat_sections,
    calculate_front_panel_components_hybrid,
    calculate_front_panel_components_with_dimension_adjustment,
    calculate_required_panel_height_for_splice_coverage
)
from unittest.mock import patch

# Define standard inputs for the tests
WIDTH = 100.0
HEIGHT = 100.0  # This height will cause splices
SHEATHING_THICK = 0.75
CLEAT_THICK = 1.5
CLEAT_WIDTH = 3.5

@pytest.fixture
def base_inputs():
    """Provides a base set of inputs for the unified front panel logic."""
    return {
        "front_panel_assembly_width": WIDTH,
        "front_panel_assembly_height": HEIGHT,
        "panel_sheathing_thickness": SHEATHING_THICK,
        "cleat_material_thickness": CLEAT_THICK,
        "cleat_material_member_width": CLEAT_WIDTH,
        "debug": False
    }

def test_dimension_adjustment_is_applied(base_inputs):
    """
    Tests that the 'dimension' strategy applies an adjustment when a splice
    is just outside the bottom cleat's coverage.
    """
    inputs = base_inputs.copy()
    inputs["strategy"] = "dimension"
    # A height of 98.0" creates a splice at y=96.0".
    inputs['front_panel_assembly_height'] = 98.0
    
    result = calculate_front_panel_components(**inputs)
    
    assert result['original_height'] == 98.0
    assert result['strategy_used'] == 'dimension_adjustment'
    assert result['height_adjustment'] > 0
    assert result['plywood_height'] > 98.0


def test_strategy_position_adjustment(base_inputs):
    """
    Tests the 'position' (base) strategy, expecting no dimension adjustment.
    """
    inputs = base_inputs.copy()
    inputs["strategy"] = "position"
    
    result = calculate_front_panel_components(**inputs)
    
    assert result['strategy_used'] == 'base_approach'
    assert result['plywood_height'] == HEIGHT
    assert result.get('height_adjustment', 0.0) == 0.0

def test_strategy_hybrid_chooses_dimension(base_inputs):
    """
    Tests the 'hybrid' strategy with a small required adjustment,
    expecting it to choose the 'dimension_adjustment' strategy.
    """
    inputs = base_inputs.copy()
    inputs["strategy"] = "hybrid"
    # A height of 97.0" creates a splice at y=96.0".
    # This requires an adjustment of 96.0 - 3.5 = 92.5, which is large.
    # To test the dimension adjustment, we need a small adjustment.
    # Let's set the height so the splice is just outside the cleat.
    inputs["front_panel_assembly_height"] = 99.0
    inputs["adjustment_threshold"] = 95.0 # A large threshold
    
    result = calculate_front_panel_components(**inputs)
    
    assert result['strategy_used'] == 'dimension_adjustment'
    assert result['plywood_height'] > 99.0

def test_strategy_hybrid_chooses_position(base_inputs):
    """
    Tests the 'hybrid' strategy with a large required adjustment,
    expecting it to choose the 'position_adjustment' strategy.
    """
    inputs = base_inputs.copy()
    inputs["strategy"] = "hybrid"
    # A height of 100 requires a large adjustment
    inputs["front_panel_assembly_height"] = 100.0
    inputs["adjustment_threshold"] = 0.1 # Set a threshold smaller than the needed adjustment
    
    result = calculate_front_panel_components(**inputs)
    
    assert result['strategy_used'] == 'position_adjustment'
    assert result['plywood_height'] == 100.0

def test_base_approach_cleat_calculation(base_inputs):
    """
    Tests the base approach to ensure correct cleat calculation.
    """
    inputs = base_inputs.copy()
    inputs["strategy"] = "position"
    result = calculate_front_panel_components(**inputs)
    assert result['num_intermediate_cleats'] > 0
    assert len(result['intermediate_cleat_positions']) == result['num_intermediate_cleats']

def test_dimension_adjustment_no_adjustment_needed(base_inputs):
    """
    Tests that no dimension adjustment is applied when not needed.
    """
    inputs = base_inputs.copy()
    inputs["strategy"] = "dimension"
    inputs["front_panel_assembly_height"] = 90.0 # No splices, no adjustment
    result = calculate_front_panel_components(**inputs)
    assert result['height_adjustment'] == 0.0

def test_filter_splice_positions():
    """
    Tests the filtering of splice positions covered by edge cleats.
    """
    splice_positions = [3.0, 50.0, 93.0] # Bottom, middle, top
    filtered = _filter_splice_positions(splice_positions, 3.5, 96.0)
    assert filtered == [50.0]

def test_adjust_cleat_positions_for_clearance():
    """
    Tests the adjustment of cleat positions for minimum clearance.
    """
    positions = [3.6, 92.4] # Too close to top and bottom
    adjusted = _adjust_cleat_positions_for_clearance(positions, 3.5, 96.0, 0.25)
    assert adjusted[0] == 3.75
    assert adjusted[1] == 92.25

def test_calculate_horizontal_cleat_sections():
    """
    Tests the calculation of horizontal cleat sections.
    """
    sections = calculate_horizontal_cleat_sections([48, 96], [50], 100)
    assert len(sections) == 4 # 2 splices * 2 sections

def test_legacy_hybrid_wrapper(base_inputs):
    """
    Tests the legacy hybrid wrapper function.
    """
    inputs = base_inputs.copy()
    del inputs['debug']
    result = calculate_front_panel_components_hybrid(**inputs)
    assert result is not None
    assert 'strategy_used' in result

def test_legacy_dimension_adjustment_wrapper(base_inputs):
    """
    Tests the legacy dimension adjustment wrapper function.
    """
    inputs = base_inputs.copy()
    del inputs['debug']
    result = calculate_front_panel_components_with_dimension_adjustment(**inputs)
    assert result is not None
    assert 'strategy_used' in result

def test_calculate_required_panel_height_for_splice_coverage():
    """
    Tests the calculation of required panel height for splice coverage.
    """
    # Test with no splices
    assert calculate_required_panel_height_for_splice_coverage([], 3.5, 100) == 0.0
    # Test with top splice
    assert calculate_required_panel_height_for_splice_coverage([98], 3.5, 100) > 0.0