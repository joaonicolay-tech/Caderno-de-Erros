# ADR-001 — Toolchain reproduzível da V0.1

- **Status:** Aceita
- **Data:** 2026-09-01
- **Escopo:** Etapa 1 da V0.1
- **Resolve:** `SDD-ABR-001`, `RD-ABR-001`, `ERR-V01-008` e a parcela de
  versões/ferramentas de `COR-P2-006`
- **Requisitos:** `RNF-018`, `RNF-019`, `RNF-052`, `RNF-053`, `RNF-056`,
  `RNF-063`, `RNF-066`, `RNF-080`
- **Testes aplicáveis nesta etapa:** `CT-099`, `CT-104`; preparação parcial de
  `CT-123` e `CT-127`

## Contexto

O SDD congela Python, Django, Django Templates, HTMX, SQLite e execução local no
Windows. O Gate exige que as versões exatas e as ferramentas sejam decididas no
início da V0.1, antes da criação definitiva do projeto Django. O ambiente de
referência não possuía uma instalação Python utilizável no começo do spike.

## Decisão

| Item | Versão/estado fixado | Licença | Finalidade e justificativa |
|---|---|---|---|
| Python | `3.13.15` CPython x64 | PSF-2.0 | Série madura, ainda suportada e compatível com todo o conjunto escolhido. A versão micro é exata. |
| Django | `5.2.17` LTS | BSD-3-Clause | LTS vigente da arquitetura aprovada; último patch da série 5.2 na data da decisão. |
| Django Templates | integrado ao Django `5.2.17` | BSD-3-Clause | Mantém renderização no servidor sem uma segunda toolchain de frontend. |
| HTMX | `2.0.10` | 0BSD | Série marcada como `latest` pela documentação oficial. A recém-lançada 4.0 não é antecipada. |
| SQLite | `3.53.1`, módulo `sqlite3` do CPython fixado | domínio público | Mantém o banco embutido definido no SDD, sem driver externo; a versão efetiva é verificada pelo gate. |
| uv | `0.12.7` | Apache-2.0 ou MIT | Provisiona o Python, cria `.venv`, resolve e sincroniza o lock no Windows sem exigir Python prévio. |
| Ruff | `0.16.5` | MIT | Um único binário para formatter, imports e lint, evitando Black, isort e Flake8 redundantes. |
| mypy | `2.3.1` | MIT | Type checker estável e suportado pelo `django-stubs` selecionado. |
| django-stubs | `6.1.0` | MIT | Suporta mypy 1.13–2.3, Python 3.11–3.14 e oferece suporte parcial explícito ao Django 5.2. |
| pytest | `9.1.1` | MIT | Executor de testes compatível com Python 3.13 e Windows. |
| pytest-django | `4.14.0` | BSD-3-Clause | Integra pytest ao Django 5.2; a configuração de settings fica para a Etapa 2. |
| pytest-cov | `7.1.0` | MIT | Mede cobertura; as metas por área do Plano de Testes serão aplicadas quando cada área existir. |
| detect-secrets | `1.5.0` | Apache-2.0 | Varredura local de arquivos versionados e novos para `RNF-018`/`CT-099`. |
| pip-audit | `2.10.1` | Apache-2.0 | Consulta vulnerabilidades conhecidas no ambiente resolvido para `RNF-019`/`CT-104`. |

As dependências diretas estão fixadas por igualdade em `pyproject.toml`; as
transitivas e seus artefatos são fixados por `uv.lock`. O projeto é marcado como
virtual (`package = false`) até a Etapa 2, portanto esta decisão não cria pacote,
`manage.py` ou scaffolding Django.

O HTMX será armazenado localmente como arquivo estático somente quando a camada
de apresentação for criada. Não se adiciona Node.js, npm, bundler nem pacote
Python de terceiros para HTMX nesta etapa. O artefato minificado oficial fica
identificado pelo SRI
`sha384-H5SrcfygHmAuTDZphMHqBJLc3FhssKjG7w/CeCpFReSfwBWDTKpkzPP8c+cLsK+V`;
a etapa que o incorporar deverá verificar esse hash.

## Compatibilidade comprovada e matriz de referência

- Django 5.2 suporta Python 3.13; o próprio Django recomenda o patch mais recente
  de cada série suportada.
- `uv.lock` exige artefatos compatíveis com Windows x64 e `uv sync --locked`
  comprova a resolução sem conflitos.
- Chrome `152.0.7977.65` e Edge `152.0.4191.53` são as versões estáveis instaladas
  e vigentes no ambiente de referência em 2026-09-01. `RNF-063` exige novo
  registro das versões vigentes no gate da entrega V0.1; não há interface para
  testar nesta etapa.
- Português e Unicode são validados no smoke do runtime. Persistência, busca e
  exportação de Unicode dependem das etapas em que banco e funcionalidades
  correspondentes forem implementados.

## Comandos normativos

```powershell
uv sync --locked
uv lock --check
uv run --locked ruff format --check .
uv run --locked ruff check .
uv run --locked mypy
uv run --locked pytest --cov=src --cov-report=term-missing
uv run --locked detect-secrets-hook --baseline .secrets.baseline <arquivos>
uv run --locked pip-audit --local --strict
.\scripts\quality.ps1
```

Enquanto não houver arquivos Python, o comando único valida as versões dos
executáveis de mypy e pytest, em vez de simular uma suite inexistente. Assim que
a Etapa 2 criar código, ausência ou falha de testes passa a bloquear o comando.

## Política de vulnerabilidades e segredos

- qualquer vulnerabilidade conhecida encontrada por `pip-audit` bloqueia por
  padrão, o que é mais estrito que o mínimo crítico de `RNF-019`/`CT-104`;
- uma exceção exige registro explícito de identificador, alcance, exploração no
  contexto local, mitigação, responsável, aprovação e prazo de remoção;
- a baseline de segredos pode conter somente falsos positivos inspecionados;
  segredo real nunca é aceito na baseline;
- `.env`, bancos, logs e backups locais são excluídos do versionamento.

Isso resolve para a V0.1 o ponto `PT-ABR-010` sem mudar requisitos de produto.

## Evidências da Etapa 1

Em Windows 11 x64, em 2026-09-01:

- `uv lock --check` aprovou um lock de 52 pacotes resolvidos, sendo 51 instalados
  (o projeto virtual é o item restante);
- duas sincronizações independentes por `uv sync --locked` produziram inventários
  de 51 pacotes, com zero diferença entre versões;
- o smoke confirmou Python `3.13.15`, Django `5.2.17`, SQLite `3.53.1` e ida/volta
  UTF-8 de texto em português;
- Ruff aprovou formatação e lint; mypy `2.3.1` e pytest `9.1.1` iniciaram no
  ambiente fixado;
- `detect-secrets` retornou zero achados no repositório, excluindo somente
  metadados Git, ambientes/cache locais e o lock já coberto pelo inventário;
- `pip-audit --local --strict` retornou `No known vulnerabilities found`;
- Chrome `152.0.7977.65` e Edge `152.0.4191.53` foram localizados no Windows de
  referência, coerentes com os canais estáveis vigentes.

Não houve teste Django, migração, banco da aplicação, template ou navegador: esses
artefatos não existem legitimamente na Etapa 1.

## Consequências e itens deliberadamente adiados

- O plugin do `django-stubs` será ativado na Etapa 2, quando existir um módulo de
  settings real; apontá-lo agora exigiria scaffolding proibido.
- Perfis Django, migrações, banco isolado, health, logging, backup, layout e
  testes funcionais pertencem às etapas seguintes da V0.1.
- A versão efetiva do SQLite é uma propriedade do runtime CPython e o gate exige
  exatamente `3.53.1`; pragmas, WAL e contenção pertencem aos marcos definidos
  no SDD e no Gate.
- Testes em Chrome/Edge, cobertura por área e smoke de release serão executados
  quando houver aplicação. Esta etapa apenas fixa e valida sua toolchain.
- HTMX 4, PostgreSQL, tags, questões, tentativas, revisões, dashboard, domínio,
  prioridade, API, autenticação remota, empacotador desktop e módulos futuros não
  pertencem à Etapa 1 e não são antecipados.

## Fontes técnicas primárias consultadas

- Python: <https://www.python.org/downloads/release/python-3130/>
- Django 5.2 e compatibilidade Python: <https://docs.djangoproject.com/en/5.2/faq/install/>
- Releases Django 5.2: <https://docs.djangoproject.com/en/5.2/releases/>
- HTMX 2.0.10: <https://htmx.org/docs/>
- uv: <https://docs.astral.sh/uv/getting-started/installation/>
- Lock do uv: <https://docs.astral.sh/uv/concepts/projects/sync/>
- django-stubs: <https://github.com/typeddjango/django-stubs>
- Pacotes e metadados: <https://pypi.org/>
