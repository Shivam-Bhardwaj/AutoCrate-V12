#!/usr/bin/env python3
"""
AutoCrate Main Launcher
Launches the AutoCrate application with proper path setup.
"""

import sys
import os

# Add the autocrate directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
autocrate_dir = os.path.join(current_dir, 'autocrate')
if autocrate_dir not in sys.path:
    sys.path.insert(0, autocrate_dir)

# Now we can import and run
if __name__ == "__main__":
    from nx_expressions_generator import CrateApp
    import tkinter as tk
    
    root = tk.Tk()
    app = CrateApp(root)
    root.mainloop()