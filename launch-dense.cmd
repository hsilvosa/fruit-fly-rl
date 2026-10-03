@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0launch-dense.ps1" %*
if errorlevel 1 (
    echo.
    echo The dense demo could not start. Review the error above.
    pause
    exit /b 1
)
