#!/usr/bin/env python
"""
Simple test to verify KL_1_X and KL_1_Z variables are in the generated expression
"""

import os
import glob

# Find a recent expression file
expression_files = glob.glob("expressions/*.exp") + glob.glob("expressions/quick_test/*.exp")
if expression_files:
    # Sort by modification time and get the most recent
    expression_files.sort(key=os.path.getmtime, reverse=True)
    latest_file = expression_files[0]
    
    print(f"Checking expression file: {latest_file}")
    print("=" * 60)
    
    with open(latest_file, 'r') as f:
        content = f.read()
    
    # Check for KL_1_Z
    found_kl_z = False
    for line in content.split('\n'):
        if '[Inch]KL_1_Z' in line:
            print(f"FOUND KL_1_Z: {line.strip()}")
            found_kl_z = True
            break
    
    if not found_kl_z:
        print("KL_1_Z variable NOT FOUND in expression file")
    
    # Check for KL_1_X
    found_kl_x = False
    for line in content.split('\n'):
        if '[Inch]KL_1_X' in line:
            print(f"FOUND KL_1_X: {line.strip()}")
            found_kl_x = True
            break
    
    if not found_kl_x:
        print("KL_1_X variable NOT FOUND in expression file")
    
    print("\n" + "=" * 60)
    if found_kl_z and found_kl_x:
        print("SUCCESS: Both KL_1_X and KL_1_Z variables are present!")
    elif found_kl_z:
        print("PARTIAL: Only KL_1_Z is present, KL_1_X is missing")
    elif found_kl_x:
        print("PARTIAL: Only KL_1_X is present, KL_1_Z is missing")
    else:
        print("FAILURE: Neither KL_1_X nor KL_1_Z variables found")
        
else:
    print("No expression files found in expressions/ directory")