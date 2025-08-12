@echo off
REM Windows batch file to fix competing session errors

echo ============================================================
echo FIXING COMPETING IB GATEWAY SESSIONS
echo ============================================================
echo.

REM Kill all Python processes
echo Step 1: Killing all Python processes...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM python3.exe 2>nul
taskkill /F /IM pythonw.exe 2>nul

echo.
echo Step 2: Waiting for cleanup...
timeout /t 3 /nobreak >nul

echo.
echo Step 3: Testing connection...
python debug_stock_price.py

echo.
echo ============================================================
echo If the test succeeded, you can now run your scripts.
echo If it failed, try restarting IB Gateway.
echo ============================================================
pause