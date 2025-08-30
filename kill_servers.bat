@echo off
echo.
echo ============================================================
echo   AutoCrate V12 - Kill All Servers
echo ============================================================
echo.

echo Killing all Node.js processes...
taskkill /f /im node.exe 2>nul
if errorlevel 1 (
    echo [INFO] No Node.js processes found to kill
) else (
    echo [OK] Node.js processes terminated
)

echo.
echo Killing Python API servers on common ports...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5000"') do (
    echo Killing process %%a on port 5000...
    taskkill /f /pid %%a 2>nul
)

for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000"') do (
    echo Killing process %%a on port 8000...
    taskkill /f /pid %%a 2>nul
)

echo.
echo Waiting 2 seconds...
timeout /t 2 >nul

echo.
echo Checking port status after cleanup...
netstat -an | findstr ":3000" >nul && echo [OCCUPIED] Port 3000: Still in use || echo [FREE] Port 3000: Available
netstat -an | findstr ":5000" >nul && echo [OCCUPIED] Port 5000: Still in use || echo [FREE] Port 5000: Available
netstat -an | findstr ":8000" >nul && echo [OCCUPIED] Port 8000: Still in use || echo [FREE] Port 8000: Available

echo.
echo ============================================================
echo   SERVER CLEANUP COMPLETE
echo ============================================================
echo.
echo All servers have been stopped.
echo You can now restart them using dev_suite.bat
echo.
pause