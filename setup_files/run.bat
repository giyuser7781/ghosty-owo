@echo off
title GhoSty OwO V4.1
cd /d "%~dp0\.."
python main.py
if errorlevel 1 (
    echo.
    echo [!] Program exited with an error. Check configuration or dependencies.
    pause
)
