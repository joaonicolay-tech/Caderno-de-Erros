# V0.3 — Etapa 2 — Resposta Inicial Protegida, Contexto Transitório e Finalização Inicial Atômica

## Situação e autorização

Tarefa formalmente autorizada para execução futura, em novo chat. A E1 está
concluída e GREEN; seus seis modelos, constraints, policies puras e política
SQLite são a base obrigatória. Esta tarefa não autoriza a Etapa 3.

O nome consolida o plano do ADR-011 §9 (“Resposta inicial, contexto e
finalização inicial”) e explicita suas proteções. Não muda o escopo aprovado.

## Objetivo

Permitir responder uma Question ACTIVE do próprio Workspace, sem revelar
gabarito antes da avaliação, e finalizar atomicamente. A avaliação é só do
servidor. A resposta avaliada gera contexto transitório; só a confirmação válida
cria histórico imutável: acerto cria Attempt e recibo; erro cria Attempt,
ErrorClassification, ReviewCycle, Review D1 e OperationReceipt.

## Escopo

- apresentar questão objetiva ACTIVE e QuestionRevision corrente, sem gabarito,
  explicação ou pegadinha;
- submeter e validar a alternativa apresentada;
- calcular resultado exclusivamente no servidor; nunca aceitar resultado alegado;
- criar, consultar e invalidar contexto transitório pós-resposta;
- confirmar acerto/erro inicial, diagnóstico mínimo no erro, recibo,
  idempotência, conflito, rollback e contenção SQLite;
- criar views, forms, URLs, templates, services/helpers e testes estritamente
  necessários para essa jornada, isolados por Workspace.

## Fora de escopo

- conclusão REVIEW ou complete_review(...);
- D7/D14/D30, conclusão de ciclo, reagendamento, fila, timeline/histórico,
  dashboard, métricas e analytics;
- correção histórica de diagnóstico, ErrorClassificationRevision, anulação,
  categorias pessoais, arquivamento/suspensão/reativação;
- snapshots, prioridade, domínio, exportação, jobs, broker, lock distribuído,
  retentativa infinita e V0.4+;
- migration nova, salvo necessidade concreta demonstrada contra o schema E1
  (previsão: nenhuma);
- commit, push, tag ou release.

## Fontes e rastreabilidade

- docs/ADR-011_Saneamento_Fronteira_e_Rastreabilidade_V0.3.md §§2–9:
  precedência para fase, orquestração, contexto, SQLite, recibo e CTs;
- PROJECT_STATE.md, tasks/completed/v03-stage1-learning-foundation.md e
  quality/v03-stage1-learning-foundation-result.md: base E1 GREEN;
- RF: RF-021–RF-024, RF-028, RF-030, RF-034 e D1 de RF-035;
- RN: RN-021–RN-025, RN-028–RN-030, RN-033, RN-035;
- RNF: RNF-010, RNF-016, RNF-020–RNF-022, RNF-025, RNF-026, RNF-031,
  RNF-032, RNF-068;
- fluxo: FL-003, somente tentativa e finalização inicial;
- ADRs de apoio: ADR-003, ADR-006, ADR-008. Em conflito, ADR-011 prevalece.

## Módulos e arquivos relevantes

- reutilizar: src/modules/attempts/models.py,
  src/modules/attempts/persistence.py, src/modules/errors/models.py,
  src/modules/reviews/models.py, src/modules/reviews/policies.py,
  src/modules/questions/{models,views,forms,urls}.py, src/config/urls.py e
  shared/domain/time/*;
- criar/alterar somente se necessário: services de attempts/reviews, helper de
  contexto transitório, forms/views/URLs/templates de resposta e testes E2;
- não alterar migrations E1/V0.1/V0.2, modelos E1 ou policies puras fora de
  necessidade comprovada.

## Serviços e fronteiras

### AttemptService

Único serviço do comando inicial. Valida usuário/sessão/Workspace, questão
ACTIVE, revisão corrente apresentada, alternativa, ausência de tentativa inicial
válida e contexto/versão. Calcula resultado no servidor e cria contexto, sem
Attempt ou recibo.

Na confirmação correta, cria somente Attempt(INITIAL, correta) e
OperationReceipt(INITIAL_CORRECT) em transação curta. No erro, delega ao
orquestrador abaixo e não cria classificação, ciclo ou D1. Resolve replay de
recibo/mesma chave e conflito, sem duplicar regras de ciclo/diagnóstico.

### CompleteReviewService

Na E2, implementar só complete_initial_error(...). É o único orquestrador do
erro inicial e cria, em uma transação curta única: Attempt(INITIAL, incorreta),
ErrorClassification, ReviewCycle(ACTIVE, INITIAL_ERROR, REV-FIXA-1.0),
Review(PENDING, D1) e OperationReceipt(INITIAL_ERROR).

Não implementar/chamar complete_review(...). D7/D14/D30 e transição de
pendências são E3. ReviewSchedulePolicy e ReviewStatusPolicy continuam puras,
sem persistência ou transação.

### Contexto transitório

Criar somente mecanismo efêmero necessário, sem model/migration e distinto de
Attempt. Pode ser armazenamento servidor ou token assinado se cumprir os
vínculos/invalidações. Não persiste fatos nem decide regras de domínio.

## Fluxos

1. Apresentação protegida: resolver questão ACTIVE do Workspace e renderizar
   enunciado/alternativas da revisão corrente; omitir gabarito, explicação e
   pegadinha de HTML, payload e contexto antecipado.
2. Submissão: validar CSRF, autorização, Workspace, revisão, alternativa e
   estado; servidor avalia e cria contexto. Não criar fato histórico.
3. Pós-resposta: mostrar resultado por contexto válido. Em erro, exigir
   categoria e descrição normalizada não vazia para OTHER; acerto não recebe
   classificação.
4. Confirmação correta: contexto válido + chave nova; revalidar e gravar
   Attempt correta + recibo, sem classificação/ciclo/review.
5. Confirmação errada: contexto e diagnóstico válidos + chave nova;
   complete_initial_error(...) grava os cinco fatos ou nenhum.
6. Abandono/cancelamento/expiração: descartar contexto e pedir nova resposta,
   sem Attempt, classificação, ciclo, review ou recibo.

## Contexto e segurança mínima

- TTL fixo de 15 minutos desde a avaliação, sem renovação em reload;
- identificador opaco/imprevisível, vinculado a usuário, sessão, Workspace,
  QuestionRevision, alternativa, resultado calculado, instante/fuso, nonce,
  versão/lock e expiração;
- nunca aceitar token entre usuários, sessões, Workspaces ou versões;
  alternativa, diagnóstico, revisão, Workspace, versão, resultado alegado ou
  facilidade divergentes são rejeitados sem mutação;
- CSRF e autorização em toda mutação; HTML escapado; hidden fields não são
  fonte de resultado/gabarito;
- logs têm correlação, mas não enunciado, alternativas, resposta, explicação,
  pegadinha, token, sessão ou corpo HTTP;
- resultado/correção somente na resposta que validou o contexto.

## Transação, SQLite, idempotência e conflitos

- cada confirmação usa transação curta, explícita e única, com validação final
  de estado, lock_version e constraints;
- acerto persiste Attempt + recibo juntos; erro persiste Attempt, classificação,
  ciclo, D1 e recibo juntos;
- falha antes do commit reverte tudo, inclusive recibo; não há sucesso visual
  nem efeito derivado antes do commit;
- manter busy_timeout de 5 s; uma única repetição após 150 ms, somente para
  SQLITE_BUSY/locked, mantendo a chave. Outro erro não repete; segunda
  contenção retorna PERSISTENCE_FAILURE recuperável sem falso sucesso;
- OperationReceipt: mesma (Workspace, operation_kind, idempotency_key) e mesmo
  hash canônico recupera resultado; mesma chave com hash/payload divergente
  conflita sem mutação;
- antes do commit, só a mesma chave confirma contexto; após consumo, outra
  chave conflita. Chaves distintas disputando o mesmo fato são barradas pela
  validação final/constraints, sem duplicação.

## CTs e provas E2

| CT | Prova exigida |
|---|---|
| CT-013 | resposta/tentativa inicial; uma inicial válida por questão |
| CT-014 | erro cria Attempt, classificação, ciclo ativo e D1 atômicos no Workspace |
| CT-015 | resultado calculado no servidor; resultado do cliente é ignorado/rejeitado |
| CT-016 | acerto cria Attempt + recibo, sem ciclo/review |
| CT-017 | classificação no erro, OTHER com descrição; nenhuma no acerto |
| CT-018 | classificação pertence à tentativa incorreta do mesmo Workspace |
| CT-021 | contexto expira em 15 min, não renova; abandono não cria histórico |
| CT-022 | feedback seguro; CSRF e validação servidor quando aplicáveis |
| CT-093 (E2) | HTML/payload sem gabarito, explicação ou pegadinha antecipados |
| CT-100 | logs sanitizados/correlacionáveis |
| CT-101 (E2) | contexto cruzado, expirado ou adulterado é rejeitado sem tentativa |

Adicionar testes de replay mesma chave/payload, payload divergente, chaves
concorrentes, Workspace cruzado, contexto consumido e falha injetada em cada
fronteira do erro com rollback integral. Eles materializam CT-014 e
RNF-025/RNF-026/RNF-031/RNF-032. Não antecipar CT-023–CT-029, CT-037–CT-042,
CT-019, CT-041, CT-107, CT-111, CT-123 ou CT-125: ADR-011 os mantém em outras
etapas.

## Critérios de aceite

- questão ativa do Workspace recebe alternativa da revisão corrente;
- resultado é exclusivamente servidor e gabarito não aparece antes da avaliação
  ligada ao contexto válido;
- TTL de 15 minutos e abandono não criam histórico;
- Attempt nasce somente na confirmação e é imutável;
- acerto cria somente Attempt inicial correta + recibo;
- erro classificado cria Attempt + classificação + ciclo + D1 + recibo,
  atomicamente e isolado por Workspace;
- falha intermediária faz rollback integral e não cria recibo de sucesso;
- replay idempotente não duplica; payload diferente na mesma chave conflita;
- contenção SQLite segue 5 s/150 ms/uma repetição; sem retry indevido;
- CSRF, escaping e logs sanitizados são provados quando aplicáveis;
- nenhuma migration sem necessidade demonstrada e nenhuma funcionalidade E3+;
- testes específicos e gate autoritativo GREEN, sem P0/P1 aplicável.

## Riscos

- Gabarito exposto: inspeção HTTP/HTML e proibição de confiar no cliente.
- Duplicação/estado parcial: fronteiras exclusivas, transação única, recibo no
  commit, constraints E1 e falhas injetadas.
- Contexto indevido/expirado: vínculos completos, TTL não renovável e
  invalidação após consumo.
- Contenção SQLite: política E1 e falha recuperável sem confirmação falsa.
- Expansão E3+: revisão de escopo/testes bloqueiam REVIEW, D7–D30, fila,
  timeline e métricas.

## Gate e evidência de encerramento

1. Executar suite E2 e CTs acima em banco descartável, sem dados pessoais reais.
2. Executar powershell -NoProfile -ExecutionPolicy Bypass -File
   .\scripts\quality.ps1.
3. Só com tudo GREEN: registrar evidência em quality/, atualizar PROJECT_STATE.md
   e arquivar esta tarefa. Não promover, fazer commit/tag/push/release ou
   iniciar E3 sem autorização expressa.
