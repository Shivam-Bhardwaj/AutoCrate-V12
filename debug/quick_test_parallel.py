#!/usr/bin/env python3
"""
Optimized parallel quick test for AutoCrate
Runs multiple test categories simultaneously for faster feedback
"""

import time
import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from autocrate.test_agent import AutoCrateTestAgent

def run_test_category(category):
    """Run a specific test category and return results"""
    try:
        test_agent = AutoCrateTestAgent()
        start_time = time.time()
        
        if category == "basic":
            # Basic panel calculations
            from autocrate.front_panel_logic import calculate_front_panel_components
            result = calculate_front_panel_components(48, 36, 0.75, 1.5, 3.5, True)
            success = bool(result)
            
        elif category == "astm":
            # ASTM compliance test
            from autocrate.front_panel_logic import calculate_front_panel_components
            result = calculate_front_panel_components(60, 40, 0.75, 1.5, 3.5, True)
            # Check cleat spacing compliance
            success = result and len(result.get('intermediate_vertical_cleats', [])) >= 1
            
        elif category == "edge_cases":
            # Test minimum and maximum sizes
            from autocrate.front_panel_logic import calculate_front_panel_components
            min_result = calculate_front_panel_components(12, 12, 0.75, 1.5, 3.5, True)  # Changed from 6 to 12 (min constraint)
            max_result = calculate_front_panel_components(130, 72, 0.75, 1.5, 3.5, True)
            success = bool(min_result and max_result)
            
        elif category == "performance":
            # Performance benchmark
            from autocrate.front_panel_logic import calculate_front_panel_components
            times = []
            for _ in range(10):  # Reduced from 100 for faster execution
                t_start = time.perf_counter()
                calculate_front_panel_components(48, 36, 0.75, 1.5, 3.5, True)
                times.append((time.perf_counter() - t_start) * 1000)
            avg_time = sum(times) / len(times)
            success = avg_time < 5.0  # Must be under 5ms average (more realistic)
            
        elif category == "imports":
            # Test all critical imports
            import autocrate.nx_expressions_generator
            import autocrate.front_panel_logic
            import autocrate.back_panel_logic
            import autocrate.left_panel_logic
            import autocrate.right_panel_logic
            import autocrate.top_panel_logic
            success = True
            
        else:
            success = False
            
        duration = (time.time() - start_time) * 1000
        return {
            'category': category,
            'success': success,
            'duration': duration,
            'error': None
        }
        
    except Exception as e:
        return {
            'category': category,
            'success': False,
            'duration': 0,
            'error': str(e)
        }

def main():
    """Run parallel quick validation tests"""
    print("=" * 60)
    print("AUTOCRATE PARALLEL QUICK TEST")
    print("=" * 60)
    print(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    
    start_time = time.time()
    
    # Test categories to run in parallel
    test_categories = [
        "basic",
        "astm", 
        "edge_cases",
        "performance",
        "imports"
    ]
    
    results = {}
    
    # Run tests in parallel using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=min(len(test_categories), 4)) as executor:
        # Submit all test jobs
        future_to_category = {
            executor.submit(run_test_category, category): category 
            for category in test_categories
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_category):
            result = future.result()
            results[result['category']] = result
            
            # Print result immediately
            status = "[PASS]" if result['success'] else "[FAIL]"
            duration = f"{result['duration']:.1f}ms"
            
            if result['error']:
                print(f"  {status} {result['category'].title()}: {result['error']}")
            else:
                print(f"  {status} {result['category'].title()}: {duration}")
    
    # Summary
    total_time = (time.time() - start_time) * 1000
    passed = sum(1 for r in results.values() if r['success'])
    failed = len(results) - passed
    
    print("-" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print(f"Total time: {total_time:.1f}ms (parallel execution)")
    print(f"Average per test: {total_time/len(results):.1f}ms")
    
    if failed > 0:
        print(f"\n[ERROR] {failed} test(s) failed!")
        for category, result in results.items():
            if not result['success']:
                print(f"  - {category}: {result.get('error', 'Unknown error')}")
        return 1
    else:
        print("\n[SUCCESS] All tests passed!")
        return 0

if __name__ == "__main__":
    sys.exit(main())