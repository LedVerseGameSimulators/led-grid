@echo off
setlocal EnableExtensions
cd /d "%~dp0"
set "ROOT=%CD%"

if not defined ACTIVERSE_KIOSK set "ACTIVERSE_KIOSK=1"

title LED Grid - Starting
echo.
echo ========================================
echo   LED GRID - Starting game
echo   Mode: HARDWARE + simulator
echo ========================================
echo.

where python >nul 2>&1
if errorlevel 1 (
    if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
        set "PATH=%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python311\Scripts;%PATH%"
    ) else (
        echo ERROR: Python not found. Ask tech to run SETUP_FIRST_TIME.bat
        goto :fail
    )
)

where npm >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found. Ask tech to run SETUP_FIRST_TIME.bat
    goto :fail
)

if not exist "games\setting\led_parameter.dat" (
    echo ERROR: Floor settings missing: games\setting\led_parameter.dat
    goto :fail
)

echo Checking Python packages...
python -c "import fastapi, uvicorn, httpx, serial" >nul 2>&1
if errorlevel 1 (
    echo Installing Python packages - first time...
    python -m pip install -r "api\requirements.txt"
    if errorlevel 1 goto :fail
)

if not exist "frontend\node_modules" (
    echo First run: installing frontend packages...
    pushd frontend
    call npm install
    if errorlevel 1 (
      popd
      goto :fail
    )
    popd
)

if not exist "frontend\.env" (
    if exist "frontend\.env.example" (
        copy /Y "frontend\.env.example" "frontend\.env" >nul
        echo Created frontend\.env - confirm RFID IP if needed.
    )
)

echo Stopping any previous game windows...
call "%ROOT%\STOP_GAME.bat" /quiet
ping -n 3 127.0.0.1 >nul

echo Starting floor engine with HARDWARE mode (API port 8003)...
start "LED Grid API" /MIN /D "%ROOT%" cmd /k "call scripts\run-api-hardware.bat"
ping -n 4 127.0.0.1 >nul

echo Starting bridge (port 8769)...
start "LED Grid ws_bridge" /MIN /D "%ROOT%" cmd /k "set API_PORT=8003&& set WS_BRIDGE_PORT=8769&& python ws_bridge.py"
ping -n 3 127.0.0.1 >nul

echo Starting game UI (port 5176)...
set "WINDOW_TITLE_UI=LED Grid UI"
call "%ROOT%\scripts\kiosk\run-ui-prod.bat" 5176
if errorlevel 1 goto :fail
ping -n 5 127.0.0.1 >nul

echo Waiting for game UI...
set /a _tries=0

:wait_ui
set /a _tries+=1
powershell -NoProfile -Command "try { (Invoke-WebRequest -Uri 'http://127.0.0.1:5176/' -UseBasicParsing -TimeoutSec 2).StatusCode } catch { exit 1 }" >nul 2>&1
if not errorlevel 1 goto ui_ready
if %_tries% GEQ 30 goto ui_timeout
ping -n 2 127.0.0.1 >nul
goto wait_ui

:ui_timeout
echo WARNING: UI did not respond yet. Opening browser anyway.
goto check_hw

:ui_ready
echo UI is ready.

:check_hw
echo Checking hardware mode...
powershell -NoProfile -Command "try { $r = Invoke-RestMethod -Uri 'http://localhost:8003/hw-debug' -TimeoutSec 5; if ($r.use_serial_hd) { Write-Host 'HARDWARE MODE: ON' } else { Write-Host 'ERROR: HARDWARE MODE OFF - floor will stay dark'; exit 2 } } catch { Write-Host 'WARNING: could not confirm hardware mode yet'; exit 0 }"
if errorlevel 2 goto :fail

call "%ROOT%\scripts\kiosk\open-ui.bat" 5176 grid

echo.
echo ========================================
echo   LED GRID is running (HARDWARE)
echo   Open:  http://127.0.0.1:5176/
echo   Ctrl+Shift+K exits fullscreen kiosk
echo   To stop: double-click STOP_GAME.bat
echo ========================================
echo.
exit /b 0

:fail
echo.
echo START FAILED. See OPERATOR_GUIDE.md or run SETUP_FIRST_TIME.bat
pause
exit /b 1
