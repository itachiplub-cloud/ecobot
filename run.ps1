# Telegram Economy RPG Bot — Windows PowerShell Runner
# Right-click > Run with PowerShell, or: .\run.ps1

$ErrorActionPreference = "Stop"

Write-Host "============================================" -ForegroundColor Green
Write-Host "  Telegram Economy RPG Bot — PowerShell" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""

# Check Python
try {
    $pyVersion = python --version 2>&1
    Write-Host "[+] $pyVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python not found!" -ForegroundColor Red
    Write-Host "Install Python 3.12+ from https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "Check 'Add Python to PATH' during installation." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check .env
if (-not (Test-Path ".env")) {
    Write-Host "[!] No .env file found. Creating from .env.example..." -ForegroundColor Yellow
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host ""
        Write-Host "Edit .env with your credentials:" -ForegroundColor Cyan
        Write-Host "  notepad .env" -ForegroundColor White
        Write-Host ""
        Start-Process notepad ".env"
        Read-Host "Press Enter after saving .env to continue"
    } else {
        Write-Host "[ERROR] No .env.example found!" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Install dependencies
Write-Host "[+] Installing dependencies..." -ForegroundColor Green
pip install -r requirements.txt --quiet

Write-Host ""
Write-Host "[+] Starting bot... Press Ctrl+C to stop." -ForegroundColor Green
Write-Host ""

python -m bot.main

Write-Host ""
Write-Host "Bot stopped." -ForegroundColor Yellow
Read-Host "Press Enter to exit"
