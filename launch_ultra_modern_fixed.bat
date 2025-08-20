@echo off
title AutoCrate V12 - Ultra Modern GUI (Fixed)
echo ======================================
echo AutoCrate V12 - Ultra Modern Interface
echo ======================================
echo.
echo Features:
echo - Non-blocking test execution
echo - Automatic progress logging
echo - Responsive UI during operations
echo.
echo Starting application...
echo.

python launch_threaded_gui.py

if %errorlevel% neq 0 (
    echo.
    echo Error: Failed to launch application
    echo Make sure Python is installed and in PATH
    pause
)