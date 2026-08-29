@echo off
title GhoSty OwO V4.1 - Setup Assistant
cd /d "%~dp0\.."
python setup.py
if errorlevel 1 (
    echo.
    echo [!] Setup exited with an error.
    pause
)
