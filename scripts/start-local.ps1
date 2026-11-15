[CmdletBinding()]
param(
    [ValidateSet("production_local")]
    [string]$Profile = "production_local",

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

$root = Split-Path -Parent $projectRoot
if ((Split-Path -Leaf $projectRoot) -eq 'code') {
    $root = Split-Path -Parent (Split-Path -Parent $root)
}
$allowed = $projectRoot -ceq (Join-Path $root 'candidate') -or $projectRoot.StartsWith((Join-Path $root 'validation') + '\', [System.StringComparison]::OrdinalIgnoreCase) -or $projectRoot.StartsWith((Join-Path $root 'installed') + '\', [System.StringComparison]::OrdinalIgnoreCase)
if (-not $allowed) { Stop-WithGuidance 'Instalação fora do perímetro qualificado.' }
if ($projectRoot.StartsWith((Join-Path $root 'installed') + '\', [System.StringComparison]::OrdinalIgnoreCase)) {
    $instance = Get-Content -LiteralPath (Join-Path $projectRoot '.local-r1.json') -Raw | ConvertFrom-Json
    if (($instance.user_enabled -isnot [bool]) -or ($instance.user_enabled -ne $true) -or ($instance.activation_purpose -ne 'REAL_USE')) { Stop-WithGuidance 'Esta instalacao aguarda a decisao final de liberacao. Nao insira dados reais na verificacao sintetica.' }
}
foreach ($name in @('CEI_PRODUCTION_LOCAL_DB','CEI_DEVELOPMENT_DB','CEI_LOCAL_ROOT','CEI_SECRET_KEY','DATABASE_URL','PYTHONPATH','PYTHONHOME')) {
    Remove-Item -LiteralPath "Env:$name" -ErrorAction SilentlyContinue
}
$env:TEMP = Join-Path $root 'validation\tmp'
$env:TMP = $env:TEMP
$env:PYTHONDONTWRITEBYTECODE = '1'
if ($projectRoot.StartsWith((Join-Path $root 'installed') + '\', [System.StringComparison]::OrdinalIgnoreCase)) {
    $env:PYTHONPYCACHEPREFIX = Join-Path $root 'user\tmp\pycache'
} else {
    $env:PYTHONPYCACHEPREFIX = Join-Path $root 'validation\cache\pycache'
}
$env:DJANGO_SETTINGS_MODULE = 'config.settings.production_local'
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
& $python -c "import sys; sys.path.insert(0, r'$projectRoot\src'); from shared.infrastructure.local_boundary import configure_process; configure_process()"
if ($LASTEXITCODE -ne 0) { Stop-WithGuidance 'Marcador ou identidade da instalação inválidos.' }

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
    & $python $managePy runserver "127.0.0.1:$Port" "--settings=$settingsModule" --noreload --insecure
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
