# AutoCrate Changelog

## [12.0.3] - 2025-07-31

### Fixed
- **Horizontal Splice Cleat Bug**: Fixed critical issue where horizontal plywood splices were not getting proper cleat support when panels had no intermediate vertical cleats. This occurred with unusual product dimensions (e.g., 20x20x100 - very tall but thin products). The fix ensures all horizontal splices receive structural support per ASTM requirements, regardless of vertical cleat configuration.
  - Modified `calculate_horizontal_cleat_sections` to create cleat sections even when no intermediate vertical cleats exist
  - Updated conditional logic in `nx_expressions_generator.py` to properly trigger horizontal cleat recalculation
  - Applied fix across all panel types (Front, Back, Left, Right, Top)

## [12.0.2] - Previous Release
- Major refactor and cleanup