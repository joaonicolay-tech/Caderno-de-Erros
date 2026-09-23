# Plano A4 — V0.5-S2D: exclusão permanente por agregado

- ID da tarefa: `V0.5-S2D` (`tasks/current.md`, `AUTHORIZED`).
- Status: `COMPLETED` — implementação, A8 deep e gate registrados em
  `quality/v05-s2d-permanent-deletion-result.md`.
- Baseline auditado: `654a9af885caa83610e9b32c1b8b73362220e9ec`;
  `v0.4.4` é a base histórica, S2A/S2B/S2C já estão no código.
- Escopo: somente services/domain, schema mínimo justificado, checker, testes,
  recovery e evidência S2D. S3+ permanece sem autorização.
- Regra de entrada cumprida: as decisões destrutivas abaixo foram resolvidas
  explicitamente pelo usuário. O plano continua limitado a S2D.

## Fontes e reconciliação

- `AGENTS.md`, `tasks/current.md`, `docs/A3_Progressive_Disclosure.md` e
  `tasks/plans/v05-release-execution-plan.md` dão autoridade e limites.
- `docs/V0.5_S1_Contratos_Normativos_e_Invariantes.md` §§ exclusão,
  auditoria, migrations e S5/S6 é a decisão S1 de retenção sanitizada.
- `docs/Caderno_de_Erros_Inteligente_Etapa_3_Requisitos_Funcionais.md`
  RF-020/RF-071; `docs/Caderno_de_Erros_Inteligente_Etapa_5_Regras_de_Negocio.md`
  RN-087–091; `docs/Caderno_de_Erros_Inteligente_Etapa_7_Modelo_de_Dados.md`
  §13; `docs/Caderno_de_Erros_Inteligente_Etapa_8_Fluxos_Principais.md`
  FL-007 fixam preview, confirmação e ordem conceitual.
- `docs/ADR-011_Saneamento_Fronteira_e_Rastreabilidade_V0.3.md` §7 fixa a
  retenção mínima e condições de descarte de `OperationReceipt`.
- Models/migrations e serviços atuais de `questions`, `attempts`, `errors`,
  `reviews`, `operations`, `taxonomy`, `analytics`, `search` e
  `data_management`; checker `operations/integrity.py`; testes S2A/S2B/S2C.
- `quality/v05-s2a-foundation-result.md`,
  `quality/v05-s2b-attempt-correction-result.md`,
  `quality/v05-s2c-answer-key-correction-result.md` e `PROJECT_STATE.md`
  confirmam o baseline implementado. `PROJECT_STATE.md` ainda descreve S2D
  como não autorizada; a autorização mais recente está em `tasks/current.md`.

## Grafo real e classificação

Todas as FKs funcionais auditadas abaixo usam `PROTECT`; a implementação
precisa tratar a ordem explicitamente. O mesmo `Workspace` deve ser verificado
em cada aresta antes da mutação. A tabela marca o destino autorizado;
referência externa inesperada é `BLOCKS_DELETE`.

| Relação real | Classe | Motivo e tratamento previsto |
| --- | --- | --- |
| `Question` → `Workspace`, `Discipline`, `Subject`, `Subsubject` | `SHARED_PRESERVE` | Remover somente a Question; taxonomia e Workspace sobrevivem. |
| `QuestionRevision.question` → `Question`; `Alternative.question_revision` → revisão; `QuestionRevision.correct_alternative` → `Alternative` | `DELETE_WITH_AGGREGATE` | Todas as versões R1/R2/R3 e alternativas, inclusive a correta; o ciclo é removido na mesma transação com FKs diferidas. |
| `Attempt.question/question_revision/selected_alternative/review/replaces_attempt` | `DELETE_WITH_AGGREGATE` | Todos INITIAL/REVIEW, VALID/VOIDED; cadeia inteira, inclusive sucessoras, removida em ordem de folhas para raiz. Elo fora da Question bloqueia. |
| `ErrorClassification.attempt`; `ErrorClassificationRevision.error_classification` | `DELETE_WITH_AGGREGATE` | Projeção atual e histórico de classificação ligados às Attempts removidas. |
| `ErrorClassification.category`, `ErrorClassificationRevision.category` | `SHARED_PRESERVE` | Categoria padrão/pessoal, inclusive MERGED, não muda lifecycle nem é apagada. |
| `ReviewCycle.question/origin_attempt/origin_question_revision`; `Review.review_cycle/question/scheduled_from_attempt`; `ReviewScheduleChange.review` | `DELETE_WITH_AGGREGATE` | Ciclos ACTIVE/COMPLETED/SUPERSEDED, inclusive MANUAL e ATTEMPT_CORRECTION, Reviews PENDING/concluídas e reagendamentos; validar todas as âncoras. |
| `QuestionOrigin.question` | `DELETE_WITH_AGGREGATE` | Associação pertence à Question. |
| `QuestionOrigin.source/exam/board`; `Exam.board` | `SHARED_PRESERVE` | Catálogos de origem são reutilizáveis. |
| Tags e tabela de associação | Sem model/tabela implementada no baseline | Nada a apagar em S2D; reauditar no upgrade. |
| Analytics/dashboard/drill-down, busca e fila | `DERIVED_RECONCILE` | Consultas sobre fatos; nenhum cache ou snapshot materializado de Question encontrado. Testar antes/depois. |
| `AuditEvent` S2A/S2B/S2C com IDs de Question, Attempt, revisão, ciclo ou Review | `DELETE_WITH_AGGREGATE` | Exceção append-only exclusiva do delete permanente; nenhum ID sem alvo permanece. |
| `OperationReceipt.result_entity_id` → Attempt, sem FK | `BLOCKS_DELETE` ou `DELETE_WITH_AGGREGATE` | Bloqueia antes de 30 dias ou com contexto transitório válido; depois é removido junto com a Attempt. |
| Outro vínculo ou referência cross-Workspace descoberta no preview/revalidação | `BLOCKS_DELETE` | Abortar e emitir finding; nunca apagar dado do outro Workspace. |

Não há `CASCADE` amplo que resolva o agregado; todo relacionamento acima é
`PROTECT` ou referência técnica sem FK. Os métodos de model/QuerySet bloqueiam
delete normal de fatos imutáveis, de `AuditEvent` e de `OperationReceipt`;
qualquer exceção exclusiva ao serviço S2D precisa ser limitada e testada.

## Elegibilidade e preview

1. Selector read-only por `(workspace_id, question_id)` carrega estado,
   versões, alternativas, origem, Attempts e cadeias, classificações/revisões,
   ciclos/Reviews/reagendamentos, eventos e recibos. Valida o pertencimento de
   cada nó e aresta. Conta também efeitos analíticos e pendências. Não retorna
   texto de conteúdo no preview persistido/log.
2. DTO fechado: `eligible`, `blockers`, `warnings`, `impact`, contagens,
   `backup_required`, tipo de confirmação e versão/fingerprint técnico do
   estado. Preview não faz backup nem escrita.
3. DRAFT sem Attempt, ciclo nem dependência histórica tem confirmação simples
   por RN-088/S1. Revisões de conteúdo e alternativas do próprio rascunho
   integram seu agregado; decidir o tratamento de origem/recibo/evento antes
   de classificar um rascunho como simples.
4. Question com histórico mantém arquivamento como padrão. Candidata a
   exclusão somente após impacto, backup S6 validado por restore isolado/S5,
   confirmação reforçada, revalidação e ausência de dependência bloqueante.
   Recibos dentro de 30 dias ou com contexto transitório válido bloqueiam.
   Rascunho objetivamente simples pode dispensar backup obrigatório.
5. Confirmação nunca confia no preview: transação, lock/revalidação de
   Workspace, estado, `lock_version`, grafo e contagens. Preview antigo ou
   dependência nova é conflito, sem mutação. Objeto inexistente com correlação
   diferente não recebe sucesso fictício; retry após remoção é conflito porque
   o evento sanitizado não retém o ID da Question.

## Backup, transação e ordem condicional

- S6 existente: `backup_sqlite`/`create_sqlite_backup`, manifesto SHA-256,
  `validate_backup`, `restore_backup` em arquivo isolado, reconciliação e
  `check_integrity` S5 exit 0. Backup pré-delete válido precede exclusão quando
  requerido. A cópia primária nunca é destino de ensaio. Backups antigos não
  são reescritos; backup pós-delete só complementa o teste de recovery.
- Na unidade `transaction.atomic(durable=True)` e escrita SQLite crítica,
  adquirir controle de concorrência da Question/agregado; revalidar. Mutações
  S2B/S2C, criação de Attempt, conclusão/reagendamento e double delete devem
  serializar ou conflitar. Usar CAS/`lock_version` e `select_for_update` onde
  aplicável, apoiados por constraints e teste de interleaving.
- Ordem SQL explícita na transação, com FKs diferidas pelo SQLite e verificação
  final de FKs: (1) referências técnicas `AuditEvent`/`OperationReceipt`
  autorizadas; (2) `ReviewScheduleChange`; (3)
  `ErrorClassificationRevision` e `ErrorClassification`; (4) ReviewCycles;
  (5) Reviews; (6) todas as Attempts, inclusive cadeias S2B; (7)
  `QuestionOrigin`; (8) todas as Alternatives; (9) todas as
  `QuestionRevision`; (10) Question; (11) reconciliação dos derivados e
  evento final. O ciclo `ReviewCycle.origin_attempt` ↔ `Attempt.review` e o
  ciclo `QuestionRevision.correct_alternative` ↔ `Alternative.question_revision`
  impedem uma ordem ORM simples sem alteração transitória de fatos imutáveis.
  O SQL explícito remove todos os nós antes da checagem FK no commit, sem
  `CASCADE` e sem reescrever fatos. Uma falha em qualquer ponto reverte tudo.
- Fault injection: após lock/elegibilidade, primeira dependência, meio da
  ordem, antes/depois da reconciliação, antes/depois de AuditEvent e antes do
  commit; cada falha restaura todos os fatos e não deixa evento sem delete.
- Nenhum `repr` de Question/Attempt, texto de classificação, stem, answer,
  payload ou snapshot em logs/erros. Timeline funcional acaba com o agregado.

## Schema, auditoria, retenção e purge

- Migration S2D é justificada ao menos pelo novo choice/constraint
  `QUESTION_PERMANENTLY_DELETED` e pela nulabilidade/estrutura de `entity_id`
  para o evento final sem Question ID. `expires_at` é derivável de
  `created_at + 90 × 24 h` e não requer coluna. Sem backfill cosmético.
- Evento final permitido por S1: código, timestamp autoritativo, ID do próprio
  evento, correlação técnica, tipo de entidade e motivo codificado. Não reter
  Question ID, revisões, texto, payload ou dados reconstruíveis. Decisão humana
  desta execução permite `workspace_id` técnico para isolamento, mesmo sem
  constar da lista fechada de S1. `previous_entity_id`,
  `related_entity_id`, datas de review e timezone devem ser nulos.
- AuditEvents anteriores diretamente vinculados ao agregado são removidos
  dentro do fluxo de exclusão, como exceção explícita e exclusiva à regra
  append-only. Nenhum ID ou referência técnica ao objeto apagado sobrevive.
- Retenção S1: 90 dias corridos e expurgo obrigatório. Decisão humana desta
  execução fixa `created_at` do AuditEvent como fonte e 90 períodos de 24 horas
  em UTC; o evento é elegível no instante exato
  `created_at + timedelta(days=90)` (`now >= expiry`). Purge antecipado é
  vedado. Implementar manutenção explícita idempotente somente dos eventos S2D
  sanitizados e expirados, sem scheduler e separada do checker read-only. Expiração de
  `OperationReceipt` continua sob seu contrato próprio, nunca sob os 90 dias.

## Verificação e saída após decisões

- Testes focados: elegibilidade/preview sem escrita, DRAFT e histórico,
  Workspace/anomalia externa, stale preview, confirmação, backup exigido,
  agregado rico R1/R2/R3 com S2A/S2B/S2C, todas as classes de Review,
  categorias compartilhadas, origens, recibos/eventos, FK/checker, analytics,
  timeline, ordem, double delete, retry, interleavings e fault injection.
- Testes de retenção nos dois lados e exatamente no limite temporal; purge
  seletivo/idempotente; conteúdo proibido e logs; migration reversível antes de
  fatos, restore pré-delete e backup pós-delete em arquivo isolado. Upgrade
  V0.4.4-equivalente → S2A → S2B → S2C → S2D preserva fatos anteriores.
- Checker S5 permanece read-only; novos checks apenas para sanitização,
  retenção, vínculos técnicos e consistência após delete. Analytics calculado
  por queries deve reconciliar registered/performed, attempts, acertos/erros,
  taxas, categoria/merge, disciplina/assunto e drill-down sem cache órfão.
- A8 deep precisa `APPROVED` sem Blocker/Major; então gate
  `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1`
  exit 0 observado, evidência, métricas A7, estado e arquivamento. Nenhum
  commit/push/tag/release nem início de S3.
- Reverse migration com fatos S2D não recupera conteúdo. Recovery só por
  backup compatível pré-delete, isoladamente restaurado e validado.

## Human Decision Gate — liberado

Decisão explícita do usuário nesta execução:

1. Remover controladamente `AuditEvent` antigos diretamente vinculados ao
   agregado na transação S2D; a exceção append-only não vale para outro fluxo.
2. Bloquear enquanto `OperationReceipt` não completar 30 dias ou tiver
   contexto transitório válido. Depois, removê-lo com o agregado.
3. Permitir histórico mediante preview, ausência de bloqueios, backup S6
   criado/validado/restaurado isoladamente com S5, confirmação reforçada e
   revalidação imediata. Rascunho simples sem histórico/dependência relevante
   pode dispensar backup por regra objetiva/testável/auditável.
4. Evento final mantém `workspace_id` técnico sem Question ID. Expurgo manual
   elegível em `created_at + 90 × 24 h` UTC, no limite exato.
