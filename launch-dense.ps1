$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$checkpoint = Join-Path $PSScriptRoot 'runs\dense-flight-policy.zip'
if (Test-Path -LiteralPath $checkpoint) {
    & (Join-Path $PSScriptRoot 'launch-demo.ps1') --room-mode dense --dynamics coordinated --brain-view --checkpoint $checkpoint @args
} else {
    $checkpoint = Join-Path $PSScriptRoot 'runs\dense-policy.zip'
    if (-not (Test-Path -LiteralPath $checkpoint)) {
        $checkpoint = Join-Path $PSScriptRoot 'runs\navigation-policy.zip'
        Write-Host 'Using the small-room legacy policy as a transfer baseline.'
    }
    & (Join-Path $PSScriptRoot 'launch-demo.ps1') --room-mode dense --checkpoint $checkpoint @args
}
if ($LASTEXITCODE -ne 0) { throw 'The dense-room demo failed.' }
