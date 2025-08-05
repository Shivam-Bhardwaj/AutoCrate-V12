# AutoCrate Comprehensive Testing System

## Overview
The AutoCrate testing system provides automated validation, continuous testing, and comprehensive reporting for engineering calculations, ASTM compliance, and system performance.

## Components

### 1. Test Agent (`autocrate/test_agent.py`)
The core testing framework that manages all test execution and reporting.

**Features:**
- Automated test suite execution
- Performance benchmarking with baseline tracking
- ASTM compliance validation
- Test result aggregation and reporting
- Manual test instruction generation

**Test Categories:**
- **Unit Tests**: Individual function validation
- **Integration Tests**: NX expression generation and file output
- **ASTM Compliance**: ASTM D6256 standard validation
- **Performance Tests**: Speed and memory benchmarks
- **Boundary Tests**: Edge case and extreme input handling
- **Property-Based Tests**: Random input generation for comprehensive coverage

### 2. Test Runner (`run_tests.py`)
Continuous testing runner with watch mode and selective test execution.

**Usage:**
```bash
# Run all tests once
python run_tests.py

# Quick validation (unit + ASTM only)
python run_tests.py --quick

# Continuous testing mode
python run_tests.py --watch

# Run specific test categories
python run_tests.py --category unit astm
python run_tests.py --category performance boundary
```

**Available Categories:**
- `unit` - Unit tests for calculation modules
- `integration` - Integration tests for NX expressions
- `astm` - ASTM compliance validation
- `performance` - Performance benchmarks
- `boundary` - Boundary and edge case tests
- `property` - Property-based random tests
- `all` - Run all test categories (default)

### 3. Quick Test (`quick_test.py`)
Rapid validation script for pre-commit and pre-deployment checks.

**Tests Performed:**
1. Basic panel calculations
2. ASTM compliance verification
3. Edge case handling
4. Performance benchmarks
5. Module import validation

**Usage:**
```bash
python quick_test.py
```

Returns exit code 0 if all tests pass, 1 if any fail.

### 4. Property-Based Testing (`tests/test_property_based.py`)
Uses hypothesis framework for comprehensive input space testing.

**Properties Tested:**
- Dimension consistency
- Cleat spacing compliance (24" maximum)
- Structural symmetry
- Cross-module consistency
- Input validation boundaries

## Test Execution Workflow

### Automated Testing After Operations
The system automatically runs tests after:
- Code changes
- New feature implementation
- Bug fixes
- Configuration updates

### Test Suite Hierarchy
```
1. Quick Validation (< 5 seconds)
   - Critical calculations
   - ASTM compliance
   - Import validation

2. Standard Test Suite (< 30 seconds)
   - All unit tests
   - Integration tests
   - Performance benchmarks

3. Comprehensive Testing (< 5 minutes)
   - Property-based tests
   - Stress tests
   - Full regression suite
```

## Manual Testing Instructions

When automated tests pass, the system provides specific manual testing instructions for:

### GUI Validation
- Input field validation
- Error message clarity
- Responsiveness during calculations
- Result display accuracy

### NX Integration
- Expression file generation
- NX import compatibility
- 3D model accuracy
- Component placement verification

### End-to-End Workflows
- Design input to file output
- Material optimization
- Manufacturing documentation
- Multi-panel consistency

## Test Reports

### Report Types
1. **JSON Report** (`test_reports/test_report_*.json`)
   - Machine-readable format
   - Complete test details
   - Performance metrics
   - Coverage statistics

2. **HTML Report** (`test_reports/test_report_*.html`)
   - Human-readable format
   - Visual pass/fail indicators
   - Test suite summaries
   - Manual test instructions

3. **Console Output**
   - Real-time test progress
   - Quick pass/fail summary
   - Immediate feedback

### Performance Baselines
The system maintains performance baselines in `test_reports/performance_baselines.json`:
- Tracks calculation speeds
- Detects performance regressions
- Updates baselines for improvements

## ASTM Compliance Testing

### Standards Validated
- **ASTM D6256**: Standard specification for wood crates
- **Panel Thickness**: Minimum 0.75" requirement
- **Cleat Spacing**: Maximum 24" center-to-center
- **Safety Factors**: 3.0 minimum for shipping crates
- **Material Grades**: CDX plywood, SPF #2 lumber

### Compliance Checks
1. Minimum material thickness
2. Maximum spacing requirements
3. Structural safety factors
4. Corner reinforcement placement
5. Load distribution validation

## Integration with Logging System

The testing system integrates with AutoCrate's debug logger:
- Test execution is logged with timing
- Failures include detailed debug information
- Performance metrics are tracked
- Session summaries include test results

## Continuous Integration

### Pre-Commit Checks
```bash
# Run before committing code
python quick_test.py
```

### Pre-Deployment Validation
```bash
# Full test suite before deployment
python run_tests.py --category all
```

### Automated Monitoring
```bash
# Continuous monitoring mode
python run_tests.py --watch
```

## Test Coverage Goals

- **Unit Tests**: > 90% code coverage
- **Integration Tests**: All file generation paths
- **ASTM Compliance**: 100% of requirements
- **Performance**: No regressions > 20%
- **Edge Cases**: All boundary conditions

## Adding New Tests

### Unit Tests
Add to `tests/test_*_logic.py` files:
```python
def test_new_calculation():
    result = calculate_function(params)
    assert result['value'] == expected_value
```

### Integration Tests
Add to test agent's integration suite:
```python
test_cases.append({
    "name": "new_integration_test",
    "params": {...},
    "expected": {...}
})
```

### Manual Tests
Add to test agent's manual test instructions:
```python
ManualTestInstruction(
    test_id="MT###",
    category="CATEGORY",
    priority="HIGH/MEDIUM/LOW",
    title="Test Title",
    description="What to test",
    steps=[...],
    expected_results=[...]
)
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure all dependencies are installed
   - Check Python path configuration
   - Verify module structure

2. **Performance Test Failures**
   - Check system load
   - Verify baseline accuracy
   - Consider hardware differences

3. **ASTM Compliance Failures**
   - Review calculation logic
   - Verify safety factors
   - Check material specifications

## Best Practices

1. **Run quick tests before every commit**
2. **Run full suite before deployments**
3. **Update baselines after performance improvements**
4. **Document new manual test requirements**
5. **Keep test coverage above 90%**

## Command Reference

```bash
# Quick validation
python quick_test.py

# Run all tests
python run_tests.py

# Run specific categories
python run_tests.py -c unit astm

# Continuous testing
python run_tests.py --watch

# Quick validation only
python run_tests.py --quick

# Run property-based tests
pytest tests/test_property_based.py -v

# Run with coverage
pytest --cov=autocrate --cov-report=html

# Run specific test file
pytest tests/test_front_panel_logic.py -v
```

## Contact

For questions about the testing system or to report issues:
- Review test reports in `test_reports/` directory
- Check logs in `logs/` directory
- Consult ASTM D6256 documentation for compliance questions