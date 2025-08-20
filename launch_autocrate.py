#!/usr/bin/env python3
"""
AutoCrate Professional Launcher v12.1
Main entry point for the AutoCrate Engineering Crate Design System

This launcher provides easy access to AutoCrate with intelligent interface selection.
It automatically detects the best available interface and provides options for
both modern professional and legacy interfaces.

Usage:
    python launch_autocrate.py           # Auto-select best interface
    python launch_autocrate.py --modern  # Force modern interface
    python launch_autocrate.py --legacy  # Force legacy interface
    python launch_autocrate.py --help    # Show help information
"""

import sys
import os

# Add the autocrate module to Python path
autocrate_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'autocrate')
if autocrate_dir not in sys.path:
    sys.path.insert(0, autocrate_dir)

def main():
    """Main launcher function."""
    try:
        # Import the main application
        from autocrate_main import main as autocrate_main
        
        # Launch AutoCrate
        print("AutoCrate Professional v12.1 - Engineering Crate Design System")
        print("Initializing...")
        autocrate_main()
        
    except ImportError as e:
        print(f"Error: Could not import AutoCrate modules: {e}")
        print("Please ensure all required dependencies are installed.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: AutoCrate failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()