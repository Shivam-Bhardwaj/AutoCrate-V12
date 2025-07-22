"""
Main GUI application for AutoCrate.

This module contains the primary tkinter application interface,
providing a clean separation between UI and business logic.
"""

import sys
import os
import traceback
from pathlib import Path
from typing import Optional, Dict, Any

# Add the root directory to path for importing original modules during transition
root_dir = Path(__file__).parent.parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
except ImportError as e:
    print(f"Error importing tkinter: {e}")
    print("Please ensure tkinter is installed (usually included with Python)")
    sys.exit(1)

from ..config.settings import Settings
from ..config.materials import MaterialConfig
from ..utils.logging import get_logger, LoggingContextManager
from ..exceptions import AutoCrateError, ValidationError, CalculationError


class AutoCrateApp:
    """Main AutoCrate application window."""
    
    def __init__(self):
        """Initialize the AutoCrate application."""
        self.root = None
        self.settings = None
        self.materials = None
        self.logger = None
        self.status_var = None
        self.current_calculation = None
        
        self._initialize_components()
        self._create_gui()
        self._setup_event_handlers()
        self._load_initial_state()
    
    def _initialize_components(self):
        """Initialize core application components."""
        try:
            # Initialize logging first
            self.logger = get_logger(log_level="INFO")
            self.logger.info("Initializing AutoCrate application")
            
            # Initialize configuration
            self.settings = Settings()
            self.materials = MaterialConfig()
            
            self.logger.info("Application components initialized successfully")
            
        except Exception as e:
            print(f"Failed to initialize application components: {e}")
            traceback.print_exc()
            sys.exit(1)
    
    def _create_gui(self):
        """Create the main GUI interface."""
        # Create main window
        self.root = tk.Tk()
        self.root.title("AutoCrate v12.0.2 - Professional Edition")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Set window icon if available
        try:
            # Look for icon in the application directory
            icon_path = Path(__file__).parent.parent.parent.parent / "autocrate_icon.ico"
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except Exception:
            pass  # Icon not critical
        
        # Configure style
        self._configure_style()
        
        # Create menu bar
        self._create_menu_bar()
        
        # Create main content area
        self._create_main_content()
        
        # Create status bar
        self._create_status_bar()
        
        self.logger.info("GUI interface created successfully")
    
    def _configure_style(self):
        """Configure the application visual style."""
        style = ttk.Style()
        
        # Try to use a modern theme
        available_themes = style.theme_names()
        preferred_themes = ['vista', 'winnative', 'clam', 'alt']
        
        for theme in preferred_themes:
            if theme in available_themes:
                style.theme_use(theme)
                break
        
        # Configure custom styles
        style.configure('Title.TLabel', font=('Segoe UI', 12, 'bold'))
        style.configure('Heading.TLabel', font=('Segoe UI', 10, 'bold'))
        style.configure('Status.TLabel', font=('Segoe UI', 8))
    
    def _create_menu_bar(self):
        """Create the application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", accelerator="Ctrl+N", command=self._new_calculation)
        file_menu.add_command(label="Open...", accelerator="Ctrl+O", command=self._open_file)
        file_menu.add_separator()
        file_menu.add_command(label="Save", accelerator="Ctrl+S", command=self._save_file)
        file_menu.add_command(label="Save As...", accelerator="Ctrl+Shift+S", command=self._save_as_file)
        file_menu.add_separator()
        
        # Recent files submenu
        self.recent_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Recent Files", menu=self.recent_menu)
        self._update_recent_files_menu()
        
        file_menu.add_separator()
        file_menu.add_command(label="Exit", accelerator="Alt+F4", command=self._exit_application)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Preferences...", command=self._show_preferences)
        edit_menu.add_command(label="Material Properties...", command=self._show_material_properties)
        
        # Calculate menu
        calc_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Calculate", menu=calc_menu)
        calc_menu.add_command(label="Generate Expressions", accelerator="F5", command=self._calculate_expressions)
        calc_menu.add_command(label="Validate Inputs", accelerator="F6", command=self._validate_inputs)
        calc_menu.add_separator()
        calc_menu.add_command(label="Clear All", command=self._clear_all_inputs)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Lumber Calculator", command=self._show_lumber_calculator)
        tools_menu.add_command(label="Plywood Layout", command=self._show_plywood_layout)
        tools_menu.add_separator()
        tools_menu.add_command(label="Export Configuration", command=self._export_configuration)
        tools_menu.add_command(label="Import Configuration", command=self._import_configuration)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="User Manual", command=self._show_user_manual)
        help_menu.add_command(label="Keyboard Shortcuts", command=self._show_shortcuts)
        help_menu.add_separator()
        help_menu.add_command(label="View Log File", command=self._view_log_file)
        help_menu.add_command(label="About AutoCrate", command=self._show_about)
    
    def _create_main_content(self):
        """Create the main content area with input fields."""
        # Create notebook for tabbed interface
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 0))
        
        # Basic Dimensions tab
        self._create_dimensions_tab()
        
        # Advanced Settings tab
        self._create_advanced_tab()
        
        # Results tab
        self._create_results_tab()
        
        # Create control buttons
        self._create_control_buttons()
    
    def _create_dimensions_tab(self):
        """Create the basic dimensions input tab."""
        dims_frame = ttk.Frame(self.notebook)
        self.notebook.add(dims_frame, text="Basic Dimensions")
        
        # Main container with padding
        container = ttk.Frame(dims_frame)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(container, text="Crate Dimensions", style='Title.TLabel')
        title_label.pack(anchor=tk.W, pady=(0, 20))
        
        # Input fields frame
        inputs_frame = ttk.Frame(container)
        inputs_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Create input variables
        self.width_var = tk.StringVar()
        self.height_var = tk.StringVar()
        self.depth_var = tk.StringVar()
        self.clearance_var = tk.StringVar(value=str(self.settings.get('calculations.default_clearance', 2.0)))
        
        # Width input
        ttk.Label(inputs_frame, text="Width (inches):", style='Heading.TLabel').grid(row=0, column=0, sticky=tk.W, pady=5)
        width_entry = ttk.Entry(inputs_frame, textvariable=self.width_var, font=('Segoe UI', 10))
        width_entry.grid(row=0, column=1, sticky=tk.EW, padx=(10, 0), pady=5)
        
        # Height input
        ttk.Label(inputs_frame, text="Height (inches):", style='Heading.TLabel').grid(row=1, column=0, sticky=tk.W, pady=5)
        height_entry = ttk.Entry(inputs_frame, textvariable=self.height_var, font=('Segoe UI', 10))
        height_entry.grid(row=1, column=1, sticky=tk.EW, padx=(10, 0), pady=5)
        
        # Depth input
        ttk.Label(inputs_frame, text="Depth (inches):", style='Heading.TLabel').grid(row=2, column=0, sticky=tk.W, pady=5)
        depth_entry = ttk.Entry(inputs_frame, textvariable=self.depth_var, font=('Segoe UI', 10))
        depth_entry.grid(row=2, column=1, sticky=tk.EW, padx=(10, 0), pady=5)
        
        # Clearance input
        ttk.Label(inputs_frame, text="Clearance (inches):", style='Heading.TLabel').grid(row=3, column=0, sticky=tk.W, pady=5)
        clearance_entry = ttk.Entry(inputs_frame, textvariable=self.clearance_var, font=('Segoe UI', 10))
        clearance_entry.grid(row=3, column=1, sticky=tk.EW, padx=(10, 0), pady=5)
        
        # Configure grid weights
        inputs_frame.columnconfigure(1, weight=1)
        
        # Quick preset buttons
        presets_frame = ttk.LabelFrame(container, text="Quick Presets", padding=10)
        presets_frame.pack(fill=tk.X, pady=(0, 20))
        
        preset_buttons = [
            ("50x50x30", lambda: self._set_dimensions(50, 50, 30)),
            ("120x120x120", lambda: self._set_dimensions(120, 120, 120)),
            ("135x135x135", lambda: self._set_dimensions(135, 135, 135)),
            ("170x170x170", lambda: self._set_dimensions(170, 170, 170)),
        ]
        
        for i, (label, command) in enumerate(preset_buttons):
            btn = ttk.Button(presets_frame, text=label, command=command)
            btn.grid(row=0, column=i, padx=5, sticky=tk.EW)
        
        # Configure preset buttons grid
        for i in range(len(preset_buttons)):
            presets_frame.columnconfigure(i, weight=1)
    
    def _create_advanced_tab(self):
        """Create the advanced settings tab."""
        adv_frame = ttk.Frame(self.notebook)
        self.notebook.add(adv_frame, text="Advanced Settings")
        
        # Placeholder for advanced settings
        ttk.Label(adv_frame, text="Advanced settings will be implemented here", 
                 style='Title.TLabel').pack(pady=50)
    
    def _create_results_tab(self):
        """Create the results display tab."""
        results_frame = ttk.Frame(self.notebook)
        self.notebook.add(results_frame, text="Results")
        
        # Results text area
        self.results_text = tk.Text(results_frame, font=('Consolas', 9), wrap=tk.NONE)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        h_scrollbar = ttk.Scrollbar(results_frame, orient=tk.HORIZONTAL, command=self.results_text.xview)
        
        self.results_text.config(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.results_text.grid(row=0, column=0, sticky=tk.NSEW)
        v_scrollbar.grid(row=0, column=1, sticky=tk.NS)
        h_scrollbar.grid(row=1, column=0, sticky=tk.EW)
        
        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)
    
    def _create_control_buttons(self):
        """Create the main control buttons."""
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Calculate button (primary)
        self.calc_button = ttk.Button(
            button_frame, 
            text="Generate NX Expressions", 
            command=self._calculate_expressions,
            style='Accent.TButton'
        )
        self.calc_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Validate button
        validate_button = ttk.Button(
            button_frame, 
            text="Validate Inputs", 
            command=self._validate_inputs
        )
        validate_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Clear button
        clear_button = ttk.Button(
            button_frame, 
            text="Clear All", 
            command=self._clear_all_inputs
        )
        clear_button.pack(side=tk.LEFT)
    
    def _create_status_bar(self):
        """Create the status bar at the bottom."""
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Status text
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, style='Status.TLabel')
        status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Progress bar (hidden by default)
        self.progress_bar = ttk.Progressbar(status_frame, mode='indeterminate')
    
    def _setup_event_handlers(self):
        """Set up keyboard shortcuts and event handlers."""
        # Bind keyboard shortcuts
        self.root.bind('<Control-n>', lambda e: self._new_calculation())
        self.root.bind('<Control-o>', lambda e: self._open_file())
        self.root.bind('<Control-s>', lambda e: self._save_file())
        self.root.bind('<Control-S>', lambda e: self._save_as_file())
        self.root.bind('<F5>', lambda e: self._calculate_expressions())
        self.root.bind('<F6>', lambda e: self._validate_inputs())
        
        # Window close event
        self.root.protocol("WM_DELETE_WINDOW", self._exit_application)
    
    def _load_initial_state(self):
        """Load initial application state from settings."""
        # Restore window size and position
        width = self.settings.get('ui.window_width', 1000)
        height = self.settings.get('ui.window_height', 700)
        self.root.geometry(f"{width}x{height}")
        
        if self.settings.get('ui.window_maximized', False):
            self.root.state('zoomed')
        
        self.logger.info("Initial application state loaded")
    
    def _set_dimensions(self, width: float, height: float, depth: float):
        """Set dimension input fields."""
        self.width_var.set(str(width))
        self.height_var.set(str(height))
        self.depth_var.set(str(depth))
        
        self.logger.log_user_action("preset_dimensions", {
            'width': width, 'height': height, 'depth': depth
        })
    
    def _update_status(self, message: str):
        """Update the status bar message."""
        if self.status_var:
            self.status_var.set(message)
        self.root.update_idletasks()
    
    def _show_progress(self, show: bool = True):
        """Show or hide the progress bar."""
        if show:
            self.progress_bar.pack(side=tk.RIGHT, padx=10, pady=2)
            self.progress_bar.start()
        else:
            self.progress_bar.stop()
            self.progress_bar.pack_forget()
    
    # Menu command implementations (stubs for now)
    def _new_calculation(self):
        """Create a new calculation."""
        self._clear_all_inputs()
        self.logger.log_user_action("new_calculation")
    
    def _open_file(self):
        """Open a saved calculation file."""
        filename = filedialog.askopenfilename(
            title="Open Calculation",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.logger.log_user_action("open_file", {'filename': filename})
    
    def _save_file(self):
        """Save current calculation."""
        self.logger.log_user_action("save_file")
    
    def _save_as_file(self):
        """Save calculation with new filename."""
        filename = filedialog.asksaveasfilename(
            title="Save Calculation As",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.logger.log_user_action("save_as_file", {'filename': filename})
    
    def _update_recent_files_menu(self):
        """Update the recent files menu."""
        # Clear existing menu items
        self.recent_menu.delete(0, tk.END)
        
        recent_files = self.settings.get_recent_files()
        if recent_files:
            for filepath in recent_files:
                filename = os.path.basename(filepath)
                self.recent_menu.add_command(
                    label=filename,
                    command=lambda f=filepath: self._open_recent_file(f)
                )
        else:
            self.recent_menu.add_command(label="(No recent files)", state=tk.DISABLED)
    
    def _open_recent_file(self, filepath: str):
        """Open a recent file."""
        self.logger.log_user_action("open_recent_file", {'filepath': filepath})
    
    def _validate_inputs(self):
        """Validate input fields."""
        try:
            self._update_status("Validating inputs...")
            
            # Get values
            width = float(self.width_var.get() or 0)
            height = float(self.height_var.get() or 0)
            depth = float(self.depth_var.get() or 0)
            clearance = float(self.clearance_var.get() or 0)
            
            # Validate
            if width <= 0 or height <= 0 or depth <= 0:
                raise ValidationError("All dimensions must be positive numbers")
            
            if clearance < 0:
                raise ValidationError("Clearance cannot be negative")
            
            self._update_status("Input validation successful")
            messagebox.showinfo("Validation", "All inputs are valid!")
            
        except ValueError as e:
            messagebox.showerror("Validation Error", "Please enter valid numbers for all dimensions")
        except ValidationError as e:
            messagebox.showerror("Validation Error", str(e))
        except Exception as e:
            self.logger.error("Unexpected error during validation", exception=e)
            messagebox.showerror("Error", f"Validation failed: {str(e)}")
    
    def _calculate_expressions(self):
        """Generate NX expressions from current inputs."""
        try:
            with LoggingContextManager("expression_calculation", self.logger):
                self._update_status("Calculating expressions...")
                self._show_progress(True)
                
                # For now, just show a placeholder
                self.results_text.delete(1.0, tk.END)
                self.results_text.insert(tk.END, "// AutoCrate NX Expressions\\n")
                self.results_text.insert(tk.END, f"// Generated: {self.logger.logger.handlers[0].formatter.formatTime(self.logger.logger.makeRecord('', 0, '', 0, '', (), None))}\\n")
                self.results_text.insert(tk.END, "// This is a placeholder - full calculation logic will be implemented\\n")
                
                # Switch to results tab
                self.notebook.select(2)
                
                self._update_status("Expression calculation complete")
                
        except Exception as e:
            self.logger.error("Expression calculation failed", exception=e)
            messagebox.showerror("Calculation Error", f"Failed to calculate expressions: {str(e)}")
        finally:
            self._show_progress(False)
    
    def _clear_all_inputs(self):
        """Clear all input fields."""
        self.width_var.set("")
        self.height_var.set("")
        self.depth_var.set("")
        self.clearance_var.set(str(self.settings.get('calculations.default_clearance', 2.0)))
        self.results_text.delete(1.0, tk.END)
        self._update_status("Inputs cleared")
    
    def _show_preferences(self):
        """Show preferences dialog."""
        messagebox.showinfo("Preferences", "Preferences dialog will be implemented")
    
    def _show_material_properties(self):
        """Show material properties dialog."""
        messagebox.showinfo("Material Properties", "Material properties dialog will be implemented")
    
    def _show_lumber_calculator(self):
        """Show lumber calculator tool.""" 
        messagebox.showinfo("Lumber Calculator", "Lumber calculator will be implemented")
    
    def _show_plywood_layout(self):
        """Show plywood layout tool."""
        messagebox.showinfo("Plywood Layout", "Plywood layout tool will be implemented")
    
    def _export_configuration(self):
        """Export configuration."""
        filename = filedialog.asksaveasfilename(
            title="Export Configuration",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        if filename:
            try:
                self.settings.export_settings(filename)
                messagebox.showinfo("Export", "Configuration exported successfully")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export: {str(e)}")
    
    def _import_configuration(self):
        """Import configuration."""
        filename = filedialog.askopenfilename(
            title="Import Configuration",
            filetypes=[("JSON files", "*.json")]
        )
        if filename:
            try:
                self.settings.import_settings(filename)
                messagebox.showinfo("Import", "Configuration imported successfully")
            except Exception as e:
                messagebox.showerror("Import Error", f"Failed to import: {str(e)}")
    
    def _show_user_manual(self):
        """Show user manual."""
        messagebox.showinfo("User Manual", "User manual will be available in the final release")
    
    def _show_shortcuts(self):
        """Show keyboard shortcuts."""
        shortcuts = """
Keyboard Shortcuts:

Ctrl+N - New calculation
Ctrl+O - Open file
Ctrl+S - Save file
Ctrl+Shift+S - Save as
F5 - Generate expressions
F6 - Validate inputs
Alt+F4 - Exit application
"""
        messagebox.showinfo("Keyboard Shortcuts", shortcuts)
    
    def _view_log_file(self):
        """Open log file in default editor."""
        log_path = self.logger.get_log_file_path()
        try:
            if os.name == 'nt':  # Windows
                os.startfile(log_path)
            else:  # Unix-like
                os.system(f"open '{log_path}'")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open log file: {str(e)}")
    
    def _show_about(self):
        """Show about dialog."""
        about_text = """
AutoCrate v12.0.2 - Professional Edition

Automated CAD Design Tool for Custom Shipping Crates

A sophisticated CAD automation tool that generates parametric 
design data for Siemens NX CAD software, enabling automated 
creation of detailed 3D models and technical drawings.

© 2024 AutoCrate Development Team
All rights reserved.
"""
        messagebox.showinfo("About AutoCrate", about_text)
    
    def _exit_application(self):
        """Exit the application."""
        try:
            # Save current window state
            if self.root.state() == 'zoomed':
                self.settings.set('ui.window_maximized', True)
            else:
                self.settings.set('ui.window_maximized', False)
                self.settings.set('ui.window_width', self.root.winfo_width())
                self.settings.set('ui.window_height', self.root.winfo_height())
            
            # Save settings
            self.settings.save()
            
            self.logger.info("Application closing normally")
            self.root.destroy()
            
        except Exception as e:
            self.logger.error("Error during application shutdown", exception=e)
            self.root.destroy()
    
    def run(self):
        """Start the application main loop."""
        try:
            self.logger.info("Starting AutoCrate application")
            self.root.mainloop()
        except Exception as e:
            self.logger.critical("Critical error in main loop", exception=e)
            messagebox.showerror("Critical Error", f"Application encountered a critical error: {str(e)}")
        finally:
            self.logger.info("Application terminated")


def main():
    """Entry point for the AutoCrate application."""
    try:
        app = AutoCrateApp()
        app.run()
    except Exception as e:
        print(f"Failed to start AutoCrate: {e}")
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())