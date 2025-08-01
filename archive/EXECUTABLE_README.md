# AutoCrate Executable

## Overview
This folder contains a standalone AutoCrate executable that can be shared with team members who don't have Python installed.

## Files

### AutoCrate.exe
- **Location**: `dist/AutoCrate.exe`
- **Size**: ~10.4 MB
- **Description**: Standalone executable of the AutoCrate application with GUI
- **Requirements**: None - no Python installation needed

## Usage

### Running the Application
1. Navigate to the `dist` folder
2. Double-click `AutoCrate.exe` to launch the application
3. The GUI will open with all the same functionality as the Python version

### Distribution
- The `AutoCrate.exe` file can be copied to any Windows machine
- No Python installation required on the target machine
- All dependencies are bundled within the executable

## Features Included
- Complete AutoCrate GUI interface
- All panel calculation logic (front, back, left, right, top, end panels)
- Cleat positioning calculations
- Expression file generation
- All bug fixes including the horizontal cleat splice logic fix

## Technical Details
- Built with PyInstaller 6.14.2
- Single-file executable (--onefile)
- Windowed application (--windowed) - no console window
- Includes all necessary Python libraries and tkinter GUI components

## Troubleshooting
- If the application doesn't start, ensure Windows Defender isn't blocking it
- First run may take a few seconds as the executable unpacks
- If issues persist, check Windows Event Viewer for error details

## Build Information
- Source: `nx_expressions_generator.py`
- Build date: July 15, 2025
- Python version: 3.13.5
- Platform: Windows 11

## Files for Development
- `build_exe.py`: Script to rebuild the executable
- `requirements.txt`: Python dependencies (for development only)
- `AutoCrate.spec`: PyInstaller specification file