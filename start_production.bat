@echo off
echo ========================================
echo     AutoCrate Production Mode
echo ========================================
echo.

REM Set production environment (default)
set AUTOCRATE_DEV_MODE=0
set AUTOCRATE_SKIP_SECURITY=0
set AUTOCRATE_USE_MOCK_DATA=0
set AUTOCRATE_DEBUG=0

echo Starting AutoCrate in production mode...
echo.
echo Features enabled:
echo - Full security and authentication
echo - Real ASTM calculations
echo - Audit logging
echo - Professional tkinter GUI
echo.

REM Check if executable exists, otherwise run Python version
if exist "dist\AutoCrate.exe" (
    echo Running executable version...
    start "" "dist\AutoCrate.exe"
) else (
    echo Running Python version...
    python nx_expressions_generator.py
)

echo.
echo Production session ended.
pause
