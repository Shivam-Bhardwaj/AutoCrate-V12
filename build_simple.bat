@echo off
echo ============================================
echo AutoCrate Simple Build System
echo ============================================
echo.

REM Clean previous builds
echo [1/3] Cleaning previous builds...
if exist build rmdir /S /Q build 2>nul
if exist dist rmdir /S /Q dist 2>nul
if exist AutoCrate.exe del AutoCrate.exe 2>nul
if exist AutoCrate.spec del AutoCrate.spec 2>nul
echo       Cleanup complete.
echo.

REM Run PyInstaller with simple configuration
echo [2/3] Building executable...
echo       This may take 30-60 seconds...
python -m PyInstaller ^
    --onefile ^
    --windowed ^
    --name AutoCrate ^
    --distpath . ^
    autocrate/nx_expressions_generator.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ============================================
    echo [ERROR] Build failed!
    echo ============================================
    pause
    exit /b 1
)

REM Clean up build artifacts
echo.
echo [3/3] Cleaning up build artifacts...
if exist build rmdir /S /Q build 2>nul
if exist dist rmdir /S /Q dist 2>nul
if exist AutoCrate.spec del AutoCrate.spec 2>nul

echo.
echo ============================================
echo [SUCCESS] Build completed successfully!
echo [SUCCESS] AutoCrate.exe is ready.
echo ============================================
pause