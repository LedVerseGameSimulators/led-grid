@echo off
REM ============================================================
REM  LED Grid (Floor Is Lava) - Studio stop script
REM  Double-click to shut down the three game windows/ports.
REM ============================================================
setlocal EnableExtensions

set "QUIET=%~1"

if /I not "%QUIET%"=="/quiet" (
  title LED Grid - Stopping...
  echo.
  echo  Stopping LED Grid...
)

REM Close the named cmd windows started by START_GAME.bat
taskkill /FI "WINDOWTITLE eq LED Grid - Floor Engine*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq LED Grid - Display Bridge*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq LED Grid - Game Screen*" /F >nul 2>&1
REM Older / alternate titles from scripts\start-dev.bat
taskkill /FI "WINDOWTITLE eq LED Grid API*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq LED Grid ws_bridge*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq LED Grid Frontend*" /F >nul 2>&1

REM Also free the ports in case a process was left hanging
for %%P in (8003 8769 5176) do (
  for /f "tokens=5" %%A in ('netstat -ano ^| findstr ":%%P " ^| findstr "LISTENING"') do (
    taskkill /PID %%A /F >nul 2>&1
  )
)

if /I not "%QUIET%"=="/quiet" (
  echo  Done. LED Grid is stopped.
  echo.
  echo  Press any key to close.
  pause >nul
)

endlocal
exit /b 0
