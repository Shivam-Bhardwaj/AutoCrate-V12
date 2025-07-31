#!/usr/bin/env python3
"""
Build script for AutoCrate application.

This script handles building the AutoCrate application into a distributable
executable using PyInstaller with proper configuration and error handling.
"""

import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path
import json
from datetime import datetime


class AutoCrateBuild:
    """Handles building AutoCrate into executable."""
    
    def __init__(self, project_root: Path):
        """
        Initialize the build system.
        
        Args:
            project_root: Path to project root directory
        """
        self.project_root = project_root
        self.src_dir = project_root / "src"
        self.scripts_dir = project_root / "scripts"
        self.build_dir = project_root / "build"
        self.dist_dir = project_root / "dist"
        self.spec_file = project_root / "AutoCrate.spec"
        
        self.build_info = {
            'timestamp': datetime.now().isoformat(),
            'version': '12.0.3',
            'python_version': sys.version,
        }
    
    def clean(self):
        """Clean previous build artifacts."""
        print("Cleaning previous build artifacts...")
        
        dirs_to_clean = [self.build_dir, self.dist_dir]
        files_to_clean = [self.spec_file]
        
        for directory in dirs_to_clean:
            if directory.exists():
                print(f"  Removing {directory}")
                shutil.rmtree(directory)
        
        for file_path in files_to_clean:
            if file_path.exists():
                print(f"  Removing {file_path}")
                file_path.unlink()
        
        print("Clean completed.")
    
    def create_spec_file(self):
        """Create PyInstaller spec file with proper configuration."""
        print("Creating PyInstaller spec file...")
        
        # Use forward slashes and raw strings to avoid Unicode escape issues
        main_script = str(self.project_root / "legacy" / "nx_expressions_generator.py").replace('\\', '/')
        project_root_str = str(self.project_root).replace('\\', '/')
        legacy_dir_str = str(self.project_root / "legacy").replace('\\', '/')
        version_file_str = str(self.project_root / "version_info.txt").replace('\\', '/')
        
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# Add legacy directory to path for imports
legacy_path = r"{legacy_dir_str}"
sys.path.insert(0, legacy_path)

block_cipher = None

a = Analysis(
    [r"{main_script}"],
    pathex=[r"{project_root_str}", r"{legacy_dir_str}"],
    binaries=[],
    datas=[
        # Include legacy modules
        (r"{legacy_dir_str}", "legacy"),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.simpledialog',
        'datetime',
        'math',
        'traceback',
        'typing',
        # Include legacy modules
        'legacy.front_panel_logic',
        'legacy.back_panel_logic',
        'legacy.left_panel_logic',
        'legacy.right_panel_logic',
        'legacy.top_panel_logic',
        'legacy.end_panel_logic',
        'legacy.skid_logic',
        'legacy.floorboard_logic',
        'legacy.plywood_layout_generator',
        'legacy.front_panel_logic_unified',
        'legacy.nx_expressions_generator',
        # Direct imports (for backward compatibility)
        'front_panel_logic',
        'back_panel_logic',
        'left_panel_logic',
        'right_panel_logic',
        'top_panel_logic',
        'end_panel_logic',
        'skid_logic',
        'floorboard_logic',
        'plywood_layout_generator',
        'front_panel_logic_unified',
        'nx_expressions_generator',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'scipy',
        'PIL',
        'cv2',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AutoCrate',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Windowed application
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
    version_file=r"{version_file_str}",
)
'''
        
        with open(self.spec_file, 'w') as f:
            f.write(spec_content)
        
        print(f"Spec file created: {self.spec_file}")
    
    def create_version_info(self):
        """Create Windows version info file."""
        print("Creating version info file...")
        
        version_info_content = '''# UTF-8
# Version information for AutoCrate.exe
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(12, 0, 3, 0),
    prodvers=(12, 0, 3, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'AutoCrate Development Team'),
        StringStruct(u'FileDescription', u'AutoCrate - Automated CAD Design Tool'),
        StringStruct(u'FileVersion', u'12.0.2.0'),
        StringStruct(u'InternalName', u'AutoCrate'),
        StringStruct(u'LegalCopyright', u'© 2024 AutoCrate Development Team'),
        StringStruct(u'OriginalFilename', u'AutoCrate.exe'),
        StringStruct(u'ProductName', u'AutoCrate'),
        StringStruct(u'ProductVersion', u'12.0.2.0')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
'''
        
        version_file = self.project_root / "version_info.txt"
        with open(version_file, 'w') as f:
            f.write(version_info_content)
        
        print(f"Version info file created: {version_file}")
    
    def run_tests(self):
        """Run tests before building."""
        print("Running tests...")
        
        try:
            # Change to project directory
            os.chdir(self.project_root)
            
            # Run pytest
            result = subprocess.run([
                sys.executable, '-m', 'pytest', 
                'tests/', '-v', '--tb=short'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("All tests passed!")
                print(result.stdout)
            else:
                print("Some tests failed:")
                print(result.stdout)
                print(result.stderr)
                return False
                
        except FileNotFoundError:
            print("pytest not found - skipping tests")
            print("Install pytest with: pip install pytest")
        
        return True
    
    def build_executable(self):
        """Build the executable using PyInstaller."""
        print("Building executable with PyInstaller...")
        
        try:
            # Change to project directory
            os.chdir(self.project_root)
            
            # Run PyInstaller
            cmd = [sys.executable, '-m', 'PyInstaller', str(self.spec_file), '--noconfirm']
            
            print(f"Running command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("Build completed successfully!")
                print("Output:")
                print(result.stdout)
            else:
                print("Build failed!")
                print("Error output:")
                print(result.stderr)
                return False
        
        except FileNotFoundError:
            print("PyInstaller not found!")
            print("Install PyInstaller with: pip install pyinstaller")
            return False
        
        return True
    
    def create_build_info(self):
        """Create build information file."""
        print("Creating build information...")
        
        build_info_file = self.dist_dir / "build_info.json"
        
        # Add additional info
        self.build_info.update({
            'build_success': True,
            'executable_path': str(self.dist_dir / "AutoCrate.exe"),
            'build_machine': os.environ.get('COMPUTERNAME', 'unknown'),
        })
        
        with open(build_info_file, 'w') as f:
            json.dump(self.build_info, f, indent=2)
        
        print(f"Build info created: {build_info_file}")
    
    def copy_additional_files(self):
        """Copy additional files to distribution directory."""
        print("Copying additional files...")
        
        files_to_copy = [
            # Sample expression files
            ("*.exp", "Sample NX expression files"),
            # Documentation
            ("README.md", "README file"),
            ("EXECUTABLE_README.md", "Executable README"),
        ]
        
        for pattern, description in files_to_copy:
            source_files = list(self.project_root.glob(pattern))
            for source_file in source_files:
                if source_file.exists():
                    dest_file = self.dist_dir / source_file.name
                    shutil.copy2(source_file, dest_file)
                    print(f"  Copied {description}: {source_file.name}")
    
    def verify_build(self):
        """Verify the build was successful."""
        print("Verifying build...")
        
        executable = self.dist_dir / "AutoCrate.exe"
        
        if not executable.exists():
            print("ERROR: Executable not found!")
            return False
        
        # Check file size (should be reasonable)
        file_size = executable.stat().st_size
        print(f"Executable size: {file_size / 1024 / 1024:.1f} MB")
        
        if file_size < 1024 * 1024:  # Less than 1MB is suspicious
            print("WARNING: Executable seems very small")
        
        # Try to get version info (Windows only)
        if os.name == 'nt':
            try:
                result = subprocess.run([
                    'powershell', '-Command', 
                    f'(Get-Item "{executable}").VersionInfo.ProductVersion'
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    version = result.stdout.strip()
                    print(f"Executable version: {version}")
            except Exception:
                pass  # Not critical
        
        print("Build verification completed.")
        return True
    
    def create_installer(self):
        """Create installer (placeholder for future implementation)."""
        print("Installer creation not implemented yet.")
        print("Manual distribution files are ready in dist/ directory.")
    
    def full_build(self, skip_tests=False, skip_clean=False):
        """Perform a complete build process."""
        print("=" * 60)
        print("AutoCrate Build Process Starting")
        print("=" * 60)
        
        try:
            if not skip_clean:
                self.clean()
            
            if not skip_tests:
                if not self.run_tests():
                    print("Build aborted due to test failures.")
                    return False
            
            self.create_version_info()
            self.create_spec_file()
            
            if not self.build_executable():
                print("Build failed!")
                return False
            
            self.copy_additional_files()
            self.create_build_info()
            
            if not self.verify_build():
                print("Build verification failed!")
                return False
            
            print("=" * 60)
            print("AutoCrate Build Completed Successfully!")
            print("=" * 60)
            print(f"Executable location: {self.dist_dir / 'AutoCrate.exe'}")
            print(f"Distribution directory: {self.dist_dir}")
            
            return True
            
        except Exception as e:
            print(f"Build process failed with error: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Main entry point for build script."""
    parser = argparse.ArgumentParser(description="Build AutoCrate executable")
    parser.add_argument('--skip-tests', action='store_true',
                        help='Skip running tests before build')
    parser.add_argument('--skip-clean', action='store_true',
                        help='Skip cleaning previous build artifacts')
    parser.add_argument('--clean-only', action='store_true',
                        help='Only clean, don\'t build')
    
    args = parser.parse_args()
    
    # Get project root (parent of scripts directory)
    project_root = Path(__file__).parent.parent
    
    build_system = AutoCrateBuild(project_root)
    
    if args.clean_only:
        build_system.clean()
        return 0
    
    success = build_system.full_build(
        skip_tests=args.skip_tests,
        skip_clean=args.skip_clean
    )
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())