# ADR-011 — Saneamento, fronteira e rastreabilidade da V0.3

| Campo | Valor |
|---|---|
| Status | Aprovada — decisão controlada da V0.3 |
| Data | 8 de setembro de 2026 |
| Marco | V0.3 — Etapa 0 — saneamento documental e fronteira |
| Baseline protegida | `v0.2.0` (`a756b6d`) |
| Decisão | A V0.3 fica documentalmente implementável no recorte abaixo; nenhuma implementação é criada por este ADR. |

## 1. Contexto e precedência

`ADR-010` permanece íntegro: ele congelou a V0.2 sem aprendizagem. Este ADR
resolve somente os bloqueadores que ficaram para a V0.3. Quando documentos
anteriores divergirem quanto a fase, orquestração, contexto transitório,
idempotência ou rastreabilidade da V0.3, este ADR e a errata `ERR-V03-001` do
Plano de Testes prevalecem. O texto histórico não é reescrito.

O piloto V0.3 continua limitado a banco local descartável. Não entram dashboard,
domínio, prioridade, snapshots, categorias pessoais, reagendamento,
`ReviewScheduleChange`, correção estrutural de tentativa, exportação ou
reativação de questão.

## 2. Fronteira e entidades aprovadas

| Entidade | Fase | Finalidade e limite |
|---|---|---|
| `Attempt` | Etapa 1 (schema); usada nas Etapas 2–3 | Fato finalizado `INITIAL` ou `REVIEW`; sempre aponta à `QuestionRevision` usada. |
| `ErrorClassification` | Etapa 1; usada nas Etapas 2 e 4 | Diagnóstico atual de uma tentativa incorreta. |
| `ErrorClassificationRevision` | Etapa 1; usada na Etapa 4 | Histórico append-only do diagnóstico; não altera resultado nem ciclo. |
| `ReviewCycle` | Etapa 1; usada nas Etapas 2–4 | Ciclo automático de erro inicial, com no máximo um ativo por questão. |
| `Review` | Etapa 1; usada nas Etapas 2–4 | D1/D7/D14/D30; no máximo uma pendência por ciclo. |
| `OperationReceipt` | Etapa 1; usada nas Etapas 2–3 | Recibo idempotente de operação crítica, sem conteúdo de estudo. |
| `AuditEvent` | Não é model V0.3 | O mínimo já é atendido por fatos imutáveis, revisões de diagnóstico, estados/datas de arquivamento e logs sanitizados. Auditoria genérica permanece posterior. |

`ReviewScheduleChange` é exclusivamente V1. `SavedFilter`, categorias pessoais,
domínio, prioridade, analytics e snapshots permanecem fora da V0.3.

## 3. Fase funcional corrigida

- `RF-021`–`RF-026`, `RF-028`–`RF-032` e `RF-034`–`RF-044` pertencem à V0.3
  nos recortes desta decisão. `RF-027`, `RF-033`, `RF-045` e `RF-046` não
  entram.
- `CT-019` pertence à Etapa 4 da V0.3: aplica `RF-031`, `RN-032` e `FL-008`.
  A correção é auditável por `ErrorClassificationRevision`; não muda resposta,
  resultado, `Attempt` ou calendário.
- `CT-041` pertence à Etapa 4 da V0.3: o recorte de `FL-006` arquiva a questão
  e, na mesma transação, suspende ciclo ativo e `Review` pendente, preservando
  histórico e retirando-a da fila. Reativação continua posterior.
- Revisão espaçada, fila e D1/D7/D14/D30 são V0.3. A proibição herdada da V0.2
  significa apenas não antecipá-las antes das etapas próprias da V0.3.

## 4. Orquestração e transações

`AttemptService` recebe exclusivamente o comando de tentativa inicial. Ele
valida Workspace, questão `ACTIVE`, `QuestionRevision` corrente apresentada,
alternativa, ausência de tentativa inicial válida e o contexto transitório. Ele
calcula o resultado, mas não agenda por conta própria.

Para acerto, `AttemptService` cria somente a `Attempt` e o `OperationReceipt`.
Para erro, ele delega a composição da finalização a
`CompleteReviewService.complete_initial_error(...)`; este é o único orquestrador
que cria, na mesma transação, `Attempt`, `ErrorClassification`, `ReviewCycle`,
`Review` D1 e `OperationReceipt`.

`CompleteReviewService.complete_review(...)` é o único orquestrador da revisão
pendente: valida a revisão e o contexto, cria a `Attempt` de revisão e eventual
diagnóstico, conclui a revisão, aplica `REV-FIXA-1.0`, cria a próxima pendência
ou conclui o ciclo e grava o recibo. `ReviewSchedulePolicy` e
`ReviewStatusPolicy` são puras; elas não persistem nem iniciam transações.

`AttemptService` não cria ciclo/D1, e `CompleteReviewService` não cria tentativa
inicial correta. Views/forms somente adaptam entrada/saída. Cada um dos dois
comandos de finalização tem uma transação curta única: falha antes do commit
reverte todos os fatos e o recibo; efeitos derivados só são solicitados após o
commit. Não há atualização parcial, confirmação antecipada ou regra duplicada.

## 5. Contexto transitório pós-resposta

O contexto é um registro efêmero, distinto de `Attempt`, criado após avaliação e
antes da confirmação. Não é migration, evento histórico, fila nem prova de que o
estudante concluiu a operação.

| Parâmetro | Decisão V0.3 |
|---|---|
| Conteúdo mínimo | Identificador opaco, usuário/sessão e Workspace, `QuestionRevision` e `Review` quando houver, alternativa enviada, resultado calculado, instante/fuso, nonce, versão/lock e expiração. |
| Validade | 15 minutos a partir da avaliação; não é renovada por recarregar a página. |
| Proteção | Identificador imprevisível, armazenado no servidor ou assinado; vinculado a usuário, sessão, Workspace e versão apresentada; CSRF e autorização normais continuam obrigatórios. |
| Expiração/abandono | Expirado, cancelado ou abandonado é descartado sem escrever `Attempt`, diagnóstico, ciclo, revisão ou recibo. A tela pede nova resposta. |
| Replay | Antes do commit, só a confirmação com a mesma chave é aceita. Após sucesso, a mesma chave devolve o `OperationReceipt`; outra chave para o contexto consumido conflita. |
| Payload divergente | Alternativa, diagnóstico, revisão, Workspace, versão, resultado alegado ou facilidade divergente do contexto são rejeitados sem mutação. |

O gabarito, explicação e pegadinha não são enviados na apresentação inicial. A
correção só é mostrada pela resposta que validou o contexto, e o token nunca é
aceito entre usuários, sessões, Workspaces ou versões de questão.

## 6. SQLite, concorrência e idempotência

| Aspecto | Parâmetro mínimo aprovado |
|---|---|
| Transação | Curta, explícita, com validação final de estado e `lock_version`; constraints e índices únicos continuam a última barreira. |
| Timeout | `busy_timeout` de 5 segundos para operações críticas locais. |
| Retry | Somente para `SQLITE_BUSY`/`locked`, uma nova tentativa após 150 ms. Mantém a mesma chave idempotente; nenhum outro erro é repetido automaticamente. |
| Contenção | Se a segunda tentativa não adquirir o lock, responder `PERSISTENCE_FAILURE` recuperável, sem sucesso visual; o usuário pode reenviar com a mesma chave. |
| Dupla submissão | Mesma chave e hash devolve o resultado original; chaves distintas disputando o mesmo fato são bloqueadas por estado/unique constraint e retornam conflito ou estado já atualizado. |
| Falha parcial | Rollback da operação e do recibo. Nenhuma tentativa, conclusão, ciclo ou pendência parcial fica visível. |
| Escopo | Sem fila de jobs, lock distribuído, broker ou retentativa infinita; SQLite/WAL é reavaliado pelo teste de contenção e pelo `BCR-1`. |

## 7. `OperationReceipt`

O recibo é a prova técnica de que uma operação mutável já foi concluída. Sua chave
é única por `(workspace_id, operation_kind, idempotency_key)`; o `request_hash`
é calculado do payload canônico permitido e diferencia o reuso indevido da chave.
Ele referencia somente tipo/ID do resultado e estado lógico necessário para
reproduzir a resposta. Efeito e recibo são persistidos na mesma transação.

Aplica-se a finalização inicial correta, inicial incorreta e conclusão de revisão.
Retenção mínima é 30 dias após `created_at`; depois pode ser descartado somente
se o efeito estiver finalizado, íntegro e já não houver contexto transitório
válido. Não armazena enunciado, alternativas, resposta livre, explicação,
pegadinha, token/sessão, credenciais, corpo HTTP, IP ou dados pessoais
desnecessários.

## 8. Matriz autoritativa V0.3

As referências abaixo substituem as ligações inválidas dos CTs listados. “E1” a
“E5” significam as etapas incrementais da seção 9; a fase indica onde o caso é
implementado, e todos voltam na regressão/promoção aplicável.

| CT | Etapa | RF / RN / RNF | Fluxo | Entidade / serviço | Parcela futura |
|---|---|---|---|---|---|
| `CT-013` | E2 | `RF-021`–`023`; `RN-021`, `RN-023`, `RN-024` | `FL-003` | Attempt / AttemptService | métricas: V0.4 |
| `CT-014` | E2 | `RF-021`, `022`, `024`, `028`, `030`, `034`, `035`; `RN-021`, `023`, `025`, `028`, `030`, `033`, `035`; `RNF-025`, `026` | `FL-003` | Attempt, Classification, Cycle, Review / CompleteReviewService | nenhuma |
| `CT-015` | E2 | `RF-022`; `RN-023`; `RNF-016` | `FL-003` | AttemptService | nenhuma |
| `CT-016` | E2 | `RF-021`; `RN-021`; `RNF-026`, `031` | `FL-003` | Attempt, Receipt / AttemptService | nenhuma |
| `CT-017` | E2 | `RF-024`, `028`, `030`; `RN-025`, `028`, `030` | `FL-003` | ErrorClassification / CompleteReviewService | nenhuma |
| `CT-018` | E2 | `RF-023`, `028`; `RN-028` | `FL-003` | Attempt, Classification / CompleteReviewService | nenhuma |
| `CT-019` | E4 | `RF-031`; `RN-032`; `RNF-028`, `031` | `FL-008` | Classification, ClassificationRevision / diagnostic service | analytics: V0.4 |
| `CT-021` | E2 | `RF-021`, `022`; `RNF-010`, `032` | `FL-003` | transient context / AttemptService | nenhuma |
| `CT-022` | E2 | `RF-021`, `022`; `RNF-016`, `020`–`022` | `FL-003` | transient context / AttemptService | nenhuma |
| `CT-023`–`029` | E3 | `RF-034`, `035`, `043`, `044`; `RN-033`–`039`, `046`, `047` | `FL-010`, `FL-013` | Cycle, Review / CompleteReviewService, schedule policy | nenhuma |
| `CT-030`–`036` | E4 | `RF-036`–`040`; `RN-040`–`044`, `048`, `049` | `FL-009`, `FL-013` | Review / status policy, queue selector | dashboard: V0.4 |
| `CT-037`–`040` | E3 | `RF-025`, `043`, `044`; `RN-026`, `046`; `RNF-025`, `026`, `031`, `032` | `FL-010` | Attempt, Review, Receipt / CompleteReviewService | nenhuma |
| `CT-041` | E4 | `RF-019` (recorte V0.3); `RN-055`, `RN-087`; `RNF-025`, `031`, `032` | `FL-006` | Question, Cycle, Review / archive service | reativação: posterior |
| `CT-042` | E3 | `RF-042`, `044`; `RN-038`; `RNF-025` | `FL-010` | Attempt, Review / schedule policy | uso adaptativo: posterior |
| `CT-073`–`074` | E1 | `RNF-013`, `027` | todos os mutáveis | seis entidades V0.3 / services | repetido por release |
| `CT-076`–`080` | E1/E3 | `RN-021`, `026`, `033`, `039`; `RNF-025`, `026`, `027` | `FL-003`, `FL-010` | Attempt, Cycle, Review, Receipt / services | nenhuma |
| `CT-081`–`082` | E1/E5 | `RNF-033`, `057` | migrações | schema V0.3 | regressão futura |
| `CT-093` | E2/E3 | `RF-021`, `040`, `041`; `RN-043`; `RNF-016` | `FL-003`, `FL-009`, `FL-010` | presentation/context | nenhuma |
| `CT-100` | E2 | `RNF-020`–`022`, `068` | `FL-003`, `FL-010` | logs sanitizados | contínuo |
| `CT-101` | E2/E3 | `RNF-016`, `020`–`022`, `026` | `FL-003`, `FL-009`, `FL-010` | transient context | nenhuma |
| `CT-107` | E5 | `RNF-003`; `BCR-1` | críticos | Attempt/Review writes | repetido V1 |
| `CT-111` | E3/E5 | `RNF-031`, `032` | `FL-003`, `FL-010` | SQLite / services | gatilho PostgreSQL se falhar |
| `CT-123` | E5 | `RNF-080` | smoke V0.3 | matriz de capacidades | repetido por release |
| `CT-125` | E4 | `RNF-009`–`011` | `FL-003`, `FL-010` | interface pós-resposta | reexecução V0.4 |

## 9. Plano incremental congelado

| Etapa | Escopo | Modelo sugerido |
|---|---|---|
| 0 | Este saneamento, ADR, erratas e matriz; sem código | nenhum |
| 1 | Fundação/schema de aprendizagem, constraints, migrations e testes de integridade | `Attempt`, `ErrorClassification`, `ErrorClassificationRevision`, `ReviewCycle`, `Review`, `OperationReceipt` |
| 2 | Resposta inicial, contexto e finalização inicial | os modelos da E1; sem novos models |
| 3 | Política e conclusão D1/D7/D14/D30, atomicidade e idempotência | os modelos da E1; sem novos models |
| 4 | Fila/timeline, diagnóstico e arquivamento com suspensão | os modelos da E1; sem novos models |
| 5 | Integração, migração, regressão, carga/concorrência e promoção | nenhum |

## 10. Critério de saída da Etapa 0

Não há bloqueador documental P0/P1 para planejar a Etapa 1. A Etapa 1 está
**documentalmente liberada**, mas não está autorizada a iniciar até que uma nova
`tasks/current.md` seja formalmente aprovada em novo chat. Este ADR não cria
models, migrations, código de produto, commit, tag, push ou release.
