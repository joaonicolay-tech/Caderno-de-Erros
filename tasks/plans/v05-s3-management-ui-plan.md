# Plano V0.5-S3 — UI de gestão, confirmações e filtros salvos

- Task ID: `V0.5-S3`
- Status: `COMPLETED`
- Autoridade: `tasks/current.md` (`AUTHORIZED`); somente S3 está autorizada.
- Objetivo: entregar a UI de gestão sobre os services S2A–S2D e salvar filtros
  da listagem de Questions sem duplicar busca, paginação ou regras de domínio.
- A4: concluído em 2026-09-23, antes da primeira edição funcional.
- Baseline: `main`, HEAD `53c92f517950a1a2d884e4fb41de939deb82bde7`; alteração
  preexistente de `tasks/current.md` é o contrato S3 autorizado e será preservada.
- Evidência de baseline: encerramento S2D registra gate GREEN, exit 0, 409 testes,
  87% de cobertura e A8 deep APPROVED; esse resultado histórico não é tratado como
  gate desta execução.
- Política de execução desta autorização: GPT-6 Luna, reasoning xHigh, conforme
  `tasks/current.md` e pedido da execução; escalar somente nos gatilhos abaixo.

## A4 — auditoria anterior à implementação

### Fontes lidas

- `AGENTS.md`, `tasks/current.md`, `docs/A3_Progressive_Disclosure.md`,
  `PROJECT_STATE.md`, `tasks/plans/README.md`,
  `tasks/plans/v05-release-execution-plan.md` e
  `docs/V0.5_S1_Contratos_Normativos_e_Invariantes.md`.
- Contratos de conclusão S1, S2A, S2B, S2C e S2D; `quality/v05-s2d-human-decision-gate.md`;
  `quality/v05-s2d-permanent-deletion-result.md` e evidências A8/gate ali registradas.
- Código e testes diretamente relacionados às rotas, listagem, serviços,
  migrações, Workspace, backup/recovery, checker, acessibilidade e gate, conforme
  o inventário desta seção.

### Baseline e superfície existente

- Rotas Questions: listagem, criação/ativação, detalhe, edição e arquivamento em
  `modules.questions.urls`/`views`; Attempts expõe somente resposta INITIAL;
  Reviews expõe fila, timeline, correção de diagnóstico e conclusão.
- Categorias pessoais não têm views/URLs de gestão. Os serviços S2A existentes
  oferecem create/rename/archive/merge com escopo de Workspace e versões de lock.
- A listagem já usa `QuestionSearchForm`, `list_questions` e
  `paginate_questions`: busca, status, disciplina, assunto, subassunto, estado de
  Review, resultado INITIAL e categoria de erro são filtros conhecidos; tamanho
  de página é 10. O selector filtra e ordena antes da paginação e já seleciona ou
  prefetch os dados da listagem.
- `modules.search` hoje é biblioteca de forms/selectors, não está em
  `INSTALLED_APPS`, não possui `apps.py`, `models.py` ou migrations. Busca atual é
  GET; páginas de mutação existentes usam forms Django, POST e PRG. Templates usam
  HTML semântico; não há HTMX nem `django.contrib.messages`/middleware de sessão.
- Workspace local é resolvido por `get_workspace_for_owner(LOCAL_USER_ID,
  LOCAL_WORKSPACE_ID)`. O `Workspace` contém `owner_user`; queries de leitura e
  mutation devem sempre escopar ambos, além de validar referências de payload no
  Workspace corrente.
- `CsrfViewMiddleware` está ativo. Não há motivo para exceção de CSRF ou para
  mapear `request.POST` diretamente a campos de model.
- S2A services: `ReviewScheduleService.reschedule` exige `expected_lock_version`;
  `ManualReviewInclusionService.include` aceita Question e motivo opcional;
  `PersonalCategoryService` implementa os quatro ciclos solicitados e valida
  estado/versão/Workspace.
- S2B `AttemptCorrectionService.preview/void/replace` expõe impacto e exige a
  ponta efetiva observada; replacement cria novo fato e aceita chave idempotente.
  S2C `AnswerKeyCorrectionService.correct` recebe revisão observada e posição do
  novo gabarito; QuestionRevision e Alternative são imutáveis.
- S2D `PermanentQuestionDeletionService.preview/delete` é a fronteira exclusiva.
  Preview fornece elegibilidade, blockers, warnings, impacto, fingerprint,
  `backup_required` e token de confirmação. Delete revalida tudo e, para histórico,
  cria, valida e restaura isoladamente o backup antes de excluir. Exige caminhos
  novos fornecidos pelo chamador; o diretório deve existir e ser direto, sem link
  ou junction. `docs/V0.4_S6_Backup_e_Recuperacao.md` documenta `backups/` como
  convenção, preservação do par SQLite/manifesto e ausência de rotação automática.
- A exclusão S2D já está fechada pelo Human Decision Gate; não há decisão humana
  aberta aplicável a S3. O serviço, elegibilidade, fingerprint, backup, agregado,
  auditoria, retention, purge e recuperação permanecem protegidos.
- `scripts/quality.ps1` usa `quality/v05-s2d-migrations.json` como manifesto
  suplementar único. Uma migration S3 exige manifesto suplementar S3 com hashes
  completos do conjunto V0.5 e seleção dele no gate; manifestos S2 anteriores
  não devem ser reescritos.
- A8 é revisão de risco, não preferência de estilo (`docs/review/code-review.md`).
  O gate autoritativo continua `scripts/quality.ps1`; checker S5 é read-only.

### Decisão A4 de migration e SavedFilter

- **Migration necessária e aprovada pelo contrato:** hoje não existe persistência
  de filtro; sem tabela não se pode satisfazer criar/aplicar/renomear/excluir.
  Não haverá backfill de dados transitórios.
- Registrar `modules.search` como app Django e criar o schema mínimo
  `SavedFilter`: FK `workspace`, FK `owner_user`, nome de apresentação, chave de
  nome normalizada, `context_code`, `schema_version`, `payload` JSON fechado e
  timestamps `created_at`/`updated_at`. Unicidade por owner/contexto/nome
  normalizado; Workspace permanece obrigatório e validado contra owner.
- Contexto inicial único: `QUESTIONS_LIST`, `schema_version=1`. Payload contém
  somente filtros reconhecidos por `QuestionSearchForm` (query, status,
  discipline, subject, subsubject, review_status, initial_result e error_category).
  `page` não é filtro salvo. Rejeitar chave/tipo/estrutura inesperados, valor fora
  do choice, hierarquia taxonômica incoerente, ID ausente/de outro Workspace,
  contexto diferente e versão sem suporte. Categoria arquivada/merged não será
  reinterpretada: marcar o filtro como requer ajuste quando não puder ser aplicado
  com o significado atual.
- Aplicação traduz o payload validado para os parâmetros da listagem existente e
  redireciona para URL determinística. A view atual continua sendo a única dona
  da chamada de form, selector e paginação.
- Migration aditiva e reversível por remoção somente da nova tabela; não altera
  tabelas, migrations, services ou semântica S2A–S2D. Provar banco vazio,
  upgrade existente, constraints/defaults e ausência de drift de migrations.

### Decisões de UX, segurança e performance

- Forms/views/templates server-rendered e URLs namespaced; manter fallback HTML,
  GET somente para leitura/preview, POST para mutação e PRG após sucesso.
- Feedback usa padrão atual de códigos de resultado na URL e erros de form; não
  adicionar HTMX ou sistema global de mensagens nesta tarefa.
- Forms declaram todos os campos permitidos; IDs são carregados por selector
  Workspace-scoped. Stale lock, ponta efetiva, revisão corrente ou fingerprint
  resultam em erro explícito e nova confirmação/preview, sem retry automático.
- Para S2D, nunca aceitar caminho de backup/restauração vindo do browser. Gerar
  nomes únicos/correlation IDs no servidor dentro do `BASE_DIR/backups` existente,
  que é ignorado pelo Git e documentado pelo S6; usar diretório temporário novo
  dentro desse destino para o restore isolado e removê-lo ao final. Preservar o
  backup validado e manifesto. Diretório ausente, inseguro, sem espaço ou sem
  permissão deixa a operação falhar fechada; nenhum sucesso é informado.
- Confirmar acessibilidade por labels, `aria-describedby`, erro associado,
  headings, status, teclado e foco em erro; manter distinção semântica de ações
  destrutivas e empty states explicitados em `tasks/current.md`.
- Reusar `select_related`/`prefetch_related` existentes; adicionar provas de
  consultas para páginas/listas S3 de maior agregação, sem duplicar consultas de
  preview nem carregar timeline por item.

### Auditoria de testes e regressão

- Padrões e cobertura a ampliar: `tests/test_question_search.py`,
  `tests/test_question_interface.py`, `tests/test_review_completion.py`,
  `tests/test_taxonomy_interface.py`, `tests/test_error_categories.py`,
  `tests/test_v05_s2a.py`, `tests/test_v05_s2b.py`, `tests/test_v05_s2c.py`,
  `tests/test_v05_s2d.py`, `tests/test_integrity_checker.py`,
  `tests/test_backup_recovery.py` e `tests/test_quality_gate.py`.
- Criar testes S3 para SavedFilter CRUD/schema/contexto/ownership, fluxos das quatro
  famílias de UI, service boundary, stale state, Workspace, GET/CSRF, double
  submit, empty states e consultas. Migration/upgrade recebe teste específico sem
  mudar manifestos históricos.
- Rodar primeiro testes S3 e suites diretamente alteradas; depois regressão
  Questions/search, Reviews, S2A–S2D, categories/analytics/timeline, checker e
  backup/recovery; por fim o gate completo com exit code observado.

## Decomposição

1. Implementar SavedFilter no app `search`, migration mínima, validator/service de
   payload fechado e CRUD/apply integrado à listagem e paginação existentes.
2. Adicionar forms/views/URLs/templates de reagendamento, inclusão manual e
   categorias pessoais, chamando exclusivamente services S2A.
3. Adicionar fluxos separados de preview/confirm para void e replacement S2B,
   correção prospectiva de gabarito S2C e preview/confirmação de exclusão S2D.
4. Adicionar testes focados de interface, isolamento, stale, HTTP/CSRF, acessibilidade
   semântica, performance e boundaries de service; testar upgrade da migration.
5. Criar manifesto de migrations S3 sem alterar manifestos históricos; ajustar
   somente a seleção do manifesto corrente no gate e cobrir essa seleção.
6. Executar regressão relacionada, revisão A8 standard, gate completo; criar
   `quality/v05-s3-management-ui-result.md`, registrar A7 apenas com valores
   observáveis, atualizar `PROJECT_STATE.md` e arquivar S3 somente após todos os
   critérios do contrato estarem comprovados.

## Dependências, riscos e escalonamento

- S2A–S2D são dependências concluídas; a UI apenas chama suas fronteiras existentes.
- Migration adiciona só preferências `SavedFilter`; rollback da migration remove
  essas preferências e não afeta fatos S2A–S2D. Não presumir rollback de outros
  dados persistentes.
- Diretório de backup e double submit são falhas que devem ser recusadas sem
  contornar S2D; operação de delete bem-sucedida usa exatamente o service oficial.
- Não há complexidade backend transversal identificada além do app/model/migration
  isolados de SavedFilter e config de destino já documentada pelo S6. Não escalar
  modelo por ora.
- Se implementação exigir mudança em eligibility, backup policy, aggregate boundary,
  retention/purge, reconstrução S2B ou versionamento S2C, parar antes da mudança,
  recomendar GPT-6 Sol High e A8 deep. Se nova arquitetura/backend transversal
  exceder os itens previstos acima, registrar o achado antes de implementação pesada
  e recomendar GPT-6 Sol Medium.
- A8 standard está planejado enquanto S2A–S2D e integridade persistente ficarem
  intocados; qualquer gatilho acima exige A8 deep.

## Condição de saída

Concluída conforme o contrato S3: evidência GREEN e A8 aprovado em
`quality/v05-s3-management-ui-result.md`, estado factual atualizado, contrato
arquivado e `tasks/current.md` retornado a `NO_TASK_AUTHORIZED`. S4+ continuam
não autorizadas; nenhum commit, push, tag, release ou funcionalidade posterior
foi iniciada nesta execução.
