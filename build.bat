@echo off
:: This script is a launcher for the main PowerShell build engine.
echo ============================================
echo AutoCrate Build System v12.1.2
echo ============================================
echo.
echo [INIT] Build Configuration:
echo        - Target: AutoCrate.exe
echo        - Type: Single executable
echo        - Python: %PYTHON_HOME%
echo        - Working directory: %CD%
echo.
echo [INIT] Starting build process...
echo [INIT] Launching PowerShell build engine...
echo.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\run_build.ps1"
echo.
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ============================================
    echo [ERROR] Build failed with error code %ERRORLEVEL%
    echo [ERROR] Check the build log for detailed error information.
    echo ============================================
    pause
) else (
    echo.
    echo ============================================
    echo [SUCCESS] Build completed successfully!
    echo [SUCCESS] AutoCrate.exe is ready in the project root.
    echo ============================================
)
exit /b %ERRORLEVEL%
