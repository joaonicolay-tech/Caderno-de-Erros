# Task Contract

Status: AUTHORIZED
Phase: BLOCKED

## Identification

- Task ID: V1.0-S6
- Product version: V1.0
- Stage: S6 — Cadeia de upgrade e recuperação
- Task type: compatibility / upgrade / backup / restore / recovery / CEI evidence
- Size: L
- Risk: high
- Migration expectation: NO
- Potential data impact: HIGH
- A7 planned execution model: GPT-6 Sol High
- Effective authorized execution model: GPT-6.1 Sol High
- Model decision: human-authorized execution-model override for V1.0-S6 (2026-09-30); only this stage, without changing the global plan
- A8 review: deep


## Execution checkpoint — 2026-09-30

- S6 was AUTHORIZED / IN EXECUTION with the human-authorized GPT-6.1 Sol High override before any functional probe.
- Final decision for this execution: BLOCKED. Finding S6-F01 (Major): a valid V1 CEI package imported into a fresh empty V0.4.4-schema target executed eight successful INSERT statements before OperationalError on errors_error_category.category_kind. SQLite total_changes increased by eight; transaction rollback restored the logical and physical fingerprints. This is not REJECTED_BEFORE_WRITE.
- Evidence: quality/v10-s6-cei-result.json and quality/v10-s6-upgrade-recovery-result.md; reproducible opt-in probe tests/probe_v10_s6_cei_prewrite.py.
- Mandatory stop applied under section 13 of the functional authorization. No remaining functional proofs, application fix, gate or A8 were executed after this finding. S6 is not complete; do not archive this contract or return it to NO_TASK_AUTHORIZED.
- Probe targets are preserved as NON-CANDIDATE in the execution workspace; no original/active user database was touched. The first attempt failed during harness preparation before import and is preserved separately; it is not a product finding.
- S1–S5 and S2R1 remain COMPLETED; S7–S10 remain NOT AUTHORIZED. New migrations zero; no git add, commit, push, tag or release.

## Goal

Provar de forma reproduzível a cadeia de uma V0.4.4 representativa para V0.5 e candidato V1, além de instalação limpa, backup, restore, recovery e CEI em provas independentes. Estado final pretendido: upgrade/recuperação V1 comprovados.

## Context

- S1–S5 e S2R1 concluídas. Baseline de autorização: HEAD e origin/main em 5eb6930aba35a0d1083c92816a83c7c4c2451830, árvore inicial limpa.
- Plano oficial: tasks/plans/v10-release-execution-plan.md, seção S6. A4 obrigatório: tasks/plans/v10-s6-upgrade-recovery-plan.md, fechado antes de qualquer operação de risco.
- Contratos: docs/V1.0_S1_Contratos_e_Compatibilidade.md, docs/CEI_EXPORT_1_0.md, docs/V0.4_S6_Backup_e_Recuperacao.md e docs/V0.5_S7_Portabilidade_e_Restore.md.
- Fontes executáveis: MigrationExecutor em tests/test_v05_s2a_upgrade.py e provas relacionadas; services de backup/restore, portability.py, ui_services.py e integrity.py.
- Nenhum PASS S6 pode depender somente de evidência V0.5 antiga.

## Acceptance Criteria

- Cadeia V0.4.4 → V0.5 → V1 exercitada em cópias com migrations reais, backup pré, IDs, contagens, histórico, policies, derivados, fingerprints, SQLite integrity_check, foreign_key_check e checker reconciliados sem diferença inexplicada.
- Instalação limpa V1 comprovada independentemente, com migrations, schema, defaults, checks físicos/funcionais e smoke mínimo.
- Backup válido e corrompido, restore isolado, recovery offline em cópia, retorno e reconciliação comprovados; pré-backup preservado.
- Export CEI V0.5 válido → import V1 válido e round-trip aplicável; CEI-EXPORT-1.0 / format_version 1.0 mantidos, application_version identifica produtor. Só produtores V0.5/V1.0 estritamente compatíveis são aceitos.
- Pacotes/ambientes negativos cobrem produtor, migration, policy, schema, checksum, arquivo ausente/extra, UUID/referência e destino incompatível, com rejeição antes de escrita quando aplicável e fingerprint do destino.
- CT-113–120 e CT-122 mapeados a prova V1 nova; gate integral exit 0 observado; A8 deep aprovado sem Blocker/Major nem P0/P1 aplicável aberto.

## Expected Scope

- Fixtures e testes/harness sintéticos de upgrade, instalação, backup, restore, recovery, CEI e checker estritamente necessários à prova.
- Correção local de defeito concreto de compatibilidade S6 somente após reprodução e dentro dos contratos vigentes, sem migration nova automática.
- Evidências brutas e relatório consolidado S6 em quality/, este contrato e A4; atualização de PROJECT_STATE.md e arquivamento do contrato somente no fechamento futuro.
- Dados de execução exclusivamente fixtures, cópias e targets isolados.

## Protected Scope

- Banco original, banco ativo e dados reais; jamais restore, overwrite, importação ou recovery nesses alvos.
- Fatos históricos e contratos CEI/policies congelados; nenhuma conversão silenciosa, coerção, importação parcial, merge, remapeamento ou adaptação automática de schema.
- S7, S8, S9 e S10: NOT AUTHORIZED. Sem downgrade automático, tag ou release.
- Migration expectation NO. Necessidade real de migration exige parada HUMAN_DECISION_REQUIRED com análise de dados, reversibilidade, compatibilidade, risco e alternativas.

## Constraints

- A4 permanece fechado e aprovado antes de qualquer operação de risco, mesmo em cópia descartável. Execução funcional S6 explicitamente autorizada em 2026-09-30; todos os alvos de dados devem ser comprovadamente sintéticos e isolados.
- Validar integralmente CEI e compatibilidade efetiva do destino antes de escrita. Distinguir rejeição pré-escrita de rollback transacional.
- Parar em diferença inexplicada, perda semântica, ID/contagem divergente, backup/restore inválido, checker/SQLite/FK finding, CEI incompatível sem decisão, escrita prematura, migration inesperada ou risco de tocar original/ativo.
- Verificar modelo/esforço A7 antes da execução funcional. Se não corresponder ao plano autorizado, parar e reportar.
- Git add, commit, push, tag e release não são autorizados nesta execução funcional.

## Verification

- A4 define matriz, fingerprints, recovery e testes focados. Na execução funcional futura: testes de upgrade S6 e regressões relacionadas, backup/restore, CEI e checker.
- Ao final funcional: powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1; observar exit 0, além de git diff --check e A8 deep.
- Nesta execução funcional: registrar provas, testes focados, comandos, contagens e tempos; executar gate integral somente após todas as provas. Finding de rejeição apenas após escrita exige parada e relatório.

## Documentation Impact

Execução funcional: contrato/estado/A4 e evidências necessárias da S6. Na conclusão funcional: quality/v10-s6-upgrade-recovery-result.md e tasks/completed/v10-s6-upgrade-recovery.md, com estado reconciliado.

## Done When

Todas as provas independentes e negativas V1 forem reproduzíveis, sem perda semântica ou mutação prematura; checker, SQLite/FK, fingerprints e recovery forem reconciliados; gate integral for GREEN com exit 0 observado; A8 deep aprovado; contrato arquivado e PROJECT_STATE.md atualizado. S7–S10 permanecem sem autorização até decisão humana própria.
