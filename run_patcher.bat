@echo off
chcp 65001 > nul
cd /d "%~dp0"
python patcher.py gui
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Failed to launch patcher.py with Python.
    echo Please make sure Python 3 is installed and available in PATH.
    pause
)
