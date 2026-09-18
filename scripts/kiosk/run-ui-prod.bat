@echo off
setlocal EnableExtensions

set "UI_PORT=%~1"
if "%UI_PORT%"=="" (
    echo ERROR: UI port required.
    exit /b 1
)

set "FRONTEND_DIR=%~dp0..\..\frontend"
pushd "%FRONTEND_DIR%"
if errorlevel 1 (
    echo ERROR: frontend directory not found: %FRONTEND_DIR%
    exit /b 1
)

if not exist "dist\index.html" (
    echo Building frontend...
    call npm run build
    if errorlevel 1 (
        popd
        exit /b 1
    )
)

if not defined WINDOW_TITLE_UI set "WINDOW_TITLE_UI=LED Grid UI"

start /min "%WINDOW_TITLE_UI%" cmd /c "npm run preview -- --host 127.0.0.1 --port %UI_PORT% --strictPort"
popd
exit /b 0
