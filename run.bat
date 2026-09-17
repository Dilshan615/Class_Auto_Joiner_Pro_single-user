@echo off
title Java Institute - Class Auto Joiner
cd /d "%~dp0"
echo Starting Java Institute Class Auto Joiner...
python app.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo An error occurred while starting the application.
    pause
)
