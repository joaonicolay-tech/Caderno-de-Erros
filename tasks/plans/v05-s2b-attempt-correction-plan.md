# Plano A4: V0.5-S2B — Correção estrutural de Attempt

- ID da tarefa relacionada: `V0.5-S2B`
- Status: `COMPLETED`
- Objetivo: fixar a menor decomposição executável para void, replacement e
  reconstrução antes da primeira edição funcional, sem ampliar
  `tasks/current.md`.
- Baseline observado: `main` em
  `8206a355d1ca602b6d953676997a88da1e6d032c`; tag `v0.4.4` no commit
  `46e887e0c4fa4dd6f7e128ab63802223d99c9e29`; somente a autorização em
  `tasks/current.md` estava modificada ao iniciar.
- Premissas: preservar fatos V0.4.4/S2A, `Workspace`, `registered`,
  `performed`, `INITIAL`/`REVIEW`, `REV-FIXA-1.0`, D1/D7/D14/D30,
  `ReviewStatusPolicy`, auditoria append-only, checker read-only e recovery S6.

## Auditoria fechada antes da implementação

1. **Schema e migration gate.** `Attempt` já possui `VALID`/`VOIDED`,
   `voided_at`, `void_reason`, `replaces_attempt` `OneToOne`, unicidades
   parciais de INITIAL/Review válida e guards de update/delete. Não será criada
   migration artificial em `attempts`: a cardinalidade de sucessora direta e
   os dados de void já são suficientes. Guards cross-row/cross-Workspace,
   aciclicidade e ponta efetiva ficam em selector/serviço/checker.
2. **Lacunas físicas confirmadas.** `AuditEvent` tem check constraint fechado
   apenas aos eventos S2A e não aceita entidade `ATTEMPT`; requer migration
   mínima para `ATTEMPT_VOIDED`/`ATTEMPT_REPLACED`. `ReviewCycle` não distingue
   uma projeção substituída por correção de um ciclo suspenso por arquivamento,
   nem permite uma projeção de correção iniciada por Attempt de REVIEW. Para
   preservar ciclos/Reviews concluídos sem reescrevê-los, a migration mínima
   acrescentará origem `ATTEMPT_CORRECTION`, estado `SUPERSEDED` e instante de
   supersession, com constraints explícitas. Não haverá backfill funcional.
3. **Lifecycle atual.** `Attempt.save/update/delete` impede mutação geral;
   somente um método interno de CAS poderá efetuar `VALID → VOIDED`. Creation
   continuará validando Question, revision, Alternative, Review, resultado,
   Workspace e contexto de replacement. `OperationReceipt` não será ampliado:
   correção é idempotente pela correlação de auditoria e revalidação da ponta,
   sem alterar a política de expiração do receipt.
4. **Derivados existentes.** Analytics/search já filtram `status=VALID` e
   classificação é OneToOne por Attempt; portanto VOIDED sai da projeção sem
   apagar classificação/revisões históricas. Reviews/Cycles exigem reconstrução
   explícita: pendências derivadas são canceláveis, ciclos ativos afetados são
   preservados como `SUPERSEDED` e uma nova projeção mínima é criada somente
   quando os fatos efetivos exigirem agenda atual.

## Decomposição fechada antes da implementação

1. **Ponta efetiva e grafo.** Criar selector único em `attempts` que resolva
   cadeia iterativamente em lote, com conjunto visitado, cardinalidade de
   sucessora e Workspace/contexto verificados. Ele será a fonte para preview,
   mutação, checker e testes; não haverá versões divergentes em analytics,
   classificação, timeline ou templates.
2. **Serviço transacional.** Criar `AttemptCorrectionService` Workspace-scoped
   com preview de impacto, void e replacement. Exigir motivo codificado,
   confirmação pela ponta esperada, Attempt `VALID`, contexto atual, CAS e
   correlação. Replacement deriva `is_correct` da mesma revision/Alternative,
   mantém tipo/Question/revision/Review, cria novo fato imutável e liga-o à
   ponta anulada. A operação será `atomic(durable=True)` e usará o retry SQLite
   existente; hooks de fault injection testarão rollback após void,
   replacement, reconstruction e antes/depois da auditoria.
3. **Reconstrução proporcional.** Não varrer a base. Para INITIAL, preservar
   ciclos de ativação independentes e substituir somente agenda cuja origem ou
   âncora efetiva foi invalidada; criar D1 apenas quando o último fato efetivo e
   a arquitetura vigente exigirem. Para REVIEW, preservar Review concluída e
   sua Attempt histórica, cancelar apenas pendência derivada, marcar o ciclo
   atual afetado como `SUPERSEDED` e materializar uma nova projeção conforme a
   decisão de `ReviewSchedulePolicy`. Void sem replacement reoferece a etapa
   anulada a partir do último fato válido; replacement usa o resultado novo.
   Nenhum estágio, prazo, policy ou timezone será redefinido.
4. **Classificação, analytics e timeline.** Não mover nem apagar
   `ErrorClassification`; VOIDED deixa de ser corrente pelo filtro central já
   existente. Replacement correta não herda classificação; incorreta permanece
   sem classificação até o fluxo autorizado. Analytics, `performed`,
   acerto/erro, categorias pessoais/merge e drill-down serão reconciliados por
   snapshots lógicos. Timeline passa a explicar estado, predecessor/sucessora e
   eventos correlacionados, sem UI geral.
5. **Checker read-only.** Acrescentar apenas checks S2B para estado de void,
   sucessora única, contexto, ciclos e ponta. Ajustar checks de Reviews para
   distinguir fatos concluídos históricos ligados a VOIDED de projeções atuais;
   `SUPERSEDED` não pode ter pendência. Não haverá repair.
6. **Upgrade, rollback e recovery.** Testar migrations reais de uma folha
   V0.4.4-equivalente por S2A até S2B, preservando AuditEvent, categoria
   pessoal/merge, ReviewScheduleChange e ciclo MANUAL. Reverse é tecnicamente
   seguro somente antes de fatos S2B; após supersession/auditoria, recovery é
   `restore required`. Provar backup, validação, restore isolado, checks físicos,
   checker, cadeia efetiva, analytics, ciclo/Review e classificação.
7. **Testes e gate.** Cobrir lifecycle/cadeia/ciclos/branch, INITIAL/REVIEW,
   contexto, Workspace, classification/merge, analytics, fault injection,
   concorrência local, migration e recovery; depois regressão focada,
   `makemigrations --check --dry-run`, `git diff --check`, A8 deep e gate
   autoritativo. Persistir evidence, métricas A7 observáveis, estado e
   arquivamento apenas após GREEN.

## Migration design

- `operations`: alterar choices e check constraints de evento/entidade, sem
  nova coluna, default ou backfill. Compatível com todos os eventos S2A.
- `reviews`: adicionar choices `ATTEMPT_CORRECTION`/`SUPERSEDED` e
  `superseded_at` nullable; dados antigos permanecem com valor nulo. Constraint
  exige instante somente em `SUPERSEDED`, preserva os estados anteriores e
  valida a presença de origem para correção. Nenhuma linha antiga é reescrita.
- Risco: high pela semântica de reconstrução, embora as mudanças sejam
  aditivas. Reverse antes de fatos S2B é seguro; depois deles perde metadados e
  estados necessários, portanto `restore required`.

## Riscos e controles

- **Branch/ciclo/dupla ponta:** `OneToOne`, unicidades parciais, selector com
  visited set, lock/CAS e revalidação antes da escrita.
- **História reescrita:** somente status de Attempt e projeções pendentes/ciclo
  atual sofrem transição explícita; Attempts, Reviews concluídas,
  classificações e revisões históricas permanecem.
- **Agenda incoerente:** policy vigente é a única fonte de próxima etapa; nova
  projeção referencia fatos válidos e o checker separa história de current.
- **Cross-Workspace/contexto:** todos os objetos são recarregados sob o mesmo
  Workspace antes de qualquer mutation e testes negativos cobrem cada FK.
- **Falha parcial/concorrência:** transação integral, constraint, CAS e fault
  injection; não há lock distribuído.
- **Leakage:** AuditEvent aceita somente IDs, correlação, motivo codificado e
  datas técnicas; nenhum conteúdo, payload ou secret.
- **Escopo:** nenhuma revisão de gabarito S2C, delete/retention/purge S2D, UI
  S3, domínio, prioridade, export/import ou mudança de arquitetura.

## Condição de saída

O desenho A4 está fechado antes de qualquer edição funcional. A execução segue
somente dentro de `V0.5-S2B`; conclusão depende de testes focados, upgrade e
recovery reais, A8 deep `APPROVED`, gate GREEN, evidence e `finish-task`.
