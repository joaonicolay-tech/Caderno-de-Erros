# Task Contract

Status: AUTHORIZED

## Identification

- Task ID: V0.4-S4
- Product version: V0.4
- Stage: S4 — Consulta, detalhe e histórico
- Task type: product implementation / consultation / navigation / history
- Size: M
- Risk: medium
- Recommended execution profile: GPT-5.6 Terra, Medium reasoning
- Expected review: standard; elevate to deep review if high risk emerges
- Persistent A4 plan: not initially required; reassess only if the audit shows material complexity beyond M

## Goal

Complete the V0.4 consultation experience by reusing and consolidating existing
listing, search, pagination, detail, and history/timeline capabilities, adding
only the filters and integrations required for the MVP. Users must be able to
navigate from question sets to specific records and understand their history,
without reimplementing S2 analytics, redefining S1 metrics, duplicating the
existing timeline, or anticipating V0.5.

## Context

- `docs/V0.4_S1_Contratos_de_Metricas_e_Reconciliacao.md` remains authoritative
  for metric meaning.
- `docs/V0.4_S2_Interface_Analitica_Interna.md` remains authoritative for
  analytics and reconciled drill-downs.
- `tasks/plans/v04-release-execution-plan.md` identifies the reusable V0.3
  baseline: Workspace-isolated listing, text search in statement/explanation,
  hierarchy/status filters, empty state, pagination of ten items, and total
  ordering `-updated_at, id`; versioned detail and learning timeline exist as
  separate screens.
- Before implementation, audit actual behavior and reuse what is already
  correct. Do not rewrite functional behavior merely to standardize style.
- The exact V0.4 filters are those in P0/RF-065: review status, initial result,
  and relevant error category when supported by the current domain. Combining,
  visible summary, and clearing are in scope; saved/custom filters and personal
  categories are not.
- S3 deliberately deferred complete drill-down destinations to S4. A drill-down
  destination must represent the same universe as its source metric; map filter
  parameters explicitly when necessary.

## Expected Scope

- Consolidate question listing and existing textual search; validate searched
  fields, filters, empty result, Workspace isolation, ordering, and pagination.
- Add only the basic V0.4 filters: review status, initial result, and relevant
  error category where supported.
- Ensure total deterministic ordering and stable pagination, including ties in
  the primary ordering field.
- Connect applicable S3/S2 drill-downs to the consultation experience without
  semantic drift or parallel analytical queries.
- Reuse and complete existing question detail, timeline/history, and navigation
  between dashboard, consultation, detail, and history; preserve context on
  return where appropriate.
- Add accessible empty states for no questions, no search/filter results, no
  relevant history, and no category when that absence is allowed.
- Make only necessary view, template, CSS, documentation, and navigation
  changes. Add proportional tests for listing, search, filters, combinations,
  pagination, ordering, isolation, drill-down, detail, history, missing/foreign
  objects, and empty states.
- Audit query behavior for N+1, required `select_related`/`prefetch_related`,
  duplicate queries, counting/pagination, combined filters, and ordering. Do
  not turn S4 into premature optimization; S8 validates scale/BCR-1.
- Apply A8 review and record actual S4 facts in A7 metrics; duration and quota
  may remain `unknown` and must not be estimated.

## Constraints

- S4 may decide only consultation filters, navigation, presentation, and page
  composition. It must not reinterpret metrics or replace S1/S2 semantics.
- Listing, search, filters, detail, and history must be strictly
  Workspace-isolated. Cross-workspace leakage is a Blocker; foreign or missing
  objects follow the existing project pattern.
- Detail must present the currently supported question, relevant content,
  taxonomy, current state, attempts, reviews, applicable error category, and
  MVP-required metadata. History reuses the existing timeline; do not create a
  parallel mechanism or V0.5 correction history.
- Preserve basic accessibility: labels, keyboard navigation and focus, heading
  hierarchy, semantic tables/lists, clear links, accessible empty states, and
  understandable control names. Preserve current responsive use without a
  global redesign or SPA/complex routing.
- Do not introduce advanced/FTS search, saved filters, personal categories,
  migrations, schema changes, writing rules, review-cycle changes, analytics
  recalculation, or new metrics.

## Protected Scope

- S1 contracts and S2 services/read models, except a proven blocker requiring a
  separately authorized decision.
- S3 dashboard, except a minimal integration necessary for S4 navigation.
- Schema, migrations, writing rules, review cycles, existing historical facts,
  Architecture v1.0, Skills, A7/A8 policies, and `scripts/quality.ps1`.
- V0.5 correction history, saved filters, personal categories, domain/priority,
  mastered/reopen, and every stage from S5 onward.

## Verification

- Test the expected scope proportionally, including multi-page and ordering-tie
  cases, negative Workspace cases, and drill-down semantic equivalence.
- Review for Workspace leakage, semantically incorrect filters/drill-downs,
  unstable ordering, N+1, duplicated history, V0.5 anticipation, parallel
  analytics queries, broken navigation, and basic accessibility.
- The A8 review must be `APPROVED` with no open Blocker or Major; elevate to
  deep review if high risk emerges.
- Run `git diff --check` and the authoritative quality gate:
  `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1`.

## Documentation Impact

Update only the technical documentation and traceability actually affected by
the implemented work. On real completion, archive S4, update applicable state,
and record A7 metrics separately from this authorization bootstrap.

## Done When

- Listing and existing search are consolidated; basic V0.4 filters work in
  combination; pagination has total deterministic ordering.
- Applicable S3/S2 drill-downs are connected to semantically equivalent,
  Workspace-isolated consultation results.
- Complete detail and existing timeline/history are integrated with clear
  navigation and correct accessible empty states.
- There is no structural N+1, no migration/schema change, and no semantic or
  Workspace leakage.
- Focused tests and standard-or-deeper A8 review are GREEN/`APPROVED`, with no
  open Blocker or Major; `git diff --check` and the authoritative gate are
  GREEN.
- S4 is archived only after real completion, `tasks/current.md` then returns to
  `NO_TASK_AUTHORIZED`, and S5 remains unauthorized.

## Evidência de encerramento

- Auditoria inicial: listagem, busca em enunciado/explicação, paginação de dez
  itens com ordering total `-updated_at, id`, detalhe e timeline já existiam e
  foram reutilizados. Os filtros de aprendizagem, retorno de contexto e
  destinos de drill-down eram parciais/ausentes.
- Implementação: a consulta agora aceita, combina e resume filtros GET de
  situação de revisão, resultado inicial e categoria de erro, incluindo o
  resíduo explícito de tentativas válidas incorretas sem classificação. Valores
  de categoria são Workspace-scoped e parâmetros desconhecidos não são
  propagados na navegação.
- Semântica e drill-down: a situação temporal reutiliza `eligible_reviews` da
  camada S2; os links do dashboard para atrasadas/devidas/futuras apresentam o
  mesmo conjunto de questões das revisões pendentes elegíveis, uma por ciclo
  ativo. Não foram conectados totais de tentativas a uma lista de questões, o
  que evitaria uma equivalência falsa de cardinalidade.
- Detalhe/histórico: o detalhe preserva retorno seguro à consulta e aponta para
  a única timeline de aprendizagem existente; não foi criada timeline paralela.
- Testes: 52 testes focados (interface, detalhe, busca, analytics e timeline)
  GREEN; novos cenários cobrem filtros combinados, resíduo, isolamento entre
  Workspaces, drill-down de revisão, retorno e preservação de parâmetros.
- Review A8 padrão: **APPROVED**, sem Blocker ou Major. A revisão verificou
  isolamento, semântica S1/S2, parâmetros, ordering/paginação, ausência de
  N+1 estrutural, acessibilidade e escopo protegido.
- `git diff --check`: aprovado. Gate autoritativo final: **GREEN**, exit code
  0, 292 testes aprovados em 63,04 s e 87% de cobertura; migrations,
  formatação, Ruff, mypy, detect-secrets e pip-audit aprovados.
- Não houve migration, alteração de schema, alteração de S1/S2, nova timeline,
  implementação de S5, commit, push, tag ou release.
