#!/usr/bin/env python3
"""
AutoCrate Modern GUI Demonstration Script v12.1

This script demonstrates the new modern professional interface capabilities
without requiring a full application launch. Perfect for showcasing features
and testing interface components.

Features demonstrated:
- Professional engineering software color scheme
- Real-time input validation with visual feedback
- 3D crate preview (if matplotlib available)
- Tabbed workflow organization
- Modern typography and spacing
- Progress indicators and status feedback
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox

# Add autocrate to path
autocrate_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'autocrate')
if autocrate_dir not in sys.path:
    sys.path.insert(0, autocrate_dir)

try:
    from modern_gui import ModernTheme, ValidationWidget, CratePreview3D, ModernStatusBar
except ImportError as e:
    print(f"Could not import modern GUI components: {e}")
    sys.exit(1)

class ModernGUIDemo:
    """Demonstration of AutoCrate modern GUI capabilities."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AutoCrate Modern GUI - Feature Demonstration")
        self.root.geometry("1000x700")
        
        # Apply modern styling
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self._configure_styles()
        
        self._create_demo_interface()
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1000 // 2)
        y = (self.root.winfo_screenheight() // 2) - (700 // 2)
        self.root.geometry(f"1000x700+{x}+{y}")
    
    def _configure_styles(self):
        """Configure modern styles for demo."""
        self.style.configure('Demo.TFrame', background=ModernTheme.COLORS['primary_bg'])
        self.style.configure('Card.TFrame', background=ModernTheme.COLORS['accent_bg'], 
                           relief='solid', borderwidth=1)
        self.style.configure('Header.TLabel', font=ModernTheme.FONTS['heading'],
                           background=ModernTheme.COLORS['primary_bg'])
        self.style.configure('Title.TLabel', font=ModernTheme.FONTS['title'],
                           background=ModernTheme.COLORS['primary_bg'])
    
    def _create_demo_interface(self):
        """Create the demonstration interface."""
        # Main container
        main_frame = ttk.Frame(self.root, style='Demo.TFrame', padding=ModernTheme.SPACING['md'])
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(main_frame, style='Demo.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, ModernTheme.SPACING['lg']))
        
        ttk.Label(header_frame, text="AutoCrate Modern GUI Demonstration", 
                 style='Title.TLabel').pack(side=tk.LEFT)
        
        ttk.Label(header_frame, text="Professional Engineering Interface", 
                 font=ModernTheme.FONTS['small'],
                 foreground=ModernTheme.COLORS['secondary_text']).pack(side=tk.LEFT, padx=(15, 0))
        
        ttk.Separator(main_frame, orient='horizontal').pack(fill=tk.X, pady=(0, ModernTheme.SPACING['md']))
        
        # Create notebook for feature tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, ModernTheme.SPACING['md']))
        
        # Tab 1: Input Validation Demo
        self._create_validation_tab(notebook)
        
        # Tab 2: 3D Preview Demo
        self._create_preview_tab(notebook)
        
        # Tab 3: Color Scheme Demo
        self._create_theme_tab(notebook)
        
        # Status bar
        self.status_bar = ModernStatusBar(self.root)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_bar.set_status("AutoCrate Modern GUI Demo - Showcasing Professional Features", "success")
    
    def _create_validation_tab(self, notebook):
        """Create input validation demonstration tab."""
        tab_frame = ttk.Frame(notebook, style='Demo.TFrame')
        notebook.add(tab_frame, text="   Input Validation Demo   ")
        
        # Description
        desc_frame = ttk.LabelFrame(tab_frame, text="Real-Time Input Validation with Visual Feedback",
                                  padding=ModernTheme.SPACING['md'])
        desc_frame.pack(fill=tk.X, padx=ModernTheme.SPACING['md'], pady=ModernTheme.SPACING['md'])
        
        desc_text = ("The modern interface provides instant feedback on input validity. "
                    "Try entering invalid values to see the validation indicators change.")
        ttk.Label(desc_frame, text=desc_text, font=ModernTheme.FONTS['body'], wraplength=800).pack()
        
        # Demo inputs
        inputs_frame = ttk.LabelFrame(tab_frame, text="Try These Inputs", 
                                    padding=ModernTheme.SPACING['md'])
        inputs_frame.pack(fill=tk.X, padx=ModernTheme.SPACING['md'], pady=(0, ModernTheme.SPACING['md']))
        
        # Create validation widgets
        def validate_dimension(value):
            try:
                return 0 < float(value) <= 200
            except:
                return False
        
        def validate_weight(value):
            try:
                return 0 < float(value) <= 50000
            except:
                return False
        
        self.demo_length = ValidationWidget(
            inputs_frame, "Product Length:", "96.0", validate_dimension,
            "Must be between 0.1 and 200 inches", "inches"
        )
        self.demo_length.grid(row=0, column=0, sticky="ew", padx=(0, 10), pady=5)
        
        self.demo_width = ValidationWidget(
            inputs_frame, "Product Width:", "100.0", validate_dimension,
            "Must be between 0.1 and 200 inches", "inches"
        )
        self.demo_width.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        self.demo_weight = ValidationWidget(
            inputs_frame, "Product Weight:", "8000.0", validate_weight,
            "Must be between 0.1 and 50000 lbs", "lbs"
        )
        self.demo_weight.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)
        
        inputs_frame.columnconfigure(0, weight=1)
        inputs_frame.columnconfigure(1, weight=1)
        
        # Instructions
        instructions_frame = ttk.LabelFrame(tab_frame, text="Try These Examples",
                                          padding=ModernTheme.SPACING['md'])
        instructions_frame.pack(fill=tk.X, padx=ModernTheme.SPACING['md'])
        
        examples = [
            "✓ Valid inputs: 96.5, 100.25, 8000",
            "✗ Invalid inputs: -5, 500, abc, empty fields",
            "✓ Edge cases: 0.1, 199.9, 49999"
        ]
        
        for example in examples:
            ttk.Label(instructions_frame, text=example, font=ModernTheme.FONTS['small']).pack(anchor='w', pady=2)
    
    def _create_preview_tab(self, notebook):
        """Create 3D preview demonstration tab."""
        tab_frame = ttk.Frame(notebook, style='Demo.TFrame')
        notebook.add(tab_frame, text="   3D Preview Demo   ")
        
        # Description
        desc_frame = ttk.LabelFrame(tab_frame, text="Interactive 3D Crate Visualization",
                                  padding=ModernTheme.SPACING['md'])
        desc_frame.pack(fill=tk.X, padx=ModernTheme.SPACING['md'], pady=ModernTheme.SPACING['md'])
        
        try:
            import matplotlib
            desc_text = ("Real-time 3D visualization of crate designs using matplotlib. "
                        "The preview updates automatically as you change dimensions.")
        except ImportError:
            desc_text = ("3D visualization requires matplotlib. Install with 'pip install matplotlib' "
                        "for full 3D preview capabilities. A 2D fallback is provided.")
        
        ttk.Label(desc_frame, text=desc_text, font=ModernTheme.FONTS['body'], wraplength=800).pack()
        
        # Preview area
        preview_frame = ttk.LabelFrame(tab_frame, text="Crate Preview", 
                                     padding=ModernTheme.SPACING['sm'])
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=ModernTheme.SPACING['md'], 
                         pady=(0, ModernTheme.SPACING['md']))
        
        # Create 3D preview
        self.preview = CratePreview3D(preview_frame)
        
        # Controls
        controls_frame = ttk.Frame(tab_frame, style='Demo.TFrame')
        controls_frame.pack(fill=tk.X, padx=ModernTheme.SPACING['md'])
        
        ttk.Button(controls_frame, text="Update Preview", 
                  command=self._update_demo_preview).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(controls_frame, text="Random Dimensions", 
                  command=self._randomize_preview).pack(side=tk.LEFT)
    
    def _create_theme_tab(self, notebook):
        """Create color scheme demonstration tab."""
        tab_frame = ttk.Frame(notebook, style='Demo.TFrame')
        notebook.add(tab_frame, text="   Color Scheme Demo   ")
        
        # Description
        desc_frame = ttk.LabelFrame(tab_frame, text="Professional Engineering Software Color Palette",
                                  padding=ModernTheme.SPACING['md'])
        desc_frame.pack(fill=tk.X, padx=ModernTheme.SPACING['md'], pady=ModernTheme.SPACING['md'])
        
        desc_text = ("The modern interface uses a carefully selected color palette designed "
                    "for professional engineering applications with excellent readability and reduced eye strain.")
        ttk.Label(desc_frame, text=desc_text, font=ModernTheme.FONTS['body'], wraplength=800).pack()
        
        # Color swatches
        colors_frame = ttk.LabelFrame(tab_frame, text="Color Palette", 
                                    padding=ModernTheme.SPACING['md'])
        colors_frame.pack(fill=tk.BOTH, expand=True, padx=ModernTheme.SPACING['md'])
        
        # Create color swatches
        colors = [
            ("Primary Background", ModernTheme.COLORS['primary_bg']),
            ("Accent Background", ModernTheme.COLORS['accent_bg']),
            ("Primary Text", ModernTheme.COLORS['primary_text']),
            ("Accent Text", ModernTheme.COLORS['accent_text']),
            ("Success", ModernTheme.COLORS['success']),
            ("Warning", ModernTheme.COLORS['warning']),
            ("Error", ModernTheme.COLORS['error']),
            ("Info", ModernTheme.COLORS['info'])
        ]
        
        for i, (name, color) in enumerate(colors):
            row = i // 4
            col = i % 4
            
            swatch_frame = ttk.Frame(colors_frame, style='Demo.TFrame')
            swatch_frame.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
            
            # Color swatch
            swatch = tk.Frame(swatch_frame, bg=color, width=80, height=40, relief='solid', bd=1)
            swatch.pack()
            swatch.pack_propagate(False)
            
            # Label
            ttk.Label(swatch_frame, text=name, font=ModernTheme.FONTS['small']).pack(pady=(5, 0))
            ttk.Label(swatch_frame, text=color, font=('Consolas', 8),
                     foreground=ModernTheme.COLORS['secondary_text']).pack()
        
        for i in range(4):
            colors_frame.columnconfigure(i, weight=1)
        
        # Typography demo
        typo_frame = ttk.LabelFrame(tab_frame, text="Typography System",
                                  padding=ModernTheme.SPACING['md'])
        typo_frame.pack(fill=tk.X, padx=ModernTheme.SPACING['md'], pady=(0, ModernTheme.SPACING['md']))
        
        fonts = [
            ("Title Font", ModernTheme.FONTS['title'], "AutoCrate Professional"),
            ("Heading Font", ModernTheme.FONTS['heading'], "Engineering Parameters"),
            ("Body Font", ModernTheme.FONTS['body'], "Standard input field labels"),
            ("Small Font", ModernTheme.FONTS['small'], "Help text and annotations"),
            ("Monospace Font", ModernTheme.FONTS['monospace'], "Code and technical data")
        ]
        
        for name, font_spec, sample in fonts:
            font_frame = ttk.Frame(typo_frame, style='Demo.TFrame')
            font_frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(font_frame, text=f"{name}:", font=ModernTheme.FONTS['small'],
                     foreground=ModernTheme.COLORS['secondary_text']).pack(side=tk.LEFT)
            ttk.Label(font_frame, text=sample, font=font_spec).pack(side=tk.LEFT, padx=(10, 0))
    
    def _update_demo_preview(self):
        """Update the 3D preview with current demo values."""
        try:
            dimensions = {
                'width': float(self.demo_width.get() or "100"),
                'length': float(self.demo_length.get() or "96"),
                'height': 30.0  # Fixed for demo
            }
            self.preview.update_preview(dimensions)
            self.status_bar.set_status("3D preview updated successfully", "success")
        except Exception as e:
            self.status_bar.set_status(f"Preview update failed: {str(e)}", "warning")
    
    def _randomize_preview(self):
        """Randomize dimensions for demo purposes."""
        import random
        
        length = round(random.uniform(50, 150), 1)
        width = round(random.uniform(50, 150), 1)
        
        self.demo_length.set(str(length))
        self.demo_width.set(str(width))
        
        self._update_demo_preview()
        self.status_bar.set_status("Random dimensions generated", "info")
    
    def run(self):
        """Run the demonstration."""
        self.root.mainloop()

def main():
    """Main demo function."""
    print("AutoCrate Modern GUI Demonstration")
    print("==================================")
    print("Launching feature showcase...")
    
    try:
        demo = ModernGUIDemo()
        demo.run()
    except Exception as e:
        print(f"Demo failed to start: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()