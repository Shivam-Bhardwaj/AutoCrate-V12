@echo off
setlocal enabledelayedexpansion
title AutoCrate V12 - Master Control System

:menu
cls
echo ================================================================================
echo                     AutoCrate V12 - Master Control System
echo ================================================================================
echo.
echo   DEVELOPMENT:
echo   [1] Start Web Dev Server (Next.js @ port 3000)
echo   [2] Start API Server (Python Flask @ port 5000)
echo   [3] Start Both Servers (Web + API)
echo   [4] Run Desktop App (Python Tkinter)
echo.
echo   BUILD & DEPLOY:
echo   [5] Build Executable (.exe)
echo   [6] Deploy to Vercel
echo   [7] Build Web Production
echo   [S] Save All (Git + Deploy + Build)
echo.
echo   TESTING:
echo   [8] Run Tests
echo   [9] Test NX Expressions
echo.
echo   UTILITIES:
echo   [A] Check Dependencies
echo   [B] Install Dependencies
echo   [C] Clean Build Files
echo   [D] View Logs
echo   [E] Show Project Status
echo   [K] Kill All Servers
echo.
echo   ADVANCED:
echo   [X] Advanced Compilation Options
echo.
echo   [Q] Quit
echo.
echo ================================================================================
set /p choice="Select option: "

if /i "%choice%"=="1" goto dev_server
if /i "%choice%"=="2" goto api_server
if /i "%choice%"=="3" goto start_both
if /i "%choice%"=="4" goto run_desktop
if /i "%choice%"=="5" goto build_exe
if /i "%choice%"=="6" goto deploy_vercel
if /i "%choice%"=="7" goto build_web
if /i "%choice%"=="s" goto save_all
if /i "%choice%"=="8" goto run_tests
if /i "%choice%"=="9" goto test_nx
if /i "%choice%"=="a" goto check_deps
if /i "%choice%"=="b" goto install_deps
if /i "%choice%"=="c" goto clean_build
if /i "%choice%"=="d" goto view_logs
if /i "%choice%"=="e" goto show_status
if /i "%choice%"=="k" goto kill_servers
if /i "%choice%"=="x" goto advanced_compile
if /i "%choice%"=="q" exit /b 0
goto invalid

:dev_server
    cls
    echo ================================================================================
    echo                      Starting Web Development Server
    echo ================================================================================
    echo.
    if not exist "web" (
        echo [ERROR] Web directory not found!
        pause
        goto menu
    )
    
    cd web
    
    if not exist "node_modules" (
        echo Installing dependencies...
        call npm install
        if errorlevel 1 (
            echo [ERROR] Failed to install dependencies!
            cd ..
            pause
            goto menu
        )
    )
    
    echo.
    echo Starting development server...
    echo Server will run at: http://localhost:3000
    echo Press Ctrl+C to stop the server.
    echo.
    call npm run dev
    cd ..
    pause
    goto menu

:api_server
    cls
    echo ================================================================================
    echo                      Starting Python API Server
    echo ================================================================================
    echo.
    if not exist "api_server.py" (
        echo [ERROR] api_server.py not found!
        pause
        goto menu
    )
    
    echo Starting Python API server...
    echo Server will run at: http://localhost:5000
    echo.
    echo This provides the exact desktop calculation engine to the web app
    echo Press Ctrl+C to stop the server.
    echo.
    python api_server.py
    pause
    goto menu

:start_both
    cls
    echo ================================================================================
    echo                      Starting Both Servers
    echo ================================================================================
    echo.
    
    echo [1/2] Starting API Server (port 5000)...
    start "AutoCrate API" cmd /k "title AutoCrate API Server && cd /d "%~dp0" && python api_server.py"
    
    echo Waiting for API to initialize...
    timeout /t 2 >nul
    
    echo [2/2] Starting Web Server (port 3000)...
    start "AutoCrate Web" cmd /k "title AutoCrate Web Server && cd /d "%~dp0web" && npm run dev"
    
    echo.
    echo ================================================================================
    echo Both servers started in separate windows:
    echo   API Server: http://localhost:5000
    echo   Web Server: http://localhost:3000
    echo ================================================================================
    pause
    goto menu

:run_desktop
    cls
    echo ================================================================================
    echo                      Running Desktop Application
    echo ================================================================================
    echo.
    if not exist "main.py" (
        echo [ERROR] main.py not found!
        pause
        goto menu
    )
    
    echo Starting AutoCrate desktop application...
    python main.py
    pause
    goto menu

:build_exe
    cls
    echo ================================================================================
    echo                         Build Executable
    echo ================================================================================
    echo.
    set /p confirm="Build AutoCrate.exe? (y/n): "
    if /i not "!confirm!"=="y" goto menu
    
    echo.
    echo Cleaning previous builds...
    if exist "build" rmdir /s /q "build"
    if exist "dist" rmdir /s /q "dist"
    
    echo.
    echo Building with PyInstaller...
    python -m PyInstaller ^
        --noconfirm ^
        --onefile ^
        --windowed ^
        --name AutoCrate ^
        --distpath dist ^
        --workpath build ^
        --add-data "security;security" ^
        --add-data "autocrate;autocrate" ^
        --hidden-import security.input_validator ^
        --hidden-import security.file_manager ^
        --hidden-import security.windows_security ^
        --hidden-import security.auth_manager ^
        --hidden-import security.audit_logger ^
        --exclude-module pytest ^
        --exclude-module matplotlib ^
        main.py
    
    if errorlevel 1 (
        echo.
        echo [ERROR] Build failed!
        pause
        goto menu
    )
    
    echo.
    if exist "dist\AutoCrate.exe" (
        copy /Y "dist\AutoCrate.exe" "AutoCrate.exe" >nul 2>&1
        echo [SUCCESS] AutoCrate.exe created successfully!
    )
    
    echo Cleaning up build directories...
    if exist "build" rmdir /s /q "build"
    if exist "dist" rmdir /s /q "dist"
    
    echo.
    echo [COMPLETE] Executable available at: %cd%\AutoCrate.exe
    pause
    goto menu

:deploy_vercel
    cls
    echo ================================================================================
    echo                         Deploy to Vercel
    echo ================================================================================
    echo.
    
    if exist "deploy_automatic.bat" (
        call deploy_automatic.bat
    ) else (
        echo Deploying directly with Vercel CLI...
        cd web
        if exist ".vercel" (
            echo Using existing Vercel project configuration...
            call vercel --prod --yes
        ) else (
            echo First-time deployment - configuring project...
            call vercel --prod
        )
        cd ..
    )
    pause
    goto menu

:build_web
    cls
    echo ================================================================================
    echo                      Build Web for Production
    echo ================================================================================
    echo.
    
    cd web
    
    echo Installing dependencies...
    call npm install
    
    echo.
    echo Building production bundle...
    call npm run build
    
    if errorlevel 1 (
        echo.
        echo [ERROR] Build failed!
    ) else (
        echo.
        echo [SUCCESS] Production build completed!
        echo Build output: %cd%\.next
    )
    
    cd ..
    pause
    goto menu

:save_all
    cls
    echo ================================================================================
    echo                        Save All - Complete Workflow
    echo ================================================================================
    echo.
    echo This will:
    echo   1. Commit and push to Git
    echo   2. Deploy to Vercel
    echo   3. Build executable
    echo.
    set /p confirm="Continue? (y/n): "
    if /i not "!confirm!"=="y" goto menu
    
    echo.
    echo [STEP 1/3] Git Operations
    echo ------------------------
    git status >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Not a git repository!
        goto save_all_deploy
    )
    
    git status --porcelain > temp_git_status.txt
    for /f %%i in (temp_git_status.txt) do set HAS_CHANGES=1
    del temp_git_status.txt 2>nul
    
    if not defined HAS_CHANGES (
        echo No changes to commit.
    ) else (
        git add .
        set COMMIT_MSG=AutoCrate V12 - Save All %date% %time%
        git commit -m "!COMMIT_MSG!"
        git push
        echo [SUCCESS] Changes pushed to Git!
    )
    
:save_all_deploy
    echo.
    echo [STEP 2/3] Vercel Deployment
    echo ---------------------------
    call :deploy_vercel_inline
    
    echo.
    echo [STEP 3/3] Build Executable
    echo --------------------------
    call :build_exe_inline
    
    echo.
    echo ================================================================================
    echo                          WORKFLOW COMPLETE!
    echo ================================================================================
    pause
    goto menu

:deploy_vercel_inline
    cd web
    if exist ".vercel" (
        call vercel --prod --yes
    ) else (
        call vercel --prod
    )
    cd ..
    goto :eof

:build_exe_inline
    if exist "build" rmdir /s /q "build"
    if exist "dist" rmdir /s /q "dist"
    python -m PyInstaller ^
        --noconfirm ^
        --onefile ^
        --windowed ^
        --name AutoCrate ^
        --distpath dist ^
        --workpath build ^
        --add-data "security;security" ^
        --add-data "autocrate;autocrate" ^
        --hidden-import security.input_validator ^
        --hidden-import security.file_manager ^
        --hidden-import security.windows_security ^
        --hidden-import security.auth_manager ^
        --hidden-import security.audit_logger ^
        --exclude-module pytest ^
        --exclude-module matplotlib ^
        main.py
    if exist "dist\AutoCrate.exe" (
        copy /Y "dist\AutoCrate.exe" "AutoCrate.exe" >nul 2>&1
    )
    if exist "build" rmdir /s /q "build"
    if exist "dist" rmdir /s /q "dist"
    goto :eof

:run_tests
    cls
    echo ================================================================================
    echo                             Run Tests
    echo ================================================================================
    echo.
    echo [1] Quick Test Suite (run_tests.py)
    echo [2] NX Expression Tests
    echo [3] Full Test Suite (pytest)
    echo [4] Web Tests (npm test)
    echo [5] Back to Menu
    echo.
    set /p test_choice="Select test option (1-5): "
    
    if "!test_choice!"=="1" (
        cls
        echo Running quick test suite...
        if exist "run_tests.py" python run_tests.py
        pause
    ) else if "!test_choice!"=="2" (
        cls
        echo Running NX expression tests...
        if exist "test_nx_generation.py" python test_nx_generation.py
        pause
    ) else if "!test_choice!"=="3" (
        cls
        echo Running full test suite...
        python -m pytest tests/ -v --tb=short
        pause
    ) else if "!test_choice!"=="4" (
        cls
        echo Running web tests...
        cd web
        call npm test
        cd ..
        pause
    )
    goto menu

:test_nx
    cls
    echo ================================================================================
    echo                        Test NX Expression Generation
    echo ================================================================================
    echo.
    if exist "test_nx_generation.py" (
        python test_nx_generation.py
    ) else (
        echo [ERROR] test_nx_generation.py not found!
    )
    pause
    goto menu

:check_deps
    cls
    echo ================================================================================
    echo                        Check Dependencies
    echo ================================================================================
    echo.
    
    echo Python:
    python --version
    echo.
    echo Python packages:
    pip list | findstr /i "numpy pandas tkinter pyinstaller pytest flask"
    
    echo.
    echo Node.js:
    node --version
    npm --version
    
    echo.
    if exist "web\package.json" (
        cd web
        echo Web dependencies:
        npm list --depth=0
        cd ..
    )
    
    pause
    goto menu

:install_deps
    cls
    echo ================================================================================
    echo                       Install Dependencies
    echo ================================================================================
    echo.
    
    echo Checking Node.js...
    node --version >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Node.js not found!
        echo Please install from: https://nodejs.org
        pause
        goto menu
    )
    
    echo Installing Python packages...
    pip install numpy pandas pyinstaller pytest flask
    
    echo.
    echo Installing web dependencies...
    cd web
    npm install --verbose
    
    echo.
    echo Verifying installation...
    if exist "node_modules\" (
        echo [OK] Web dependencies installed
    ) else (
        echo [ERROR] Web dependencies installation failed!
    )
    
    cd ..
    pause
    goto menu

:clean_build
    cls
    echo ================================================================================
    echo                         Clean Build Files
    echo ================================================================================
    echo.
    
    echo Cleaning Python build files...
    if exist "build" rmdir /s /q "build" && echo - Removed build/
    if exist "dist" rmdir /s /q "dist" && echo - Removed dist/
    if exist "__pycache__" rmdir /s /q "__pycache__" && echo - Removed __pycache__/
    if exist ".pytest_cache" rmdir /s /q ".pytest_cache" && echo - Removed .pytest_cache/
    
    echo.
    echo Cleaning web build files...
    if exist "web\.next" (
        cd web
        rmdir /s /q ".next" && echo - Removed web/.next/
        if exist "out" rmdir /s /q "out" && echo - Removed web/out/
        cd ..
    )
    
    echo.
    echo Cleaning log files...
    del *.log 2>nul && echo - Removed log files
    if exist "logs" del logs\*.log 2>nul && echo - Removed logs/
    
    echo.
    echo [SUCCESS] Build files cleaned!
    pause
    goto menu

:view_logs
    cls
    echo ================================================================================
    echo                            View Logs
    echo ================================================================================
    echo.
    
    echo Available log files:
    dir *.log /b 2>nul
    dir logs\*.log /b 2>nul
    
    echo.
    echo [1] View latest log
    echo [2] View all logs
    echo [3] Clear logs
    echo [4] Back to Menu
    echo.
    set /p log_choice="Select option (1-4): "
    
    if "!log_choice!"=="1" (
        if exist "autocrate.log" type autocrate.log | more
        pause
    ) else if "!log_choice!"=="2" (
        for %%f in (*.log logs\*.log) do (
            echo === %%f ===
            type "%%f" 2>nul
            echo.
        )
        pause
    ) else if "!log_choice!"=="3" (
        del *.log 2>nul
        del logs\*.log 2>nul
        echo Logs cleared.
        pause
    )
    goto menu

:show_status
    cls
    echo ================================================================================
    echo                          Project Status
    echo ================================================================================
    echo.
    
    echo Directory: %CD%
    echo.
    
    echo Python:
    python --version 2>nul && echo [OK] Python installed || echo [ERROR] Python not found
    
    echo.
    echo Node.js:
    node --version 2>nul && echo [OK] Node.js installed || echo [ERROR] Node.js not found
    npm --version 2>nul && echo [OK] npm installed || echo [ERROR] npm not found
    
    echo.
    echo Core Files:
    if exist "main.py" (echo [OK] main.py) else (echo [ERROR] main.py missing)
    if exist "api_server.py" (echo [OK] api_server.py) else (echo [ERROR] api_server.py missing)
    if exist "web\package.json" (echo [OK] web\package.json) else (echo [ERROR] web\package.json missing)
    if exist "web\node_modules" (echo [OK] web\node_modules) else (echo [WARN] web\node_modules missing - run Install Dependencies)
    if exist "AutoCrate.exe" (echo [OK] AutoCrate.exe) else (echo [INFO] AutoCrate.exe not built yet)
    
    echo.
    echo Server Ports:
    netstat -an 2>nul | findstr ":3000" >nul && echo [OCCUPIED] Port 3000 (Web) || echo [FREE] Port 3000 (Web)
    netstat -an 2>nul | findstr ":5000" >nul && echo [OCCUPIED] Port 5000 (API) || echo [FREE] Port 5000 (API)
    
    pause
    goto menu

:kill_servers
    cls
    echo ================================================================================
    echo                        Kill All Servers
    echo ================================================================================
    echo.
    
    echo Stopping Node.js servers (ports 3000-3010)...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000') do (
        echo Killing PID %%a on port 3000
        taskkill /F /PID %%a 2>nul
    )
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3001') do (
        echo Killing PID %%a on port 3001
        taskkill /F /PID %%a 2>nul
    )
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3002') do (
        echo Killing PID %%a on port 3002
        taskkill /F /PID %%a 2>nul
    )
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3003') do (
        echo Killing PID %%a on port 3003
        taskkill /F /PID %%a 2>nul
    )
    
    echo.
    echo Stopping Python servers (ports 5000, 8000)...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5000') do (
        echo Killing PID %%a on port 5000
        taskkill /F /PID %%a 2>nul
    )
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
        echo Killing PID %%a on port 8000
        taskkill /F /PID %%a 2>nul
    )
    
    echo.
    echo Stopping AutoCrate processes...
    taskkill /F /IM python.exe /FI "WINDOWTITLE eq AutoCrate*" 2>nul
    taskkill /F /IM pythonw.exe /FI "WINDOWTITLE eq AutoCrate*" 2>nul
    taskkill /F /IM AutoCrate.exe 2>nul
    
    echo.
    echo Cleaning zombie processes...
    wmic process where "name='node.exe' and commandline like '%%autocrate%%'" delete 2>nul
    wmic process where "name='python.exe' and commandline like '%%autocrate%%'" delete 2>nul
    
    echo.
    set /p kill_all_node="Kill ALL node.exe processes? (y/n): "
    if /i "!kill_all_node!"=="y" (
        taskkill /F /IM node.exe 2>nul
        echo All node.exe processes terminated.
    )
    
    echo.
    echo Verifying ports...
    netstat -an | findstr :3000 >nul 2>&1
    if not errorlevel 1 (echo [WARNING] Port 3000 still occupied) else (echo [OK] Port 3000 free)
    netstat -an | findstr :5000 >nul 2>&1
    if not errorlevel 1 (echo [WARNING] Port 5000 still occupied) else (echo [OK] Port 5000 free)
    
    echo.
    echo [COMPLETE] Server cleanup finished.
    pause
    goto menu

:advanced_compile
    cls
    echo ================================================================================
    echo                    Advanced Compilation Options
    echo ================================================================================
    echo.
    echo [1] Standard Build (Windowed .exe)
    echo [2] Console Build (With debug console)
    echo [3] Optimized Build (Smaller size)
    echo [4] Debug Build (With symbols)
    echo [5] Portable Build (All dependencies)
    echo [6] Back to Menu
    echo.
    set /p compile_choice="Select option (1-6): "
    
    if "!compile_choice!"=="6" goto menu
    
    echo.
    echo Cleaning previous builds...
    if exist "build" rmdir /s /q "build"
    if exist "dist" rmdir /s /q "dist"
    
    set PYINSTALLER_CMD=python -m PyInstaller --noconfirm --onefile --distpath dist --workpath build --add-data "security;security" --add-data "autocrate;autocrate" --hidden-import security.input_validator --hidden-import security.file_manager --hidden-import security.windows_security --hidden-import security.auth_manager --hidden-import security.audit_logger --exclude-module pytest --exclude-module matplotlib
    
    if "!compile_choice!"=="1" (
        echo Building standard version...
        !PYINSTALLER_CMD! --windowed --name AutoCrate main.py
        set OUTPUT_NAME=AutoCrate.exe
    ) else if "!compile_choice!"=="2" (
        echo Building console version...
        !PYINSTALLER_CMD! --console --name AutoCrate-Console main.py
        set OUTPUT_NAME=AutoCrate-Console.exe
    ) else if "!compile_choice!"=="3" (
        echo Building optimized version...
        !PYINSTALLER_CMD! --windowed --optimize 2 --strip --name AutoCrate-Optimized main.py
        set OUTPUT_NAME=AutoCrate-Optimized.exe
    ) else if "!compile_choice!"=="4" (
        echo Building debug version...
        !PYINSTALLER_CMD! --console --debug all --name AutoCrate-Debug main.py
        set OUTPUT_NAME=AutoCrate-Debug.exe
    ) else if "!compile_choice!"=="5" (
        echo Building portable version...
        !PYINSTALLER_CMD! --windowed --collect-all tkinter --collect-all numpy --name AutoCrate-Portable main.py
        set OUTPUT_NAME=AutoCrate-Portable.exe
    )
    
    if exist "dist\!OUTPUT_NAME!" (
        copy /Y "dist\!OUTPUT_NAME!" "!OUTPUT_NAME!" >nul 2>&1
        echo [SUCCESS] !OUTPUT_NAME! created!
    )
    
    if exist "build" rmdir /s /q "build"
    if exist "dist" rmdir /s /q "dist"
    
    pause
    goto menu

:invalid
    echo.
    echo [ERROR] Invalid option!
    timeout /t 2 >nul
    goto menu