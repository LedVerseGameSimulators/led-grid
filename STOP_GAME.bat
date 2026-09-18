@echo off
setlocal EnableExtensions
cd /d "%~dp0"

set "QUIET=%~1"
if /i not "%QUIET%"=="/quiet" (
  title LED Grid - Stopping
  echo.
  echo ========================================
  echo   LED GRID - Stopping game
  echo ========================================
  echo.
)

REM Kill by window titles started by START_GAME.bat
taskkill /FI "WINDOWTITLE eq LED Grid API*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq LED Grid ws_bridge*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq LED Grid UI*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq LED Grid Frontend*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Activerse Kiosk Exit*" /T /F >nul 2>&1
REM Older titles from previous START_GAME.bat versions
taskkill /FI "WINDOWTITLE eq LED Grid - Floor Engine*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq LED Grid - Display Bridge*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq LED Grid - Game Screen*" /T /F >nul 2>&1

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\kiosk\kill-kiosk-browser.ps1" -ProfileSlug grid

REM Also free ports (works even if window titles differ)
powershell -NoProfile -Command ^
  "foreach ($p in 8003,8769,5176) { Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue } }" >nul 2>&1

if /i "%QUIET%"=="/quiet" (
  endlocal
  exit /b 0
)

echo.
echo LED Grid stopped. Ports 8003 / 8769 / 5176 are free.
echo You can close this window.
echo.
pause
endlocal
