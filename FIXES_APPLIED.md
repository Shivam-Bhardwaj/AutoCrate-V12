# AutoCrate Web vs Desktop NX Expression Fixes

## Issue Resolved
The web version was generating **100" overall length** while desktop generated **105" overall length**.

## Root Cause
The web version's `calculateVerticalCleatMaterialNeeded` function had incorrect logic for checking splice cleat interference. It was checking minimum spacing between cleats instead of checking if splice cleats were too close to the right edge cleat.

## Fix Applied
Updated `web/src/lib/autocrate-calculations-fixed.ts`:

### 1. Fixed vertical cleat material calculation (lines 228-269)
- Changed from checking minimum spacing between all cleats
- Now correctly checks if splice cleats are too close to right edge cleat
- Matches desktop logic exactly from `nx_expressions_generator.py`

### 2. Fixed top panel length property (line 580)
- Changed from `result.length = width` 
- To `result.length = height` (since height parameter contains the length for top panel)

## Results
✅ **Overall Length OD**: Now 105.000" (matches desktop)
✅ **End Panel Length**: Now 100.500" (matches desktop)  
✅ **Top Panel Length**: Now 105.000" (matches desktop)
✅ **Skid Length**: Now 105.000" (matches desktop)

## Remaining Minor Differences
These don't affect the main dimensions but could be addressed later:
- Floorboard widths (5.5" vs 6.0")
- Skid origin offset calculation
- Floorboard start offset

## Test Command
```bash
cd web && npx tsx test-nx-direct.ts
```

## Verification
Both desktop and web now produce the same key dimensions for a 96x48x30" @ 1000lbs crate with 2" clearance.