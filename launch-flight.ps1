$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$checkpoint = Join-Path $PSScriptRoot 'runs\training\flight-v1\selected-policy.zip'
if (Test-Path -LiteralPath $checkpoint) {
    & (Join-Path $PSScriptRoot 'launch-demo.ps1') --dynamics coordinated --brain-view --checkpoint $checkpoint @args
} else {
    Write-Host 'New coordinated dynamics: untrained controller until its checkpoint is available.'
    & (Join-Path $PSScriptRoot 'launch-demo.ps1') --untrained --dynamics coordinated --brain-view @args
}
if ($LASTEXITCODE -ne 0) { throw 'The coordinated-flight demo failed.' }
