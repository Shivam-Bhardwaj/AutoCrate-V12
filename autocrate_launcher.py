#!/usr/bin/env python
"""
AutoCrate Launcher - Choose Your Interface
==========================================
Select between ultra-modern, modern, or classic interfaces
"""

import sys
import os
import customtkinter as ctk
from tkinter import PhotoImage
import json

# Configuration file for saving preferences
CONFIG_FILE = os.path.join(os.path.dirname(__file__), ".autocrate_config.json")

class InterfaceSelector:
    """Interface selection dialog"""
    
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("AutoCrate - Select Interface")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - 300
        y = (self.root.winfo_screenheight() // 2) - 200
        self.root.geometry(f"600x400+{x}+{y}")
        
        self.selected_interface = None
        self.remember_choice = ctk.BooleanVar(value=False)
        
        self.create_ui()
        
        # Check for saved preference
        self.check_saved_preference()
    
    def create_ui(self):
        """Create selection UI"""
        # Header
        header = ctk.CTkLabel(
            self.root,
            text="Choose Your AutoCrate Experience",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        header.pack(pady=30)
        
        # Options frame
        options_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        options_frame.pack(fill="both", expand=True, padx=40)
        
        # Ultra-Modern option
        ultra_frame = ctk.CTkFrame(options_frame, corner_radius=10, height=80)
        ultra_frame.pack(fill="x", pady=10)
        ultra_frame.pack_propagate(False)
        
        ultra_content = ctk.CTkFrame(ultra_frame, fg_color="transparent")
        ultra_content.pack(expand=True)
        
        ultra_title = ctk.CTkLabel(
            ultra_content,
            text="🚀 Ultra-Modern",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=("#007acc", "#00aaff")
        )
        ultra_title.pack()
        
        ultra_desc = ctk.CTkLabel(
            ultra_content,
            text="Cutting-edge design with 3D preview and animations",
            font=ctk.CTkFont(size=12),
            text_color=("#666666", "#aaaaaa")
        )
        ultra_desc.pack()
        
        ultra_btn = ctk.CTkButton(
            ultra_frame,
            text="Launch",
            width=100,
            command=lambda: self.select_interface("ultra")
        )
        ultra_btn.pack(side="right", padx=20)
        
        # Modern option
        modern_frame = ctk.CTkFrame(options_frame, corner_radius=10, height=80)
        modern_frame.pack(fill="x", pady=10)
        modern_frame.pack_propagate(False)
        
        modern_content = ctk.CTkFrame(modern_frame, fg_color="transparent")
        modern_content.pack(expand=True)
        
        modern_title = ctk.CTkLabel(
            modern_content,
            text="✨ Modern",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=("#28a745", "#34ce57")
        )
        modern_title.pack()
        
        modern_desc = ctk.CTkLabel(
            modern_content,
            text="Professional interface with enhanced usability",
            font=ctk.CTkFont(size=12),
            text_color=("#666666", "#aaaaaa")
        )
        modern_desc.pack()
        
        modern_btn = ctk.CTkButton(
            modern_frame,
            text="Launch",
            width=100,
            command=lambda: self.select_interface("modern")
        )
        modern_btn.pack(side="right", padx=20)
        
        # Classic option
        classic_frame = ctk.CTkFrame(options_frame, corner_radius=10, height=80)
        classic_frame.pack(fill="x", pady=10)
        classic_frame.pack_propagate(False)
        
        classic_content = ctk.CTkFrame(classic_frame, fg_color="transparent")
        classic_content.pack(expand=True)
        
        classic_title = ctk.CTkLabel(
            classic_content,
            text="📦 Classic",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=("#6c757d", "#8c959d")
        )
        classic_title.pack()
        
        classic_desc = ctk.CTkLabel(
            classic_content,
            text="Original AutoCrate interface",
            font=ctk.CTkFont(size=12),
            text_color=("#666666", "#aaaaaa")
        )
        classic_desc.pack()
        
        classic_btn = ctk.CTkButton(
            classic_frame,
            text="Launch",
            width=100,
            command=lambda: self.select_interface("classic")
        )
        classic_btn.pack(side="right", padx=20)
        
        # Remember choice checkbox
        remember_check = ctk.CTkCheckBox(
            self.root,
            text="Remember my choice",
            variable=self.remember_choice,
            font=ctk.CTkFont(size=12)
        )
        remember_check.pack(pady=20)
    
    def check_saved_preference(self):
        """Check for saved interface preference"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    if 'interface' in config:
                        # Auto-launch saved preference
                        self.selected_interface = config['interface']
                        self.root.after(100, self.launch_interface)
            except:
                pass
    
    def select_interface(self, interface_type):
        """Select and launch interface"""
        self.selected_interface = interface_type
        
        # Save preference if requested
        if self.remember_choice.get():
            try:
                with open(CONFIG_FILE, 'w') as f:
                    json.dump({'interface': interface_type}, f)
            except:
                pass
        
        self.launch_interface()
    
    def launch_interface(self):
        """Launch the selected interface"""
        self.root.destroy()
        
        # Launch selected interface
        if self.selected_interface == "ultra":
            from autocrate.ultra_modern_gui import main
            main()
        elif self.selected_interface == "modern":
            try:
                from autocrate.modern_gui import main
                main()
            except ImportError:
                # Fallback to ultra-modern if modern not available
                from autocrate.ultra_modern_gui import main
                main()
        else:
            # Launch classic interface
            from autocrate.nx_expressions_generator import main
            main()
    
    def run(self):
        """Run the selector"""
        self.root.mainloop()

def main():
    """Main entry point"""
    # Check for command line arguments
    if len(sys.argv) > 1:
        if "--ultra" in sys.argv:
            from autocrate.ultra_modern_gui import main
            main()
        elif "--modern" in sys.argv:
            try:
                from autocrate.modern_gui import main
                main()
            except ImportError:
                from autocrate.ultra_modern_gui import main
                main()
        elif "--classic" in sys.argv:
            from autocrate.nx_expressions_generator import main
            main()
        elif "--reset" in sys.argv:
            # Reset saved preference
            if os.path.exists(CONFIG_FILE):
                os.remove(CONFIG_FILE)
                print("Preferences reset")
            selector = InterfaceSelector()
            selector.run()
        else:
            print("Usage: autocrate_launcher.py [--ultra|--modern|--classic|--reset]")
    else:
        # Show selector
        selector = InterfaceSelector()
        selector.run()

if __name__ == "__main__":
    main()