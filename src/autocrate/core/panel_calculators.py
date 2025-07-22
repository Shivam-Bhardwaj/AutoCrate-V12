"""
Panel calculation modules for AutoCrate.

This module imports and organizes all panel calculation logic into
a unified interface while preserving the original calculation functions
for NX expressions compatibility.
"""

# Import all the original panel logic modules
import sys
import os
import importlib.util

# Add the root directory to the path to import original modules
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Import original modules from legacy folder
try:
    from legacy.front_panel_logic_unified import calculate_front_panel_components
    from legacy.back_panel_logic import calculate_back_panel_components
    from legacy.left_panel_logic import calculate_left_panel_components
    from legacy.right_panel_logic import calculate_right_panel_components
    from legacy.top_panel_logic import calculate_top_panel_components
    from legacy.end_panel_logic import calculate_end_panel_components
    from legacy.skid_logic import calculate_skid_components
    from legacy.floorboard_logic import calculate_floorboard_components
except ImportError as e:
    # Fallback for development - try relative imports
    import warnings
    warnings.warn(f"Could not import original modules: {e}. Using fallback imports.")


class PanelCalculatorBase:
    """Base class for all panel calculators."""
    
    def __init__(self):
        self.name = self.__class__.__name__
    
    def calculate(self, **kwargs):
        """Calculate panel components. Override in subclasses."""
        raise NotImplementedError("Subclasses must implement calculate method")


class FrontPanelCalculator(PanelCalculatorBase):
    """Front panel calculation logic."""
    
    def calculate(self, **kwargs):
        """Calculate front panel components using unified logic."""
        return calculate_front_panel_components(**kwargs)


class BackPanelCalculator(PanelCalculatorBase):
    """Back panel calculation logic."""
    
    def calculate(self, **kwargs):
        """Calculate back panel components.""" 
        return calculate_back_panel_components(**kwargs)


class LeftPanelCalculator(PanelCalculatorBase):
    """Left panel calculation logic."""
    
    def calculate(self, **kwargs):
        """Calculate left panel components."""
        return calculate_left_panel_components(**kwargs)


class RightPanelCalculator(PanelCalculatorBase):
    """Right panel calculation logic."""
    
    def calculate(self, **kwargs):
        """Calculate right panel components."""
        return calculate_right_panel_components(**kwargs)


class TopPanelCalculator(PanelCalculatorBase):
    """Top panel calculation logic."""
    
    def calculate(self, **kwargs):
        """Calculate top panel components."""
        return calculate_top_panel_components(**kwargs)


class EndPanelCalculator(PanelCalculatorBase):
    """End panel calculation logic."""
    
    def calculate(self, **kwargs):
        """Calculate end panel components."""
        return calculate_end_panel_components(**kwargs)


class SkidCalculator(PanelCalculatorBase):
    """Skid calculation logic."""
    
    def calculate(self, **kwargs):
        """Calculate skid components."""
        return calculate_skid_components(**kwargs)


class FloorboardCalculator(PanelCalculatorBase):
    """Floorboard calculation logic."""
    
    def calculate(self, **kwargs):
        """Calculate floorboard components."""
        return calculate_floorboard_components(**kwargs)