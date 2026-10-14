@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0launch-demo.ps1" %*
if errorlevel 1 (
    echo.
    echo The demo could not start. Review the error above.
    pause
    exit /b 1
)
