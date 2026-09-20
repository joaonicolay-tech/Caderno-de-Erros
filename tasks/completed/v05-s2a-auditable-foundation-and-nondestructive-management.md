# Task Contract

Status: COMPLETED

## Identification

- Task ID: V0.5-S2A
- Product version: V0.5 -- Beta das capacidades V1
- Stage: Fundação auditável e gestão não destrutiva
- Task type: implementação funcional e migração conservadora
- Size: L
- Risk: high
- Migration: EXPECTED
- A4 plan: required and completed before implementation
- A8: deep

## Goal

Entregar a fundação de dados e serviços transacionais auditáveis para
categorias pessoais e sua consolidação, reagendamento manual de Review e
inclusão manual de Question inicialmente correta no ciclo de revisão, sem
reescrever fatos históricos ou alterar as semânticas V0.4.

## Acceptance Criteria achieved

- `AuditEvent` funcional é mínimo, sanitizado, Workspace-scoped e append-only;
  os cinco eventos S2A são atômicos com suas mutações.
- Categorias pessoais suportam create/rename/archive/merge não destrutivos;
  cadeias resolvem ao alvo ativo sem reescrever FKs históricas nem duplicar
  analytics, e categorias padrão permanecem protegidas.
- Review pendente pode ser reagendada para hoje/futuro no fuso do Workspace,
  preservando `first_due_date`, estágio, policy, ciclo e Attempts.
- Inclusão manual exige INITIAL correta/VALID existente, cria ciclo `MANUAL` e
  D1 sem criar Attempt nem aumentar `performed`.
- Guards de Workspace, lifecycle, atomicidade, optimistic locking e
  concorrência proporcional foram cobertos por testes negativos e rollback.
- Upgrade V0.4.4-equivalente, reverse seguro sem fatos S2A, backup/restore
  isolado, reconciliação e checker read-only com 20 checks foram comprovados.
- S2B, S2C e S2D não foram implementadas ou autorizadas.

## Closure Evidence

- Plano A4: `tasks/plans/v05-s2a-auditable-foundation-plan.md`.
- Resultado integrado: `quality/v05-s2a-foundation-result.md`.
- Proteção aditiva das migrations: `quality/v05-s2a-migrations.json`, sem
  alterar o manifesto histórico V0.3.
- Regressão focada: 170 testes aprovados; teste do verificador: 20 aprovados.
- A8 deep: APPROVED, Blocker 0, Major 0, Minor 0 aberto.
- Gate de 2026-09-20: segunda execução GREEN, exit 0; 356 testes aprovados em
  113,51 s; cobertura global 87%; duração total 157,6 s; `pip-audit` sem
  vulnerabilidades conhecidas.
- Primeira execução do gate: RED no controle de rastreabilidade das migrations;
  corrigida pelo manifesto adicional S2A antes da repetição completa.

## Non-actions

Não houve VOID/substituição/rebuild de Attempt, correção de gabarito,
delete/retention/expurgo, UI geral, filtros salvos, event sourcing,
infraestrutura distribuída, commit, push, tag, release ou autorização/início
de V0.5-S2B, S2C ou S2D.
