$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$manifestPath = Join-Path $PSScriptRoot 'runs\latest-large-demo.json'
$checkpoint = Join-Path $PSScriptRoot 'runs\training\panorama-coverage-v8\policy.zip'
if (Test-Path -LiteralPath $manifestPath) {
    $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
    $checkpoint = Join-Path $PSScriptRoot $manifest.checkpoint
    if ((Get-FileHash -LiteralPath $checkpoint -Algorithm SHA256).Hash.ToLowerInvariant() -ne $manifest.sha256) {
        throw 'The experimental checkpoint differs from the recorded demo manifest.'
    }
    Write-Host "Experiment: $($manifest.experiment) / status: $($manifest.navigation_status)"
}
if (-not (Test-Path -LiteralPath $checkpoint)) {
    throw 'The experimental checkpoint is not available. Check the local demo manifest and saved training artifacts.'
}
Write-Host 'Experimental panoramic controller in an original large room. This launcher does not train or promote a model.'
Write-Host "Checkpoint: $checkpoint"
& (Join-Path $PSScriptRoot 'launch-demo.ps1') --room-mode dense --map-profile large --dynamics coordinated --seed 430000 --brain-view --checkpoint $checkpoint @args
if ($LASTEXITCODE -ne 0) { throw 'The panoramic demo failed.' }

