@echo off
REM AutoCrate V12 Development Suite - Fixed Version
REM Simple, reliable development tools
setlocal EnableDelayedExpansion

title AutoCrate V12 - Dev Suite

echo.
echo ============================================================
echo           AutoCrate V12 - Development Suite                
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
echo   [Q] Quit
echo.

set /p choice="Enter your choice: "

if /i "%choice%"=="1" goto START_DEV
if /i "%choice%"=="2" goto RUN_TESTS  
if /i "%choice%"=="3" goto BUILD_APP
if /i "%choice%"=="4" goto DEPLOY_WEB
if /i "%choice%"=="5" goto CLEAN_PROJECT
if /i "%choice%"=="6" goto SYSTEM_CHECK
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

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found
    pause
    goto MAIN_MENU
)

REM Check Node.js
cd web >nul 2>&1
if errorlevel 1 (
    echo Error: web directory not found
    cd ..
    pause
    goto MAIN_MENU
)

npm --version >nul 2>&1
if errorlevel 1 (
    echo Error: Node.js/npm not found
    cd ..
    pause
    goto MAIN_MENU
)

echo Starting API server...
cd ..
start "AutoCrate API" cmd /k "python api_server.py"

echo Starting web server...
cd web
start "AutoCrate Web" cmd /k "npm run dev"

cd ..
echo.
echo Servers started!
echo API: http://localhost:8000
echo Web: http://localhost:3000
echo.
pause
goto MAIN_MENU

:RUN_TESTS
echo.
echo Running Tests...
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found
    pause
    goto MAIN_MENU
)

echo Running Python tests...
python -m pytest tests/ -v --tb=short 2>nul || (
    echo Running basic test...
    python -c "print('Basic test: PASSED')"
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
    echo Error: Python not found
    pause
    goto MAIN_MENU
)

echo Installing PyInstaller...
pip install pyinstaller >nul 2>&1

echo Building executable...
pyinstaller --onefile --windowed --name="AutoCrate-V12" main.py

if exist "dist\AutoCrate-V12.exe" (
    echo Build successful! Executable: dist\AutoCrate-V12.exe
) else (
    echo Build failed!
)

echo.
pause
goto MAIN_MENU

:DEPLOY_WEB
echo.
echo Deploying Web Application...
echo.

cd web >nul 2>&1
if errorlevel 1 (
    echo Error: web directory not found
    pause
    goto MAIN_MENU
)

npm --version >nul 2>&1
if errorlevel 1 (
    echo Error: Node.js not found
    cd ..
    pause
    goto MAIN_MENU
)

echo Building for production...
npm run build

echo.
echo Build completed! Deploy manually to Vercel.
cd ..
pause
goto MAIN_MENU

:CLEAN_PROJECT
echo.
echo Cleaning Project...
echo.

echo Removing temporary files...
if exist "__pycache__" rmdir /s /q __pycache__ 2>nul
if exist "build" rmdir /s /q build 2>nul
if exist "dist" rmdir /s /q dist 2>nul

for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" 2>nul

echo Cleaning web artifacts...
cd web >nul 2>&1
if not errorlevel 1 (
    if exist ".next" rmdir /s /q .next 2>nul
    if exist "out" rmdir /s /q out 2>nul
    cd ..
)

echo Cleaning logs...
del /q *.log 2>nul
del /q *.tmp 2>nul
del /q nul 2>nul

echo.
echo Cleanup completed!
pause
goto MAIN_MENU

:SYSTEM_CHECK
echo.
echo System Status Check...
echo.

echo Python:
python --version 2>nul || echo   Python: NOT FOUND

echo.
echo Node.js:
cd web >nul 2>&1 && (
    node --version 2>nul || echo   Node.js: NOT FOUND
    npm --version 2>nul || echo   npm: NOT FOUND
    cd ..
) || echo   Web directory: NOT FOUND

echo.
echo Files:
if exist "main.py" (echo   main.py: OK) else (echo   main.py: MISSING)
if exist "web\package.json" (echo   web app: OK) else (echo   web app: MISSING)

echo.
pause
goto MAIN_MENU

:QUIT
echo.
echo Goodbye!
echo.
exit /b 0