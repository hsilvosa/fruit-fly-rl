$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
Write-Host 'Architectural full-connectome demo. Experimental explicit planner; no training.'
& (Join-Path $PSScriptRoot '.conda\python.exe') -s -m fly_rl demo --architecture-scene office-floor --brain-view @args
if ($LASTEXITCODE -ne 0) { throw 'The architectural demo failed. See the error above.' }
