# Caderno de Erros

Sistema para registro, classificação e revisão de erros de estudo.

A documentação oficial do projeto está localizada em `/docs`.

## Estado atual

A Etapa 7 da V0.1 fornece identidade e Workspace locais, tempo/fuso, as dez
categorias padrão, logging/diagnóstico, interface acessível e backup/restauração
técnica mínima do SQLite. Ainda não existem conteúdo de estudo, tentativas ou
revisões.

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
uv run --locked python manage.py runserver 127.0.0.1:8000 --insecure --settings=config.settings.production_local
Remove-Item -LiteralPath Env:CEI_SECRET_KEY
```

O banco padrão desse perfil é `var/production_local.sqlite3`. Um caminho externo
pode ser informado por `CEI_PRODUCTION_LOCAL_DB`. `CEI_ALLOWED_HOSTS` aceita
somente `127.0.0.1`, `localhost` e `[::1]`; `0.0.0.0` e nomes de rede são
recusados. Não altere o endereço de escuta para expor a aplicação.
`--insecure` habilita somente os assets estáticos no servidor local com
`DEBUG=False`; esse comando não é uma configuração de implantação remota.

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
aplicação com confirmação e `lock_version`, tanto pelo comando quanto pela
interface local descrita a seguir.

Depois de migrar, também é possível iniciar o servidor e concluir esse fluxo pela
interface em `http://127.0.0.1:8000/`:

```powershell
uv run --locked python manage.py runserver 127.0.0.1:8000
```

A tela solicita o fuso sem deduzi-lo do computador. Depois da criação, “Início”
mostra a configuração efetiva e “Configurações” permite cancelar ou confirmar uma
mudança. Conflitos de versão exigem nova confirmação e nunca sobrescrevem o valor
silenciosamente.

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

## Backup e restauração técnica mínima

O backup usa o mecanismo consistente do próprio SQLite e gera um manifesto sidecar
com formato `CEI-SQLITE-BACKUP` 1.0, instante UTC, tamanho e SHA-256. Crie o diretório
de destino e informe um nome novo; arquivos existentes nunca são sobrescritos:

```powershell
New-Item -ItemType Directory -Force backups
uv run --locked python manage.py backup_sqlite --output backups\cei-v01.sqlite3
uv run --locked python manage.py validate_backup --backup backups\cei-v01.sqlite3
```

O manifesto será `backups\cei-v01.sqlite3.manifest.json`. Mantenha os dois arquivos
juntos. O backup contém os mesmos dados privados do banco: restrinja seu acesso e,
se ele sair do dispositivo protegido, aplique proteção adequada antes do transporte.

Restauração na V0.1 sempre usa um novo arquivo em diretório isolado. O comando valida
manifesto, tamanho, checksum, integridade SQLite, migrações, identidade/Workspace,
locale, fuso e as dez categorias antes de publicar o destino:

```powershell
New-Item -ItemType Directory -Force recovery
uv run --locked python manage.py restore_backup --backup backups\cei-v01.sqlite3 --destination recovery\validated.sqlite3
```

Para provar a inicialização sem trocar o banco de desenvolvimento, aponte
temporariamente o perfil para a cópia validada e remova a variável em seguida:

```powershell
$env:CEI_DEVELOPMENT_DB = (Resolve-Path recovery\validated.sqlite3).Path
uv run --locked python manage.py check
uv run --locked python manage.py shell -c "from modules.accounts.models import User, Workspace; from modules.errors.models import ErrorCategory; assert (User.objects.count(), Workspace.objects.count(), ErrorCategory.objects.count()) == (1, 1, 10)"
Remove-Item -LiteralPath Env:CEI_DEVELOPMENT_DB
```

Esses comandos não substituem o banco ativo nem recriam dados ausentes. Checksum
inválido, versão desconhecida, migração divergente ou reconciliação incompleta falham
antes da publicação. Use sempre destinos descartáveis para exercícios. RPO/RTO,
retenção automática, rotação, scheduler, nuvem, exportação e restauração pela
interface só entram nos marcos posteriores documentados.

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

Questões, revisões, dashboard, busca, métricas e links correspondentes não fazem
parte da interface V0.1 atual. Telemetria remota, alertas, retenção automatizada,
exportação e auditoria funcional persistente também permanecem posteriores.

Decisões técnicas:

- [`ADR-001 — Toolchain`](docs/ADR-001_Toolchain_Reproduzivel_V0.1.md)
- [`ADR-002 — Perfis e isolamento`](docs/ADR-002_Perfis_e_Isolamento_Django_V0.1.md)
- [`ADR-003 — Identidade, Workspace e tempo`](docs/ADR-003_Identidade_Workspace_e_Tempo_V0.1.md)
- [`ADR-004 — Categorias padrão e seed`](docs/ADR-004_Categorias_Padrao_e_Seed_V0.1.md)
- [`ADR-005 — Logging, correlação e health local`](docs/ADR-005_Logging_Correlacao_e_Health_Local_V0.1.md)
- [`ADR-006 — Interface acessível da fundação`](docs/ADR-006_Interface_Acessivel_da_Fundacao_V0.1.md)
- [`ADR-007 — Backup e restauração mínima SQLite`](docs/ADR-007_Backup_e_Restauracao_Minima_SQLite_V0.1.md)
