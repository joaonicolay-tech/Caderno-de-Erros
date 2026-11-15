[CmdletBinding()]
param([string]$Uv = 'uv')
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    & $Uv sync --locked --project $projectRoot
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao criar o ambiente fixado.' }
}
& $python (Join-Path $PSScriptRoot 'source_gate.py') --uv $Uv
exit $LASTEXITCODE
