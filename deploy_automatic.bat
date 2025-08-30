@echo off
setlocal enabledelayedexpansion
title AutoCrate V12 - Automatic Vercel Deployment

echo ================================================================================
echo                    AutoCrate V12 - Automatic Vercel Deployment
echo ================================================================================
echo.

REM Check if we're in the correct directory
if not exist "web" (
    echo [ERROR] Web directory not found! Make sure you're in the AutoCrate V12 root directory.
    pause
    exit /b 1
)

REM Check if Vercel CLI is installed
vercel --version >nul 2>&1
if errorlevel 1 (
    echo Vercel CLI not found. Installing...
    npm install -g vercel
    if errorlevel 1 (
        echo [ERROR] Failed to install Vercel CLI!
        echo Please install it manually: npm install -g vercel
        pause
        exit /b 1
    )
)

echo Vercel CLI is ready!
echo.

REM Navigate to web directory
cd web

echo Updating version information...
REM Update version.json with current timestamp
echo { > version.json
echo   "version": "1.2.0", >> version.json
echo   "buildDate": "%date% %time%", >> version.json
echo   "environment": "production" >> version.json
echo } >> version.json

echo.
echo Installing dependencies...
call npm install
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies!
    cd ..
    pause
    exit /b 1
)

echo.
echo Building production version...
call npm run build
if errorlevel 1 (
    echo [ERROR] Build failed!
    cd ..
    pause
    exit /b 1
)

echo.
echo Deploying to Vercel...
REM Deploy with automatic domain assignment
call vercel --prod --yes
if errorlevel 1 (
    echo [ERROR] Deployment failed!
    cd ..
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Deployment completed successfully!
echo.
echo Your application has been deployed to Vercel.
echo Check the output above for the deployment URL.
echo.

cd ..
pause