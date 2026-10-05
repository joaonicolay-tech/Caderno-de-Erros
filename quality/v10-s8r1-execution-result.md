# V1.0-S8R1 — resultado da execução funcional sintética

S8R1_COMPLETED. H1–H4 verificadas; gate próprio GREEN; A8 deep APPROVED. SOURCE real não acessada; publicação Git e PILOT não executados.

| # | Campo exigido | Resultado observado |
| --- | --- | --- |
| 1 | START_TIME | 2026-10-05T11:01:44.850829-03:00 (primeiro marco medido; não retroestimado) |
| 2 | END_TIME | 2026-10-05T13:10:05.041702-03:00 (preparação do fechamento; confirmação Git posterior registrada no manifesto final) |
| 3 | duração | 7700.19 segundos / 128.34 minutos entre os marcos medidos |
| 4 | modelo | Autorizado GPT-6.1 Sol High; identidade/effort efetivos não verificáveis de forma independente nesta interface |
| 5 | baseline | HEAD == local origin/main == dcccb8950a7752d03461665e0a4952c8a9bc663b; sem fetch/publicação |
| 6 | H1 | Implementada: limitações tipadas, sem usar Workspace atual como prova retroativa; checks verificáveis mantidos |
| 7 | H2 | Implementada: membership R/D por Attempt.local_date histórica; fórmula/40-30-20-10/suficiência/ties inalterados |
| 8 | policy Priority final | PRI-HEUR-1.1 prospectiva em 2026-10-05; PRI-HEUR-1.0 e registros anteriores preservados |
| 9 | H3 | Implementada: nova replacement usa contexto corrente capturado; lifecycle VALID→VOIDED/AuditEvents conforme esclarecimento humano |
| 10 | H4 | Sem campo inaugural/contexto durável, model, schema, migration, CEI field/set, backfill ou repair |
| 11 | SOURCE acessada? | NO durante S8R1; nenhum fingerprint da SOURCE real foi lido para fabricar prova de preservação |
| 12 | RED R1 | Preservado antes do fix: checker acrescenta 1 finding REV-004 após Acre→SP |
| 13 | RED R2 | Preservados três limites: comparáveis 3→0 em 29/30, 0→3 em 59/60; recorrência elegível 0→3 em 89/90, today igual |
| 14 | RED R3 | Preservado antes do fix: replacement herdava Brazil/Acre com Workspace America/Sao_Paulo |
| 15 | implementação REV-004 | SQL canônico byte-igual ao baseline; catálogo 25; offsets confiáveis +1/+7/+14/+30, sequência/etapa/transição/escopo preservados |
| 16 | limited verification | LIMITED_VERIFICATION / TIMEZONE_CONTEXT_UNAVAILABLE separado de finding/ERROR; 0 no vazio, 1 ativação, 2 ativação+manual/reopen; sem PASS exato fictício |
| 17 | Priority local_date | PASS nas fronteiras 0/-1,29/30,59/60,89/90; same today preserva R/D/result; referência corrente distinta pode mudar O/Domain legitimamente |
| 18 | replacement | INITIAL/REVIEW PASS; Attempt nova e agenda usam contexto capturado; predecessor preserva datas/fuso/resultado/revisão/vínculos, além do lifecycle normal autorizado |
| 19 | T1 | PASS — Workspace vazio, troca e cancel/noop/owner/stale/IANA inválido; sem novos fatos |
| 20 | T2 | PASS — Seis UTCs: 02:59:59Z,03:00Z,04:00Z,04:59:59Z,05:00Z,12:00Z; histórico INITIAL/REVIEW preservado; ATT-002 negativo mantido |
| 21 | T3 | PASS — QUESTION_ACTIVATION/MANUAL INCLUSION/MASTERY_REOPEN e regressões INITIAL_ERROR; âncora exata versus limitação explícita |
| 22 | T4 | PASS — ScheduleChange/Audit antigos preservados, novo reagendamento usa fuso capturado; divergências/audit fault regressões PASS |
| 23 | T5 | PASS — D1→D7→D14→D30 via serviços, sucesso terminal, erro em cada etapa; política civil e offsets negativos PASS |
| 24 | T6 | PASS — R/D históricos nas fronteiras com >=3 Questions; fórmula, fractions, thresholds, unavailable/ties; data futura rejeitada explicitamente |
| 25 | T7 | PASS — Domain read-only, mesma avaliação preserva resultado; 60/61,120/121,180/181,365/366 e suficiência; futuro sem clamp |
| 26 | T8 | PASS — 25 checks; CLI healthy/findings/operational exits; positivos/negativos Python/SQL; zero attempted/completed DML/native changes, fingerprint igual |
| 27 | T9 | PASS — Snapshot de TODAS as tabelas físicas exceto Workspace byte/semanticamente equivalente; Workspace muda exatamente timezone_name/lock_version/updated_at |
| 28 | T10 | PASS — Novos fatos SP/local_date05-10 e D1 seguinte; inclusão/reopen/reagendamento e leituras analíticas/fila/dashboard em suíte integral |
| 29 | T11 | PASS — INITIAL/REVIEW replacement, void sem substituta, preservação manual, tip/idempotência/fault rollback; campos antigos intactos |
| 30 | T12 | PASS — CEI V0.5/1.0, V1/1.0 e V1/1.1; genuíno runtime V0.5→V1, 21 sets iguais; backup/restore/upgrade; negativos antes DML |
| 31 | T13 | PASS — CAS simultâneo um vencedor/um stale; races reais criação/replacement/reagendamento com troca; interleaving reverso rejeita futuro e rollback íntegro |
| 32 | T14 | PASS — Virada anual, fevereiro bissexto, IANA 2010 Acre/SP, DST NY e alias Rio_Branco; soma civil e não duração fixa |
| 33 | CEI format | CEI-EXPORT-1.0 preservado; 21 sets/campos AST iguais; sem bump |
| 34 | CEI policies | V0.5 aceita 1.0; V1 aceita históricas 1.0 e vigente 1.1; produtor novo emite 1.1; desconhecida/V0.5+1.1 rejeitados antes DML |
| 35 | V0.5→V1 | PASS com código histórico inalterado da tag v0.5.0 (commit d24cde1d3c25f7ff0e23306ce7e15e7ea85fd228) sob interpreter/dependências atuais disponíveis, sem alegar recriação integral do ambiente original; dados sintéticos, upgrade com plano vazio/tabelas iguais e round-trip 21 sets iguais |
| 36 | migrations | No changes detected; 0 novas; schema/migrations package compatíveis; migrations históricas intactas |
| 37 | focused tests | 325 PASS / 0 fail / 0 error / 0 skip + 5 CEI/REV-004 PASS; matriz final 61 PASS após fixture T13 determinístico; 325 focados precedem esse refinamento somente de teste, código funcional idêntico; gate final cobre todos os testes correntes |
| 38 | gate | GREEN / exit 0; powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1; script intacto; perfis dev/prod apontados para alvos sintéticos |
| 39 | total tests | 741 PASS / 0 fail / 0 error / 0 skip no gate próprio |
| 40 | coverage | 87.157780979827% global; gate de cobertura de domínio PASS; métricas completas no JSON |
| 41 | pip-audit | PASS / 0 vulnerabilidades conhecidas; auditoria efetivamente concluída |
| 42 | A8 deep | APPROVED após gate GREEN; revisão pelo agente raiz, sem alegação de reviewer humano/externo independente |
| 43 | Blocker/Major/Minor | 0 / 0 / 0 abertos; achados UI e visibilidade pós-import corrigidos e revalidados; limitações H1/H4 são decisões aprovadas |
| 44 | historical preservation | 9 artefatos iniciais byte-iguais nos paths; 3 JSONs iniciais em cópias qualificadas por exceção humana, originais completos byte-iguais fora Git; 5 JSONs/36 strings qualificados reversivelmente; current/state históricos e REDs preservados; sem alteração factual |
| 45 | SOURCE untouched | YES por ações executadas exclusivamente em DBs sintéticos; sem abrir/copiar/hash/ORM/checker/backup/restore na SOURCE |
| 46 | S8R1 state | S8R1_COMPLETED; contrato arquivado em tasks/completed/v10-s8r1-timezone-semantics-remediation.md |
| 47 | S8 state | AUTHORIZED / PLANNING / RESUMABLE AFTER S8R1; contrato anterior restaurado com bloco de retomada |
| 48 | PILOT_EXECUTION | NOT YET AUTHORIZED; correção real na futura cópia PILOT exige autorização humana específica |
| 49 | S9–S10 | NOT AUTHORIZED; não executadas |
| 50 | git diff --check | PASS, exit 0; confirmação pós-fechamento no manifesto final |
| 51 | git status | Árvore suja esperada, alterações e untracked classificados por caminho; nada staged; manifesto final anexo registra lista exata |
| 52 | nenhum commit/push/tag/release | YES; nenhum git add, commit, push, tag ou release; HEAD/origin local permanecem baseline |
| 53 | decisão | S8R1_COMPLETED; PARAR após fechamento autorizado; nenhum piloto/etapa seguinte/publicação |

## Evidências e limites

quality/v10-s8r1-verification.json contém T1–T14 com nomes reais do JUnit, métricas, hashes qualificados, as 11 provas nativas de destino incompatível e a prova genuína V0.5→V1. quality/v10-s8r1-red-evidence.json preserva a reprodução anterior à implementação. quality/v10-s8r1-a8-deep.json registra a revisão posterior ao gate. quality/v10-s8r1-final-paths.json registra a inspeção Git final e decisões por caminho.

Raw sintético em work permanece fora do repositório: REDs, todos os runs intermediários, JUnit, gate, runtime histórico arquivado e bancos/pacote da prova de upgrade. Não afirmar retenção dos DBs efêmeros de fixtures que pytest/Django encerraram normalmente. START_TIME é o primeiro marco medido; END_TIME aqui é a preparação do fechamento e o manifesto final registra a confirmação posterior.

A proveniência V0.5 é do código inalterado extraído da tag verificada. Ele foi executado sob o interpreter/dependências atuais disponíveis; não foi recriado byte a byte todo o ambiente de instalação histórico. O manifesto CEI não possui metadata de versões de runtime. A prova final observou Python 3.13.15/Django 5.2.17/SQLite 3.53.1 no processo produtor e no consumidor e usa config.settings.test nas duas fases, alvos sintéticos novos explicitamente guardados. A primeira prova usava perfil development com binding sintético guardado, sem SOURCE; foi preservada e repetida no perfil test para cumprir também a exigência literal do contrato atual. A prova não confunde ambiente do observador com identidade do produtor, nem substitui V0.5 apenas alterando o rótulo do manifesto.

As duas expectativas inaugurais CEI antigas foram preservadas com suas falhas observadas e atualizadas para outcomes limitados explícitos sob H1; negativos ancorados continuam ativos, sem skip/xfail e com os mesmos 63 casos na matriz CEI. O primeiro gate foi interrompido de forma intencional, exit 1/não elegível; somente a execução integral posterior GREEN é usada para fechamento.

O segundo gate terminou com 740 PASS/1 FAIL: fixture T13 atribuía o mesmo instante à INITIAL e à replacement, deixando o desempate técnico por UUID aleatório escolher a última evidência. Log, JUnit, coverage e fonte desse FAIL permanecem preservados. Apenas o fixture foi refinado com instantes UTC fixos distintos, mantendo rejeição por futuro e rollback obrigatórios; a política Domain não foi alterada. A matriz de 61 casos foi reexecutada integralmente. A terceira tentativa de captura parou antes de pytest por NativeCommandError em stderr normal do uv; captura ajustada sem mudar quality.ps1 ou omitir logs. A quarta tentativa integral é a evidência elegível do fechamento. Nenhum gate anterior foi convertido em PASS.

Zero-DML refere-se à leitura do checker/projeção e à rejeição no destino. A materialização CEI privada em RAM possui CREATE/INSERT próprios antes de validar; não é mutation no destino nem escrita do checker. Não confundir isso com uma alegação impossível de materialização sem escrita. Negative desconhecida é reject-before-write; rejeição Domain por futuro na injeção reversa é rollback de uma operação já iniciada, explicitamente diferenciada.

Nenhum documento congelado é reescrito retroativamente. O adendo novo define PRI-HEUR-1.1 e compatibilidade atual. Due date inaugural sem contexto independente não recebe prova exata: 0 findings com N limitações continua uma validação de alcance limitado.

O hook oficial sinalizou hashes literais históricos. Após rejeição automática da alteração do inventário por preservação literal, o humano aprovou especificamente a qualificação SHA256:/COMMIT: em cinco JSONs versionáveis (36 strings). Originais completos permanecem em work/s8r1-execution/metadata-proposal/*.original; transformação reversível exatamente verificada, sem mudança de fatos ou digests substantivos. Nove paths iniciais continuam byte-iguais; três JSONs iniciais têm cópias qualificadas e originais byte-iguais. quality/v10-s8r1-metadata-approval.json contém a autorização e hashes antes/depois. Uma tentativa opcional de prefixar contrato/state com essa exceção foi rejeitada e não aplicada; a alternativa segura limitou a aplicação aos cinco JSONs e evidência separada. Baseline de segredos e gate permaneceram intactos.
