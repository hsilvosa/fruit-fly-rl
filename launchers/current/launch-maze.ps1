$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location -LiteralPath $Root
Write-Host 'Experimental maze controller: two retained goals; five of eight fresh development goals, further corrections pending. No training.'
& (Join-Path $Root '.conda\python.exe') -s -m fly_rl demo --controller observed-map --controller-version 1.3-exp.11 --map-profile maze --seed 14000000 --brain-view @args
if ($LASTEXITCODE -ne 0) { throw 'The maze demo failed. See the error above.' }
