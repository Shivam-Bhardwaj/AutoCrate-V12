"""
Launch the threaded ultra-modern GUI for AutoCrate
This version doesn't freeze during test execution
"""

import sys
import os
from pathlib import Path

# Add autocrate directory to path
current_dir = Path(__file__).parent
autocrate_dir = current_dir / "autocrate"
sys.path.insert(0, str(autocrate_dir))
sys.path.insert(0, str(current_dir))

# Import and launch
from autocrate.ultra_modern_gui_threaded import main

if __name__ == "__main__":
    print("Launching AutoCrate Ultra Modern GUI (Threaded Version)...")
    print("Features:")
    print("  - Non-blocking test execution")
    print("  - Automatic progress logging to progress_log.txt")
    print("  - Responsive UI during all operations")
    print("-" * 50)
    main()