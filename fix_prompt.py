#!/usr/bin/env python3
"""
Fix Prompt - Automated test analysis and code fixing
Run when user says "fix" to analyze test results and implement solutions
"""

import os
import shutil
import datetime
from pathlib import Path

def backup_test_results():
    """Backup current test results to legacy folder"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    legacy_folder = Path("legacy_tests") / f"test_session_{timestamp}"
    
    # Create legacy folder
    legacy_folder.mkdir(parents=True, exist_ok=True)
    
    # Copy test_results to legacy
    test_results = Path("test_results")
    if test_results.exists():
        shutil.copytree(test_results, legacy_folder / "test_results", dirs_exist_ok=True)
        print(f"[SUCCESS] Backed up tests to: {legacy_folder}")
        return legacy_folder
    else:
        print("[ERROR] No test_results folder found")
        return None

def read_test_notes():
    """Read and parse test notes"""
    notes_file = Path("test_results/test_notes.txt")
    if not notes_file.exists():
        print("[ERROR] No test_notes.txt found")
        return []
    
    with open(notes_file, 'r') as f:
        content = f.read()
    
    # Parse test entries
    test_entries = []
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if line and '.png' in line and ' - ' in line:
            parts = line.split(' - ')
            if len(parts) >= 3:
                screenshot = parts[0].strip()
                dimensions = parts[1].strip()
                observation = ' - '.join(parts[2:]).strip()
                test_entries.append({
                    'screenshot': screenshot,
                    'dimensions': dimensions,
                    'observation': observation
                })
    
    return test_entries

def analyze_issues(test_entries):
    """Analyze test entries for common issues"""
    issues = []
    for entry in test_entries:
        obs = entry['observation'].lower()
        if 'error' in obs or 'failed' in obs or '❌' in obs:
            issues.append({
                'type': 'error',
                'entry': entry,
                'severity': 'high'
            })
        elif 'slow' in obs or 'performance' in obs:
            issues.append({
                'type': 'performance', 
                'entry': entry,
                'severity': 'medium'
            })
        elif 'weird' in obs or '⚠️' in obs or 'unexpected' in obs:
            issues.append({
                'type': 'unexpected',
                'entry': entry, 
                'severity': 'medium'
            })
    
    return issues

def clear_test_folder():
    """Clear test_results folder for fresh testing"""
    test_results = Path("test_results")
    screenshots = test_results / "screenshots"
    
    # Clear screenshots
    if screenshots.exists():
        for file in screenshots.glob("*.png"):
            file.unlink()
        print("[SUCCESS] Cleared screenshots")
    
    # Reset test notes
    notes_file = test_results / "test_notes.txt"
    if notes_file.exists():
        with open(notes_file, 'w') as f:
            f.write("AutoCrate Test Notes\n")
            f.write("====================\n\n")
            f.write("Format: screenshot_name - dimensions, weight - observation\n\n")
            f.write("Your tests:\n")
            f.write("-----------\n")
        print("[SUCCESS] Reset test notes")

def generate_fix_summary(test_entries, issues, backup_location):
    """Generate summary for AI agent"""
    summary = f"""
# Fix Analysis Summary

## Test Session Backup
Location: {backup_location}

## Tests Analyzed
Total tests: {len(test_entries)}
Issues found: {len(issues)}

## Test Results Overview
"""
    
    for entry in test_entries:
        summary += f"- {entry['screenshot']}: {entry['dimensions']} - {entry['observation']}\n"
    
    summary += "\n## Issues Identified\n"
    for issue in issues:
        entry = issue['entry']
        summary += f"- **{issue['type'].upper()}** ({issue['severity']}): {entry['dimensions']} - {entry['observation']}\n"
    
    summary += "\n## Ready for AI Analysis\n"
    summary += "The test results have been backed up and the folder cleared for next iteration.\n"
    summary += "Recommend using nx-expression-engineer agent for AutoCrate-specific fixes.\n"
    
    return summary

def main():
    """Main fix prompt execution"""
    print("[FIX] AutoCrate Fix Prompt Activated")
    print("=" * 40)
    
    # Step 1: Backup
    backup_location = backup_test_results()
    if not backup_location:
        return
    
    # Step 2: Read tests
    test_entries = read_test_notes()
    print(f"[INFO] Read {len(test_entries)} test entries")
    
    # Step 3: Analyze
    issues = analyze_issues(test_entries)
    print(f"[INFO] Found {len(issues)} issues to address")
    
    # Step 4: Generate summary
    summary = generate_fix_summary(test_entries, issues, backup_location)
    
    # Step 5: Clear for next iteration
    clear_test_folder()
    
    # Output summary
    print("\n" + summary)
    
    # Save summary for AI agent
    summary_file = backup_location / "fix_analysis.md"
    with open(summary_file, 'w') as f:
        f.write(summary)
    
    print(f"\n[SUCCESS] Fix analysis complete. Summary saved to: {summary_file}")
    print("[SUCCESS] Ready for next test iteration!")

if __name__ == "__main__":
    main()