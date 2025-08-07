#!/usr/bin/env python3
"""
ASCII Validation Script for AutoCrate
Validates that all Python files contain only ASCII characters (0-127).
"""

import os
import sys
from pathlib import Path
import re
from typing import List, Tuple

def find_non_ascii_chars(file_path: Path) -> List[Tuple[int, str, List[str]]]:
    """
    Find non-ASCII characters in a file.
    
    Returns:
        List of (line_number, line_content, non_ascii_chars)
    """
    violations = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                non_ascii_chars = []
                for char in line:
                    if ord(char) >= 128:
                        if char not in non_ascii_chars:
                            non_ascii_chars.append(char)
                
                if non_ascii_chars:
                    violations.append((line_num, line.strip(), non_ascii_chars))
    except UnicodeDecodeError as e:
        violations.append((0, f"File encoding error: {e}", []))
    except Exception as e:
        violations.append((0, f"Error reading file: {e}", []))
    
    return violations

def validate_python_files(root_dir: Path) -> bool:
    """
    Validate all Python files in the directory tree.
    
    Returns:
        True if all files are ASCII-compliant, False otherwise
    """
    print("AutoCrate ASCII Validation Tool")
    print("=" * 40)
    
    python_files = list(root_dir.rglob("*.py"))
    if not python_files:
        print("No Python files found.")
        return True
    
    print(f"Scanning {len(python_files)} Python files...")
    print()
    
    total_violations = 0
    files_with_violations = 0
    
    for py_file in sorted(python_files):
        violations = find_non_ascii_chars(py_file)
        
        if violations:
            files_with_violations += 1
            total_violations += len(violations)
            
            relative_path = py_file.relative_to(root_dir)
            print(f"[FAIL] {relative_path}")
            
            for line_num, line_content, non_ascii_chars in violations:
                if line_num == 0:  # Error case
                    print(f"  ERROR: {line_content}")
                else:
                    char_display = ", ".join([f"U+{ord(char):04X}" for char in non_ascii_chars])
                    print(f"  Line {line_num}: Non-ASCII chars: {char_display}")
                    # Replace non-ASCII with placeholders for display
                    safe_content = ''.join([char if ord(char) < 128 else f'[U+{ord(char):04X}]' for char in line_content])
                    print(f"    Content: {safe_content}")
            print()
    
    # Summary
    compliant_files = len(python_files) - files_with_violations
    print("=" * 40)
    print("VALIDATION SUMMARY")
    print("=" * 40)
    print(f"Total files scanned: {len(python_files)}")
    print(f"ASCII-compliant files: {compliant_files}")
    print(f"Files with violations: {files_with_violations}")
    print(f"Total violations: {total_violations}")
    
    if files_with_violations == 0:
        print()
        print("[PASS] All Python files are ASCII-compliant!")
        return True
    else:
        print()
        print("[FAIL] Non-ASCII characters found in Python files.")
        print()
        print("COMMON REPLACEMENTS:")
        print("  U+2713 -> 'PASS' or 'SUCCESS'")
        print("  U+274C -> 'FAIL' or 'ERROR'")
        print("  U+26A0 -> 'WARNING' or 'WARN'")
        print("  U+2192 -> '->' or '-->'")
        print("  U+2022 -> '-' or '*'")
        print()
        print("See CODING_STANDARDS.md for full replacement guidelines.")
        return False

def main():
    """Main entry point."""
    root_dir = Path.cwd()
    
    # Allow specifying a different directory
    if len(sys.argv) > 1:
        root_dir = Path(sys.argv[1])
        if not root_dir.exists():
            print(f"Error: Directory '{root_dir}' does not exist.")
            sys.exit(1)
    
    print(f"Validating ASCII compliance in: {root_dir}")
    print()
    
    is_compliant = validate_python_files(root_dir)
    
    # Exit with appropriate code
    sys.exit(0 if is_compliant else 1)

if __name__ == "__main__":
    main()