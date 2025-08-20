"""
AutoCrate Modern GUI Module v1.0
Professional engineering software interface with enhanced user experience.

This module provides a modernized tkinter-based GUI that maintains full compatibility
with existing AutoCrate functionality while providing:
- Professional engineering software appearance
- Tabbed workflow organization
- Real-time input validation
- Enhanced visual feedback
- 3D crate preview capabilities
- Smart defaults and templates

All calculations and core functionality remain unchanged.
"""

import datetime
import math
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, font
import traceback
import sys
import threading
from typing import Dict, Any, Optional, Callable
import json

# Try to import optional 3D visualization
try:
    import matplotlib
    matplotlib.use('TkAgg')
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    from mpl_toolkits.mplot3d import Axes3D
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

class ModernTheme:
    """Professional engineering software color scheme and styling."""
    
    # Color Palette - Professional Engineering Software
    COLORS = {
        'primary_bg': '#f8f9fa',           # Light gray background
        'secondary_bg': '#e9ecef',         # Slightly darker gray
        'accent_bg': '#ffffff',            # Pure white for input areas
        'dark_bg': '#343a40',              # Dark gray for headers
        'primary_text': '#212529',         # Dark text
        'secondary_text': '#6c757d',       # Medium gray text
        'accent_text': '#0056b3',          # Professional blue
        'success': '#28a745',              # Green for success states
        'warning': '#ffc107',              # Amber for warnings
        'error': '#dc3545',                # Red for errors
        'info': '#17a2b8',                 # Cyan for information
        'border': '#dee2e6',               # Light border color
        'hover': '#e3f2fd',                # Light blue hover
        'selected': '#bbdefb'              # Darker blue selected
    }
    
    # Typography
    FONTS = {
        'title': ('Segoe UI', 16, 'bold'),
        'heading': ('Segoe UI', 12, 'bold'),
        'body': ('Segoe UI', 10),
        'small': ('Segoe UI', 9),
        'monospace': ('Consolas', 10),
        'input': ('Segoe UI', 10)
    }
    
    # Spacing and sizing
    SPACING = {
        'xs': 4,
        'sm': 8,
        'md': 12,
        'lg': 16,
        'xl': 24,
        'xxl': 32
    }

class ValidationWidget:
    """Enhanced input widget with real-time validation and visual feedback."""
    
    def __init__(self, parent, label_text: str, default_value: str = "", 
                 validation_func: Optional[Callable] = None, 
                 help_text: str = "", unit: str = ""):
        self.parent = parent
        self.validation_func = validation_func
        self.is_valid = True
        
        # Create container frame
        self.frame = ttk.Frame(parent)
        
        # Label
        self.label = ttk.Label(self.frame, text=label_text, font=ModernTheme.FONTS['body'])
        self.label.grid(row=0, column=0, sticky="w", pady=(0, 2))
        
        # Input frame for entry and validation indicator
        input_frame = ttk.Frame(self.frame)
        input_frame.grid(row=1, column=0, sticky="ew", pady=(0, 2))
        
        # Entry widget
        self.entry = ttk.Entry(input_frame, font=ModernTheme.FONTS['input'], width=20)
        self.entry.grid(row=0, column=0, sticky="ew")
        self.entry.insert(0, default_value)
        
        # Unit label
        if unit:
            unit_label = ttk.Label(input_frame, text=unit, font=ModernTheme.FONTS['small'],
                                 foreground=ModernTheme.COLORS['secondary_text'])
            unit_label.grid(row=0, column=1, padx=(4, 0))
        
        # Validation indicator
        self.indicator = ttk.Label(input_frame, text="✓", foreground=ModernTheme.COLORS['success'],
                                 font=('Segoe UI', 12, 'bold'))
        self.indicator.grid(row=0, column=2, padx=(4, 0))
        
        # Help text
        if help_text:
            help_label = ttk.Label(self.frame, text=help_text, font=ModernTheme.FONTS['small'],
                                 foreground=ModernTheme.COLORS['secondary_text'])
            help_label.grid(row=2, column=0, sticky="w")
        
        # Configure grid weights
        input_frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)
        
        # Bind validation
        self.entry.bind('<KeyRelease>', self._validate)
        self.entry.bind('<FocusOut>', self._validate)
        
        # Initial validation
        self._validate()
    
    def _validate(self, event=None):
        """Perform validation and update visual indicators."""
        value = self.entry.get().strip()
        
        if self.validation_func:
            try:
                self.is_valid = self.validation_func(value)
            except:
                self.is_valid = False
        else:
            self.is_valid = bool(value)  # Non-empty by default
        
        # Update indicator
        if self.is_valid:
            self.indicator.config(text="✓", foreground=ModernTheme.COLORS['success'])
            self.entry.config(style='TEntry')
        else:
            self.indicator.config(text="⚠", foreground=ModernTheme.COLORS['error'])
            # Could apply error styling here if needed
    
    def get(self) -> str:
        """Get the current value."""
        return self.entry.get().strip()
    
    def set(self, value: str):
        """Set the value."""
        self.entry.delete(0, tk.END)
        self.entry.insert(0, value)
        self._validate()
    
    def grid(self, **kwargs):
        """Grid the widget."""
        self.frame.grid(**kwargs)

class CratePreview3D:
    """3D visualization of the crate design using matplotlib."""
    
    def __init__(self, parent):
        self.parent = parent
        self.fig = None
        self.canvas = None
        
        if MATPLOTLIB_AVAILABLE:
            self._setup_3d_view()
        else:
            # Fallback to 2D schematic if matplotlib not available
            self._setup_2d_fallback()
    
    def _setup_3d_view(self):
        """Set up 3D matplotlib visualization."""
        self.fig = Figure(figsize=(8, 6), dpi=100, facecolor=ModernTheme.COLORS['accent_bg'])
        self.ax = self.fig.add_subplot(111, projection='3d')
        
        self.canvas = FigureCanvasTkAgg(self.fig, self.parent)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initial empty plot
        self.ax.set_xlabel('Width (X)', fontsize=10)
        self.ax.set_ylabel('Length (Y)', fontsize=10)
        self.ax.set_zlabel('Height (Z)', fontsize=10)
        self.ax.set_title('Crate Design Preview', fontsize=12, fontweight='bold')
        
        # Set clean styling
        self.ax.grid(True, alpha=0.3)
        self.fig.tight_layout()
    
    def _setup_2d_fallback(self):
        """Setup 2D fallback visualization."""
        fallback_frame = ttk.Frame(self.parent)
        fallback_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(fallback_frame, text="3D Preview", 
                 font=ModernTheme.FONTS['heading']).pack(pady=10)
        ttk.Label(fallback_frame, text="Install matplotlib for 3D visualization",
                 font=ModernTheme.FONTS['small'],
                 foreground=ModernTheme.COLORS['secondary_text']).pack()
        
        # Simple 2D schematic placeholder
        canvas = tk.Canvas(fallback_frame, bg=ModernTheme.COLORS['accent_bg'], 
                          height=300, relief='sunken', bd=1)
        canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Draw simple crate outline
        canvas.create_rectangle(50, 50, 350, 250, outline=ModernTheme.COLORS['primary_text'], width=2)
        canvas.create_text(200, 150, text="Crate Preview\n(2D Schematic)", 
                          font=ModernTheme.FONTS['body'], fill=ModernTheme.COLORS['secondary_text'])
    
    def update_preview(self, dimensions: Dict[str, float]):
        """Update the 3D preview with new dimensions."""
        if not MATPLOTLIB_AVAILABLE or not self.fig:
            return
            
        # Clear previous plot
        self.ax.clear()
        
        # Extract dimensions
        width = dimensions.get('width', 100)
        length = dimensions.get('length', 96) 
        height = dimensions.get('height', 30)
        
        # Create wireframe crate
        self._draw_crate_wireframe(width, length, height)
        
        # Update labels and limits
        self.ax.set_xlabel('Width (X)', fontsize=10)
        self.ax.set_ylabel('Length (Y)', fontsize=10) 
        self.ax.set_zlabel('Height (Z)', fontsize=10)
        self.ax.set_title(f'Crate: {width:.1f}" × {length:.1f}" × {height:.1f}"', 
                         fontsize=12, fontweight='bold')
        
        # Set equal aspect ratio and reasonable limits
        max_dim = max(width, length, height)
        margin = max_dim * 0.1
        self.ax.set_xlim(-margin, width + margin)
        self.ax.set_ylim(-margin, length + margin)
        self.ax.set_zlim(-margin, height + margin)
        
        self.ax.grid(True, alpha=0.3)
        self.fig.tight_layout()
        self.canvas.draw()
    
    def _draw_crate_wireframe(self, width, length, height):
        """Draw a wireframe representation of the crate."""
        # Bottom face
        x_bottom = [0, width, width, 0, 0]
        y_bottom = [0, 0, length, length, 0]
        z_bottom = [0, 0, 0, 0, 0]
        self.ax.plot(x_bottom, y_bottom, z_bottom, 'b-', linewidth=2)
        
        # Top face
        x_top = [0, width, width, 0, 0]
        y_top = [0, 0, length, length, 0]
        z_top = [height, height, height, height, height]
        self.ax.plot(x_top, y_top, z_top, 'b-', linewidth=2)
        
        # Vertical edges
        for x, y in [(0, 0), (width, 0), (width, length), (0, length)]:
            self.ax.plot([x, x], [y, y], [0, height], 'b-', linewidth=2)
        
        # Add some internal structure hints
        # Skids
        skid_z = 3.5  # Typical skid height
        self.ax.plot([0, width], [length/4, length/4], [skid_z, skid_z], 'r-', linewidth=1, alpha=0.7)
        self.ax.plot([0, width], [3*length/4, 3*length/4], [skid_z, skid_z], 'r-', linewidth=1, alpha=0.7)

class ModernStatusBar:
    """Professional status bar with progress indicators and icons."""
    
    def __init__(self, parent):
        self.parent = parent
        
        # Main status frame
        self.frame = ttk.Frame(parent, relief='sunken', borderwidth=1)
        
        # Status text
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(self.frame, textvariable=self.status_var,
                                    font=ModernTheme.FONTS['small'])
        self.status_label.pack(side=tk.LEFT, padx=ModernTheme.SPACING['sm'])
        
        # Progress bar (initially hidden)
        self.progress = ttk.Progressbar(self.frame, mode='indeterminate', length=200)
        
        # Status icon
        self.icon_label = ttk.Label(self.frame, text="●", 
                                   foreground=ModernTheme.COLORS['success'])
        self.icon_label.pack(side=tk.RIGHT, padx=ModernTheme.SPACING['sm'])
    
    def set_status(self, message: str, status_type: str = "info"):
        """Set status message with optional type indicator."""
        self.status_var.set(message)
        
        # Update icon color based on status type
        color_map = {
            'info': ModernTheme.COLORS['info'],
            'success': ModernTheme.COLORS['success'],
            'warning': ModernTheme.COLORS['warning'],
            'error': ModernTheme.COLORS['error']
        }
        self.icon_label.config(foreground=color_map.get(status_type, ModernTheme.COLORS['info']))
    
    def show_progress(self, show: bool = True):
        """Show or hide progress indicator."""
        if show:
            self.progress.pack(side=tk.RIGHT, padx=ModernTheme.SPACING['sm'])
            self.progress.start(10)
        else:
            self.progress.stop()
            self.progress.pack_forget()
    
    def pack(self, **kwargs):
        """Pack the status bar."""
        self.frame.pack(**kwargs)

class ModernCrateApp:
    """
    Modern, professional AutoCrate GUI with enhanced user experience.
    
    This class provides a complete modernization of the AutoCrate interface while
    maintaining 100% compatibility with existing calculation modules and functionality.
    """
    
    def __init__(self, master, legacy_app_class):
        self.master = master
        self.legacy_app_class = legacy_app_class
        self.legacy_app = None
        
        # Initialize the GUI
        self._setup_window()
        self._configure_style()
        self._create_interface()
        
        # Create legacy app instance for calculations (hidden)
        self._initialize_legacy_backend()
    
    def _setup_window(self):
        """Configure main window properties."""
        self.master.title("AutoCrate Professional v12.1 - Engineering Crate Design System")
        self.master.geometry("1200x800")
        self.master.minsize(1000, 700)
        
        # Configure window icon if available
        try:
            # Could set window icon here if we had one
            pass
        except:
            pass
        
        # Center window on screen
        self.master.update_idletasks()
        x = (self.master.winfo_screenwidth() // 2) - (1200 // 2)
        y = (self.master.winfo_screenheight() // 2) - (800 // 2)
        self.master.geometry(f"1200x800+{x}+{y}")
    
    def _configure_style(self):
        """Configure modern ttk styling."""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure modern styles
        self.style.configure('Modern.TFrame', background=ModernTheme.COLORS['primary_bg'])
        self.style.configure('Card.TFrame', background=ModernTheme.COLORS['accent_bg'], 
                           relief='solid', borderwidth=1)
        self.style.configure('Header.TLabel', font=ModernTheme.FONTS['heading'],
                           background=ModernTheme.COLORS['primary_bg'])
        self.style.configure('Title.TLabel', font=ModernTheme.FONTS['title'],
                           background=ModernTheme.COLORS['primary_bg'])
        
        # Notebook (tab) styling
        self.style.configure('Modern.TNotebook.Tab', padding=[20, 8])
        self.style.map('Modern.TNotebook.Tab',
                      background=[('selected', ModernTheme.COLORS['accent_bg']),
                                ('active', ModernTheme.COLORS['hover'])])
    
    def _create_interface(self):
        """Create the main interface layout."""
        # Main container
        self.main_frame = ttk.Frame(self.master, style='Modern.TFrame', padding=ModernTheme.SPACING['md'])
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        self._create_header()
        
        # Main content area with tabs
        self._create_tabbed_interface()
        
        # Status bar
        self.status_bar = ModernStatusBar(self.master)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_bar.set_status("AutoCrate Professional Ready - Advanced Engineering Crate Design", "success")
    
    def _create_header(self):
        """Create professional header section."""
        header_frame = ttk.Frame(self.main_frame, style='Modern.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, ModernTheme.SPACING['lg']))
        
        # Title section
        title_frame = ttk.Frame(header_frame, style='Modern.TFrame')
        title_frame.pack(fill=tk.X)
        
        ttk.Label(title_frame, text="AutoCrate Professional", 
                 style='Title.TLabel').pack(side=tk.LEFT)
        
        ttk.Label(title_frame, text="v12.1 Engineering Edition", 
                 font=ModernTheme.FONTS['small'],
                 foreground=ModernTheme.COLORS['secondary_text']).pack(side=tk.LEFT, padx=(10, 0))
        
        # Compliance badges
        compliance_frame = ttk.Frame(title_frame, style='Modern.TFrame')
        compliance_frame.pack(side=tk.RIGHT)
        
        badges = ["ASTM D6179", "ASTM D6251", "ASTM D6256", "Professional"]
        for i, badge in enumerate(badges):
            badge_label = ttk.Label(compliance_frame, text=badge, 
                                  font=ModernTheme.FONTS['small'],
                                  foreground=ModernTheme.COLORS['accent_text'])
            badge_label.pack(side=tk.LEFT, padx=(10 if i > 0 else 0, 0))
        
        # Separator
        ttk.Separator(header_frame, orient='horizontal').pack(fill=tk.X, pady=(ModernTheme.SPACING['sm'], 0))
    
    def _create_tabbed_interface(self):
        """Create the main tabbed interface."""
        # Create notebook widget
        self.notebook = ttk.Notebook(self.main_frame, style='Modern.TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Design Parameters
        self.design_tab = ttk.Frame(self.notebook, style='Modern.TFrame')
        self.notebook.add(self.design_tab, text="   Design Parameters   ")
        self._create_design_tab()
        
        # Tab 2: 3D Preview
        self.preview_tab = ttk.Frame(self.notebook, style='Modern.TFrame')
        self.notebook.add(self.preview_tab, text="   3D Preview   ")
        self._create_preview_tab()
        
        # Tab 3: Advanced Options
        self.advanced_tab = ttk.Frame(self.notebook, style='Modern.TFrame')
        self.notebook.add(self.advanced_tab, text="   Advanced Options   ")
        self._create_advanced_tab()
        
        # Tab 4: Results & Output
        self.results_tab = ttk.Frame(self.notebook, style='Modern.TFrame')
        self.notebook.add(self.results_tab, text="   Results & Output   ")
        self._create_results_tab()
        
        # Bind tab change event for 3D updates
        self.notebook.bind('<<NotebookTabChanged>>', self._on_tab_changed)
    
    def _create_design_tab(self):
        """Create the main design parameters tab."""
        # Create scrollable frame
        canvas = tk.Canvas(self.design_tab, bg=ModernTheme.COLORS['primary_bg'])
        scrollbar = ttk.Scrollbar(self.design_tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Modern.TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Layout
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Left column - Input parameters
        left_frame = ttk.Frame(scrollable_frame, style='Modern.TFrame')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, ModernTheme.SPACING['md']))
        
        # Product Dimensions Card
        self._create_product_dimensions_card(left_frame)
        
        # Engineering Parameters Card  
        self._create_engineering_parameters_card(left_frame)
        
        # Material Specifications Card
        self._create_material_specifications_card(left_frame)
        
        # Right column - Quick Preview and Actions
        right_frame = ttk.Frame(scrollable_frame, style='Modern.TFrame')
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(ModernTheme.SPACING['md'], 0))
        
        self._create_quick_preview_card(right_frame)
        self._create_action_card(right_frame)
    
    def _create_product_dimensions_card(self, parent):
        """Create product dimensions input card."""
        card = ttk.LabelFrame(parent, text="Product Dimensions", padding=ModernTheme.SPACING['md'])
        card.pack(fill=tk.X, pady=(0, ModernTheme.SPACING['md']))
        
        # Validation functions
        def validate_dimension(value):
            try:
                return 0 < float(value) <= 200  # Reasonable limits
            except:
                return False
        
        def validate_weight(value):
            try:
                return 0 < float(value) <= 50000  # Up to 50k lbs
            except:
                return False
        
        # Input widgets with validation
        self.length_widget = ValidationWidget(
            card, "Length:", "96.0", validate_dimension, 
            "Along Y-axis (crate length)", "inches"
        )
        self.length_widget.grid(row=0, column=0, sticky="ew", pady=ModernTheme.SPACING['xs'])
        
        self.width_widget = ValidationWidget(
            card, "Width:", "100.0", validate_dimension,
            "Along X-axis (crate width)", "inches"
        )
        self.width_widget.grid(row=1, column=0, sticky="ew", pady=ModernTheme.SPACING['xs'])
        
        self.height_widget = ValidationWidget(
            card, "Height:", "30.0", validate_dimension,
            "Along Z-axis (vertical)", "inches"
        )
        self.height_widget.grid(row=2, column=0, sticky="ew", pady=ModernTheme.SPACING['xs'])
        
        self.weight_widget = ValidationWidget(
            card, "Weight:", "8000.0", validate_weight,
            "Total product weight", "lbs"
        )
        self.weight_widget.grid(row=3, column=0, sticky="ew", pady=ModernTheme.SPACING['xs'])
        
        card.columnconfigure(0, weight=1)
        
        # Bind change events for real-time preview updates
        for widget in [self.length_widget, self.width_widget, self.height_widget, self.weight_widget]:
            widget.entry.bind('<KeyRelease>', self._on_dimension_change)
    
    def _create_engineering_parameters_card(self, parent):
        """Create engineering parameters input card."""
        card = ttk.LabelFrame(parent, text="Engineering Parameters", padding=ModernTheme.SPACING['md'])
        card.pack(fill=tk.X, pady=(0, ModernTheme.SPACING['md']))
        
        def validate_clearance(value):
            try:
                return 0 <= float(value) <= 10  # Reasonable clearance limits
            except:
                return False
        
        self.side_clearance_widget = ValidationWidget(
            card, "Side Clearance:", "2.0", validate_clearance,
            "Clearance on each side of product", "inches"
        )
        self.side_clearance_widget.grid(row=0, column=0, sticky="ew", pady=ModernTheme.SPACING['xs'])
        
        self.top_clearance_widget = ValidationWidget(
            card, "Top Clearance:", "2.0", validate_clearance,
            "Clearance above product", "inches"
        )
        self.top_clearance_widget.grid(row=1, column=0, sticky="ew", pady=ModernTheme.SPACING['xs'])
        
        self.ground_clearance_widget = ValidationWidget(
            card, "Ground Clearance:", "1.0", validate_clearance,
            "For forklift access", "inches"
        )
        self.ground_clearance_widget.grid(row=2, column=0, sticky="ew", pady=ModernTheme.SPACING['xs'])
        
        # Advanced options
        ttk.Separator(card, orient='horizontal').grid(row=3, column=0, sticky="ew", 
                                                     pady=ModernTheme.SPACING['sm'])
        
        self.allow_3x4_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(card, text="Allow 3x4 skids for lighter loads",
                       variable=self.allow_3x4_var).grid(row=4, column=0, sticky="w", 
                                                        pady=ModernTheme.SPACING['xs'])
        
        card.columnconfigure(0, weight=1)
    
    def _create_material_specifications_card(self, parent):
        """Create material specifications display card."""
        card = ttk.LabelFrame(parent, text="Material Specifications (ASTM Compliant)", 
                            padding=ModernTheme.SPACING['md'])
        card.pack(fill=tk.X, pady=(0, ModernTheme.SPACING['md']))
        
        # Professional material display
        materials = [
            ("Panel Material:", "1/4 inch (0.25\") Plywood", "ASTM D6007 compliant"),
            ("Cleat Material:", "1x4 inch Lumber (0.75\" × 3.5\" actual)", "SPF Grade 2 or better"),
            ("Fasteners:", "Structural screws and bolts", "Per ASTM specifications"),
            ("Finish:", "Weather-resistant treatment", "Industrial grade protection")
        ]
        
        for i, (label, spec, note) in enumerate(materials):
            row_frame = ttk.Frame(card, style='Modern.TFrame')
            row_frame.grid(row=i, column=0, sticky="ew", pady=ModernTheme.SPACING['xs'])
            
            ttk.Label(row_frame, text=label, font=ModernTheme.FONTS['body']).pack(side=tk.LEFT)
            ttk.Label(row_frame, text=spec, font=(ModernTheme.FONTS['body'][0], ModernTheme.FONTS['body'][1], 'bold'),
                     foreground=ModernTheme.COLORS['accent_text']).pack(side=tk.LEFT, padx=(10, 0))
            ttk.Label(row_frame, text=f"({note})", font=ModernTheme.FONTS['small'],
                     foreground=ModernTheme.COLORS['secondary_text']).pack(side=tk.LEFT, padx=(5, 0))
        
        card.columnconfigure(0, weight=1)
    
    def _create_quick_preview_card(self, parent):
        """Create quick preview card in right column."""
        card = ttk.LabelFrame(parent, text="Quick Preview", padding=ModernTheme.SPACING['md'])
        card.pack(fill=tk.X, pady=(0, ModernTheme.SPACING['md']))
        
        # Dimensions display
        self.preview_dimensions = ttk.Label(card, text="Crate: 100.0\" × 96.0\" × 32.0\"",
                                          font=ModernTheme.FONTS['heading'])
        self.preview_dimensions.pack(pady=ModernTheme.SPACING['xs'])
        
        # Quick stats
        stats_frame = ttk.Frame(card, style='Modern.TFrame')
        stats_frame.pack(fill=tk.X, pady=ModernTheme.SPACING['sm'])
        
        self.volume_label = ttk.Label(stats_frame, text="Volume: 188.1 ft³", font=ModernTheme.FONTS['small'])
        self.volume_label.pack()
        
        self.weight_ratio_label = ttk.Label(stats_frame, text="Weight ratio: 1.7 lbs/ft³", font=ModernTheme.FONTS['small'])
        self.weight_ratio_label.pack()
        
        # Update preview
        self._update_quick_preview()
    
    def _create_action_card(self, parent):
        """Create action buttons card."""
        card = ttk.LabelFrame(parent, text="Actions", padding=ModernTheme.SPACING['md'])
        card.pack(fill=tk.X, pady=(0, ModernTheme.SPACING['md']))
        
        # Primary action button
        self.generate_btn = ttk.Button(card, text="Generate NX Expressions",
                                     command=self._generate_expressions)
        self.generate_btn.pack(fill=tk.X, pady=ModernTheme.SPACING['xs'])
        
        # Secondary actions
        self.test_btn = ttk.Button(card, text="Run Test Suite", 
                                 command=self._run_test_suite)
        self.test_btn.pack(fill=tk.X, pady=ModernTheme.SPACING['xs'])
        
        self.preview_btn = ttk.Button(card, text="Update 3D Preview",
                                    command=self._update_3d_preview)
        self.preview_btn.pack(fill=tk.X, pady=ModernTheme.SPACING['xs'])
    
    def _create_preview_tab(self):
        """Create 3D preview tab."""
        # Header
        header_frame = ttk.Frame(self.preview_tab, style='Modern.TFrame')
        header_frame.pack(fill=tk.X, padx=ModernTheme.SPACING['md'], pady=ModernTheme.SPACING['md'])
        
        ttk.Label(header_frame, text="3D Crate Preview", style='Header.TLabel').pack(side=tk.LEFT)
        
        ttk.Button(header_frame, text="Refresh Preview", 
                  command=self._update_3d_preview).pack(side=tk.RIGHT)
        
        # 3D Preview
        preview_frame = ttk.Frame(self.preview_tab, style='Card.TFrame')
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=ModernTheme.SPACING['md'], 
                          pady=(0, ModernTheme.SPACING['md']))
        
        self.crate_preview = CratePreview3D(preview_frame)
    
    def _create_advanced_tab(self):
        """Create advanced options tab."""
        # Floorboard configuration
        floorboard_frame = ttk.LabelFrame(self.advanced_tab, text="Floorboard Configuration",
                                        padding=ModernTheme.SPACING['md'])
        floorboard_frame.pack(fill=tk.X, padx=ModernTheme.SPACING['md'], 
                            pady=ModernTheme.SPACING['md'])
        
        def validate_thickness(value):
            try:
                return 0.5 <= float(value) <= 3.0
            except:
                return False
        
        self.floorboard_thickness_widget = ValidationWidget(
            floorboard_frame, "Floorboard Thickness:", "1.5", validate_thickness,
            "2x lumber actual thickness", "inches"
        )
        self.floorboard_thickness_widget.grid(row=0, column=0, sticky="ew", pady=ModernTheme.SPACING['xs'])
        
        # Lumber selection
        lumber_frame = ttk.LabelFrame(floorboard_frame, text="Available Lumber Sizes")
        lumber_frame.grid(row=1, column=0, sticky="ew", pady=ModernTheme.SPACING['md'])
        
        self.lumber_vars = {}
        lumber_sizes = [("2x6 (5.5\")", 5.5), ("2x8 (7.25\")", 7.25), 
                       ("2x10 (9.25\")", 9.25), ("2x12 (11.25\")", 11.25)]
        
        for i, (name, width) in enumerate(lumber_sizes):
            var = tk.BooleanVar(value=True)
            self.lumber_vars[width] = var
            ttk.Checkbutton(lumber_frame, text=name, variable=var).grid(row=i//2, column=i%2, 
                                                                       sticky="w", padx=ModernTheme.SPACING['sm'])
        
        floorboard_frame.columnconfigure(0, weight=1)
        lumber_frame.columnconfigure(0, weight=1)
        lumber_frame.columnconfigure(1, weight=1)
    
    def _create_results_tab(self):
        """Create results and output tab."""
        # Results display
        results_frame = ttk.LabelFrame(self.results_tab, text="Generation Results",
                                     padding=ModernTheme.SPACING['md'])
        results_frame.pack(fill=tk.BOTH, expand=True, padx=ModernTheme.SPACING['md'],
                         pady=ModernTheme.SPACING['md'])
        
        # Console output
        self.results_text = tk.Text(results_frame, height=20, width=80, wrap=tk.WORD,
                                   font=ModernTheme.FONTS['monospace'],
                                   bg=ModernTheme.COLORS['accent_bg'])
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        results_scrollbar = ttk.Scrollbar(results_frame, orient="vertical", 
                                        command=self.results_text.yview)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_text.configure(yscrollcommand=results_scrollbar.set)
        
        # Initial message
        self.results_text.insert(tk.END, "AutoCrate Professional v12.1 - Ready\\n")
        self.results_text.insert(tk.END, "Advanced Engineering Crate Design System\\n")
        self.results_text.insert(tk.END, "ASTM D6179/D6251/D6256 Compliant\\n\\n")
        self.results_text.insert(tk.END, "Enter product specifications and click 'Generate NX Expressions' to begin.\\n")
    
    def _initialize_legacy_backend(self):
        """Initialize the legacy calculation backend."""
        # Create a hidden tkinter window for the legacy app
        self.legacy_window = tk.Toplevel(self.master)
        self.legacy_window.withdraw()  # Hide it
        
        # Initialize legacy app
        try:
            self.legacy_app = self.legacy_app_class(self.legacy_window)
        except Exception as e:
            self.status_bar.set_status(f"Backend initialization error: {str(e)}", "error")
    
    def _sync_inputs_to_legacy(self):
        """Sync modern GUI inputs to legacy app for calculations."""
        if not self.legacy_app:
            return False
            
        try:
            # Sync product dimensions
            self.legacy_app.length_entry.delete(0, tk.END)
            self.legacy_app.length_entry.insert(0, self.length_widget.get())
            
            self.legacy_app.width_entry.delete(0, tk.END)
            self.legacy_app.width_entry.insert(0, self.width_widget.get())
            
            self.legacy_app.product_height_entry.delete(0, tk.END)
            self.legacy_app.product_height_entry.insert(0, self.height_widget.get())
            
            self.legacy_app.weight_entry.delete(0, tk.END)
            self.legacy_app.weight_entry.insert(0, self.weight_widget.get())
            
            # Sync engineering parameters
            self.legacy_app.clearance_entry.delete(0, tk.END)
            self.legacy_app.clearance_entry.insert(0, self.side_clearance_widget.get())
            
            self.legacy_app.clearance_above_entry.delete(0, tk.END)
            self.legacy_app.clearance_above_entry.insert(0, self.top_clearance_widget.get())
            
            self.legacy_app.ground_clearance_entry.delete(0, tk.END)
            self.legacy_app.ground_clearance_entry.insert(0, self.ground_clearance_widget.get())
            
            # Sync advanced options
            self.legacy_app.allow_3x4_skids_var.set(self.allow_3x4_var.get())
            
            if hasattr(self, 'floorboard_thickness_widget'):
                self.legacy_app.floorboard_thickness_entry.delete(0, tk.END)
                self.legacy_app.floorboard_thickness_entry.insert(0, self.floorboard_thickness_widget.get())
            
            # Sync lumber selections
            if hasattr(self, 'lumber_vars'):
                for width, var in self.lumber_vars.items():
                    if width in self.legacy_app.lumber_vars:
                        self.legacy_app.lumber_vars[width].set(var.get())
            
            return True
        except Exception as e:
            self.status_bar.set_status(f"Input sync error: {str(e)}", "error")
            return False
    
    def _generate_expressions(self):
        """Generate NX expressions using the legacy backend."""
        if not self.legacy_app:
            self.status_bar.set_status("Backend not available", "error")
            return
        
        # Validate all inputs first
        all_valid = all([
            self.length_widget.is_valid,
            self.width_widget.is_valid, 
            self.height_widget.is_valid,
            self.weight_widget.is_valid,
            self.side_clearance_widget.is_valid,
            self.top_clearance_widget.is_valid,
            self.ground_clearance_widget.is_valid
        ])
        
        if not all_valid:
            self.status_bar.set_status("Please correct input validation errors", "error")
            messagebox.showerror("Validation Error", 
                               "Please correct the highlighted input validation errors before generating expressions.")
            return
        
        # Show progress
        self.status_bar.show_progress(True)
        self.status_bar.set_status("Generating NX expressions...", "info")
        
        # Sync inputs to legacy app
        if not self._sync_inputs_to_legacy():
            self.status_bar.show_progress(False)
            return
        
        # Run generation in thread to prevent GUI freezing
        def generation_thread():
            try:
                # Redirect legacy app output to our results
                import io
                import contextlib
                
                output_buffer = io.StringIO()
                
                # Capture the legacy app's log messages
                original_log = self.legacy_app.log_message
                
                def capture_log(message):
                    output_buffer.write(f"{datetime.datetime.now().strftime('%H:%M:%S')} - {message}\\n")
                    # Also update our results in main thread
                    self.master.after(0, lambda: self._append_result(f"{datetime.datetime.now().strftime('%H:%M:%S')} - {message}\\n"))
                
                self.legacy_app.log_message = capture_log
                
                # Run the generation
                self.legacy_app.generate_expressions()
                
                # Restore original logging
                self.legacy_app.log_message = original_log
                
                # Update status in main thread
                self.master.after(0, lambda: self._generation_complete(True, "NX expressions generated successfully"))
                
            except Exception as e:
                error_msg = f"Generation failed: {str(e)}"
                self.master.after(0, lambda: self._generation_complete(False, error_msg))
        
        # Start generation thread
        threading.Thread(target=generation_thread, daemon=True).start()
    
    def _generation_complete(self, success: bool, message: str):
        """Handle completion of expression generation."""
        self.status_bar.show_progress(False)
        
        if success:
            self.status_bar.set_status(message, "success")
            self._append_result(f"\\n=== GENERATION COMPLETE ===\\n")
            self._append_result(f"Success: {message}\\n")
        else:
            self.status_bar.set_status(message, "error")
            self._append_result(f"\\n=== GENERATION FAILED ===\\n")
            self._append_result(f"Error: {message}\\n")
    
    def _append_result(self, text: str):
        """Append text to results display."""
        self.results_text.insert(tk.END, text)
        self.results_text.see(tk.END)
        self.master.update_idletasks()
    
    def _run_test_suite(self):
        """Run the test suite using legacy functionality."""
        if not self.legacy_app:
            self.status_bar.set_status("Backend not available", "error")
            return
        
        self.status_bar.show_progress(True)
        self.status_bar.set_status("Running test suite...", "info")
        
        def test_thread():
            try:
                # Capture test output
                def capture_test_log(message):
                    self.master.after(0, lambda: self._append_result(f"{message}\\n"))
                
                original_log = self.legacy_app.log_message
                self.legacy_app.log_message = capture_test_log
                
                # Run test suite
                self.legacy_app.run_quick_test_suite()
                
                # Restore logging
                self.legacy_app.log_message = original_log
                
                self.master.after(0, lambda: self._test_complete(True, "Test suite completed"))
                
            except Exception as e:
                error_msg = f"Test suite failed: {str(e)}"
                self.master.after(0, lambda: self._test_complete(False, error_msg))
        
        threading.Thread(target=test_thread, daemon=True).start()
    
    def _test_complete(self, success: bool, message: str):
        """Handle test suite completion."""
        self.status_bar.show_progress(False)
        
        if success:
            self.status_bar.set_status(message, "success")
        else:
            self.status_bar.set_status(message, "error")
    
    def _on_tab_changed(self, event=None):
        """Handle tab change events."""
        current_tab = self.notebook.index(self.notebook.select())
        
        if current_tab == 1:  # 3D Preview tab
            self._update_3d_preview()
    
    def _on_dimension_change(self, event=None):
        """Handle dimension input changes for real-time updates."""
        self._update_quick_preview()
    
    def _update_quick_preview(self):
        """Update the quick preview display."""
        try:
            # Get current values
            length = float(self.length_widget.get() or "0")
            width = float(self.width_widget.get() or "0")
            height = float(self.height_widget.get() or "0")
            weight = float(self.weight_widget.get() or "0")
            
            side_clearance = float(self.side_clearance_widget.get() or "0")
            top_clearance = float(self.top_clearance_widget.get() or "0")
            
            # Calculate crate dimensions (simplified)
            crate_width = width + (2 * side_clearance) + 1.5  # Add material thickness
            crate_length = length + (2 * side_clearance) + 1.5
            crate_height = height + top_clearance + 5.0  # Add skid and top clearances
            
            # Update displays
            self.preview_dimensions.config(text=f"Crate: {crate_width:.1f}\" × {crate_length:.1f}\" × {crate_height:.1f}\"")
            
            # Calculate volume and ratios
            volume_ft3 = (crate_width * crate_length * crate_height) / 1728  # Convert to ft³
            weight_ratio = weight / volume_ft3 if volume_ft3 > 0 else 0
            
            self.volume_label.config(text=f"Volume: {volume_ft3:.1f} ft³")
            self.weight_ratio_label.config(text=f"Weight ratio: {weight_ratio:.1f} lbs/ft³")
            
        except (ValueError, ZeroDivisionError):
            # Handle invalid input gracefully
            self.preview_dimensions.config(text="Crate: Invalid dimensions")
            self.volume_label.config(text="Volume: ---")
            self.weight_ratio_label.config(text="Weight ratio: ---")
    
    def _update_3d_preview(self):
        """Update the 3D preview."""
        try:
            dimensions = {
                'width': float(self.width_widget.get() or "100"),
                'length': float(self.length_widget.get() or "96"),
                'height': float(self.height_widget.get() or "30")
            }
            
            # Add clearances for total crate size
            side_clearance = float(self.side_clearance_widget.get() or "2")
            top_clearance = float(self.top_clearance_widget.get() or "2")
            
            dimensions['width'] += (2 * side_clearance) + 1.5
            dimensions['length'] += (2 * side_clearance) + 1.5  
            dimensions['height'] += top_clearance + 5.0
            
            self.crate_preview.update_preview(dimensions)
            self.status_bar.set_status("3D preview updated", "success")
            
        except Exception as e:
            self.status_bar.set_status(f"Preview update failed: {str(e)}", "warning")


def create_modern_autocrate_app(master, legacy_app_class):
    """
    Factory function to create the modern AutoCrate application.
    
    Args:
        master: The tkinter root window
        legacy_app_class: The original CrateApp class for calculations
    
    Returns:
        ModernCrateApp instance
    """
    return ModernCrateApp(master, legacy_app_class)