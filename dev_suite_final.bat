@echo off
REM AutoCrate V12 - Final Working Development Suite
REM Bypasses problematic checks that cause hanging
setlocal

title AutoCrate V12 - Final Dev Suite

echo.
echo ============================================================
echo           AutoCrate V12 - Final Development Suite                
echo ============================================================
echo.

:MAIN_MENU
echo Available Commands:
echo.
echo   [1] Start API Server (Python)
echo   [2] Start Web Server (Next.js) 
echo   [3] Start Both Servers
echo   [4] Start Desktop App
echo   [5] Install Dependencies
echo   [6] Clean Project
echo   [Q] Quit
echo.

set /p choice="Enter your choice: "

if /i "%choice%"=="1" goto START_API
if /i "%choice%"=="2" goto START_WEB
if /i "%choice%"=="3" goto START_BOTH
if /i "%choice%"=="4" goto START_DESKTOP
if /i "%choice%"=="5" goto INSTALL_DEPS
if /i "%choice%"=="6" goto CLEAN
if /i "%choice%"=="Q" goto QUIT
if /i "%choice%"=="q" goto QUIT

echo Invalid choice. Try again.
timeout /t 1 >nul
goto MAIN_MENU

:START_API
echo.
echo Starting API Server...
echo.

start "AutoCrate API Server" cmd /k "title AutoCrate API Server && cd /d "%~dp0" && echo AutoCrate API Server Starting... && python api_server.py"

echo.
echo ============================================================
echo   API SERVER STARTED
echo ============================================================
echo.
echo URL: http://localhost:5000
echo Window opened: AutoCrate API Server
echo.
pause
goto MAIN_MENU

:START_WEB
echo.
echo Starting Web Server...
echo.

echo Starting Next.js development server...
start "AutoCrate Web Server" cmd /k "title AutoCrate Web Server && cd /d "%~dp0web" && echo AutoCrate Web Server Starting... && npm run dev"

echo.
echo ============================================================
echo   WEB SERVER STARTED
echo ============================================================
echo.
echo URL: http://localhost:3000
echo Window opened: AutoCrate Web Server
echo.
echo If you get 'next' not found error, run Option 5 first.
echo.
pause
goto MAIN_MENU

:START_BOTH
echo.
echo Starting Both Servers...
echo.

echo [1/2] Starting API Server...
start "AutoCrate API Server" cmd /k "title AutoCrate API Server && cd /d "%~dp0" && echo AutoCrate API Server Starting... && python api_server.py"

echo Waiting 2 seconds...
timeout /t 2 >nul

echo [2/2] Starting Web Server...
start "AutoCrate Web Server" cmd /k "title AutoCrate Web Server && cd /d "%~dp0web" && echo AutoCrate Web Server Starting... && npm run dev"

echo.
echo ============================================================
echo   BOTH SERVERS STARTED
echo ============================================================
echo.
echo API Server: http://localhost:5000
echo Web Server: http://localhost:3000
echo.
echo Two windows should have opened.
echo If web server fails, run Option 5 first.
echo.
pause
goto MAIN_MENU

:START_DESKTOP
echo.
echo Starting Desktop Application...
echo.

start "AutoCrate Desktop" cmd /k "title AutoCrate Desktop && cd /d "%~dp0" && echo AutoCrate Desktop Starting... && python main.py"

echo.
echo Desktop application window opened!
echo.
pause
goto MAIN_MENU

:INSTALL_DEPS
echo.
echo Installing Dependencies...
echo.

echo Installing Node.js dependencies...
cd web
echo This may take a few minutes...
npm install

echo.
echo Dependencies installation completed!
echo You can now use Options 2 or 3 to start the web server.
echo.
cd ..
pause
goto MAIN_MENU

:CLEAN
echo.
echo Cleaning Project...
echo.

if exist "__pycache__" rmdir /s /q __pycache__ 2>nul
if exist "build" rmdir /s /q build 2>nul
if exist "dist" rmdir /s /q dist 2>nul
if exist "web\.next" rmdir /s /q web\.next 2>nul
if exist "web\out" rmdir /s /q web\out 2>nul
del /q *.log 2>nul
del /q *.tmp 2>nul

echo Cleanup completed!
pause
goto MAIN_MENU

:QUIT
echo.
echo Goodbye!
timeout /t 1 >nul
exit /b 0