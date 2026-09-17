[CmdletBinding()]
param(
    [ValidateSet("development", "production_local")]
    [string]$Profile = "development",

    [ValidateRange(1, 65535)]
    [int]$Port = 8000
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$projectRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$python = Join-Path $projectRoot ".venv\Scripts\python.exe"
$managePy = Join-Path $projectRoot "manage.py"
$settingsModule = "config.settings.$Profile"

function Stop-WithGuidance {
    param([Parameter(Mandatory)][string]$Message)
    Write-Error $Message
    exit 1
}

if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    Stop-WithGuidance "Ambiente virtual ausente. Na raiz do projeto, execute: uv sync --locked"
}
if (-not (Test-Path -LiteralPath $managePy -PathType Leaf)) {
    Stop-WithGuidance "manage.py não foi encontrado. Confirme a instalação do projeto e execute este entry point sem movê-lo."
}

$pythonVersion = & $python -c "import sys; print('.'.join(map(str, sys.version_info[:3])))"
if ($LASTEXITCODE -ne 0 -or $pythonVersion -ne "3.13.15") {
    Stop-WithGuidance "O ambiente virtual deve usar Python 3.13.15. Recrie-o com: uv sync --locked"
}
if ($Profile -eq "production_local" -and [string]::IsNullOrWhiteSpace($env:CEI_SECRET_KEY)) {
    Stop-WithGuidance "CEI_SECRET_KEY é obrigatória no perfil production_local. Defina-a somente neste processo antes de iniciar."
}

$listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, $Port)
try {
    $listener.Start()
} catch {
    Stop-WithGuidance "A porta 127.0.0.1:$Port já está ocupada. Encerre conscientemente o processo que a usa ou escolha -Port outra-porta."
} finally {
    if ($null -ne $listener) {
        $listener.Stop()
    }
}

Write-Host "Iniciando Caderno de Erros em http://127.0.0.1:$Port/"
Write-Host "Para encerrar com segurança, pressione Ctrl+C neste terminal."
Push-Location -LiteralPath $projectRoot
try {
    & $python $managePy runserver "127.0.0.1:$Port" "--settings=$settingsModule" --noreload
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
