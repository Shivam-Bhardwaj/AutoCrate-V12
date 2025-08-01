@echo off
echo ========================================
echo   AutoCrate Development Environment
echo ========================================
echo.

REM Set development environment variables
set AUTOCRATE_DEV_MODE=1
set AUTOCRATE_SKIP_SECURITY=1
set AUTOCRATE_USE_MOCK_DATA=1
set AUTOCRATE_DEBUG=1

echo Starting Streamlit development interface...
echo.
echo Features enabled:
echo - Hot reload on code changes
echo - Instant calculations (no exe build)
echo - Mock data for fast testing
echo - 3D preview and interactive reports
echo - Security disabled for speed
echo.
echo Opening in browser: http://localhost:8501
echo.

REM Start Streamlit development interface
streamlit run dev_interface.py --server.port 8501 --server.headless false

echo.
echo Development session ended.
pause
