@echo off
setlocal EnableExtensions

set "UI_PORT=%~1"
set "PROFILE=%~2"

if "%UI_PORT%"=="" (
    echo ERROR: UI port required.
    exit /b 1
)
if "%PROFILE%"=="" (
    echo ERROR: profile slug required.
    exit /b 1
)

set "UI_URL=http://127.0.0.1:%UI_PORT%/"

if "%ACTIVERSE_KIOSK%"=="0" (
    start "" "%UI_URL%"
    exit /b 0
)

call "%~dp0find-browser.bat"
if errorlevel 1 exit /b 1

set "KIOSK_PROFILE=%LOCALAPPDATA%\ActiverseKiosk\%PROFILE%"

wscript.exe "%~dp0run-hidden.vbs" "powershell.exe -NoProfile -ExecutionPolicy Bypass -File ""%~dp0kiosk-exit-listener.ps1"" -ProfileSlug %PROFILE%"

start "" "%BROWSER_EXE%" --kiosk --no-first-run --disable-session-crashed-bubble --disable-infobars --user-data-dir="%KIOSK_PROFILE%" "%UI_URL%"

exit /b 0
