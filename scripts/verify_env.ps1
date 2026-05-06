<#
Simple PowerShell environment verifier.
It checks common environment variables and optionally loads .env files found in the repo.
Run from repository root in PowerShell (Windows PowerShell or PowerShell Core):

# ./scripts/verify_env.ps1

# If you prefer to load .env into the session first, run:
# Get-Content .\.env | ForEach-Object { if ($_ -and $_ -notmatch '^\s*#') { $pair = $_ -split '='; Set-Item -Path env:$($pair[0].Trim()) -Value $pair[1].Trim() } }
#
# Exits with code 0 when OK, 1 when missing variables are detected.
#>
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent (Split-Path -Path $MyInvocation.MyCommand.Definition -Parent)
$envFiles = @(
    Join-Path $root '..\.env'
    Join-Path $root '..\backend\.env'
    Join-Path $root '..\frontend\redmineAgentUI\.env'
)

foreach ($f in $envFiles) {
    if (Test-Path $f) {
        Get-Content $f | ForEach-Object {
            if ($_ -and ($_ -notmatch '^\s*#')) {
                $parts = $_ -split '=', 2
                if ($parts.Length -eq 2) {
                    $name = $parts[0].Trim()
                    $value = $parts[1].Trim()
                    if (-not [string]::IsNullOrEmpty($name)) {
                        Set-Item -Path Env:$name -Value $value
                    }
                }
            }
        }
    }
}

$vars = @('OPENROUTER_API_KEY','REDMINE_URL','REDMINE_API_KEY','BACKEND_PORT','VITE_API_BASE_URL')
$missing = @()
foreach ($v in $vars) {
    if (-not $env:$v) { $missing += $v }
}

if ($missing.Count -gt 0) {
    Write-Error "Missing environment variables: $($missing -join ', ')"
    Write-Host "Tip: copy .env.sample files and set values, or use 'setx' to persist vars in Windows." -ForegroundColor Yellow
    exit 1
}

Write-Host "All required environment variables appear to be set." -ForegroundColor Green
exit 0
