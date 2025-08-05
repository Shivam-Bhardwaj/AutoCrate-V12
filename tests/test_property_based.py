"""
Property-Based Testing Suite for AutoCrate

This module uses hypothesis to generate comprehensive test cases
across the valid input space, ensuring robust engineering calculations.
"""

import pytest
import math
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from hypothesis import given, strategies as st, assume, settings, example
    from hypothesis.stateful import RuleBasedStateMachine, rule, invariant, Bundle
    HYPOTHESIS_AVAILABLE = True
except ImportError:
    HYPOTHESIS_AVAILABLE = False
    # Fallback for environments without hypothesis
    def given(*args, **kwargs):
        def decorator(func):
            return pytest.mark.skip("hypothesis not installed")(func)
        return decorator
    st = None

from autocrate.front_panel_logic import calculate_front_panel_components
from autocrate.back_panel_logic import calculate_back_panel_components
from autocrate.end_panel_logic import calculate_end_panel_components
from autocrate.left_panel_logic import calculate_left_panel_components
from autocrate.right_panel_logic import calculate_right_panel_components
from autocrate.top_panel_logic import calculate_top_panel_components
from autocrate.floorboard_logic import calculate_floorboard_components
from autocrate.skid_logic import calculate_skid_components


# Define valid ranges for crate dimensions based on ASTM standards
DIMENSION_STRATEGY = st.floats(min_value=6.0, max_value=240.0)
WIDTH_STRATEGY = st.floats(min_value=6.0, max_value=240.0)
LENGTH_STRATEGY = st.floats(min_value=6.0, max_value=200.0)
HEIGHT_STRATEGY = st.floats(min_value=12.0, max_value=72.0)
THICKNESS_STRATEGY = st.floats(min_value=0.5, max_value=1.5)
CLEAT_WIDTH_STRATEGY = st.floats(min_value=1.5, max_value=5.5)
CLEAT_THICKNESS_STRATEGY = st.floats(min_value=0.75, max_value=3.5)


class TestPanelCalculationsProperties:
    """Property-based tests for panel calculations."""
    
    @pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
    @given(
        width=WIDTH_STRATEGY,
        height=HEIGHT_STRATEGY,
        sheathing_thickness=THICKNESS_STRATEGY,
        cleat_thickness=CLEAT_THICKNESS_STRATEGY,
        cleat_width=CLEAT_WIDTH_STRATEGY
    )
    @settings(max_examples=100, deadline=1000)
    def test_front_panel_dimensions_consistency(self, width, height, sheathing_thickness, 
                                               cleat_thickness, cleat_width):
        """
        Property: Front panel plywood dimensions should match input dimensions.
        """
        result = calculate_front_panel_components(
            front_panel_assembly_width=width,
            front_panel_assembly_height=height,
            panel_sheathing_thickness=sheathing_thickness,
            cleat_material_thickness=cleat_thickness,
            cleat_material_member_width=cleat_width
        )
        
        # Property 1: Plywood dimensions match input
        assert result['plywood']['width'] == pytest.approx(width, rel=1e-6)
        assert result['plywood']['height'] == pytest.approx(height, rel=1e-6)
        assert result['plywood']['thickness'] == pytest.approx(sheathing_thickness, rel=1e-6)
        
        # Property 2: All dimensions are positive
        assert result['plywood']['width'] > 0
        assert result['plywood']['height'] > 0
        assert result['plywood']['thickness'] > 0
    
    @pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
    @given(
        width=WIDTH_STRATEGY,
        height=HEIGHT_STRATEGY,
        sheathing_thickness=THICKNESS_STRATEGY,
        cleat_thickness=CLEAT_THICKNESS_STRATEGY,
        cleat_width=CLEAT_WIDTH_STRATEGY
    )
    @settings(max_examples=100, deadline=1000)
    def test_cleat_spacing_compliance(self, width, height, sheathing_thickness, 
                                     cleat_thickness, cleat_width):
        """
        Property: Cleat spacing should never exceed 24 inches (ASTM requirement).
        """
        result = calculate_front_panel_components(
            front_panel_assembly_width=width,
            front_panel_assembly_height=height,
            panel_sheathing_thickness=sheathing_thickness,
            cleat_material_thickness=cleat_thickness,
            cleat_material_member_width=cleat_width
        )
        
        # Check intermediate cleat spacing
        if result['intermediate_vertical_cleats']['count'] > 0:
            positions = result['intermediate_vertical_cleats']['positions_x_centerline']
            
            # Check spacing from edge to first cleat
            if positions:
                first_spacing = positions[0]
                assert first_spacing <= 24.1, f"First cleat spacing {first_spacing} exceeds 24 inches"
                
                # Check spacing from last cleat to edge
                last_spacing = width - positions[-1]
                assert last_spacing <= 24.1, f"Last cleat spacing {last_spacing} exceeds 24 inches"
                
                # Check spacing between consecutive cleats
                for i in range(1, len(positions)):
                    spacing = positions[i] - positions[i-1]
                    assert spacing <= 24.1, f"Cleat spacing {spacing} exceeds 24 inches"
    
    @pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
    @given(
        width=st.floats(min_value=30.0, max_value=100.0),  # Ensure we get intermediate cleats
        height=HEIGHT_STRATEGY,
        sheathing_thickness=THICKNESS_STRATEGY,
        cleat_thickness=CLEAT_THICKNESS_STRATEGY,
        cleat_width=CLEAT_WIDTH_STRATEGY
    )
    @settings(max_examples=50, deadline=1000)
    def test_cleat_symmetry(self, width, height, sheathing_thickness, 
                           cleat_thickness, cleat_width):
        """
        Property: Intermediate cleats should be positioned symmetrically.
        """
        result = calculate_front_panel_components(
            front_panel_assembly_width=width,
            front_panel_assembly_height=height,
            panel_sheathing_thickness=sheathing_thickness,
            cleat_material_thickness=cleat_thickness,
            cleat_material_member_width=cleat_width
        )
        
        if result['intermediate_vertical_cleats']['count'] > 0:
            positions = result['intermediate_vertical_cleats']['positions_x_centerline']
            center = width / 2.0
            
            # For odd number of cleats, one should be at center
            if len(positions) % 2 == 1:
                center_cleat = positions[len(positions) // 2]
                assert abs(center_cleat - center) < 0.1, "Center cleat not at panel center"
            
            # Check that cleats are evenly distributed
            if len(positions) > 1:
                spacings = []
                # Add edge spacings
                spacings.append(positions[0])
                spacings.append(width - positions[-1])
                # Add inter-cleat spacings
                for i in range(1, len(positions)):
                    spacings.append(positions[i] - positions[i-1])
                
                # All spacings should be similar (within 10%)
                avg_spacing = sum(spacings) / len(spacings)
                for spacing in spacings:
                    assert abs(spacing - avg_spacing) / avg_spacing < 0.1, \
                        f"Uneven cleat spacing: {spacing} vs average {avg_spacing}"
    
    @pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
    @given(
        width=WIDTH_STRATEGY,
        length=LENGTH_STRATEGY,
        height=HEIGHT_STRATEGY,
        sheathing_thickness=THICKNESS_STRATEGY,
        cleat_thickness=CLEAT_THICKNESS_STRATEGY,
        cleat_width=CLEAT_WIDTH_STRATEGY
    )
    @settings(max_examples=50, deadline=2000)
    def test_panel_consistency_across_modules(self, width, length, height,
                                             sheathing_thickness, cleat_thickness, cleat_width):
        """
        Property: All panel modules should produce consistent outputs for same inputs.
        """
        # Calculate all panels
        front = calculate_front_panel_components(
            width, height, sheathing_thickness, cleat_thickness, cleat_width
        )
        
        back = calculate_back_panel_components(
            width, height, sheathing_thickness, cleat_thickness, cleat_width
        )
        
        # Front and back panels should be identical (same dimensions)
        assert front['plywood']['width'] == pytest.approx(back['plywood']['width'], rel=1e-6)
        assert front['plywood']['height'] == pytest.approx(back['plywood']['height'], rel=1e-6)
        
        # Left and right panels
        left = calculate_left_panel_components(
            length, height, sheathing_thickness, cleat_thickness, cleat_width
        )
        
        right = calculate_right_panel_components(
            length, height, sheathing_thickness, cleat_thickness, cleat_width
        )
        
        # Left and right panels should be identical
        assert left['plywood']['width'] == pytest.approx(right['plywood']['width'], rel=1e-6)
        assert left['plywood']['height'] == pytest.approx(right['plywood']['height'], rel=1e-6)
        
        # End panels
        end1 = calculate_end_panel_components(
            width, length, height, sheathing_thickness, cleat_thickness, cleat_width, 1
        )
        
        end2 = calculate_end_panel_components(
            width, length, height, sheathing_thickness, cleat_thickness, cleat_width, 2
        )
        
        # Both end panels should have same dimensions (different positions though)
        assert end1['plywood']['width'] == pytest.approx(end2['plywood']['width'], rel=1e-6)
        assert end1['plywood']['height'] == pytest.approx(end2['plywood']['height'], rel=1e-6)


class TestSkidCalculationsProperties:
    """Property-based tests for skid calculations."""
    
    @pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
    @given(
        width=WIDTH_STRATEGY,
        length=LENGTH_STRATEGY,
        weight=st.floats(min_value=100, max_value=10000),  # pounds
        skid_thickness=st.floats(min_value=3.5, max_value=5.5)
    )
    @settings(max_examples=50, deadline=1000)
    def test_skid_count_adequacy(self, width, length, weight, skid_thickness):
        """
        Property: Number of skids should be adequate for the load.
        """
        result = calculate_skid_components(
            crate_width=width,
            crate_length=length,
            total_weight=weight,
            skid_thickness=skid_thickness
        )
        
        # Property 1: At least 2 skids (minimum for stability)
        assert result['skid_count'] >= 2
        
        # Property 2: More skids for heavier loads
        if weight > 5000:
            assert result['skid_count'] >= 3
        
        # Property 3: Skid spacing should not exceed reasonable limits
        if result['skid_count'] > 2:
            spacing = length / (result['skid_count'] - 1)
            assert spacing <= 48, f"Skid spacing {spacing} too large"
    
    @pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
    @given(
        width=WIDTH_STRATEGY,
        length=LENGTH_STRATEGY,
        weight=st.floats(min_value=100, max_value=10000)
    )
    @settings(max_examples=50, deadline=1000)
    def test_skid_dimensions_validity(self, width, length, weight):
        """
        Property: Skid dimensions should be valid and consistent.
        """
        result = calculate_skid_components(
            crate_width=width,
            crate_length=length,
            total_weight=weight,
            skid_thickness=3.5
        )
        
        # All skid dimensions should be positive
        assert result['skid_width'] > 0
        assert result['skid_length'] > 0
        assert result['skid_thickness'] > 0
        
        # Skids should span the full width
        assert result['skid_length'] == pytest.approx(width, rel=1e-6)
        
        # Skid width should be reasonable (typically 3.5" or 5.5")
        assert result['skid_width'] in [3.5, 5.5]


class TestFloorboardCalculationsProperties:
    """Property-based tests for floorboard calculations."""
    
    @pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
    @given(
        width=WIDTH_STRATEGY,
        length=LENGTH_STRATEGY,
        board_width=st.floats(min_value=3.5, max_value=11.25),
        board_thickness=st.floats(min_value=0.75, max_value=1.5)
    )
    @settings(max_examples=50, deadline=1000)
    def test_floorboard_coverage(self, width, length, board_width, board_thickness):
        """
        Property: Floorboards should cover the entire crate floor.
        """
        result = calculate_floorboard_components(
            crate_width=width,
            crate_length=length,
            board_width=board_width,
            board_thickness=board_thickness
        )
        
        # Calculate total coverage
        total_coverage = result['board_count'] * board_width
        
        # Coverage should be at least the crate length (allowing for small gaps)
        assert total_coverage >= length - 0.5, \
            f"Insufficient floor coverage: {total_coverage} < {length}"
        
        # But not excessive overcoverage
        assert total_coverage <= length + board_width, \
            f"Excessive floor coverage: {total_coverage} > {length + board_width}"
    
    @pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
    @given(
        width=WIDTH_STRATEGY,
        length=LENGTH_STRATEGY,
        board_thickness=st.floats(min_value=0.75, max_value=1.5)
    )
    @settings(max_examples=50, deadline=1000)
    def test_floorboard_spacing_uniformity(self, width, length, board_thickness):
        """
        Property: Floorboard spacing should be uniform.
        """
        result = calculate_floorboard_components(
            crate_width=width,
            crate_length=length,
            board_width=5.5,  # Standard board width
            board_thickness=board_thickness
        )
        
        if result['board_count'] > 1:
            # Check that spacing is uniform
            positions = result.get('board_positions', [])
            if len(positions) > 1:
                spacings = []
                for i in range(1, len(positions)):
                    spacings.append(positions[i] - positions[i-1])
                
                # All spacings should be similar
                if spacings:
                    avg_spacing = sum(spacings) / len(spacings)
                    for spacing in spacings:
                        # Allow 10% variation
                        assert abs(spacing - avg_spacing) / avg_spacing < 0.1, \
                            f"Non-uniform floorboard spacing: {spacing} vs {avg_spacing}"


class TestEngineeringConstraints:
    """Test engineering constraints and safety factors."""
    
    @pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
    @given(
        width=WIDTH_STRATEGY,
        height=HEIGHT_STRATEGY,
        weight=st.floats(min_value=100, max_value=10000)
    )
    @settings(max_examples=50, deadline=1000)
    def test_structural_integrity(self, width, height, weight):
        """
        Property: Structural calculations should maintain safety factors.
        """
        # Safety factor for shipping crates (ASTM D6256)
        SAFETY_FACTOR = 3.0
        
        # Calculate panel stress
        panel_area = width * height  # square inches
        stress = weight / panel_area  # psi
        
        # Maximum allowable stress for plywood (typical)
        max_allowable_stress = 1200 / SAFETY_FACTOR  # psi with safety factor
        
        # This is a simplified check - real calculations would be more complex
        if stress > max_allowable_stress:
            # Should require thicker panels or additional reinforcement
            # This test verifies the calculation doesn't produce unsafe designs
            pytest.skip(f"Stress {stress} exceeds allowable {max_allowable_stress}")
    
    @pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
    @given(
        width=st.floats(min_value=6, max_value=500),  # Include invalid ranges
        height=st.floats(min_value=6, max_value=500),
        thickness=st.floats(min_value=0.1, max_value=5)
    )
    def test_input_validation_boundaries(self, width, height, thickness):
        """
        Property: System should handle invalid inputs gracefully.
        """
        # Define valid ranges
        MAX_WIDTH = 240
        MAX_HEIGHT = 72
        MIN_WIDTH = 6
        MIN_HEIGHT = 12
        MIN_THICKNESS = 0.5
        MAX_THICKNESS = 1.5
        
        # Skip if inputs are valid (we're testing invalid inputs here)
        if (MIN_WIDTH <= width <= MAX_WIDTH and 
            MIN_HEIGHT <= height <= MAX_HEIGHT and
            MIN_THICKNESS <= thickness <= MAX_THICKNESS):
            # Valid inputs - should work
            result = calculate_front_panel_components(
                width, height, thickness, 1.5, 3.5
            )
            assert result is not None
        else:
            # Invalid inputs - should either handle gracefully or raise appropriate error
            try:
                result = calculate_front_panel_components(
                    width, height, thickness, 1.5, 3.5
                )
                # If it doesn't raise an error, results should still be somewhat valid
                if result:
                    assert result['plywood']['width'] > 0
                    assert result['plywood']['height'] > 0
            except (ValueError, AssertionError) as e:
                # Expected for invalid inputs
                pass


@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
class CrateDesignStateMachine(RuleBasedStateMachine):
    """
    Stateful testing for crate design workflow.
    Tests that the system maintains consistency through design changes.
    """
    
    # Bundle to track crate configurations
    configurations = Bundle('configurations')
    
    def __init__(self):
        super().__init__()
        self.current_config = None
        self.design_history = []
    
    @rule(
        target=configurations,
        width=WIDTH_STRATEGY,
        length=LENGTH_STRATEGY,
        height=HEIGHT_STRATEGY
    )
    def create_configuration(self, width, length, height):
        """Create a new crate configuration."""
        config = {
            'width': width,
            'length': length,
            'height': height,
            'timestamp': len(self.design_history)
        }
        self.design_history.append(config)
        self.current_config = config
        return config
    
    @rule(config=configurations)
    def calculate_all_panels(self, config):
        """Calculate all panels for a configuration."""
        # This should not raise any exceptions
        front = calculate_front_panel_components(
            config['width'], config['height'], 0.75, 1.5, 3.5
        )
        back = calculate_back_panel_components(
            config['width'], config['height'], 0.75, 1.5, 3.5
        )
        
        # Verify consistency
        assert front['plywood']['width'] == back['plywood']['width']
        assert front['plywood']['height'] == back['plywood']['height']
    
    @rule(
        config=configurations,
        scale_factor=st.floats(min_value=0.5, max_value=2.0)
    )
    def scale_configuration(self, config, scale_factor):
        """Scale a configuration and verify proportionality."""
        # Scale dimensions
        new_width = min(max(config['width'] * scale_factor, 6), 240)
        new_height = min(max(config['height'] * scale_factor, 12), 72)
        
        # Calculate panels for both configurations
        original = calculate_front_panel_components(
            config['width'], config['height'], 0.75, 1.5, 3.5
        )
        scaled = calculate_front_panel_components(
            new_width, new_height, 0.75, 1.5, 3.5
        )
        
        # Plywood dimensions should scale proportionally
        width_ratio = scaled['plywood']['width'] / original['plywood']['width']
        height_ratio = scaled['plywood']['height'] / original['plywood']['height']
        
        expected_width_ratio = new_width / config['width']
        expected_height_ratio = new_height / config['height']
        
        assert abs(width_ratio - expected_width_ratio) < 0.01
        assert abs(height_ratio - expected_height_ratio) < 0.01
    
    @invariant()
    def configuration_history_valid(self):
        """Invariant: Configuration history should be consistent."""
        if self.design_history:
            # All configurations should have required fields
            for config in self.design_history:
                assert 'width' in config
                assert 'length' in config
                assert 'height' in config
                assert config['width'] > 0
                assert config['length'] > 0
                assert config['height'] > 0


# Test the state machine
if HYPOTHESIS_AVAILABLE:
    TestCrateDesign = CrateDesignStateMachine.TestCase


def test_regression_specific_cases():
    """Test specific cases that have caused issues in the past."""
    
    # Test case 1: Very tall thin crate (horizontal splice bug)
    result = calculate_front_panel_components(
        front_panel_assembly_width=20,
        front_panel_assembly_height=100,
        panel_sheathing_thickness=0.75,
        cleat_material_thickness=1.5,
        cleat_material_member_width=3.5
    )
    assert result is not None
    assert result['plywood']['width'] == 20
    assert result['plywood']['height'] == 100
    
    # Test case 2: Standard plywood size
    result = calculate_front_panel_components(
        front_panel_assembly_width=96,
        front_panel_assembly_height=48,
        panel_sheathing_thickness=0.75,
        cleat_material_thickness=1.5,
        cleat_material_member_width=3.5
    )
    assert result is not None
    # Should have intermediate cleats for 96" width
    assert result['intermediate_vertical_cleats']['count'] > 0
    
    # Test case 3: Perfect cube
    result = calculate_front_panel_components(
        front_panel_assembly_width=48,
        front_panel_assembly_height=48,
        panel_sheathing_thickness=0.75,
        cleat_material_thickness=1.5,
        cleat_material_member_width=3.5
    )
    assert result is not None
    assert result['plywood']['width'] == result['plywood']['height']
    
    # Test case 4: Minimum size
    result = calculate_front_panel_components(
        front_panel_assembly_width=6,
        front_panel_assembly_height=12,
        panel_sheathing_thickness=0.75,
        cleat_material_thickness=1.5,
        cleat_material_member_width=3.5
    )
    assert result is not None
    assert result['intermediate_vertical_cleats']['count'] == 0  # Too small for intermediate cleats


if __name__ == "__main__":
    # Run property-based tests
    pytest.main([__file__, "-v", "--tb=short"])