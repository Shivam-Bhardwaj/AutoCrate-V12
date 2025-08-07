#!/usr/bin/env python3
"""
Professional Language Validation Script for AutoCrate
Validates that all Python files use professional engineering terminology.
"""

import os
import sys
import re
from pathlib import Path
from typing import List, Tuple, Dict

# Define patterns for unprofessional language
UNPROFESSIONAL_PATTERNS = {
    'slang_informal': [
        r'\bbug\b(?![a-zA-Z_])',  # Avoid matching "debug"
        r'\bhack(?:y|ed)?\b',
        r'\bkludge\b',
        r'\bwonky\b',
        r'\bweird\b',
        r'\bcrazy\b',
        r'\bnasty\b',
        r'\bjanky\b',
        r'\bsketchy\b',
        r'\bdodgy\b',
    ],
    'casual_intensifiers': [
        r'\bvery\s+(?:large|big|small|fast|slow|good|bad)\b',
        r'\breally\s+(?:large|big|small|fast|slow|good|bad)\b',
        r'\bsuper\s+(?:large|big|small|fast|slow|good|bad)\b',
        r'\btotally\s+(?:large|big|small|fast|slow|good|bad)\b',
        r'\bpretty\s+(?:large|big|small|fast|slow|good|bad)\b',
        r'\bquite\s+(?:large|big|small|fast|slow|good|bad)\b',
        r'\bextremely\s+(?:large|big|small|fast|slow|good|bad)\b',
    ],
    'informal_expressions': [
        r'\bclearly\s+(?:better|worse|good|bad)\b',
        r'\bobviously\s+(?:better|worse|good|bad)\b',
        r'\bsimply\s+(?:better|worse|good|bad)\b',
        r'\bjust\s+(?:better|worse|good|bad)\b',
    ],
    'placeholder_terms': [
        r'\b(?:foo|bar|baz|qux|quux)\b',
        r'\bstuff\b',
        r'\bthings\b',
        r'\bthingy\b',
        r'\bwhatsit\b',
        r'\bdoohickey\b',
        r'\bgizmo\b',
        r'\bwidget\b(?!.*test)',  # Allow in test contexts
    ],
    'casual_speech': [
        r'\bgonna\b',
        r'\bkinda\b',
        r'\bsorta\b',
        r'\byeah\b',
        r'\bnope\b',
        r'\bwanna\b',
        r'\bdunno\b',
        r'\bokay\b',
    ],
    'informal_reactions': [
        r'\boops\b',
        r'\bwhoops\b',
        r'\buh[- ]?oh\b',
        r'\boh[- ]?no\b',
        r'\bdarn\b',
        r'\bjeez\b',
        r'\bwow\b',
        r'\bwhoa\b',
        r'\byay\b',
        r'\bbummer\b',
    ],
}

# Professional alternatives
PROFESSIONAL_ALTERNATIVES = {
    'bug': 'defect, issue, anomaly',
    'hack': 'temporary solution, workaround',
    'very large': 'maximum capacity, high-volume',
    'clearly better': 'optimal, preferred, more efficient',
    'weird': 'unexpected, anomalous',
    'wonky': 'unstable, inconsistent',
    'stuff': 'components, elements, parameters',
    'things': 'components, elements, items',
}

def find_unprofessional_language(file_path: Path) -> List[Tuple[int, str, str, str]]:
    """
    Find unprofessional language in a file.
    
    Returns:
        List of (line_number, category, matched_text, line_content)
    """
    violations = []
    
    # Skip validation script itself and definitions
    if file_path.name == 'validate_professional_language.py':
        return violations
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line_stripped = line.strip()
                
                # Skip lines that are legitimate uses (dictionary definitions, CSS classes)
                if (line_stripped.startswith("'") and "'" in line_stripped[1:] and ":" in line_stripped) or \
                   (".progress-bar" in line_stripped) or \
                   ("class=" in line_stripped and "bar" in line_stripped):
                    continue
                
                for category, patterns in UNPROFESSIONAL_PATTERNS.items():
                    for pattern in patterns:
                        matches = re.finditer(pattern, line, re.IGNORECASE)
                        for match in matches:
                            violations.append((
                                line_num, 
                                category, 
                                match.group(), 
                                line.strip()
                            ))
    except Exception as e:
        violations.append((0, "file_error", str(e), ""))
    
    return violations

def validate_professional_language(root_dir: Path) -> bool:
    """
    Validate professional language in all Python files.
    
    Returns:
        True if all files use professional language, False otherwise
    """
    print("AutoCrate Professional Language Validation Tool")
    print("=" * 50)
    
    python_files = list(root_dir.rglob("*.py"))
    if not python_files:
        print("No Python files found.")
        return True
    
    print(f"Scanning {len(python_files)} Python files for unprofessional language...")
    print()
    
    total_violations = 0
    files_with_violations = 0
    violations_by_category = {}
    
    for py_file in sorted(python_files):
        violations = find_unprofessional_language(py_file)
        
        if violations:
            files_with_violations += 1
            total_violations += len(violations)
            
            relative_path = py_file.relative_to(root_dir)
            print(f"[FAIL] {relative_path}")
            
            for line_num, category, matched_text, line_content in violations:
                if line_num == 0:  # File error
                    print(f"  ERROR: {matched_text}")
                else:
                    print(f"  Line {line_num}: [{category}] '{matched_text}'")
                    print(f"    Context: {line_content}")
                    
                    # Track violations by category
                    if category not in violations_by_category:
                        violations_by_category[category] = 0
                    violations_by_category[category] += 1
            print()
    
    # Summary
    compliant_files = len(python_files) - files_with_violations
    print("=" * 50)
    print("VALIDATION SUMMARY")
    print("=" * 50)
    print(f"Total files scanned: {len(python_files)}")
    print(f"Professional language compliant: {compliant_files}")
    print(f"Files with violations: {files_with_violations}")
    print(f"Total violations: {total_violations}")
    
    if violations_by_category:
        print("\nVIOLATIONS BY CATEGORY:")
        for category, count in sorted(violations_by_category.items()):
            print(f"  {category.replace('_', ' ').title()}: {count}")
    
    if files_with_violations == 0:
        print()
        print("[PASS] All Python files use professional language!")
        return True
    else:
        print()
        print("[FAIL] Unprofessional language found in Python files.")
        print()
        print("PROFESSIONAL ALTERNATIVES:")
        for informal, professional in PROFESSIONAL_ALTERNATIVES.items():
            print(f"  '{informal}' -> {professional}")
        print()
        print("See CODING_STANDARDS.md for complete guidelines.")
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
    
    print(f"Validating professional language in: {root_dir}")
    print()
    
    is_compliant = validate_professional_language(root_dir)
    
    # Exit with appropriate code
    sys.exit(0 if is_compliant else 1)

if __name__ == "__main__":
    main()