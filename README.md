# Caderno de Erros

Sistema para registro, classificação e revisão de erros de estudo.

A documentação oficial do projeto está localizada em `/docs`.

## Estado atual

A Etapa 5 da V0.1 fornece identidade e Workspace locais, tempo/fuso, as dez
categorias padrão, logging estruturado e sanitizado, correlação e diagnóstico
local. Ainda não existem conteúdo de estudo, tentativas ou revisões.

Pré-requisitos do ambiente validado:

- Windows 11 x64;
- PowerShell 5.1 ou posterior;
- Git;
- `uv 0.12.7`.

Instalação exata do `uv` no Windows:

```powershell
powershell -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/0.12.7/install.ps1 | iex"
```

Preparação reproduzível:

```powershell
uv sync --locked
```

O `uv` baixa automaticamente o CPython `3.13.15` fixado em `.python-version`.
Não use `pip install` manual nem regenere o lock implicitamente. Atualizações são
intencionais: altere as versões diretas, execute `uv lock` e valide novamente.

## Perfis Django

### Desenvolvimento

O perfil padrão de `manage.py` usa SQLite em `var/development.sqlite3`, arquivo
ignorado pelo Git, e o servidor é iniciado explicitamente apenas em localhost:

```powershell
New-Item -ItemType Directory -Force var
uv run --locked python manage.py migrate
uv run --locked python manage.py runserver 127.0.0.1:8000
```

Para escolher outro arquivo local sem editar código:

```powershell
$env:CEI_DEVELOPMENT_DB = "C:\dados-locais\cei-development.sqlite3"
```

### Testes

pytest-django seleciona `config.settings.test` automaticamente. Esse perfil cria
um arquivo SQLite em diretório temporário exclusivo e ignora caminhos de banco e
chaves dos outros perfis:

```powershell
uv run --locked pytest
```

Nunca configure testes para usar `development.sqlite3` ou
`production_local.sqlite3`.

### Produção local

O perfil de produção local mantém `DEBUG=False`, aceita somente hosts locais e
exige chave externa. Gere uma chave apenas no processo atual e não a salve no
repositório:

```powershell
$env:CEI_SECRET_KEY = uv run --locked python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
New-Item -ItemType Directory -Force var
uv run --locked python manage.py migrate --settings=config.settings.production_local
uv run --locked python manage.py runserver 127.0.0.1:8000 --settings=config.settings.production_local
Remove-Item -LiteralPath Env:CEI_SECRET_KEY
```

O banco padrão desse perfil é `var/production_local.sqlite3`. Um caminho externo
pode ser informado por `CEI_PRODUCTION_LOCAL_DB`. `CEI_ALLOWED_HOSTS` aceita
somente `127.0.0.1`, `localhost` e `[::1]`; `0.0.0.0` e nomes de rede são
recusados. Não altere o endereço de escuta para expor a aplicação.

## Primeiro acesso local

Migre o banco e escolha explicitamente o fuso IANA do espaço. O comando é
idempotente: repeti-lo recupera o mesmo User/Workspace, preserva o fuso já salvo e
mantém exatamente as dez categorias padrão com seus textos canônicos atuais.

```powershell
uv run --locked python manage.py migrate
uv run --locked python manage.py bootstrap_local --timezone America/Sao_Paulo
```

Opcionalmente, informe `--workspace-name` e `--display-name`. Não existe fuso
implícito derivado do sistema. Alterações posteriores são feitas pelo serviço de
aplicação com confirmação e `lock_version`; a interface será adicionada em etapa
própria.

## Logging e diagnóstico local

Os logs operacionais são emitidos como uma linha JSON por evento. Cada evento
possui horário UTC, nível, código estável, UUID de correlação, operação, resultado
e contexto técnico mínimo. Senhas, chaves, tokens, cabeçalhos de autorização,
cookies, sessões, corpos, payloads e conteúdo de estudo são removidos por uma
camada central antes da serialização.

O diagnóstico está disponível somente pela fronteira local:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health/
```

Com aplicação e SQLite disponíveis, retorna HTTP `200` e estado `healthy`. Banco
indisponível retorna HTTP `503` e estado `unhealthy`, sem caminho, configuração,
segredo ou stack trace. Clientes não loopback recebem HTTP `403`. A resposta
inclui `X-Correlation-ID`; clientes podem enviar um UUID nesse mesmo cabeçalho.

Os comandos técnicos também aceitam correlação explícita quando necessário:

```powershell
uv run --locked python manage.py migrate --correlation-id 12345678-1234-4234-8234-123456789abc
uv run --locked python manage.py bootstrap_local --timezone America/Sao_Paulo --correlation-id 12345678-1234-4234-8234-123456789abc
```

## Qualidade e verificação

O gate único executa checks dos três perfis, verifica ausência de migrações
inesperadas, migra um banco vazio descartável, executa Ruff, mypy, pytest,
detecção de segredos e auditoria de dependências:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1
```

Falhas comuns:

- `uv` em versão diferente: reinstale exatamente `0.12.7`;
- produção local recusa iniciar: defina `CEI_SECRET_KEY` apenas no ambiente;
- host recusado: use `127.0.0.1` ou `localhost`, nunca uma interface de rede;
- lock desatualizado: não o regenere implicitamente; revise a mudança de
  dependência antes de executar `uv lock`.

Interface de configuração e backup/restauração ainda não existem e serão
implementados nas respectivas etapas. Telemetria remota, métricas, alertas e
auditoria funcional persistente não pertencem à Etapa 5.

Decisões técnicas:

- [`ADR-001 — Toolchain`](docs/ADR-001_Toolchain_Reproduzivel_V0.1.md)
- [`ADR-002 — Perfis e isolamento`](docs/ADR-002_Perfis_e_Isolamento_Django_V0.1.md)
- [`ADR-003 — Identidade, Workspace e tempo`](docs/ADR-003_Identidade_Workspace_e_Tempo_V0.1.md)
- [`ADR-004 — Categorias padrão e seed`](docs/ADR-004_Categorias_Padrao_e_Seed_V0.1.md)
- [`ADR-005 — Logging, correlação e health local`](docs/ADR-005_Logging_Correlacao_e_Health_Local_V0.1.md)
