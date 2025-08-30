@echo off
REM AutoCrate V12 - Windows-Compatible Web Server Start
REM Fixed for Windows with proper memory allocation

echo.
echo ============================================================
echo   AutoCrate V12 - Web Server (Windows Fixed)
echo ============================================================
echo.

echo Setting Node.js memory limit to 8GB...
set NODE_OPTIONS=--max-old-space-size=8192

echo Starting Next.js development server...
echo Memory limit: %NODE_OPTIONS%
echo Port: 3000
echo.

npx next dev

pause