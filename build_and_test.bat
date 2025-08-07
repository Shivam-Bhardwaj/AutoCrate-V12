@echo off
setlocal enabledelayedexpansion
echo ========================================
echo   AutoCrate - Build, Test, and Clean
echo ========================================
echo.

REM Clean expressions folder first
echo [1/5] Cleaning expressions folder...
if exist "expressions" (
    rmdir /s /q "expressions" 2>nul
    mkdir "expressions"
    mkdir "expressions\quick_test"
) else (
    mkdir "expressions"
    mkdir "expressions\quick_test"
)
echo    Expressions folder cleaned.
echo.

REM Run comprehensive tests
echo [2/5] Running comprehensive tests...
echo ========================================
python -m pytest tests\ -v --tb=short
if errorlevel 1 (
    echo.
    echo [ERROR] Tests failed! Build aborted.
    pause
    exit /b 1
)
echo.

REM Build executable
echo [3/5] Building executable...
echo ========================================
echo This will take 1-2 minutes...

REM Clean previous build
if exist "build" rmdir /s /q "build" 2>nul
if exist "dist" rmdir /s /q "dist" 2>nul
if exist "AutoCrate.exe" del "AutoCrate.exe" 2>nul

REM Build with PyInstaller
python -m PyInstaller ^
    --noconfirm ^
    --onefile ^
    --windowed ^
    --name AutoCrate ^
    --distpath . ^
    --workpath build ^
    --add-data "security;security" ^
    --add-data "autocrate;autocrate" ^
    --hidden-import security ^
    --hidden-import security.input_validator ^
    --hidden-import autocrate.expression_file_manager ^
    --exclude-module pytest ^
    --exclude-module hypothesis ^
    --strip ^
    --optimize 2 ^
    autocrate/nx_expressions_generator.py

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed!
    pause
    exit /b 1
)
echo.

REM Clean build artifacts
echo [4/5] Cleaning build artifacts...
if exist "build" rmdir /s /q "build" 2>nul
if exist "dist" rmdir /s /q "dist" 2>nul
if exist "AutoCrate.spec" del "AutoCrate.spec" 2>nul
echo    Build artifacts cleaned.
echo.

REM Verify executable
echo [5/5] Verifying executable...
if exist "AutoCrate.exe" (
    for %%A in ("AutoCrate.exe") do set file_size=%%~zA
    set /a size_mb=!file_size!/1048576
    
    echo [SUCCESS] Build complete!
    echo    Executable: AutoCrate.exe
    echo    Size: !size_mb! MB
    echo    Location: Root folder
) else (
    echo [ERROR] Executable not found!
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Build and Test Complete!
echo ========================================
echo.
pause