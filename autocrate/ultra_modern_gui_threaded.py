"""
Ultra Modern AutoCrate GUI - Threaded Version
Features:
- Non-blocking test execution
- Automatic progress logging
- Responsive UI during operations
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
import threading
from datetime import datetime
import os
import sys
from pathlib import Path

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Add parent directory to path for imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(current_dir))

# Import the main application
try:
    from nx_expressions_generator import AutocrateMasterApp
    HAS_GENERATOR = True
except ImportError:
    HAS_GENERATOR = False

try:
    import quick_test
except ImportError:
    quick_test = None

class ProgressLogger:
    """Automatic progress logging to file"""
    def __init__(self, log_file="progress_log.txt"):
        self.log_file = log_file
        self.ensure_log_exists()
    
    def ensure_log_exists(self):
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f:
                f.write("AutoCrate Progress Log\n")
                f.write("======================\n\n")
    
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, 'a') as f:
            f.write(f"[{timestamp}] [{level}] {message}\n")
    
    def log_task_start(self, task):
        self.log(f"Starting: {task}", "TASK")
    
    def log_task_complete(self, task):
        self.log(f"Completed: {task}", "SUCCESS")
    
    def log_error(self, error):
        self.log(f"Error: {error}", "ERROR")

class UltraModernAutocrateGUI:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("AutoCrate V12 - Ultra Modern Interface (Threaded)")
        self.root.geometry("1400x900")
        
        # Initialize logger
        self.logger = ProgressLogger()
        self.logger.log("Application started", "SYSTEM")
        
        # Track running threads
        self.test_thread = None
        self.generate_thread = None
        
        # Legacy app integration
        self.crate_app = None
        if HAS_GENERATOR:
            try:
                # Create a hidden root for the legacy app
                self.legacy_root = tk.Tk()
                self.legacy_root.withdraw()
                self.crate_app = AutocrateMasterApp(self.legacy_root)
                self.logger.log("Legacy generator loaded successfully", "SYSTEM")
            except Exception as e:
                self.logger.log_error(f"Failed to load legacy generator: {e}")
                self.crate_app = None
        
        self.setup_ui()
        self.setup_bindings()
        
    def setup_ui(self):
        """Setup the modern UI"""
        # Main container with padding
        main_container = ctk.CTkFrame(self.root, corner_radius=0)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header_frame = ctk.CTkFrame(main_container)
        header_frame.pack(fill="x", pady=(0, 20))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="🏗️ AutoCrate V12",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title_label.pack(side="left", padx=20, pady=10)
        
        # Status indicator
        self.status_label = ctk.CTkLabel(
            header_frame,
            text="✅ Ready",
            font=ctk.CTkFont(size=14)
        )
        self.status_label.pack(side="right", padx=20, pady=10)
        
        # Main content area with tabs
        self.tab_view = ctk.CTkTabview(main_container)
        self.tab_view.pack(fill="both", expand=True)
        
        # Create tabs
        self.tab_view.add("📦 Product")
        self.tab_view.add("🔧 Materials")
        self.tab_view.add("⚙️ Settings")
        self.tab_view.add("📊 Output")
        
        # Setup each tab
        self.setup_product_tab()
        self.setup_materials_tab()
        self.setup_settings_tab()
        self.setup_output_tab()
        
        # Bottom control panel
        control_frame = ctk.CTkFrame(main_container)
        control_frame.pack(fill="x", pady=(20, 0))
        
        # Action buttons
        self.generate_btn = ctk.CTkButton(
            control_frame,
            text="🚀 Generate Expression",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            command=self.generate_expression_threaded
        )
        self.generate_btn.pack(side="left", padx=10, pady=10)
        
        self.test_btn = ctk.CTkButton(
            control_frame,
            text="🧪 Run Tests",
            font=ctk.CTkFont(size=16),
            height=50,
            command=self.run_quick_test_threaded
        )
        self.test_btn.pack(side="left", padx=10, pady=10)
        
        # Progress bar
        self.progress = ctk.CTkProgressBar(control_frame)
        self.progress.pack(side="left", fill="x", expand=True, padx=20, pady=10)
        self.progress.set(0)
        
        # Progress text
        self.progress_text = ctk.CTkLabel(
            control_frame,
            text="",
            font=ctk.CTkFont(size=12)
        )
        self.progress_text.pack(side="left", padx=10)
        
    def setup_product_tab(self):
        """Setup product input tab"""
        tab = self.tab_view.tab("📦 Product")
        
        # Create scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(tab)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Product dimensions
        dim_frame = ctk.CTkFrame(scroll_frame)
        dim_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(dim_frame, text="Product Dimensions", 
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=5)
        
        fields = [
            ("Length (inches):", "product_length", "96"),
            ("Width (inches):", "product_width", "100"),
            ("Height (inches):", "product_height", "30"),
            ("Weight (lbs):", "product_weight", "8000"),
        ]
        
        for label, attr, default in fields:
            row = ctk.CTkFrame(dim_frame)
            row.pack(fill="x", pady=5)
            ctk.CTkLabel(row, text=label, width=150).pack(side="left", padx=10)
            entry = ctk.CTkEntry(row, width=200)
            entry.insert(0, default)
            entry.pack(side="left", padx=10)
            setattr(self, f"{attr}_entry", entry)
        
        # Clearances
        clear_frame = ctk.CTkFrame(scroll_frame)
        clear_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(clear_frame, text="Clearances", 
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=5)
        
        clearances = [
            ("Side Clearance:", "clearance", "5.0"),
            ("Above Clearance:", "clearance_above", "5.0"),
            ("Ground Clearance:", "ground_clearance", "6.0"),
        ]
        
        for label, attr, default in clearances:
            row = ctk.CTkFrame(clear_frame)
            row.pack(fill="x", pady=5)
            ctk.CTkLabel(row, text=label, width=150).pack(side="left", padx=10)
            entry = ctk.CTkEntry(row, width=200)
            entry.insert(0, default)
            entry.pack(side="left", padx=10)
            setattr(self, f"{attr}_entry", entry)
    
    def setup_materials_tab(self):
        """Setup materials tab"""
        tab = self.tab_view.tab("🔧 Materials")
        
        scroll_frame = ctk.CTkScrollableFrame(tab)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Panel materials
        panel_frame = ctk.CTkFrame(scroll_frame)
        panel_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(panel_frame, text="Panel Materials",
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=5)
        
        materials = [
            ("Panel Thickness:", "panel_thickness", "0.25"),
            ("Cleat Thickness:", "cleat_thickness", "1.5"),
            ("Cleat Width:", "cleat_member_width", "3.5"),
        ]
        
        for label, attr, default in materials:
            row = ctk.CTkFrame(panel_frame)
            row.pack(fill="x", pady=5)
            ctk.CTkLabel(row, text=label, width=150).pack(side="left", padx=10)
            entry = ctk.CTkEntry(row, width=200)
            entry.insert(0, default)
            entry.pack(side="left", padx=10)
            setattr(self, f"{attr}_entry", entry)
    
    def setup_settings_tab(self):
        """Setup settings tab"""
        tab = self.tab_view.tab("⚙️ Settings")
        
        scroll_frame = ctk.CTkScrollableFrame(tab)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Floorboard settings
        floor_frame = ctk.CTkFrame(scroll_frame)
        floor_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(floor_frame, text="Floorboard Settings",
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=5)
        
        settings = [
            ("Floorboard Thickness:", "floorboard_thickness", "1.5"),
            ("Max Gap:", "max_gap", "1.0"),
            ("Min Custom Width:", "min_custom", "2.0"),
        ]
        
        for label, attr, default in settings:
            row = ctk.CTkFrame(floor_frame)
            row.pack(fill="x", pady=5)
            ctk.CTkLabel(row, text=label, width=150).pack(side="left", padx=10)
            entry = ctk.CTkEntry(row, width=200)
            entry.insert(0, default)
            entry.pack(side="left", padx=10)
            setattr(self, f"{attr}_entry", entry)
        
        # Lumber options
        self.lumber_vars = {}
        lumber_frame = ctk.CTkFrame(scroll_frame)
        lumber_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(lumber_frame, text="Available Lumber Widths",
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=5)
        
        lumber_sizes = ["11.25", "9.25", "7.25", "5.5", "3.5", "1.5"]
        for size in lumber_sizes:
            var = tk.BooleanVar(value=True)
            self.lumber_vars[size] = var
            ctk.CTkCheckBox(lumber_frame, text=f"{size}″", 
                          variable=var).pack(anchor="w", padx=20, pady=2)
    
    def setup_output_tab(self):
        """Setup output tab"""
        tab = self.tab_view.tab("📊 Output")
        
        # Output text area
        self.output_text = ctk.CTkTextbox(tab, font=ctk.CTkFont(family="Consolas", size=12))
        self.output_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Button frame
        btn_frame = ctk.CTkFrame(tab)
        btn_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkButton(btn_frame, text="📋 Clear Output",
                     command=self.clear_output).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="💾 Save Output",
                     command=self.save_output).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="📂 Open Log File",
                     command=self.open_log_file).pack(side="left", padx=5)
    
    def setup_bindings(self):
        """Setup keyboard bindings"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.bind("<Control-g>", lambda e: self.generate_expression_threaded())
        self.root.bind("<Control-t>", lambda e: self.run_quick_test_threaded())
        self.root.bind("<F5>", lambda e: self.run_quick_test_threaded())
    
    def update_progress(self, value, text=""):
        """Thread-safe progress update"""
        self.root.after(0, lambda: self.progress.set(value))
        if text:
            self.root.after(0, lambda: self.progress_text.configure(text=text))
            self.logger.log(text)
    
    def update_status(self, text, color="white"):
        """Thread-safe status update"""
        self.root.after(0, lambda: self.status_label.configure(text=text))
        self.logger.log(f"Status: {text}")
    
    def log_message(self, message):
        """Thread-safe output logging"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] {message}\n"
        self.root.after(0, lambda: self.output_text.insert("end", formatted_msg))
        self.root.after(0, lambda: self.output_text.see("end"))
        self.logger.log(message)
    
    def generate_expression_threaded(self):
        """Generate expression in background thread"""
        if self.generate_thread and self.generate_thread.is_alive():
            messagebox.showwarning("In Progress", "Generation already in progress!")
            return
        
        self.generate_thread = threading.Thread(target=self.generate_expression_worker)
        self.generate_thread.daemon = True
        self.generate_thread.start()
    
    def generate_expression_worker(self):
        """Worker thread for expression generation"""
        try:
            self.update_status("🔄 Generating expression...")
            self.update_progress(0, "Starting generation...")
            self.logger.log_task_start("Expression Generation")
            
            # Disable buttons
            self.root.after(0, lambda: self.generate_btn.configure(state="disabled"))
            self.root.after(0, lambda: self.test_btn.configure(state="disabled"))
            
            if not self.crate_app:
                self.log_message("ERROR: Generator not available")
                self.update_status("❌ Generation failed")
                return
            
            # Copy input values to legacy app
            self.update_progress(0.2, "Reading inputs...")
            self.sync_inputs_to_legacy()
            
            # Generate expression
            self.update_progress(0.5, "Calculating dimensions...")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Get parameters
            length = float(self.product_length_entry.get())
            width = float(self.product_width_entry.get())
            height = float(self.product_height_entry.get())
            weight = float(self.product_weight_entry.get())
            clearance = float(self.clearance_entry.get())
            panel_thickness = float(self.panel_thickness_entry.get())
            
            filename = (f"expressions/{timestamp}_Crate_"
                       f"{length:.0f}x{width:.0f}x{height:.0f}_"
                       f"W{weight:.0f}_5P_"
                       f"{'PLY' if panel_thickness >= 0.5 else 'OSB'}{panel_thickness}_"
                       f"C{clearance}_ASTM.exp")
            
            self.update_progress(0.7, "Generating NX expressions...")
            
            # Call the legacy generate method
            self.crate_app.generate_expression_file()
            
            self.update_progress(1.0, "Complete!")
            self.log_message(f"✅ Expression generated: {filename}")
            self.update_status("✅ Generation complete")
            self.logger.log_task_complete("Expression Generation")
            
            # Show success message
            self.root.after(0, lambda: messagebox.showinfo("Success", 
                f"Expression file generated:\n{filename}"))
            
        except Exception as e:
            self.log_message(f"❌ Generation failed: {str(e)}")
            self.update_status("❌ Generation failed")
            self.logger.log_error(str(e))
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            # Re-enable buttons
            self.root.after(0, lambda: self.generate_btn.configure(state="normal"))
            self.root.after(0, lambda: self.test_btn.configure(state="normal"))
            self.update_progress(0, "")
    
    def run_quick_test_threaded(self):
        """Run tests in background thread"""
        if self.test_thread and self.test_thread.is_alive():
            messagebox.showwarning("In Progress", "Tests already running!")
            return
        
        self.test_thread = threading.Thread(target=self.run_quick_test_worker)
        self.test_thread.daemon = True
        self.test_thread.start()
    
    def run_quick_test_worker(self):
        """Worker thread for test execution"""
        try:
            self.update_status("🧪 Running tests...")
            self.update_progress(0, "Initializing test suite...")
            self.logger.log_task_start("Quick Test Suite")
            
            # Disable buttons
            self.root.after(0, lambda: self.generate_btn.configure(state="disabled"))
            self.root.after(0, lambda: self.test_btn.configure(state="disabled"))
            
            if not self.crate_app:
                self.log_message("ERROR: Test suite not available")
                self.update_status("❌ Tests failed")
                return
            
            # Test cases
            test_cases = [
                (1000, 20, 20, 100, 1.0, "Very Tall Thin"),
                (500, 96, 48, 30, 2.0, "Standard Plywood Size"),
                (2000, 120, 120, 48, 1.5, "Large Square Heavy"),
                (100, 12, 12, 24, 0.5, "Very Small Light"),
                (5000, 130, 120, 60, 3.0, "Very Large Heavy"),
                (800, 30, 30, 80, 1.0, "Medium Square Tall"),
                (1500, 100, 50, 40, 2.5, "Long Narrow"),
                (300, 48, 48, 48, 1.0, "Perfect Cube"),
                (10000, 130, 130, 72, 4.0, "Maximum Size Heavy"),
                (50, 12, 12, 12, 0.25, "Minimum Size Light"),
            ]
            
            total_tests = len(test_cases)
            passed_tests = 0
            failed_tests = 0
            
            for i, (weight, length, width, height, clearance, desc) in enumerate(test_cases, 1):
                progress = i / total_tests
                self.update_progress(progress, f"Test {i}/{total_tests}: {desc}")
                self.log_message(f"Running test {i}/{total_tests}: {desc}")
                
                try:
                    # Set inputs
                    self.crate_app.product_weight_entry.delete(0, tk.END)
                    self.crate_app.product_weight_entry.insert(0, str(weight))
                    self.crate_app.product_length_entry.delete(0, tk.END)
                    self.crate_app.product_length_entry.insert(0, str(length))
                    self.crate_app.product_width_entry.delete(0, tk.END)
                    self.crate_app.product_width_entry.insert(0, str(width))
                    self.crate_app.product_height_entry.delete(0, tk.END)
                    self.crate_app.product_height_entry.insert(0, str(height))
                    self.crate_app.clearance_entry.delete(0, tk.END)
                    self.crate_app.clearance_entry.insert(0, str(clearance))
                    
                    # Generate
                    self.crate_app.generate_expression_file()
                    
                    passed_tests += 1
                    self.log_message(f"  ✅ Test {i} passed")
                    
                except Exception as e:
                    failed_tests += 1
                    self.log_message(f"  ❌ Test {i} failed: {str(e)}")
                    self.logger.log_error(f"Test {i} failed: {str(e)}")
            
            # Final results
            self.update_progress(1.0, "Tests complete!")
            result_msg = f"Test Results: {passed_tests}/{total_tests} passed, {failed_tests} failed"
            self.log_message(f"\n{result_msg}")
            self.update_status(f"✅ {result_msg}")
            self.logger.log_task_complete(f"Quick Test Suite: {result_msg}")
            
            # Show results
            if failed_tests == 0:
                self.root.after(0, lambda: messagebox.showinfo("Success", 
                    f"All {total_tests} tests passed!"))
            else:
                self.root.after(0, lambda: messagebox.showwarning("Tests Complete", 
                    result_msg))
            
        except Exception as e:
            self.log_message(f"❌ Test suite failed: {str(e)}")
            self.update_status("❌ Tests failed")
            self.logger.log_error(str(e))
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            # Re-enable buttons
            self.root.after(0, lambda: self.generate_btn.configure(state="normal"))
            self.root.after(0, lambda: self.test_btn.configure(state="normal"))
            self.update_progress(0, "")
    
    def sync_inputs_to_legacy(self):
        """Sync modern UI inputs to legacy app"""
        if not self.crate_app:
            return
        
        # Product dimensions
        self.crate_app.product_length_entry.delete(0, tk.END)
        self.crate_app.product_length_entry.insert(0, self.product_length_entry.get())
        self.crate_app.product_width_entry.delete(0, tk.END)
        self.crate_app.product_width_entry.insert(0, self.product_width_entry.get())
        self.crate_app.product_height_entry.delete(0, tk.END)
        self.crate_app.product_height_entry.insert(0, self.product_height_entry.get())
        self.crate_app.product_weight_entry.delete(0, tk.END)
        self.crate_app.product_weight_entry.insert(0, self.product_weight_entry.get())
        
        # Clearances
        self.crate_app.clearance_entry.delete(0, tk.END)
        self.crate_app.clearance_entry.insert(0, self.clearance_entry.get())
        self.crate_app.clearance_above_entry.delete(0, tk.END)
        self.crate_app.clearance_above_entry.insert(0, self.clearance_above_entry.get())
        self.crate_app.ground_clearance_entry.delete(0, tk.END)
        self.crate_app.ground_clearance_entry.insert(0, self.ground_clearance_entry.get())
        
        # Materials
        self.crate_app.panel_thickness_entry.delete(0, tk.END)
        self.crate_app.panel_thickness_entry.insert(0, self.panel_thickness_entry.get())
        self.crate_app.cleat_thickness_entry.delete(0, tk.END)
        self.crate_app.cleat_thickness_entry.insert(0, self.cleat_thickness_entry.get())
        self.crate_app.cleat_member_width_entry.delete(0, tk.END)
        self.crate_app.cleat_member_width_entry.insert(0, self.cleat_member_width_entry.get())
        
        # Floorboard settings
        self.crate_app.floorboard_thickness_entry.delete(0, tk.END)
        self.crate_app.floorboard_thickness_entry.insert(0, self.floorboard_thickness_entry.get())
        self.crate_app.max_gap_entry.delete(0, tk.END)
        self.crate_app.max_gap_entry.insert(0, self.max_gap_entry.get())
        self.crate_app.min_custom_entry.delete(0, tk.END)
        self.crate_app.min_custom_entry.insert(0, self.min_custom_entry.get())
        
        # Lumber options
        for width, var in self.lumber_vars.items():
            if width in self.crate_app.lumber_vars:
                self.crate_app.lumber_vars[width].set(var.get())
    
    def clear_output(self):
        """Clear output text"""
        self.output_text.delete("1.0", "end")
        self.log_message("Output cleared")
    
    def save_output(self):
        """Save output to file"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            with open(file_path, 'w') as f:
                f.write(self.output_text.get("1.0", "end"))
            messagebox.showinfo("Saved", f"Output saved to {file_path}")
            self.logger.log(f"Output saved to {file_path}")
    
    def open_log_file(self):
        """Open the progress log file"""
        log_path = os.path.abspath(self.logger.log_file)
        if sys.platform == "win32":
            os.startfile(log_path)
        else:
            os.system(f"open '{log_path}'")
    
    def on_closing(self):
        """Clean shutdown"""
        self.logger.log("Application closing", "SYSTEM")
        
        # Wait for threads to complete
        if self.test_thread and self.test_thread.is_alive():
            self.test_thread.join(timeout=1.0)
        if self.generate_thread and self.generate_thread.is_alive():
            self.generate_thread.join(timeout=1.0)
        
        # Clean up legacy app
        if hasattr(self, 'legacy_root'):
            self.legacy_root.destroy()
        
        self.root.destroy()
    
    def run(self):
        """Run the application"""
        self.root.mainloop()

def main():
    """Main entry point"""
    app = UltraModernAutocrateGUI()
    app.run()

if __name__ == "__main__":
    main()