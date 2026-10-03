$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$flyEnvironment = Join-Path $PSScriptRoot '.conda'
if (-not (Test-Path -LiteralPath (Join-Path $flyEnvironment 'python.exe'))) {
    conda env create --prefix $flyEnvironment --file environment.yml
    if ($LASTEXITCODE -ne 0) { throw 'Conda environment creation failed.' }
}
if (Test-Path -LiteralPath 'requirements-lock.txt') {
    & (Join-Path $flyEnvironment 'python.exe') -s -m pip install --extra-index-url https://download.pytorch.org/whl/cu128 -r requirements-lock.txt
    if ($LASTEXITCODE -ne 0) { throw 'Locked dependency installation failed.' }
}
& (Join-Path $flyEnvironment 'python.exe') -s -m pip install -e .
if ($LASTEXITCODE -ne 0) { throw 'Package installation failed.' }
& (Join-Path $flyEnvironment 'python.exe') -s -m fly_rl prepare-data
if ($LASTEXITCODE -ne 0) { throw 'Dataset preparation failed.' }
