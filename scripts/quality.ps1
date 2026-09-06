[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$gateStopwatch = [System.Diagnostics.Stopwatch]::StartNew()

$toolsDirectory = Join-Path $PSScriptRoot "..\.tools"
$env:UV_CACHE_DIR = Join-Path $toolsDirectory "cache"
$env:UV_PYTHON_INSTALL_DIR = Join-Path $toolsDirectory "python"
$qualityReportsDirectory = Join-Path $toolsDirectory "quality"
$coverageReport = ".tools/quality/coverage.json"
$gateManifest = "quality/v02-stage1-gate.json"
$pytestBaseTemp = Join-Path ([System.IO.Path]::GetTempPath()) (
    "cei-pytest-" + [Guid]::NewGuid().ToString("N")
)
New-Item -ItemType Directory -Path $qualityReportsDirectory -Force | Out-Null
Remove-Item -LiteralPath $coverageReport -ErrorAction SilentlyContinue

$uvCommand = Get-Command uv -ErrorAction SilentlyContinue
if ($null -eq $uvCommand) {
    $workspaceUv = Join-Path $PSScriptRoot "..\.tools\uv\uv.exe"
    if (-not (Test-Path -LiteralPath $workspaceUv -PathType Leaf)) {
        throw "uv 0.12.7 não encontrado no PATH nem em .tools/uv/uv.exe."
    }
    $uvExecutable = (Get-Item -LiteralPath $workspaceUv).FullName
} else {
    $uvExecutable = $uvCommand.Source
}

function Invoke-Tool {
    param(
        [Parameter(Mandatory)]
        [string]$Step,

        [Parameter(Mandatory)]
        [string[]]$Arguments
    )

    Write-Host "==> $Step"
    & $uvExecutable @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Falha na etapa '$Step' (código $LASTEXITCODE)."
    }
}

function Invoke-PipAudit {
    $auditReport = Join-Path $qualityReportsDirectory (
        "pip-audit-" + [Guid]::NewGuid().ToString("N") + ".json"
    )

    Write-Host "==> auditar vulnerabilidades"
    & $uvExecutable "run" "--locked" "pip-audit" "--local" "--strict" "--format" "json" "--output" $auditReport
    $auditExitCode = $LASTEXITCODE
    if ($auditExitCode -eq 0) {
        return
    }

    $vulnerabilityCount = 0
    if (Test-Path -LiteralPath $auditReport -PathType Leaf) {
        try {
            $auditResult = Get-Content -Raw -LiteralPath $auditReport | ConvertFrom-Json
            $vulnerabilityCount = @(
                $auditResult.dependencies |
                    ForEach-Object { $_.vulns } |
                    Where-Object { $null -ne $_ }
            ).Count
        } catch {
            throw "A auditoria de vulnerabilidades falhou sem produzir um relatorio JSON valido (codigo $auditExitCode)."
        }
    }

    if ($vulnerabilityCount -gt 0) {
        throw "A auditoria encontrou $vulnerabilityCount vulnerabilidade(s) conhecida(s) (codigo $auditExitCode)."
    }

    throw "A auditoria de vulnerabilidades nao foi concluida (codigo $auditExitCode; por exemplo, falha de rede ou de ferramenta)."
}

Invoke-Tool "validar lock" @("lock", "--check")
Invoke-Tool "sincronizar ambiente" @("sync", "--locked")
Invoke-Tool "validar runtime" @(
    "run",
    "--locked",
    "python",
    "-c",
    "import django, sqlite3, sys; sample = 'quest\u00e3o'; assert sys.version_info[:3] == (3, 13, 15); assert django.get_version() == '5.2.17'; assert sqlite3.sqlite_version_info == (3, 53, 1); assert sample.encode('utf-8').decode('utf-8') == sample; print(f'Python={sys.version.split()[0]} Django={django.get_version()} SQLite={sqlite3.sqlite_version}')"
)
Invoke-Tool "validar rastreabilidade e baseline documental" @(
    "run", "--locked", "python", "scripts/verify_v01.py", "repository",
    "--manifest", $gateManifest
)
Invoke-Tool "verificar perfil de desenvolvimento" @(
    "run", "--locked", "python", "manage.py", "check",
    "--settings=config.settings.development"
)
Invoke-Tool "verificar perfil de teste" @(
    "run", "--locked", "python", "manage.py", "check",
    "--settings=config.settings.test"
)

$hadProductionSecret = Test-Path -LiteralPath "Env:CEI_SECRET_KEY"
$previousProductionSecret = [Environment]::GetEnvironmentVariable("CEI_SECRET_KEY", "Process")
try {
    if (-not $hadProductionSecret) {
        $env:CEI_SECRET_KEY = [Guid]::NewGuid().ToString("N") + [Guid]::NewGuid().ToString("N")
    }
    Invoke-Tool "verificar perfil de produção local" @(
        "run", "--locked", "python", "manage.py", "check",
        "--settings=config.settings.production_local"
    )
} finally {
    if ($hadProductionSecret) {
        $env:CEI_SECRET_KEY = $previousProductionSecret
    } else {
        Remove-Item -LiteralPath "Env:CEI_SECRET_KEY" -ErrorAction SilentlyContinue
    }
}

Invoke-Tool "verificar migrações inesperadas" @(
    "run", "--locked", "python", "manage.py", "makemigrations",
    "--check", "--dry-run", "--settings=config.settings.test"
)
Invoke-Tool "migrar banco vazio isolado" @(
    "run", "--locked", "python", "manage.py", "migrate",
    "--noinput", "--settings=config.settings.test"
)
Invoke-Tool "verificar formatação" @("run", "--locked", "ruff", "format", "--check", ".")
Invoke-Tool "executar lint" @("run", "--locked", "ruff", "check", ".")

$pythonFiles = @(
    Get-ChildItem -LiteralPath "src", "tests" -Recurse -File -Filter "*.py" -ErrorAction SilentlyContinue
)

if ($pythonFiles.Count -gt 0) {
    Invoke-Tool "executar type checker" @("run", "--locked", "mypy")
    Invoke-Tool "executar testes e cobertura" @(
        "run",
        "--locked",
        "pytest",
        "--basetemp=$pytestBaseTemp",
        "--cov=src",
        "--cov-report=term-missing",
        "--cov-report=json:$coverageReport"
    )
    Invoke-Tool "validar cobertura de domínio" @(
        "run", "--locked", "python", "scripts/verify_v01.py", "coverage",
        "--manifest", $gateManifest, "--coverage-file", $coverageReport
    )
} else {
    Write-Host "==> validar executáveis de análise e testes (não há código Python)"
    Invoke-Tool "validar mypy" @("run", "--locked", "mypy", "--version")
    Invoke-Tool "validar pytest" @("run", "--locked", "pytest", "--version")
}

$filesToScan = @(
    & git ls-files --cached --others --exclude-standard |
        Where-Object { $_ -ne ".secrets.baseline" }
)
if ($LASTEXITCODE -ne 0) {
    throw "Não foi possível enumerar os arquivos para a varredura de segredos."
}
if ($filesToScan.Count -gt 0) {
    $secretArguments = @(
        "run",
        "--locked",
        "detect-secrets-hook",
        "--baseline",
        ".secrets.baseline",
        "--exclude-files",
        "^uv\\.lock$",
        "--"
    ) + $filesToScan
    Invoke-Tool "detectar segredos" $secretArguments
}

Invoke-PipAudit

$gateStopwatch.Stop()
Write-Host "Gate autoritativo do projeto validado em $([Math]::Round($gateStopwatch.Elapsed.TotalSeconds, 1)) s."
