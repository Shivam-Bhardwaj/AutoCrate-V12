@echo off
echo ============================================
echo AutoCrate Multi-Version Build System
echo Building all 3 UI versions
echo ============================================
echo.

:: Clean previous builds
echo [CLEAN] Removing previous build artifacts...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist AutoCrate.exe del /q AutoCrate.exe
if exist AutoCrate_Modern.exe del /q AutoCrate_Modern.exe
if exist AutoCrate_Ultra.exe del /q AutoCrate_Ultra.exe
echo [CLEAN] Cleanup complete.
echo.

:: Build Standard Version
echo ============================================
echo [1/3] Building Standard AutoCrate...
echo ============================================
python -m PyInstaller --noconfirm --onefile --windowed ^
    --name "AutoCrate" ^
    --distpath "dist" ^
    --workpath "build" ^
    --add-data "security;security" ^
    --hidden-import "security" ^
    --exclude-module "pytest" ^
    --exclude-module "hypothesis" ^
    --strip --optimize 1 --noupx ^
    autocrate/nx_expressions_generator.py

if exist dist\AutoCrate.exe (
    move dist\AutoCrate.exe AutoCrate.exe
    echo [SUCCESS] AutoCrate.exe built successfully!
) else (
    echo [ERROR] Failed to build AutoCrate.exe
)
echo.

:: Clean for next build
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

:: Build Modern Version
echo ============================================
echo [2/3] Building Modern AutoCrate...
echo ============================================
python -m PyInstaller --noconfirm --onefile --windowed ^
    --name "AutoCrate_Modern" ^
    --distpath "dist" ^
    --workpath "build" ^
    --add-data "security;security" ^
    --hidden-import "security" ^
    --hidden-import "autocrate.modern_gui" ^
    --exclude-module "pytest" ^
    --exclude-module "hypothesis" ^
    --strip --optimize 1 --noupx ^
    demo_modern_gui.py

if exist dist\AutoCrate_Modern.exe (
    move dist\AutoCrate_Modern.exe AutoCrate_Modern.exe
    echo [SUCCESS] AutoCrate_Modern.exe built successfully!
) else (
    echo [ERROR] Failed to build AutoCrate_Modern.exe
)
echo.

:: Clean for next build
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

:: Build Ultra-Modern Version
echo ============================================
echo [3/3] Building Ultra-Modern AutoCrate...
echo ============================================
python -m PyInstaller --noconfirm --onefile --windowed ^
    --name "AutoCrate_Ultra" ^
    --distpath "dist" ^
    --workpath "build" ^
    --add-data "security;security" ^
    --hidden-import "security" ^
    --hidden-import "autocrate.ultra_modern_gui" ^
    --hidden-import "autocrate.nx_expressions_generator" ^
    --exclude-module "pytest" ^
    --exclude-module "hypothesis" ^
    --strip --optimize 1 --noupx ^
    launch_ultra_modern.py

if exist dist\AutoCrate_Ultra.exe (
    move dist\AutoCrate_Ultra.exe AutoCrate_Ultra.exe
    echo [SUCCESS] AutoCrate_Ultra.exe built successfully!
) else (
    echo [ERROR] Failed to build AutoCrate_Ultra.exe
)
echo.

:: Final cleanup
echo [CLEAN] Final cleanup...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo.

:: Summary
echo ============================================
echo BUILD SUMMARY
echo ============================================
if exist AutoCrate.exe (
    echo [OK] AutoCrate.exe - Standard Version
) else (
    echo [FAIL] AutoCrate.exe - Standard Version
)

if exist AutoCrate_Modern.exe (
    echo [OK] AutoCrate_Modern.exe - Modern GUI Demo
) else (
    echo [FAIL] AutoCrate_Modern.exe - Modern GUI Demo
)

if exist AutoCrate_Ultra.exe (
    echo [OK] AutoCrate_Ultra.exe - Ultra-Modern Version
) else (
    echo [FAIL] AutoCrate_Ultra.exe - Ultra-Modern Version
)
echo ============================================
echo.
pause