# install.ps1 — installs the acm-debug skill into a project or globally
# Usage:
#   .\install.ps1                         Install to current project (.claude\commands\)
#   .\install.ps1 -Global                 Install globally (~\.claude\commands\)
#   .\install.ps1 -Project C:\my\project  Install to a specific project directory

param(
    [switch]$Global,
    [string]$Project = ""
)

$SkillFile   = "commands\debug.md"
$CommandName = "debug.md"
$ScriptDir   = Split-Path -Parent $MyInvocation.MyCommand.Path
$Src         = Join-Path $ScriptDir $SkillFile

# Verify source exists
if (-not (Test-Path $Src)) {
    Write-Error "Skill file not found at: $Src"
    Write-Error "Make sure you are running this script from the acm-debug repository root."
    exit 1
}

# Resolve destination
if ($Global) {
    $Dest = Join-Path $env:USERPROFILE ".claude\commands"
} elseif ($Project -ne "") {
    $Dest = Join-Path $Project ".claude\commands"
} else {
    $Dest = Join-Path (Get-Location) ".claude\commands"
}

# Create destination directory and copy file
New-Item -ItemType Directory -Force -Path $Dest | Out-Null
Copy-Item -Path $Src -Destination (Join-Path $Dest $CommandName) -Force

Write-Host ""
Write-Host "  acm-debug skill installed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "  Location : $Dest\$CommandName"
Write-Host ""
Write-Host "  Usage:"
Write-Host "    /debug src\app.py             Full debug report for a file"
Write-Host "    /debug src\app.py --fix       Debug and auto-apply critical fixes"
Write-Host "    /debug src\app.py --quick     Critical and logic errors only"
Write-Host ""
