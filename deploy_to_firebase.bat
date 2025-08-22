@echo off
echo ============================================
echo AutoCrate Web - Firebase Deployment
echo ============================================
echo.

:: Check if Firebase CLI is installed
where firebase >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Firebase CLI not found!
    echo Please install it with: npm install -g firebase-tools
    echo.
    pause
    exit /b 1
)

:: Check if in correct directory
if not exist "web\app.py" (
    echo [ERROR] Not in AutoCrate project root!
    echo Please run this script from the AutoCrate V12 directory.
    echo.
    pause
    exit /b 1
)

echo [1/5] Checking Firebase authentication...
firebase login:list >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo You need to login to Firebase first.
    echo Running: firebase login
    firebase login
)

echo.
echo [2/5] Installing Python dependencies...
cd web
pip install -r requirements.txt
cd ..

echo.
echo [3/5] Copying documentation to web/static...
if not exist "web\static\docs" mkdir web\static\docs
xcopy /E /Y /Q docs\* web\static\docs\

echo.
echo [4/5] Validating Firebase configuration...
firebase projects:list

echo.
echo [5/5] Deploying to Firebase...
echo.
echo This will deploy:
echo - Flask application as Cloud Functions
echo - Static files and documentation to Firebase Hosting
echo - Authentication system with password protection
echo.
echo Project: autocrate-web
echo Region: us-central1
echo.
pause

firebase deploy --only hosting,functions

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================
    echo [SUCCESS] Deployment completed!
    echo.
    echo Your app is now live at:
    echo https://autocrate-web.web.app
    echo.
    echo Default password: autocrate2024
    echo (Change this in production!)
    echo ============================================
) else (
    echo.
    echo ============================================
    echo [ERROR] Deployment failed!
    echo Check the error messages above.
    echo ============================================
)

pause