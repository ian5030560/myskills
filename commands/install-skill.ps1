# PowerShell script to copy skill directory
param(
    [string]$source,
    [string]$destination
)

if (-not $source -or -not $destination) {
    Write-Host "Usage: .\install-skill.ps1 -source <path> -destination <path>" -ForegroundColor Yellow
    exit 1
}

if (Test-Path $destination) {
    Write-Host "Destination already exists. Overwriting..." -ForegroundColor Yellow
    Remove-Item $destination -Recurse -Force
}

Copy-Item $source $destination -Recurse -Force
Write-Host "Successfully copied $source to $destination" -ForegroundColor Green
