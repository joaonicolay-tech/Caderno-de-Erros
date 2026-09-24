# Task Contract

Status: COMPLETED

## Identification

- Task ID: V0.5-S3
- Product version: V0.5 -- Beta das capacidades V1
- Stage: UI de gestão, confirmações, categorias pessoais e filtros salvos
- Task type: implementação funcional de UI e persistência isolada de SavedFilter
- Size: M
- Risk: high
- Migration: EXPECTED, sujeita à auditoria do schema e decisão fundamentada no A4
- A4: obrigatório antes da implementação funcional
- Recommended execution model: GPT-6 Luna, reasoning xHigh; escalar para GPT-6 Sol Medium se o A4 revelar complexidade backend/transversal além do escopo previsto; escalar para GPT-6 Sol High se for necessário alterar a fronteira de segurança de exclusão permanente
- A8 review: standard; deep obrigatório se houver alteração de comportamento destrutivo ou integridade de dados, conforme gatilhos abaixo

## Goal

Entregar a camada de gestão/UX da V0.5 sobre os serviços estabilizados em S2A–S2D, com fluxos seguros, acessíveis e isolados por Workspace, sem duplicar regras de domínio na UI.

## Context

- Baseline: V0.4.4, V0.5-P0, V0.5-S1 e V0.5-S2A–S2D concluídos; serviços críticos disponíveis; checker read-only saudável; backup/recovery S6 disponível.
- S3 é a única tarefa autorizada. S4 e etapas posteriores não estão autorizadas.
- Fontes normativas: `docs/V0.5_S1_Contratos_Normativos_e_Invariantes.md` e `tasks/plans/v05-release-execution-plan.md`.
- Evidências de conclusão: `tasks/completed/v05-s1-normative-contracts-and-invariants.md`, `tasks/completed/v05-s2a-auditable-foundation-and-nondestructive-management.md`, `tasks/completed/v05-s2b-attempt-correction-reconstruction.md`, `tasks/completed/v05-s2c-answer-key-correction.md`, `tasks/completed/v05-s2d-permanent-deletion.md`; resultado S2D em `quality/v05-s2d-permanent-deletion-result.md`.
- S1 exige para SavedFilter owner e Workspace, nome único por owner/contexto, `context_code`, `schema_version`, payload fechado com operadores/campos permitidos e IDs do mesmo Workspace; referências arquivadas devem permanecer compreensíveis ou exigir ajuste, e campos removidos/futuros não podem ser interpretados silenciosamente.

## Acceptance Criteria

- Antes de implementação funcional, concluir plano A4 S3 auditando URLs, views, forms, templates/componentes, HTMX, services S2A–S2D, feedback/messages, stale state, concorrência, confirmações, SavedFilter, schema/migrations, acessibilidade, segurança, testes, regressão, A8 e gate. O A4 decide se migration é necessária; não criar migration para UI.
- SavedFilter permite salvar/aplicar filtro atual, renomear e excluir, com estados vazios e tratamento de contexto/schema incompatível. Reutiliza filtros/listagem vigentes, aplica filtros antes de paginação e mantém URLs/estado determinísticos. Payload é fechado e validado; não aceitar querystrings arbitrárias nem payload executável. Provar create/apply/rename/delete, nome duplicado, payload inválido, incompatibilidade de contexto/schema e isolamento de owner/Workspace; acesso incompatível falha explicitamente.
- Gestão de Reviews oferece reagendamento e inclusão manual. Reagendamento mostra Review e data atual, coleta nova data e motivo quando exigido, valida entrada e trata stale state. Inclusão manual mostra Question, motivo/efeito e confirmação. Ambos chamam services S2A; views não editam Review nem criam ReviewCycle diretamente.
- Categorias pessoais oferecem create, rename, archive e merge conforme S2A. Merge deixa claros origem, alvo, preservação do histórico físico na origem, mudança da projeção atual ao alvo e que merge não é delete; somente pessoal ACTIVE para pessoal ACTIVE no mesmo Workspace. Não oferecer mutações proibidas para categorias padrão. Cobrir fluxos, validações, cross-Workspace e stale version.
- Correção de Attempt oferece fluxos distintos de void e replacement via S2B, nunca edita Attempt diretamente. Void exige motivo, informa que o fato histórico permanece e projeções correntes serão reconstruídas; replacement informa que a Attempt atual será anulada, nova Attempt criada e histórico preservado. Exibir impacto/confirmar antes da ação. Se a ponta efetiva mudar entre renderização e confirmação, apresentar conflito sem correção automática. Cobrir impacto/confirmação, stale tip e erros de domínio.
- Correção de gabarito usa exclusivamente `AnswerKeyCorrectionService` S2C. Apresenta revisão/gabarito atual, novo gabarito, motivo e aviso claro de que a correção afeta tentativas futuras e não reinterpreta automaticamente tentativas históricas; não sugere recálculo de analytics antigos. Cobrir correção, stale revision, validação de exatamente uma alternativa correta e preservação da apresentação histórica.
- Exclusão permanente usa somente preview e serviço oficial S2D, sem `.delete()` direto ou bypass. A UI consome elegibilidade, blockers, warnings, impacto, requisito de backup, confirmação e fingerprint/state token conforme API existente. Em estado blocked, explica a razão sem caminho alternativo. Se backup validado for exigido, não libera confirmação final até cumprir o requisito. Stale fingerprint, falha, double submit e cross-Workspace são tratados sem contornar S2D. Cobrir preview elegível/bloqueado, backup, confirmação, stale fingerprint, sucesso, duplo envio, isolamento e falha sem bypass.
- Todas as mutações preservam isolamento por Workspace e usam serviços oficiais S2A–S2D; stale state/conflitos são apresentados explicitamente. Regras críticas não são duplicadas na camada UI. Checker continua read-only, sem reparo automático.
- Segurança HTTP: GET não destrutivo; métodos apropriados para mutações, CSRF conforme estratégia de testes e respostas corretas para redirect/HTMX. Erros de domínio são apresentados adequadamente.
- Acessibilidade básica verificada: labels, associação de erros, semântica de confirmações destrutivas, teclado/foco quando suportado; revisão manual/documental complementar onde automação não cobrir. Incluir empty states para nenhuma categoria pessoal, nenhum filtro salvo, nenhuma Review elegível, item stale/alterado e exclusão bloqueada. Evitar N+1/consultas repetidas para categories, previews, SavedFilter e timeline; reutilizar selectors existentes.
- Regressão relacionada cobre dashboard, list/search/filter, detalhe de Question, Reviews, S2A–S2D, categorias, timeline, checker e backup/recovery.
- A8 standard para UI + SavedFilter isolado. Escalar para deep se houver alteração no serviço/eligibilidade/aggregate boundary/backup requirement de exclusão permanente, reconstrução S2B, versionamento S2C ou migration com impacto além de SavedFilter.
- Gate final `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1` GREEN observável; registrar tentativa 1, falhas reais, retries, incidentes e first-pass corretamente.

## Expected Scope

- A4 S3; URLs/views/forms/templates/components; integração HTMX/messages; SavedFilter e migration mínima somente se confirmada necessária; testes de UI/serviços, segurança, isolamento e acessibilidade; evidência S3 e documentação estritamente necessária.
- `quality/`, `PROJECT_STATE.md`, métricas A7 e arquivamento da tarefa somente no encerramento comprovado da S3.

## Protected Scope

- Semântica de S2A, lifecycle S2B, versionamento S2C, fronteira agregada, eligibility, retenção de 90 dias, backup requirement, recovery, checker e policies de scheduling. Se a UI exigir mudança em qualquer regra, parar, reclassificar o impacto e não alterar silenciosamente.
- Nenhuma alteração de domínio fora da UI necessária, repair do checker, mecanismo paralelo de busca, dashboards personalizados complexos ou funcionalidade S4+.

## Constraints

- Services S2A–S2D mantêm as regras críticas; views/forms/templates coletam intenção, validam estrutura, chamam services oficiais, apresentam preview/impacto e tratam conflitos/resultados.
- SavedFilter: auditar existência antes de propor schema; se ausente e necessário, criar apenas schema mínimo, documentando ownership, Workspace, context, schema version, payload fechado, unicidades e reversibilidade; sem backfill.
- Não reescrever fatos históricos ou projeções fora dos services oficiais; não chamar void de delete; não criar `QuestionRevision` ou `ReviewCycle` diretamente pela UI.
- Nenhuma etapa S4 ou posterior deve ser autorizada ou iniciada.

## Verification

- Executar testes focados definidos no A4 e regressão relacionada descrita nos critérios, incluindo prova razoável de que fluxos críticos passam pelos services oficiais e que GET não destrói.
- Executar gate autoritativo acima, A8 aplicável e registrar evidence S3 com baseline, A4, decisão de migration, SavedFilter, rotas, views/forms, integrações de services, categorias, Reviews, Attempts, correção de gabarito, exclusão permanente, stale state, Workspace, segurança, acessibilidade, performance, testes, A8 e gate.
- Registrar execução A7 separadamente; não estimar duração/cota. Se indisponível, registrar `unknown`.

## Documentation Impact

Criar plano A4 e evidence S3; atualizar `PROJECT_STATE.md`, métricas e contrato arquivado somente quando a conclusão efetiva estiver comprovada. Não replicar informação sem necessidade.

## Done When

- A4 concluído e decisão de migration justificada; SavedFilter funcional e isolado; fluxos de reagendamento, inclusão manual, categorias, void/replacement, correção de gabarito e exclusão permanente atendem critérios e usam os services oficiais sem bypass.
- Stale conflicts, Workspace, segurança HTTP, acessibilidade básica, empty/error states e performance estão cobertos; regressão S2A–S2D e gate GREEN; A8 aprovado e evidence persistida.
- Encerramento completo: atualizar estado/métricas, arquivar S3 e retornar `tasks/current.md` a `NO_TASK_AUTHORIZED`; S4+ permanecem não autorizadas. Nenhuma destas condições permite iniciar S4.

## Closure Evidence

- Plano A4: `tasks/plans/v05-s3-management-ui-plan.md`, `COMPLETED`.
- Evidência de implementação, A8 e gate: `quality/v05-s3-management-ui-result.md`.
- Migration: somente `search.0001_initial`; manifesto corrente
  `quality/v05-s3-migrations.json`; manifestos históricos preservados.
- Testes focados S3/migration: 14 passed; regressões afetadas: 7 passed.
- Gate autoritativo: GREEN, exit code 0, 423 passed, 87% de cobertura,
  tentativa aceita 3; A8 standard APPROVED, sem Blocker/Major/Minor aberto.
- Métricas A7 registradas em `quality/operational-execution-metrics.jsonl`;
  duração total e quotas indisponíveis, sem estimativa.
- `PROJECT_STATE.md` atualizado. `tasks/current.md` retornou a
  `NO_TASK_AUTHORIZED`; S4+ permanecem não autorizadas.
- Sem commit, push, tag, release ou funcionalidade posterior.