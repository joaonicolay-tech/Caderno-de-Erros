# S8 restoration after verified S8R1 closure

Status: AUTHORIZED
Phase: PLANNING
Task ID: V1.0-S8
Resumption: RESUMABLE AFTER S8R1
S8R1: S8R1_COMPLETED at 2026-10-05T13:10:05.041702-03:00
REAL_DATA_ACCESS: NO FURTHER ACCESS AUTHORIZED
SOURCE_ACCESS: PROHIBITED IN THIS SESSION
PILOT_EXECUTION: NOT YET AUTHORIZED
S9–S10: NOT AUTHORIZED
Git publication: NOT AUTHORIZED

User-authorized restoration preserves the original S8 contract below. Historical
preflight in that contract remains historical evidence; it grants no fresh SOURCE
access. Planning resumes as an available state only: no S8 work is performed by
S8R1 closure. Any future real timezone correction on the isolated PILOT copy
requires a separate explicit human authorization. S8R1's full execution contract,
planning history and H3 clarification are archived in
tasks/completed/v10-s8r1-timezone-semantics-remediation.md.

Verified semantics: PRI-HEUR-1.1, canonical H1 limited verification, current
replacement context, no migrations/schema/CEI shape change. Gate GREEN/exit 0
and A8 deep APPROVED with 0/0/0. See quality/v10-s8r1-execution-result.md.

---

# Task Contract — V1.0-S8

Status: AUTHORIZED
Phase: PLANNING
REAL_DATA_ACCESS: EXACT SOURCE READ-ONLY PREFLIGHT AND TIMEZONE IMPACT ASSESSMENT EXECUTED; FURTHER ACCESS NOT AUTHORIZED
PILOT_EXECUTION: NOT YET AUTHORIZED
S9–S10: NOT AUTHORIZED

## Identification

- Task ID: V1.0-S8
- Product version: V1.0 (candidate; no promotion)
- Stage: Piloto final local real controlado — planejamento, contrato e A4
- Task type: documentary planning and read-only source audit
- Size: L
- Risk: critical
- Migration expectation: NO
- Real/personal data: YES in the future pilot; access prohibited in planning
- Authorized model/effort: GPT-6.1 Sol High; explicit human override of GPT-6 Sol High recommended by the V1 plan. Runtime identity not independently observable.
- Future execution A8: deep; not performed by this planning task.

## Goal

Produzir um A4 revisável e um contrato durável que permitam ao responsável decidir a origem, consentimento e proteção do futuro piloto privado, sem acessar dados pessoais nem executar o piloto.

## Context

Autorização humana de 2026-10-03 inclui baseline, auditoria read-only de código/documentação, contrato, A4, roteiro, proteção, checkpoints, critérios e sincronização administrativa nesta execução. Essa autorização prevalece sobre a convenção de bootstrap em sessão separada de A2, somente para esse escopo documental. Não autoriza operações de dados.

Baseline observada: HEAD == origin/main == dcccb8950a7752d03461665e0a4952c8a9bc663b; árvore inicial limpa. S1–S7 e S2R1–S2R5 COMPLETED; S6R1 COMPLETED / S6_REVALIDATED; S7R1/S7R2 COMPLETED; S7-F01/F02 RESOLVED. S7 checkpoint COMPLETED; A8 S7 APPROVED WITH NOTES, 0 Blocker / 0 Major / 2 Minor. O commit dcccb895 é reconciliação administrativa posterior ao checkpoint 6879e6ad; ambos permanecem históricos.

Fontes indispensáveis: AGENTS.md, docs/A2_Contrato_de_Tarefa_Atual.md, docs/A3_Progressive_Disclosure.md, tasks/plans/v10-release-execution-plan.md (§S8), docs/V1.0_S1_Contratos_e_Compatibilidade.md, docs/V1.0_Operacao_Local.md, docs/CEI_EXPORT_1_0.md, docs/V1.0_Adendo_V10-D2_Matriz_de_Browsers_S4.md, docs/operations/temporary-test-evidence.md, RNF-035/038 na Etapa 4, evidências S3–S7/S6R1/S7R1/S7R2 e fontes operacionais referidas no A4.

## Acceptance Criteria

- Baseline exata e estado anterior confirmados, sem tocar banco ou conteúdo pessoal.
- A4 contém origem/consentimento pendentes, isolamento, pré-backup/restore pré-uso, retorno/recovery, fingerprints, representatividade qualitativa, roteiro e stop conditions.
- RPO/RTO definidos com eventos/relógios e metas existentes RNF-035, sem resultados inventados.
- Privacidade, retenção de cada classe temporária e allowlist de evidência versionável definidos antes do acesso.
- Contrato e PROJECT_STATE sincronizados em AUTHORIZED / PLANNING, REAL_DATA_ACCESS e PILOT_EXECUTION NOT YET AUTHORIZED, S9–S10 NOT AUTHORIZED.
- A4 termina em S8_REAL_DATA_AUTHORIZATION_REQUIRED, listando as dez decisões humanas necessárias.
- Relatório de planejamento e git diff --check/status finais observados; nenhum PASS de piloto, A8 deep ou gate funcional inferido.

## Expected Scope

Somente tasks/current.md, cabeçalho atual de PROJECT_STATE.md, tasks/plans/v10-s8-controlled-real-pilot-plan.md, tasks/plans/v10-s8-pilot-route.md, tasks/plans/v10-s8-data-protection.md e quality/v10-s8-planning-result.md. Checklist, riscos e temporários integrados nesses artefatos, sem cópias redundantes.

## Protected Scope

Bancos/fontes reais, registros, exports CEI reais, backups reais, código, configuração executável, testes, migrations, dependências/lock, contratos congelados, evidência histórica e Git index/publicação. Proibido descobrir bancos pessoais por busca na máquina. Nenhuma S9/S10, promoção, deploy, hosting, multiusuário, feature ou redesign.

## Constraints

- Não abrir/consultar/copiar/exportar dados pessoais, criar CEI/backup real, iniciar app, migrar banco real, executar restore/recovery ou mutar dados.
- PILOT_SOURCE: HUMAN_DECISION_REQUIRED; nenhuma classe/origem selecionada automaticamente.
- Original futuro: READ-ONLY SOURCE / DO NOT MUTATE. Piloto futuro: ISOLATED PILOT COPY. Todos os passos do A4 são procedimentos futuros, não autorização atual.
- Migration nova necessária, fonte/alvo incerto, consentimento insuficiente ou qualquer passo que exija acesso real: STOP / HUMAN_DECISION_REQUIRED.
- Nenhum git add, commit, push, tag ou release. Nenhuma remediação funcional silenciosa.

## Verification

Read-only source audit; coerência entre contrato/A4/estado, referências e argumentos comparados com fontes; revisão de privacidade dos textos; git diff --check; git status --short --untracked-files=all. Sem testes funcionais, manage.py, quality.ps1, aplicativo ou operações SQLite nesta execução.

## Documentation Impact

Artefatos do Expected Scope. Evidências e contratos históricos ficam preservados. O A4 define paths futuros para resultado, checkpoints, findings, RPO/RTO, retention manifest e A8 deep; eles não devem conter resultados fictícios nesta fase.

## Done When

Planejamento documentado e verificações documentais satisfeitas; decisão S8_A4_READY_FOR_HUMAN_DATA_AUTHORIZATION registrada. Parar aguardando nova autorização humana conforme bloco final do A4. S8 continua AUTHORIZED / PLANNING, sem execução e sem declaração S8_COMPLETED; este contrato não se arquiva como piloto concluído.

## SOURCE_READONLY_PREFLIGHT_EXECUTED — 2026-10-03

A later explicit human authorization selected exact SOURCE privately and permitted only its technical read-only preflight in development, with ownership/control confirmed. This completed microstep superseded earlier planning-only access prohibitions only for that observed read-only session; it grants no future access or data operation. Result: quality/v10-s8-source-readonly-preflight.json.

Decision: HUMAN_DECISION_REQUIRED / TIMEZONE_MISMATCH. SOURCE_PHYSICALLY_UNCHANGED; SQLite ok; FK 0; migrations 34/34 compatible; normative schema comparison compatible; checker 25/0. WORKSPACE_COUNT=1; WORKSPACE_SCOPE_CANDIDATE=W01; candidate timezone differs from the human confirmation (actual value kept private). Immediate stop: no functional aggregate counts, D1/D7/D14/D30 availability or representativity assessment after mismatch. No Workspace selected for mutations.

PILOT_EXECUTION remains NOT YET AUTHORIZED. No copy, backup, snapshot, PILOT, migration, bootstrap, repair, export CEI, restore, recovery or root creation. ROOTS_APPROVED_BUT_NOT_CREATED. RETENTION_POLICY=UNTIL_S8_A8_AND_HUMAN_DISPOSAL_APPROVAL. Recovery remains future isolated RECOVERY_TARGET only; ORIGINAL recovery need is a material incident/STOP. S9–S10 and add/commit/push/tag/release remain NOT AUTHORIZED. Await explicit human timezone decision; do not resume source access automatically.
Human decision after the stop: keep the originally confirmed expected timezone and leave the mismatch pending for a separate decision. No timezone correction, source-access resumption or pilot authorized.

## TIMEZONE_IMPACT_ASSESSMENT_EXECUTED — 2026-10-03

Explicit human authorization permitted only the W01 read-only timezone impact assessment, with GPT-6 Luna High authorized for this microstep; runtime identity is not independently observable. Result: quality/v10-s8-timezone-impact.json. This completed session grants no future source access or mutation. Historical A4 and prior preflight remain unchanged.

Decision: TIMEZONE_CORRECTION_REQUIRES_SEPARATE_REMEDIATION. SOURCE_PHYSICALLY_UNCHANGED; mode=ro with mutation guards; native total_changes=0; SQLite ok/FK 0; canonical current-source checker 25/0. At one observed NOW_UTC, civil dates coincide; eligible pending Reviews=9, overdue=9/due=0/future=0 in both zones; temporal classification delta=0. Existing phases: D1 in 9 cycles; D7 in 2; D14/D30 absent. REPRESENTATIVITY_PRECHECK=LIMITED: core facts exist, but later phases, SavedFilters and relevant correction/reschedule/audit histories are absent.

The official confirmed compare-and-swap configuration service updates only Workspace fields and emits structured operational events; it does not rewrite agenda/history, recompute historical facts or require a migration. Historical timezone fact rewrite required=NO. Nevertheless REV-004 validates historical inaugural dates against the current Workspace zone, and Priority derives civil windows by relocalizing historical Review instants. The five observed inaugural Reviews have zero counterfactual mismatches; current Priority memberships also have zero delta. These observations do not eliminate the static civil-boundary invariant risk. No correction or historical repair was executed or designed. Separate remediation decision required before any future correction; migration need for an eventual remediation remains undecided.

WORKSPACE_SCOPE=W01 for the completed READ-ONLY assessment only. No ORIGINAL mutation, copy, backup, PILOT, timezone update, migration, functional operation, CEI export, restore or recovery. PILOT_EXECUTION=NOT YET AUTHORIZED; S9–S10=NOT AUTHORIZED. No Git add/commit/push/tag/release. Stop; no automatic continuation.
