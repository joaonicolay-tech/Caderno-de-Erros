# V1.0-S8R1 — relatório final de planejamento + A4

Decision: HUMAN_DECISION_REQUIRED
V1.0-S8R1: AUTHORIZED / PLANNING
V1.0-S8: AUTHORIZED / PAUSED / RESUMABLE AFTER S8R1
REAL_DATA: NO
PILOT_EXECUTION: NOT YET AUTHORIZED
S9–S10: NOT AUTHORIZED

## Relatório obrigatório (1–33)

| Item | Resultado |
| --- | --- |
| 1. START_TIME | 2026-10-05T10:13:54.8164281-03:00 — primeiro timestamp observado nesta tarefa, após leitura inicial do pedido; tempo anterior à marca não medido. |
| 2. END_TIME | 2026-10-05T10:34:26.8302299-03:00 |
| 3. Duração | 00:20:32 desde START_TIME observado. |
| 4. Modelo | Autorizado: GPT-6.1 Sol High; identidade/modelo/effort efetivos não verificáveis pelas ferramentas da sessão. Não alegar execução observada nesse modelo. |
| 5. Baseline | HEAD == ref local origin/main == dcccb8950a7752d03461665e0a4952c8a9bc663b; confirmado sem fetch. |
| 6. Paths iniciais | Exatamente oito; tabela completa abaixo e hashes em quality/v10-s8r1-initial-paths.json; todos com decisão explícita e preservação conferida. |
| 7. SOURCE real acessada? | NO. Nenhuma abertura/consulta/cópia da SOURCE/development.sqlite3, checker/backup/PILOT/export/restore/recovery reais ou alteração de timezone real. |
| 8. Causa REV-004 | Complemento inaugural converte started_at usando Workspace.timezone_name atual; SQL ancorado já usa Attempt.local_date própria. Data histórica passa a depender de configuração mutável. |
| 9. Causa Priority | Adapter descarta contexto histórico e reconverte occurred_at no ZoneInfo atual; janelas 0–89,0–29,30–59 podem mudar amostra/score com today igual. Decisão humana anterior aprovou essa base e precisa reconciliação explícita. |
| 10. Outras superfícies | Corrections REVIEW mistura timezone antigo da substituta com schedule atual; CEI pre-DML/restore reutilizam REV-004; Domain aging/status/filtros/dashboard variam prospectivamente por today. Matriz separa 38 superfícies em UNAFFECTED/PROSPECTIVE_ONLY/HISTORICAL_TIMEZONE_SENSITIVE/UNKNOWN. |
| 11. Timezone histórico disponível? | YES para Attempts, ReviewScheduleChange e AuditEvent de reagendamento. NO universalmente para ReviewCycle inaugural QUESTION_ACTIVATION/MANUAL. Âncora antiga e data prevista não são prova independente do fuso de criação. |
| 12. Service de mudança | Owner + IANA + confirmação + CAS; altera somente timezone_name,lock_version,updated_at; cancel/no-op anteriores ao CAS. Eventos são logs estruturados, não AuditEvent durável de troca. Mudança do service não demonstrada necessária para troca prospectiva; contexto futuro depende de H4. |
| 13. Comportamento prospectivo | Today e novos cálculos usam SP após troca; due dates antigas preservadas. Domain confidence/O/completed_today/status podem mudar legitimamente; não exigir score global sempre igual. Replacement precisa H3. |
| 14. Risco histórico | Falso finding/masking inaugural e membership R/D por relocalização, propagação CEI/restore; inexistência de contexto original exato universal. |
| 15. Corrupção real observada? | Nenhuma no relato/preflight anterior; não reconsultado agora. Contrafactuais desta auditoria são estáticos, não observação de user-data corruption. |
| 16. Migration necessária? | NO para A em campos existentes. Não determinada para solução completa; B em novo campo exige YES e decisão humana H4. Nenhuma criada/executada. |
| 17. Schema change? | Nenhuma feita; desnecessária para A. Possível/condicionada para B; não autorizada. |
| 18. CEI change? | Nenhuma feita; preferência NO FORMAT CHANGE. Campo/contexto adicional exige analisar sets fechados e produtores/consumidores antes de decidir. |
| 19. Alternativas A/B/C | A usa contexto próprio; B persiste contexto somente futuro; C usa invariantes realmente independentes de timezone. Comparadas em correctness, compatibilidade, churn, migration, risco, FP/FN, checker e Priority no A4. |
| 20. Recomendação | A para fatos com contexto/Priority; B prospectiva se aprovada para origens inaugurais; C somente estrutural ou limitação legada explicitamente aprovada. Nenhuma fornece exatidão universal legada sem informação independente. |
| 21. T1–T10 | Todos planejados com fixtures/oráculos e testes-alvo; NOT EXECUTED. T11–T14 adicionam correction, compatibilidade, concorrência e bordas. |
| 22. Fronteiras temporais | UTC fixos 02:59:59,03:00,04:00,04:59:59,05:00,12:00 de 05/10/2026; mesmos/diferentes dias, meia-noite SP/Acre; ages29/30,59/60,89/90; Domain60/61,120/121,180/181,365/366. Conferência isolada datetime/ZoneInfo, sem app/banco. |
| 23. Compatibilidade | V0.5/V1, CEI, backup/restore/recovery, checker/upgrade/schema/migrations e contratos congelados avaliados; regra canônica compartilhada, zero-DML nos negativos futuros, contexto faltante não recuperável por upgrade. |
| 24. Severidade | Major / latent semantic risk para REV-004/Priority/correction; corrupção real não observada. Amostra real sem divergência não reduz finding. |
| 25. Critérios de aceite | Troca suportada, histórico preservado, REV-004 correto, 25/0 em válidos conforme H1, Priority estável na base histórica aprovada, SP futuro coerente, sem repair/perda/migration inesperada, T1–T10 PASS, gate integral GREEN e A8 deep APPROVED. Todos são FUTUROS. |
| 26. A8 futura | deep / NOT EXECUTED. Gate funcional também NOT EXECUTED; diff check não é GREEN funcional. |
| 27. S8 state | AUTHORIZED / PAUSED / RESUMABLE AFTER S8R1; finding preservado, sem retomada automática. |
| 28. S8R1 state | AUTHORIZED / PLANNING; planejamento produzido, decisões funcionais pendentes; não S8R1_COMPLETED. |
| 29. PILOT_EXECUTION | NOT YET AUTHORIZED. |
| 30. S9–S10 | NOT AUTHORIZED. |
| 31. git diff --check | Exit 0 observado; verificação de whitespace adicional nos seis arquivos novos. Histórico SHA/sufixos conferidos: PASS documental — seis SHA256 iguais e dois sufixos byte a byte iguais. |
| 32. Git publication | Nenhum git add/commit/push/tag/release. Index inicialmente sem staging e permaneceu sem staging; HEAD/origin/main invariáveis. |
| 33. Decisão | HUMAN_DECISION_REQUIRED. H1 limite do checker legado; H2 base/versionamento Priority; H3 semântica da replacement; H4 contexto futuro/schema/CEI. Depois parar; nenhuma implementação autorizada por este A4. |

## Inventário inicial exato e decisão por path

| Estado inicial | Path | Decisão | Prova final |
| --- | --- | --- | --- |
| M | PROJECT_STATE.md | PRESERVE_AND_PREPEND_ADMINISTRATIVE_STATE | Bytes iniciais preservados como sufixo histórico; novo cabeçalho/decisão somente. |
| M | tasks/current.md | PRESERVE_AND_PREPEND_ADMINISTRATIVE_STATE | Bytes iniciais preservados como sufixo histórico; novo contrato S8R1/decisão somente. |
| ?? | quality/v10-s8-planning-result.md | PRESERVE_BYTE_FOR_BYTE | SHA256 inicial=final. |
| ?? | quality/v10-s8-source-readonly-preflight.json | PRESERVE_BYTE_FOR_BYTE | SHA256 inicial=final. |
| ?? | quality/v10-s8-timezone-impact.json | PRESERVE_BYTE_FOR_BYTE | SHA256 inicial=final. |
| ?? | tasks/plans/v10-s8-controlled-real-pilot-plan.md | PRESERVE_BYTE_FOR_BYTE | SHA256 inicial=final. |
| ?? | tasks/plans/v10-s8-data-protection.md | PRESERVE_BYTE_FOR_BYTE | SHA256 inicial=final. |
| ?? | tasks/plans/v10-s8-pilot-route.md | PRESERVE_BYTE_FOR_BYTE | SHA256 inicial=final. |

Nenhum path ficou sem decisão; nenhum S8 foi restaurado, descartado ou interpretado como novo PASS. O registro do source configuration preflight foi preservado onde já existia, sem reabrir configuração pessoal ou fabricar novo artefato.

## Arquivos produzidos e verificação

- tasks/current.md: contrato S8R1, limites, critérios e histórico S8 integral.
- PROJECT_STATE.md: S8R1 planning, S8 pausa/resumável e histórico integral.
- tasks/plans/v10-s8r1-timezone-semantics-plan.md: A4, A/B/C, H1–H4 e aceite futuro.
- tasks/plans/v10-s8r1-timezone-surfaces.md: superfícies e classificações.
- tasks/plans/v10-s8r1-synthetic-test-matrix.md: T1–T14, contrafactuais e oráculos.
- quality/v10-s8r1-timezone-investigation.md: causas/fontes/risco/compatibilidade.
- quality/v10-s8r1-initial-paths.json: oito paths/decisões/hashes iniciais.
- quality/v10-s8r1-planning-result.md: este relatório final.

Leitura documental, verificação de refs/status/diff, hashes/sufixos e conferência de horários em ZoneInfo concluídas. Nenhum pytest/manage.py/quality.ps1, teste funcional, gate integral ou A8 realizado. Sem produto/schema/testes/configuração/dependências modificados. A exceção safe.directory foi fornecida somente como opção de comando Git; não foi alterada configuração global. Falhas de descoberta por nomes/globs inexistentes foram resolvidas por rg --files; nenhuma evidência funcional foi inferida delas.

Estado final `git status --short --untracked-files=all`:

```text
 M PROJECT_STATE.md
 M tasks/current.md
?? quality/v10-s8-planning-result.md
?? quality/v10-s8-source-readonly-preflight.json
?? quality/v10-s8-timezone-impact.json
?? quality/v10-s8r1-initial-paths.json
?? quality/v10-s8r1-planning-result.md
?? quality/v10-s8r1-timezone-investigation.md
?? tasks/plans/v10-s8-controlled-real-pilot-plan.md
?? tasks/plans/v10-s8-data-protection.md
?? tasks/plans/v10-s8-pilot-route.md
?? tasks/plans/v10-s8r1-synthetic-test-matrix.md
?? tasks/plans/v10-s8r1-timezone-semantics-plan.md
?? tasks/plans/v10-s8r1-timezone-surfaces.md
```

Aguardar escolhas H1–H4 e nova autorização funcional; não continuar S8 nem acessar SOURCE.
