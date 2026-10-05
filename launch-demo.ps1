$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$demoArguments = @($args)
$untrained = $demoArguments -contains '--untrained'
$demoArguments = @($demoArguments | Where-Object { $_ -ne '--untrained' })
$navigationPolicy = Join-Path $PSScriptRoot 'runs\navigation-policy.zip'
if (-not ($demoArguments -contains 'observed-map') -and -not $untrained -and (Test-Path -LiteralPath $navigationPolicy) -and -not ($demoArguments -contains '--checkpoint')) {
    Write-Host 'Opening the selected navigation policy. Use --untrained for the initial controller.'
    $demoArguments = @('--checkpoint', $navigationPolicy) + $demoArguments
}
& (Join-Path $PSScriptRoot '.conda\python.exe') -s -m fly_rl demo @demoArguments
if ($LASTEXITCODE -ne 0) { throw 'The fly demo failed. See the error above.' }
