# Splice Cleat Bug Fix Summary

## Issue Description
When vertical plywood splices occur near panel edges, the expression generation system was creating incorrect NX variables for intermediate vertical cleats. Specifically, cleats positioned at splices that were too close to edge cleats (less than 0.25" clearance) would cause overlapping cleats and invalid geometries.

## Root Cause
The `calculate_vertical_cleat_positions` function in `nx_expressions_generator.py` was placing cleats at ALL splice positions without checking if they would have adequate clearance from edge cleats. This led to:
- Negative gaps between cleats
- Overlapping cleat geometries
- Invalid NX model generation

## Fix Implementation

### 1. Updated `calculate_vertical_cleat_positions` function
- Added `MIN_CLEAT_SPACING = 0.25` constant to define minimum clearance between cleats
- Modified splice cleat placement logic to check clearance from both edge cleats
- Only places splice cleats if they have at least 0.25" clearance from edge cleats
- Updated gap-filling logic to ensure all new cleats maintain proper spacing

### 2. Updated `calculate_vertical_cleat_material_needed` function
- Now checks if any splice would be too close to panel edges
- Calculates material needed to extend panel width if splices are too close to edges
- Ensures structural integrity by extending panels rather than omitting critical splice cleats

## Test Results
The fix was tested with various panel sizes:
- 98" wide panel (splice at 96"): Splice cleat correctly excluded due to insufficient clearance
- 100" wide panel (splice at 96"): Splice cleat correctly excluded
- 102" wide panel (splice at 96"): Splice cleat included with 0.75" clearance
- Expression generation verified to produce correct NX variables with proper suppress flags

## Impact
- Prevents generation of invalid NX models
- Ensures all cleats maintain proper spacing for manufacturability
- Maintains structural integrity by either placing cleats with adequate clearance or extending panels
- Preserves backward compatibility with existing crate designs

## Files Modified
- `legacy/nx_expressions_generator.py`: Updated cleat positioning functions

## Compliance
This fix maintains compliance with ASTM standards by ensuring:
- Structural support at all plywood splices (when clearance allows)
- Proper spacing between structural members
- Panel dimension adjustments when needed to maintain structural integrity