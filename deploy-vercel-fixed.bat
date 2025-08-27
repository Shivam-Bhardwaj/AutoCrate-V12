@echo off
setlocal enabledelayedexpansion

echo.
echo ========================================
echo      AutoCrate V12 Vercel Deploy
echo ========================================
echo.

REM Navigate to the web directory
cd web

REM Check if we're in the right directory
if not exist "package.json" (
    echo [ERROR] package.json not found. Make sure you're in the correct directory.
    pause
    exit /b 1
)

REM Check if node_modules exists
if not exist "node_modules" (
    echo [INFO] Installing dependencies first...
    npm install
    if errorlevel 1 (
        echo [ERROR] npm install failed!
        pause
        exit /b 1
    )
)

REM Test build locally first
echo.
echo [1/4] Testing local build...
echo.
npm run build
if errorlevel 1 (
    echo.
    echo [ERROR] Local build failed! Fix build errors before deploying.
    echo Common issues:
    echo - TypeScript errors
    echo - Missing dependencies
    echo - Import/export issues
    echo - Environment variables
    pause
    exit /b 1
)

echo.
echo [2/4] Local build successful! Proceeding with deployment...
echo.

REM Set production environment variables
echo [3/4] Setting up production environment...
echo NEXT_PUBLIC_API_URL=https://adequate-patience-production.up.railway.app/api > .env.production.local

REM Deploy to Vercel with error handling
echo.
echo [4/4] Deploying to Vercel...
echo.

REM Try deployment with verbose output
vercel --prod --yes --confirm
set DEPLOY_EXIT_CODE=!errorlevel!

REM Clean up environment file
if exist ".env.production.local" del .env.production.local

REM Check deployment result
if !DEPLOY_EXIT_CODE! equ 0 (
    echo.
    echo ========================================
    echo       Deployment Successful!
    echo ========================================
    echo.
    echo Your application has been deployed to Vercel.
    echo Check your Vercel dashboard for the live URL.
) else (
    echo.
    echo ========================================
    echo       Deployment Failed!
    echo ========================================
    echo.
    echo Common solutions:
    echo 1. Check your Vercel account permissions
    echo 2. Verify project name exists or create new one
    echo 3. Check build logs for specific errors
    echo 4. Ensure all dependencies are properly installed
    echo 5. Verify environment variables are set correctly
    echo.
    echo Run 'vercel --help' for more options
    echo Or try 'vercel login' to re-authenticate
)

echo.
echo Press any key to continue...
pause >nul

cd ..
exit /b !DEPLOY_EXIT_CODE!
