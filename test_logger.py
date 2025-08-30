#!/usr/bin/env python3
"""
Simple test logger for rapid AutoCrate testing
Run: python test_logger.py
"""

import datetime
import os
from pathlib import Path

def create_test_log():
    """Create a simple test log file"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"test_log_{timestamp}.txt"
    
    with open(log_file, 'w') as f:
        f.write(f"AutoCrate Test Log - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*50 + "\n\n")
        f.write("QUICK TEST TEMPLATE:\n")
        f.write("Test: [what you're testing]\n")
        f.write("Input: L_W_H_weight\n") 
        f.write("Result: [PASS/FAIL/WARN]\n")
        f.write("Screenshot: [filename]\n")
        f.write("Notes: [one line]\n")
        f.write("\n" + "-"*30 + "\n\n")
        
        # Add some pre-filled common tests
        common_tests = [
            ("Basic Function", "48x48x48, 1000 lbs"),
            ("Very Tall", "20x20x100, 500 lbs"), 
            ("Very Wide", "100x100x20, 2000 lbs"),
            ("Small Size", "12x12x12, 50 lbs")
        ]
        
        for test_name, dimensions in common_tests:
            f.write(f"Test: {test_name}\n")
            f.write(f"Input: {dimensions}\n")
            f.write("Result: [PASS/FAIL/WARN]\n")
            f.write("Screenshot: []\n")
            f.write("Notes: []\n")
            f.write("\n" + "-"*30 + "\n\n")
    
    print(f"Created test log: {log_file}")
    print("Fill it out as you test, then use for prompt refinement.")
    
    # Try to open the file
    try:
        os.startfile(log_file)
        print("Opened in default editor.")
    except:
        print("Open the file manually to start logging.")

if __name__ == "__main__":
    create_test_log()