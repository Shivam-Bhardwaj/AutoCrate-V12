# AutoCrate Changelog

## [12.0.4] - 2025-07-31

### Fixed
- **Expressions File Location**: Fixed issue where .exp files were being saved to temp folder instead of intended location. Expressions are now saved to `expressions/` folder in the same directory as the executable for easier access and organization.
  - Modified path detection logic to use executable directory when running as built application
  - Added proper distinction between script mode and executable mode
  - Ensures expressions are always saved alongside the executable for better user experience

## [12.0.3] - 2025-07-31

### Fixed
- **Horizontal Splice Cleat Bug**: Fixed critical issue where horizontal plywood splices were not getting proper cleat support when panels had no intermediate vertical cleats. This occurred with unusual product dimensions (e.g., 20x20x100 - very tall but thin products). The fix ensures all horizontal splices receive structural support per ASTM requirements, regardless of vertical cleat configuration.
  - Modified `calculate_horizontal_cleat_sections` to create cleat sections even when no intermediate vertical cleats exist
  - Updated conditional logic in `nx_expressions_generator.py` to properly trigger horizontal cleat recalculation
  - Applied fix across all panel types (Front, Back, Left, Right, Top)

## [12.0.2] - Previous Release
- Major refactor and cleanup