"""
Test script to verify NX expression generation for web version
"""

import sys
import os

# Add API directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))

from nx_expression_service import generate_full_nx_expression_content

# Test 1: Default values
print("Test 1: Default values (48x36x24, 1000 lbs)")
content1 = generate_full_nx_expression_content(
    product_weight=1000,
    product_length=48,
    product_width=36,
    product_height=24
)

# Extract key values from generated content
lines1 = content1.split('\n')
key_values1 = {}
for line in lines1:
    if 'product_weight =' in line:
        key_values1['weight'] = line
    elif 'product_length_input =' in line:
        key_values1['length'] = line
    elif 'product_width_input =' in line:
        key_values1['width'] = line
    elif 'crate_overall_width_OD =' in line:
        key_values1['crate_width'] = line
    elif 'crate_overall_length_OD =' in line:
        key_values1['crate_length'] = line
    elif 'FP_Panel_Assembly_Width =' in line:
        key_values1['front_width'] = line

print("Key values from Test 1:")
for key, value in key_values1.items():
    print(f"  {key}: {value}")

print("\n" + "="*50 + "\n")

# Test 2: Different values
print("Test 2: Changed values (60x48x36, 2000 lbs)")
content2 = generate_full_nx_expression_content(
    product_weight=2000,
    product_length=60,
    product_width=48,
    product_height=36,
    clearance=3.0  # Different clearance too
)

lines2 = content2.split('\n')
key_values2 = {}
for line in lines2:
    if 'product_weight =' in line:
        key_values2['weight'] = line
    elif 'product_length_input =' in line:
        key_values2['length'] = line
    elif 'product_width_input =' in line:
        key_values2['width'] = line
    elif 'crate_overall_width_OD =' in line:
        key_values2['crate_width'] = line
    elif 'crate_overall_length_OD =' in line:
        key_values2['crate_length'] = line
    elif 'FP_Panel_Assembly_Width =' in line:
        key_values2['front_width'] = line

print("Key values from Test 2:")
for key, value in key_values2.items():
    print(f"  {key}: {value}")

print("\n" + "="*50 + "\n")

# Compare values
print("Comparison:")
for key in key_values1:
    if key in key_values2:
        if key_values1[key] == key_values2[key]:
            print(f"  {key}: UNCHANGED (ERROR - should be different!)")
        else:
            print(f"  {key}: CHANGED (OK)")
            print(f"    Test 1: {key_values1[key]}")
            print(f"    Test 2: {key_values2[key]}")
    
print("\nExpected behavior: All dimension-related values should change when inputs change")
print("If crate dimensions don't change with product dimensions, that's the bug!")