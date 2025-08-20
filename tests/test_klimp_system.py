"""
Comprehensive test suite for the klimp system in AutoCrate.
Tests positioning, orientation, and NX expression generation for all 30 klimps.
"""

import pytest
import numpy as np
from typing import List, Dict, Tuple
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from autocrate.klimp_placement_logic_all_sides import calculate_all_klimp_placements
from autocrate.klimp_quaternion_integration import (
    calculate_klimp_quaternion_orientations,
    generate_klimp_quaternion_nx_expressions,
    KlimpQuaternionOrientation
)


class TestKlimpPlacement:
    """Test klimp placement calculations."""
    
    def test_all_klimps_generated(self):
        """Test that all 30 klimps are generated with proper placements."""
        # Test dimensions
        panel_width = 100.0
        panel_height = 40.0
        panel_length = 120.0
        panel_thickness = 0.25
        cleat_thickness = 0.75
        cleat_member_width = 1.5
        
        placements = calculate_all_klimp_placements(
            panel_width, panel_height, panel_length,
            panel_thickness, cleat_thickness, cleat_member_width
        )
        
        # Should have exactly 30 klimps
        assert len(placements) == 30
        
        # Check that all klimp IDs are present
        expected_ids = set(range(1, 31))
        actual_ids = {p['id'] for p in placements}
        assert actual_ids == expected_ids
        
        # Each placement should have required fields
        required_fields = {'id', 'x', 'y', 'z', 'panel', 'suppress'}
        for placement in placements:
            assert set(placement.keys()) >= required_fields
    
    def test_top_panel_klimps(self):
        """Test that top panel klimps (1-10) are positioned correctly."""
        panel_width = 100.0
        panel_height = 40.0
        panel_length = 120.0
        panel_thickness = 0.25
        cleat_thickness = 0.75
        cleat_member_width = 1.5
        
        placements = calculate_all_klimp_placements(
            panel_width, panel_height, panel_length,
            panel_thickness, cleat_thickness, cleat_member_width
        )
        
        top_klimps = [p for p in placements if p['panel'] == 'top']
        
        # Should have 10 top klimps
        assert len(top_klimps) == 10
        
        # All top klimps should have Y=0 (on top surface)
        for klimp in top_klimps:
            assert klimp['y'] == 0.0
        
        # Z should be at top of crate
        expected_z = panel_height + panel_thickness + cleat_thickness + cleat_member_width
        for klimp in top_klimps:
            assert abs(klimp['z'] - expected_z) < 0.001
    
    def test_side_panel_klimps(self):
        """Test that side panel klimps are positioned correctly."""
        panel_width = 100.0
        panel_height = 40.0
        panel_length = 120.0
        panel_thickness = 0.25
        cleat_thickness = 0.75
        cleat_member_width = 1.5
        
        placements = calculate_all_klimp_placements(
            panel_width, panel_height, panel_length,
            panel_thickness, cleat_thickness, cleat_member_width
        )
        
        left_klimps = [p for p in placements if p['panel'] == 'left']
        right_klimps = [p for p in placements if p['panel'] == 'right']
        
        # Should have 10 klimps on each side
        assert len(left_klimps) == 10
        assert len(right_klimps) == 10
        
        # Left klimps should be on left edge
        for klimp in left_klimps:
            assert klimp['x'] < 0  # Negative X for left side
        
        # Right klimps should be on right edge
        for klimp in right_klimps:
            assert klimp['x'] > 0  # Positive X for right side


class TestKlimpOrientation:
    """Test klimp orientation calculations."""
    
    def test_quaternion_orientations_generated(self):
        """Test that quaternion orientations are generated for all klimps."""
        placements = [
            {'id': i, 'x': 0, 'y': 0, 'z': 0, 'panel': 'top', 'suppress': 0 if i <= 5 else 1}
            for i in range(1, 31)
        ]
        
        orientations = calculate_klimp_quaternion_orientations(placements)
        
        # Should have 30 orientations
        assert len(orientations) == 30
        
        # Each orientation should be a KlimpQuaternionOrientation
        for orientation in orientations:
            assert isinstance(orientation, KlimpQuaternionOrientation)
            assert hasattr(orientation, 'id')
            assert hasattr(orientation, 'position')
            assert hasattr(orientation, 'quaternion')
            assert hasattr(orientation, 'direction_vectors')
    
    def test_top_panel_orientation(self):
        """Test that top panel klimps have correct orientation."""
        placements = [
            {'id': 1, 'x': 0, 'y': 0, 'z': 40, 'panel': 'top', 'suppress': 0}
        ]
        
        orientations = calculate_klimp_quaternion_orientations(placements)
        orientation = orientations[0]
        
        # Check direction vectors for top panel
        # X-axis should point sideways (1,0,0)
        assert np.allclose(orientation.direction_vectors['x'], [1, 0, 0])
        # Y-axis should point away (0,1,0)
        assert np.allclose(orientation.direction_vectors['y'], [0, 1, 0])
        # Z-axis should point down (0,0,-1) for top panel
        assert np.allclose(orientation.direction_vectors['z'], [0, 0, -1]) or \
               np.allclose(orientation.direction_vectors['z'], [0, 0, 1])
    
    def test_side_panel_orientations(self):
        """Test that side panel klimps have correct orientations."""
        placements = [
            {'id': 11, 'x': -50, 'y': 0, 'z': 20, 'panel': 'left', 'suppress': 0},
            {'id': 21, 'x': 50, 'y': 0, 'z': 20, 'panel': 'right', 'suppress': 0}
        ]
        
        orientations = calculate_klimp_quaternion_orientations(placements)
        
        left_orientation = next(o for o in orientations if o.id == 11)
        right_orientation = next(o for o in orientations if o.id == 21)
        
        # Left panel Z should point up
        assert np.allclose(left_orientation.direction_vectors['z'], [0, 0, 1])
        
        # Right panel Z should also point up
        assert np.allclose(right_orientation.direction_vectors['z'], [0, 0, 1])


class TestKlimpNXExpressions:
    """Test NX expression generation for klimps."""
    
    def test_nx_expressions_generated(self):
        """Test that NX expressions are generated for all klimps."""
        placements = [
            {'id': i, 'x': i*10, 'y': 0, 'z': 40, 'panel': 'top', 'suppress': 0 if i <= 5 else 1}
            for i in range(1, 31)
        ]
        
        orientations = calculate_klimp_quaternion_orientations(placements)
        expressions = generate_klimp_quaternion_nx_expressions(orientations)
        
        # Should generate many expressions
        assert len(expressions) > 0
        
        # Check for required variables for each klimp
        for i in range(1, 31):
            # Position variables
            assert any(f'[Inch]KL_{i}_X' in expr for expr in expressions)
            assert any(f'[Inch]KL_{i}_Y' in expr for expr in expressions)
            assert any(f'[Inch]KL_{i}_Z' in expr for expr in expressions)
            
            # Quaternion variables
            assert any(f'KL_{i}_Q_W' in expr for expr in expressions)
            assert any(f'KL_{i}_Q_X' in expr for expr in expressions)
            assert any(f'KL_{i}_Q_Y' in expr for expr in expressions)
            assert any(f'KL_{i}_Q_Z' in expr for expr in expressions)
            
            # Direction vectors
            assert any(f'KL_{i}_X_DIR_X' in expr for expr in expressions)
            assert any(f'KL_{i}_Y_DIR_X' in expr for expr in expressions)
            assert any(f'KL_{i}_Z_DIR_X' in expr for expr in expressions)
            
            # Suppress flag
            assert any(f'KL_{i}_SUPPRESS' in expr for expr in expressions)
    
    def test_suppress_flags(self):
        """Test that suppress flags are correctly set."""
        placements = []
        for i in range(1, 31):
            suppress = 0 if i <= 5 else 1  # First 5 visible, rest hidden
            placements.append({
                'id': i, 'x': 0, 'y': 0, 'z': 0, 
                'panel': 'top', 'suppress': suppress
            })
        
        orientations = calculate_klimp_quaternion_orientations(placements)
        expressions = generate_klimp_quaternion_nx_expressions(orientations)
        
        # Check suppress flags
        for i in range(1, 6):
            suppress_expr = next(e for e in expressions if f'KL_{i}_SUPPRESS' in e)
            assert '= 0' in suppress_expr  # Should be visible
        
        for i in range(6, 31):
            suppress_expr = next(e for e in expressions if f'KL_{i}_SUPPRESS' in e)
            assert '= 1' in suppress_expr  # Should be hidden
    
    def test_no_unicode_in_expressions(self):
        """Test that generated expressions contain no Unicode characters."""
        placements = [
            {'id': i, 'x': 0, 'y': 0, 'z': 0, 'panel': 'top', 'suppress': 0}
            for i in range(1, 31)
        ]
        
        orientations = calculate_klimp_quaternion_orientations(placements)
        expressions = generate_klimp_quaternion_nx_expressions(orientations)
        
        # Check that all expressions are ASCII-only
        for expr in expressions:
            assert all(ord(c) < 128 for c in expr), f"Unicode found in: {expr}"


class TestKlimpIntegration:
    """Test full integration of klimp system."""
    
    def test_realistic_crate_dimensions(self):
        """Test with realistic crate dimensions."""
        # Typical medium-sized crate
        panel_width = 96.0
        panel_height = 48.0
        panel_length = 120.0
        panel_thickness = 0.25
        cleat_thickness = 0.75
        cleat_member_width = 1.5
        
        # Generate placements
        placements = calculate_all_klimp_placements(
            panel_width, panel_height, panel_length,
            panel_thickness, cleat_thickness, cleat_member_width
        )
        
        # Generate orientations
        orientations = calculate_klimp_quaternion_orientations(placements)
        
        # Generate expressions
        expressions = generate_klimp_quaternion_nx_expressions(orientations)
        
        # Basic validation
        assert len(placements) == 30
        assert len(orientations) == 30
        assert len(expressions) > 500  # Should have many expression lines
        
        # Check KL_1_Z matches expected total height
        expected_height = panel_height + panel_thickness + cleat_thickness + cleat_member_width
        kl_1_z_expr = next(e for e in expressions if '[Inch]KL_1_Z' in e)
        z_value = float(kl_1_z_expr.split('=')[1].split('//')[0].strip())
        assert abs(z_value - expected_height) < 0.001
    
    def test_extreme_dimensions(self):
        """Test with extreme crate dimensions."""
        test_cases = [
            # Very small crate
            (12.0, 12.0, 12.0, 0.25, 0.5, 1.0),
            # Very large crate
            (130.0, 130.0, 130.0, 0.5, 1.0, 2.0),
            # Very tall, thin crate
            (20.0, 100.0, 20.0, 0.25, 0.75, 1.5),
            # Very wide, flat crate
            (130.0, 10.0, 130.0, 0.25, 0.75, 1.5),
        ]
        
        for width, height, length, p_thick, c_thick, c_width in test_cases:
            placements = calculate_all_klimp_placements(
                width, height, length, p_thick, c_thick, c_width
            )
            
            orientations = calculate_klimp_quaternion_orientations(placements)
            expressions = generate_klimp_quaternion_nx_expressions(orientations)
            
            # Should always generate 30 klimps
            assert len(placements) == 30
            assert len(orientations) == 30
            assert len(expressions) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])