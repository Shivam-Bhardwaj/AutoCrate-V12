@echo off
REM AutoCrate V12 - Working Development Suite
REM Tested and verified to work without hanging
setlocal

title AutoCrate V12 - Working Dev Suite

echo.
echo ============================================================
echo           AutoCrate V12 - Working Development Suite                
echo ============================================================
echo.

:MAIN_MENU
echo Available Commands:
echo.
echo   [1] Start API Server (Python)
echo   [2] Start Web Server (Next.js) 
echo   [3] Start Both Servers
echo   [4] Start Desktop App
echo   [5] Test Environment
echo   [6] Install/Fix Dependencies
echo   [7] Clean Project
echo   [Q] Quit
echo.

set /p choice="Enter your choice: "

if /i "%choice%"=="1" goto START_API
if /i "%choice%"=="2" goto START_WEB
if /i "%choice%"=="3" goto START_BOTH
if /i "%choice%"=="4" goto START_DESKTOP
if /i "%choice%"=="5" goto TEST_ENV
if /i "%choice%"=="6" goto FIX_DEPS
if /i "%choice%"=="7" goto CLEAN
if /i "%choice%"=="Q" goto QUIT
if /i "%choice%"=="q" goto QUIT

echo Invalid choice. Try again.
timeout /t 2 >nul
cls
goto MAIN_MENU

:START_API
echo.
echo Starting API Server...
echo.

if not exist "api_server.py" (
    echo ERROR: api_server.py not found!
    echo Current directory: %CD%
    pause
    goto MAIN_MENU
)

echo Starting Python API server on port 5000...
start "AutoCrate API Server" cmd /k "title AutoCrate API Server && echo Starting API Server... && python api_server.py"

echo.
echo ============================================================
echo   API SERVER STARTING
echo ============================================================
echo.
echo Check: http://localhost:5000
echo A new window should have opened for the API server.
echo.
pause
goto MAIN_MENU

:START_WEB
echo.
echo Starting Web Server...
echo.

if not exist "web\" (
    echo ERROR: web directory not found!
    pause
    goto MAIN_MENU
)

if not exist "web\package.json" (
    echo ERROR: web\package.json not found!
    pause
    goto MAIN_MENU
)

cd web

echo Checking if Next.js is available...
npx next --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Next.js not found! Run option 6 to install dependencies.
    cd ..
    pause
    goto MAIN_MENU
)

echo Starting Next.js development server...
start "AutoCrate Web Server" cmd /k "title AutoCrate Web Server && cd /d "%~dp0web" && echo Starting Web Server... && npm run dev"

cd ..

echo.
echo ============================================================
echo   WEB SERVER STARTING
echo ============================================================
echo.
echo Check: http://localhost:3000
echo A new window should have opened for the web server.
echo.
pause
goto MAIN_MENU

:START_BOTH
echo.
echo Starting Both Servers...
echo.

REM Start API first
echo [1/2] Starting API Server...
if exist "api_server.py" (
    start "AutoCrate API Server" cmd /k "title AutoCrate API Server && echo Starting API Server... && python api_server.py"
    echo API Server: Starting...
) else (
    echo WARNING: api_server.py not found, skipping API server
)

echo Waiting 3 seconds for API to initialize...
timeout /t 3 >nul

REM Start Web server
echo [2/2] Starting Web Server...
if exist "web\package.json" (
    cd web
    npx next --version >nul 2>&1
    if errorlevel 1 (
        echo ERROR: Next.js not available! Run option 6 first.
        cd ..
        pause
        goto MAIN_MENU
    )
    start "AutoCrate Web Server" cmd /k "title AutoCrate Web Server && cd /d "%~dp0web" && echo Starting Web Server... && npm run dev"
    cd ..
    echo Web Server: Starting...
) else (
    echo WARNING: web\package.json not found, skipping web server
)

echo.
echo ============================================================
echo   BOTH SERVERS STARTING
echo ============================================================
echo.
echo API Server: http://localhost:5000
echo Web Server: http://localhost:3000
echo.
echo Two new windows should have opened.
echo.
pause
goto MAIN_MENU

:START_DESKTOP
echo.
echo Starting Desktop Application...
echo.

if not exist "main.py" (
    echo ERROR: main.py not found!
    echo Current files:
    dir *.py /b
    pause
    goto MAIN_MENU
)

echo Starting AutoCrate Desktop GUI...
start "AutoCrate Desktop" python main.py

echo.
echo Desktop application started!
echo A new window should have opened with the AutoCrate GUI.
echo.
pause
goto MAIN_MENU

:TEST_ENV
echo.
echo Testing Environment...
echo.

echo [1/5] Testing Python...
python --version 2>nul
if errorlevel 1 (
    echo   Python: NOT FOUND
    echo   Please install Python 3.8+ from python.org
) else (
    python --version
    echo   Python: OK
)

echo.
echo [2/5] Testing Node.js...
node --version 2>nul
if errorlevel 1 (
    echo   Node.js: NOT FOUND
    echo   Please install Node.js from nodejs.org
) else (
    node --version
    echo   Node.js: OK
)

echo.
echo [3/5] Testing npm...
npm --version 2>nul
if errorlevel 1 (
    echo   npm: NOT FOUND
) else (
    npm --version
    echo   npm: OK
)

echo.
echo [4/5] Checking project files...
if exist "main.py" (echo   main.py: OK) else (echo   main.py: MISSING)
if exist "api_server.py" (echo   api_server.py: OK) else (echo   api_server.py: MISSING)
if exist "web\package.json" (echo   web\package.json: OK) else (echo   web\package.json: MISSING)

echo.
echo [5/5] Testing Next.js (if available)...
if exist "web\" (
    cd web
    npx next --version 2>nul
    if errorlevel 1 (
        echo   Next.js: NOT AVAILABLE (run option 6 to install)
    ) else (
        npx next --version
        echo   Next.js: OK
    )
    cd ..
) else (
    echo   web directory: NOT FOUND
)

echo.
echo Environment test completed!
pause
goto MAIN_MENU

:FIX_DEPS
echo.
echo Installing/Fixing Dependencies...
echo.

echo [1/2] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found!
    echo Please install Node.js from: https://nodejs.org
    echo Download and install the LTS version.
    pause
    goto MAIN_MENU
)

echo Node.js found: 
node --version

echo.
echo [2/2] Installing web dependencies...
if not exist "web\" (
    echo ERROR: web directory not found!
    pause
    goto MAIN_MENU
)

cd web
echo Installing npm packages (this may take a few minutes)...
npm install

if errorlevel 1 (
    echo Installation failed, trying with --legacy-peer-deps...
    npm install --legacy-peer-deps
    if errorlevel 1 (
        echo Installation still failed, trying with --force...
        npm install --force
    )
)

echo Testing Next.js installation...
npx next --version
if errorlevel 1 (
    echo ERROR: Next.js installation failed!
    cd ..
    pause
    goto MAIN_MENU
) else (
    echo Next.js installed successfully:
    npx next --version
)

cd ..

echo.
echo ============================================================
echo   DEPENDENCIES FIXED!
echo ============================================================
echo.
echo You can now use options 2 or 3 to start the web server.
echo.
pause
goto MAIN_MENU

:CLEAN
echo.
echo Cleaning Project...
echo.

echo Removing build artifacts...
if exist "__pycache__" (
    rmdir /s /q __pycache__ 2>nul
    echo Removed __pycache__
)
if exist "build" (
    rmdir /s /q build 2>nul
    echo Removed build/
)
if exist "dist" (
    rmdir /s /q dist 2>nul
    echo Removed dist/
)

echo Cleaning web artifacts...
if exist "web\.next" (
    rmdir /s /q web\.next 2>nul
    echo Removed web\.next/
)
if exist "web\out" (
    rmdir /s /q web\out 2>nul
    echo Removed web\out/
)

echo Cleaning temporary files...
del /q *.log 2>nul
del /q *.tmp 2>nul
del /q nul 2>nul

echo.
echo Cleanup completed!
pause
goto MAIN_MENU

:QUIT
echo.
echo Goodbye!
echo.
echo To restart: dev_suite_working.bat
timeout /t 2 >nul
exit /b 0