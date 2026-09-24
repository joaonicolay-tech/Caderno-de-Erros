# Plano A4: V0.5-S5 aplicação de Domain

- Tarefa: `V0.5-S5`, autorizada em `tasks/current.md`.
- Status: `COMPLETED` — auditoria, decisões humanas, arquitetura, migration e sequência de verificação fechadas antes da primeira edição funcional.
- Baseline: `main` e `origin/main` em `1b95d53b028759a3909ed909057c98988bbe4f83`; antes deste plano, somente `tasks/current.md` estava modificado pela autorização. Sem commit, push, tag ou release.
- Escopo protegido: consumir `DOM-HEUR-1.0` de S4 sem mudar fórmulas, thresholds, maturity/sufficiency, seleção de ciclo ou semântica de explicação; não iniciar Priority/S6.

## Fontes e auditoria do estado atual

- `src/modules/domain/policy.py` calcula `Aq`, `Pq`, `Fq`, `Eq`, `M_q`, `C_q`, RN-078, RN-079 e agregação pura por Question distinta. `DomainResult` inclui versão, vetor, incluídos/excluídos e códigos de explicação; `aggregate_hierarchy` calcula `M_h`, `N_h`, `Cob_h` e `C_h` sem omitir silenciosamente confiança ausente. S4 é protegida.
- `src/modules/domain/selectors.py::evaluate_question_domain` já recebe Workspace e Question ativa, usa `valid_attempts`, Reviews elegíveis e data local do Workspace. Seleciona o ciclo efetivo, inclusive `COMPLETED`, exclui `SUPERSEDED`, não escreve e rejeita Question estrangeira, arquivada ou excluída. Ainda é uma consulta unitária de sete queries na fixture medida; chamar em loop cria N+1 operacional.
- `Attempt` é fato histórico ligado à `QuestionRevision` apresentada; `status=VOIDED` e predecessor de replacement não entram em `valid_attempts`. `resolve_attempt_chain` centraliza a ponta válida e detecta ciclo/ramificação/contexto inválido. S2B faz void/replacement, reconstrução e auditoria na mesma transação; S2C cria revisão prospectiva e mantém resultados antigos.
- `ReviewCycle` tem origem, estado, datas e `lock_version`; `Review` tem etapa, data original/atual e constraints de pendência. `ManualReviewInclusionService` S2A cria ciclo `MANUAL` e D1 sob lock/transação, mas exige `INITIAL` correta e usa essa INITIAL como origem e âncora. `FL-019` pede a última Attempt válida como contexto histórico, que numa Question dominada em geral é uma REVIEW D30. A constraint e o guard atuais de `MANUAL` não aceitam essa origem. Inclusão manual S2A e reabertura manual são ações distintas.
- `Question` tem status `ACTIVE/ARCHIVED`, taxonomia `Discipline → Subject → Subsubject` e `lock_version`. `archive_question` suspende ciclo/Review sob lock e CAS; `PermanentQuestionDeletionService` remove explicitamente o agregado com backup e restore isolado quando há histórico. Uma nova entidade de mastery vinculada à Question precisaria integrar o grafo de exclusão, fingerprint, backup/restore e reconciliação S2D; a auditoria final sanitizada não pode virar evidência.
- `AuditEvent` é append-only, fechado por códigos e checks, com metadados técnicos. Não contém `DOMINATED`, `AUTO_REOPENED` ou `MANUAL_REOPENED`; o Modelo de Dados §9.5 especifica `MasteryStateEvent` append-only próprio. `OperationReceipt` é recibo técnico de idempotência e não substitui histórico de mastery. `operations/integrity.py` é checker read-only; não executar repair.
- `RN-068–080`, `RN-097–100`, `FL-018/019`, `CT-044`, S1, planos/resultados S4 e evidências S2A–S2D/S3 foram consultados. `RN-080` lista somente erro válido, anulação de evidência essencial, arquivamento e `C_q < 80`; envelhecimento pode retirar mastery. `ReviewCycle.COMPLETED` não equivale a `DOMINATED`.

## Mapa de dados e fronteiras

`Question` ativa e sua taxonomia corrente → Attempts efetivas `VALID` vinculadas à revisão histórica → Review/ReviewCycle válidos → adapter S4 → `evaluate_domain`/RN-079 → mastery corrente derivada → histórico append-only de transições, se aprovado → `aggregate_hierarchy` por Question distinta → explicações estruturadas consultáveis.

- Fatos históricos: `QuestionRevision`, Attempts, ciclos, Reviews e eventuais `MasteryStateEvent`; não reescrever por recálculo ou correção posterior.
- Projeções correntes: elegibilidade ACTIVE, ponta efetiva, ciclo selecionado e eventual estado corrente reconciliado. A origem de verdade precisa ser única e explícita.
- Valores derivados: `DomainResult`, confidence, sufficiency, agregado e explicações em uma data local explícita. Não precisam de cache por si só.
- Eventos de transição: representam que `DOMINATED`, `AUTO_REOPENED` ou `MANUAL_REOPENED` ocorreu; não devem ser fabricados retroativamente. Reavaliação sem mudança não duplica evento.

## Migration e OD04

**Migration: YES para cumprir o escopo integral.** O schema não contém `MasteryStateEvent`; o histórico de FL-018/019 e a reabertura manual que suprime o mastery corrente apesar dos mesmos Attempts exigem um fato durável. O ciclo `MANUAL` existente não aceita a última REVIEW válida como origem. A migration será aditiva: tabela append-only de transições com Workspace, Question, tipo, `formula_code`, data real, data local de avaliação, scores opcionais, motivo codificado, Attempt gatilho opcional e ciclo manual opcional; índices para último evento por Question e constraints de tipos/referências. `ReviewCycle` ganha discriminador nullable de propósito manual: `INCLUSION` para ciclos MANUAL S2A existentes e `MASTERY_REOPEN` para FL-019; demais origens ficam null. O backfill somente de `MANUAL` legado para `INCLUSION` representa fato conhecido, sem inventar mastery. Constraints e guards preservam INITIAL correta para `INCLUSION` e aceitam última Attempt VALID de qualquer tipo apenas para `MASTERY_REOPEN`. Nenhuma migration de cache de `M_q`, `C_q` ou agregado.

`V05-OD04` / `RN-ABR-004`: **RESOLVED por decisão humana nesta execução**. Quando entrar uma versão nova, Domain corrente será calculado pela policy vigente na próxima avaliação/reconciliação; eventos antigos mantêm `formula_code` e nunca são reescritos. Não há migration apenas para recalcular derivado. `MasterySnapshot` permanece fora da S5; o benchmark não estabeleceu necessidade de materialização nem um novo threshold.

## Benchmark on-demand antes de snapshot

Medição local em 2026-09-24 com perfil Django `config.settings.test`, SQLite temporário e schema migrado do HEAD; geração via serviços/modelos existentes, sem alteração funcional. Fixture: 40 Questions ACTIVE, 2 disciplines × 2 subjects × 10 Questions, 3 Attempts válidas por Question (INITIAL errada e D1/D7 corretas em ciclo COMPLETED), fuso `America/Sao_Paulo`, `FixedClock` em 2026-09-24 15:00 UTC. `CaptureQueriesContext` e `time.perf_counter`; uma execução por cenário, sem aquecimento estatístico. Todas as 40 tiveram `M_q` não nulo.

| Consulta atual | Questions | Queries | Tempo observado |
| --- | ---: | ---: | ---: |
| Uma Question | 1 | 7 | 14,89 ms |
| Lote | 40 | 280 | 671,52 ms |
| Um subject | 10 | 70 | 121,03 ms |
| Uma discipline | 20 | 140 | 276,84 ms |

O lote usou o adapter S4 unitário em loop; o crescimento de 7 queries por Question prova necessidade de seleção em lote em S5, sem alterar a policy S4. As medidas não são evidência suficiente para snapshot: não existe threshold aprovado e não houve medição do adapter em lote proposto. O processo retornou exit 0 e imprimiu os números; na saída, a limpeza automática do SQLite temporário encontrou `WinError 32` por conexão ainda aberta. Isso não altera as medições, mas deve ser corrigido em benchmark posterior para reprodutibilidade limpa.

## Decisões humanas aprovadas para S5

1. **OD04:** on-demand com policy vigente na próxima avaliação/reconciliação. Eventos antigos preservam `formula_code`; sem snapshot, migration de recálculo ou reescrita de histórico.
2. **Mastery legado:** a primeira reconciliação mutável válida após S5 cria `DOMINATED` se RN-079 já for verdadeiro, com `occurred_at` real da reconciliação. Não há backfill ou data retroativa; idempotência impede duplicata.
3. **Manual:** ciclo `origin_kind=MANUAL` e discriminador `MASTERY_REOPEN`; a última Attempt VALID, inclusive REVIEW, é contexto, nunca âncora temporal. Inclusão S2A continua `INCLUSION` e exige INITIAL correta. Motivo obrigatório, Question ACTIVE, domínio corrente e ausência de ciclo ACTIVE são revalidados sob lock; evento, ciclo e D1 hoje+1 confirmam juntos.
4. **Envelhecimento:** estado corrente read-only respeita a `evaluation_date` sem escrita em GET; `AUTO_REOPENED` surge na primeira reconciliação mutável segura após `C_q < 80`, com instante real, sem scheduler nem data retroativa.

O estado corrente usa resultado RN-079 da policy vigente e fatos válidos. Após `MANUAL_REOPENED`, um D30 correto VALID do novo ciclo é condição adicional para restaurar `DOMINATED`; o `M_q` anterior permanece consultável no evento e no histórico, sem alterar a fórmula. O último evento é histórico da última transição reconhecida, não fonte concorrente de pontuação. Leitura read-only nunca escreve; reconciliação mutável bloqueia a Question, compara o último evento e grava só transições reais. Se a avaliação corrente for não dominada por archive, registrar `AUTO_REOPENED` no mesmo commit de archive; permanent delete remove os eventos vinculados antes de remover Question e deixa somente auditoria S2D sanitizada.

Para explicabilidade S5, a mesma avaliação pura de RN-079 expõe os cinco predicados matemáticos/temporais que já compõem a decisão, seus resultados e IDs de evidência permitidos; a consulta S5 acrescenta a condição estrutural `Question ACTIVE` e, quando aplicável, o novo D30 do ciclo manual. Isto não altera ordem, fórmula ou limiares S4. O reverse da nova tabela é recusado se houver eventos; o reverse do discriminador é recusado se houver ciclo de reabertura. Recuperação após fatos S5 é restore isolado sob código compatível.

Migrations: aditivas para tabela de eventos e discriminador; indexes/constraints para Workspace/Question, tipos e última transição; backfill do discriminador de ciclos MANUAL legados apenas; sem backfill de eventos, score ou snapshot. Antes de fatos S5, reverse pode ser avaliado; depois de eventos/ciclos de reopening, rollback por reverse não é seguro e recovery usa backup com código compatível restaurado isoladamente. Atualizar provas de upgrade/restore e grafo explícito S2D; não reescrever migrations históricas.

## Sequência após decisão

1. Fechar o A4 `COMPLETED` com decisão normativa e schema exato; registrar migration/rollback/recovery e plano de benchmark em lote.
2. Implementar consultas Workspace-scoped em lote consumindo policy S4; hierarquia por IDs distintos e explicação consultável sem N+1.
3. Implementar ledger e reconciliação atômica/idempotente, depois manual reopen com CAS/lock e D1 hoje+1; integrar S2B, archive e S2D na mesma fronteira transacional apropriada.
4. Cobrir testes focados de Domain, transições, gatilhos, double submit, concorrência, fault injection, Workspace, upgrade/recovery e regressões S2A–S2D/S4.
5. Medir consultas de uma Question, lote, subject e discipline após batching; fazer A8 deep e gate autoritativo; somente após GREEN e evidências encerrar S5 e retornar `tasks/current.md` a `NO_TASK_AUTHORIZED`.
