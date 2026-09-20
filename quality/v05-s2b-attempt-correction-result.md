# V0.5-S2B — Resultado da correção estrutural de Attempt

- Data: 2026-09-20
- Tarefa: `V0.5-S2B`
- Baseline de execução: `main` em
  `8206a355d1ca602b6d953676997a88da1e6d032c`; tag `v0.4.4` documentada em
  `46e887e0c4fa4dd6f7e128ab63802223d99c9e29`.
- Estado inicial da árvore: somente `tasks/current.md`, com a autorização S2B,
  estava modificado.
- Resultado: **APPROVED / GREEN**.

## Preparação e plano A4

O baseline focado anterior à implementação aprovou 118 testes. O plano
`tasks/plans/v05-s2b-attempt-correction-plan.md` foi fechado antes da primeira
edição funcional e auditou schema, migrations, lifecycle, grafo, projeções,
Workspace, atomicidade, concorrência, idempotência, upgrade, rollback,
recovery, checker, testes e gate.

A auditoria confirmou que `Attempt` já possuía os campos e as unicidades
necessários para void e replacement; por isso não foi criada migration
artificial em `attempts`. Foram necessárias somente duas migrations aditivas:

- `operations.0002_attempt_audit_events`, para os eventos sanitizados
  `ATTEMPT_VOIDED` e `ATTEMPT_REPLACED` e a entidade `ATTEMPT`;
- `reviews.0004_attempt_correction_projection`, para origem
  `ATTEMPT_CORRECTION`, estado `SUPERSEDED`, `superseded_at` nullable e as
  constraints correspondentes.

Não há backfill funcional. O reverse é seguro antes de fatos S2B; depois de
uma correção real, a recuperação suportada é restore de backup, porque o
reverse perderia estado necessário à reconstrução.

## Implementação comprovada

- `AttemptCorrectionService` exige Workspace, motivo codificado, confirmação
  da ponta esperada e fato `VALID`; void usa transição CAS e replacement cria
  novo fato imutável com o mesmo contexto de Question/revision/Review/tipo.
- `resolve_attempt_chain` centraliza a resolução iterativa e determinística da
  ponta efetiva, rejeita ciclo, branch, autorreferência, contexto divergente e
  múltiplas pontas, e mantém quantidade constante de queries no cenário
  coberto.
- A operação completa é atômica: void, replacement opcional, reconstrução e
  auditoria correlacionada confirmam juntas ou sofrem rollback juntas.
- Reviews e ciclos concluídos permanecem fatos históricos. Somente projeções
  atuais afetadas são canceladas/superseded; void de REVIEW reoferece a etapa
  aplicável e replacement usa `ReviewSchedulePolicy`, sem alterar
  D1/D7/D14/D30, `REV-FIXA-1.0` ou timezone.
- Ciclos manuais S2A independentes são preservados. Classificações históricas
  permanecem ligadas ao fato anulado, sem serem herdadas ou inventadas para a
  substituta.
- Analytics, busca e drill-down continuam contando somente `VALID`: o fato
  anulado não participa da projeção corrente e apenas a ponta válida conta,
  sem duplicar `registered`, `performed`, acertos, erros ou categorias.
- A timeline expõe estado histórico, predecessor/sucessora, supersession e
  correlação de auditoria. `AuditEvent` retém somente IDs, códigos, instante e
  correlação; não retém enunciado, resposta, explicação, estudo ou payload.
- `OperationReceipt` e sua expiração não foram alterados. A correlação de
  auditoria é idempotente somente para uma requisição semanticamente
  equivalente.
- O checker continua read-only e passou de 20 para 22 checks, com `ATT-003` e
  `REV-006`; história VOIDED válida é distinguida de projeção corrente
  inconsistente.

## Integridade, concorrência e recovery

Fault injection após void, criação da substituta, reconstrução, antes da
auditoria e após a auditoria comprovou rollback integral. O teste concorrente
com duas substituições simultâneas produziu exatamente uma sucessora e um
conflito, sem double replacement. Casos cross-Workspace e de contexto
incompatível falharam sem mutação.

O ensaio descartável percorreu migrations reais de uma folha equivalente a
V0.4.4 por S2A até S2B. Antes de fatos S2B, reverse e novo forward preservaram
categorias, eventos de auditoria e reagendamento S2A. Depois de uma correção
real, confirmou original `VOIDED`, substituta `VALID`, classificação histórica,
analytics reconciliado, `PRAGMA integrity_check=ok`, zero violações de foreign
key, backup não vazio, restore isolado e checker com 22 checks e zero findings.
O serviço de reconciliação S6 foi ajustado para reconhecer fatos históricos
VOIDED sem mascarar projeções correntes inválidas.

## Testes e retrabalho observado

- Baseline focado: 118 aprovados em 47,17 s.
- Testes próprios S2B: 18 casos coletados (17 lifecycle/reconstrução e 1
  upgrade/recovery), incluindo cinco pontos de falha transacional.
- Regressão focada multicamada: 206 aprovados em 75,41 s; validações posteriores
  cobriram os ajustes de review profundo.
- `makemigrations --check --dry-run`: nenhuma mudança pendente.
- Manifesto `quality/v05-s2b-migrations.json`: aprovado pelo verificador de
  rastreabilidade, preservando S2A e protegendo as duas migrations S2B.
- Antes do gate, o primeiro ensaio focado de upgrade/recovery detectou que a
  reconciliação S6 tratava classificação e âncora históricas de Attempt VOIDED
  como correntes. A semântica foi corrigida e o ensaio completo passou.
- A8 também detectou e corrigiu resolução iniciada no meio da cadeia,
  preservação de ciclo manual após replacement INITIAL correto, equivalência
  de retry por correlação e autorreferência no modelo.

## A8 deep

Decisão: **APPROVED**.

- Blocker aberto: 0
- Major aberto: 0
- Minor aberto: 0
- Schema/migrations, história, grafo, ponta efetiva, reconstrução, analytics,
  Reviews, classificação, Workspace, atomicidade, concorrência, auditoria,
  upgrade/recovery, regressões S2A e ausência de escopo S2C/S2D foram revistos.

## Gate autoritativo

Comando:

`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1`

Primeira e única execução do gate: **GREEN**, exit code 0.

- runtime: Python 3.13.15, Django 5.2.17 e SQLite 3.53.1;
- banco vazio e migrations: aprovados;
- formatação: 299 arquivos aprovados;
- Ruff: aprovado;
- mypy: 147 arquivos aprovados;
- pytest: 374 aprovados em 156,28 s;
- cobertura global: 87%; mínimos de domínio aprovados;
- detect-secrets: aprovado;
- pip-audit: nenhuma vulnerabilidade conhecida;
- duração total do gate: 208,3 s;
- `gate_first_pass: true`, `attempt_number: 1`;
- incidente de infraestrutura: não.

## Limites e non-actions

Não foram implementados correção prospectiva de gabarito/nova revisão S2C,
delete permanente/retention/purge S2D, UI geral, event sourcing, infraestrutura
distribuída ou mudança de policy. Não houve commit, push, tag ou release.
S2C e S2D permanecem `NOT AUTHORIZED`.
