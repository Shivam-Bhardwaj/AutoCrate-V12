# Intelligent Expression File Management System

## Overview
AutoCrate v12.0.9 now includes an intelligent expression file replacement system that automatically manages duplicate expression files based on their parameters. This ensures a clean, organized expressions folder where each unique parameter combination has only one (latest) expression file.

## Features

### 1. Automatic Duplicate Detection
- Detects existing expression files with identical parameters
- Compares based on:
  - Product dimensions (length, width, height)
  - Product weight
  - Material type (PLY/OSB)
  - Panel thickness
  - Clearance values

### 2. Smart Replacement
- When generating a new expression with parameters matching an existing file, the system:
  - Automatically identifies the duplicate
  - Deletes the old file
  - Saves only the new version
  - Reports the replacement in the GUI log

### 3. Filename Parsing
Supports multiple filename formats:
- Standard: `YYYYMMDD_HHMMSS_Crate_LxWxH_Wweight_5P_MaterialThickness_Cclearance_ASTM.exp`
- Quick Test: `YYYYMMDD_HHMMSS_QuickTest_##_LxWxH_Wweight_MaterialThickness_Cclearance_Description.exp`
- Legacy formats with variations in naming conventions

### 4. Tolerance Matching
- Uses intelligent tolerance (0.1) for floating-point comparisons
- Accounts for rounding differences in parameters
- Ensures reliable duplicate detection

## Benefits

### For Rapid Testing
- Generate expressions repeatedly without accumulating duplicates
- Test iterations quickly without manual cleanup
- Maintain a clean test environment

### For Organization
- Each parameter combination has only one expression file
- Latest version always preserved
- No confusion from multiple versions

### For Performance
- Reduced directory clutter
- Faster file operations
- Easier to locate specific expressions

## Usage

### Automatic Operation
The system works automatically when generating expressions through:
- Main GUI expression generation
- Quick Test Suite
- Any programmatic expression generation

### Manual Cleanup Utility
Clean existing expressions folder:
```bash
# Dry run (preview what would be deleted)
python clean_expressions.py

# Actually delete duplicates
python clean_expressions.py --execute

# Clean specific directory
python clean_expressions.py --dir /path/to/expressions
```

### Testing the System
Verify the replacement system:
```bash
python test_expression_manager.py
python test_duplicate_replacement.py
```

## Implementation Details

### Core Module
`autocrate/expression_file_manager.py`
- `ExpressionFileManager`: Main management class
- `ExpressionParameters`: Parameter data structure
- `extract_parameters_from_inputs()`: Helper function

### Integration Points
- `nx_expressions_generator.py`: Modified to use file manager
- Both normal generation and quick test suite integrated
- Fallback to original behavior if manager unavailable

### Parameter Matching Logic
```python
# Parameters considered for matching:
- length (±0.1 inch tolerance)
- width (±0.1 inch tolerance)  
- height (±0.1 inch tolerance)
- weight (±0.1 lbs tolerance)
- material_type (exact match)
- panel_thickness (±0.1 inch tolerance)
- clearance (±0.1 inch tolerance)
```

## Technical Notes

### File Safety
- Only deletes files with matching parameters
- Never deletes the file being created
- Handles file access errors gracefully

### Backwards Compatibility
- System includes fallback behavior
- Works with existing expression files
- Parses multiple filename formats

### Performance
- Minimal overhead on expression generation
- Fast pattern matching with compiled regex
- Efficient file operations

## Example Workflow

1. Generate expression for 72x48x36 crate, 1500 lbs
   - File created: `20250807_150000_Crate_72x48x36_W1500_5P_PLY0.75_C2.0_ASTM.exp`

2. Adjust design, regenerate same parameters
   - Old file automatically deleted
   - New file created: `20250807_151000_Crate_72x48x36_W1500_5P_PLY0.75_C2.0_ASTM.exp`
   - GUI shows: "Replaced 1 existing expression with same parameters"

3. Generate different size: 96x48x36
   - New file created without affecting previous
   - Both expressions coexist (different parameters)

## Maintenance

### Adding New Filename Formats
Edit `PATTERNS` list in `expression_file_manager.py` to add new regex patterns.

### Adjusting Tolerance
Modify the `tolerance` parameter in the `matches()` method to adjust sensitivity.

### Debugging
- Check logs for replacement messages
- Use `clean_expressions.py` in dry-run mode to preview operations
- Run test scripts to verify functionality

## Future Enhancements
- [ ] Archive old versions instead of deleting
- [ ] Parameter-based search and retrieval
- [ ] Batch comparison tools
- [ ] Expression version history
- [ ] Cloud backup integration

---

This intelligent file management system ensures AutoCrate maintains a clean, organized expression library optimized for rapid iterative design and testing workflows.