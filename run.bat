@echo off
title Telegram Economy RPG Bot
color 0A

echo ============================================
echo   Telegram Economy RPG Bot — Windows Runner
echo ============================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found! Install Python 3.12+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

REM Check if .env exists
if not exist ".env" (
    echo [!] No .env file found.
    echo Copying from .env.example...
    if exist ".env.example" (
        copy .env.example .env
        echo.
        echo ============================================
        echo   EDIT .env WITH YOUR CREDENTIALS:
        echo   notepad .env
        echo ============================================
        echo.
        notepad .env
    ) else (
        echo [ERROR] No .env.example found. Create a .env file manually.
        pause
        exit /b 1
    )
)

REM Install dependencies
echo [+] Installing dependencies...
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies!
    pause
    exit /b 1
)

echo.
echo [+] Starting bot...
echo     Press Ctrl+C to stop.
echo.

python -m bot.main

echo.
echo Bot stopped.
pause
