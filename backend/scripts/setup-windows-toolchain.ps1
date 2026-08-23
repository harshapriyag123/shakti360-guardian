<#
Setup script for Windows: installs Visual Studio C++ build tools and Rust (rustup).
Run in an elevated PowerShell (as Administrator).

Usage:
  Open PowerShell as Administrator and run:
    .\backend\scripts\setup-windows-toolchain.ps1

Notes:
  - This script downloads the VS Build Tools installer and runs it with the
    C++ workload. The installer is large and will take time.
  - rustup will be installed for the current user; you may need to restart
    the shell for `cargo` to be on PATH.
#>

function Ensure-CommandExists {
    param([string]$cmd)
    return (Get-Command $cmd -ErrorAction SilentlyContinue) -ne $null
}

if (-not ([bool](Get-CimInstance -ClassName Win32_OperatingSystem))) {
    Write-Host "This script must be run on Windows." -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path "$PSScriptRoot\..\..\backend")) {
    # loose guard; script is safe to run from repo root too
}

if (-not (Ensure-CommandExists -cmd 'curl') -and -not (Ensure-CommandExists -cmd 'Invoke-WebRequest')) {
    Write-Host "Neither curl nor Invoke-WebRequest is available; please run in PowerShell 5+ or install curl." -ForegroundColor Red
    exit 1
}

Write-Host "Installing Visual Studio Build Tools (C++ workload). This will take a while..." -ForegroundColor Cyan
$vsUrl = 'https://aka.ms/vs/17/release/vs_buildtools.exe'
$vsInstaller = "$env:TEMP\vs_buildtools.exe"
Invoke-WebRequest -Uri $vsUrl -OutFile $vsInstaller -UseBasicParsing

Start-Process -FilePath $vsInstaller -ArgumentList '--add', 'Microsoft.VisualStudio.Workload.VCTools', '--quiet', '--wait', '--norestart' -Wait

Write-Host "Visual Studio Build Tools installation finished (or returned). Now installing Rust (rustup)..." -ForegroundColor Cyan
$rustUrl = 'https://win.rustup.rs'
$rustInstaller = "$env:TEMP\rustup-init.exe"
Invoke-WebRequest -Uri $rustUrl -OutFile $rustInstaller -UseBasicParsing

Start-Process -FilePath $rustInstaller -ArgumentList '-y' -Wait

Write-Host 'Toolchain install complete. Close and re-open your terminal (or restart) before running: `pip install -r requirements.txt`' -ForegroundColor Green
