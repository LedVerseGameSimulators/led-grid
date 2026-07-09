@echo off
REM Start Grid (Floor Is Lava) dev stack (API 8003, ws_bridge 8769, UI 5176).
REM NOTE: This game lives inside activerse_final_changes\led-grid\
setlocal
cd /d "%~dp0.."

echo ==^> LED Grid dev stack from %CD%

start "LED Grid API" cmd /k "cd /d %CD% && set USE_SERIAL_HD=1 && python -m uvicorn api.main:app --host 0.0.0.0 --port 8003"
timeout /t 2 /nobreak >nul
start "LED Grid ws_bridge" cmd /k "cd /d %CD% && set API_PORT=8003 && set WS_BRIDGE_PORT=8769 && python ws_bridge.py"
timeout /t 2 /nobreak >nul
start "LED Grid Frontend" cmd /k "cd /d %CD%\frontend && npm run dev"

echo.
echo Grid ready:
echo   UI:        http://localhost:5176
echo   API:       http://localhost:8003
echo   ws_bridge: http://localhost:8769
echo.
echo Close the three command windows to stop the stack.
endlocal
