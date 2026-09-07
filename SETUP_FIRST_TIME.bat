@echo off
REM One-time tech setup — NOT for daily operators.
REM After this succeeds once, operators only use START_GAME.bat / STOP_GAME.bat.
setlocal EnableExtensions
cd /d "%~dp0"
title LED Game - First-time setup

echo.
echo ==========================================
echo   FIRST TIME SETUP (tech only)
echo   Folder: %CD%
echo ==========================================
echo.

where git >nul 2>&1
if errorlevel 1 (
  echo ERROR: Install Git for Windows first.
  goto :fail
)

where python >nul 2>&1
if errorlevel 1 (
  if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    set "PATH=%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python311\Scripts;%PATH%"
  ) else (
    echo ERROR: Install Python 3.11 and tick "Add to PATH".
    goto :fail
  )
)

where npm >nul 2>&1
if errorlevel 1 (
  echo ERROR: Install Node.js LTS from https://nodejs.org
  goto :fail
)

echo Ensuring Git LFS is ready and level files are downloaded...
git lfs install
git lfs pull
if errorlevel 1 (
  echo WARNING: git lfs pull reported an error. Level files may be incomplete.
)

echo Installing Python packages...
python -m pip install -r "api\requirements.txt"
if errorlevel 1 goto :fail

echo Installing frontend packages...
pushd frontend
call npm install
if errorlevel 1 (
  popd
  goto :fail
)
popd

if not exist "frontend\.env" (
  if exist "frontend\.env.example" (
    copy /Y "frontend\.env.example" "frontend\.env" >nul
    echo Created frontend\.env — confirm VITE_RFID_API_URL points at the RFID PC.
  )
)

echo.
echo SETUP COMPLETE for this game.
echo Next: double-click START_GAME.bat
echo.
pause
exit /b 0

:fail
echo.
echo SETUP FAILED. Fix the error above, then run this again.
pause
exit /b 1
