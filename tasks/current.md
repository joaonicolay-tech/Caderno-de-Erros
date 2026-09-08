# V0.3 — Etapa 1 — Fundação de Aprendizagem: Schema, Constraints e Políticas Puras

## Identificação e autorização

| Campo | Valor |
|---|---|
| Versão | V0.3 |
| Etapa | 1 |
| Status | **Liberada, não iniciada** |
| Execução | Obrigatoriamente em **novo chat**; esta autorização não permite iniciar a implementação no chat que a criou. |
| Baseline protegida | `v0.2.0` (`a756b6d`); migrations V0.1/V0.2 permanecem imutáveis. |

## Objetivo

Criar a fundação persistente da aprendizagem da V0.3: schema, migrations,
constraints, índices, validações de integridade e políticas puras, sem expor
qualquer jornada de aprendizagem ao usuário nesta etapa.

## Escopo autorizado

### Entidades e divisão de módulos

- Novo módulo `attempts`: `Attempt` e `OperationReceipt`.
- Módulo existente `errors`: `ErrorClassification` e `ErrorClassificationRevision`, preservando `ErrorCategory` como catálogo V0.2.
- Novo módulo `reviews`: `ReviewCycle` e `Review`.
- Referências somente a `accounts` (`Workspace`) e `questions` (`Question`, `QuestionRevision`, `Alternative`).

As seis entidades entram como schema. Não criar `AuditEvent`, `ReviewScheduleChange`, `SavedFilter`, categorias pessoais, domínio, prioridade, analytics, snapshots ou entidade adiada pelo ADR-011.

### Migrations previstas, dependências e ordem

1. `attempts/0001_learning_foundation`: `Attempt`, com FK para `Workspace`, `Question`, `QuestionRevision` e `Alternative`; depende de `accounts/0001_initial` e `questions/0002_question_catalog`.
2. `errors/0002_learning_classification`: `ErrorClassification` e `ErrorClassificationRevision`; depende de `errors/0001_initial` e `attempts/0001_learning_foundation`.
3. `reviews/0001_learning_foundation`: `ReviewCycle` e `Review`; depende de `accounts/0001_initial`, `questions/0002_question_catalog` e `attempts/0001_learning_foundation`.
4. `attempts/0002_review_receipt_constraints`: FK referencial de `Attempt` para `Review`, `OperationReceipt`, constraints/índices finais; depende de `reviews/0001_learning_foundation` e, quando necessário à composição final, de `errors/0002_learning_classification`. Não usar UUID solto nem criar dependência circular.

Os nomes finais devem respeitar o mecanismo Django, mas a ordem/dependências são obrigatórias. Não editar, regenerar, condensar ou reordenar migrations V0.1/V0.2. Provar instalação em banco vazio e upgrade de cópia `v0.2.0 → V0.3 Etapa 1`; rollback é restauração verificável do backup pré-upgrade ao plano V0.2, sem reversão manual de migration protegida.

### Constraints e invariantes por camada

| Camada | Garantias desta etapa |
|---|---|
| SQLite/schema | FKs `PROTECT`, índices, `CHECK` de enums/estados/faixas/datas/lock; unicidade parcial de inicial válida por questão, tentativa válida por `Review`, ciclo `ACTIVE` por questão e `Review` `PENDING` por ciclo; unicidade `(classification, revision_number)`, classificação por tentativa e `(workspace, operation_kind, idempotency_key)` do recibo. |
| Services | Revalidar Workspace, relações cruzadas, estado e `lock_version`; `Attempt.question` coincide com a `QuestionRevision` apresentada e alternativa/gabarito pertencem a ela; classificação somente para erro e obrigatória para incorreta finalizada; `Attempt` imutável e revisões de classificação append-only. |
| Policies puras | Implementar, sem ORM/escrita/transação, `ReviewSchedulePolicy` e `ReviewStatusPolicy`, com `Clock`/`Calendar` injetáveis para D1/D7/D14/D30 e situação temporal. Sem fila, conclusão ou agendamento de efeitos. |
| Transações | Preparar contratos curtos com validação final e recibo junto do efeito. `AttemptService` aceita apenas inicial e nunca cria ciclo/D1; `CompleteReviewService` será o único orquestrador do erro inicial e da conclusão da revisão. Não criar esses services nesta etapa. |

O isolamento por `Workspace` é obrigatório em FKs, consultas e validações; `CHECK` SQLite não lê outra tabela. A temporalidade usa `Clock.now()` e `Calendar.today(timezone)`/`add_days()`.

### Parâmetros congelados do ADR-011

- Contexto pós-resposta: transitório, 15 minutos, não renovável; não é model/migration desta etapa.
- SQLite crítico: `busy_timeout` de 5 segundos; um retry após 150 ms, somente para `SQLITE_BUSY`/`locked`, preservando a chave.
- `OperationReceipt`: retenção mínima de 30 dias e payload minimizado, sem conteúdo de estudo, sessão, token, corpo HTTP, IP ou dados pessoais desnecessários.
- Mesma chave/hash recupera o resultado; hash diferente conflita; efeito e recibo integram a mesma transação futura.
- As fronteiras `AttemptService`/`CompleteReviewService` são contratuais e não podem ser invertidas.

### RF, RN, RNF e fluxos aplicáveis

É um recorte fundacional, sem RF observável: sustenta `RF-021`–`026`, `RF-028`–`030`, `RF-034`–`035` e `RF-043`–`044`, sem executá-los. Exclui `RF-027`, `RF-031`–`033`, `RF-036`–`042` e `RF-045`–`046`.

Aplicar `RN-021`, `RN-026`, `RN-033`, `RN-039` e a parcela estrutural de `RN-023`, `RN-025`, `RN-028`, `RN-030`; `RN-032` é apenas base append-only e sua correção funcional é E4. Aplicar `RNF-013`, `RNF-025`–`027`, `RNF-031`–`033`, `RNF-057`. `FL-003` e `FL-010` são referência de schema/atomicidade/idempotência, não fluxos a implementar.

### Casos de teste obrigatórios

- `CT-073`: FKs rejeitam órfãos; `CT-074`: vínculo entre Workspaces é rejeitado.
- `CT-076`: segunda inicial válida é rejeitada; `CT-077`: segunda tentativa válida da mesma revisão é rejeitada.
- `CT-078`: segundo ciclo ativo da questão é rejeitado; histórico concluído permanece possível.
- `CT-079`: segunda `Review` pendente é rejeitada no banco e serviço.
- `CT-080`: mesma chave/hash recupera recibo; hash divergente conflita.
- `CT-081`: migrations em banco vazio; `CT-082`: upgrade V0.2 preserva contagens, vínculos, datas e histórico; backup/restauração prova rollback.
- Complementares: `CHECK`, imutabilidade, classificação só em erro, revisão apresentada, minimização/retenção do recibo, Clock/Calendar, corrida e retry SQLite controlado.

## Fora de escopo

- fluxo web de resposta, apresentação de correção e tela pós-resposta;
- contexto transitório funcional, fila/selector, conclusão funcional de revisão, timeline, dashboard, métricas e analytics;
- diagnóstico/correção funcional, arquivamento com suspensão, reativação, jobs, broker, lock distribuído, retry infinito ou PostgreSQL;
- V0.4+ e entidades adiadas; commit, push, tag ou release.

## Critérios de aceite verificáveis

1. As seis entidades existem nos módulos definidos, sem entidade adiada nem interface/fluxo antecipado.
2. Migrations respeitam ordem/dependências, preservam hashes/conteúdo V0.1/V0.2 e passam em banco vazio (`CT-081`).
3. Schema materializa FKs, checks, índices e unicidades; `CT-073`, `074`, `076`–`080` passam.
4. Upgrade `v0.2.0 → V0.3 Etapa 1` preserva dados; restauração do backup pré-upgrade retorna a V0.2 (`CT-082`).
5. Não há vazamento entre Workspaces nem referência incompatível entre tentativa, classificação e revisão.
6. Recibo prova idempotência/colisão; contenção verifica timeout, retry único e ausência de estado parcial ou falso sucesso.
7. Policies são puras e determinísticas com Clock/Calendar controláveis; não criar service, view, form ou template de fluxo.
8. Gate autoritativo GREEN.

## Gate obrigatório

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1
```

Exit code diferente de `0` bloqueia a conclusão. Registrar evidências de migration, upgrade/rollback, constraints, concorrência e gate antes de arquivar; não iniciar a Etapa 2 automaticamente.

## Fontes vinculantes

- `docs/ADR-011_Saneamento_Fronteira_e_Rastreabilidade_V0.3.md` (§§2, 4–9);
- `docs/Caderno_de_Erros_Inteligente_Etapa_7_Modelo_de_Dados.md` (§§7–9, 14 e errata V0.3);
- `docs/Caderno_de_Erros_Inteligente_Etapa_6_SDD.md` (errata V0.3);
- `docs/Caderno_de_Erros_Inteligente_Etapa_10_Plano_de_Testes.md` (§9.6 e `ERR-V03-001`).
