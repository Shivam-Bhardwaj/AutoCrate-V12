#!/usr/bin/env python3
"""
AutoCrate V12 - Redundant File Cleanup Script
Identifies and removes duplicate, temporary, and unnecessary files
"""

import os
import shutil
from pathlib import Path
import json

def cleanup_redundant_files():
    """Remove redundant files from the project"""
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    cleanup_report = {
        "removed_files": [],
        "moved_files": [],
        "kept_files": [],
        "errors": []
    }
    
    # Files to remove (redundant/temporary/debug)
    files_to_remove = [
        # Redundant test files (keep only essential ones)
        "test_nx_web_generation.py",
        "test_nx_generation_comparison.py", 
        "test_web_nx_comparison.py",
        "test_nx_comparison.py",
        "test_nx_direct_comparison.py",
        "test_output_diff.py",
        "test_api_direct.py",
        "test_web_integration.py",
        "test_desktop_direct.py",
        "test_nx_simple.py",
        "test_cleat_material.py",
        "test_material_calc.py",
        
        # Debug/trace files (move to debug folder)
        "analyze_logs.py",
        "analyze_logs_simple.py", 
        "trace_material_addition.py",
        "trace_web_calc.py",
        "trace_desktop_calc.py",
        "trace_calculation_values.py",
        "debug_nx_generation.py",
        "compare_nx_outputs.py",
        "compare_nx_detailed.py",
        "verify_nx_match.py",
        
        # Temporary/utility files
        "fix_prompt.py",
        "validate_professional_language.py",
        "validate_ascii.py", 
        "build_performance_test.py",
        "quick_test_parallel.py",
        "generate_nx_offline.py",
        "minimal_importer.py",
        "smoke_nx_expr.py",
        "config.py",
        
        # Old batch files (keep only essential ones)
        "nx_generator_bridge.bat",
        "restart_api_server.bat",
        
        # Replace problematic dev_suite.bat
        "dev_suite.bat"
    ]
    
    # Files to move to debug folder
    debug_files = [
        "analyze_logs.py",
        "analyze_logs_simple.py",
        "trace_material_addition.py", 
        "trace_web_calc.py",
        "trace_desktop_calc.py",
        "trace_calculation_values.py",
        "debug_nx_generation.py",
        "compare_nx_outputs.py",
        "compare_nx_detailed.py",
        "verify_nx_match.py",
        "build_performance_test.py",
        "quick_test_parallel.py"
    ]
    
    # Create debug directory if it doesn't exist
    debug_dir = Path("debug")
    debug_dir.mkdir(exist_ok=True)
    
    # Move debug files first
    for file_name in debug_files:
        file_path = Path(file_name)
        if file_path.exists():
            try:
                dest_path = debug_dir / file_name
                shutil.move(str(file_path), str(dest_path))
                cleanup_report["moved_files"].append(f"{file_name} -> debug/{file_name}")
                print(f"Moved: {file_name} -> debug/")
            except Exception as e:
                cleanup_report["errors"].append(f"Error moving {file_name}: {e}")
                print(f"Error moving {file_name}: {e}")
    
    # Remove redundant files
    for file_name in files_to_remove:
        if file_name not in debug_files:  # Don't remove if already moved
            file_path = Path(file_name)
            if file_path.exists():
                try:
                    file_path.unlink()
                    cleanup_report["removed_files"].append(file_name)
                    print(f"Removed: {file_name}")
                except Exception as e:
                    cleanup_report["errors"].append(f"Error removing {file_name}: {e}")
                    print(f"Error removing {file_name}: {e}")
    
    # Replace dev_suite.bat with fixed version
    try:
        if Path("dev_suite_fixed.bat").exists():
            if Path("dev_suite.bat").exists():
                Path("dev_suite.bat").unlink()
            shutil.move("dev_suite_fixed.bat", "dev_suite.bat")
            cleanup_report["moved_files"].append("dev_suite_fixed.bat -> dev_suite.bat")
            print("Replaced dev_suite.bat with fixed version")
    except Exception as e:
        cleanup_report["errors"].append(f"Error replacing dev_suite.bat: {e}")
    
    # Clean up temporary files and directories
    temp_patterns = [
        "*.tmp",
        "*.temp", 
        "nul",
        "*.log",
        "*.prof",
        "comparison_report_*.txt",
        "desktop_*.exp",
        "web_api_*.exp", 
        "desktop_key_values.txt",
        "desktop_nx_output*.json",
        "nx_test_results_*.json",
        "quick_test_.log",
        "test_debug.log",
        "test_output_diff.log",
        "error_detail_*.json",
        "session_summary_*.json",
        "performance_*.json"
    ]
    
    for pattern in temp_patterns:
        for file_path in Path(".").glob(pattern):
            try:
                if file_path.is_file():
                    file_path.unlink()
                    cleanup_report["removed_files"].append(str(file_path))
                    print(f"Removed temp file: {file_path}")
            except Exception as e:
                cleanup_report["errors"].append(f"Error removing {file_path}: {e}")
    
    # Clean up empty directories
    empty_dirs = []
    for root, dirs, files in os.walk(".", topdown=False):
        for dir_name in dirs:
            dir_path = Path(root) / dir_name
            try:
                if not any(dir_path.iterdir()):  # Directory is empty
                    dir_path.rmdir()
                    empty_dirs.append(str(dir_path))
                    print(f"Removed empty directory: {dir_path}")
            except Exception as e:
                cleanup_report["errors"].append(f"Error removing directory {dir_path}: {e}")
    
    # Clean up __pycache__ directories
    for pycache_dir in Path(".").rglob("__pycache__"):
        try:
            shutil.rmtree(pycache_dir)
            cleanup_report["removed_files"].append(str(pycache_dir))
            print(f"Removed: {pycache_dir}")
        except Exception as e:
            cleanup_report["errors"].append(f"Error removing {pycache_dir}: {e}")
    
    # Generate cleanup report
    with open("debug/cleanup_report.json", "w") as f:
        json.dump(cleanup_report, f, indent=2)
    
    print("\n" + "="*50)
    print("CLEANUP SUMMARY")
    print("="*50)
    print(f"Files removed: {len(cleanup_report['removed_files'])}")
    print(f"Files moved: {len(cleanup_report['moved_files'])}")
    print(f"Errors: {len(cleanup_report['errors'])}")
    print(f"\nReport saved to: debug/cleanup_report.json")
    
    if cleanup_report['errors']:
        print("\nErrors encountered:")
        for error in cleanup_report['errors']:
            print(f"  - {error}")
    
    return cleanup_report

if __name__ == "__main__":
    cleanup_redundant_files()