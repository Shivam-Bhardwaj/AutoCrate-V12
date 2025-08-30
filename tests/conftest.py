"""
Test configuration and fixtures for AutoCrate V12 testing suite.
Provides common test fixtures and utilities for all test modules.
"""

import pytest
import sys
import os
import tempfile
import json
import logging
from pathlib import Path
from typing import Dict, Any, Generator
from unittest.mock import Mock, MagicMock

# Add autocrate to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "autocrate"))

@pytest.fixture(scope="session")
def project_root_path():
    """Return the project root directory path."""
    return Path(__file__).parent.parent

@pytest.fixture(scope="session")
def test_data_dir(project_root_path):
    """Create and return test data directory."""
    test_data = project_root_path / "tests" / "data"
    test_data.mkdir(parents=True, exist_ok=True)
    return test_data

@pytest.fixture
def temp_output_dir():
    """Create temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)

@pytest.fixture
def sample_crate_specs():
    """Standard crate specifications for testing."""
    return {
        "product_length": 96.0,
        "product_width": 48.0, 
        "product_height": 30.0,
        "product_weight": 1000.0,
        "clearance_all_sides": 2.0,
        "clearance_above": 4.0,
        "ground_clearance": 4.0,
        "panel_thickness": 0.75,
        "cleat_thickness": 1.5,
        "cleat_width": 3.5,
        "skid_height": 4.0,
        "floorboard_thickness": 1.5
    }

@pytest.fixture
def expected_results():
    """Expected calculation results for sample specs."""
    return {
        "overall_length_od": 105.0,
        "overall_width_od": 56.5,
        "overall_height_od": 43.5,
        "front_panel_width": 56.5,
        "front_panel_height": 33.5,
        "end_panel_length": 100.5,
        "end_panel_height": 33.5
    }

@pytest.fixture
def mock_logger():
    """Mock logger for testing without actual logging."""
    logger = MagicMock()
    logger.info = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    logger.debug = Mock()
    return logger

@pytest.fixture
def edge_case_specs():
    """Edge case specifications for boundary testing."""
    return [
        # Minimum size crate
        {
            "product_length": 12.0,
            "product_width": 6.0,
            "product_height": 6.0,
            "product_weight": 10.0,
            "clearance_all_sides": 1.0,
            "panel_thickness": 0.5,
            "cleat_thickness": 1.5,
            "cleat_width": 2.5
        },
        # Large crate requiring extra cleats
        {
            "product_length": 192.0,
            "product_width": 96.0, 
            "product_height": 60.0,
            "product_weight": 5000.0,
            "clearance_all_sides": 3.0,
            "panel_thickness": 1.0,
            "cleat_thickness": 2.0,
            "cleat_width": 4.0
        },
        # Unusual dimensions
        {
            "product_length": 73.5,
            "product_width": 25.75,
            "product_height": 18.25,
            "product_weight": 275.0,
            "clearance_all_sides": 1.5,
            "panel_thickness": 0.625,
            "cleat_thickness": 1.25,
            "cleat_width": 3.25
        }
    ]

@pytest.fixture
def performance_baseline():
    """Performance baseline for regression testing."""
    return {
        "max_calculation_time_ms": 500,
        "max_memory_mb": 50,
        "max_expression_size_kb": 20
    }

class TestHelper:
    """Helper class for common test operations."""
    
    @staticmethod
    def validate_nx_expression(expression_content: str) -> bool:
        """Validate NX expression format and content."""
        if not expression_content:
            return False
        
        required_sections = [
            "Overall_Length_OD=",
            "Overall_Width_OD=", 
            "Overall_Height_OD=",
            "Front_Panel_Width=",
            "End_Panel_Length="
        ]
        
        for section in required_sections:
            if section not in expression_content:
                return False
        
        # Check for numeric values
        import re
        numeric_pattern = r'=\s*\d+\.?\d*'
        matches = re.findall(numeric_pattern, expression_content)
        
        return len(matches) >= 10  # Should have at least 10 numeric assignments
    
    @staticmethod
    def compare_calculations(desktop_result: Dict[str, Any], 
                           web_result: Dict[str, Any], 
                           tolerance: float = 0.01) -> bool:
        """Compare desktop and web calculation results within tolerance."""
        
        key_dimensions = [
            "overall_length_od", "overall_width_od", "overall_height_od",
            "front_panel_width", "front_panel_height",
            "end_panel_length", "end_panel_height"
        ]
        
        for key in key_dimensions:
            desktop_val = desktop_result.get(key, 0)
            web_val = web_result.get(key, 0)
            
            if abs(desktop_val - web_val) > tolerance:
                return False
        
        return True
    
    @staticmethod
    def generate_test_report(test_results: Dict[str, Any], 
                           output_file: Path) -> None:
        """Generate comprehensive test report."""
        report = {
            "test_summary": test_results,
            "timestamp": "2024-08-29T12:00:00Z",
            "environment": {
                "python_version": sys.version,
                "platform": sys.platform,
                "working_directory": str(Path.cwd())
            }
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)

@pytest.fixture
def test_helper():
    """Provide TestHelper instance for tests."""
    return TestHelper()

# Performance monitoring decorator
def performance_test(max_time_ms: int = 1000):
    """Decorator to monitor test performance."""
    def decorator(test_func):
        def wrapper(*args, **kwargs):
            import time
            start_time = time.time()
            result = test_func(*args, **kwargs)
            end_time = time.time()
            
            execution_time_ms = (end_time - start_time) * 1000
            if execution_time_ms > max_time_ms:
                pytest.fail(f"Test {test_func.__name__} exceeded {max_time_ms}ms "
                          f"(took {execution_time_ms:.2f}ms)")
            
            return result
        return wrapper
    return decorator

# Custom markers for test categorization
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "performance: Performance tests")
    config.addinivalue_line("markers", "security: Security tests")
    config.addinivalue_line("markers", "slow: Tests that take more than 1 second")

@pytest.fixture(autouse=True)
def setup_test_logging(caplog):
    """Configure logging for tests."""
    caplog.set_level(logging.INFO)
    
# Mock GUI components for headless testing
@pytest.fixture
def mock_tkinter():
    """Mock Tkinter components for GUI testing."""
    mock_tk = MagicMock()
    mock_tk.Tk.return_value = MagicMock()
    mock_tk.StringVar.return_value = MagicMock()
    mock_tk.DoubleVar.return_value = MagicMock()
    
    with pytest.MonkeyPatch().context() as m:
        m.setattr("tkinter.Tk", mock_tk.Tk)
        m.setattr("tkinter.StringVar", mock_tk.StringVar)
        m.setattr("tkinter.DoubleVar", mock_tk.DoubleVar)
        yield mock_tk