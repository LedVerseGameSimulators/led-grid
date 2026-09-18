@echo off
setlocal EnableExtensions

set "BROWSER_EXE="

if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" (
    set "BROWSER_EXE=%ProgramFiles%\Google\Chrome\Application\chrome.exe"
    goto :found
)

if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" (
    set "BROWSER_EXE=%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
    goto :found
)

if exist "%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe" (
    set "BROWSER_EXE=%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"
    goto :found
)

if exist "%ProgramFiles%\Microsoft\Edge\Application\msedge.exe" (
    set "BROWSER_EXE=%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"
    goto :found
)

for /f "delims=" %%I in ('where chrome 2^>nul') do (
    set "BROWSER_EXE=%%I"
    goto :found
)

for /f "delims=" %%I in ('where msedge 2^>nul') do (
    set "BROWSER_EXE=%%I"
    goto :found
)

echo ERROR: Chrome or Edge not found. Install Google Chrome or Microsoft Edge.
exit /b 1

:found
endlocal & set "BROWSER_EXE=%BROWSER_EXE%"
exit /b 0
