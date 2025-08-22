@echo off
echo ============================================
echo AutoCrate Web - Vercel Deployment
echo ============================================
echo.

:: Check if Vercel CLI is installed
where vercel >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] Vercel CLI not found. Installing...
    echo.
    npm install -g vercel
    echo.
)

:: Check if in correct directory
if not exist "api\index.py" (
    echo [ERROR] Not in AutoCrate project root!
    echo Please run this script from the AutoCrate V12 directory.
    echo.
    pause
    exit /b 1
)

echo [Step 1/4] Setting up environment...
echo.

:: Create .vercel directory if it doesn't exist
if not exist ".vercel" mkdir .vercel

echo [Step 2/4] Configuring environment variables...
echo.
echo You'll need to set these environment variables in Vercel:
echo.
echo 1. AUTH_PASSWORD_HASH - Password hash for authentication
echo    Default password: autocrate2024
echo    Default hash: Use the value from api/index.py
echo.
echo 2. SECRET_KEY - Session secret key (generate a random string)
echo.
echo These can be set in Vercel dashboard after deployment.
echo.
pause

echo.
echo [Step 3/4] Preparing for deployment...
echo.

:: Copy static files if needed
if not exist "web\static" mkdir web\static

echo [Step 4/4] Deploying to Vercel...
echo.
echo This will:
echo - Deploy Python Flask API as serverless functions
echo - Serve static files and templates
echo - Set up password authentication
echo.
echo If this is your first deployment, Vercel will:
echo 1. Ask you to login (opens browser)
echo 2. Ask for project setup details
echo 3. Create and deploy your project
echo.

vercel --prod

echo.
echo ============================================
echo Deployment process completed!
echo.
echo NEXT STEPS:
echo -----------
echo 1. Go to your Vercel dashboard: https://vercel.com/dashboard
echo 2. Find your AutoCrate project
echo 3. Go to Settings > Environment Variables
echo 4. Add these variables:
echo    - AUTH_PASSWORD_HASH (for password)
echo    - SECRET_KEY (random string)
echo.
echo Your app URL will be shown above (usually https://autocrate-web.vercel.app)
echo.
echo Default password: autocrate2024
echo (Change this in production via environment variables!)
echo ============================================
pause