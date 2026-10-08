$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
Write-Host 'Verified large development controller: six retained and eight fresh goals. No training.'
& (Join-Path $PSScriptRoot '.conda\python.exe') -s -m fly_rl demo --controller observed-map --controller-version 1.3-exp.9 --map-profile large --seed 15000000 --brain-view @args
if ($LASTEXITCODE -ne 0) { throw 'The large demo failed. See the error above.' }
