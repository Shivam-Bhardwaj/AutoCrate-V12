@echo off
setlocal enabledelayedexpansion
echo ====================================
echo   AutoCrate - Build and Final Testing
echo ====================================
echo.

REM Set test environment
set AUTOCRATE_TEST_MODE=1
set start_time=%time%

echo [1/4] Running comprehensive tests...
echo ====================================
python quick_test_parallel.py
if errorlevel 1 (
    echo.
    echo [ERROR] Tests failed! Build aborted.
    pause
    exit /b 1
)

echo.
echo [2/4] Building optimized executable...
echo =====================================
echo This will take 1-2 minutes...
echo.

REM Clean previous build
if exist "build" rmdir /s /q "build" 2>nul
if exist "dist" rmdir /s /q "dist" 2>nul

REM Optimized PyInstaller build
python -m PyInstaller ^
    --noconfirm ^
    --onefile ^
    --windowed ^
    --name AutoCrate ^
    --distpath dist ^
    --workpath build ^
    --add-data "security;security" ^
    --hidden-import security ^
    --hidden-import security.input_validator ^
    --hidden-import security.file_manager ^
    --hidden-import security.windows_security ^
    --hidden-import security.auth_manager ^
    --hidden-import security.audit_logger ^
    --exclude-module pytest ^
    --exclude-module hypothesis ^
    --exclude-module matplotlib ^
    --exclude-module IPython ^
    --exclude-module jupyter ^
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
echo [3/4] Validating executable...
echo ==============================

if exist "dist\AutoCrate.exe" (
    for %%A in ("dist\AutoCrate.exe") do set file_size=%%~zA
    set /a size_mb=file_size/1048576
    
    echo [SUCCESS] Executable created!
    echo    Location: dist\AutoCrate.exe
    echo    Size: !size_mb! MB
    echo.
    
    REM Quick startup test
    echo Testing executable startup...
    start /min "" "dist\AutoCrate.exe"
    timeout /t 3 >nul
    taskkill /f /im AutoCrate.exe 2>nul
    
) else (
    echo [ERROR] Executable not found!
    pause
    exit /b 1
)

echo [4/4] Build summary...
echo =====================
set end_time=%time%

REM Calculate build time (simplified)
echo Build completed successfully!
echo Ready for distribution: dist\AutoCrate.exe
echo.
echo [SUCCESS] Build and testing complete!
echo.
pause