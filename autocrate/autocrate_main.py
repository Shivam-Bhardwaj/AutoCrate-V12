"""
AutoCrate Main Application Entry Point v12.1
Professional Engineering Crate Design System

This module provides the main entry point for AutoCrate with options for both
the modern professional GUI and legacy interface. Users can select their
preferred interface while maintaining full compatibility with all features.

Usage:
    python autocrate_main.py           # Launch with GUI selection dialog
    python autocrate_main.py --modern  # Launch modern GUI directly
    python autocrate_main.py --legacy  # Launch legacy GUI directly
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox
import argparse
from typing import Optional

# Setup import paths
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import required modules
try:
    from nx_expressions_generator import CrateApp as LegacyCrateApp
    from modern_gui import create_modern_autocrate_app, ModernTheme
except ImportError as e:
    print(f"Error importing required modules: {e}")
    sys.exit(1)

class GUISelectionDialog:
    """Dialog for selecting between modern and legacy GUI interfaces."""
    
    def __init__(self):
        self.selection = None
        self.remember_choice = False
        
        # Create dialog window
        self.root = tk.Tk()
        self.root.title("AutoCrate - Select Interface")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # Center the window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.root.winfo_screenheight() // 2) - (400 // 2)
        self.root.geometry(f"500x400+{x}+{y}")
        
        self._create_dialog()
    
    def _create_dialog(self):
        """Create the GUI selection dialog."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = ttk.Label(header_frame, text="AutoCrate Professional v12.1",
                               font=('Segoe UI', 16, 'bold'))
        title_label.pack()
        
        subtitle_label = ttk.Label(header_frame, text="Engineering Crate Design System",
                                 font=('Segoe UI', 12))
        subtitle_label.pack(pady=(5, 0))
        
        ttk.Separator(main_frame, orient='horizontal').pack(fill=tk.X, pady=(0, 20))
        
        # Interface selection
        selection_label = ttk.Label(main_frame, text="Choose your preferred interface:",
                                  font=('Segoe UI', 12, 'bold'))
        selection_label.pack(pady=(0, 15))
        
        # Modern GUI option
        modern_frame = ttk.LabelFrame(main_frame, text="Modern Professional Interface (Recommended)",
                                    padding=15)
        modern_frame.pack(fill=tk.X, pady=(0, 10))
        
        modern_features = [
            "✓ Professional engineering software appearance",
            "✓ Tabbed workflow organization", 
            "✓ Real-time input validation and feedback",
            "✓ 3D crate preview visualization",
            "✓ Enhanced progress indicators",
            "✓ Modern color scheme and typography"
        ]
        
        for feature in modern_features:
            ttk.Label(modern_frame, text=feature, font=('Segoe UI', 9)).pack(anchor='w', pady=1)
        
        modern_btn = ttk.Button(modern_frame, text="Launch Modern Interface",
                              command=lambda: self._select_interface('modern'))
        modern_btn.pack(pady=(10, 0))
        
        # Legacy GUI option
        legacy_frame = ttk.LabelFrame(main_frame, text="Legacy Interface",
                                    padding=15)
        legacy_frame.pack(fill=tk.X, pady=(0, 15))
        
        legacy_desc = ttk.Label(legacy_frame, 
                              text="Original AutoCrate interface. Provides all core functionality\\nwith the familiar traditional layout.",
                              font=('Segoe UI', 9))
        legacy_desc.pack(anchor='w', pady=(0, 10))
        
        legacy_btn = ttk.Button(legacy_frame, text="Launch Legacy Interface",
                              command=lambda: self._select_interface('legacy'))
        legacy_btn.pack()
        
        # Options
        options_frame = ttk.Frame(main_frame)
        options_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.remember_var = tk.BooleanVar()
        remember_check = ttk.Checkbutton(options_frame, 
                                       text="Remember my choice (can be changed in settings)",
                                       variable=self.remember_var)
        remember_check.pack(side=tk.LEFT)
        
        # Info note
        info_label = ttk.Label(main_frame,
                             text="Both interfaces provide identical functionality and NX expression output.\\nChoose based on your preference for appearance and workflow.",
                             font=('Segoe UI', 8),
                             foreground='#666666')
        info_label.pack(pady=(15, 0))
    
    def _select_interface(self, interface_type: str):
        """Handle interface selection."""
        self.selection = interface_type
        self.remember_choice = self.remember_var.get()
        
        # Save preference if requested
        if self.remember_choice:
            self._save_preference(interface_type)
        
        self.root.quit()
        self.root.destroy()
    
    def _save_preference(self, interface_type: str):
        """Save the user's interface preference."""
        try:
            import json
            config_file = os.path.join(current_dir, 'autocrate_config.json')
            
            config = {}
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
            
            config['preferred_interface'] = interface_type
            
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
                
        except Exception as e:
            print(f"Could not save preference: {e}")
    
    def run(self) -> Optional[str]:
        """Run the selection dialog and return the choice."""
        self.root.mainloop()
        return self.selection

def load_saved_preference() -> Optional[str]:
    """Load the user's saved interface preference."""
    try:
        import json
        config_file = os.path.join(current_dir, 'autocrate_config.json')
        
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
                return config.get('preferred_interface')
    except:
        pass
    
    return None

def launch_modern_gui():
    """Launch the modern AutoCrate GUI."""
    try:
        root = tk.Tk()
        app = create_modern_autocrate_app(root, LegacyCrateApp)
        
        # Handle window closing
        def on_closing():
            if messagebox.askokcancel("Quit", "Do you want to quit AutoCrate?"):
                root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to launch modern GUI: {str(e)}")
        print(f"Modern GUI launch error: {e}")
        print("Traceback:", exc_info=True)

def launch_legacy_gui():
    """Launch the legacy AutoCrate GUI."""
    try:
        root = tk.Tk()
        app = LegacyCrateApp(root)
        
        # Handle window closing
        def on_closing():
            if messagebox.askokcancel("Quit", "Do you want to quit AutoCrate?"):
                root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to launch legacy GUI: {str(e)}")
        print(f"Legacy GUI launch error: {e}")
        print("Traceback:", exc_info=True)

def main():
    """Main application entry point."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='AutoCrate Professional Engineering Crate Design System')
    parser.add_argument('--modern', action='store_true', help='Launch modern GUI directly')
    parser.add_argument('--legacy', action='store_true', help='Launch legacy GUI directly')
    parser.add_argument('--reset-preference', action='store_true', help='Reset saved interface preference')
    
    args = parser.parse_args()
    
    # Reset preference if requested
    if args.reset_preference:
        try:
            config_file = os.path.join(current_dir, 'autocrate_config.json')
            if os.path.exists(config_file):
                import json
                with open(config_file, 'r') as f:
                    config = json.load(f)
                config.pop('preferred_interface', None)
                with open(config_file, 'w') as f:
                    json.dump(config, f, indent=2)
                print("Interface preference reset.")
            else:
                print("No saved preference found.")
        except Exception as e:
            print(f"Error resetting preference: {e}")
        return
    
    # Determine which interface to launch
    interface_choice = None
    
    if args.modern:
        interface_choice = 'modern'
    elif args.legacy:
        interface_choice = 'legacy'
    else:
        # Check for saved preference
        saved_preference = load_saved_preference()
        if saved_preference:
            interface_choice = saved_preference
        else:
            # Show selection dialog
            dialog = GUISelectionDialog()
            interface_choice = dialog.run()
    
    # Launch selected interface
    if interface_choice == 'modern':
        print("Launching AutoCrate with Modern Professional Interface...")
        launch_modern_gui()
    elif interface_choice == 'legacy':
        print("Launching AutoCrate with Legacy Interface...")
        launch_legacy_gui()
    else:
        print("No interface selected. Exiting.")
        sys.exit(0)

if __name__ == "__main__":
    main()