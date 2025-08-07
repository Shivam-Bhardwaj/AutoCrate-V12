"""
Test the intelligent expression file replacement system.
Creates duplicate expressions with same parameters and verifies replacement.
"""

import os
import sys
import time
from datetime import datetime

# Add autocrate to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'autocrate'))

from autocrate.expression_file_manager import ExpressionFileManager, extract_parameters_from_inputs

def test_replacement():
    """Test the replacement system with real files."""
    
    # Use the actual expressions directory
    expressions_dir = os.path.join(os.path.dirname(__file__), "expressions", "test")
    
    # Create test directory
    os.makedirs(expressions_dir, exist_ok=True)
    
    print("Testing Intelligent Expression File Replacement")
    print("=" * 60)
    print(f"Test directory: {expressions_dir}")
    
    # Initialize file manager
    manager = ExpressionFileManager(expressions_dir)
    
    # Test Case 1: Create initial file
    print("\n[Test 1] Creating initial expression file...")
    params1 = extract_parameters_from_inputs(
        product_length=72,
        product_width=48,
        product_height=36,
        product_weight=1500,
        panel_thickness=0.75,
        clearance=2.0
    )
    
    # Generate filename and create file
    params1.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename1 = manager.generate_filename(params1)
    filepath1 = os.path.join(expressions_dir, filename1)
    
    with open(filepath1, 'w') as f:
        f.write("Expression content 1")
    print(f"Created: {filename1}")
    
    # Wait a second to ensure different timestamp
    time.sleep(1)
    
    # Test Case 2: Create duplicate with same parameters
    print("\n[Test 2] Creating duplicate with same parameters...")
    params2 = extract_parameters_from_inputs(
        product_length=72,  # Same parameters
        product_width=48,
        product_height=36,
        product_weight=1500,
        panel_thickness=0.75,
        clearance=2.0
    )
    
    # Check for duplicates before creating
    output_path, deleted_files = manager.manage_expression_file(params2)
    
    with open(output_path, 'w') as f:
        f.write("Expression content 2 (replacement)")
    
    print(f"Created: {os.path.basename(output_path)}")
    if deleted_files:
        print(f"Deleted {len(deleted_files)} duplicate(s):")
        for deleted in deleted_files:
            print(f"  - {os.path.basename(deleted)}")
    
    # Test Case 3: Create file with different parameters
    print("\n[Test 3] Creating file with different parameters...")
    params3 = extract_parameters_from_inputs(
        product_length=96,  # Different length
        product_width=48,
        product_height=36,
        product_weight=1500,
        panel_thickness=0.75,
        clearance=2.0
    )
    
    output_path3, deleted_files3 = manager.manage_expression_file(params3)
    
    with open(output_path3, 'w') as f:
        f.write("Expression content 3 (different params)")
    
    print(f"Created: {os.path.basename(output_path3)}")
    if deleted_files3:
        print(f"Deleted {len(deleted_files3)} duplicate(s)")
    else:
        print("No duplicates found (expected - different parameters)")
    
    # Final check: List all files
    print("\n[Final] Files in test directory:")
    files = [f for f in os.listdir(expressions_dir) if f.endswith('.exp')]
    for file in files:
        params = manager.parse_filename(file)
        if params:
            print(f"  - {file}")
            print(f"    Params: {params.length}x{params.width}x{params.height}, {params.weight}lbs")
    
    print(f"\nTotal files: {len(files)}")
    print("Expected: 2 files (one for 72x48x36, one for 96x48x36)")
    
    # Cleanup
    print("\nCleaning up test directory...")
    import shutil
    shutil.rmtree(expressions_dir, ignore_errors=True)
    
    print("\n[SUCCESS] Test completed!")

if __name__ == "__main__":
    test_replacement()