# Task Contract

Status: COMPLETED

## Identification

- Task ID: `V0.5-S10`
- Product version: `V0.5`
- Stage: `S10`
- Name: `Piloto controlado e decisão documental V0.5`
- Task type: piloto controlado, validação final e decisão documental de promoção
- Size: `L`
- Risk: `high`
- Phase: `COMPLETED` (fase anterior: `PILOT_COMPLETE_PENDING_FINAL_REVIEW`)
- Migration: `NO` (decisão final A4; classificação inicial: `UNLIKELY`)
- A4: plano completo obrigatório antes de qualquer execução do piloto, em `tasks/plans/v05-s10-controlled-pilot-plan.md`
- A7 oficial: `GPT-6 Sol / High`
- A8: `deep`, obrigatório

A4 concluído. A decisão humana D1 de 2026-09-27 aprovou a base sintética integrada para o piloto controlado. P01 original falhou por `S10-F01` no seed; a nova cópia corrigiu a fixture e P01–P11 passaram. P12 original falhou por `S10-F02` no checker; a correção autorizada passou no teste RED/GREEN e reteste P12, seguido de P13/P14 PASS. P15 original falhou por `S10-F03`: o validador de restore aplicava a regra antiga de inclusão manual a `MASTERY_REOPEN`. A correção mínima posterior foi explicitamente autorizada, passou no teste RED/GREEN, e P15 reteste/P16–P18 passaram em cópia protegida, com recuperação e cleanup comprovados. Os FAIL históricos foram preservados em `quality/v05-s10-controlled-pilot-result.md`. S10 permanece aberta e aguarda revisão final; A8 e gate finais, fechamento e promoção continuam fora desta sessão.

## Goal

Executar um piloto controlado da V0.5 em cópia protegida/sanitizada, comprovar backup, recovery e restore aplicáveis, verificar o comportamento integrado, registrar e tratar somente findings autorizados e necessários, executar validação final e A8 deep, e decidir documentalmente se o gate de promoção beta V0.5 foi satisfeito.

Done When resumido: `cópia protegida, backup/restore, findings tratados e promoção decidida`.

Esta tarefa não autoriza promoção antecipada. A decisão documental poderá concluir que o gate foi satisfeito ou não; nenhum item será marcado PASS sem evidência diretamente observada.

## Context and Baseline

- Bootstrap observado em 2026-09-27: branch `main`; `HEAD = origin/main = 5a5b20f80329bda0b8eae21b39a898ca54de9ab8`; working tree inicialmente limpa; `git diff --check` sem apontamentos.
- `tasks/current.md` estava em `NO_TASK_AUTHORIZED`; este bootstrap administrativo persistiu este contrato e não executou A4 ou o piloto.
- Dependência mandatória: `V0.5-S9 COMPLETED`, registrada em `tasks/completed/v05-s9-beta-hardening.md`, `tasks/completed/v05-s9-checkpoint.md` e `quality/v05-s9-beta-hardening-result.md`.
- S9 concluiu com A8 deep `APPROVED`, Blocker 0/Major 0, gate final GREEN e nenhum P0/P1 aplicável aberto. Seu estado histórico, evidências e ressalvas permanecem imutáveis.
- Fontes mandatórias: `tasks/plans/v05-release-execution-plan.md` (incluindo gate de promoção V0.5), artefatos de fechamento/evidence S9 listados acima. A4 deve confirmar o estado atual e consultar evidências S1–S8 estritamente conforme as dependências e critérios do piloto.
- Se baseline, dependência S9, gate de qualidade ou pré-requisito de dados divergir, parar antes de qualquer operação do piloto e registrar a divergência.

## Objective Canonical Scope

Preservar o escopo S10 definido no plano executável V0.5:

- executar piloto controlado em cópia protegida/sanitizada, nunca destrutivamente no banco ativo/original do usuário;
- comprovar backup, recovery e restore aplicáveis, com isolamento e reconciliação;
- verificar comportamento integrado V0.5 segundo plano A4 fechado;
- registrar findings com evidência, tratar somente os autorizados e necessários, e revalidar as correções dentro do escopo;
- realizar validação final e A8 deep;
- auditar cada requisito do gate de promoção e registrar a decisão documental;
- atualizar `PROJECT_STATE.md` somente na fase apropriada e após evidência conclusiva.

## Data Protection and Pilot Safety

É proibido operar destrutivamente sobre o banco ativo/original do usuário. O A4 deve definir, antes de qualquer operação, de modo reproduzível e verificável:

- qual cópia será usada e a origem/autorização de seus dados;
- como a cópia será criada e sanitizada/protegida, incluindo validação de ausência de dados/segredos indevidos;
- backup prévio validado e seu isolamento;
- isolamento operacional que impeça apontamento acidental ao banco ativo;
- fingerprints, contagens, integridade e reconciliação pré/pós necessários;
- recovery e restore aplicáveis, incluindo validação e destino isolado;
- quais operações destrutivas podem ser exercitadas exclusivamente nessa cópia e como comprovar a contenção.

O bootstrap não escolheu origem, método de cópia/sanitização, semântica de recovery, fingerprints ou operações destrutivas. O A4 fechou o procedimento e D1 escolheu a base sintética integrada. Antes de qualquer operação, comprovar os pré-requisitos e o isolamento definidos no plano.

## Promotion Gate to Preserve

A decisão final deve auditar o gate V0.5 definido em `tasks/plans/v05-release-execution-plan.md`, incluindo no mínimo:

- S1–S10 concluídas e arquivadas conforme aplicável;
- quality gate GREEN;
- migrations limpas e upgrade evidenciado;
- S5/read-only saudável;
- backup/restore;
- compatibilidade V0.4.4;
- portabilidade round-trip e rejeições;
- documentação beta;
- BCR aplicável;
- acessibilidade;
- operação Windows;
- segurança de arquivos e logs;
- piloto em cópia protegida;
- A8 deep `APPROVED`;
- Blocker = 0, Major = 0 e nenhum P0/P1 aberto.

Registrar status e evidência por critério, sem converter expectativa, histórico ou ausência de relato em PASS. Falhas de integridade, perda de dados, cross-Workspace, duplicação, export/backup irrecuperável ou migration destrutiva bloqueiam a promoção. A decisão S10 é documental e não cria tag, release ou V1.

## Protected Scope and Exclusions

Esta tarefa não autoriza redesign, feature nova, algoritmo novo, novo DOM-HEUR, novo PRI-HEUR, FTS, mudança de thresholds ou policy, API, deploy público, HA, PostgreSQL de produção, scheduler, autenticação, V1 ou Pós-V1.

A autorização desta sessão cobriu somente a correção mínima de `S10-F03` no validador/reconciliador de restore, testes proporcionais, reteste P15 em cópia protegida e P16–P18 condicionados a PASS. A execução do piloto está completa e aguarda revisão final em sessão própria. Não autoriza terceira correção automática, mudança de S5/checker/CEI/schema, migration, uso de dados reais, restore sobre banco real/ativo, decisão final de promoção, arquivamento S10, A8 final, quality gate final, atualização de `PROJECT_STATE.md` como V0.5 promovida, tag, release, commit ou push.

Findings não autorizam correção automaticamente. Antes de qualquer alteração funcional, seu tratamento deve estar explicitamente coberto pela fase/autorização apropriada e pelo plano A4 fechado. Não ampliar o escopo para resolver findings não necessários ao gate.

## A4 and Phase Boundary

O bootstrap não executou A4. Este A4 foi concluído em `tasks/plans/v05-s10-controlled-pilot-plan.md`, com procedimento reproduzível, critérios observáveis, opções de cópia e proteção de dados, backup/recovery/restore, matriz integrada, tratamento de findings, gate final, A8, rollback e stop conditions. A decisão humana D1 aprovou a fonte sintética integrada para esta execução, sem afirmar representatividade de uso real.

A autorização explícita para avançar da fase de planejamento foi dada em 2026-09-27. Instruções humanas posteriores autorizaram corrigir somente o seed `S10-F01`, depois o checker `S10-F02` e, por fim, o restore/reconciliation `S10-F03`, cada uma com seus retestes condicionais. P15 reteste e P16–P18 passaram; a próxima fase é revisão final própria, não iniciada aqui. A classificação inicial de migration era `UNLIKELY`; o A4 decidiu `NO`, sem criar migration.

## Verification and Done When

- Baseline e S9 mandatória confirmadas para a execução.
- A4 completo, revisado e fechado antes do piloto; proteção/isolation da cópia comprovadas antes de qualquer operação.
- Backup, recovery e restore aplicáveis executados e reconciliados conforme A4, somente em cópia isolada.
- Comportamento integrado validado; findings registrados e apenas os explicitamente autorizados/necessários tratados e revalidados.
- Todos os itens do gate de promoção têm status e evidência; falhas bloqueadoras permanecem explícitas.
- Validação final aplicável e A8 deep concluídos; A8 `APPROVED`, Blocker 0/Major 0 e nenhum P0/P1 aberto para decisão favorável.
- Quality gate autoritativo GREEN com exit code 0; evidências e estado atualizados conforme permitido na fase apropriada.
- Decisão documental V0.5 registrada sem promoção antecipada, tag, release ou início de V1.
- Se qualquer evidência obrigatória falhar ou faltar, não declarar gate satisfeito nem promoção; registrar o bloqueio e parar conforme A4.

## Git and Authorization Boundary

Não executar `git add`, commit, push, tag ou release sob este contrato sem autorização explícita própria. O bootstrap não executou A4; a fase A4 posterior concluiu somente o planejamento. O P12 original falhou e passou no reteste após `S10-F02`; o P15 original falhou e passou no reteste após `S10-F03`. P16–P18 passaram, sem iniciar revisão final, fechamento ou etapa futura.

## Encerramento — 2026-09-27

As restrições acima que dizem "desta sessão" e vedam A8/gate/decisão registram a fronteira da sessão anterior do piloto. A instrução humana posterior autorizou expressamente revisão final, gate e fechamento documental S10, sem Git checkpoint, tag, release, publicação ou V1. O histórico do contrato e dos findings não foi reescrito como se as falhas não tivessem ocorrido.

- D1: `APPROVED_SYNTHETIC_INTEGRATED_PILOT`; fonte sintética suficiente para este piloto técnico, sem alegar representatividade de uso real. O original permaneceu intacto pelo SHA-256 verificado novamente no fechamento.
- Migration: `NO`; `makemigrations --check --dry-run --settings=config.settings.test` exit 0, `No changes detected`.
- P01–P18: PASS final conforme matriz e adendos em `quality/v05-s10-controlled-pilot-result.md`. P01, P12 e P15 originais FAIL, com retestes PASS distintos.
- S10-F01: `RESOLVED_TEST_FIXTURE`, somente no seed temporário; S10-F02: `RESOLVED`, checker REV-001/REV-002; S10-F03: `RESOLVED`, reconciliação de restore. Os dois testes RED/GREEN e as regressões focadas de 49 e 99 testes estão registrados na evidência. Na revisão final, três testes focados adicionais passaram.
- A8 deep final: `APPROVED`; Blocker 0, Major 0, Minor novo 0 e P0/P1 aplicável aberto 0. O Minor histórico S9 de precisão da evidência manual de acessibilidade permanece identificado.
- Quality gate autoritativo: tentativa 1 RED no mypy por tipagem do teste S10; tentativa 2 RED ambiental em `pip-audit` (`WinError 10013`) após 505 testes PASS; tentativa 3 **GREEN, exit 0, 324,4 s**, 505 testes, 86% de cobertura, migrations, formatter, Ruff, mypy, detect-secrets e auditoria de dependências PASS. `gate_first_pass=false`; ambas as RED estão preservadas.
- Checklist beta: todos os critérios obrigatórios PASS. Decisão documental `PROMOTION_APPROVED`: V0.5 beta concluída/aprovada no gate. O resultado completo está em `quality/v05-s10-controlled-pilot-result.md` e o estado operacional em `PROJECT_STATE.md`.
- Nenhum `git add`, commit, push, tag, release ou publicação foi executado. V1 permanece `NOT AUTHORIZED`; `tasks/current.md` retornou a `NO_TASK_AUTHORIZED`.
