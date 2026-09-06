# V0.2 — Etapa 3 — Catálogo de Origem

## Identificação

- Versão: V0.2.
- Etapa: 3.
- Nome: Catálogo de Origem.
- Status: concluída.
- Execução: realizada em novo chat, conforme o fluxo operacional.

## Objetivo

Criar a fundação persistente e interna do catálogo de origem da V0.2, composta
por `Board`, `Exam` e `Source`, dentro de `SDD-MOD-003`, com isolamento por
Workspace, normalização, criação/reuso, arquivamento e evolução reproduzível do
banco.

## Escopo autorizado e executado

- criado o módulo Django `questions` somente com a estrutura da etapa;
- implementados `Board`, `Exam` e `Source` conforme o modelo aprovado;
- criada a migration congelada `questions/0001_origin_catalog`, dependente de
  `accounts/0001_initial`;
- implementados validadores, serviços internos e selectors para criar,
  reutilizar, consultar e arquivar referências de origem;
- aplicados `name_key`, unicidades ativas, índices, estados, controle de versão
  e FKs protegidas;
- validado `Exam.year` entre 1900 e o ano civil corrente do Workspace + 2 por
  `Clock`/`Calendar`;
- garantido isolamento integral entre Workspaces;
- ampliado o manifesto intermediário apenas com evidências desta etapa;
- criados testes unitários, de integração, migrations, upgrades e regressão.

## Fora de escopo preservado

- nenhuma interface independente de origem foi criada;
- `Question`, `QuestionRevision`, `Alternative` e `QuestionOrigin` não foram
  criados;
- `questions/0002_question_catalog` não foi criada;
- nenhuma capacidade de questão, aprendizagem, tags, busca ou métricas foi
  antecipada.

## Constraints e invariantes comprovadas

- nomes usam trim, colapso de espaços, NFC e `casefold`, preservando acentos;
- Board é única por `(workspace, name_key)` enquanto ativa;
- Exam é único pela chave lógica `(workspace, board?, name_key, year?)`, com
  tratamento explícito de componentes nulos, enquanto ativo;
- Source é única por `(workspace, source_type, name_key)` enquanto ativa;
- estados, coerência de `archived_at`, `lock_version`, tipos de Source e ano
  mínimo possuem constraints SQLite;
- o limite anual superior usa o fuso do Workspace e fonte de tempo injetável;
- Board opcional de Exam precisa estar ativa e no mesmo Workspace;
- arquivamento preserva identidade e histórico; FKs existentes usam `PROTECT`.

## Evidência final

- testes específicos: 19 aprovados em `tests/test_origin_catalog.py`;
- CTs: `CT-073`, `CT-074`, `CT-081`, `CT-082` e parcela aplicável de `CT-138`;
- regressão/gate: 144 testes aprovados;
- cobertura: 85% global; Questions Models 92%, Services 91%, Validators 91% e
  Selectors 100%;
- `makemigrations --check --dry-run`: sem alterações;
- banco vazio: `questions.0001_origin_catalog` aplicada com sucesso;
- upgrades desde `v0.1.0` e desde a Etapa 2: dados preservados;
- gate autoritativo: GREEN, exit code 0;
- Ruff, mypy, segredos, `pip-audit` e `git diff --check`: aprovados;
- migrations históricas: hashes de `accounts/0001_initial`,
  `errors/0001_initial` e `taxonomy/0001_initial` preservados;
- P0/P1 aplicável aberto: nenhum.

## Próximo estado autorizado

V0.2 — Etapa 4 — Catálogo de Questões está liberada, não iniciada, e deve ser
executada somente em novo chat a partir de `tasks/current.md`.
