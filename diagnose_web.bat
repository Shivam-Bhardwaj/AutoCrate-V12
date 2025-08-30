@echo off
echo.
echo ============================================================
echo   AutoCrate V12 - Web Server Diagnostic
echo ============================================================
echo.

echo [1/5] Checking if web server is responding...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:3000' -TimeoutSec 2 -UseBasicParsing; Write-Host '[OK] Web server is responding - Status:' $response.StatusCode } catch { Write-Host '[STUCK] Web server not responding' }"

echo.
echo [2/5] Checking Next.js processes...
tasklist /fi "imagename eq node.exe" /fo table 2>nul | find "node.exe" >nul && echo [RUNNING] Node.js processes found || echo [NONE] No Node.js processes

echo.
echo [3/5] Checking port 3000...
netstat -an | findstr ":3000" >nul && echo [OCCUPIED] Port 3000 is in use || echo [FREE] Port 3000 is available

echo.
echo [4/5] Checking for compilation issues in web directory...
cd web
if exist ".next\trace" (
    echo [INFO] Found .next\trace - checking latest build...
    dir .next\trace /od /b | tail -1
) else (
    echo [INFO] No trace files found
)

if exist "next.config.js" (
    echo [INFO] Found next.config.js - checking config...
    findstr "timeout" next.config.js >nul && echo [WARNING] Custom timeout in config || echo [OK] Standard config
) else (
    echo [INFO] No custom Next.js config
)

echo.
echo [5/5] Testing direct Next.js start...
echo Trying to start Next.js directly (will timeout in 10 seconds)...
timeout 10 npx next dev --port 3001 || echo [RESULT] Next.js test completed

cd ..

echo.
echo ============================================================
echo   DIAGNOSTIC COMPLETE
echo ============================================================
echo.
echo SOLUTIONS:
echo.
echo If web server is stuck compiling:
echo   1. Close the web server window (Ctrl+C)
echo   2. Run: dev_suite.bat
echo   3. Choose Option 6 (Clean Project) to clear cache
echo   4. Choose Option 2 (Start Web Server) again
echo.
echo If compilation is just slow:
echo   - Wait 1-2 minutes for initial compilation
echo   - Next.js compiles pages on first access
echo   - Try opening http://localhost:3000 in browser
echo.
pause