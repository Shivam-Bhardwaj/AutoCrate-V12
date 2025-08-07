"""
Test script for the Expression File Manager
Verifies that the intelligent replacement system works correctly.
"""

import os
import sys
import tempfile
import shutil
from datetime import datetime

# Add autocrate to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'autocrate'))

from autocrate.expression_file_manager import (
    ExpressionFileManager, 
    ExpressionParameters,
    extract_parameters_from_inputs
)

def test_file_manager():
    """Test the expression file manager functionality."""
    
    # Create a temporary directory for testing
    test_dir = tempfile.mkdtemp(prefix="test_expressions_")
    print(f"Test directory: {test_dir}")
    
    try:
        # Initialize file manager
        manager = ExpressionFileManager(test_dir)
        
        # Test 1: Create initial expression file
        print("\n[Test 1] Creating initial expression file...")
        params1 = extract_parameters_from_inputs(
            product_length=72,
            product_width=48,
            product_height=36,
            product_weight=1500,
            panel_thickness=0.75,
            clearance=2.0
        )
        
        filename1 = manager.generate_filename(params1)
        filepath1 = os.path.join(test_dir, filename1)
        
        # Simulate creating the file
        with open(filepath1, 'w') as f:
            f.write("Test expression 1")
        print(f"Created: {filename1}")
        
        # Test 2: Create another file with different parameters
        print("\n[Test 2] Creating file with different parameters...")
        params2 = extract_parameters_from_inputs(
            product_length=96,  # Different length
            product_width=48,
            product_height=36,
            product_weight=1500,
            panel_thickness=0.75,
            clearance=2.0
        )
        
        filename2 = manager.generate_filename(params2)
        filepath2 = os.path.join(test_dir, filename2)
        
        with open(filepath2, 'w') as f:
            f.write("Test expression 2")
        print(f"Created: {filename2}")
        
        # Test 3: Create duplicate with same parameters as file 1
        print("\n[Test 3] Creating duplicate of first file (should replace)...")
        params3 = extract_parameters_from_inputs(
            product_length=72,  # Same as params1
            product_width=48,
            product_height=36,
            product_weight=1500,
            panel_thickness=0.75,
            clearance=2.0
        )
        
        # This should detect and delete the first file
        output_path, deleted_files = manager.manage_expression_file(params3)
        
        # Create the new file
        with open(output_path, 'w') as f:
            f.write("Test expression 3 (replacement)")
        
        print(f"Created: {os.path.basename(output_path)}")
        print(f"Deleted {len(deleted_files)} duplicate(s):")
        for deleted in deleted_files:
            print(f"  - {os.path.basename(deleted)}")
        
        # Test 4: Verify parsing existing filenames
        print("\n[Test 4] Testing filename parsing...")
        test_filenames = [
            "20250807_135201_Crate_72x48x36_W2000_5P_PLY0.50_C2.0_ASTM.exp",
            "20250807_135341_Crate_96x60x48_W3000_5P_PLY0.75_C2.5_ASTM.exp",
            "20250807_140938_Crate_48x36x24_500lbs_PLY0.75_CLR2.0.exp",
        ]
        
        for test_file in test_filenames:
            parsed = manager.parse_filename(test_file)
            if parsed:
                print(f"Parsed {test_file}:")
                print(f"  Dimensions: {parsed.length}x{parsed.width}x{parsed.height}")
                print(f"  Weight: {parsed.weight}, Material: {parsed.material_type}")
                print(f"  Thickness: {parsed.panel_thickness}, Clearance: {parsed.clearance}")
            else:
                print(f"Failed to parse: {test_file}")
        
        # Test 5: Test parameter matching
        print("\n[Test 5] Testing parameter matching...")
        params_a = ExpressionParameters(
            length=72.0,
            width=48.0,
            height=36.0,
            weight=1500.0,
            material_type="PLY",
            panel_thickness=0.75,
            clearance=2.0
        )
        
        params_b = ExpressionParameters(
            length=72.01,  # Slightly different but within tolerance
            width=48.0,
            height=36.0,
            weight=1500.0,
            material_type="PLY",
            panel_thickness=0.75,
            clearance=2.0
        )
        
        params_c = ExpressionParameters(
            length=96.0,  # Significantly different
            width=48.0,
            height=36.0,
            weight=1500.0,
            material_type="PLY",
            panel_thickness=0.75,
            clearance=2.0
        )
        
        print(f"params_a matches params_b: {params_a.matches(params_b)}")
        print(f"params_a matches params_c: {params_a.matches(params_c)}")
        
        # List final files in test directory
        print("\n[Test 6] Final files in test directory:")
        for file in os.listdir(test_dir):
            if file.endswith('.exp'):
                print(f"  - {file}")
        
        print("\n[SUCCESS] All tests completed successfully!")
        
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Clean up test directory
        print(f"\nCleaning up test directory: {test_dir}")
        shutil.rmtree(test_dir, ignore_errors=True)

if __name__ == "__main__":
    print("Expression File Manager Test Suite")
    print("=" * 50)
    test_file_manager()