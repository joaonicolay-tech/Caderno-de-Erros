# Task Contract

Status: AUTHORIZED

## Identification

- Task ID: V0.4.2-UX1
- Product version: v0.4.2 (future patch release; tag creation is not authorized)
- Stage: UX1 â€” Enriquecimento da Fila de revisÃµes
- Task type: localized UX improvement
- Size: M
- Risk: medium
- Recommended execution model: GPT-5.6 Terra
- Recommended reasoning: Medium
- Expected review: standard A8

## Goal

Enriquecer a Fila de revisÃµes com o conjunto mÃ­nimo de contexto Ãºtil, derivado
do domÃ­nio existente, para permitir identificar e priorizar visualmente cada
revisÃ£o sem abrir todos os itens, preservando a simplicidade, legibilidade e
coerÃªncia do MVP.

## Context

A fila atual agrupa revisÃµes pendentes em Atrasadas, Hoje e Futuras e mostra
principalmente estÃ¡gio e data. A execuÃ§Ã£o deve primeiro auditar a view,
service/selector, template, rotas, queries, testes e as relaÃ§Ãµes reais entre
ReviewCycle/Review, Question, disciplina, assunto, tentativa e resultado
anterior. Descobrir o que jÃ¡ estÃ¡ disponÃ­vel sem alterar regras de domÃ­nio ou
inventar campos. A data civil e o fuso do Workspace continuam sendo a fonte da
semÃ¢ntica temporal.

## Acceptance Criteria

- Cada item permite identificar o que serÃ¡ revisado, a disciplina/assunto
  quando disponÃ­veis e Ãºteis, o estÃ¡gio, a data prevista e a situaÃ§Ã£o temporal.
- Atrasadas, Hoje e Futuras permanecem semanticamente corretos; estÃ¡gio
  D1/D7/D14/D30 e data continuam claros.
- A implementaÃ§Ã£o seleciona apenas informaÃ§Ãµes confiÃ¡veis e Ãºteis do domÃ­nio
  existente: identificador ou trecho curto da questÃ£o, disciplina, assunto,
  estÃ¡gio, data, situaÃ§Ã£o temporal, resultado/tentativa anterior e dias de
  atraso sÃ£o candidatos, nÃ£o requisitos cegos.
- Texto longo da questÃ£o Ã© apresentado de modo curto e legÃ­vel; o conteÃºdo
  completo permanece no detalhe/revisÃ£o.
- Metadados ausentes nÃ£o exibem placeholders enganosos nem quebram a fila.
- Rotas, links, abertura da revisÃ£o, ordenaÃ§Ã£o determinÃ­stica e isolamento por
  Workspace permanecem corretos.
- Nenhum N+1 Ã© introduzido; os dados adicionais usam carregamento relacional
  eficiente somente quando necessÃ¡rio.
- Empty states permanecem claros e acessibilidade, teclado, foco, semÃ¢ntica,
  contraste, responsividade e zoom de 200% permanecem adequados.

## Expected Scope

- Auditoria e mudanÃ§a mÃ­nima, se necessÃ¡ria, na view, service/selector e
  template diretamente responsÃ¡veis pela Fila de revisÃµes.
- Uso das relaÃ§Ãµes existentes de ReviewCycle/Review, Question, disciplina,
  assunto e tentativa/resultados somente para apresentaÃ§Ã£o contextual.
- Testes focados da fila, incluindo grupos temporais, metadados ausentes,
  questÃ£o longa, navegaÃ§Ã£o, isolamento de Workspace e prevenÃ§Ã£o de N+1.
- ObservaÃ§Ãµes objetivas de teste manual no navegador com revisÃµes atrasadas,
  Hoje no estado real e futuras com contextos diferentes.

## Protected Scope

- CÃ¡lculo e semÃ¢ntica de D1/D7/D14/D30, ReviewCycle, overdue/due/future,
  data civil/fuso do Workspace e ordenaÃ§Ã£o temporal.
- SemÃ¢ntica S1, AnalyticsService S2, dashboard S3, lÃ³gica de tentativa,
  backup, checker e arquitetura vigente.
- Regras de domÃ­nio, rescheduling, mastered/reopen, prioridade,
  personalizaÃ§Ã£o/filtros salvos, notificaÃ§Ãµes, gamificaÃ§Ã£o, dashboard nova,
  redesign geral e V0.5.
- Schema, migrations e campos persistentes novos para enriquecimento visual.

## Constraints

- NÃ£o inventar dados, campos, mÃ©tricas ou regras analÃ­ticas; avaliar e usar
  somente o conjunto mÃ­nimo que o domÃ­nio real forneÃ§a de modo eficiente.
- Se uma migration parecer necessÃ¡ria, parar e justificar antes de prosseguir.
- NÃ£o ocultar achado funcional dentro da mudanÃ§a visual: registrÃ¡-lo
  separadamente.
- Reutilizar padrÃµes e classes visuais existentes; nÃ£o criar design system novo.
- Tratar `v0.4.1` como tag histÃ³rica e imutÃ¡vel. Ela aponta inicialmente para
  `9aebb07f22d190666b26bb7b54d5ac447ac71de4`; nÃ£o mover, apagar, recriar,
  alterar nem fazer force-push. Confirmar por leitura ao concluir.
- NÃ£o criar, mover ou alterar a tag `v0.4.2`. A criaÃ§Ã£o requer implementaÃ§Ã£o,
  testes, teste manual, review, gate, checkpoint Git humano e autorizaÃ§Ã£o
  explÃ­cita posterior.

## Verification

- Executar testes focados que cubram Atrasadas, Hoje, Futuras, contexto de
  disciplina/assunto, ausÃªncia de metadados, questÃ£o longa, navegaÃ§Ã£o,
  Workspace, empty states e contagem de queries sem N+1.
- Realizar teste manual objetivo de hierarquia, clareza, densidade,
  responsividade, zoom e links, sem fabricar feedback humano.
- Executar review A8 padrÃ£o, com foco em clareza, densidade, campos enganosos,
  N+1, Workspace leakage, acessibilidade, responsividade, semÃ¢ntica temporal,
  scope creep e migration desnecessÃ¡ria; requer APPROVED sem Blocker/Major.
- Executar `git diff --check` e
  `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1`;
  o gate deve ficar GREEN.
- Confirmar por leitura que `v0.4.1` ainda aponta para o commit inicial e que
  `v0.4.2` nÃ£o existe.

## Documentation Impact

Atualizar somente evidÃªncias de quality, estado e arquivamento exigidos pelo
encerramento, se a tarefa for concluÃ­da; nenhuma documentaÃ§Ã£o de produto Ã©
esperada salvo mudanÃ§a de comportamento comprovada.

## Done When

- A fila foi auditada e o contexto exibido foi selecionado a partir do domÃ­nio
  real, sem dados fictÃ­cios ou novas regras.
- Itens atrasados, de Hoje e futuros tÃªm contexto suficiente, mantÃªm seus
  grupos corretos e preservam estÃ¡gio e data claros.
- A questÃ£o Ã© identificÃ¡vel sem abrir cada item, e disciplina/assunto aparecem
  quando disponÃ­veis e Ãºteis, sem degradar ausÃªncia de metadados.
- NÃ£o houve alteraÃ§Ã£o de semÃ¢ntica de revisÃ£o, N+1, leakage de Workspace,
  migration ou schema.
- Acessibilidade, responsividade e zoom estÃ£o validados proporcionalmente;
  testes focados, teste manual, review A8, `git diff --check` e gate completo
  estÃ£o GREEN.
- `v0.4.1` permanece inalterada, `v0.4.2` ainda nÃ£o existe, a tarefa Ã©
  arquivada e `tasks/current.md` retorna a `NO_TASK_AUTHORIZED` no
  encerramento posterior.
- V0.5 permanece nÃ£o autorizada e nÃ£o iniciada.

## Closure Evidence

- Audit: `list_review_queue` remained the sole temporal classifier through `ReviewStatusPolicy`; the view and route were unchanged.
- Chosen context: current question stem (visually truncated to 160 characters), existing discipline and subject, and existing stage/date/group state. Previous result, last attempt and overdue-day count were rejected because they add density or require separate semantics/queries.
- Query safety: selector uses `select_related` for question/taxonomy/cycle and one filtered `Prefetch` for the current revision. The focused query regression confirms the count is constant from one to six items.
- Focused tests: `tests/test_stage4_learning.py` — 8 passed.
- Manual browser check (127.0.0.1, controlled local data): one overdue, empty Today, four future D1 on the same date and one future D7 were visually distinguishable; the overdue link opened its existing review route. At 360 px, text wrapped without horizontal overflow or overlap. The browser automation could not produce an observable 200% zoom change, so exact zoom validation is recorded as a limitation rather than claimed.
- Accessibility: heading hierarchy, semantic sections/articles, textual temporal states, native links, existing visible focus styling and keyboard-reachable review link were inspected. No full WCAG claim is made.
- Migration check: `python manage.py makemigrations --check --dry-run` — no changes detected.
- A8 standard review: APPROVED; no Blocker or Major.
- `git diff --check`: PASS.
- Authoritative gate: GREEN, exit 0; 335 passed, 88% coverage; Ruff, mypy, detect-secrets and pip-audit passed on 2026-09-19.
- Tags: `v0.4.1` remains annotated object `9aebb07f22d190666b26bb7b54d5ac447ac71de4` pointing to commit `acbb497dbdc71f8a3d7893ae4772a87231c281f0` (the HF1 checkpoint); `v0.4.2` is absent. The contract had these hashes inverted; no tag was created or altered.
- Non-actions: no migration, schema/domain/temporal change, V0.5 work, commit, push, tag or release.
