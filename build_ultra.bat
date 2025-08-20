@echo off
:: This script builds AutoCrate with the Ultra-Modern GUI as default
echo ============================================
echo AutoCrate Ultra-Modern Build System v12.1.5
echo ============================================
echo.
echo [INIT] Build Configuration:
echo        - Target: AutoCrate.exe
echo        - GUI: Ultra-Modern (Default)
echo        - Type: Single executable
echo        - Python: %PYTHON_HOME%
echo        - Working directory: %CD%
echo.

:: Clean previous builds
echo [CLEAN] Removing previous build artifacts...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist AutoCrate.exe del /q AutoCrate.exe
echo [CLEAN] Cleanup complete.
echo.

:: Build with Ultra-Modern GUI
echo [BUILD] Building AutoCrate with Ultra-Modern GUI...
echo.
python -m PyInstaller --noconfirm --onefile --windowed ^
    --name "AutoCrate" ^
    --distpath "dist" ^
    --workpath "build" ^
    --add-data "security;security" ^
    --hidden-import "security" ^
    --hidden-import "customtkinter" ^
    --hidden-import "autocrate.ultra_modern_gui" ^
    --hidden-import "PIL" ^
    --hidden-import "PIL.Image" ^
    --hidden-import "PIL.ImageDraw" ^
    --hidden-import "PIL.ImageFilter" ^
    --collect-all "customtkinter" ^
    --exclude-module "pytest" ^
    --exclude-module "hypothesis" ^
    --strip --optimize 1 --noupx ^
    autocrate/nx_expressions_generator.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Build failed with error code %ERRORLEVEL%
    echo [ERROR] Check the output above for details.
    pause
    exit /b %ERRORLEVEL%
)

:: Move executable to root
if exist dist\AutoCrate.exe (
    move dist\AutoCrate.exe AutoCrate.exe
    echo [SUCCESS] AutoCrate.exe built successfully!
) else (
    echo [ERROR] Failed to build AutoCrate.exe
    pause
    exit /b 1
)

:: Final cleanup
echo [CLEAN] Final cleanup...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo.

:: Success message
echo ============================================
echo [SUCCESS] Build Complete!
echo [SUCCESS] AutoCrate.exe with Ultra-Modern GUI is ready
echo ============================================
echo.
pause