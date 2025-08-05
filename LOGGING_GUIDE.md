# AutoCrate Logging & Debugging Guide

The AutoCrate application now includes a comprehensive logging system for debugging, error tracking, and performance monitoring.

## Log Files Location

All log files are created in the `logs/` directory with timestamps:

```
logs/
├── debug_YYYYMMDD_HHMMSS.log           # Detailed debug information
├── errors_YYYYMMDD_HHMMSS.log          # Error messages and stack traces  
├── performance_YYYYMMDD_HHMMSS.json    # Performance metrics in JSON format
├── session_summary_YYYYMMDD_HHMMSS.json # Session summary with statistics
└── error_detail_YYYYMMDD_HHMMSS.json   # Detailed error information
```

## Debug Levels

### Environment Variables
Control logging behavior with environment variables:

```bash
# Enable detailed console debugging
set AUTOCRATE_DEBUG=1

# For development mode (includes debug logging)
set AUTOCRATE_DEV_MODE=1
```

### Log Levels
- **DEBUG**: Detailed function entry/exit, parameter values
- **INFO**: General information, successful operations  
- **WARNING**: Non-critical issues, fallback operations
- **ERROR**: Errors with recovery, validation failures
- **CRITICAL**: Fatal errors that may stop the application

## What Gets Logged

### Startup Information
- Session ID and timestamp
- Python version and working directory
- Module import success/failures
- Available files and paths (for debugging import issues)

### Function Execution
- Function entry with parameters
- Function exit with results and duration
- Performance metrics (execution time)
- Function call counts

### Expression Generation
- Input parameters for crate generation
- Calculation progress and intermediate results
- File output information (size, location)
- Success/failure status with detailed errors

### Import Debugging
- Relative vs direct import attempts
- Module paths and available files
- Import error details with context

## Example Log Output

### Debug Log (debug_*.log)
```
2025-08-04 19:11:12,345 | INFO     | AutoCrate.NX_Generator | generate_crate_expressions_logic:278 | Starting crate expression generation | Data: {"product_weight_lbs": 100, "product_length_in": 24}
2025-08-04 19:11:12,346 | INFO     | AutoCrate.NX_Generator | generate_crate_expressions_logic:1376 | Expression generation completed successfully | Data: {"expressions_count": 715, "file_size_bytes": 31339}
```

### Performance Log (performance_*.json)
```json
{
  "timestamp": "2025-08-04T19:11:12.346",
  "session_id": "20250804_191112_28544",
  "operation": "generate_crate_expressions",
  "duration_ms": 1.33,
  "details": {
    "expressions_count": 715,
    "file_size_bytes": 31339
  }
}
```

### Error Log (errors_*.log)
```
2025-08-04 19:11:12,347 | ERROR | AutoCrate.NX_Generator | generate_crate_expressions_logic:1390 | Expression generation failed | Error Info: {"message": "Invalid input", "exception_type": "ValueError", "traceback": "..."}
```

## Using the Logging System

### In Python Code
```python
from debug_logger import get_logger

logger = get_logger("MyModule")

# Basic logging
logger.info("Operation started")
logger.error("Something went wrong", exception, {"context": "additional_data"})

# Performance logging
logger.log_performance("my_operation", duration_seconds, {"detail": "value"})

# Function decoration for automatic logging
@debug_function(logger)
def my_function(param1, param2):
    return result
```

### Console Output
When `AUTOCRATE_DEBUG=1`:
- Shows DEBUG level and above
- Includes timestamps and function names
- Real-time feedback during development

When `AUTOCRATE_DEBUG=0` (default):
- Shows INFO level and above
- Cleaner output for production use

## Troubleshooting with Logs

### Import Issues
Check the debug log for:
- "Starting module imports" entries
- "Relative import failed" warnings  
- "Direct imports successful" confirmations
- Available files in the module directory

### Expression Generation Problems
Check for:
- Input parameter validation errors
- Calculation intermediate steps
- File writing permission issues
- Performance bottlenecks

### Build/PyInstaller Issues
The logging system helps debug:
- Module path resolution
- Missing dependencies
- Import path conflicts
- Runtime environment differences

## Performance Analysis

### View Performance Summary
```python
from debug_logger import get_logger

logger = get_logger()
summary = logger.get_performance_summary()
print(summary)
```

Example output:
```python
{
  'generate_crate_expressions': {
    'count': 5,
    'avg_ms': 1.24,
    'min_ms': 0.95,
    'max_ms': 1.68,
    'total_ms': 6.20
  }
}
```

### JSON Performance Data
Each `performance_*.json` file contains detailed metrics that can be analyzed with tools like:
- Python pandas for data analysis
- Excel for visualization  
- Log analysis tools

## Log Cleanup

The logging system creates timestamped files that don't auto-delete. To manage disk space:

```bash
# Delete logs older than 30 days (Windows)
forfiles /p logs /s /m *.log /d -30 /c "cmd /c del @path"

# Keep only the 10 most recent log files
# (Manual cleanup recommended)
```

## Integration with Build Process

The logging system is integrated into:
- `build_and_test.bat` - Logs build progress and errors
- `start_dev.bat` - Enables debug logging automatically  
- `start_production.bat` - Uses production logging levels
- PyInstaller builds - Helps debug packaging issues

## Session Management

Each run creates a unique session with:
- Session ID: `YYYYMMDD_HHMMSS_ProcessID`
- All logs tagged with session ID
- Session summary written on clean exit
- Automatic session finalization

This comprehensive logging system makes debugging AutoCrate issues much easier by providing detailed information about imports, calculations, file operations, and performance metrics.