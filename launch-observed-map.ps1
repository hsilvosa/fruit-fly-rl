$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
Write-Host 'Large-room planner. Default: planner-1.0 (baseline); use --controller-version 1.2 for dual readout. No training.'
& (Join-Path $PSScriptRoot '.conda\python.exe') -s -m fly_rl demo --controller observed-map --seed 370000 --brain-view @args
if ($LASTEXITCODE -ne 0) { throw 'The observed-map demo failed. See the error above.' }
