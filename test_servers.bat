@echo off
echo.
echo ============================================================
echo           AutoCrate V12 - Server Status Test                
echo ============================================================
echo.

echo Testing if servers are running...
echo.

echo [1/2] Testing API Server (port 5000)...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:5000' -TimeoutSec 3 -UseBasicParsing; Write-Host 'API Server: RUNNING (Status:' $response.StatusCode ')' } catch { Write-Host 'API Server: NOT RUNNING' }"

echo.
echo [2/2] Testing Web Server (port 3000)...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:3000' -TimeoutSec 3 -UseBasicParsing; Write-Host 'Web Server: RUNNING (Status:' $response.StatusCode ')' } catch { Write-Host 'Web Server: NOT RUNNING' }"

echo.
echo ============================================================
echo   SERVER STATUS CHECK COMPLETE
echo ============================================================
echo.
echo If servers are running:
echo - API Server: http://localhost:5000
echo - Web Server: http://localhost:3000
echo.
pause