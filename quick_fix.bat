@echo off
REM AutoCrate V12 - Quick Fix for Missing Dependencies
echo.
echo ============================================================
echo   AutoCrate V12 - Installing Missing Dependencies
echo ============================================================
echo.

echo [1/3] Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found!
    echo Please install Node.js from: https://nodejs.org
    echo Download the LTS version and install it.
    pause
    exit /b 1
) else (
    node --version
    echo Node.js: OK
)

echo.
echo [2/3] Installing web dependencies...
cd web
if not exist "package.json" (
    echo ERROR: package.json not found in web directory!
    cd ..
    pause
    exit /b 1
)

echo Installing npm packages (this may take a few minutes)...
npm install

if errorlevel 1 (
    echo.
    echo Installation failed! Trying with --force...
    npm install --force
)

cd ..

echo.
echo [3/3] Testing installation...
cd web
npm run dev --help >nul 2>&1
if errorlevel 1 (
    echo ERROR: Next.js still not working after installation!
    echo Try manually running: cd web && npm install
    cd ..
    pause
    exit /b 1
) else (
    echo Next.js: OK
)
cd ..

echo.
echo ============================================================
echo   INSTALLATION COMPLETE!
echo ============================================================
echo.
echo You can now run the development servers:
echo 1. Run: dev_suite_simple.bat
echo 2. Choose option 1 to start both servers
echo.
pause