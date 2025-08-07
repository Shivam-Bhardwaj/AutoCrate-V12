"""
Utility script to clean up duplicate expression files in the expressions folder.
Keeps only the latest version of each unique parameter combination.
"""

import os
import sys
from collections import defaultdict

# Add autocrate to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'autocrate'))

from autocrate.expression_file_manager import ExpressionFileManager, ExpressionParameters

def clean_expressions_folder(expressions_dir: str, dry_run: bool = True):
    """
    Clean up duplicate expression files in the specified directory.
    
    Args:
        expressions_dir: Path to the expressions directory
        dry_run: If True, only show what would be deleted without actually deleting
    """
    
    if not os.path.exists(expressions_dir):
        print(f"Error: Directory does not exist: {expressions_dir}")
        return
    
    manager = ExpressionFileManager(expressions_dir)
    
    # Group files by their parameters
    parameter_groups = defaultdict(list)
    
    print(f"Scanning directory: {expressions_dir}")
    print("=" * 60)
    
    # Scan all .exp files
    exp_files = [f for f in os.listdir(expressions_dir) if f.endswith('.exp')]
    
    for filename in exp_files:
        filepath = os.path.join(expressions_dir, filename)
        params = manager.parse_filename(filename)
        
        if params:
            # Create a key based on parameters
            key = (
                round(params.length, 1),
                round(params.width, 1),
                round(params.height, 1),
                round(params.weight, 1),
                params.material_type,
                round(params.panel_thickness, 2),
                round(params.clearance, 1)
            )
            parameter_groups[key].append({
                'filename': filename,
                'filepath': filepath,
                'timestamp': params.timestamp or '00000000_000000',
                'params': params
            })
        else:
            print(f"Warning: Could not parse filename: {filename}")
    
    # Find duplicates
    duplicates_found = False
    total_files_to_delete = 0
    
    for key, files in parameter_groups.items():
        if len(files) > 1:
            duplicates_found = True
            # Sort by timestamp to keep the latest
            files.sort(key=lambda x: x['timestamp'], reverse=True)
            
            print(f"\nFound {len(files)} files with parameters:")
            print(f"  Dimensions: {key[0]}x{key[1]}x{key[2]}")
            print(f"  Weight: {key[3]} lbs")
            print(f"  Material: {key[4]} {key[5]}\"")
            print(f"  Clearance: {key[6]}\"")
            print("\n  Files:")
            
            for i, file_info in enumerate(files):
                if i == 0:
                    print(f"    [KEEP]   {file_info['filename']}")
                else:
                    print(f"    [DELETE] {file_info['filename']}")
                    total_files_to_delete += 1
                    
                    if not dry_run:
                        try:
                            os.remove(file_info['filepath'])
                            print(f"             -> Deleted")
                        except Exception as e:
                            print(f"             -> Error deleting: {e}")
    
    # Also check quick_test subdirectory if it exists
    quick_test_dir = os.path.join(expressions_dir, "quick_test")
    if os.path.exists(quick_test_dir):
        print("\n" + "=" * 60)
        print("Checking quick_test subdirectory...")
        clean_expressions_folder(quick_test_dir, dry_run)
    
    # Summary
    if not duplicates_found:
        print("\nNo duplicate expressions found.")
    else:
        print("\n" + "=" * 60)
        if dry_run:
            print(f"DRY RUN: Would delete {total_files_to_delete} duplicate file(s)")
            print("Run with --execute to actually delete the files")
        else:
            print(f"Deleted {total_files_to_delete} duplicate file(s)")

def main():
    """Main function to run the cleanup."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Clean up duplicate expression files based on parameters"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually delete duplicate files (default is dry run)"
    )
    parser.add_argument(
        "--dir",
        default="expressions",
        help="Directory to clean (default: expressions)"
    )
    
    args = parser.parse_args()
    
    # Get the expressions directory
    if os.path.isabs(args.dir):
        expressions_dir = args.dir
    else:
        expressions_dir = os.path.join(os.path.dirname(__file__), args.dir)
    
    print("AutoCrate Expression File Cleanup Utility")
    print("=" * 60)
    
    if not args.execute:
        print("Running in DRY RUN mode - no files will be deleted")
        print("Use --execute flag to actually delete duplicate files")
        print("=" * 60)
    
    clean_expressions_folder(expressions_dir, dry_run=not args.execute)

if __name__ == "__main__":
    main()