$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
Write-Host 'Observed neuronal map planner in a large room. No learned movement weights or training.'
& (Join-Path $PSScriptRoot '.conda\python.exe') -s -m fly_rl demo --controller observed-map --seed 370000 --brain-view @args
if ($LASTEXITCODE -ne 0) { throw 'The observed-map demo failed. See the error above.' }
