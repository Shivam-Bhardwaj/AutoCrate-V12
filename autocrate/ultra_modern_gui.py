"""
AutoCrate Ultra-Modern GUI with CustomTkinter
==============================================
A cutting-edge, modern interface for AutoCrate using CustomTkinter
with dark mode, animations, and glass morphism effects.
"""

import customtkinter as ctk
from customtkinter import CTkFont
import tkinter as tk
from tkinter import messagebox, filedialog
import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
import math
from PIL import Image, ImageDraw, ImageFilter
import threading
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from autocrate import nx_expressions_generator as nx_gen
    from autocrate import plywood_layout_generator
    from autocrate import security_utils
except ImportError:
    import nx_expressions_generator as nx_gen
    import plywood_layout_generator
    import security_utils

try:
    import quick_test
except ImportError:
    quick_test = None

# Configure CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class ModernCard(ctk.CTkFrame):
    """Modern card component with shadow and hover effects"""
    
    def __init__(self, parent, title="", **kwargs):
        super().__init__(parent, corner_radius=15, **kwargs)
        
        self.title = title
        self.is_hovered = False
        
        # Configure card appearance
        self.configure(
            fg_color=("#ffffff", "#1e1e1e"),
            border_width=1,
            border_color=("#e0e0e0", "#2d2d2d")
        )
        
        # Add title if provided
        if title:
            self.title_label = ctk.CTkLabel(
                self,
                text=title,
                font=CTkFont(size=14, weight="bold"),
                text_color=("#000000", "#ffffff")
            )
            self.title_label.pack(pady=(10, 5), padx=15, anchor="w")
        
        # Bind hover events
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, event):
        """Handle mouse enter"""
        self.configure(border_color=("#007acc", "#0098ff"))
        self.configure(border_width=2)
    
    def _on_leave(self, event):
        """Handle mouse leave"""
        self.configure(border_color=("#e0e0e0", "#2d2d2d"))
        self.configure(border_width=1)

class AnimatedButton(ctk.CTkButton):
    """Button with animation effects"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(
            corner_radius=8,
            hover_color=("#0056b3", "#0098ff"),
            font=CTkFont(size=14, weight="bold")
        )

class ModernInputField(ctk.CTkFrame):
    """Modern input field with label and validation"""
    
    def __init__(self, parent, label="", units="", default_value="", validator=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.validator = validator
        self.is_valid = True
        
        # Create container (compact for fullscreen)
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="x", pady=2)
        
        # Label
        if label:
            self.label = ctk.CTkLabel(
                container,
                text=label,
                font=CTkFont(size=12),
                text_color=("#666666", "#aaaaaa")
            )
            self.label.pack(anchor="w")
        
        # Input container
        input_frame = ctk.CTkFrame(container, fg_color="transparent")
        input_frame.pack(fill="x", pady=(2, 0))
        
        # Entry field (compact for fullscreen)
        self.entry = ctk.CTkEntry(
            input_frame,
            height=28,
            corner_radius=6,
            border_width=1,
            border_color=("#cccccc", "#404040"),
            font=CTkFont(size=12)
        )
        self.entry.pack(side="left", fill="x", expand=True)
        
        if default_value:
            self.entry.insert(0, default_value)
        
        # Units label
        if units:
            self.units_label = ctk.CTkLabel(
                input_frame,
                text=units,
                font=CTkFont(size=11),
                text_color=("#888888", "#999999")
            )
            self.units_label.pack(side="left", padx=(8, 0))
        
        # Bind validation
        self.entry.bind("<FocusOut>", self._validate)
        self.entry.bind("<KeyRelease>", self._validate)
    
    def _validate(self, event=None):
        """Validate input"""
        if self.validator:
            value = self.get()
            if value and not self.validator(value):
                self.entry.configure(border_color="#ff4444")
                self.is_valid = False
            else:
                self.entry.configure(border_color=("#cccccc", "#404040"))
                self.is_valid = True
    
    def get(self):
        """Get entry value"""
        return self.entry.get()
    
    def set(self, value):
        """Set entry value"""
        self.entry.delete(0, "end")
        self.entry.insert(0, value)

class Preview3D(ctk.CTkFrame):
    """3D preview using canvas with modern styling"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, corner_radius=15, **kwargs)
        
        self.configure(
            fg_color=("#f8f9fa", "#0d0d0d"),
            border_width=1,
            border_color=("#e0e0e0", "#2d2d2d")
        )
        
        # Title
        title_frame = ctk.CTkFrame(self, fg_color="transparent", height=40)
        title_frame.pack(fill="x", padx=15, pady=(15, 5))
        title_frame.pack_propagate(False)
        
        title = ctk.CTkLabel(
            title_frame,
            text="🎯 3D PREVIEW",
            font=CTkFont(size=14, weight="bold"),
            text_color=("#000000", "#ffffff")
        )
        title.pack(side="left")
        
        # Canvas for 3D view
        self.canvas = tk.Canvas(
            self,
            bg="#0d0d0d" if ctk.get_appearance_mode() == "Dark" else "#f0f0f0",
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True, padx=15, pady=(5, 15))
        
        # Initial crate parameters
        self.width = 96
        self.length = 100
        self.height = 30
        self.rotation_x = 25
        self.rotation_y = 45
        
        # Mouse interaction
        self.last_x = 0
        self.last_y = 0
        self.canvas.bind("<Button-1>", self._on_mouse_down)
        self.canvas.bind("<B1-Motion>", self._on_mouse_drag)
        self.canvas.bind("<MouseWheel>", self._on_mouse_wheel)
        
        # Auto-rotate animation
        self.auto_rotate = True
        self._animate()
    
    def _on_mouse_down(self, event):
        """Handle mouse down"""
        self.last_x = event.x
        self.last_y = event.y
        self.auto_rotate = False
    
    def _on_mouse_drag(self, event):
        """Handle mouse drag for rotation"""
        dx = event.x - self.last_x
        dy = event.y - self.last_y
        self.rotation_y += dx * 0.5
        self.rotation_x += dy * 0.5
        self.last_x = event.x
        self.last_y = event.y
        self.draw_crate()
    
    def _on_mouse_wheel(self, event):
        """Handle mouse wheel for zoom"""
        # Zoom functionality can be added here
        pass
    
    def update_dimensions(self, width, length, height):
        """Update crate dimensions"""
        try:
            self.width = float(width) if width else 96
            self.length = float(length) if length else 100
            self.height = float(height) if height else 30
            self.draw_crate()
        except:
            pass
    
    def draw_crate(self):
        """Draw 3D crate representation"""
        self.canvas.delete("all")
        
        # Get canvas dimensions
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w <= 1 or h <= 1:
            return
        
        # Calculate scale
        max_dim = max(self.width, self.length, self.height)
        scale = min(w, h) * 0.4 / max_dim
        
        # Center point
        cx, cy = w / 2, h / 2
        
        # Convert rotation to radians
        rx = math.radians(self.rotation_x)
        ry = math.radians(self.rotation_y)
        
        # Define crate vertices (8 corners of the box)
        vertices = []
        corners = [
            (-self.width/2, -self.length/2, -self.height/2),  # 0: bottom-back-left
            (self.width/2, -self.length/2, -self.height/2),   # 1: bottom-back-right
            (-self.width/2, self.length/2, -self.height/2),   # 2: bottom-front-left
            (self.width/2, self.length/2, -self.height/2),    # 3: bottom-front-right
            (-self.width/2, -self.length/2, self.height/2),   # 4: top-back-left
            (self.width/2, -self.length/2, self.height/2),    # 5: top-back-right
            (-self.width/2, self.length/2, self.height/2),    # 6: top-front-left
            (self.width/2, self.length/2, self.height/2),     # 7: top-front-right
        ]
        
        for x, y, z in corners:
            # Apply Y rotation (around vertical axis)
            x1 = x * math.cos(ry) - y * math.sin(ry)
            y1 = x * math.sin(ry) + y * math.cos(ry)
            
            # Apply X rotation (tilt)
            y2 = y1 * math.cos(rx) - z * math.sin(rx)
            z1 = y1 * math.sin(rx) + z * math.cos(rx)
            
            # Project to 2D (isometric-style)
            px = cx + x1 * scale
            py = cy - z1 * scale  # Negative because screen Y increases downward
            vertices.append((px, py))
        
        # Define edges
        edges = [
            (0, 1), (1, 3), (3, 2), (2, 0),  # Bottom
            (4, 5), (5, 7), (7, 6), (6, 4),  # Top
            (0, 4), (1, 5), (2, 6), (3, 7)   # Vertical
        ]
        
        # Sort edges by depth for proper rendering
        edge_depths = []
        for start, end in edges:
            # Calculate average Y position for depth sorting
            avg_y = (vertices[start][1] + vertices[end][1]) / 2
            edge_depths.append((avg_y, start, end))
        edge_depths.sort(key=lambda x: x[0], reverse=True)
        
        # Draw edges with modern styling and depth-based coloring
        for _, start, end in edge_depths:
            # Determine if edge is in back or front based on Y position
            is_back = vertices[start][1] < self.canvas.winfo_height() / 2 - 20
            
            if is_back:
                edge_color = "#006644" if ctk.get_appearance_mode() == "Dark" else "#005588"
                width = 1
            else:
                edge_color = "#00ff88" if ctk.get_appearance_mode() == "Dark" else "#007acc"
                width = 2
            
            self.canvas.create_line(
                vertices[start][0], vertices[start][1],
                vertices[end][0], vertices[end][1],
                fill=edge_color, width=width, smooth=True
            )
        
        # Draw vertices
        vertex_color = "#ffffff" if ctk.get_appearance_mode() == "Dark" else "#0056b3"
        for x, y in vertices:
            self.canvas.create_oval(
                x-3, y-3, x+3, y+3,
                fill=vertex_color, outline=edge_color, width=1
            )
        
        # Draw dimension labels
        label_color = "#cccccc" if ctk.get_appearance_mode() == "Dark" else "#333333"
        font = ("Segoe UI", 10)
        
        # Width label
        self.canvas.create_text(
            cx, cy + h/2 - 30,
            text=f"Width: {self.width}\"",
            fill=label_color, font=font
        )
        
        # Length label
        self.canvas.create_text(
            cx - w/2 + 60, cy,
            text=f"Length: {self.length}\"",
            fill=label_color, font=font, angle=90
        )
        
        # Height label
        self.canvas.create_text(
            cx + w/2 - 60, cy,
            text=f"Height: {self.height}\"",
            fill=label_color, font=font
        )
    
    def _animate(self):
        """Auto-rotate animation"""
        if self.auto_rotate:
            self.rotation_y += 1
            self.draw_crate()
        self.after(50, self._animate)

class UltraModernAutocrateGUI:
    """Ultra-modern AutoCrate interface with CustomTkinter"""
    
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("AutoCrate Pro - Engineering Design Suite")
        
        # Set fullscreen mode
        self.root.attributes('-fullscreen', True)
        
        # Bind escape key to exit fullscreen (optional)
        self.root.bind('<Escape>', lambda e: self.root.attributes('-fullscreen', False))
        self.root.bind('<F11>', lambda e: self.toggle_fullscreen())
        
        # Get screen dimensions for responsive layout
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        
        # Create a hidden CrateApp instance for backend calculations
        self.hidden_root = tk.Tk()
        self.hidden_root.withdraw()  # Hide the window
        self.crate_app = nx_gen.CrateApp(self.hidden_root)
        
        # Override message dialog to prevent popups from CrateApp
        self.crate_app.master.tk.call('package', 'require', 'msgcat')
        self.crate_app.master.tk.call('msgcat::mcset', 'en', 'OK', 'OK')
        
        # Set window icon if available
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "autocrate_icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except:
            pass
        
        # Initialize variables
        self.setup_variables()
        
        # Create UI
        self.create_header()
        self.create_main_content()
        self.create_status_bar()
        
        # No need to center window in fullscreen mode
        # self.center_window()
        
        # Initial preview update
        self.root.after(500, self.update_preview)
    
    def setup_variables(self):
        """Initialize all variables"""
        self.inputs = {}
        self.preview_3d = None
        self.status_label = None
        self.progress_bar = None
    
    def create_header(self):
        """Create modern header"""
        header = ctk.CTkFrame(self.root, height=70, corner_radius=0)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        
        # Logo and title
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left", padx=30, pady=15)
        
        app_title = ctk.CTkLabel(
            title_frame,
            text="AUTOCRATE",
            font=CTkFont(size=28, weight="bold"),
            text_color=("#000000", "#ffffff")
        )
        app_title.pack(side="left")
        
        version_label = ctk.CTkLabel(
            title_frame,
            text="PRO v12.2",
            font=CTkFont(size=12),
            text_color=("#666666", "#999999")
        )
        version_label.pack(side="left", padx=(15, 0))
        
        # Action buttons
        button_frame = ctk.CTkFrame(header, fg_color="transparent")
        button_frame.pack(side="right", padx=30, pady=15)
        
        # Generate button with accent color
        generate_btn = AnimatedButton(
            button_frame,
            text="⚡ Generate",
            width=120,
            height=35,
            fg_color=("#007acc", "#0098ff"),
            hover_color=("#0056b3", "#00aaff"),
            command=self.generate_expression_file
        )
        generate_btn.pack(side="left", padx=5)
        
        # Quick test button
        test_btn = AnimatedButton(
            button_frame,
            text="🧪 Test",
            width=100,
            height=35,
            fg_color=("#28a745", "#34ce57"),
            hover_color=("#218838", "#2eb94c"),
            command=self.run_quick_test
        )
        test_btn.pack(side="left", padx=5)
    
    def create_main_content(self):
        """Create main content area with tabs"""
        # Create tab view
        self.tabview = ctk.CTkTabview(
            self.root,
            corner_radius=10,
            fg_color=("#f0f0f0", "#1a1a1a"),
            segmented_button_fg_color=("#e0e0e0", "#2d2d2d"),
            segmented_button_selected_color=("#007acc", "#0098ff"),
            segmented_button_selected_hover_color=("#0056b3", "#0078cc")
        )
        self.tabview.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Add tabs
        self.tabview.add("📐 Design")
        self.tabview.add("⚙️ Advanced")
        self.tabview.add("📊 Preview")
        
        # Create Design tab content
        self.create_design_tab()
        # Create Advanced tab content  
        self.create_advanced_tab()
        # Create Preview tab content
        self.create_preview_tab()
        
    def create_design_tab(self):
        """Create the main design input tab"""
        design_tab = self.tabview.tab("📐 Design")
        
        # Main container with two columns
        main_container = ctk.CTkFrame(design_tab, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left panel - Input forms with responsive width
        panel_width = int(450 * getattr(self, 'scale_factor', 1))
        left_panel = ctk.CTkScrollableFrame(
            main_container,
            width=panel_width,
            corner_radius=0,
            fg_color="transparent"
        )
        left_panel.pack(side="left", fill="y", padx=(0, 5))
        
        # Product specifications card
        product_card = ModernCard(left_panel, title="📦 Product Specifications")
        product_card.pack(fill="x", pady=(0, 15))
        
        product_content = ctk.CTkFrame(product_card, fg_color="transparent")
        product_content.pack(fill="x", padx=15, pady=(0, 10))
        
        # Product dimensions
        self.inputs['product_weight'] = ModernInputField(
            product_content,
            label="Product Weight",
            units="lbs",
            default_value="8000",
            validator=lambda x: x.replace('.', '').isdigit()
        )
        self.inputs['product_weight'].pack(fill="x", pady=5)
        
        self.inputs['product_length'] = ModernInputField(
            product_content,
            label="Product Length",
            units="inches",
            default_value="96",
            validator=lambda x: x.replace('.', '').isdigit()
        )
        self.inputs['product_length'].pack(fill="x", pady=5)
        
        self.inputs['product_width'] = ModernInputField(
            product_content,
            label="Product Width",
            units="inches",
            default_value="100",
            validator=lambda x: x.replace('.', '').isdigit()
        )
        self.inputs['product_width'].pack(fill="x", pady=5)
        
        self.inputs['product_height'] = ModernInputField(
            product_content,
            label="Product Height",
            units="inches",
            default_value="30",
            validator=lambda x: x.replace('.', '').isdigit()
        )
        self.inputs['product_height'].pack(fill="x", pady=5)
        
        # Clearance specifications card
        clearance_card = ModernCard(left_panel, title="📏 Clearance Requirements")
        clearance_card.pack(fill="x", pady=(0, 15))
        
        clearance_content = ctk.CTkFrame(clearance_card, fg_color="transparent")
        clearance_content.pack(fill="x", padx=15, pady=(0, 10))
        
        self.inputs['clearance_length'] = ModernInputField(
            clearance_content,
            label="Length Clearance",
            units="inches",
            default_value="5",
            validator=lambda x: x.replace('.', '').isdigit()
        )
        self.inputs['clearance_length'].pack(fill="x", pady=5)
        
        self.inputs['clearance_width'] = ModernInputField(
            clearance_content,
            label="Width Clearance",
            units="inches",
            default_value="5",
            validator=lambda x: x.replace('.', '').isdigit()
        )
        self.inputs['clearance_width'].pack(fill="x", pady=5)
        
        self.inputs['clearance_height'] = ModernInputField(
            clearance_content,
            label="Height Clearance",
            units="inches",
            default_value="2",
            validator=lambda x: x.replace('.', '').isdigit()
        )
        self.inputs['clearance_height'].pack(fill="x", pady=5)
        
        # Engineering parameters card
        eng_card = ModernCard(left_panel, title="⚙️ Engineering Parameters")
        eng_card.pack(fill="x", pady=(0, 15))
        
        eng_content = ctk.CTkFrame(eng_card, fg_color="transparent")
        eng_content.pack(fill="x", padx=15, pady=(0, 10))
        
        self.inputs['center_support_threshold'] = ModernInputField(
            eng_content,
            label="Center Support Threshold",
            units="lbs",
            default_value="2000",
            validator=lambda x: x.replace('.', '').isdigit()
        )
        self.inputs['center_support_threshold'].pack(fill="x", pady=5)
        
        # Right panel - 3D Preview
        right_panel = ctk.CTkFrame(
            main_container,
            fg_color="transparent"
        )
        right_panel.pack(side="right", fill="both", expand=True)
        
        # 3D Preview
        self.preview_3d = Preview3D(right_panel)
        self.preview_3d.pack(fill="both", expand=True)
        
        # Bind input changes to preview update
        for input_field in self.inputs.values():
            if hasattr(input_field, 'entry'):
                input_field.entry.bind("<KeyRelease>", lambda e: self.update_preview())
    
    def create_status_bar(self):
        """Create modern status bar"""
        status_frame = ctk.CTkFrame(self.root, height=40, corner_radius=0)
        status_frame.pack(fill="x", side="bottom")
        status_frame.pack_propagate(False)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="✅ Ready",
            font=CTkFont(size=12),
            text_color=("#666666", "#aaaaaa")
        )
        self.status_label.pack(side="left", padx=20)
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            status_frame,
            width=200,
            height=10,
            corner_radius=5
        )
        self.progress_bar.pack(side="right", padx=20)
        self.progress_bar.set(0)
    
    def update_preview(self):
        """Update 3D preview"""
        if self.preview_3d:
            try:
                width = float(self.inputs['product_width'].get()) if self.inputs['product_width'].get() else 100
                length = float(self.inputs['product_length'].get()) if self.inputs['product_length'].get() else 96
                height = float(self.inputs['product_height'].get()) if self.inputs['product_height'].get() else 30
                
                # Add clearances
                width += 2 * float(self.inputs['clearance_width'].get() if self.inputs['clearance_width'].get() else 5)
                length += 2 * float(self.inputs['clearance_length'].get() if self.inputs['clearance_length'].get() else 5)
                height += float(self.inputs['clearance_height'].get() if self.inputs['clearance_height'].get() else 2)
                
                self.preview_3d.update_dimensions(width, length, height)
            except:
                pass
    
    def set_status(self, message, progress=None):
        """Update status bar"""
        if self.status_label:
            self.status_label.configure(text=message)
        if self.progress_bar and progress is not None:
            self.progress_bar.set(progress)
    
    def generate_expression_file(self):
        """Generate NX expression file"""
        self.set_status("🔄 Generating expression file...", 0.3)
        
        try:
            # Collect all input values
            params = self.collect_parameters()
            
            # Validate inputs
            if not self.validate_inputs(params):
                self.set_status("❌ Validation failed", 0)
                return
            
            self.set_status("🔧 Calculating components...", 0.5)
            
            # Update CrateApp with our parameters
            self.update_crate_app_values(params)
            
            # Override the CrateApp's log_message to capture status
            original_log = self.crate_app.log_message
            status_messages = []
            
            def capture_log(msg):
                status_messages.append(msg)
                # Update our status bar
                self.set_status(f"🔧 {msg}", 0.7)
            
            self.crate_app.log_message = capture_log
            
            # Generate expression file using CrateApp
            try:
                self.crate_app.generate_expressions()
                # Check if successful by looking for success message
                success = any('successfully' in msg.lower() or 'generated' in msg.lower() 
                             for msg in status_messages)
                
                # Extract filename from messages
                filename = None
                for msg in status_messages:
                    if '.exp' in msg:
                        # Extract filename from message
                        import re
                        match = re.search(r'([^\s]+\.exp)', msg)
                        if match:
                            filename = match.group(1)
                            break
                
                result = {'success': success, 'filename': filename or 'Expression file generated'}
            finally:
                # Restore original log function
                self.crate_app.log_message = original_log
            
            if result and result.get('success'):
                self.set_status("✅ Expression file generated successfully!", 1.0)
                
                # Show success dialog
                dialog = ctk.CTkToplevel(self.root)
                dialog.title("Success")
                dialog.geometry("400x200")
                dialog.transient(self.root)
                
                msg_label = ctk.CTkLabel(
                    dialog,
                    text="Expression file generated successfully!",
                    font=CTkFont(size=16, weight="bold")
                )
                msg_label.pack(pady=30)
                
                file_label = ctk.CTkLabel(
                    dialog,
                    text=f"File: {result.get('filename', 'Unknown')}",
                    font=CTkFont(size=12)
                )
                file_label.pack(pady=10)
                
                ok_btn = AnimatedButton(
                    dialog,
                    text="OK",
                    width=100,
                    command=dialog.destroy
                )
                ok_btn.pack(pady=20)
            else:
                self.set_status("❌ Generation failed", 0)
                messagebox.showerror("Error", "Failed to generate expression file")
                
        except Exception as e:
            self.set_status("❌ Error occurred", 0)
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def collect_parameters(self):
        """Collect all parameters from inputs"""
        params = {}
        
        # Map input fields to parameter names
        field_mapping = {
            'product_weight': 'product_weight',
            'product_length': 'product_length',
            'product_width': 'product_width',
            'product_height': 'product_height',
            'clearance_length': 'clearance_length',
            'clearance_width': 'clearance_width',
            'clearance_height': 'clearance_height',
            'center_support_threshold': 'center_support_threshold'
        }
        
        # Collect values
        for field_name, param_name in field_mapping.items():
            if field_name in self.inputs:
                value = self.inputs[field_name].get()
                try:
                    params[param_name] = float(value) if value else 0
                except:
                    params[param_name] = 0
        
        # Set default values for missing parameters
        params['plywood_thickness'] = 0.25
        params['cleat_width'] = 3.5
        params['cleat_thickness'] = 0.75
        params['cleat_member_width'] = 1.5
        params['floorboard_thickness'] = 1.5
        params['small_board_threshold'] = 3.0
        params['use_small_board_for_remainder'] = True
        params['ground_clearance'] = 1.0
        params['allow_3x4_skids'] = True
        params['max_gap'] = 0.25
        params['min_custom'] = 2.5
        params['force_custom'] = True
        
        return params
    
    def update_crate_app_values(self, params):
        """Update the CrateApp instance with collected parameters"""
        # Update product dimensions
        self.crate_app.length_entry.delete(0, tk.END)
        self.crate_app.length_entry.insert(0, str(params.get('product_length', 96)))
        
        self.crate_app.width_entry.delete(0, tk.END)
        self.crate_app.width_entry.insert(0, str(params.get('product_width', 100)))
        
        self.crate_app.product_height_entry.delete(0, tk.END)
        self.crate_app.product_height_entry.insert(0, str(params.get('product_height', 30)))
        
        self.crate_app.weight_entry.delete(0, tk.END)
        self.crate_app.weight_entry.insert(0, str(params.get('product_weight', 8000)))
        
        # Update clearances
        self.crate_app.clearance_entry.delete(0, tk.END)
        self.crate_app.clearance_entry.insert(0, str(params.get('clearance_width', 2.0)))
        
        self.crate_app.clearance_above_entry.delete(0, tk.END)
        self.crate_app.clearance_above_entry.insert(0, str(params.get('clearance_height', 2.0)))
        
        self.crate_app.ground_clearance_entry.delete(0, tk.END)
        self.crate_app.ground_clearance_entry.insert(0, str(params.get('ground_clearance', 1.0)))
        
        # Update floorboard settings
        self.crate_app.floorboard_thickness_entry.delete(0, tk.END)
        self.crate_app.floorboard_thickness_entry.insert(0, str(params.get('floorboard_thickness', 1.5)))
        
        self.crate_app.max_gap_entry.delete(0, tk.END)
        self.crate_app.max_gap_entry.insert(0, str(params.get('max_gap', 0.25)))
        
        self.crate_app.min_custom_entry.delete(0, tk.END)
        self.crate_app.min_custom_entry.insert(0, str(params.get('min_custom', 2.5)))
        
        # Update checkboxes
        self.crate_app.allow_3x4_skids_var.set(params.get('allow_3x4_skids', True))
        self.crate_app.force_custom_var.set(params.get('force_custom', True))
    
    def validate_inputs(self, params):
        """Validate input parameters"""
        errors = []
        
        # Check product dimensions
        if params.get('product_length', 0) <= 0:
            errors.append("Product length must be greater than 0")
        if params.get('product_width', 0) <= 0:
            errors.append("Product width must be greater than 0")
        if params.get('product_height', 0) <= 0:
            errors.append("Product height must be greater than 0")
        if params.get('product_weight', 0) <= 0:
            errors.append("Product weight must be greater than 0")
        
        # Check clearances
        if params.get('clearance_width', 0) < 0:
            errors.append("Width clearance cannot be negative")
        if params.get('clearance_height', 0) < 0:
            errors.append("Height clearance cannot be negative")
        
        # Show errors if any
        if errors:
            messagebox.showerror("Validation Error", "\n".join(errors))
            return False
        
        return True
    
    def validate_inputs_original(self, params):
        """Validate input parameters"""
        # Check for required fields
        required = ['product_weight', 'product_length', 'product_width', 'product_height']
        for field in required:
            if field not in params or params[field] <= 0:
                messagebox.showerror("Validation Error", f"Invalid {field.replace('_', ' ').title()}")
                return False
        
        # Check ranges
        if params['product_weight'] > 70000:
            messagebox.showerror("Validation Error", "Product weight exceeds maximum (70,000 lbs)")
            return False
        
        if any(params[f'product_{dim}'] > 130 for dim in ['length', 'width']):
            messagebox.showerror("Validation Error", "Product dimensions exceed maximum (130 inches)")
            return False
        
        if params['product_height'] > 72:
            messagebox.showerror("Validation Error", "Product height exceeds maximum (72 inches)")
            return False
        
        return True
    
    def run_quick_test(self):
        """Run quick test suite"""
        self.set_status("🧪 Running tests...", 0.5)
        
        try:
            # Use the CrateApp's test suite
            self.crate_app.run_quick_test_suite()
            self.set_status("✅ Tests completed!", 1.0)
            messagebox.showinfo("Test Suite", "Quick test suite completed successfully!\nCheck the logs for details.")
        except Exception as e:
            self.set_status("❌ Test failed", 0)
            messagebox.showerror("Test Error", f"Test suite failed: {str(e)}")
        
    
    def center_window(self):
        """Center window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_advanced_tab(self):
        """Create advanced settings tab"""
        advanced_tab = self.tabview.tab("⚙️ Advanced")
        
        # Create main frame (no scroll, use grid for responsive layout)
        main_frame = ctk.CTkFrame(
            advanced_tab,
            corner_radius=0,
            fg_color="transparent"
        )
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Use scrollable frame for Advanced tab to ensure all content is visible
        scroll_frame = ctk.CTkScrollableFrame(
            main_frame,
            corner_radius=0,
            fg_color="transparent"
        )
        scroll_frame.pack(fill="both", expand=True)
        
        # Configure grid for 2-column layout on larger screens, 1-column on smaller
        if getattr(self, 'screen_width', 1920) < 1600:
            columns = 1
        else:
            columns = 2
        
        # Material Specifications Card
        material_card = ModernCard(scroll_frame, title="🔧 Material Specifications")
        material_card.pack(fill="x", pady=5, padx=10)
        
        material_content = ctk.CTkFrame(material_card, fg_color="transparent")
        material_content.pack(fill="x", padx=15, pady=(0, 10))
        
        # Panel material info (read-only display)
        panel_info = ctk.CTkLabel(
            material_content,
            text="Panel Material: 1/4\" (0.25\") Plywood - ASTM D6007 Compliant",
            font=CTkFont(size=12),
            text_color=("#666666", "#aaaaaa")
        )
        panel_info.pack(anchor="w", pady=5)
        
        cleat_info = ctk.CTkLabel(
            material_content,
            text="Cleat Material: 1x4\" Lumber (0.75\" × 3.5\" actual) - SPF Grade 2+",
            font=CTkFont(size=12),
            text_color=("#666666", "#aaaaaa")
        )
        cleat_info.pack(anchor="w", pady=5)
        
        # Floorboard Configuration Card
        floor_card = ModernCard(scroll_frame, title="📦 Floorboard Configuration")
        floor_card.pack(fill="x", pady=5, padx=10)
        
        floor_content = ctk.CTkFrame(floor_card, fg_color="transparent")
        floor_content.pack(fill="x", padx=15, pady=(0, 10))
        
        # Floorboard thickness
        self.inputs['floorboard_thickness'] = ModernInputField(
            floor_content,
            label="Floorboard Thickness",
            units="inches",
            default_value="1.5",
            validator=lambda x: x.replace('.', '').isdigit()
        )
        self.inputs['floorboard_thickness'].pack(fill="x", pady=5)
        
        # Lumber sizes checkboxes
        lumber_label = ctk.CTkLabel(
            floor_content,
            text="Available Lumber Sizes:",
            font=CTkFont(size=12, weight="bold"),
            text_color=("#000000", "#ffffff")
        )
        lumber_label.pack(anchor="w", pady=(10, 5))
        
        lumber_frame = ctk.CTkFrame(floor_content, fg_color="transparent")
        lumber_frame.pack(fill="x", pady=5)
        
        self.lumber_vars = {}
        lumber_sizes = [("2x6 (5.5\")", 5.5), ("2x8 (7.25\")", 7.25), 
                       ("2x10 (9.25\")", 9.25), ("2x12 (11.25\")", 11.25)]
        
        for i, (name, size) in enumerate(lumber_sizes):
            var = tk.BooleanVar(value=True)
            self.lumber_vars[size] = var
            checkbox = ctk.CTkCheckBox(
                lumber_frame,
                text=name,
                variable=var,
                width=150
            )
            checkbox.grid(row=i//2, column=i%2, padx=10, pady=5, sticky="w")
        
        # Gap and custom board settings
        self.inputs['max_gap'] = ModernInputField(
            floor_content,
            label="Maximum Gap Between Boards",
            units="inches",
            default_value="0.25",
            validator=lambda x: x.replace('.', '').isdigit()
        )
        self.inputs['max_gap'].pack(fill="x", pady=5)
        
        self.inputs['min_custom'] = ModernInputField(
            floor_content,
            label="Minimum Custom Board Width",
            units="inches",
            default_value="2.5",
            validator=lambda x: x.replace('.', '').isdigit()
        )
        self.inputs['min_custom'].pack(fill="x", pady=5)
        
        # Force custom board checkbox
        self.force_custom_var = tk.BooleanVar(value=True)
        force_custom_check = ctk.CTkCheckBox(
            floor_content,
            text="Force center custom board for better load distribution",
            variable=self.force_custom_var
        )
        force_custom_check.pack(anchor="w", pady=(10, 5))
        
        # Skid Configuration Card
        skid_card = ModernCard(scroll_frame, title="🏗️ Skid Configuration")
        skid_card.pack(fill="x", pady=5, padx=10)
        
        skid_content = ctk.CTkFrame(skid_card, fg_color="transparent")
        skid_content.pack(fill="x", padx=15, pady=(0, 10))
        
        # Ground clearance
        self.inputs['ground_clearance'] = ModernInputField(
            skid_content,
            label="Ground Clearance (Forklift Access)",
            units="inches",
            default_value="1.0",
            validator=lambda x: x.replace('.', '').isdigit()
        )
        self.inputs['ground_clearance'].pack(fill="x", pady=5)
        
        # Allow 3x4 skids checkbox
        self.allow_3x4_skids_var = tk.BooleanVar(value=True)
        allow_3x4_check = ctk.CTkCheckBox(
            skid_content,
            text="Allow 3x4 skids for lighter loads (unchecked uses 4x4 minimum)",
            variable=self.allow_3x4_skids_var
        )
        allow_3x4_check.pack(anchor="w", pady=(10, 5))
    
    def update_large_preview(self):
        """Update the large 3D preview canvas"""
        if hasattr(self, 'large_preview_canvas'):
            # Clear canvas
            self.large_preview_canvas.delete("all")
            
            # Get canvas dimensions
            w = self.large_preview_canvas.winfo_width()
            h = self.large_preview_canvas.winfo_height()
            if w <= 1 or h <= 1:
                # Schedule update after canvas is rendered
                self.root.after(100, self.update_large_preview)
                return
            
            # Draw a simple 3D crate representation
            cx, cy = w/2, h/2
            size = min(w, h) * 0.3
            
            # Draw crate edges
            self.large_preview_canvas.create_rectangle(
                cx - size, cy - size/2,
                cx + size, cy + size/2,
                outline="#00ff88" if ctk.get_appearance_mode() == "Dark" else "#007acc",
                width=2
            )
            
            # Add text
            self.large_preview_canvas.create_text(
                cx, cy + size/2 + 30,
                text="3D Preview - Coming Soon",
                fill="#888888",
                font=('Arial', 12)
            )
    
    def create_preview_tab(self):
        """Create the 3D preview tab"""
        preview_tab = self.tabview.tab("📊 Preview")
        
        # Create container
        preview_container = ctk.CTkFrame(preview_tab, fg_color="transparent")
        preview_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            preview_container,
            text="3D Crate Visualization",
            font=CTkFont(size=18, weight="bold"),
            text_color=("#000000", "#ffffff")
        )
        title_label.pack(pady=(0, 20))
        
        # Move the 3D preview here if it exists
        # For now, create a placeholder
        preview_frame = ModernCard(preview_container, title="")
        preview_frame.pack(fill="both", expand=True)
        
        # Create larger 3D preview canvas
        self.large_preview_canvas = tk.Canvas(
            preview_frame,
            bg="#1a1a1a" if ctk.get_appearance_mode() == "Dark" else "#f0f0f0",
            highlightthickness=0
        )
        self.large_preview_canvas.pack(fill="both", expand=True, padx=20, pady=20)
        
        # We'll update this canvas with the same 3D drawing code
        self.update_large_preview()
        
        # Instructions
        instructions = ctk.CTkLabel(
            preview_container,
            text="🖱️ Drag to rotate • Scroll to zoom • Double-click to reset",
            font=CTkFont(size=11),
            text_color=("#666666", "#aaaaaa")
        )
        instructions.pack(pady=(10, 0))
    
    def run(self):
        """Run the application"""
        # Set up cleanup on window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Handle window closing"""
        # Destroy hidden CrateApp window
        if hasattr(self, 'hidden_root'):
            self.hidden_root.destroy()
        # Destroy main window
        self.root.destroy()

def main():
    """Main entry point"""
    app = UltraModernAutocrateGUI()
    app.run()

if __name__ == "__main__":
    main()