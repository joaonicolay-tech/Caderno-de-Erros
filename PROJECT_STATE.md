# Project State

## Estado atual

- Produto: V0.3 **PROMOVIDA**; tag protegida `v0.3.0`.
- Arquitetura operacional: Project Development Architecture v1.0
  **APPROVED/FROZEN** em 12 de setembro de 2026.
- Etapas operacionais A1–A10: concluídas.
- Planejamento V0.4-P0: concluído; plano executável em
  `tasks/plans/v04-release-execution-plan.md`.
- V0.4-S1: concluída — contratos semânticos de métricas e exemplos de
  reconciliação aprovados.
- V0.4-S2: concluída — serviços analíticos, DTOs, agregações e drill-downs
  read-only reconciliáveis implementados, sem migration ou UI.
- V0.4-S3: concluída — dashboard explicável integrado exclusivamente à camada
  analítica S2, sem migration ou schema.
- V0.4-S4: concluída — consulta consolidada com filtros de revisão, resultado
  inicial, categoria/resíduo, navegação de detalhe e destinos de revisão S2.
- V0.4-S5: concluída — invariant checker operacional read-only com catálogo de
  17 invariantes, saída/logs sanitizados e exit codes distintos.
- V0.4-S6: concluída — snapshot SQLite consistente, restore isolado, checks
  físicos, reconciliação por SHA-256/fatos e invariant checker S5 integrados,
  com ensaio sintético reproduzível e documentação operacional.
- V0.4-S7: concluída — entry point PowerShell portátil, wrapper Explorer,
  operação loopback, guia de atualização segura e integração documental com S5/S6.
- Etapa de implementação atual: nenhuma; S8 permanece não autorizada.
- P0/P1 aplicável aberto: nenhum.
- V0.4 funcional: S1-S7 concluídas; nenhuma etapa autorizada.

## Última validação

Gate de V0.4-S7 GREEN no encerramento, exit code 0: 325 testes aprovados em
70,31 s, 88% de cobertura global, migrations, formatação, Ruff, mypy,
detect-secrets e pip-audit aprovados. O ensaio descartável iniciou por entry
point de diretório externo, respondeu em loopback, encerrou liberando a porta e
executou S5/backup/validação S6; a revisão A8 padrão foi **APPROVED**, sem
Blocker/Major. Não houve migration, schema, instalador, restore destrutivo ou
implementação de S8/S9.

Gate de V0.4-S6 GREEN no encerramento, exit code 0: 322 testes aprovados em
74,56 s, 88% de cobertura global, migrations, formatação, Ruff, mypy,
detect-secrets, cobertura de domínio e pip-audit aprovados. O ensaio sintético
descartável comprovou backup/restore de 655.360 bytes, abertura da aplicação,
checks SQLite, S5 exit 0, reconciliação e preservação por hash; recuperação
observada em 2,691580 s, sem constituir SLA. A revisão A8 profunda foi
**APPROVED**, sem Blocker/Major. Não houve migration, schema, restore sobre o
banco ativo ou implementação de S7-S9.

Gate de V0.4-S5 GREEN no encerramento, exit code 0: 302 testes aprovados em
62,55 s, 87% de cobertura global, checker 88% e comando 95%; migrations,
formatação, Ruff, mypy, detect-secrets, cobertura de domínio e pip-audit
aprovados. Dez testes específicos e 153 regressões relacionadas passaram; o
teste manual em SQLite descartável confirmou exit 0 e hash do banco inalterado.
A revisão A8 profunda foi **APPROVED**, sem Blocker ou Major. A primeira
execução do gate ficou inconclusiva somente no pip-audit por `WinError 10013`;
a repetição autorizada fora do sandbox terminou GREEN. Não houve migration,
schema, repair ou implementação de S6.

Gate de V0.4-S4 GREEN no encerramento, exit code 0: 292 testes aprovados em
63,04 s, 87% de cobertura global; migrations, formatação, Ruff, mypy,
detect-secrets, cobertura de domínio e pip-audit aprovados. A revisão A8
padrão foi **APPROVED**, sem finding Blocker ou Major. A etapa reutilizou a
listagem, busca, paginação e timeline existentes e acrescentou apenas filtros
GET Workspace-scoped, retorno à consulta e drill-down dos estados temporais de
revisão; não houve migration, alteração de schema ou implementação S5.

Gate de V0.4-S3 GREEN no encerramento, exit code 0: 288 testes aprovados em
67,59 s, 87% de cobertura global; migrations, formatação, Ruff, mypy,
detect-secrets, cobertura de domínio e pip-audit aprovados. A revisão A8
padrão foi **APPROVED**, sem finding Blocker ou Major. Três testes S3 novos
cobrem a integração da home com S2, taxa sem denominador, valores renderizados
e resíduo; não houve migration ou alteração de schema.

Gate de V0.4-S2 GREEN no encerramento, exit code 0: 285 testes aprovados em
62,62 s, 87% de cobertura global, selectors analíticos 90% e services 95%;
migrations, formatação, Ruff, mypy, detect-secrets, cobertura de domínio e
pip-audit aprovados. A revisão A8 profunda foi **APPROVED**, sem finding
Blocker ou Major. Cinco testes S2 novos cobrem reconciliação, isolamento,
timezone, ordering, resíduos e query counts; nenhuma migration foi criada.

Gate de V0.4-S1 GREEN no encerramento, exit code 0: 280 testes aprovados em
57,68 s, 87% de cobertura global, migrations, formatação, Ruff, mypy,
detect-secrets, cobertura de domínio e pip-audit aprovados. A revisão A8
profunda de S1 foi **APPROVED**, sem finding Blocker ou Major. S1 criou somente
o contrato em `docs/V0.4_S1_Contratos_de_Metricas_e_Reconciliacao.md`; RN-057
foi classificada como esclarecimento comprovado, sem mudança normativa.

Gate documental V0.4-P0 GREEN na primeira execução (99 s), exit code 0: 280
testes aprovados em 55,56 s, 87% de cobertura global, migrations, formatação,
Ruff, mypy, detect-secrets, cobertura de domínio e `pip-audit` aprovados.

A revisão A8 profunda da P0 foi **APPROVED**, sem findings Blocker, Major ou
Minor. Não houve mudança funcional, de schema, migration, regra de negócio,
baseline V0.3, Architecture v1.0 ou gate.

## Fontes correntes

- `docs/PROJECT_DEVELOPMENT_ARCHITECTURE_V1.md`: baseline operacional v1.0;
- `quality/v03-stage5-validation-result.md` e ADR-014: promoção V0.3;
- `tasks/plans/v04-release-execution-plan.md`: decomposição e rastreabilidade
  durável da V0.4;
- `tasks/completed/v04-p0-release-planning.md`: contrato e encerramento P0;
- `docs/V0.4_S1_Contratos_de_Metricas_e_Reconciliacao.md`: contratos e cenários
  determinísticos que S2/S3 devem consumir sem redefinir semântica;
- `tasks/completed/v04-s1-metric-contracts-and-reconciliation.md`: contrato e
  evidência de encerramento de S1;
- `docs/V0.4_S2_Interface_Analitica_Interna.md`: fronteira interna read-only
  pronta para consumo futuro por S3;
- `tasks/completed/v04-s2-analytics-services-and-drilldowns.md`: contrato e
  evidência de encerramento de S2;
- `tasks/completed/v04-s3-explainable-dashboard.md`: contrato e evidência de
  encerramento do dashboard explicável S3;
- `tasks/completed/v04-s4-consultation-detail-history.md`: contrato e evidência
  de encerramento da consulta, detalhe e histórico S4;
- `docs/V0.4_S5_Invariant_Checker.md`: catálogo e contrato operacional do
  checker read-only;
- `tasks/completed/v04-s5-integrity-checker.md`: contrato e evidência de
  encerramento de S5;
- `docs/V0.4_S6_Backup_e_Recuperacao.md`: procedimento operacional de backup,
  restore isolado, S5, reconciliação, falhas, RPO/RTO e retenção;
- `quality/v04-s6-recovery-result.md` e `quality/v04-s6-recovery-drill.json`:
  review, gate e ensaio sintético observados de S6;
- `tasks/completed/v04-s6-backup-recovery.md`: contrato e encerramento de S6;
- `quality/operational-execution-metrics.jsonl`: métricas A1–A10, V0.4-P0 e
  V0.4-S1-S7;
- `quality/v04-s7-operation-result.md`: ensaio, review A8 e gate S7;
- `tasks/current.md`: autoridade corrente; `NO_TASK_AUTHORIZED`.

Os detalhes cronológicos anteriores permanecem nos ADRs, artefatos de
`quality/` e contratos em `tasks/completed/`; este arquivo registra somente o
estado operacional corrente.

## Próximo passo possível

Recomendação: avaliar e, em nova sessão, autorizar somente `V0.4-S8`, consumindo
os comandos e a operação Windows comprovados em S5-S7 sem antecipar piloto. A recomendação não cria
autoridade. Qualquer etapa V0.4,
checkpoint Git, tag ou release exige autorização expressa própria; nenhuma
etapa funcional está autorizada.
