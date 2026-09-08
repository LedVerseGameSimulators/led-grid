@echo off
REM ============================================================
REM  LED Grid (Floor Is Lava) - Studio start script
REM ============================================================
setlocal EnableExtensions
cd /d "%~dp0"
set "ROOT=%CD%"

title LED Grid - Starting...
color 0A

echo.
echo  ========================================
echo   LED Grid  -  Floor Is Lava
echo   Starting game...
echo  ========================================
echo.

where python >nul 2>&1
if errorlevel 1 (
  if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    set "PATH=%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python311\Scripts;%PATH%"
  ) else (
    echo  [ERROR] Python not found. Ask tech to run SETUP_FIRST_TIME.bat
    goto :fail
  )
)

where npm >nul 2>&1
if errorlevel 1 (
  echo  [ERROR] Node.js / npm not found. Ask tech to run SETUP_FIRST_TIME.bat
  goto :fail
)

if not exist "games\setting\led_parameter.dat" (
  echo  [ERROR] Floor settings missing: games\setting\led_parameter.dat
  goto :fail
)

echo  Checking Python packages...
python -c "import fastapi, uvicorn, httpx, serial" >nul 2>&1
if errorlevel 1 goto :pip_install
goto :after_pip
:pip_install
echo  Installing Python packages - first time...
python -m pip install -r "api\requirements.txt"
if errorlevel 1 goto :fail
:after_pip

if not exist "frontend\node_modules\" goto :npm_install
goto :after_npm
:npm_install
echo  First run: installing UI packages...
pushd frontend
call npm install
if errorlevel 1 (
  popd
  goto :fail
)
popd
:after_npm

if not exist "frontend\.env" if exist "frontend\.env.example" (
  copy /Y "frontend\.env.example" "frontend\.env" >nul
  echo  Created frontend\.env - confirm RFID IP if needed.
)

echo  Stopping any previous LED Grid windows...
call "%~dp0STOP_GAME.bat" /quiet
ping -n 3 127.0.0.1 >nul

echo  [1/3] Starting floor / game engine (API, hardware on)...
start "LED Grid - Floor Engine" /D "%~dp0" cmd /k "set USE_SERIAL_HD=1&& python -m uvicorn api.main:app --host 0.0.0.0 --port 8003"
ping -n 3 127.0.0.1 >nul

echo  [2/3] Starting display bridge...
start "LED Grid - Display Bridge" /D "%~dp0" cmd /k "set API_PORT=8003&& set WS_BRIDGE_PORT=8769&& python ws_bridge.py"
ping -n 3 127.0.0.1 >nul

echo  [3/3] Starting game screen (UI)...
start "LED Grid - Game Screen" /D "%~dp0frontend" cmd /k "npm run dev"

echo.
echo  Waiting for the game screen...
ping -n 9 127.0.0.1 >nul

start "" "http://localhost:5176/"

echo.
echo  ========================================
echo   Game is starting: http://localhost:5176/
echo   To stop: double-click STOP_GAME.bat
echo  ========================================
echo.
pause >nul
endlocal
exit /b 0

:fail
echo.
echo  Start failed. See OPERATOR_GUIDE.md or run SETUP_FIRST_TIME.bat
pause >nul
endlocal
exit /b 1
