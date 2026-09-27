# Task Contract

Status: COMPLETED

## Identification

- Task ID: `V0.5-S9`
- Product version: `V0.5`
- Stage: `S9`
- Name: `Hardening beta, BCR, acessibilidade, segurança/operação local e documentação`
- Task type: hardening beta medido, UX/acessibilidade, operação Windows, segurança local e documentação
- Size: `L`
- Risk: `high`
- Phase: `COMPLETED`
- Migration: `NO` — decisão final do A4; classificação inicial: `UNLIKELY`.
- A4: plano completo obrigatório antes da primeira edição funcional, em `tasks/plans/v05-s9-beta-hardening-plan.md`
- A8: `deep`, obrigatório
- A7 recomendado para futura execução: GPT-6 Sol / Medium; não estimar consumo de cota

## Goal

Concluir hardening beta das capacidades V0.5 com evidência medida de BCR aplicável, UX central coberta, acessibilidade das superfícies novas/modificadas, segurança local, operação Windows comprovada e documentação beta completa. FTS somente pode ser considerada diante de falha medida da busca simples contra critério existente e aplicável. Done When exige A8 deep `APPROVED` e gate final `GREEN`.

Não ampliar esse objetivo.

## Context and Baseline

- Bootstrap baseline observada em 2026-09-26: branch `main`; `HEAD = origin/main = 4a10cdf8fa44bbaf7240fa19532f6ba29354f246`; working tree inicialmente limpa.
- O commit é o checkpoint S8 exigido. Evidências consultadas: `tasks/completed/v05-s8-integrity-compatibility.md`, `tasks/completed/v05-s8-admin-checkpoint.md` e `quality/v05-s8-integrity-compatibility-result.md`; S8 está concluída com A8 deep APPROVED e gate final GREEN (502 testes).
- Dependências obrigatórias confirmadas como concluídas: S3 (`tasks/completed/v05-s3-management-ui.md`, `quality/v05-s3-management-ui-result.md`), S6 (`tasks/completed/v05-s6-priority-heuristic.md`, `quality/v05-s6-priority-heuristic-result.md`), S7 (`tasks/completed/v05-s7-portability.md`, `quality/v05-s7-portability-result.md`) e S8 acima. Não reabrir essas etapas.
- S9 é a única etapa autorizada por este contrato. S10, piloto controlado, promoção V0.5, V1 e etapas seguintes não estão autorizadas.
- Descoberta preliminar para A4, sem auditoria profunda: BCR-1 em `src/shared/application/bcr1.py`, `src/shared/application/bcr1_reads.py`, `scripts/run_bcr1.py`, `tests/test_bcr1.py`, `quality/v04-s8-bcr1-*`; acessibilidade/hardening em `quality/v04-s8-accessibility-result.md` e `tasks/completed/v04-s8-hardening-accessibility-bcr1.md`; operação Windows em `scripts/start-local.ps1`, `scripts/start-local.cmd`, `quality/v04-s7-operation-result.md`; S3/S6/S7 em `src/modules/accounts/{views.py,forms.py}`, `src/modules/priority/`, `src/modules/data_management/` e `src/templates/{accounts,data_management,search,questions}/`; backup/export/restore em `src/modules/data_management/`, `docs/CEI_EXPORT_1_0.md`, `docs/V0.5_S7_Portabilidade_e_Restore.md` e `tests/test_backup_restore.py`, `tests/test_backup_recovery.py`; busca em `src/modules/search/`, `tests/test_question_search.py`; segurança/logging em `src/modules/operations/structured_logging.py`, scripts, staging e docs/ADRs aplicáveis; README em `README.md`. A4 deve confirmar e ampliar esse mapa com evidência atual.

## Dependencies

- S3, S6, S7 e S8 concluídas, verificadas acima; S8 no checkpoint exato `4a10cdf8fa44bbaf7240fa19532f6ba29354f246`.
- Se qualquer dependência ou baseline deixar de corresponder no início da futura execução, parar antes de alterações funcionais.
- Não reabrir S3/S6/S7/S8.

## Acceptance Criteria

### BCR

- Reutilizar BCR-1 existente; identificar operações V0.5 novas/modificadas que precisam de medição.
- Medir antes de decidir ampliar BCR e ampliar somente onde evidência justificar.
- Registrar metodologia e resultados reproduzíveis.
- Não inventar thresholds nem alterar policy porque benchmark “parece lento” sem contrato/fonte aplicável.

### Accessibility

- Auditar superfícies V0.5 novas/modificadas e, quando aplicável, teclado, foco visível, labels, associação de erros/instruções, feedback compreensível, estados empty/error/recovery, zoom 200%, viewport 360px e explicações que não dependam somente de cor.
- Distinguir teste automatizado, inspeção estática e evidência manual/visual realmente observada. Não declarar prova visual não executada.

### Local security and Windows operation

- Auditar o modelo real de operação local, sem inventar threat model de serviço público; cobrir quando aplicável validação de input, uploads/arquivos, paths, staging, versão/formato, logs, secrets, conteúdo sensível, operações destrutivas e loopback.
- Preservar ausência de secrets em logs/evidence.
- Validar somente fluxos suportados: start local, shutdown quando existente, loopback, caminhos Windows, backup/export/restore, erros recuperáveis e instruções de uso. Reutilizar S7; não criar segundo mecanismo de operação.

### Documentation and completion

- Atualizar conforme necessário README, documentação de uso, operação Windows, documentação beta e evidence S9.
- Done When: evidência medida; UX central coberta; operação Windows comprovada; documentação beta completa; A8 deep `APPROVED`; gate final `GREEN`.

## Expected Scope

- Plano A4 em `tasks/plans/v05-s9-beta-hardening-plan.md`, completo e fechado antes de qualquer edição funcional.
- Mudanças mínimas, guiadas pelo A4, em medições BCR, superfícies UX/acessibilidade, segurança/operação local e documentação/evidence beta; testes diretamente relacionados e gate aplicável.
- FTS somente se comprovada falha medida da busca simples contra critério já autorizado/aplicável; sem falha, registrar `FTS = NOT JUSTIFIED` e não implementar FTS.
- A4 deve decidir migration após auditoria de schema. Se correção indispensável aparentar exigir migration, classificar e justificar no A4; não criar migration durante A4. Migration inicial permanece `UNLIKELY` até essa decisão.

## Protected Scope

Não alterar silenciosamente contratos, fatos históricos ou semânticas de S2 lifecycle, S3 gestão, S4/S5 Domain, S6 Priority, S7 CEI/export/backup/restore, S8 checker/compatibilidade, `DOM-HEUR-1.0`, `PRI-HEUR-1.0`, `CEI-EXPORT-1.0`, `OperationReceipt`, Review Queue, analytics V0.4/V0.5, semântica de Workspace ou migrations históricas. Hardening não autoriza redesign.

Proibido neste contrato: S10, piloto controlado, promoção V0.5, tag/release, V1, FTS sem falha medida, redesign geral, refatoração oportunista, PostgreSQL de produção, deploy, HA, tuning geral, nova arquitetura de autenticação, novas features, thresholds não normativos, mudanças nas fórmulas Domain/Priority, novo scheduler e repair mutável do checker.

## Constraints and Decisions

- Registrar o risco `V05-R08 — regressão de performance/acessibilidade`. Mitigação: BCR sem threshold inventado; teclado, foco, zoom 200%, 360px e evidência medida. A4 converterá isso em matriz verificável.
- FTS não está automaticamente autorizado. A4 localizará busca atual, comportamento, dataset/fixture, medições e critério existente aplicável. Sem falha medida, `FTS = NOT JUSTIFIED`; não inventar limite, volume, latência-alvo, ranking ou fuzzy search. Se a fonte não definir limite, registrar como não definido.
- Não decidir `Migration: YES/NO` definitivamente antes de A4; não criar migration no bootstrap.
- A4 mínimo: baseline; dependências; inventário de superfícies V0.5; matriz BCR e metodologia; gate de decisão busca/FTS; matriz de acessibilidade; evidência 200%/360px; teclado/foco/labels; empty/error/recovery; segurança local; logs/secrets; arquivos/paths/staging; operação Windows/local; documentação beta; decisão de migration; testes focados; regressões; A8 deep; quality gate; rollback; stop conditions.

## Verification

- Fase atual: `IMPLEMENTATION_AUTHORIZED` por instrução humana explícita após o A4 completo em `tasks/plans/v05-s9-beta-hardening-plan.md`.
- Permanecem proibidos: migrations; FTS sem decisão humana diante de falha medida; commit, push, tag, release, piloto, promoção, S10 e demais itens do Protected Scope.
- A instrução humana explícita de execução S9 foi recebida após o A4; a implementação deve seguir o plano fechado.
- Execução da S9: seguir matriz e critérios do A4; separar evidência automatizada, estática e manual observada; registrar método/resultados BCR reproduzíveis e resultados de acessibilidade/operação Windows realmente observados.
- Executar verificações focadas, regressões, A8 deep e `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1`; gate final deve ser GREEN. Persistir evidence completa. Se evidência obrigatória, gate ou A8 faltar/falhar, não declarar conclusão nem arquivar.

## Documentation Impact

Durante futura S9, atualizar somente a documentação de uso, operação Windows, README, documentação beta e evidence necessárias segundo os resultados. Não reescrever Roadmap só para marcar avanço. Não alterar fontes normativas ou contratos anteriores silenciosamente.

## Done When

- Dependências e baseline confirmadas; A4 completo e fechado antes da primeira edição funcional.
- BCR aplicável medido sem threshold inventado; decisão de FTS sustentada por falha medida ou registrada como `NOT JUSTIFIED`.
- Superfícies UX/acessibilidade centrais cobertas com evidência corretamente classificada; segurança local e operação Windows suportadas verificadas; documentação beta completa.
- Decisão de migration sustentada por auditoria; focused tests e regressões aplicáveis aprovados.
- A8 deep `APPROVED`, Blocker 0/Major 0; gate final GREEN; evidence persistida; estado do projeto atualizado e tarefa arquivada somente no encerramento comprovado.
- S10 e qualquer etapa posterior continuam não autorizadas.

## Stop Conditions

Parar e registrar blocker/decisão humana, sem improvisar, se: S3/S6/S7/S8 não estiver concluída; baseline Git não estiver limpa; surgir regra normativa inexistente; for necessário inventar threshold BCR; FTS parecer desejável sem falha medida; surgir migration inesperada antes da decisão A4; hardening exigir redesign; for necessário alterar policy Domain/Priority; houver conflito de segurança/privacidade; ou qualquer ação S10 for necessária para concluir S9.

## Git and Authorization Boundary

Este contrato autoriza somente a execução S9 conforme o escopo e as condições acima, após A4. Não autoriza commit, push, tag, release, piloto, promoção, S10 ou V1. Preparar/autorização de etapa futura não inicia essa etapa.

## Closure evidence

- V0.5-S9 concluída em 2026-09-26, sem migration. A4 fechado antes da primeira edição funcional em `tasks/plans/v05-s9-beta-hardening-plan.md`; S9-F01 corrigiu apenas a flexão do estado vazio em `/questions/`, com teste RED→GREEN. README e guia Windows foram atualizados por drift documental.
- BCR oficial `quality/v05-s9-bcr1-human-20260926.json` preservado como FAIL de leitura (`dashboard` e `review_queue` somente no run 3); investigação `BCR_TRANSIENT_SUSPECTED_REPRODUCTION_REQUIRED`. Reprodução oficial controlada `quality/v05-s9-bcr1-reproduction-20260926.json` completa PASS em CT-107 e leitura. Conclusão do episódio `TRANSIENT_NOT_REPRODUCED`, sem causa ambiental afirmada ou regressão de produto confirmada. Busca/filtros PASS, `FTS_NOT_JUSTIFIED`. Medições adicionais V0.5 sem budget novo em `quality/v05-s9-v05-operations-measurement.json`.
- Acessibilidade/UX: evidência automatizada e estática registrada separadamente de `MANUAL_USER_OBSERVED`; usuário informou PASS para 200% nativo, 360 × 800, cinco rotas, teclado/foco, Priority ranqueada/coleta e restore preview/cancel/erro em base sintética. Nenhum restore foi aplicado ao banco ativo. Segurança local, Windows e cleanup constam em `quality/v05-s9-beta-hardening-result.md`.
- A8 deep `APPROVED`, Blocker 0, Major 0, Minor 1 (versão do browser e detalhes individuais não informados). Gate autoritativo final GREEN, exit 0, 502 testes, 86% de cobertura e duração 363,2 s; a tentativa RED ambiental intermediária e o GREEN anterior permanecem registrados. Nenhum P0/P1 aplicável aberto.
- `PROJECT_STATE.md` atualizado e `tasks/current.md` devolvido a `NO_TASK_AUTHORIZED`. Nenhum commit, push, tag, release, piloto ou promoção V0.5; S10 `NOT AUTHORIZED`.
