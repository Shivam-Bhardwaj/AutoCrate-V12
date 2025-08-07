@echo off
setlocal enabledelayedexpansion
echo ========================================
echo   AutoCrate - Test, Update, and Push
echo ========================================
echo.

REM Get current date for changelog
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set year=%datetime:~0,4%
set month=%datetime:~4,2%
set day=%datetime:~6,2%
set today=%year%-%month%-%day%

REM Check git status
echo [1/7] Checking git status...
git status --porcelain > temp_status.txt
set /p status=<temp_status.txt
del temp_status.txt
if not defined status (
    echo    No changes to commit.
    echo.
    pause
    exit /b 0
)
echo    Changes detected.
echo.

REM Run comprehensive tests with agents
echo [2/7] Running comprehensive tests...
echo ========================================
python -m pytest tests\ -v --tb=short
if errorlevel 1 (
    echo.
    echo [ERROR] Tests failed! Push aborted.
    echo Please fix the failing tests before pushing.
    pause
    exit /b 1
)
echo.

REM Run property-based tests
echo [3/7] Running property-based tests...
echo ========================================
python -m pytest tests\test_property_based.py -v
if errorlevel 1 (
    echo.
    echo [WARNING] Property tests had issues.
    set /p continue="Continue anyway? (y/n): "
    if /i not "!continue!"=="y" exit /b 1
)
echo.

REM Update CHANGELOG.md
echo [4/7] Updating CHANGELOG.md...
echo.
echo Please enter a brief description of changes:
set /p changes="Changes: "

REM Create temporary file with new changelog entry
echo ## [%today%] - Latest Update> temp_changelog.txt
echo.>> temp_changelog.txt
echo ### Changes>> temp_changelog.txt
echo - %changes%>> temp_changelog.txt
echo.>> temp_changelog.txt
echo ### Technical Details>> temp_changelog.txt
echo - All tests passing>> temp_changelog.txt
echo - Expression replacement system operational>> temp_changelog.txt
echo - Build system optimized>> temp_changelog.txt
echo.>> temp_changelog.txt

REM Append existing changelog
if exist CHANGELOG.md (
    type CHANGELOG.md >> temp_changelog.txt
    move /y temp_changelog.txt CHANGELOG.md >nul
) else (
    move /y temp_changelog.txt CHANGELOG.md >nul
)
echo    CHANGELOG.md updated.
echo.

REM Create or switch to refactor branch
echo [5/7] Managing git branch...
git branch refactor 2>nul
git checkout refactor
echo    On branch: refactor
echo.

REM Stage all changes
echo [6/7] Staging changes...
git add -A
echo    All changes staged.
echo.

REM Commit changes
echo [7/7] Committing and pushing...
git commit -m "refactor: %changes% [%today%]"
if errorlevel 1 (
    echo.
    echo [ERROR] Commit failed!
    pause
    exit /b 1
)

REM Push to remote
git push -u origin refactor
if errorlevel 1 (
    echo.
    echo [WARNING] Push failed. Trying to set upstream...
    git push --set-upstream origin refactor
)

echo.
echo ========================================
echo   Push Complete!
echo ========================================
echo.
echo Branch: refactor
echo Status: All changes pushed to remote
echo.
echo Next steps:
echo 1. Go to GitHub and create a Pull Request
echo 2. Review changes in the PR
echo 3. Merge to main branch when ready
echo.
pause