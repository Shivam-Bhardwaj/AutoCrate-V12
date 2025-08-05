#!/usr/bin/env python
"""
Quick Test Validation Script for AutoCrate

This script provides rapid validation of critical functionality
before commits or deployments.
"""

import sys
import time
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from autocrate.test_agent import AutoCrateTestAgent
from autocrate.debug_logger import get_logger, finalize_logging

# Initialize logger
logger = get_logger("AutoCrate.QuickTest")


def run_quick_validation():
    """Run quick validation tests for critical functionality."""
    
    print("\n" + "=" * 70)
    print("AUTOCRATE QUICK VALIDATION TEST")
    print("=" * 70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 70)
    
    # Initialize test agent
    agent = AutoCrateTestAgent()
    
    # Track overall results
    all_passed = True
    results_summary = []
    
    # Test 1: Basic Calculation Validation
    print("\n[1/5] Testing basic panel calculations...")
    try:
        from autocrate.front_panel_logic import calculate_front_panel_components
        
        start_time = time.time()
        result = calculate_front_panel_components(
            front_panel_assembly_width=48,
            front_panel_assembly_height=36,
            panel_sheathing_thickness=0.75,
            cleat_material_thickness=1.5,
            cleat_material_member_width=3.5
        )
        duration = (time.time() - start_time) * 1000
        
        if result and result['plywood']['width'] == 48 and result['plywood']['height'] == 36:
            print(f"  [PASS] Panel calculations working ({duration:.2f}ms)")
            results_summary.append(("Panel Calculations", True, duration))
        else:
            print(f"  [FAIL] Panel calculations failed")
            results_summary.append(("Panel Calculations", False, duration))
            all_passed = False
    except Exception as e:
        print(f"  [FAIL] Panel calculations error: {e}")
        results_summary.append(("Panel Calculations", False, 0))
        all_passed = False
    
    # Test 2: ASTM Compliance Check
    print("\n[2/5] Testing ASTM compliance...")
    try:
        start_time = time.time()
        
        # Check cleat spacing compliance
        result = calculate_front_panel_components(
            front_panel_assembly_width=60,
            front_panel_assembly_height=40,
            panel_sheathing_thickness=0.75,
            cleat_material_thickness=1.5,
            cleat_material_member_width=3.5
        )
        
        # Verify intermediate cleats are added when needed
        if result['intermediate_vertical_cleats']['count'] > 0:
            positions = result['intermediate_vertical_cleats']['positions_x_centerline']
            max_spacing = 0
            prev_pos = 0
            for pos in positions:
                spacing = pos - prev_pos
                max_spacing = max(max_spacing, spacing)
                prev_pos = pos
            
            duration = (time.time() - start_time) * 1000
            
            if max_spacing <= 24.1:  # Allow small tolerance
                print(f"  [PASS] ASTM cleat spacing compliant ({duration:.2f}ms)")
                results_summary.append(("ASTM Compliance", True, duration))
            else:
                print(f"  [FAIL] ASTM cleat spacing violation: {max_spacing:.2f}\"")
                results_summary.append(("ASTM Compliance", False, duration))
                all_passed = False
        else:
            duration = (time.time() - start_time) * 1000
            print(f"  [PASS] No intermediate cleats needed ({duration:.2f}ms)")
            results_summary.append(("ASTM Compliance", True, duration))
            
    except Exception as e:
        print(f"  [FAIL] ASTM compliance check error: {e}")
        results_summary.append(("ASTM Compliance", False, 0))
        all_passed = False
    
    # Test 3: Edge Case Handling
    print("\n[3/5] Testing edge cases...")
    edge_cases = [
        {"name": "Minimum size", "width": 6, "height": 12},
        {"name": "Maximum size", "width": 240, "height": 72},
        {"name": "Tall thin", "width": 20, "height": 100}
    ]
    
    edge_case_passed = True
    for case in edge_cases:
        try:
            start_time = time.time()
            result = calculate_front_panel_components(
                front_panel_assembly_width=case['width'],
                front_panel_assembly_height=case['height'],
                panel_sheathing_thickness=0.75,
                cleat_material_thickness=1.5,
                cleat_material_member_width=3.5
            )
            duration = (time.time() - start_time) * 1000
            
            if result and result['plywood']['width'] > 0:
                print(f"  [PASS] {case['name']}: passed ({duration:.2f}ms)")
            else:
                print(f"  [FAIL] {case['name']}: failed")
                edge_case_passed = False
                all_passed = False
        except Exception as e:
            print(f"  [FAIL] {case['name']}: error - {e}")
            edge_case_passed = False
            all_passed = False
    
    results_summary.append(("Edge Cases", edge_case_passed, 0))
    
    # Test 4: Performance Check
    print("\n[4/5] Testing performance...")
    try:
        iterations = 100
        start_time = time.time()
        
        for _ in range(iterations):
            calculate_front_panel_components(
                front_panel_assembly_width=48,
                front_panel_assembly_height=36,
                panel_sheathing_thickness=0.75,
                cleat_material_thickness=1.5,
                cleat_material_member_width=3.5
            )
        
        total_duration = (time.time() - start_time) * 1000
        avg_duration = total_duration / iterations
        
        if avg_duration < 10:  # Should be fast (< 10ms per calculation)
            print(f"  [PASS] Performance acceptable ({avg_duration:.2f}ms avg per calculation)")
            results_summary.append(("Performance", True, avg_duration))
        else:
            print(f"  [FAIL] Performance slow ({avg_duration:.2f}ms avg per calculation)")
            results_summary.append(("Performance", False, avg_duration))
            all_passed = False
            
    except Exception as e:
        print(f"  [FAIL] Performance test error: {e}")
        results_summary.append(("Performance", False, 0))
        all_passed = False
    
    # Test 5: Module Imports
    print("\n[5/5] Testing module imports...")
    modules_to_test = [
        "autocrate.front_panel_logic",
        "autocrate.back_panel_logic",
        "autocrate.end_panel_logic",
        "autocrate.left_panel_logic",
        "autocrate.right_panel_logic",
        "autocrate.top_panel_logic",
        "autocrate.floorboard_logic",
        "autocrate.skid_logic",
        "autocrate.nx_expressions_generator"
    ]
    
    import_passed = True
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"  [PASS] {module_name}")
        except ImportError as e:
            print(f"  [FAIL] {module_name}: {e}")
            import_passed = False
            all_passed = False
    
    results_summary.append(("Module Imports", import_passed, 0))
    
    # Summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    
    for test_name, passed, duration in results_summary:
        status = "[PASS]" if passed else "[FAIL]"
        if duration > 0:
            print(f"{test_name:20} {status:12} ({duration:.2f}ms)")
        else:
            print(f"{test_name:20} {status:12}")
    
    print("-" * 70)
    
    if all_passed:
        print("\n[SUCCESS] ALL QUICK VALIDATION TESTS PASSED")
        print("\nSafe to proceed with:")
        print("  - Code commits")
        print("  - NX expression generation")
        print("  - Production deployment")
        print("\nRecommended next steps:")
        print("  1. Run full test suite: python run_tests.py")
        print("  2. Perform manual GUI testing")
        print("  3. Validate NX expression import")
    else:
        print("\n[FAILURE] VALIDATION FAILED - ISSUES DETECTED")
        print("\nDO NOT proceed with:")
        print("  - Production deployment")
        print("  - Customer deliveries")
        print("\nRequired actions:")
        print("  1. Review failed tests above")
        print("  2. Fix identified issues")
        print("  3. Re-run validation")
    
    print("\n" + "=" * 70)
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    try:
        exit_code = run_quick_validation()
        finalize_logging()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nValidation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)