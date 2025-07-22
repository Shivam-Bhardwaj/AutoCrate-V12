"""
Legacy AutoCrate modules for backward compatibility.

This package contains the original AutoCrate calculation modules that were
part of the prototype version. These modules are preserved to:

1. Maintain backward compatibility with existing tests
2. Support gradual migration to the new architecture
3. Serve as reference implementations

All new development should use the modules in src/autocrate/ instead.
"""

# Import all legacy modules for easy access
from . import back_panel_logic
from . import end_panel_logic
from . import floorboard_logic
from . import front_panel_logic
from . import front_panel_logic_unified
from . import left_panel_logic
from . import nx_expressions_generator
from . import plywood_layout_generator
from . import right_panel_logic
from . import skid_logic
from . import top_panel_logic

__all__ = [
    'back_panel_logic',
    'end_panel_logic', 
    'floorboard_logic',
    'front_panel_logic',
    'front_panel_logic_unified',
    'left_panel_logic',
    'nx_expressions_generator',
    'plywood_layout_generator',
    'right_panel_logic',
    'skid_logic',
    'top_panel_logic',
]