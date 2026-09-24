# V0.5-S5 — aplicação de Domain

## Escopo e decisões

- Contrato: `tasks/current.md`, `V0.5-S5`, `Status: AUTHORIZED` durante a execução. A4 `tasks/plans/v05-s5-domain-application-plan.md` fechado antes da primeira edição funcional.
- V05-OD04 resolvida por decisão humana: Domain corrente recalculado on-demand pela policy vigente; eventos preservam seu `formula_code`; sem snapshot, backfill de mastery, migration de recálculo ou reescrita de fatos históricos.
- Migration **YES** apenas para o ledger `MasteryStateEvent` append-only e o discriminador `ReviewCycle.manual_purpose` (`INCLUSION` versus `MASTERY_REOPEN`). O backfill classifica somente ciclos MANUAL S2A existentes como `INCLUSION`. Reverse é recusado se houver eventos ou ciclos de reabertura; recuperação após fatos S5 exige backup e restore isolado com código compatível.
- S6, Priority, scheduler, UI ampliada, snapshot, commit, push, tag e release não foram iniciados.

## Implementação e evidência funcional

- `src/modules/domain/selectors.py` avalia Questions ativas por Workspace em lote, com fatos VALID efetivos e data local explícita. `services.py` entrega estado corrente read-only, agrega subject/subsubject/discipline com a policy S4, reconcilia transições reais por lock/CAS e executa reabertura manual atômica. `policy.py` expõe os cinco predicados já usados em RN-079 sem alterar fórmula, ordem ou limiares; a consulta acrescenta ACTIVE e, após reabertura manual, o novo D30 do ciclo.
- Primeiro `DOMINATED` legado é reconhecido na primeira reconciliação mutável válida, com instante real; repetição não duplica. Leitura de envelhecimento reflete `evaluation_date` sem escrita; `AUTO_REOPENED` é persistido na primeira reconciliação mutável segura, sem retrodatação.
- Reabertura manual exige Question ativa, DOMINATED corrente, motivo e ausência de ciclo ativo; usa a última Attempt VALID apenas como contexto, com âncora na ação e D1 em hoje+1. Inclusão S2A continua a exigir INITIAL correta. Evento, ciclo e D1 fazem commit ou rollback juntos.
- Integrações S2B, conclusão de Review e archive reconciliam na transação existente. Exclusão S2D inclui eventos no fingerprint, dependências e remoção explícita; backup/restore isolado e checker read-only permanecem coerentes. `MasteryStateEvent` não substitui Attempts/Reviews como evidência.
- Provas focadas/regressões: 115 passed em S5 + S4 + Reviews + S2A/S2B/S2D antes da revisão final; após a revisão, 70 passed em S5, S4, upgrade e manifesto. O gate final executou a suíte inteira, incluindo S2C, S3, analytics, taxonomy, checker e backup/recovery.

## Benchmark on-demand

Fixture S5: 40 Questions ativas, 5 Attempts VALID por Question, 2 disciplines × 2 subjects × 10 Questions; SQLite de teste, `FixedClock`, `CaptureQueriesContext` e `perf_counter`. Uma medição por consulta, sem limiar de latência aprovado:

| Consulta | Questions | Queries | Tempo observado |
| --- | ---: | ---: | ---: |
| Uma Question | 1 | 8 | 21,41 ms |
| Lote | 40 | 8 | 112,06 ms |
| Um subject | 10 | 11 | 71,05 ms |
| Uma discipline | 20 | 11 | 43,63 ms |

O A4 registra o adapter unitário anterior: 7/280/70/140 queries para uma/lote/subject/discipline, em fixture distinta com 3 Attempts por Question. A comparação prova redução do crescimento de queries; tempos entre fixtures não são comparáveis diretamente. As medições não justificam snapshot.

## A8 deep e gate

- A8 deep: **APPROVED**; Blocker 0, Major 0, Minor 0 abertos. Revisados autorização e escopo protegido, policy/limiares, temporalidade, Workspace, locks/CAS, idempotência, concorrência manual/manual e manual/archive, fault injection, S2A–S2D, migrações/reverse/recovery, checker, performance e explicações. Ajustes de revisão foram aplicados antes do gate final: seleção da última Attempt por instante, dependências S2D, probe de schema S2C, critérios explicáveis e proteção de reverse.
- `git diff --check`: exit 0. `makemigrations --check --dry-run`: `No changes detected`. Testes de upgrade provam classificação de MANUAL legado sem backfill de mastery, reverse seguro antes de fatos e recusa após evento; teste S2D executa backup/restore isolado, integridade e exclusão sem resíduo.
- Comando autoritativo: `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1`.
- Tentativa 1: **GREEN**, exit code **0**, 470 passed, 87% de cobertura; duração total 298,1 s. A8 acrescentou introspecção RN-079 e proteção de reverse depois desta execução.
- Tentativa 2, final: **GREEN**, exit code **0**, **473 passed** em 239,30 s, **87%** de cobertura global; duração total 285,9 s. Perfis, banco vazio, migrations, formatação, Ruff, mypy (179 arquivos), cobertura mínima de domínio, detect-secrets e pip-audit aprovados. `pip-audit`: `No known vulnerabilities found`.
- Dois `ResourceWarning` de conexões SQLite em teste de UI S3 apareceram sem falha de gate. `gate_first_pass=true`; duração total da sessão e métricas A7 não observadas: `unknown`.

## Encerramento

S5 concluída com gate final GREEN e A8 deep aprovado. `PROJECT_STATE.md` atualizado, contrato arquivado em `tasks/completed/v05-s5-domain-application.md` e `tasks/current.md` retornado a `NO_TASK_AUTHORIZED`. S6 e etapas posteriores permanecem não autorizadas.
