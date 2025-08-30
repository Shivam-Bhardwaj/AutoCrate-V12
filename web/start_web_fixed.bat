@echo off
REM AutoCrate V12 - Fixed Web Server Start
REM Increases Node.js memory limit to prevent heap errors

echo.
echo ============================================================
echo   AutoCrate V12 - Fixed Web Server (High Memory)
echo ============================================================
echo.

echo Starting Next.js with increased memory limit...
echo Command: node --max-old-space-size=8192 node_modules/.bin/next dev
echo Memory limit: 8GB (increased from default 4GB)
echo.

REM Start Next.js with 8GB memory limit
node --max-old-space-size=8192 node_modules/.bin/next dev

pause