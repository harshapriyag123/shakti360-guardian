<#
Create a Python 3.11 venv (if `py -3.11` is available) and install requirements.
Usage (run from repo root):
  PowerShell> Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
  PowerShell> .\backend\scripts\create-py311-venv.ps1

This script will:
 - use `py -3.11` to create a venv at `backend/.venv`
 - activate it, upgrade pip, and install `requirements.txt`
 - run the backend test suite
#>

function Ensure-CommandExists([string]$cmd) {
    return (Get-Command $cmd -ErrorAction SilentlyContinue) -ne $null
}

if (-not (Ensure-CommandExists -cmd 'py')) {
    Write-Host "The 'py' launcher is not available. Install Python 3.11 and ensure 'py' is on PATH." -ForegroundColor Yellow
    exit 1
}

$ver = & py -3.11 --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Python 3.11 is not available via 'py -3.11'. Please install Python 3.11 or use the official installer." -ForegroundColor Yellow
    exit 1
}

Write-Host "Creating Python 3.11 venv at backend/.venv" -ForegroundColor Cyan
py -3.11 -m venv backend/.venv

Write-Host "Activating venv and installing requirements..." -ForegroundColor Cyan
& backend\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r backend\requirements.txt

Write-Host "Running backend tests..." -ForegroundColor Cyan
python -m pytest -q backend || Write-Host "Tests finished (non-zero exit code)" -ForegroundColor Yellow

Write-Host "Done. Activate the environment with: .\\backend\\.venv\\Scripts\\Activate.ps1" -ForegroundColor Green
