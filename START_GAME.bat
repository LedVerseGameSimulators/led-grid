@echo off
REM ============================================================
REM  LED Grid (Floor Is Lava) - Studio start script
REM  Double-click this file to start the game on the LED floor.
REM  See OPERATOR_GUIDE.md for the short operator manual.
REM ============================================================
setlocal EnableExtensions
cd /d "%~dp0"

title LED Grid - Starting...
color 0A

echo.
echo  ========================================
echo   LED Grid  -  Floor Is Lava
echo   Starting game...
echo  ========================================
echo.

REM --- Pre-checks ---------------------------------------------------------
where python >nul 2>&1
if errorlevel 1 (
  echo  [ERROR] Python was not found on PATH.
  echo          Install Python 3.11 and tick "Add to PATH", then try again.
  goto :fail
)

where npm >nul 2>&1
if errorlevel 1 (
  echo  [ERROR] Node.js / npm was not found on PATH.
  echo          Install Node.js LTS from https://nodejs.org then try again.
  goto :fail
)

if not exist "games\setting\led_parameter.dat" (
  echo  [ERROR] Floor settings missing: games\setting\led_parameter
  echo          Copy the setting folder from the old ledplay install first.
  goto :fail
)

if not exist "frontend\node_modules\" (
  echo  First run: installing UI packages ^(one-time, may take a minute^)...
  pushd frontend
  call npm install
  if errorlevel 1 (
    echo  [ERROR] npm install failed.
    popd
    goto :fail
  )
  popd
  echo  UI packages ready.
  echo.
)

REM --- Stop any previous copy of this game --------------------------------
echo  Stopping any previous LED Grid windows...
call "%~dp0STOP_GAME.bat" /quiet
REM ping delay (timeout.exe fails if stdin is redirected)
ping -n 3 127.0.0.1 >nul

REM --- Start the three services -------------------------------------------
echo  [1/3] Starting floor / game engine ^(API, hardware on^)...
start "LED Grid - Floor Engine" /D "%~dp0" cmd /k "set USE_SERIAL_HD=1&& python -m uvicorn api.main:app --host 0.0.0.0 --port 8003"
ping -n 3 127.0.0.1 >nul

echo  [2/3] Starting display bridge...
start "LED Grid - Display Bridge" /D "%~dp0" cmd /k "set API_PORT=8003&& set WS_BRIDGE_PORT=8769&& python ws_bridge.py"
ping -n 3 127.0.0.1 >nul

echo  [3/3] Starting game screen ^(UI^)...
start "LED Grid - Game Screen" /D "%~dp0frontend" cmd /k "npm run dev"

echo.
echo  Waiting for the game screen to come up...
ping -n 9 127.0.0.1 >nul

start "" "http://localhost:5176/"

echo.
echo  ========================================
echo   Game is starting.
echo.
echo   Open on this PC:  http://localhost:5176/
echo.
echo   Three black windows will stay open -
echo   that is normal. Do NOT close them while
echo   guests are playing.
echo.
echo   To stop the game: double-click STOP_GAME.bat
echo   or close those three windows.
echo  ========================================
echo.
echo  Press any key to close this starter window
echo  ^(the game keeps running^).
pause >nul
endlocal
exit /b 0

:fail
echo.
echo  Start failed. See messages above.
echo  Press any key to close.
pause >nul
endlocal
exit /b 1
