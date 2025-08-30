@echo off
REM AutoCrate V12 - Simple Development Suite
REM No hanging, no complex checks - just works
setlocal

title AutoCrate V12 - Simple Dev Suite

echo.
echo ============================================================
echo           AutoCrate V12 - Simple Development Suite                
echo ============================================================
echo.

:MAIN_MENU
echo Available Commands:
echo.
echo   [1] Start Both Servers (API + Web)
echo   [2] Start API Server Only
echo   [3] Start Web Server Only
echo   [4] Start Desktop App
echo   [5] Run Basic Test
echo   [6] Clean Project
echo   [Q] Quit
echo.

set /p choice="Enter your choice: "

if /i "%choice%"=="1" goto START_BOTH
if /i "%choice%"=="2" goto START_API
if /i "%choice%"=="3" goto START_WEB
if /i "%choice%"=="4" goto START_DESKTOP
if /i "%choice%"=="5" goto RUN_TEST
if /i "%choice%"=="6" goto CLEAN
if /i "%choice%"=="Q" goto QUIT
if /i "%choice%"=="q" goto QUIT

echo Invalid choice. Try again.
timeout /t 2 >nul
cls
goto MAIN_MENU

:START_BOTH
echo.
echo Starting Both Servers...
echo.

echo Starting API Server...
start "AutoCrate API" cmd /k "cd /d "%~dp0" && echo Starting API Server... && python api_server.py"

echo Waiting 2 seconds...
timeout /t 2 >nul

echo Starting Web Server...
start "AutoCrate Web" cmd /k "cd /d "%~dp0web" && echo Starting Web Server... && npm run dev"

echo.
echo ============================================================
echo   SERVERS STARTING!
echo ============================================================
echo.
echo Two windows should have opened:
echo - AutoCrate API: http://localhost:8000
echo - AutoCrate Web: http://localhost:3000
echo.
echo If servers don't start, check the error messages in those windows.
echo.
pause
goto MAIN_MENU

:START_API
echo.
echo Starting API Server Only...
echo.

start "AutoCrate API" cmd /k "cd /d "%~dp0" && echo Starting API Server... && python api_server.py"

echo.
echo API Server window opened!
echo Check: http://localhost:8000
echo.
pause
goto MAIN_MENU

:START_WEB
echo.
echo Starting Web Server Only...
echo.

start "AutoCrate Web" cmd /k "cd /d "%~dp0web" && echo Starting Web Server... && npm run dev"

echo.
echo Web Server window opened!
echo Check: http://localhost:3000
echo.
pause
goto MAIN_MENU

:START_DESKTOP
echo.
echo Starting Desktop Application...
echo.

if exist "main.py" (
    start "AutoCrate Desktop" python "%~dp0main.py"
    echo Desktop application started!
) else (
    echo ERROR: main.py not found!
)

echo.
pause
goto MAIN_MENU

:RUN_TEST
echo.
echo Running Basic Test...
echo.

python -c "print('Python: OK'); import sys; print(f'Version: {sys.version}'); print('Basic test: PASSED')"

echo.
pause
goto MAIN_MENU

:CLEAN
echo.
echo Cleaning Project...
echo.

if exist "__pycache__" rmdir /s /q __pycache__ 2>nul
if exist "build" rmdir /s /q build 2>nul
if exist "dist" rmdir /s /q dist 2>nul

echo Cleaned Python cache files.

if exist "web\.next" rmdir /s /q web\.next 2>nul
if exist "web\out" rmdir /s /q web\out 2>nul

echo Cleaned web build files.

del /q *.log 2>nul
del /q *.tmp 2>nul

echo Cleaned temporary files.
echo.
echo Cleanup completed!
pause
goto MAIN_MENU

:QUIT
echo.
echo Goodbye!
timeout /t 1 >nul
exit /b 0