# ADR-013 — Ciclo de revisão na ativação da questão V0.3

| Campo | Valor |
|---|---|
| Status | Aprovada — decisão corretiva controlada da V0.3 |
| Data | 10 de setembro de 2026 |
| Marco | V0.3 — correção arquitetural anterior à nova implementação/regressão |
| Decisão | A transição efetiva de uma questão para `ACTIVE` cria o seu ciclo de revisão e a primeira D1; nenhum `Attempt` é fabricado. |

## 1. Propósito, contexto e precedência

O produto é um Caderno de Erros: em regra, a questão é cadastrada porque já
foi errada fora do sistema. Portanto, usar o acerto ou o erro da primeira
resposta dentro do sistema como gatilho de existência do ciclo não representa o
fato de aprendizagem que motivou o cadastro.

Este ADR substitui **somente no recorte V0.3 abaixo** as decisões conflitantes
de ADR-011 e das especificações congeladas. Os documentos históricos não são
reescritos. Onde houver conflito sobre nascimento do ciclo, D1 inaugural,
origem, tentativa inicial, fila, timeline, constraints ou CTs afetados,
**ADR-013 prevalece sobre ADR-011 §§2 e 4, RF-023, RF-024, RF-034, RN-024,
RN-025, RN-033, RN-035, FL-003, FL-010, CT-013, CT-014, CT-023 e a matriz E5**.
As demais decisões de ADR-011, inclusive contexto transitório, Workspace,
Clock/Calendar, transações curtas, política SQLite, idempotência e
`REV-FIXA-1.0`, permanecem vigentes.

## 2. Regra de ativação

Toda questão que efetivamente se torna `ACTIVE` cria, na mesma transação:

1. um `ReviewCycle` no estado `ACTIVE`, com origem `QUESTION_ACTIVATION`; e
2. uma única `Review` pendente, sequência 1, estágio `D1`, para o próximo dia
   civil do Workspace.

Esta regra cobre `create_active`, `complete_draft` e
`save_revision(..., activate=True)`. Em criação direta, a decisão que persiste
a questão já ativa é tratada como a transição efetiva para `ACTIVE`. Em
rascunho, aplica-se somente à transição `DRAFT → ACTIVE`; salvar um rascunho
sem ativá-lo não cria fatos de aprendizagem.

Editar questão já `ACTIVE`, inclusive salvar uma revisão de conteúdo sem nova
transição, não cria nem reinicia ciclo ou D1. A reativação de questão arquivada
continua fora de escopo e não é inferida por esta decisão.

`D1` é calculada por `Calendar` a partir da data civil obtida de `Clock` no
timezone do Workspace: `workspace_local_date + 1 dia civil`. Não é intervalo
de 24 horas, nem usa timezone do servidor ou do navegador.

## 3. Sem tentativa artificial; respostas posteriores

O nascimento do ciclo não cria `Attempt`, `ErrorClassification` ou recibo de
tentativa. A timeline deve identificar a origem como ativação, sem apresentar
uma tentativa inexistente.

| Situação | Regra final |
|---|---|
| Inicial correta antes da D1 | Persiste a `Attempt` e o recibo idempotente aplicável; mantém exatamente a D1 inaugural já existente, sem concluí-la, removê-la ou reagendá-la. |
| Inicial incorreta antes da D1 | Persiste `Attempt` e classificação válida na transação da confirmação; não cria segundo ciclo e não cria, remove ou reinicia a D1 inaugural. |
| Erro ao concluir `Review` | Continua concluindo a Review corrente e, por `REV-FIXA-1.0`, cria uma nova D1 para o próximo dia civil a partir da data real da conclusão. |

Assim, `CompleteReviewService.complete_initial_error(...)` deixa de ser o
orquestrador que cria `ReviewCycle`/D1: ele preserva sua responsabilidade de
finalizar atomicamente tentativa inicial incorreta, classificação e recibo. A
orquestração de ativação pertence ao serviço de escrita de questões. A
conclusão de Review continua exclusiva de
`CompleteReviewService.complete_review(...)`.

## 4. Modelagem autorizada para a próxima etapa

Esta seção autoriza schema e migration **somente na próxima tarefa**; este ADR
não os cria.

- `ReviewCycleOriginKind` ganha `QUESTION_ACTIVATION`.
- `ReviewCycle.origin_attempt` passa a aceitar `NULL` somente para
  `QUESTION_ACTIVATION`; `INITIAL_ERROR` continua exigindo uma `Attempt INITIAL`
  válida, incorreta, do mesmo Workspace e questão.
- `ReviewCycle.origin_question_revision` será uma FK protegida para a revisão
  que tornou a questão ativa. Ela será obrigatória no estado final do schema;
  a migration deverá preencher ciclos existentes pela revisão da
  `origin_attempt` antes de apertar a obrigatoriedade. Para origem de ativação,
  ela identifica a revisão publicada pela transição.
- `Review.scheduled_from_attempt` passa a aceitar `NULL` somente para a Review
  inaugural de ativação: origem `QUESTION_ACTIVATION`, sequência 1, estágio
  `D1` e código de transição explícito, por exemplo
  `QUESTION_ACTIVATION_D1`. As demais Reviews mantêm âncora em `Attempt`
  válida do mesmo Workspace e questão.
- Uma constraint de combinação de origem deve impedir
  `INITIAL_ERROR` sem tentativa e `QUESTION_ACTIVATION` com tentativa. As
  regras que dependem de relações (revisão de origem, mesma questão/Workspace,
  e a exceção estrita da D1) serão validadas no serviço/modelo além das
  constraints locais do banco.
- Permanecem a unicidade de no máximo um ciclo `ACTIVE` por questão, a
  unicidade de `(review_cycle, sequence_number)` e a unicidade da pendência
  compatível com o modelo vigente (no máximo uma `Review` `PENDING` por ciclo).

O migration será evolutivo e preservará os fatos existentes: não cria ciclo
retroativo para questões `ACTIVE` históricas. Ele somente torna o schema capaz
de registrar as próximas ativações e de rastrear ciclos já existentes.

## 5. Atomicidade, concorrência, idempotência e rollback

A operação que efetiva a ativação deve validar novamente estado, revisão,
Workspace e `lock_version`, criar questão/ciclo/D1 quando aplicável e confirmar
tudo em uma transação curta. Em falha, rollback integral: uma questão em
rascunho não fica ativa sem ciclo/D1 e uma criação direta não deixa agregado
parcial persistido.

Reenvio, atualização concorrente ou duas abas não podem produzir dois ciclos
ou duas D1. A transição já efetivada retorna o estado persistido ou conflito
conforme o contrato de escrita; a constraint de ciclo ativo é a barreira final.
Aplicam-se `busy_timeout`, retry único para `SQLITE_BUSY`/`locked`, chave e
recibo idempotentes das confirmações de tentativa/revisão, sem falso sucesso.
Não se cria um `OperationReceipt` de tentativa para mascarar a ativação, nem
se reutiliza uma tentativa como âncora fictícia.

## 6. Arquivamento, fila e timeline

Arquivamento continua suspendendo o ciclo ativo e sua Review pendente na mesma
operação, retirando-a da fila e preservando todos os fatos. Nenhuma regra de
reativação é autorizada.

A D1 de ativação participa da fila pelas mesmas regras de data civil: antes da
data é futura; na data é devida; depois, atrasada. A timeline e os selectors
devem suportar origem de ativação e âncora nula sem expor uma relação ou UUID
técnico inexistente. A criação da D1 não altera métricas de tentativas.

## 7. Impacto de rastreabilidade e testes

Os documentos congelados listados na seção 1 permanecem como evidência
histórica, mas seus trechos conflitantes são substituídos pelo presente ADR:

| Referência histórica | Leitura substituída neste recorte |
|---|---|
| ADR-011 §§2 e 4 | `ReviewCycle` não é exclusivamente de erro inicial e a ativação, não `CompleteReviewService`, cria ciclo/D1. |
| RF-023 / RN-024 / FL-003 / CT-013 | Acerto inicial registra tentativa real, mas não significa ausência de ciclo/D1. |
| RF-024 / RN-025 / FL-003 / CT-014 | Erro inicial registra tentativa e classificação; não é gatilho de criação/reset da D1. |
| RF-034 / RN-033 / RN-035 / CT-023 | A primeira D1 nasce na ativação efetiva, com origem própria e no próximo dia civil do Workspace. |
| FL-010 | Erro em Review continua sendo o único destes fluxos que reinicia D1. |
| Matriz E5 | Os PASSs que dependem da regra anterior não promovem V0.3 após esta mudança; devem ser reexecutados contra o candidato final. |

A próxima etapa deverá ajustar apenas os testes e CTs necessários à nova regra,
incluindo ativação pelos três caminhos, data civil, idempotência/concorrência,
rollback, `Attempt INITIAL` correta/incorreta, erro de Review, fila/timeline,
arquivamento, constraints e migration sem backfill de ciclos históricos.

O resultado humano real de `CT-125` é preservado como evidência histórica:
P01–P09 PASS, com compreensão parcial dos termos em P07–P09; P10 FAIL; total
9/10 (90%). Não se inventam observações adicionais. Ele não é suficiente para
promover a V0.3 depois da alteração estrutural: o candidato final exigirá
reteste humano conforme o protocolo aplicável.

## 8. Mojibake e fronteira desta autorização

A próxima etapa está autorizada a substituir exclusivamente literais
comprovadamente duplamente codificados por UTF-8 real em código, templates e
testes afetados, preservando os arquivos em UTF-8. Não autoriza saneamento
amplo da documentação, nem substituição global cega.

Esta execução é documental. Não cria migration, model, serviço, template,
teste funcional, commit, push, tag, release ou promoção. V0.3 permanece **NÃO
PROMOVIDA**.
