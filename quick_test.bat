@echo off
setlocal enabledelayedexpansion
echo ========================================
echo   AutoCrate - Quick Test Generator
echo ========================================
echo.

REM Clean expressions folder first
echo [1/3] Cleaning expressions folder...
if exist "expressions" (
    for /f %%i in ('dir /b "expressions\*.exp" 2^>nul') do del "expressions\%%i" 2>nul
    if exist "expressions\quick_test" (
        rmdir /s /q "expressions\quick_test" 2>nul
        mkdir "expressions\quick_test"
    )
) else (
    mkdir "expressions"
    mkdir "expressions\quick_test"
)
echo    Expressions folder cleaned.
echo.

REM Run quick test to generate expressions
echo [2/3] Generating quick test expressions...
echo ========================================
python scripts\quick_test.py
if errorlevel 1 (
    echo.
    echo [ERROR] Quick test failed!
    pause
    exit /b 1
)
echo.

REM Show generated files
echo [3/3] Generated expression files:
echo ========================================
set count=0
for /f %%i in ('dir /b "expressions\quick_test\*.exp" 2^>nul') do (
    set /a count+=1
    echo    !count!. %%i
)

if !count! equ 0 (
    echo    [WARNING] No expression files were generated!
) else (
    echo.
    echo    Total: !count! expression files generated
)

echo.
echo ========================================
echo   Quick Test Complete!
echo ========================================
echo.
pause