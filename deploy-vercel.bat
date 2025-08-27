@echo off
setlocal

echo.
echo ========================================
echo      AutoCrate V12 Vercel Deploy
echo ========================================
echo.

REM Navigate to the web directory
cd web

REM Set production environment variables for the build
echo Creating production environment file...
echo NEXT_PUBLIC_API_URL=https://adequate-patience-production.up.railway.app/api > .env.production.local

echo.
echo Deploying to Vercel for production...
echo.

REM Run the Vercel deployment command
REM The Vercel CLI will guide you through the setup on the first run.
vercel --prod

REM Clean up the local environment file
del .env.production.local

echo.
echo ========================================
echo          Deployment Complete
echo ========================================
echo.
echo Your app should be live at your Vercel URL.
echo.

endlocal
pause