# PowerShell script to copy skill directory
# Dependencies: pip install pymupdf4llm (system: Tesseract-OCR for OCR)
param(
    [string]$source,
    [string]$destination,
    [string]$skillName
)

if (-not $source -or -not $destination) {
    Write-Host "Usage: .\install-skill.ps1 -source <path> -destination <path> [-skillName <name>]" -ForegroundColor Yellow
    Write-Host "Example: .\install-skill.ps1 -source C:\myskills\write-paper-notes -destination C:\Users\user\.agents\skills -skillName write-paper-notes" -ForegroundColor Cyan
    exit 1
}

# If skillName not provided, use source folder name
if (-not $skillName) {
    $skillName = Split-Path $source -Leaf
}

$destPath = Join-Path $destination $skillName

if (Test-Path $destPath) {
    Write-Host "Destination already exists. Overwriting..." -ForegroundColor Yellow
    Remove-Item $destPath -Recurse -Force
}

Copy-Item $source $destPath -Recurse -Force
Write-Host "Successfully installed $skillName to $destination" -ForegroundColor Green
