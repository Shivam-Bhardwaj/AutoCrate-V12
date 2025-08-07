@echo off
echo ==============================
echo   AutoCrate - Fast Development
echo ==============================
echo.

REM Fast development mode - no security, debug enabled
set AUTOCRATE_DEV_MODE=1
set AUTOCRATE_SKIP_SECURITY=1
set AUTOCRATE_USE_MOCK_DATA=1
set AUTOCRATE_DEBUG=1

echo Starting UI for fast testing...
echo - Security disabled for speed
echo - Mock data enabled
echo - Debug logging active
echo.

REM Launch GUI directly for instant testing
python autocrate/nx_expressions_generator.py

echo.
pause