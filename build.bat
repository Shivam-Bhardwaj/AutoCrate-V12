@echo off
:: This script is a launcher for the main PowerShell build engine.
echo ============================================
echo AutoCrate Build System v12.0.9
echo ============================================
echo.
echo [INIT] Starting build process...
echo [INIT] Working directory: %CD%
echo [INIT] Launching PowerShell build engine...
echo.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\run_build.ps1"
echo.
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Build failed with error code %ERRORLEVEL%
    echo [ERROR] Check the build log for detailed error information.
    pause
) else (
    echo [SUCCESS] Build completed successfully!
    echo [SUCCESS] AutoCrate.exe is ready in the project root.
)
exit /b %ERRORLEVEL%
