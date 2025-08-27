@echo off
setlocal enabledelayedexpansion

:menu
cls
echo ========================================
echo        AutoCrate V12 - Master Control
echo ========================================
echo.
echo [1] Run Local Development Server
echo [2] Run Tests
echo [3] Build Application
echo [4] Deploy to Vercel
echo [5] Run Production Build
echo [6] View Logs
echo [7] Exit
echo.
set /p choice="Select an option (1-7): "

if "%choice%"=="1" goto option_1
if "%choice%"=="2" goto option_2
if "%choice%"=="3" goto option_3
if "%choice%"=="4" goto option_4
if "%choice%"=="5" goto option_5
if "%choice%"=="6" goto option_6
if "%choice%"=="7" goto option_7
goto invalid

:option_1
    echo.
    echo ========================================
    echo    Starting Local Development Server
    echo ========================================
    echo.
    cd web
    echo Starting development server...
    echo Visit http://localhost:3000 in your browser.
    echo.
    npm run dev
    pause
    goto menu

:option_3
    echo.
    echo ========================================
    echo    Building Application
    echo ========================================
    echo.
    echo [1] Run tests before building
    echo [2] Build without tests
    echo [3] Back to Main Menu
    echo.
    set /p build_choice="Select build option (1-3): "
    
    if "!build_choice!"=="1" (
        echo.
        echo Running tests first...
        python quick_test_parallel.py
        if errorlevel 1 (
            echo.
            echo [ERROR] Tests failed! Build aborted.
            pause
            goto menu
        )
    )
    
    if not "!build_choice!"=="3" (
        echo.
        echo Building application...
        echo This may take a few minutes...
        echo.
        
        REM Clean previous build
        if exist "build" rmdir /s /q "build" 2>nul
        if exist "dist" rmdir /s /q "dist" 2>nul

        REM Build with PyInstaller
        python -m PyInstaller ^
            --noconfirm ^
            --onefile ^
            --windowed ^
            --name AutoCrate ^
            --distpath dist ^
            --workpath build ^
            --add-data "security;security" ^
            --hidden-import security ^
            --hidden-import security.input_validator ^
            --hidden-import security.file_manager ^
            --hidden-import security.windows_security ^
            --hidden-import security.auth_manager ^
            --hidden-import security.audit_logger ^
            --exclude-module pytest ^
            --exclude-module hypothesis ^
            --exclude-module matplotlib ^
            --exclude-module IPython ^
            main.py
            
        if errorlevel 1 (
            echo.
            echo [ERROR] Build failed!
        ) else (
            echo.
            echo [SUCCESS] Build completed successfully!
            echo Executable created in: %cd%\dist\AutoCrate.exe
        )
        pause
    )
    goto menu

:option_4
    echo.
    echo ========================================
    echo    Deploy to Vercel
    echo ========================================
    echo.
    echo This will deploy the web application to Vercel.
    echo.
    set /p confirm="Are you sure you want to deploy to production? (y/n): "
    
    if /i "!confirm!"=="y" (
        echo.
        echo Setting up production environment...
        cd web
        echo NEXT_PUBLIC_API_URL=https://adequate-patience-production.up.railway.app/api > .env.production.local
        
        echo.
        echo Deploying to Vercel...
        vercel --prod
:option_2
    echo.
    echo ========================================
    echo    Running Tests
    echo ========================================
    echo.
    echo [1] Run Quick Tests
    echo [2] Run Full Test Suite
    echo [3] Back to Main Menu
    echo.
    set /p test_choice="Select test option (1-3): "
    
    if "!test_choice!"=="1" (
        echo.
        echo Running quick tests...
        python quick_test_parallel.py
    ) else if "!test_choice!"=="2" (
        echo.
        echo Running full test suite...
        python -m pytest tests/
    )
    
    if not "!test_choice!"=="3" (
        echo.
        echo Tests completed. Press any key to continue...
        pause >nul
    )
    goto menu

:option_3
    echo.
    echo ========================================
    echo    Building Application
    echo ========================================
    echo.
    echo [1] Run tests before building
    echo [2] Build without tests
    echo [3] Back to Main Menu
    echo.
    set /p build_choice="Select build option (1-3): "
    
    if "!build_choice!"=="1" (
        echo.
        echo Running tests first...
        python quick_test_parallel.py
        if errorlevel 1 (
            echo.
            echo [ERROR] Tests failed! Build aborted.
            pause
            goto menu
        )
    )
    
    if not "!build_choice!"=="3" (
        echo.
        echo Building application...
        echo This may take a few minutes...
        echo.
        
        REM Clean previous build
        if exist "build" rmdir /s /q "build" 2>nul
        if exist "dist" rmdir /s /q "dist" 2>nul

        REM Build with PyInstaller
        python -m PyInstaller ^
            --noconfirm ^
            --onefile ^
            --windowed ^
            --name AutoCrate ^
            --distpath dist ^
            --workpath build ^
            --add-data "security;security" ^
            --hidden-import security ^
            --hidden-import security.input_validator ^
            --hidden-import security.file_manager ^
            --hidden-import security.windows_security ^
            --hidden-import security.auth_manager ^
            --hidden-import security.audit_logger ^
            --exclude-module pytest ^
            --exclude-module hypothesis ^
            --exclude-module matplotlib ^
            --exclude-module IPython ^
            main.py
            
        if errorlevel 1 (
            echo.
            echo [ERROR] Build failed!
        ) else (
            echo.
            echo [SUCCESS] Build completed successfully!
            echo Executable created in: %cd%\dist\AutoCrate.exe
        )
        pause
    )
    goto menu

:option_4
    echo.
    echo ========================================
    echo    Deploy to Vercel
    echo ========================================
    echo.
    echo This will deploy the web application to Vercel.
    echo.
    set /p confirm="Are you sure you want to deploy to production? (y/n): "
    
    if /i "!confirm!"=="y" (
        echo.
        echo Setting up production environment...
        cd web
        echo NEXT_PUBLIC_API_URL=https://adequate-patience-production.up.railway.app/api > .env.production.local
        
        echo.
        echo Deploying to Vercel...
        vercel --prod
        
        echo.
        echo Cleaning up...
        del .env.production.local
        cd ..
    )
    pause
    goto menu

:option_5
    echo.
    echo ========================================
    echo    Run Production Build
    echo ========================================
    echo.
    if not exist "dist\AutoCrate.exe" (
        echo [ERROR] No production build found. Please build the application first.
        pause
        goto menu
    )
    
    echo Starting production build...
    echo.
    start "" "dist\AutoCrate.exe"
    goto menu

:option_6
    echo.
    echo ========================================
    echo    View Application Logs
    echo ========================================
    echo.
    echo [1] View Web Logs (JSON format)
    echo [2] View API Logs
    echo [3] View All Log Files
    echo [4] Clear All Logs
    echo [5] Back to Main Menu
    echo.
    set /p log_choice="Select log option (1-5): "
    
    if "!log_choice!"=="1" (
        echo.
        echo Web application logs:
        if exist "api\logs\web_logs_*.json" (
            for %%f in (api\logs\web_logs_*.json) do (
                echo.
                echo === %%f ===
                type "%%f" | findstr /C:"ERROR" /C:"CRITICAL" /C:"WARN" 2>nul || echo No critical issues found
            )
        ) else (
            echo No web logs found. Start the application to generate logs.
        )
    ) else if "!log_choice!"=="2" (
        echo.
        echo API server logs:
        if exist "api\logs\web_logs.log" (
            type "api\logs\web_logs.log"
        ) else (
            echo No API logs found. Start the API server to generate logs.
        )
    ) else if "!log_choice!"=="3" (
        echo.
        echo All log files:
        if exist "api\logs" (
            dir "api\logs" /B
        ) else (
            echo No logs directory found.
        )
    ) else if "!log_choice!"=="4" (
        echo.
        set /p confirm_clear="Are you sure you want to clear all logs? (y/n): "
        if /i "!confirm_clear!"=="y" (
            if exist "api\logs" (
                del /Q "api\logs\*.*" 2>nul
                echo Logs cleared successfully.
            ) else (
                echo No logs to clear.
            )
        )
    )
    
    if not "!log_choice!"=="5" (
        echo.
        echo Press any key to continue...
        pause >nul
    )
    goto menu

:option_7
    exit /b 0
    
:invalid
    echo.
    echo Invalid option. Please try again.
    timeout /t 2 >nul
    goto menu
