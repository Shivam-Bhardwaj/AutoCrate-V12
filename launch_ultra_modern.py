#!/usr/bin/env python
"""
Launch Ultra-Modern AutoCrate GUI
==================================
Entry point for the ultra-modern AutoCrate interface
"""

import sys
import os

# Add autocrate module to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    from autocrate.ultra_modern_gui import main
    main()