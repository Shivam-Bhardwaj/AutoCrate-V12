@echo off
echo ========================================
echo   AutoCrate Build and Test Pipeline
echo ========================================
echo.

REM Set environment for testing
set AUTOCRATE_TEST_MODE=1

echo Step 1: Running quick tests...
echo ===============================
python quick_test.py
if errorlevel 1 (
    echo.
    echo [ERROR] Tests failed! Build aborted.
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Tests passed! Proceeding with build...
echo.

echo Step 2: Building executable...
echo ==============================
echo This may take 2-3 minutes...
echo.

REM Fast build with optimizations
python -m PyInstaller ^
    --noconfirm ^
    --onefile ^
    --windowed ^
    --name AutoCrate ^
    --distpath dist ^
    --workpath build ^
    --add-data "security;security" ^
    --add-data "docs;docs" ^
    --hidden-import security ^
    --hidden-import security.input_validator ^
    --hidden-import security.file_manager ^
    --hidden-import security.windows_security ^
    --hidden-import security.auth_manager ^
    --hidden-import security.audit_logger ^
    autocrate/nx_expressions_generator.py

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

echo.
echo Step 3: Testing executable...
echo =============================

if exist "dist\AutoCrate.exe" (
    set file_size=0
    for %%A in ("dist\AutoCrate.exe") do set file_size=%%~zA
    set /a size_mb=file_size/1048576
    
    echo [SUCCESS] Build successful!
    echo    Location: dist\AutoCrate.exe
    echo    Size: !size_mb! MB
    echo.
    
    echo Testing executable startup...
    timeout /t 2 >nul
    
    REM Quick executable test (5 second timeout)
    start "" /wait timeout /t 5
    start "AutoCrate Test" "dist\AutoCrate.exe"
    
    echo.
    echo [SUCCESS] Build and test pipeline completed successfully!
    echo.
    echo You can now:
    echo 1. Run 'start_dev.bat' for development (fast iteration)
    echo 2. Run 'start_production.bat' for production testing  
    echo 3. Use 'dist\AutoCrate.exe' for distribution
    
) else (
    echo [ERROR] Executable not found after build!
    exit /b 1
)

echo.
pause
