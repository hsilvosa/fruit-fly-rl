$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location -LiteralPath $Root
$demoArguments = @($args)
$untrained = $demoArguments -contains '--untrained'
$demoArguments = @($demoArguments | Where-Object { $_ -ne '--untrained' })
$navigationPolicy = Join-Path $Root 'runs\navigation-policy.zip'
if (-not ($demoArguments -contains 'observed-map') -and -not $untrained -and (Test-Path -LiteralPath $navigationPolicy) -and -not ($demoArguments -contains '--checkpoint')) {
    Write-Host 'Opening the selected navigation policy. Use --untrained for the initial controller.'
    $demoArguments = @('--checkpoint', $navigationPolicy) + $demoArguments
}
& (Join-Path $Root '.conda\python.exe') -s -m fly_rl demo @demoArguments
if ($LASTEXITCODE -ne 0) { throw 'The fly demo failed. See the error above.' }
