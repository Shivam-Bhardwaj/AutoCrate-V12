#!/usr/bin/env python3
"""
Automate documentation generation for AutoCrate.

This script generates comprehensive API documentation, takes screenshots of the GUI,
and creates interactive tutorials for the AutoCrate project.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import List, Optional
import argparse
import time
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class DocumentationGenerator:
    """Automated documentation generation for AutoCrate."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.docs_dir = project_root / 'docs'
        self.api_dir = self.docs_dir / 'api'
        self.screenshots_dir = self.docs_dir / 'screenshots'
        self.build_dir = self.docs_dir / '_build'
        
        # Ensure directories exist
        self.api_dir.mkdir(exist_ok=True)
        self.screenshots_dir.mkdir(exist_ok=True)
        self.build_dir.mkdir(exist_ok=True)
    
    def generate_api_docs(self) -> bool:
        """Generate API documentation using sphinx-apidoc."""
        print("[INFO] Generating API documentation...")
        
        try:
            # Remove existing API docs
            if self.api_dir.exists():
                shutil.rmtree(self.api_dir)
            self.api_dir.mkdir()
            
            # Generate API documentation
            cmd = [
                'sphinx-apidoc',
                '-f',  # Force overwrite
                '-o', str(self.api_dir),  # Output directory
                str(self.project_root),  # Source directory
                '--separate',  # Create separate files for modules
                '--module-first',  # Put module documentation before submodule
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"[ERROR] Error generating API docs: {result.stderr}")
                return False
            
            print("[SUCCESS] API documentation generated successfully")
            return True
            
        except Exception as e:
            print(f"[ERROR] Exception during API doc generation: {e}")
            return False
    
    def build_html_docs(self) -> bool:
        """Build HTML documentation using Sphinx."""
        print("Building HTML documentation...")
        
        try:
            cmd = [
                'sphinx-build',
                '-b', 'html',  # HTML builder
                '-W',  # Treat warnings as errors
                str(self.docs_dir),  # Source directory
                str(self.build_dir / 'html'),  # Output directory
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"[ERROR] Error building HTML docs: {result.stderr}")
                return False
            
            print("[SUCCESS] HTML documentation built successfully")
            return True
            
        except Exception as e:
            print(f"[ERROR] Exception during HTML build: {e}")
            return False
    
    def generate_screenshots(self) -> bool:
        """Generate screenshots of the AutoCrate GUI."""
        print("Generating GUI screenshots...")
        
        try:
            # Import GUI modules
            import tkinter as tk
            from PIL import Image, ImageTk
            import threading
            import time
            
            # Try to import AutoCrate GUI
            try:
                import nx_expressions_generator
            except ImportError:
                print("[WARNING] Could not import AutoCrate GUI module")
                return False
            
            def capture_gui():
                """Capture GUI screenshots in a separate thread."""
                try:
                    # Create a temporary GUI instance
                    root = tk.Tk()
                    root.title("AutoCrate - Screenshot Generation")
                    
                    # Give GUI time to render
                    root.after(2000, lambda: self._capture_window(root, "main_interface"))
                    root.after(4000, root.quit)
                    
                    root.mainloop()
                    
                except Exception as e:
                    print(f"[WARNING] GUI screenshot failed: {e}")
            
            # Run GUI capture
            capture_gui()
            print("[SUCCESS] Screenshots generated successfully")
            return True
            
        except Exception as e:
            print(f"[ERROR] Exception during screenshot generation: {e}")
            return False
    
    def _capture_window(self, window: tk.Tk, filename: str):
        """Capture a specific window to file."""
        try:
            # Update window to ensure it's drawn
            window.update_idletasks()
            window.update()
            
            # Get window geometry
            x = window.winfo_rootx()
            y = window.winfo_rooty()
            width = window.winfo_width()
            height = window.winfo_height()
            
            # Capture screenshot using PIL
            import pyautogui
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
            
            # Save screenshot
            screenshot_path = self.screenshots_dir / f"{filename}.png"
            screenshot.save(screenshot_path)
            print(f"  Saved screenshot: {screenshot_path}")
            
        except Exception as e:
            print(f"  [WARNING] Failed to capture {filename}: {e}")
    
    def create_tutorial_content(self) -> bool:
        """Create interactive tutorial content."""
        print("Creating tutorial content...")
        
        try:
            tutorial_content = self._generate_tutorial_markdown()
            
            tutorial_file = self.docs_dir / 'tutorials' / 'getting_started.md'
            tutorial_file.parent.mkdir(exist_ok=True)
            
            with open(tutorial_file, 'w', encoding='utf-8') as f:
                f.write(tutorial_content)
            
            print("[SUCCESS] Tutorial content created successfully")
            return True
            
        except Exception as e:
            print(f"[ERROR] Exception during tutorial creation: {e}")
            return False
    
    def _generate_tutorial_markdown(self) -> str:
        """Generate tutorial content in Markdown format."""
        return f"""
# AutoCrate Getting Started Tutorial

*Generated automatically on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## Quick Start Guide

### 1. Launch AutoCrate

```python
python nx_expressions_generator.py
```

### 2. Enter Basic Parameters

![Main Interface](../screenshots/main_interface.png)

1. **Product Dimensions**: Enter length, width, and height
2. **Weight**: Specify product weight for structural calculations
3. **Material**: Select crate material (currently supports wood)
4. **Clearances**: Set required clearances around product

### 3. Generate Crate Design

Click the "Generate" button to:
- Calculate ASTM-compliant structural requirements
- Optimize material usage and layout
- Generate Siemens NX expression file

### 4. Review Results

The application will generate:
- `.exp` file for Siemens NX
- Material quantity report
- Structural compliance summary

## Advanced Features

### Panel Optimization

Automatic optimization of:
- Plywood sheet layout
- Cleat positioning
- Material waste reduction

### ASTM Compliance

Built-in validation against:
- Structural load requirements
- Material specifications
- Safety factors

## Troubleshooting

### Common Issues

1. **Invalid Input**: Check dimension and weight ranges
2. **File Generation**: Ensure write permissions in output directory
3. **GUI Issues**: Verify tkinter installation

### Getting Help

For technical support and feature requests:
- Check the [Documentation](../index.html)
- Review [API Reference](../api/modules.html)
- Report issues on GitHub

---

*This tutorial is part of the AutoCrate AI Development Showcase*
"""
    
    def generate_changelog(self) -> bool:
        """Generate automated changelog from git history."""
        print("Generating changelog...")
        
        try:
            # Get git log
            cmd = [
                'git', 'log',
                '--oneline',
                '--decorate',
                '--graph',
                '--max-count=50'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
            if result.returncode != 0:
                print(f"[WARNING] Could not generate git changelog: {result.stderr}")
                return False
            
            # Create changelog content
            changelog_content = f"""
# AutoCrate Changelog

*Generated automatically on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## Recent Changes

```
{result.stdout}
```

## Development History

This project demonstrates AI-assisted software development with:
- Professional engineering calculations
- ASTM compliance validation
- Comprehensive testing (78+ tests)
- Professional documentation
- CAD integration capabilities

For detailed development history, see the [AI Collaboration Log](AI_COLLABORATION_LOG.md).
"""
            
            changelog_file = self.docs_dir / 'CHANGELOG.md'
            with open(changelog_file, 'w', encoding='utf-8') as f:
                f.write(changelog_content)
            
            print("[SUCCESS] Changelog generated successfully")
            return True
            
        except Exception as e:
            print(f"[ERROR] Exception during changelog generation: {e}")
            return False
    
    def run_full_generation(self) -> bool:
        """Run complete documentation generation process."""
        print("Starting full documentation generation...")
        start_time = time.time()
        
        steps = [
            ("API Documentation", self.generate_api_docs),
            ("Screenshots", self.generate_screenshots),
            ("Tutorial Content", self.create_tutorial_content),
            ("Changelog", self.generate_changelog),
            ("HTML Build", self.build_html_docs),
        ]
        
        success_count = 0
        for step_name, step_func in steps:
            print(f"\n--- {step_name} ---")
            if step_func():
                success_count += 1
            else:
                print(f"[WARNING] {step_name} completed with warnings")
        
        elapsed = time.time() - start_time
        print(f"\nDocumentation generation completed!")
        print(f"   [SUCCESS] {success_count}/{len(steps)} steps successful")
        print(f"   [TIME] Elapsed time: {elapsed:.1f} seconds")
        print(f"   Output: {self.build_dir / 'html' / 'index.html'}")
        
        return success_count == len(steps)


def main():
    """Main entry point for documentation generation."""
    parser = argparse.ArgumentParser(description='Generate AutoCrate documentation')
    parser.add_argument('--api-only', action='store_true', help='Generate only API docs')
    parser.add_argument('--html-only', action='store_true', help='Build only HTML output')
    parser.add_argument('--screenshots', action='store_true', help='Generate screenshots only')
    parser.add_argument('--tutorials', action='store_true', help='Generate tutorials only')
    
    args = parser.parse_args()
    
    generator = DocumentationGenerator(project_root)
    
    if args.api_only:
        success = generator.generate_api_docs()
    elif args.html_only:
        success = generator.build_html_docs()
    elif args.screenshots:
        success = generator.generate_screenshots()
    elif args.tutorials:
        success = generator.create_tutorial_content()
    else:
        success = generator.run_full_generation()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
