# V1.0-S4 — Acessibilidade, navegadores e usabilidade

## Decisão

`S4_COMPLETED`. A pendência do perfil Brave foi eliminada por nova
`HUMAN_MANUAL_EVIDENCE`: Brave 1.96.59 oficial, Windows 11, 64 bits, todas as
extensões desabilitadas; o smoke final reportou PASS em dashboard/início,
cadastro de erro/questão, tentativa, revisão, lista/consulta e dados, sem
problemas. Essa evidência completa a HME anterior; a proveniência de cada
sessão e os limites do que foi reexecutado estão discriminados abaixo.

Brave 1.96.59 é o browser oficialmente validado para V1 nesta execução.
Chrome permanece não validado; Edge/Firefox seguem opcionais e não executados;
Safari é N/A. Blocker 0, Major 0, Minor 0. A8 standard: `APPROVED`.
Nenhuma mudança funcional ou migration foi feita.

## Baseline e autorização

- Data: 29 de setembro de 2026.
- Contrato: `V1.0-S4`, `AUTHORIZED`, Size `M`, Risk `medium`,
  Migration `NO` prevista.
- Antes desta retomada: `HEAD = origin/main =
  dfac3e6315f233c36c539e357b6fb4b7c5ba9d5d`; a working tree tinha alterações
  documentais preexistentes em `PROJECT_STATE.md`, `tasks/current.md` e os
  dois artefatos S4.
- S1–S3 concluídas; S5/S6+ não autorizadas.
- A7 previsto: `GPT-6 Luna High`. A regra exige recomendação
  `GPT-6 Luna xHigh` antes de correção material se surgir ambiguidade relevante
  de acessibilidade, diferença de browser difícil de explicar, comportamento
  visual/foco não trivial, usabilidade ambígua, exceção difícil de classificar
  ou correção de impacto amplo. Não surgiu finding dessa natureza; sem
  escalonamento.
- Nenhum commit, push, tag ou release.

## Política aplicável

A decisão humana persistida em `tasks/current.md` e registrada em
`docs/V1.0_Adendo_V10-D2_Matriz_de_Browsers_S4.md` exige um PASS completo em
Brave atual OU Chrome atual no Windows 11. A condição Brave sem extensões
permanece. Edge e Firefox atual/anterior são opcionais; Safari é N/A.
Responsividade 360–1920 px e os demais critérios S4 permanecem.

## Evidência manual — jornadas

A evidência é `HUMAN_MANUAL_EVIDENCE` do responsável, não execução
independente do Codex.

Na sessão manual anterior, em Brave 1.96.59 oficial, Windows 11, 64 bits, com
a extensão ChatGPT habilitada, o responsável reportou PASS nas dez jornadas:

| Jornada | Resultado informado |
| --- | --- |
| Dashboard/Início | PASS |
| Cadastro de erro/questão | PASS |
| Edição de erro/questão | PASS |
| Tentativa | PASS |
| Correção de tentativa | PASS |
| Revisão | PASS |
| Lista/consulta | PASS |
| Histórico/detalhe | PASS |
| Categorias/taxonomia | PASS |
| Dados | PASS |

Na sessão final em Brave 1.96.59 oficial, Windows 11, 64 bits, com todas as
extensões desabilitadas, o responsável executou o smoke abaixo. Todos PASS;
nenhum problema foi encontrado:

| Jornada reexecutada sem extensões | Resultado |
| --- | --- |
| Dashboard/Início | PASS |
| Cadastro de erro/questão | PASS |
| Tentativa | PASS |
| Revisão | PASS |
| Lista/consulta | PASS |
| Dados | PASS |

O reteste final foi direcionado à única pendência de condição de execução.
Ele não é apresentado como nova execução das dez jornadas: edição,
correção de tentativa, histórico/detalhe e categorias/taxonomia permanecem
respaldadas pela HME anterior. O conjunto satisfaz a matriz conforme a decisão
humana que aceita evidência manual do responsável e o reteste final sem
extensões para eliminar a ressalva de perfil. Não se atribui interferência ou
falha à extensão ChatGPT.

## Acessibilidade, usabilidade e responsividade — HME anterior preservada

O responsável reportou na evidência manual anterior:

- navegação por teclado: PASS;
- Tab: PASS; Shift+Tab: PASS; Enter/Space: PASS;
- foco visível: PASS; keyboard trap: nenhum observado;
- formulários/labels: PASS;
- erros de validação compreensíveis: PASS;
- zoom 200%: PASS;
- estados especiais: PASS;
- Windows Narrator no dashboard: PASS;
- Windows Narrator em formulário: PASS;
- nenhum finding funcional, visual, de teclado ou acessibilidade;
- viewports 360 x 800, 768 x 900, 1366 x 768 e 1920 x 1080: PASS;
- em cada viewport foram inspecionados dashboard, navegação/menu, formulário
  e lista/consulta; nenhum problema funcional, bloqueio de uso ou finding
  visual foi reportado.

A proveniência dessa HME permanece associada à sessão com ChatGPT habilitado;
a sessão final sem extensões reexecutou as seis jornadas listadas acima.
Nenhum screenshot ou medição não fornecida foi inferido.

A inspeção estática previamente registrada encontrou `lang="pt-BR"`, skip
link, landmarks, foco visível, reflow e foco de alto contraste; os testes
existentes cobrem semântica, associações de erro, confirmação/cancelamento,
foco visível estático, limites de layout e algumas combinações de contraste.
Isso é evidência estática/automatizada e não se apresenta como nova execução
manual. Não surgiu finding visual/contraste reportado.

## Matriz final de browsers

| Browser | Resultado | Proveniência / limite |
| --- | --- | --- |
| Brave | **VALIDADO OFICIALMENTE PARA V1** | HME; Brave 1.96.59 oficial, 64 bits, Windows 11; smoke final com todas as extensões desabilitadas, combinado à evidência manual anterior |
| Chrome | `NOT_EXECUTED`; não validado | Processo caiu durante tentativa de automação, conforme relato do responsável |
| Edge | `NOT_EXECUTED / OPTIONAL` | Não bloqueia S4 |
| Firefox atual | `NOT_EXECUTED / OPTIONAL` | Não bloqueia S4 |
| Firefox imediatamente anterior | `NOT_EXECUTED / OPTIONAL` | Não bloqueia S4 |
| Safari | `N/A` | Plataforma oficial Windows 11 x64 |

O Codex não abriu browser nem repetiu automação visual nesta retomada.

## Incidentes, findings e mudanças

- A automação visual CUA falhou anteriormente com
  `helper_unknown_error: apply deny-read ACLs`; não foi repetida.
- O responsável relata crash do processo Chrome durante automação. É incidente
  de automação, sem evidência de defeito do produto; Chrome não recebe PASS.
- Na preparação, o responsável relata
  `OperationalError: no such column: errors_error_category.category_kind`.
  O banco local ainda não tinha aplicado
  `errors.0003_errorcategory_category_kind_and_more`. O responsável criou
  backup local e aplicou essa migration existente. Não foi criada migration
  nova, alteração de schema de produto ou artefato de banco versionado.
- A ressalva anterior de execução Brave com extensão ChatGPT habilitada foi
  eliminada pelo smoke final reportado sem extensões.
- Findings de produto reproduzíveis: nenhum reportado ou reproduzido.
- Blocker: 0; Major: 0; Minor: 0.
- Mudanças funcionais: nenhuma. Testes futuros: nenhum criado. Migrations
  criadas: nenhuma. Redesign/feature nova: nenhuma.

## Follow-up automatizado

`DEFERRED FOLLOW-UP`, preservado sem implementação e sem task ativa:

1. Regressão para empty states, erros de validação, mensagens de sucesso/erro,
   confirmação, cancelamento e recovery.
2. Testes responsivos em 360 px, 768 px, desktop representativo e 1920 px para
   overflow, clipping, overlap, controles inacessíveis e dependência horizontal
   indevida.

Não bloqueia S4 nem autoriza S5/S6.

## A8 standard

`APPROVED`.

Revisados autorização/escopo, jornadas, browser matrix e condição sem
extensões, distinção entre HME e execução Codex, teclado/foco, labels/erros,
semântica, contraste aplicável, zoom, Narrator, responsividade, findings,
limitações ambientais, incidentes, follow-up, testes, ausência de feature,
redesign ou migration e fronteira de S5/S6. Evidência suficiente para
`S4_COMPLETED`; Blocker 0 e Major 0. A8 não recomenda escalonamento para
Luna xHigh.

## Testes e gate

- Nenhum teste novo ou focado foi criado/executado; nenhum defeito de produto
  foi reportado.
- Gate autoritativo final: **GREEN**, exit code `0`; 510 testes passaram em
  227,29 s; cobertura global 86%; cobertura mínima de domínio aprovada; duração
  total 285,8 s.
- Lock/sync, runtime, perfis de desenvolvimento/teste/produção local,
  detecção de migrations inesperadas (`No changes detected`), migrations em
  banco isolado, formatação (403 arquivos), Ruff, mypy (194 fontes),
  detect-secrets e pip-audit (`No known vulnerabilities found`) passaram.
  Nenhum warning relevante foi reportado pelo gate.
- Comando: `powershell -NoProfile -ExecutionPolicy Bypass -File
  .\scripts\quality.ps1`.
- `git diff --check`: PASS, exit code `0` após o fechamento. Git exibiu somente
  o aviso de normalização CRLF de `tasks/current.md`; não houve erro de
  whitespace.
- `git status --short` após o fechamento:
  - ` M PROJECT_STATE.md`
  - ` M tasks/current.md`
  - `?? docs/V1.0_Adendo_V10-D2_Matriz_de_Browsers_S4.md`
  - `?? quality/v10-s4-accessibility-browser-usability-result.md`
  - `?? tasks/completed/v10-s4-accessibility-browser-usability.md`
- `HEAD = origin/main = dfac3e6315f233c36c539e357b6fb4b7c5ba9d5d`.
- Nenhuma browser automation, interação UI ou migration foi executada pelo
  Codex.

## Encerramento e limites

- Resultado: `S4_COMPLETED`.
- S1–S4 concluídas; S5/S6 continuam **NOT AUTHORIZED** e não foram iniciadas.
- Brave 1.96.59 é o browser oficialmente validado para V1; Chrome permanece
  não validado.
- `PROJECT_STATE.md` atualizado; contrato arquivado em
  `tasks/completed/v10-s4-accessibility-browser-usability.md`;
  `tasks/current.md` retorna a `NO_TASK_AUTHORIZED`.
- Sem migration nova, alteração funcional, commit, push, tag ou release.
