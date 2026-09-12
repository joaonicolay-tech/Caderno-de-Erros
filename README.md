# Caderno de Erros

Aplicação web desenvolvida em Django para registrar, organizar e consultar erros cometidos durante os estudos, criando uma base estruturada de questões, disciplinas, assuntos e classificações de erro.

O projeto também é utilizado como exercício prático de engenharia de software, com arquitetura documentada, testes automatizados, controle de qualidade, decisões arquiteturais (ADRs), ambientes separados e evolução incremental por versões.

## Estado atual

A V0.3 está formalmente promovida. Ela preserva a fundação, a taxonomia e o
catálogo versionado das versões anteriores e implementa o ciclo de aprendizagem
e revisão: respostas iniciais, ciclos de revisão, agenda D1/D7/D14/D30, fila
derivada, linha do tempo, diagnóstico auditável e suspensão por arquivamento.

O gate final da V0.3 está GREEN, sem P0/P1 aplicável aberto. A V0.4 não foi
iniciada e exige nova autorização formal. A documentação oficial está em
[`docs/`](docs/).

## 1. Pré-requisitos

Ambiente suportado e validado:

- Windows 11 x64;
- PowerShell 5.1 ou posterior;
- Git;
- acesso à internet na primeira sincronização;
- `uv 0.12.7`.

Não é necessário instalar Python ou dependências com `pip`: o `uv` obtém o CPython
`3.13.15` fixado em [`.python-version`](.python-version) e cria `.venv` local.

## 2. Instalar o uv

Confira primeiro se a versão exata já está disponível:

```powershell
uv --version
```

Se necessário, instale a versão fixada pelo instalador oficial:

```powershell
powershell -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/0.12.7/install.ps1 | iex"
```

Feche e abra o PowerShell se o comando ainda não estiver no `PATH`.

## 3. Obter e sincronizar o projeto

Depois de clonar o repositório, entre em sua raiz — onde estão `pyproject.toml`,
`uv.lock` e `manage.py` — e execute:

```powershell
uv sync --locked
```

O comando deve concluir sem modificar `uv.lock`. Não use `pip install` manual nem
regenere o lock para contornar uma falha. Atualizações de dependência são mudanças
intencionais que exigem novo lock e execução do gate.

## 4. Configuração segura e perfis

Há três perfis explícitos:

| Perfil | Settings | Banco padrão | Uso |
|---|---|---|---|
| Desenvolvimento | `config.settings.development` | `var/development.sqlite3` | trabalho local |
| Teste | `config.settings.test` | diretório temporário exclusivo | suíte automatizada |
| Produção local | `config.settings.production_local` | `var/production_local.sqlite3` | execução loopback com `DEBUG=False` |

Arquivos `.env`, bancos, backups e chaves não devem ser versionados. O perfil de teste
ignora caminhos e segredos dos demais perfis e nunca deve apontar para um banco real.

Para escolher outro banco de desenvolvimento sem editar código:

```powershell
$env:CEI_DEVELOPMENT_DB = "C:\dados-locais\cei-development.sqlite3"
```

Para produção local, gere uma chave somente no processo atual:

```powershell
$env:CEI_SECRET_KEY = uv run --locked python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Opcionalmente, `CEI_PRODUCTION_LOCAL_DB` define outro arquivo de produção local.
`CEI_ALLOWED_HOSTS` aceita somente `127.0.0.1`, `localhost` e `[::1]`. Nunca use uma
chave dos exemplos como segredo e nunca exponha o servidor em `0.0.0.0`.

## 5. Migração e bootstrap local

No perfil padrão de desenvolvimento:

```powershell
New-Item -ItemType Directory -Force var
uv run --locked python manage.py migrate
uv run --locked python manage.py bootstrap_local --timezone America/Sao_Paulo
```

O fuso é um identificador IANA explícito; ele não é inferido do computador. O
bootstrap é idempotente: cria ou recupera um único User UUID, um Workspace com locale
`pt-BR` e exatamente dez categorias padrão. Também aceita `--workspace-name` e
`--display-name`.

Para conferir o estado mínimo:

```powershell
uv run --locked python manage.py shell -c "from modules.accounts.models import User, Workspace; from modules.errors.models import ErrorCategory; w=Workspace.objects.get(); print(User.objects.count(), Workspace.objects.count(), w.locale, w.timezone_name, ErrorCategory.objects.count())"
```

O resultado esperado após o primeiro bootstrap com o exemplo é:
`1 1 pt-BR America/Sao_Paulo 10`.

## 6. Executar a aplicação

### Desenvolvimento

```powershell
uv run --locked python manage.py runserver 127.0.0.1:8000
```

### Produção local

Com `CEI_SECRET_KEY` definido conforme a seção 4:

```powershell
New-Item -ItemType Directory -Force var
uv run --locked python manage.py migrate --settings=config.settings.production_local
uv run --locked python manage.py bootstrap_local --timezone America/Sao_Paulo --settings=config.settings.production_local
uv run --locked python manage.py runserver 127.0.0.1:8000 --insecure --settings=config.settings.production_local
```

Ao encerrar, remova a chave do processo:

```powershell
Remove-Item -LiteralPath Env:CEI_SECRET_KEY
```

`--insecure` serve apenas os assets versionados no loopback com `DEBUG=False`; não é
uma configuração de implantação remota.

## 7. Primeiro acesso e configuração de fuso

Abra <http://127.0.0.1:8000/>. Sem Workspace, a aplicação redireciona para
`/primeiro-acesso/`, onde o fuso IANA deve ser escolhido. Se o bootstrap por comando
já foi executado, “Início” mostra o estado efetivo.

Em “Configurações” é possível cancelar ou confirmar uma mudança de fuso. Cancelar
preserva o valor atual. Uma confirmação usa `lock_version`; conflito concorrente exige
nova confirmação e nunca sobrescreve silenciosamente o valor mais recente.

## 8. Health local

Com o servidor em execução:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health/
```

Aplicação e SQLite disponíveis retornam HTTP `200` e `healthy`. Banco indisponível
retorna HTTP `503` e `unhealthy`, sem caminho, segredo ou stack trace. Cliente não
loopback recebe `403`. A resposta contém `X-Correlation-ID`.

Logs operacionais são linhas JSON com horário UTC, nível, evento, correlação, operação
e resultado. Uma camada central remove senhas, chaves, tokens, cookies, sessões,
payloads, corpos e conteúdo privado antes da serialização.

## 9. Testes e gate único

Executar somente a suíte:

```powershell
uv run --locked pytest
```

Executar o gate autoritativo:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1
```

O gate valida lock e runtime, sincroniza o ambiente, confere documentação, IDs e
migrações históricas, testa os três perfis e um banco vazio, executa Ruff, mypy,
pytest/cobertura, detect-secrets e pip-audit. Qualquer fase obrigatória retorna código
diferente de zero e bloqueia a entrega. O mínimo documental é 80% de linhas para cada
módulo atual de domínio/regras; a cobertura global é informativa.

## 10. Backup, validação e restauração

Com o banco de desenvolvimento migrado e inicializado:

```powershell
New-Item -ItemType Directory -Force backups
uv run --locked python manage.py backup_sqlite --output backups\cei-v01.sqlite3
uv run --locked python manage.py validate_backup --backup backups\cei-v01.sqlite3
```

O manifesto `backups\cei-v01.sqlite3.manifest.json` registra formato
`CEI-SQLITE-BACKUP` 1.0, instante UTC, tamanho e SHA-256. Mantenha ambos juntos e
proteja-os como o banco original.

Na V0.2, restaure sempre em um arquivo novo e isolado:

```powershell
New-Item -ItemType Directory -Force recovery
uv run --locked python manage.py restore_backup --backup backups\cei-v01.sqlite3 --destination recovery\validated.sqlite3
```

Valide a inicialização sobre a cópia sem trocar o banco normal:

```powershell
$env:CEI_DEVELOPMENT_DB = (Resolve-Path recovery\validated.sqlite3).Path
uv run --locked python manage.py check
uv run --locked python manage.py shell -c "from modules.accounts.models import User, Workspace; from modules.errors.models import ErrorCategory; assert (User.objects.count(), Workspace.objects.count(), ErrorCategory.objects.count()) == (1, 1, 10)"
Remove-Item -LiteralPath Env:CEI_DEVELOPMENT_DB
```

Checksum inválido, versão desconhecida, migração divergente ou reconciliação
incompleta — incluindo taxonomia, origem, questões, revisões, alternativas, gabarito e
referências do catálogo — falham antes da publicação do destino.

## 11. Fixture sintética V0.2

O catálogo V0.2 inclui uma fixture sintética para demonstração e regressão. Ela cria
somente no **perfil de teste descartável**: um Workspace local explícito, uma
taxonomia, origem, uma questão em rascunho, uma ativa com duas revisões e uma
arquivada. As alternativas, o gabarito e a origem são artificiais e não representam
aprendizagem, pessoas ou conteúdo privado. A carga é idempotente para a semente
`v02-catalog-demo-001`; nunca é automática e recusa desenvolvimento e produção local.

Em um banco de teste descartável já migrado, execute:

```powershell
uv run --locked python manage.py load_v02_fixture --settings=config.settings.test
```

Não use esse comando para carregar banco de uso local. Para uma demonstração, execute
o perfil de teste em ambiente isolado e descarte o banco ao encerrar.

## 12. Solução de problemas

- **`uv` não encontrado:** reabra o PowerShell após instalar e confirme `uv --version`.
- **Versão de `uv` divergente:** reinstale exatamente `0.12.7`.
- **Lock inconsistente:** não execute `uv lock` por conveniência; confirme que a revisão
  correta do `uv.lock` foi obtida.
- **Produção local não inicia:** defina `CEI_SECRET_KEY` no processo atual.
- **Host recusado:** use `127.0.0.1` ou `localhost`, nunca uma interface de rede.
- **Porta 8000 ocupada:** encerre o processo anterior ou use outra porta loopback,
  como `127.0.0.1:8001`.
- **Banco inesperado:** remova a variável de banco do processo e confira a tabela de
  perfis; nunca apague um banco sem confirmar seu caminho absoluto e possuir backup.
- **Backup já existe:** informe um nome novo; o comando não sobrescreve arquivos.
- **Restauração recusada:** valide backup e manifesto juntos e use destino inexistente.
- **Teste temporário bloqueado pelo Windows:** encerre processos Python que ainda
  mantenham arquivos abertos e execute novamente; não redirecione testes para banco real.

## 13. Limitações conhecidas da V0.3

- Não há dashboard ou analytics de aprendizagem.
- Não há categorias pessoais, autenticação remota, API, notificações ou PWA.
- O servidor é exclusivamente local; hospedagem e PostgreSQL pertencem a marcos futuros.
- Backup/restauração são comandos técnicos; não há interface, agenda, rotação, nuvem ou
  garantia de RPO/RTO nesta versão.
- O HTMX está versionado, mas não é carregado até existir interação que o justifique.
- O workflow de CI de um provedor será definido somente após escolha formal; o gate
  Windows local é a fonte única atual.

## Decisões técnicas

- [`ADR-001 — Toolchain`](docs/ADR-001_Toolchain_Reproduzivel_V0.1.md)
- [`ADR-002 — Perfis e isolamento`](docs/ADR-002_Perfis_e_Isolamento_Django_V0.1.md)
- [`ADR-003 — Identidade, Workspace e tempo`](docs/ADR-003_Identidade_Workspace_e_Tempo_V0.1.md)
- [`ADR-004 — Categorias padrão e seed`](docs/ADR-004_Categorias_Padrao_e_Seed_V0.1.md)
- [`ADR-005 — Logging, correlação e health local`](docs/ADR-005_Logging_Correlacao_e_Health_Local_V0.1.md)
- [`ADR-006 — Interface acessível da fundação`](docs/ADR-006_Interface_Acessivel_da_Fundacao_V0.1.md)
- [`ADR-007 — Backup e restauração mínima SQLite`](docs/ADR-007_Backup_e_Restauracao_Minima_SQLite_V0.1.md)
- [`ADR-008 — Gate único de qualidade`](docs/ADR-008_Gate_Unico_de_Qualidade_V0.1.md)
- [`ADR-009 — Validação final e promoção`](docs/ADR-009_Validacao_Final_e_Promocao_V0.1.md)
