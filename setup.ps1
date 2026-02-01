# setup.ps1 - Automation for RoB-2 Tool Installation

Write-Host "--- Starting Installation for RoB-2 Automated Ratings ---" -ForegroundColor Cyan

# 1. Check if Python is installed
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Python not found. Please install Python 3.8+ first." -ForegroundColor Red
    exit
}

# 2. Create Virtual Environment
Write-Host "Step 1: Creating Virtual Environment (venv)..." -ForegroundColor Yellow
python -m venv venv

# 3. Activate and Install Dependencies
Write-Host "Step 2: Installing Python libraries..." -ForegroundColor Yellow
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\python.exe -m pip install streamlit ollama pandas PyPDF2 xlsxwriter

# 4. Check for Ollama
if (!(Get-Command ollama -ErrorAction SilentlyContinue)) {
    Write-Host "Warning: Ollama not found in PATH. Remember to install it from ollama.com" -ForegroundColor Magenta
} else {
    Write-Host "Ollama detected! You are ready to go." -ForegroundColor Green
}

Write-Host "`n--- Installation Complete! ---" -ForegroundColor Cyan
Write-Host "To run the app, use: .\venv\Scripts\streamlit run rob2.py" -ForegroundColor White
pause