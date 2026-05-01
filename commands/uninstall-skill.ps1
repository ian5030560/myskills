# PowerShell script to uninstall/remove a skill directory
param(
    [string]$destination,
    [string]$skillName
)

if (-not $destination -or -not $skillName) {
    Write-Host "Usage: .\uninstall-skill.ps1 -destination <path> -skillName <name>" -ForegroundColor Yellow
    Write-Host "Example: .\uninstall-skill.ps1 -destination C:\Users\user\.agents\skills -skillName write-paper-notes" -ForegroundColor Cyan
    exit 1
}

$skillPath = Join-Path $destination $skillName

if (Test-Path $skillPath) {
    Write-Host "Removing skill '$skillName' from $destination..." -ForegroundColor Yellow
    Remove-Item $skillPath -Recurse -Force
    Write-Host "Successfully removed $skillPath" -ForegroundColor Green
} else {
    Write-Host "Skill not found: $skillPath" -ForegroundColor Red
    exit 1
}
