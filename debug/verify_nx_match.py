"""
Verify that NX expressions from desktop and web are identical
"""
import subprocess
import difflib
import sys

def compare_files(file1, file2):
    """Compare two files line by line, ignoring timestamp differences"""
    with open(file1, 'r') as f1:
        lines1 = f1.readlines()
    with open(file2, 'r') as f2:
        lines2 = f2.readlines()
    
    # Skip timestamp line (line 2)
    if len(lines1) > 2 and len(lines2) > 2:
        lines1[1] = "// Generated: [TIMESTAMP]\n"
        lines2[1] = "// Generated: [TIMESTAMP]\n"
    
    # Compare
    diff = list(difflib.unified_diff(lines1, lines2, fromfile=file1, tofile=file2, n=0))
    
    if not diff:
        print("[SUCCESS] Files are IDENTICAL (except timestamps)")
        return True
    else:
        print("[ERROR] Files have differences:")
        for line in diff[:20]:
            print(line.rstrip())
        return False

def main():
    print("="*60)
    print("NX EXPRESSION VERIFICATION")
    print("="*60)
    
    # Run the comparison test
    result = subprocess.run([sys.executable, "test_nx_direct_comparison.py"], 
                          capture_output=True, text=True)
    
    # Check for the latest generated files
    import glob
    import os
    
    desktop_files = sorted(glob.glob("desktop_*.exp"), key=os.path.getmtime)
    web_files = sorted(glob.glob("web_api_*.exp"), key=os.path.getmtime)
    
    if desktop_files and web_files:
        latest_desktop = desktop_files[-1]
        latest_web = web_files[-1]
        
        print(f"\nComparing:")
        print(f"  Desktop: {latest_desktop}")
        print(f"  Web:     {latest_web}")
        print("-"*60)
        
        if compare_files(latest_desktop, latest_web):
            print("\n[SUCCESS] NX expressions are now IDENTICAL!")
            print("You can import either file into NX without errors.")
        else:
            print("\n[WARNING] Files still have differences.")
            print("Check the comparison output above.")
    else:
        print("[ERROR] Could not find generated expression files")

if __name__ == "__main__":
    main()