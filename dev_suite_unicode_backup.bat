@echo off
REM AutoCrate V12 - Verbose Development Suite
REM Shows detailed output for all operations
setlocal EnableDelayedExpansion

title AutoCrate V12 - Verbose Dev Suite

echo.
echo ============================================================
echo           AutoCrate V12 - Verbose Development Suite                
echo ============================================================
echo.

:MAIN_MENU
echo Available Commands:
echo.
echo   [1] Start API Server (Python)
echo   [2] Start Web Server (Next.js) 
echo   [3] Start Both Servers
echo   [4] Start Desktop App
echo   [5] Install Dependencies (Verbose)
echo   [6] Clean Project (Verbose)
echo   [7] Show Project Status
echo   [Q] Quit
echo.

set /p choice="Enter your choice: "

if /i "%choice%"=="1" goto START_API
if /i "%choice%"=="2" goto START_WEB
if /i "%choice%"=="3" goto START_BOTH
if /i "%choice%"=="4" goto START_DESKTOP
if /i "%choice%"=="5" goto INSTALL_DEPS
if /i "%choice%"=="6" goto CLEAN_VERBOSE
if /i "%choice%"=="7" goto SHOW_STATUS
if /i "%choice%"=="Q" goto QUIT
if /i "%choice%"=="q" goto QUIT

echo Invalid choice. Try again.
timeout /t 1 >nul
goto MAIN_MENU

:START_API
echo.
echo Starting API Server...
echo.
echo Command: python api_server.py
echo Port: 5000
echo Working Directory: %~dp0
echo.

start "AutoCrate API Server" cmd /k "title AutoCrate API Server && cd /d "%~dp0" && echo AutoCrate API Server Starting... && python api_server.py"

echo.
echo ============================================================
echo   API SERVER STARTED
echo ============================================================
echo.
echo URL: http://localhost:5000
echo Window opened: AutoCrate API Server
echo Process: python api_server.py
echo.
pause
goto MAIN_MENU

:START_WEB
echo.
echo Starting Web Server...
echo.
echo Command: npm run dev
echo Port: 3000
echo Working Directory: %~dp0web
echo.

start "AutoCrate Web Server" cmd /k "title AutoCrate Web Server && cd /d "%~dp0web" && echo AutoCrate Web Server Starting... && npm run dev"

echo.
echo ============================================================
echo   WEB SERVER STARTED
echo ============================================================
echo.
echo URL: http://localhost:3000
echo Window opened: AutoCrate Web Server
echo Process: npm run dev
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
echo   Command: python api_server.py
echo   Port: 5000
start "AutoCrate API Server" cmd /k "title AutoCrate API Server && cd /d "%~dp0" && echo AutoCrate API Server Starting... && python api_server.py"

echo   Waiting 2 seconds for API to initialize...
timeout /t 2 >nul

echo [2/2] Starting Web Server...
echo   Command: npm run dev  
echo   Port: 3000
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
echo Command: python main.py
echo Working Directory: %~dp0
echo GUI Framework: Tkinter
echo.

start "AutoCrate Desktop" cmd /k "title AutoCrate Desktop && cd /d "%~dp0" && echo AutoCrate Desktop Starting... && python main.py"

echo.
echo ============================================================
echo   DESKTOP APPLICATION STARTED
echo ============================================================
echo.
echo Process: python main.py
echo Window opened: AutoCrate Desktop
echo Framework: Python Tkinter GUI
echo.
pause
goto MAIN_MENU

:INSTALL_DEPS
echo.
echo Installing Dependencies (Verbose Mode)...
echo.

echo Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found!
    echo Please install Node.js from: https://nodejs.org
    pause
    goto MAIN_MENU
) else (
    echo Node.js version: 
    node --version
    echo npm version:
    npm --version
)

echo.
echo Changing to web directory: %~dp0web
cd web

echo.
echo Current directory: %CD%
echo.
echo Package.json contents:
if exist "package.json" (
    echo   ✓ package.json found
    findstr "\"name\":" package.json
    findstr "\"version\":" package.json
) else (
    echo   ✗ package.json not found!
    cd ..
    pause
    goto MAIN_MENU
)

echo.
echo Installing npm packages with verbose output...
echo Command: npm install --verbose
echo This may take several minutes...
echo.

npm install --verbose

echo.
echo ============================================================
echo   DEPENDENCY INSTALLATION COMPLETED
echo ============================================================
echo.
echo Verifying installation...
if exist "node_modules\" (
    echo   ✓ node_modules directory created
    dir node_modules | find "Directory" | find /c "Directory" > temp_count.txt
    set /p DIR_COUNT=<temp_count.txt
    del temp_count.txt
    echo   ✓ Found !DIR_COUNT! installed packages
) else (
    echo   ✗ node_modules directory not found!
)

echo.
echo Testing Next.js availability...
npx next --version >nul 2>&1
if errorlevel 1 (
    echo   ✗ Next.js not available
) else (
    echo   ✓ Next.js version:
    npx next --version
)

echo.
echo You can now use Options 2 or 3 to start the web server.
echo.
cd ..
pause
goto MAIN_MENU

:CLEAN_VERBOSE
echo.
echo ============================================================
echo   PROJECT CLEANUP - VERBOSE MODE
echo ============================================================
echo.

set CLEANED_COUNT=0

echo [1/7] Scanning for Python cache files...
if exist "__pycache__" (
    echo   Found: __pycache__ directory
    dir __pycache__ /s /b 2>nul | find /c ".pyc" > temp_count.txt
    set /p PYFILE_COUNT=<temp_count.txt
    del temp_count.txt
    echo   Contains: !PYFILE_COUNT! .pyc files
    rmdir /s /q __pycache__ 2>nul
    if not exist "__pycache__" (
        echo   ✓ Removed: __pycache__ directory
        set /a CLEANED_COUNT+=1
    ) else (
        echo   ✗ Failed to remove: __pycache__
    )
) else (
    echo   ✓ No __pycache__ directory found
)

echo.
echo [2/7] Scanning for build directories...
if exist "build" (
    echo   Found: build directory
    dir build /s /b 2>nul | find /c "\" > temp_count.txt
    set /p BUILD_COUNT=<temp_count.txt
    del temp_count.txt
    echo   Contains: !BUILD_COUNT! files/folders
    rmdir /s /q build 2>nul
    if not exist "build" (
        echo   ✓ Removed: build directory
        set /a CLEANED_COUNT+=1
    ) else (
        echo   ✗ Failed to remove: build directory
    )
) else (
    echo   ✓ No build directory found
)

echo.
echo [3/7] Scanning for dist directories...
if exist "dist" (
    echo   Found: dist directory
    dir dist /b 2>nul
    rmdir /s /q dist 2>nul
    if not exist "dist" (
        echo   ✓ Removed: dist directory
        set /a CLEANED_COUNT+=1
    ) else (
        echo   ✗ Failed to remove: dist directory
    )
) else (
    echo   ✓ No dist directory found
)

echo.
echo [4/7] Scanning for Next.js cache...
if exist "web\.next" (
    echo   Found: web\.next directory
    for /f %%i in ('dir "web\.next" /s /-c 2^>nul ^| find "File(s)"') do echo   Size: %%i
    rmdir /s /q web\.next 2>nul
    if not exist "web\.next" (
        echo   ✓ Removed: web\.next directory
        set /a CLEANED_COUNT+=1
    ) else (
        echo   ✗ Failed to remove: web\.next
    )
) else (
    echo   ✓ No web\.next directory found
)

echo.
echo [5/7] Scanning for Next.js output...
if exist "web\out" (
    echo   Found: web\out directory
    dir "web\out" /b 2>nul
    rmdir /s /q web\out 2>nul
    if not exist "web\out" (
        echo   ✓ Removed: web\out directory
        set /a CLEANED_COUNT+=1
    ) else (
        echo   ✗ Failed to remove: web\out
    )
) else (
    echo   ✓ No web\out directory found
)

echo.
echo [6/7] Scanning for log files...
set LOG_COUNT=0
for %%f in (*.log) do (
    if exist "%%f" (
        echo   Found: %%f
        del "%%f" 2>nul
        if not exist "%%f" (
            echo   ✓ Removed: %%f
            set /a LOG_COUNT+=1
        ) else (
            echo   ✗ Failed to remove: %%f
        )
    )
)
if !LOG_COUNT! equ 0 (
    echo   ✓ No log files found
) else (
    echo   ✓ Removed: !LOG_COUNT! log files
    set /a CLEANED_COUNT+=!LOG_COUNT!
)

echo.
echo [7/7] Scanning for temporary files...
set TEMP_COUNT=0
for %%f in (*.tmp) do (
    if exist "%%f" (
        echo   Found: %%f
        del "%%f" 2>nul
        if not exist "%%f" (
            echo   ✓ Removed: %%f
            set /a TEMP_COUNT+=1
        ) else (
            echo   ✗ Failed to remove: %%f
        )
    )
)
if !TEMP_COUNT! equ 0 (
    echo   ✓ No temporary files found
) else (
    echo   ✓ Removed: !TEMP_COUNT! temporary files
    set /a CLEANED_COUNT+=!TEMP_COUNT!
)

echo.
echo ============================================================
echo   CLEANUP SUMMARY
echo ============================================================
echo.
echo Total items cleaned: !CLEANED_COUNT!
echo.
echo Project status after cleanup:
if exist "__pycache__" (echo   __pycache__: EXISTS) else (echo   __pycache__: CLEAN)
if exist "build" (echo   build/: EXISTS) else (echo   build/: CLEAN)
if exist "dist" (echo   dist/: EXISTS) else (echo   dist/: CLEAN)
if exist "web\.next" (echo   web\.next/: EXISTS) else (echo   web\.next/: CLEAN)
if exist "web\out" (echo   web\out/: EXISTS) else (echo   web\out/: CLEAN)

echo.
echo Cleanup completed successfully!
pause
goto MAIN_MENU

:SHOW_STATUS
echo.
echo ============================================================
echo   PROJECT STATUS
echo ============================================================
echo.

echo Current Directory: %CD%
echo.

echo Python Environment:
python --version 2>nul && echo   ✓ Python installed || echo   ✗ Python not found
echo.

echo Node.js Environment:
node --version 2>nul && echo   ✓ Node.js installed || echo   ✗ Node.js not found
npm --version 2>nul && echo   ✓ npm installed || echo   ✗ npm not found
echo.

echo Project Files:
if exist "main.py" (echo   ✓ main.py) else (echo   ✗ main.py missing)
if exist "api_server.py" (echo   ✓ api_server.py) else (echo   ✗ api_server.py missing)
if exist "web\package.json" (echo   ✓ web\package.json) else (echo   ✗ web\package.json missing)
if exist "web\node_modules" (echo   ✓ web\node_modules) else (echo   ✗ web\node_modules missing)
echo.

echo Running Processes:
echo Checking for running servers...
netstat -an 2>nul | findstr ":5000" >nul && echo   ✓ Port 5000 (API): OCCUPIED || echo   ○ Port 5000 (API): FREE
netstat -an 2>nul | findstr ":3000" >nul && echo   ✓ Port 3000 (Web): OCCUPIED || echo   ○ Port 3000 (Web): FREE
echo.

pause
goto MAIN_MENU

:QUIT
echo.
echo ============================================================
echo   SESSION ENDING
echo ============================================================
echo.
echo AutoCrate Development Suite closing...
echo Thank you for using AutoCrate V12!
echo.
timeout /t 2 >nul
exit /b 0