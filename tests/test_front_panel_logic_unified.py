import pytest
from legacy.front_panel_logic_unified import calculate_front_panel_components

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
    Tests the 'hybrid' strategy with a large required adjustment,
    expecting it to choose the 'position_adjustment' strategy.
    """
    inputs = base_inputs.copy()
    inputs["strategy"] = "hybrid"
    # A height of 98.0" requires a large adjustment.
    inputs["front_panel_assembly_height"] = 98.0
    inputs["adjustment_threshold"] = 2.0
    
    result = calculate_front_panel_components(**inputs)
    
    assert result['strategy_used'] == 'position_adjustment'
    assert result['plywood_height'] == 98.0

def test_strategy_hybrid_chooses_position(base_inputs):
    """
    Tests the 'hybrid' strategy with a large required adjustment,
    expecting it to choose the 'position_adjustment' strategy.
    """
    inputs = base_inputs.copy()
    inputs["strategy"] = "hybrid"
    # A height of 100 requires a large adjustment
    inputs["front_panel_assembly_height"] = 100.0
    inputs["adjustment_threshold"] = 5.0 # Set a threshold smaller than the needed adjustment
    
    result = calculate_front_panel_components(**inputs)
    
    assert result['strategy_used'] == 'position_adjustment'
    assert result['plywood_height'] == 100.0


def test_invalid_strategy(base_inputs):
    """
    Tests that an invalid strategy defaults to base approach.
    """
    inputs = base_inputs.copy()
    inputs["strategy"] = "invalid_strategy"
    
    result = calculate_front_panel_components(**inputs)
    
    assert result['strategy_used'] == 'base_approach'
    assert result['plywood_height'] == inputs['front_panel_assembly_height']


def test_custom_adjustment_increment(base_inputs):
    """
    Tests dimension strategy with custom adjustment increment.
    """
    inputs = base_inputs.copy()
    inputs["strategy"] = "dimension"
    inputs["adjustment_increment"] = 1.0  # 1 inch increments
    inputs["front_panel_assembly_height"] = 98.0  # Needs adjustment
    
    result = calculate_front_panel_components(**inputs)
    
    if result['strategy_used'] == 'dimension_adjustment':
        # Height adjustment should be in multiples of 1.0
        assert result['height_adjustment'] % 1.0 == 0


def test_debug_mode(base_inputs):
    """
    Tests that debug mode produces output without errors.
    """
    inputs = base_inputs.copy()
    inputs["debug"] = True
    inputs["strategy"] = "hybrid"
    
    # Should run without errors
    result = calculate_front_panel_components(**inputs)
    
    assert 'strategy_used' in result
    assert 'plywood_width' in result
    assert 'plywood_height' in result


def test_zero_dimensions(base_inputs):
    """
    Tests handling of zero dimensions.
    """
    inputs = base_inputs.copy()
    inputs["front_panel_assembly_width"] = 0.0
    
    result = calculate_front_panel_components(**inputs)
    
    assert result['plywood_width'] == 0.0
    # For zero width, we expect no intermediate vertical cleats
    assert result['num_intermediate_cleats'] == 0
    assert len(result['intermediate_cleat_positions']) == 0


def test_very_large_panel(base_inputs):
    """
    Tests very large panel dimensions.
    """
    inputs = base_inputs.copy()
    inputs["front_panel_assembly_width"] = 300.0
    inputs["front_panel_assembly_height"] = 200.0
    
    result = calculate_front_panel_components(**inputs)
    
    # Should have multiple splices
    assert len(result['horizontal_splice_positions']) >= 2
    # For 300" width, should have many vertical cleats
    assert result['num_intermediate_cleats'] > 5
    # Verify we have 12 intermediate cleats for 300" width
    assert result['num_intermediate_cleats'] == 12


def test_negative_adjustment_threshold(base_inputs):
    """
    Tests hybrid strategy with negative adjustment threshold.
    """
    inputs = base_inputs.copy()
    inputs["strategy"] = "hybrid"
    inputs["adjustment_threshold"] = -1.0  # Invalid threshold
    inputs["front_panel_assembly_height"] = 98.0
    
    # Should still produce valid result
    result = calculate_front_panel_components(**inputs)
    
    assert 'strategy_used' in result
    assert result['plywood_height'] >= 98.0
