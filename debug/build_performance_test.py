#!/usr/bin/env python3
"""
Build Performance Comparison Tool
Compares original vs optimized build and test pipeline
"""

import time
import subprocess
import sys
import os

def run_command_with_timing(command, description):
    """Run a command and measure execution time"""
    print(f"\n{description}")
    print("-" * 50)
    
    start_time = time.time()
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=300)
        duration = time.time() - start_time
        
        if result.returncode == 0:
            print(f"[PASS] SUCCESS: {duration:.1f}s")
            return duration, True
        else:
            print(f"[FAIL] FAILED: {duration:.1f}s")
            print(f"Error: {result.stderr[:200]}...")
            return duration, False
            
    except subprocess.TimeoutExpired:
        duration = time.time() - start_time
        print(f"[TIMEOUT] TIMEOUT: {duration:.1f}s")
        return duration, False
    except Exception as e:
        duration = time.time() - start_time
        print(f"[ERROR] ERROR: {duration:.1f}s - {str(e)}")
        return duration, False

def main():
    """Compare build performance"""
    print("=" * 60)
    print("AutoCrate Build Performance Comparison")
    print("=" * 60)
    
    results = {}
    
    # Test 1: Original quick test
    print("\n1. TESTING PHASE COMPARISON")
    print("=" * 30)
    
    duration, success = run_command_with_timing(
        "python quick_test.py", 
        "Original Sequential Testing"
    )
    results['original_test'] = {'time': duration, 'success': success}
    
    duration, success = run_command_with_timing(
        "python quick_test_parallel.py", 
        "Optimized Parallel Testing"
    )
    results['optimized_test'] = {'time': duration, 'success': success}
    
    # Calculate test improvement
    if results['original_test']['success'] and results['optimized_test']['success']:
        test_improvement = ((results['original_test']['time'] - results['optimized_test']['time']) 
                           / results['original_test']['time']) * 100
        print(f"\n[INFO] Testing Speed Improvement: {test_improvement:.1f}%")
        
        if results['optimized_test']['time'] < results['original_test']['time']:
            speedup = results['original_test']['time'] / results['optimized_test']['time']
            print(f"[INFO] Parallel Testing is {speedup:.1f}x faster")
    
    # Test 2: Build comparison (only if both tests passed)
    if all(r['success'] for r in results.values()):
        print("\n\n2. BUILD PHASE COMPARISON")
        print("=" * 30)
        print("Note: Builds can take 2-5 minutes each...")
        
        # Original build
        duration, success = run_command_with_timing(
            "build_and_test.bat", 
            "Original Build Pipeline"
        )
        results['original_build'] = {'time': duration, 'success': success}
        
        if success:
            # Check original executable size
            if os.path.exists("dist/AutoCrate.exe"):
                original_size = os.path.getsize("dist/AutoCrate.exe") / (1024*1024)
                results['original_size'] = original_size
                print(f"   [SIZE] Original Size: {original_size:.1f} MB")
        
        # Clean up for optimized build
        if os.path.exists("dist"):
            subprocess.run("rmdir /s /q dist", shell=True, capture_output=True)
        if os.path.exists("build"):
            subprocess.run("rmdir /s /q build", shell=True, capture_output=True)
            
        # Optimized build
        duration, success = run_command_with_timing(
            "build_and_test_optimized.bat", 
            "Optimized Build Pipeline"
        )
        results['optimized_build'] = {'time': duration, 'success': success}
        
        if success:
            # Check optimized executable size
            if os.path.exists("dist/AutoCrate.exe"):
                optimized_size = os.path.getsize("dist/AutoCrate.exe") / (1024*1024)
                results['optimized_size'] = optimized_size
                print(f"   [SIZE] Optimized Size: {optimized_size:.1f} MB")
    
    # Final Results Summary
    print("\n\n" + "=" * 60)
    print("PERFORMANCE SUMMARY")
    print("=" * 60)
    
    # Test results
    if 'original_test' in results and 'optimized_test' in results:
        orig_time = results['original_test']['time']
        opt_time = results['optimized_test']['time']
        
        print(f"\n[TEST] TESTING PERFORMANCE:")
        print(f"   Original: {orig_time:.2f}s")
        print(f"   Optimized: {opt_time:.2f}s")
        
        if opt_time < orig_time:
            improvement = ((orig_time - opt_time) / orig_time) * 100
            speedup = orig_time / opt_time
            print(f"   [PASS] {improvement:.1f}% faster ({speedup:.1f}x speedup)")
        else:
            print(f"   [FAIL] No improvement")
    
    # Build results
    if 'original_build' in results and 'optimized_build' in results:
        orig_time = results['original_build']['time']
        opt_time = results['optimized_build']['time']
        
        print(f"\n[BUILD] BUILD PERFORMANCE:")
        print(f"   Original: {orig_time:.1f}s ({orig_time/60:.1f}m)")
        print(f"   Optimized: {opt_time:.1f}s ({opt_time/60:.1f}m)")
        
        if opt_time < orig_time:
            improvement = ((orig_time - opt_time) / orig_time) * 100
            time_saved = orig_time - opt_time
            print(f"   [PASS] {improvement:.1f}% faster ({time_saved:.0f}s saved)")
        else:
            print(f"   [FAIL] No improvement")
    
    # Size results
    if 'original_size' in results and 'optimized_size' in results:
        orig_size = results['original_size']
        opt_size = results['optimized_size']
        
        print(f"\n[SIZE] EXECUTABLE SIZE:")
        print(f"   Original: {orig_size:.1f} MB")
        print(f"   Optimized: {opt_size:.1f} MB")
        
        if opt_size < orig_size:
            reduction = ((orig_size - opt_size) / orig_size) * 100
            saved_mb = orig_size - opt_size
            print(f"   [PASS] {reduction:.1f}% smaller ({saved_mb:.1f} MB saved)")
        else:
            print(f"   [FAIL] No size reduction")
    
    print("\n" + "=" * 60)
    print("Performance test completed!")
    
    # Return success status
    return 0 if all(r.get('success', False) for r in results.values()) else 1

if __name__ == "__main__":
    sys.exit(main())