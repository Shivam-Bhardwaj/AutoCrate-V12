@echo off
setlocal enabledelayedexpansion
echo ===============================
echo   AutoCrate - Deploy Project
echo ===============================
echo.

REM Check if executable exists
if not exist "dist\AutoCrate.exe" (
    echo [ERROR] No executable found! Run 'build.bat' first.
    pause
    exit /b 1
)

echo [1/5] Pre-deployment validation...
echo ==================================
python quick_test_parallel.py
if errorlevel 1 (
    echo [ERROR] Tests failed! Deploy aborted.
    pause
    exit /b 1
)

echo.
echo [2/5] Cleaning up project...
echo ============================
REM Remove development artifacts
if exist "__pycache__" rmdir /s /q "__pycache__" 2>nul
if exist "build" rmdir /s /q "build" 2>nul
find . -name "*.pyc" -delete 2>nul
find . -name "__pycache__" -type d -exec rmdir /s /q {} + 2>nul

REM Clean old logs (keep recent ones)
if exist "logs" (
    echo Cleaning old log files...
    forfiles /p logs /m *.log /d -7 /c "cmd /c del @path" 2>nul
    forfiles /p logs /m *.json /d -7 /c "cmd /c del @path" 2>nul
)

echo [3/5] Updating version info...
echo ==============================
for /f "tokens=2 delims= " %%a in ('findstr "## \[" CHANGELOG.md') do (
    set version=%%a
    goto version_found
)
:version_found
echo Current version: %version%

echo.
echo [4/5] Git operations...
echo ======================
echo Checking git status...
git status --porcelain

echo.
echo Staging all changes...
git add .

echo.
echo Creating commit...
git commit -m "v%version%: Production build ready for deployment

🚀 Generated with optimized build pipeline
🧪 All tests passing
📦 Executable: dist/AutoCrate.exe

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

if errorlevel 1 (
    echo [WARNING] Commit failed - possibly no changes
) else (
    echo [SUCCESS] Commit created
)

echo.
echo [5/5] Final deployment checklist...
echo ==================================
echo ✅ Tests passed
echo ✅ Executable built: dist\AutoCrate.exe
echo ✅ Project cleaned
echo ✅ Changes committed

echo.
echo DEPLOYMENT OPTIONS:
echo 1. Push to repository: git push origin main
echo 2. Create release package
echo 3. Deploy executable to production

echo.
set /p choice="Push to repository now? (y/n): "
if /i "%choice%"=="y" (
    echo.
    echo Pushing to repository...
    git push origin main
    if errorlevel 1 (
        echo [ERROR] Push failed! Check network/permissions.
    ) else (
        echo [SUCCESS] Deployed to repository!
    )
) else (
    echo [INFO] Skipped repository push.
)

echo.
echo [SUCCESS] Deploy process completed!
echo.
echo Next steps:
echo - Test the executable: dist\AutoCrate.exe
echo - Create release documentation if needed
echo - Deploy to production environment
echo.
pause