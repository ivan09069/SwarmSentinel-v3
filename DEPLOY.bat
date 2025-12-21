@echo off
REM SwarmSentinel v3 - One-Click Deploy to Railway
REM Run this script to deploy your bot

echo ========================================
echo SwarmSentinel v3 - Railway Deployment
echo ========================================
echo.

cd /d "%~dp0"

echo [1/4] Logging into Railway...
echo (This will open your browser - authenticate there)
call railway login

if %ERRORLEVEL% neq 0 (
    echo ERROR: Railway login failed
    pause
    exit /b 1
)

echo.
echo [2/4] Creating new Railway project...
call railway init

echo.
echo [3/4] Setting environment variables...
echo.
echo IMPORTANT: You need to set your XAI_API_KEY
echo.
set /p XAI_KEY="Enter your XAI API key (starts with xai-): "
call railway variables set XAI_API_KEY=%XAI_KEY%
call railway variables set SIM_MODE=True
call railway variables set POLL_INTERVAL=60

echo.
echo [4/4] Deploying...
call railway up

echo.
echo ========================================
echo DEPLOYMENT COMPLETE!
echo ========================================
echo.
echo Next steps:
echo 1. Run: railway logs --tail
echo 2. When ready for live: railway variables set SIM_MODE=False
echo 3. Dashboard: railway open
echo.
pause
