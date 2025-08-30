#!/usr/bin/env python
"""
AutoCrate Automated Test Runner

This script provides continuous testing capabilities for AutoCrate,
automatically running tests after code changes and generating reports.
"""

import sys
import os
import time
import argparse
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from autocrate.test_agent import AutoCrateTestAgent, TestCategory
from autocrate.debug_logger import get_logger, finalize_logging

# Initialize logger
logger = get_logger("AutoCrate.TestRunner")


class ContinuousTestRunner:
    """
    Continuous test runner that monitors for changes and automatically runs tests.
    """
    
    def __init__(self, watch_mode: bool = False, test_categories: list = None):
        """
        Initialize the continuous test runner.
        
        Args:
            watch_mode: Whether to watch for file changes and re-run tests.
            test_categories: List of test categories to run (None = all).
        """
        self.watch_mode = watch_mode
        self.test_categories = test_categories or []
        self.test_agent = AutoCrateTestAgent()
        self.last_run_time = None
        self.run_count = 0
        
        logger.info("Continuous Test Runner initialized", {
            'watch_mode': watch_mode,
            'test_categories': test_categories
        })
    
    def run_selected_tests(self):
        """Run selected test categories."""
        logger.info(f"Starting test run #{self.run_count + 1}")
        self.run_count += 1
        
        results = {}
        
        # Map categories to test methods
        test_mapping = {
            'unit': self.test_agent.run_unit_tests,
            'integration': self.test_agent.run_integration_tests,
            'astm': self.test_agent.run_astm_compliance_tests,
            'performance': self.test_agent.run_performance_tests,
            'boundary': self.test_agent.run_boundary_tests,
            'property': self.test_agent.run_property_based_tests,
            'all': self.test_agent.run_all_tests
        }
        
        # Run selected tests
        if not self.test_categories or 'all' in self.test_categories:
            results = self.test_agent.run_all_tests()
        else:
            for category in self.test_categories:
                if category in test_mapping:
                    logger.info(f"Running {category} tests...")
                    try:
                        if category == 'all':
                            results = test_mapping[category]()
                        else:
                            result = test_mapping[category]()
                            results[result.suite_name] = result
                    except Exception as e:
                        logger.error(f"Failed to run {category} tests: {e}")
        
        return results
    
    def check_test_results(self, results):
        """
        Check test results and determine if action is needed.
        
        Args:
            results: Test results dictionary.
            
        Returns:
            Tuple of (all_passed, critical_failures)
        """
        total_failed = sum(r.failed + r.errors for r in results.values())
        
        # Check for critical failures (ASTM compliance, integration)
        critical_failures = []
        
        for suite_name, result in results.items():
            if "ASTM" in suite_name and (result.failed > 0 or result.errors > 0):
                critical_failures.append(f"ASTM compliance tests failed")
            elif "Integration" in suite_name and result.errors > 0:
                critical_failures.append(f"Integration tests have errors")
        
        all_passed = total_failed == 0
        
        return all_passed, critical_failures
    
    def generate_quick_report(self, results):
        """Generate a quick summary report."""
        print("\n" + "=" * 60)
        print("QUICK TEST SUMMARY")
        print("=" * 60)
        
        total_tests = sum(r.total_tests for r in results.values())
        total_passed = sum(r.passed for r in results.values())
        total_failed = sum(r.failed for r in results.values())
        total_errors = sum(r.errors for r in results.values())
        
        if total_tests > 0:
            pass_rate = (total_passed / total_tests) * 100
            
            # Color coding for terminal (if supported)
            if pass_rate == 100:
                status_symbol = "[PASS]"
                status_color = "\033[92m"  # Green
            elif pass_rate >= 80:
                status_symbol = "!"
                status_color = "\033[93m"  # Yellow
            else:
                status_symbol = "[FAIL]"
                status_color = "\033[91m"  # Red
            
            reset_color = "\033[0m"
            
            print(f"{status_color}{status_symbol} Overall Pass Rate: {pass_rate:.1f}%{reset_color}")
            print(f"   Total: {total_tests} | Passed: {total_passed} | Failed: {total_failed} | Errors: {total_errors}")
            
            # Show suite breakdown
            print("\nSuite Results:")
            for suite_name, result in results.items():
                suite_rate = (result.passed / result.total_tests * 100) if result.total_tests > 0 else 0
                suite_symbol = "[PASS]" if suite_rate == 100 else "[FAIL]" if suite_rate < 50 else "[WARN]"
                print(f"  {suite_symbol} {suite_name}: {result.passed}/{result.total_tests} ({suite_rate:.1f}%)")
        
        print("=" * 60)
    
    def suggest_manual_tests(self, results):
        """Suggest relevant manual tests based on automated test results."""
        print("\n" + "-" * 60)
        print("SUGGESTED MANUAL TESTS")
        print("-" * 60)
        
        all_passed, critical_failures = self.check_test_results(results)
        
        if all_passed:
            print("\n[PASS] All automated tests passed!")
            print("\nRecommended manual tests to complete validation:")
            
            # Get high priority manual tests
            high_priority = self.test_agent.get_manual_test_instructions("HIGH")
            for test in high_priority[:2]:
                print(f"\n• {test.test_id}: {test.title}")
                print(f"  Time: ~{test.estimated_time_minutes} minutes")
                print(f"  {test.description}")
        else:
            print("\n! Some automated tests failed.")
            print("\nFocus manual testing on these areas:")
            
            if critical_failures:
                for failure in critical_failures:
                    print(f"  • {failure}")
            
            # Suggest specific manual tests based on failures
            failed_categories = set()
            for suite_name, result in results.items():
                if result.failed > 0 or result.errors > 0:
                    if "Integration" in suite_name:
                        failed_categories.add("NX_INTEGRATION")
                    elif "ASTM" in suite_name:
                        failed_categories.add("ASTM_COMPLIANCE")
                    elif "Performance" in suite_name:
                        failed_categories.add("STRESS_TEST")
            
            relevant_tests = [
                test for test in self.test_agent.manual_tests
                if test.category in failed_categories
            ]
            
            for test in relevant_tests[:2]:
                print(f"\n• {test.test_id}: {test.title}")
                print(f"  Priority: {test.priority}")
                print(f"  {test.description}")
        
        print("-" * 60)
    
    def run_continuous(self):
        """Run tests continuously in watch mode."""
        print("Starting continuous test mode...")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                # Run tests
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Running tests...")
                results = self.run_selected_tests()
                
                # Generate reports
                self.generate_quick_report(results)
                report_path = self.test_agent.generate_test_report(results)
                print(f"\nFull report: {report_path}")
                
                # Check results and suggest actions
                all_passed, critical_failures = self.check_test_results(results)
                
                if critical_failures:
                    print("\n[WARNING] CRITICAL FAILURES DETECTED:")
                    for failure in critical_failures:
                        print(f"  • {failure}")
                
                # Suggest manual tests
                self.suggest_manual_tests(results)
                
                if self.watch_mode:
                    print(f"\nWaiting for changes... (next run in 60 seconds)")
                    time.sleep(60)  # Wait 60 seconds before next run
                else:
                    break
                    
        except KeyboardInterrupt:
            print("\n\nStopping continuous test mode...")
    
    def run_quick_validation(self):
        """Run a quick validation suite for rapid feedback."""
        print("Running quick validation tests...")
        
        # Run only critical tests
        quick_tests = ['unit', 'astm']
        self.test_categories = quick_tests
        
        results = self.run_selected_tests()
        self.generate_quick_report(results)
        
        all_passed, critical_failures = self.check_test_results(results)
        
        if all_passed:
            print("\n[PASS] Quick validation PASSED - Safe to proceed")
            return 0
        else:
            print("\n[FAIL] Quick validation FAILED - Review issues before proceeding")
            return 1


def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(
        description="AutoCrate Automated Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                    # Run all tests once
  python run_tests.py --quick            # Run quick validation tests
  python run_tests.py --watch            # Run tests continuously
  python run_tests.py --category unit    # Run only unit tests
  python run_tests.py --category astm performance  # Run ASTM and performance tests
  
Available test categories:
  unit         - Unit tests for calculation modules
  integration  - Integration tests for NX expressions
  astm         - ASTM compliance validation
  performance  - Performance benchmarks
  boundary     - Boundary and edge case tests
  property     - Property-based random tests
  all          - Run all test categories (default)
        """
    )
    
    parser.add_argument(
        '--watch', '-w',
        action='store_true',
        help='Run tests continuously, watching for changes'
    )
    
    parser.add_argument(
        '--quick', '-q',
        action='store_true',
        help='Run quick validation suite (unit + ASTM tests only)'
    )
    
    parser.add_argument(
        '--category', '-c',
        nargs='+',
        choices=['unit', 'integration', 'astm', 'performance', 'boundary', 'property', 'all'],
        help='Specific test categories to run'
    )
    
    parser.add_argument(
        '--report-only', '-r',
        action='store_true',
        help='Generate report from last test run without running new tests'
    )
    
    args = parser.parse_args()
    
    # Initialize test runner
    runner = ContinuousTestRunner(
        watch_mode=args.watch,
        test_categories=args.category if args.category else []
    )
    
    try:
        if args.quick:
            # Run quick validation
            return runner.run_quick_validation()
        elif args.report_only:
            # Just generate a report from existing data
            print("Generating report from last test run...")
            # This would load and display the most recent test results
            print("Feature not yet implemented")
            return 0
        else:
            # Run tests (once or continuously)
            runner.run_continuous()
            return 0
            
    except Exception as e:
        logger.error(f"Test runner failed: {e}")
        print(f"\n[ERROR] Test runner encountered an error: {e}")
        return 1
    finally:
        finalize_logging()


if __name__ == "__main__":
    sys.exit(main())