[CmdletBinding()]
param(
    [switch]$SkipVulnerabilityAudit
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$uvCommand = Get-Command uv -ErrorAction Stop

function Invoke-Tool {
    param(
        [Parameter(Mandatory)]
        [string]$Step,

        [Parameter(Mandatory)]
        [string[]]$Arguments
    )

    Write-Host "==> $Step"
    & $uvCommand.Source @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Falha na etapa '$Step' (código $LASTEXITCODE)."
    }
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
        "--cov=src",
        "--cov-report=term-missing"
    )
} else {
    Write-Host "==> validar executáveis de análise e testes (não há código Python na Etapa 1)"
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

if (-not $SkipVulnerabilityAudit) {
    Invoke-Tool "auditar vulnerabilidades" @(
        "run",
        "--locked",
        "pip-audit",
        "--local",
        "--strict"
    )
}

Write-Host "Toolchain da Etapa 1 validada."
