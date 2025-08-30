@echo off
setlocal enabledelayedexpansion
title AutoCrate V12 - Master Control

:menu
cls
echo ================================================================================
echo                         AutoCrate V12 - Master Control Panel
echo ================================================================================
echo.
echo   Development & Testing:
echo   [1] Start Local Development Server (Web)
echo   [2] Run Python Application (main.py)
echo   [3] Run Tests
echo   [A] Start Python API Server (Flask)
echo.
echo   Build & Deploy:
echo   [4] Build Executable (.exe)
echo   [C] Compile Local App (Advanced)
echo   [5] Deploy to Vercel
echo   [6] Build Web for Production
echo.
echo   Complete Actions:
echo   [S] Save All (Deploy + Git Push + Build Exe)
echo.
echo   Utilities:
echo   [7] Check Dependencies
echo   [8] Clean Build Files
echo   [9] View Logs
echo   [K] Kill All AutoCrate Servers
echo.
echo   [0] Exit
echo   [Q] Quit (Direct)
echo.
echo ================================================================================
set /p choice="Select an option (0-9, A, C, S, K, Q): "

if "%choice%"=="0" exit /b 0
if /i "%choice%"=="q" exit /b 0
if "%choice%"=="1" goto dev_server
if "%choice%"=="2" goto run_python
if "%choice%"=="3" goto run_tests
if /i "%choice%"=="a" goto api_server
if "%choice%"=="4" goto build_exe
if /i "%choice%"=="c" goto compile_local
if "%choice%"=="5" goto deploy_vercel
if "%choice%"=="6" goto build_web
if "%choice%"=="7" goto check_deps
if "%choice%"=="8" goto clean_build
if "%choice%"=="9" goto view_logs
if /i "%choice%"=="s" goto save_all
if /i "%choice%"=="k" goto kill_servers
goto invalid

:dev_server
    cls
    echo ================================================================================
    echo                      Starting Local Development Server
    echo ================================================================================
    echo.
    if not exist "web" (
        echo [ERROR] Web directory not found!
        pause
        goto menu
    )
    
    cd web
    
    REM Check if node_modules exists
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

:run_python
    cls
    echo ================================================================================
    echo                        Running Python Application
    echo ================================================================================
    echo.
    if not exist "main.py" (
        echo [ERROR] main.py not found!
        pause
        goto menu
    )
    
    echo Starting AutoCrate Python application...
    python main.py
    pause
    goto menu

:run_tests
    cls
    echo ================================================================================
    echo                             Run Tests
    echo ================================================================================
    echo.
    echo [1] Quick Test Suite (run_tests.py)
    echo [2] NX Expression Tests (test_nx_simple.py)
    echo [3] Full Test Suite (pytest)
    echo [4] Web Tests (npm test)
    echo [5] Back to Menu
    echo.
    set /p test_choice="Select test option (1-5): "
    
    if "!test_choice!"=="1" (
        cls
        echo Running quick test suite...
        echo.
        if exist "run_tests.py" (
            python run_tests.py
        ) else (
            echo [ERROR] run_tests.py not found!
        )
        pause
    ) else if "!test_choice!"=="2" (
        cls
        echo Running NX expression tests...
        echo.
        if exist "test_nx_simple.py" (
            python test_nx_simple.py
        ) else (
            echo [ERROR] test_nx_simple.py not found!
        )
        pause
    ) else if "!test_choice!"=="3" (
        cls
        echo Running full test suite with pytest...
        echo.
        python -m pytest tests/ -v --tb=short
        pause
    ) else if "!test_choice!"=="4" (
        cls
        echo Running web tests...
        echo.
        cd web
        call npm test
        cd ..
        pause
    )
    goto menu

:api_server
    cls
    echo ================================================================================
    echo                      Starting Python API Server (Flask)
    echo ================================================================================
    echo.
    if not exist "api_server.py" (
        echo [ERROR] api_server.py not found!
        pause
        goto menu
    )
    
    echo This server provides the exact desktop calculation engine to the web app
    echo.
    echo Starting Python API server...
    echo Server will run at: http://localhost:5000
    echo.
    echo To use with web app:
    echo   1. Keep this server running
    echo   2. Start the web dev server (Option 1)
    echo   3. The web app will automatically detect and use the Python API
    echo.
    echo Press Ctrl+C to stop the server.
    echo.
    python api_server.py
    pause
    goto menu

:build_exe
    cls
    echo ================================================================================
    echo                         Build Executable
    echo ================================================================================
    echo.
    echo This will create AutoCrate.exe
    echo.
    set /p confirm="Continue with build? (y/n): "
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
    echo [SUCCESS] Build completed!
    echo.
    echo Moving executable to root directory...
    if exist "dist\AutoCrate.exe" (
        copy /Y "dist\AutoCrate.exe" "AutoCrate.exe" >nul 2>&1
        if errorlevel 1 (
            echo [WARNING] Failed to copy AutoCrate.exe to root
        ) else (
            echo AutoCrate.exe copied to root directory
        )
    )
    
    echo.
    echo Cleaning up build directories...
    if exist "build" (
        rmdir /s /q "build"
        echo - Removed build/
    )
    if exist "dist" (
        rmdir /s /q "dist"
        echo - Removed dist/
    )
    
    echo.
    echo [COMPLETE] Executable available at: %cd%\AutoCrate.exe
    pause
    goto menu

:compile_local
    cls
    echo ================================================================================
    echo                      Compile Local App (Advanced Options)
    echo ================================================================================
    echo.
    echo Select compilation type:
    echo.
    echo [1] Standard Build (Same as Option 4 - Windowed .exe)
    echo [2] Console Build (With debug console)
    echo [3] Optimized Build (Smaller size, slower startup)
    echo [4] Debug Build (With debug symbols)
    echo [5] Portable Build (Include all dependencies)
    echo [6] Back to Menu
    echo.
    set /p compile_choice="Select compilation option (1-6): "
    
    if "!compile_choice!"=="6" goto menu
    if "!compile_choice!"=="1" goto compile_standard
    if "!compile_choice!"=="2" goto compile_console
    if "!compile_choice!"=="3" goto compile_optimized
    if "!compile_choice!"=="4" goto compile_debug
    if "!compile_choice!"=="5" goto compile_portable
    echo Invalid option!
    timeout /t 2 >nul
    goto compile_local

:compile_standard
    echo.
    echo Building standard windowed executable...
    echo.
    goto build_exe_common

:compile_console
    echo.
    echo Building console executable with debug output...
    echo.
    set BUILD_TYPE=console
    goto build_exe_common

:compile_optimized
    echo.
    echo Building optimized executable (may take longer)...
    echo.
    set BUILD_TYPE=optimized
    goto build_exe_common

:compile_debug
    echo.
    echo Building debug executable with symbols...
    echo.
    set BUILD_TYPE=debug
    goto build_exe_common

:compile_portable
    echo.
    echo Building portable executable with all dependencies...
    echo.
    set BUILD_TYPE=portable
    goto build_exe_common

:build_exe_common
    set /p confirm="Continue with compilation? (y/n): "
    if /i not "!confirm!"=="y" goto compile_local
    
    echo.
    echo Cleaning previous builds...
    if exist "build" rmdir /s /q "build"
    if exist "dist" rmdir /s /q "dist"
    
    echo.
    echo Compiling with PyInstaller...
    
    REM Base PyInstaller command
    set PYINSTALLER_CMD=python -m PyInstaller --noconfirm --onefile --distpath dist --workpath build --add-data "security;security" --add-data "autocrate;autocrate" --hidden-import security.input_validator --hidden-import security.file_manager --hidden-import security.windows_security --hidden-import security.auth_manager --hidden-import security.audit_logger --exclude-module pytest --exclude-module matplotlib
    
    REM Adjust command based on build type
    if "!BUILD_TYPE!"=="console" (
        set PYINSTALLER_CMD=!PYINSTALLER_CMD! --console --name AutoCrate-Console
        echo Building console version...
    ) else if "!BUILD_TYPE!"=="optimized" (
        set PYINSTALLER_CMD=!PYINSTALLER_CMD! --windowed --optimize 2 --strip --name AutoCrate-Optimized
        echo Building optimized version...
    ) else if "!BUILD_TYPE!"=="debug" (
        set PYINSTALLER_CMD=!PYINSTALLER_CMD! --console --debug all --name AutoCrate-Debug
        echo Building debug version...
    ) else if "!BUILD_TYPE!"=="portable" (
        set PYINSTALLER_CMD=!PYINSTALLER_CMD! --windowed --collect-all tkinter --collect-all numpy --name AutoCrate-Portable
        echo Building portable version...
    ) else (
        set PYINSTALLER_CMD=!PYINSTALLER_CMD! --windowed --name AutoCrate
        echo Building standard version...
    )
    
    REM Execute the build command
    !PYINSTALLER_CMD! main.py
    
    if errorlevel 1 (
        echo.
        echo [ERROR] Compilation failed!
        pause
        goto compile_local
    )
    
    echo.
    echo [SUCCESS] Compilation completed!
    echo.
    
    REM Copy executable to root based on build type
    if "!BUILD_TYPE!"=="console" (
        if exist "dist\AutoCrate-Console.exe" (
            copy /Y "dist\AutoCrate-Console.exe" "AutoCrate-Console.exe" >nul 2>&1
            echo AutoCrate-Console.exe copied to root directory
        )
    ) else if "!BUILD_TYPE!"=="optimized" (
        if exist "dist\AutoCrate-Optimized.exe" (
            copy /Y "dist\AutoCrate-Optimized.exe" "AutoCrate-Optimized.exe" >nul 2>&1
            echo AutoCrate-Optimized.exe copied to root directory
        )
    ) else if "!BUILD_TYPE!"=="debug" (
        if exist "dist\AutoCrate-Debug.exe" (
            copy /Y "dist\AutoCrate-Debug.exe" "AutoCrate-Debug.exe" >nul 2>&1
            echo AutoCrate-Debug.exe copied to root directory
        )
    ) else if "!BUILD_TYPE!"=="portable" (
        if exist "dist\AutoCrate-Portable.exe" (
            copy /Y "dist\AutoCrate-Portable.exe" "AutoCrate-Portable.exe" >nul 2>&1
            echo AutoCrate-Portable.exe copied to root directory
        )
    ) else (
        if exist "dist\AutoCrate.exe" (
            copy /Y "dist\AutoCrate.exe" "AutoCrate.exe" >nul 2>&1
            echo AutoCrate.exe copied to root directory
        )
    )
    
    echo.
    echo Cleaning up build directories...
    if exist "build" (
        rmdir /s /q "build"
        echo - Removed build/
    )
    if exist "dist" (
        rmdir /s /q "dist"
        echo - Removed dist/
    )
    
    echo.
    echo [COMPLETE] Executable compilation finished!
    echo Check the root directory for your compiled application.
    echo.
    set BUILD_TYPE=
    pause
    goto menu

:deploy_vercel
    cls
    echo ================================================================================
    echo                    Automatic Deployment to Vercel
    echo ================================================================================
    echo.
    echo Starting automatic deployment process...
    echo No permissions or prompts required - just deploying!
    echo.
    
    REM Run the automatic deployment script
    if exist "deploy_automatic.bat" (
        call deploy_automatic.bat
    ) else (
        echo [ERROR] deploy_automatic.bat not found!
        echo Creating deployment script...
        pause
        goto menu
    )
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

:check_deps
    cls
    echo ================================================================================
    echo                        Check Dependencies
    echo ================================================================================
    echo.
    
    echo Python Dependencies:
    echo --------------------
    python --version
    echo.
    pip list | findstr /i "numpy pandas tkinter pyinstaller pytest"
    
    echo.
    echo Node.js Dependencies:
    echo ---------------------
    node --version
    npm --version
    echo.
    
    if exist "web\package.json" (
        cd web
        echo Web dependencies installed:
        npm list --depth=0
        cd ..
    )
    
    pause
    goto menu

:clean_build
    cls
    echo ================================================================================
    echo                         Clean Build Files
    echo ================================================================================
    echo.
    
    echo Cleaning Python build files...
    if exist "build" (
        rmdir /s /q "build"
        echo - Removed build/
    )
    if exist "dist" (
        rmdir /s /q "dist"
        echo - Removed dist/
    )
    if exist "__pycache__" (
        rmdir /s /q "__pycache__"
        echo - Removed __pycache__/
    )
    if exist ".pytest_cache" (
        rmdir /s /q ".pytest_cache"
        echo - Removed .pytest_cache/
    )
    
    echo.
    echo Cleaning web build files...
    if exist "web\.next" (
        cd web
        rmdir /s /q ".next"
        echo - Removed web/.next/
        if exist "out" (
            rmdir /s /q "out"
            echo - Removed web/out/
        )
        cd ..
    )
    
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
    echo.
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
        if exist "autocrate.log" (
            type autocrate.log | more
        ) else (
            echo No log files found.
        )
        pause
    ) else if "!log_choice!"=="2" (
        for %%f in (*.log logs\*.log) do (
            echo.
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

:save_all
    cls
    echo ================================================================================
    echo                           Save All - Complete Workflow
    echo ================================================================================
    echo.
    echo This will perform a complete save and deployment workflow:
    echo.
    echo   1. Git: Add, commit, and push all changes
    echo   2. Vercel: Deploy web application to production
    echo   3. Build: Create Windows executable (.exe)
    echo.
    echo WARNING: This will commit ALL current changes to git!
    echo Make sure you have reviewed your changes before proceeding.
    echo.
    set /p confirm="Continue with complete workflow? (y/n): "
    if /i not "!confirm!"=="y" goto menu
    
    echo.
    echo ================================================================================
    echo                              STEP 1: Git Operations
    echo ================================================================================
    echo.
    
    REM Check if we're in a git repository
    git status >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Not a git repository or git not installed!
        echo Skipping git operations...
        goto save_all_deploy
    )
    
    echo Checking git status...
    git status --porcelain > temp_git_status.txt
    
    REM Check if there are any changes to commit
    for /f %%i in (temp_git_status.txt) do set HAS_CHANGES=1
    del temp_git_status.txt 2>nul
    
    if not defined HAS_CHANGES (
        echo No changes to commit. Repository is clean.
    ) else (
        echo Adding all changes to git...
        git add .
        
        if errorlevel 1 (
            echo [ERROR] Failed to add files to git!
            pause
            goto menu
        )
        
        echo.
        echo Creating commit with timestamp...
        set COMMIT_MSG=AutoCrate V12 - Save All deployment %date% %time%
        git commit -m "!COMMIT_MSG!"
        
        if errorlevel 1 (
            echo [ERROR] Failed to commit changes!
            pause
            goto menu
        )
        
        echo.
        echo Pushing to remote repository...
        git push
        
        if errorlevel 1 (
            echo [WARNING] Failed to push to remote repository.
            echo Continuing with deployment anyway...
        ) else (
            echo [SUCCESS] Git push completed!
        )
    )
    
:save_all_deploy
    echo.
    echo ================================================================================
    echo                            STEP 2: Vercel Deployment
    echo ================================================================================
    echo.
    
    echo Starting Vercel deployment...
    call deploy_automatic.bat
    
    if errorlevel 1 (
        echo [ERROR] Vercel deployment failed!
        echo Continuing with executable build...
    ) else (
        echo [SUCCESS] Vercel deployment completed!
    )

:save_all_build
    echo.
    echo ================================================================================
    echo                           STEP 3: Build Executable
    echo ================================================================================
    echo.
    
    echo Building Windows executable...
    echo Cleaning previous builds...
    if exist "build" rmdir /s /q "build"
    if exist "dist" rmdir /s /q "dist"
    
    echo.
    echo Compiling with PyInstaller...
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
        echo [ERROR] Executable build failed!
        pause
        goto menu
    )
    
    echo.
    echo Moving executable to root directory...
    if exist "dist\AutoCrate.exe" (
        copy /Y "dist\AutoCrate.exe" "AutoCrate.exe" >nul 2>&1
        if errorlevel 1 (
            echo [WARNING] Failed to copy AutoCrate.exe to root
        ) else (
            echo AutoCrate.exe copied to root directory
        )
    )
    
    echo.
    echo Cleaning up build directories...
    if exist "build" (
        rmdir /s /q "build"
        echo - Removed build/
    )
    if exist "dist" (
        rmdir /s /q "dist"
        echo - Removed dist/
    )
    
    echo.
    echo ================================================================================
    echo                             WORKFLOW COMPLETE!
    echo ================================================================================
    echo.
    echo Summary:
    if defined HAS_CHANGES (
        echo   ✓ Git: Changes committed and pushed
    ) else (
        echo   ✓ Git: Repository was already clean
    )
    echo   ✓ Vercel: Web application deployed
    echo   ✓ Build: AutoCrate.exe created
    echo.
    echo Your complete AutoCrate V12 project has been:
    echo   - Saved to git repository
    echo   - Deployed to Vercel (web)
    echo   - Compiled to executable (desktop)
    echo.
    echo All components are now synchronized and ready for distribution!
    echo.
    pause
    goto menu

:kill_servers
    cls
    echo ================================================================================
    echo                      Kill All AutoCrate Servers
    echo ================================================================================
    echo.
    
    echo Checking for running processes...
    echo.
    
    REM Kill Node.js processes (development servers)
    echo Stopping Node.js servers (port 3000-3010)...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000') do (
        echo Killing process on port 3000 (PID: %%a)
        taskkill /F /PID %%a 2>nul
    )
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3001') do (
        echo Killing process on port 3001 (PID: %%a)
        taskkill /F /PID %%a 2>nul
    )
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3002') do (
        echo Killing process on port 3002 (PID: %%a)
        taskkill /F /PID %%a 2>nul
    )
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3003') do (
        echo Killing process on port 3003 (PID: %%a)
        taskkill /F /PID %%a 2>nul
    )
    
    REM Kill Python processes running main.py or AutoCrate
    echo.
    echo Stopping Python AutoCrate processes...
    taskkill /F /IM python.exe /FI "WINDOWTITLE eq AutoCrate*" 2>nul
    taskkill /F /IM pythonw.exe /FI "WINDOWTITLE eq AutoCrate*" 2>nul
    taskkill /F /IM AutoCrate.exe 2>nul
    
    REM Kill any npm or node processes
    echo.
    echo Stopping npm and node processes...
    tasklist | findstr /i "node.exe" >nul 2>&1
    if not errorlevel 1 (
        set /p confirm="Kill ALL node.exe processes? This may affect other applications (y/n): "
        if /i "!confirm!"=="y" (
            taskkill /F /IM node.exe 2>nul
            echo Node.exe processes terminated.
        )
    )
    
    REM Clean up zombie processes
    echo.
    echo Cleaning up zombie processes...
    wmic process where "name='node.exe' and commandline like '%%autocrate%%'" delete 2>nul
    wmic process where "name='python.exe' and commandline like '%%autocrate%%'" delete 2>nul
    
    REM Check if any processes are still running
    echo.
    echo Verifying shutdown...
    netstat -ano | findstr :3000 >nul 2>&1
    if not errorlevel 1 (
        echo [WARNING] Some processes on port 3000 may still be running.
    ) else (
        echo [SUCCESS] Port 3000 is free.
    )
    
    netstat -ano | findstr :3001 >nul 2>&1
    if not errorlevel 1 (
        echo [WARNING] Some processes on port 3001 may still be running.
    ) else (
        echo [SUCCESS] Port 3001 is free.
    )
    
    echo.
    echo [COMPLETE] Server cleanup finished.
    echo.
    echo Tip: If ports are still blocked, you may need to restart your computer.
    pause
    goto menu

:invalid
    echo.
    echo [ERROR] Invalid option!
    timeout /t 2 >nul
    goto menu