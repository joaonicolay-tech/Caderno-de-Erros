# V0.2 — Etapa 8 — Evidência automatizada

Data: 7 de setembro de 2026 (UTC)

## Resultado

- `CT-141`: PASS — fixture explícita, sintética, sem dados pessoais, determinística
  para a semente `v02-catalog-demo-001`, idempotente e limitada ao perfil `test`.
  Cria 1 taxonomia em três níveis, 1 Board, 1 Exam, 1 Source, 3 questões
  (DRAFT/ACTIVE/ARCHIVED), 3 revisões, 12 alternativas e 1 origem.
- `CT-143`: PASS — backup/recovery reconcilia contagens e relações V0.2; o teste
  confirma taxonomia, catálogo de origem, estados, revisão corrente, alternativas,
  gabarito e origem. Corrupção de byte é rejeitada antes da criação do destino.
- `CT-081`, `CT-123`: PASS — o gate aplicou todas as migrations em SQLite vazio e
  `makemigrations --check --dry-run` não detectou alterações.
- `CT-082`, `CT-122`: PASS — a regressão inclui os testes de upgrade partindo da
  baseline V0.1, preservando dados existentes e migrations protegidas.
- Regressão V0.1/V0.2: PASS — 192 testes aprovados.
- `CT-142` automatizável: PASS — semântica, controles nativos, labels/erros,
  foco visível, skip link, layout responsivo e contraste permanecem cobertos pelos
  testes de interface do catálogo.

## Gate autoritativo

`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1`

Resultado final: **GREEN**, exit code **0**, em 61,8 s (reexecutado após o registro
manual de `CT-142`).

- cobertura global: 86%; mínimo de 80% por módulo de domínio/regra: atendido;
- Ruff e mypy: aprovados;
- detect-secrets: aprovado;
- pip-audit: aprovado, sem vulnerabilidades conhecidas;
- rastreabilidade e hashes das migrations protegidas: aprovados; `git diff --check`
  também foi executado separadamente e aprovado.

## CT-142 manual — PASS integral

Data do registro: 7 de setembro de 2026.

Evidência manual fornecida pelo usuário, realizada no Windows em Chrome e Edge
vigentes, com dados sintéticos e sem uso de mouse. O resultado foi **PASS** para ambos
os navegadores nos seguintes itens do roteiro de `CT-142`:

- navegação somente por teclado, ordem coerente de foco, foco visível e skip link;
- labels, erros e feedback acessíveis, inclusive feedback que não depende somente de
  cor;
- gestão da taxonomia, cadastro rápido, rascunho/ativação, detalhe, edição e
  arquivamento;
- listagem, busca e filtros;
- viewport aproximado de 360 px e zoom de 200%, sem rolagem horizontal indevida,
  sobreposição ou controles/conteúdo inacessíveis.

Não foi reportado defeito durante a validação. Portanto, `CT-142` está **PASS
integralmente** e não há P0/P1 aplicável aberto.
