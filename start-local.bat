@echo off
setlocal

echo.
echo ========================================
echo    Starting AutoCrate V12 Locally
echo ========================================
echo.

REM Navigate to the web directory
cd web

REM Start the Next.js development server
echo Starting development server...
echo Visit http://localhost:3000 in your browser.
echo.

npm run dev

echo.
echo ========================================
echo        Development Server Stopped
echo ========================================
echo.

endlocal
pause
