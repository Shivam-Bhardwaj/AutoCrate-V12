@echo off
:: This script is a launcher for the main PowerShell build engine.
echo Starting build process...
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\run_build.ps1"
if %ERRORLEVEL% NEQ 0 (
    echo Build failed with error code %ERRORLEVEL%
    pause
)
exit /b %ERRORLEVEL%
