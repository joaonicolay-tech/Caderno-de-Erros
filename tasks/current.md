# V0.3 — Etapa 3 — Política e Conclusão de Revisões

## Situação e autorização

**Autorizada para execução em novo chat; não iniciada.** Preparada em 8 de
setembro de 2026 após o encerramento GREEN da E2 (240 testes e gate com exit
code 0). Autoriza exclusivamente a futura conclusão de `Review` pendente pela
política fixa `REV-FIXA-1.0`; não muda o escopo do ADR-011 §9.

## Objetivo

Concluir uma `Review` pendente e disponível do próprio Workspace, calculando a
resposta apenas no servidor. Uma única transação deve criar o fato histórico
imutável `Attempt(REVIEW)`, criar `ErrorClassification` quando incorreta,
finalizar a Review, aplicar D1/D7/D14/D30 e gravar `OperationReceipt`. O efeito é
uma única próxima pendência, ou ciclo concluído somente após acerto D30.

## Fontes e limites obrigatórios

- `docs/ADR-011_Saneamento_Fronteira_e_Rastreabilidade_V0.3.md` §§2–9 é
  autoritativo para fase, orquestração, contexto, recibo, SQLite e CTs.
- A base E2 GREEN é `tasks/completed/v03-stage2-initial-answer.md` e
  `quality/v03-stage2-initial-answer-result.md`. `AttemptService` continua
  exclusivo da tentativa inicial; `complete_review` é do
  `CompleteReviewService`.
- Aplicar: RF-025, RF-034, RF-035, RF-042, RF-043, RF-044; RN-026, RN-033–041,
  RN-044, RN-046 e RN-049; FL-010. Consultar SDD, modelo de dados, plano de
  testes, ADR-003/006/008 nas partes pertinentes.
- Não aplicar antecipadamente fila/selector (`FL-009`/`FL-013`), correção
  histórica, arquivamento, métricas, dashboard, domínio ou prioridade.

## Base técnica e migrations

Reutilizar integralmente schema/constraints E1: `Attempt`,
`ErrorClassification`, `ReviewCycle`, `Review`, `OperationReceipt`,
`ReviewSchedulePolicy`, `ReviewStatusPolicy`, `Clock`, `Calendar` e política
SQLite. **Não há migration prevista**: já existem `AttemptType.REVIEW`, vínculo
único Attempt–Review, facilidade opcional, imutabilidade, estados, datas,
`lock_version`, pendência única por ciclo e recibos. Não alterar models ou
migrations E1/V0.1/V0.2. Se schema novo parecer necessário, não criar: registrar
evidência e bloqueador para revisão humana.

## `CompleteReviewService.complete_review(...)`

Único orquestrador de REVIEW. A assinatura deve aceitar apenas identidade e
Workspace server-side, Review/contexto protegido, `QuestionRevision` apresentada,
alternativa, facilidade opcional, diagnóstico no erro e `idempotency_key`. Nunca
aceitar do cliente resultado, hash, Workspace, data, versão ou transição.

Pré-condições: mesmo usuário/sessão/Workspace; Review/ciclo/questão do Workspace;
ciclo `ACTIVE`; Review `PENDING`; questão `ACTIVE`; revisão corrente apresentada
e `lock_version`/contexto válidos; alternativa da `QuestionRevision`; situação
`DUE`/`OVERDUE` derivada por `ReviewStatusPolicy`; nenhuma Attempt válida da
Review. Contexto expirado/adulterado/cruzado/consumido não grava fatos.

O serviço calcula resultado pelo gabarito, compõe hash canônico, grava
`Attempt(REVIEW)` com Review, alternativa, resultado, instante UTC, timezone,
data civil, chave e facilidade, e devolve o recibo técnico. Não duplicar
responsabilidades iniciais de `AttemptService`.

No erro, categoria deve ser do Workspace e `OTHER` exige descrição normalizada
não vazia; criar `ErrorClassification` da nova Attempt. Não criar
`ErrorClassificationRevision`, corrigir diagnóstico prévio ou modificar fatos:
isso é E4.

## Política, histórico e transações

Chamar `ReviewSchedulePolicy.decide(...)` com `REV-FIXA-1.0`, etapa atual e
resultado server-side; a âncora é a data civil real da Attempt.

| Resultado | Review atual | Ciclo | Próximo fato |
|---|---|---|---|
| Acerto D1 | `COMPLETED` + UTC | `ACTIVE` | D7, sequência seguinte, `local_date + 7` |
| Acerto D7 | `COMPLETED` | `ACTIVE` | D14, sequência seguinte, `+14` dias reais |
| Acerto D14 | `COMPLETED` | `ACTIVE` | D30, sequência seguinte, `+30` dias reais |
| Acerto D30 | `COMPLETED` | `COMPLETED` + UTC | nenhuma Review nova |
| Erro em D1/D7/D14/D30 | `COMPLETED` + UTC | mantém `ACTIVE` | D1, sequência seguinte, `+1` dia real, no mesmo ciclo |

Sempre preservar etapas anteriores; nova Review recebe `scheduled_from_attempt`,
datas iguais `first_due_date/current_due_date`, policy/transition code e contexto
coerente. `Attempt`, diagnóstico eventual, conclusão, próxima Review/ciclo e
recibo devem pertencer à mesma transação curta:

- acerto intermediário: validar/lock → Attempt → concluir Review → D7/D14/D30 →
  recibo → commit;
- acerto D30: validar/lock → Attempt → concluir D30/ciclo → recibo → commit;
- erro: validar/lock → Attempt incorreta → classificação → concluir Review → D1
  → recibo → commit.

Exceção antes do commit reverte todos os fatos/locks/recibo, sem sucesso visual.
Constraints são última barreira, não substituem validação explícita.

## Tempo, futura e facilidade

- Usar somente `Clock.now()` e `Calendar.today(workspace.timezone_name)`
  injetáveis; jamais `datetime.now()` direto. Persistir UTC, timezone e data
  civil; `Calendar.add_days` trata datas civis/DST.
- `ReviewStatusPolicy` bloqueia `FUTURE` com erro de domínio claro, sem contexto,
  Attempt, classificação, recibo ou lock. Cliente não contorna a regra.
- Atraso não avança sozinho; ao concluir, próxima data/reinício é contado da data
  civil real, preservando a prevista antiga.
- Facilidade é opcional, somente `EASY`, `MEDIUM`, `HARD`, em
  `Attempt.perceived_ease`; inválido é rejeitado. Não é dificuldade da questão e
  não altera calendário, transição, data ou política `REV-FIXA-1.0`.

## Idempotência, concorrência e SQLite

`OperationReceipt` usa `(workspace, operation_kind, idempotency_key)` e hash do
payload canônico. Mesma chave+mesmo hash retorna resultado original sem duplicar;
mesma chave+payload divergente conflita sem mutação. Após o contexto ser consumido,
outra chave conflita. Review concluída/Attempt já existente com outra chave retorna
conflito/estado atualizado, sem falso sucesso.

Duas abas usam validação final, `lock_version` e constraints: uma vence; replay
idêntico recupera recibo e a outra chave conflita. Unicidades impedem duas
Attempts válidas por Review e duas pendências no ciclo. Não criar fila/selector.

Preservar SQLite `busy_timeout` de 5 s e uma única repetição após 150 ms apenas
para `SQLITE_BUSY`/`locked`, mantendo chave/hash. Erro diverso não repete; segunda
contenção retorna `PERSISTENCE_FAILURE` recuperável, sem confirmação falsa.

## Interface mínima

Implementar somente acesso direto seguro a Review conhecida/disponível,
apresentação de questão/revisão e alternativas sem gabarito, submissão, avaliação
server-side, confirmação e feedback. Reutilizar contexto transitório, CSRF,
autorização, escaping, cache e sanitização E2. Sem fila de hoje/atrasadas/futuras,
timeline ou histórico visual; futura pode ser consultada, não iniciada/concluída.

## CTs, qualidade e aceite

Testes determinísticos, sem dados pessoais reais, somente banco descartável,
explicitamente carregados no perfil de teste e sem aprendizagem fictícia. Cobrir:

- CT-023–029: D1→D7→D14→D30, D30 concluído, erro em toda etapa, uma pendência;
- CT-037–040: replay, payload divergente, rollback injetado e duas abas;
- CT-042: facilidade ausente/todos os valores sem efeito no calendário;
- CT-076–080: constraints de Attempt REVIEW/ciclo/pendência/etapas/datas;
- CT-093/101 (recorte E3): contexto/apresentação seguros; CT-111 (E3):
  contenção SQLite quando aplicável;
- futura bloqueada, atraso/data real, timezone/data civil/DST, Workspace cruzado,
  Attempt imutável e diagnóstico sem revisão histórica.

Aceite mínimo: Review pendente conclui; resultado é server-side; tabela de
progressão/reinício é cumprida; D30 encerra ciclo; facilidade não muda agenda;
futura não grava; tentativa é imutável; uma válida por Review/uma pendência por
ciclo; replay, conflito, concorrência, rollback e isolamento funcionam; não há
E4+ ou migration; testes E3 e gate `powershell -NoProfile -ExecutionPolicy Bypass
-File .\scripts\quality.ps1` GREEN, sem P0/P1.

## Fora de escopo, riscos e encerramento

Fora: fila/selectors, timeline, dashboard, métricas/analytics, domínio,
prioridade, correção histórica, `ErrorClassificationRevision`,
arquivamento/suspensão/reativação, reagendamento manual/adaptativo,
`ReviewScheduleChange`, snapshots, jobs/broker/lock distribuído e V0.4+.

Riscos: parcial/duplicação (transação, recibo, locks/constraints), calendário
(Clock/Calendar/policies), resultado exposto/adulterado (contexto e servidor) e
contenção SQLite (5 s/150 ms/um retry). Sem bloqueador documental conhecido.

Em novo chat, executar CTs/suite E3 e gate, registrar evidência, atualizar estado
e arquivar esta task. Commit, push, tag, release e E4 exigem autorização expressa.
