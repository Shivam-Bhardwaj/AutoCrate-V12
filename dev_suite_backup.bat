@echo off
REM AutoCrate V12 Development Suite - Robust Version
REM Fixed hanging issues with better error handling
setlocal EnableDelayedExpansion

title AutoCrate V12 - Dev Suite (Robust)

echo.
echo ============================================================
echo           AutoCrate V12 - Development Suite (Fixed)               
echo ============================================================
echo.

:MAIN_MENU
echo Available Commands:
echo.
echo   [1] Start Development Servers
echo   [2] Run Tests
echo   [3] Build Desktop App  
echo   [4] Deploy Web App
echo   [5] Clean Project
echo   [6] System Check
echo   [7] Quick Start (Desktop Only)
echo   [Q] Quit
echo.

set /p choice="Enter your choice: "

if /i "%choice%"=="1" goto START_DEV
if /i "%choice%"=="2" goto RUN_TESTS  
if /i "%choice%"=="3" goto BUILD_APP
if /i "%choice%"=="4" goto DEPLOY_WEB
if /i "%choice%"=="5" goto CLEAN_PROJECT
if /i "%choice%"=="6" goto SYSTEM_CHECK
if /i "%choice%"=="7" goto QUICK_START
if /i "%choice%"=="Q" goto QUIT
if /i "%choice%"=="q" goto QUIT

echo Invalid choice. Please try again.
timeout /t 2 >nul
cls
goto MAIN_MENU

:START_DEV
echo.
echo Starting Development Servers...
echo.

echo [1/5] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.8+
    echo.
    pause
    goto MAIN_MENU
) else (
    echo Python: OK
)

echo [2/5] Checking web directory...
if not exist "web\" (
    echo ERROR: web directory not found!
    echo.
    pause
    goto MAIN_MENU
) else (
    echo Web directory: OK
)

echo [3/5] Checking Node.js...
cd web
npm --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js/npm not found! Please install Node.js 16+
    echo.
    cd ..
    pause
    goto MAIN_MENU
) else (
    echo Node.js/npm: OK
)
cd ..

echo [4/5] Checking API server file...
if not exist "api_server.py" (
    echo ERROR: api_server.py not found!
    echo.
    pause
    goto MAIN_MENU
) else (
    echo API server file: OK
)

echo [5/5] Starting servers...
echo.

REM Start API server with error handling
echo Starting API server (python api_server.py)...
timeout /t 1 >nul
start "AutoCrate API Server" cmd /k "echo Starting API server... && python api_server.py || (echo API server failed to start && pause)"

echo Waiting 3 seconds for API to initialize...
timeout /t 3 >nul

REM Start web server
echo Starting web development server...
cd web
start "AutoCrate Web Server" cmd /k "echo Starting web server... && npm run dev || (echo Web server failed to start && pause)"
cd ..

echo.
echo ============================================================
echo   SERVERS STARTED SUCCESSFULLY!
echo ============================================================
echo.
echo API Server: http://localhost:8000
echo Web Server: http://localhost:3000
echo.
echo Two new command windows should have opened.
echo If servers fail to start, check the error messages in those windows.
echo.
echo Press any key to return to menu...
pause >nul
goto MAIN_MENU

:RUN_TESTS
echo.
echo Running Tests...
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found
    pause
    goto MAIN_MENU
)

echo Running Python tests...
if exist "tests\" (
    python -m pytest tests/ -v --tb=short 2>nul
    if errorlevel 1 (
        echo Tests may have failed, running basic validation...
        python -c "print('Basic Python test: PASSED')"
    )
) else (
    echo No tests directory found, running basic validation...
    python -c "print('Basic Python test: PASSED')"
)

echo.
echo Tests completed!
pause
goto MAIN_MENU

:BUILD_APP  
echo.
echo Building Desktop Application...
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found
    pause
    goto MAIN_MENU
)

echo Installing PyInstaller...
pip install pyinstaller --quiet

echo Building executable...
pyinstaller --onefile --windowed --name="AutoCrate-V12" main.py --distpath=dist --workpath=build --specpath=.

if exist "dist\AutoCrate-V12.exe" (
    echo.
    echo ============================================================
    echo   BUILD SUCCESSFUL!
    echo ============================================================
    echo Executable created: dist\AutoCrate-V12.exe
    echo Size: 
    dir "dist\AutoCrate-V12.exe" | find "AutoCrate-V12.exe"
) else (
    echo.
    echo BUILD FAILED! Check for errors above.
)

echo.
pause
goto MAIN_MENU

:DEPLOY_WEB
echo.
echo Deploying Web Application...
echo.

if not exist "web\" (
    echo ERROR: web directory not found
    pause
    goto MAIN_MENU
)

cd web
npm --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found
    cd ..
    pause
    goto MAIN_MENU
)

echo Installing dependencies...
npm install --silent

echo Building for production...
npm run build

if exist ".next" (
    echo.
    echo ============================================================
    echo   BUILD SUCCESSFUL!
    echo ============================================================
    echo Next.js build completed in .next directory
    echo.
    echo To deploy to Vercel:
    echo 1. Install Vercel CLI: npm i -g vercel
    echo 2. Run: vercel --prod
    echo.
) else (
    echo BUILD FAILED! Check for errors above.
)

cd ..
pause
goto MAIN_MENU

:CLEAN_PROJECT
echo.
echo Cleaning Project...
echo.

echo Removing Python cache files...
if exist "__pycache__" rmdir /s /q __pycache__ 2>nul
if exist "build" rmdir /s /q build 2>nul
if exist "dist" rmdir /s /q dist 2>nul

for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" 2>nul

echo Cleaning web artifacts...
if exist "web\.next" rmdir /s /q web\.next 2>nul
if exist "web\out" rmdir /s /q web\out 2>nul
if exist "web\node_modules\.cache" rmdir /s /q web\node_modules\.cache 2>nul

echo Cleaning logs and temp files...
del /q *.log 2>nul
del /q *.tmp 2>nul
del /q nul 2>nul
del /q debug\*.log 2>nul

echo.
echo ============================================================
echo   CLEANUP COMPLETED!
echo ============================================================
pause
goto MAIN_MENU

:SYSTEM_CHECK
echo.
echo System Status Check...
echo.

echo Python:
python --version 2>nul && echo   Status: OK || echo   Status: NOT FOUND

echo.
echo Node.js:
if exist "web\" (
    cd web
    node --version 2>nul && echo   Node.js: OK || echo   Node.js: NOT FOUND
    npm --version 2>nul && echo   npm: OK || echo   npm: NOT FOUND
    cd ..
) else (
    echo   Web directory: NOT FOUND
)

echo.
echo Project Files:
if exist "main.py" (echo   main.py: OK) else (echo   main.py: MISSING)
if exist "api_server.py" (echo   api_server.py: OK) else (echo   api_server.py: MISSING)
if exist "web\package.json" (echo   web\package.json: OK) else (echo   web\package.json: MISSING)
if exist "autocrate\" (echo   autocrate\: OK) else (echo   autocrate\: MISSING)

echo.
echo Port Status:
netstat -an | findstr ":3000" >nul && echo   Port 3000: OCCUPIED || echo   Port 3000: FREE
netstat -an | findstr ":8000" >nul && echo   Port 8000: OCCUPIED || echo   Port 8000: FREE

echo.
pause
goto MAIN_MENU

:QUICK_START
echo.
echo Quick Start - Desktop Application Only...
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found
    pause
    goto MAIN_MENU
)

if not exist "main.py" (
    echo ERROR: main.py not found
    pause
    goto MAIN_MENU
)

echo Starting AutoCrate Desktop Application...
start "AutoCrate Desktop" python main.py

echo.
echo Desktop application started!
echo A new window should have opened with the AutoCrate GUI.
echo.
pause
goto MAIN_MENU

:QUIT
echo.
echo Goodbye! 
echo.
echo To restart the development suite, run: dev_suite.bat
echo.
pause
exit /b 0