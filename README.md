# Caderno de Erros

Sistema para registro, classificação e revisão de erros de estudo.

A documentação oficial do projeto está localizada em `/docs`.

## Estado atual

A Etapa 2 da V0.1 fornece o projeto Django mínimo, com perfis separados de
desenvolvimento, teste e produção local. Ainda não existem models ou
funcionalidades de produto.

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
uv run --locked python manage.py migrate --settings=config.settings.production_local
uv run --locked python manage.py runserver 127.0.0.1:8000 --settings=config.settings.production_local
Remove-Item -LiteralPath Env:CEI_SECRET_KEY
```

O banco padrão desse perfil é `var/production_local.sqlite3`. Um caminho externo
pode ser informado por `CEI_PRODUCTION_LOCAL_DB`. `CEI_ALLOWED_HOSTS` aceita
somente `127.0.0.1`, `localhost` e `[::1]`; `0.0.0.0` e nomes de rede são
recusados. Não altere o endereço de escuta para expor a aplicação.

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

Backup/restauração, logging, health e migrações de domínio ainda não existem e
serão documentados nas respectivas etapas.

Decisões técnicas:

- [`ADR-001 — Toolchain`](docs/ADR-001_Toolchain_Reproduzivel_V0.1.md)
- [`ADR-002 — Perfis e isolamento`](docs/ADR-002_Perfis_e_Isolamento_Django_V0.1.md)
