# Task Contract

Status: COMPLETED

## Identification

- Task ID: V0.5-S1
- Product version: V0.5 -- Beta das capacidades V1
- Stage: Fechamento normativo e contratos de invariantes/dados
- Task type: normativa e documental, sem implementação funcional
- Size: M
- Risk: high
- Migration: UNLIKELY; proibida nesta etapa
- A8: deep

## Goal

Transformar decisões normativas necessárias à implementação segura da V0.5 em
contratos explícitos, rastreáveis e testáveis, sem implementar funcionalidade.

## Acceptance Criteria achieved

- OD01 e as parcelas necessárias de OD02 foram resolvidas ou explicitamente
  deferidas; não há decisão humana bloqueante ao desenho das subetapas S2.
- Persistidos contratos de lifecycle, auditoria, invariantes, analytics, reviews,
  Workspace, compatibilidade V0.4.4 e constraints de migration.
- S2 foi reavaliada como XL e decomposta antes de qualquer autorização.
- A8 deep APPROVED, gate GREEN, métricas A7, estado e arquivamento concluídos.

## Closure Evidence

- Contrato canônico: `docs/V0.5_S1_Contratos_Normativos_e_Invariantes.md`.
- Decisões humanas: auditoria sanitizada de exclusão por 90 dias com expurgo
  obrigatório; consolidação somente pessoal → pessoal ativa, com métricas
  atuais pelo alvo e revisões históricas preservadas.
- `V05-OD01`: RESOLVED; `V05-OD02`: PARTIALLY_RESOLVED; OD03–OD06 deferidas a
  S6/S5/S7/S9. S2A–S2D são L/high/EXPECTED e não autorizadas.
- A8 deep: APPROVED, Blocker 0, Major 0; `git diff --check`: PASS.
- Gate de 2026-09-20: exit 0; 338 testes aprovados; 88% de cobertura;
  migrações sem mudanças; formatação, Ruff, mypy, detect-secrets e pip-audit
  GREEN; 116,8 s. A primeira captura de streaming não preservou o exit code; a
  repetição completa e verificável foi GREEN.

## Non-actions

Não houve funcionalidade V0.5, migration, schema, backfill, dado operacional,
teste funcional, commit, push, tag, release ou autorização/início de S2A–S2D.
