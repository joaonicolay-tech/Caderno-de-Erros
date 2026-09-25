# Task Contract

Status: AUTHORIZED

## Identification

- Task ID: `V0.5-S7`
- Product version: `V0.5`
- Stage: `S7`
- Name: `CEI-EXPORT-1.0, UI de backup/restore e staging seguro`
- Task type: portabilidade, exportação funcional, backup/restore operacional e UI segura
- Size: `L`
- Risk: `high`
- Migration: `UNLIKELY`; auditar schema no A4. Não criar migration sem necessidade comprovada; se necessária, justificar antes da criação.
- A4: plano completo obrigatório antes da primeira edição funcional
- A8: `deep`, aprovação com Blocker 0 e Major 0
- A7 recomendado para a execução: GPT-6 Sol / `High`; não estimar consumo

## Goal

Implementar S7 para exportar dados funcionais em formato aberto e versionado `CEI-EXPORT-1.0`, e oferecer fluxos seguros de backup e restore pela UI, com validação em staging antes de mutação, proteção contra falha parcial, reconciliação verificável e preservação do histórico e isolamento por Workspace.

## Context

- Baseline confirmada no bootstrap: branch `main`; `HEAD` e `origin/main` em `461e2bd1f1abe7321726d30e7e5e47737faa6be2`, commit `feat(v0.5): complete S6 priority heuristic`; working tree limpa; `git diff --check` passou.
- V0.5-P0, S1/OD05, S2A–S2D e S6 estão concluídas; evidências S6: `tasks/completed/v05-s6-priority-heuristic.md` e `quality/v05-s6-priority-heuristic-result.md`. S4/S5 também estão concluídas.
- S7 é a única tarefa autorizada. S8, S9, S10, V1 e posteriores permanecem não autorizadas.
- `V05-OD05 = OPEN / MANDATORY_IN_S7_A4`. O bootstrap identifica `CEI-EXPORT-1.0`, sem escolher schema ou formato final.
- Manter distintos: exportação funcional aberta, snapshot de backup operacional e restauração operacional compatível. Restore não é importação genérica.
- Antes de implementação funcional, criar e fechar A4 em `tasks/plans/`, auditar as fontes/código/modelos/migrations/testes/formats existentes e resolver OD05 com respaldo. Se persistir escolha normativa sem respaldo, registrar `BLOCKED_HUMAN_DECISION` e parar a parte dependente antes de implementar.

## Acceptance Criteria

- Definir e documentar `CEI-EXPORT-1.0` como formato aberto, documentado, UTF-8 e independente do banco interno, com schema, versão, data de geração, manifesto/checksums, relações, semântica de IDs e dados incluídos/excluídos definidos no A4 a partir das fontes aprovadas.
- Resolver `V05-OD05` no A4 com fontes e decisão rastreáveis; não inventar defaults. Auditar especificamente schema, manifesto, checksums, versionamento, importabilidade, relações, fatos autoritativos/derivados, pacote/arquivos, Workspace e round-trip.
- Implementar exportação funcional reutilizável que inclua dados relevantes e histórico conforme fontes, permita reconciliação, não altere a base e exclua segredos técnicos, credenciais, tokens e paths/variáveis internos sensíveis.
- Implementar backup operacional e restore seguro pela UI, reutilizando mecanismos existentes de backup SQLite, validação, restore isolado e checker/reconciliação quando aplicável; sem confundir esses fluxos com exportação funcional.
- Usar staging temporário e validar formato, versão, integridade/checksums, conteúdo, segurança de arquivos e pertencimento aplicável antes de qualquer mutação/substituição; rejeitar formatos incompatíveis, versões futuras/desconhecidas, corrupção e pertencimento inválido sem alterar dados.
- Apresentar impacto e resultado verificável/reconciliável, exigir confirmação reforçada e criar pré-backup antes de restore de destino existente. Falha não pode deixar mistura parcial; manter estado consistente ou executar retorno aprovado.
- Cobrir round-trip autorizado: exportar conjunto conhecido, importar/restaurar em ambiente/espaço vazio autorizado, reexportar e comparar equivalência semântica. Isso não autoriza overwrite arbitrário.
- Preservar histórico e semânticas S2A–S2D: auditoria funcional, categorias pessoais, Attempt void/replacement, correção prospectiva de gabarito, exclusão permanente e retenção sanitizada; nunca reconstruir fatos anulados como válidos nem reinterpretar histórico.
- No A4 classificar entidades/fatos autoritativos, projeções, caches, derivados, eventos, configurações e dados recalculáveis, incluindo o tratamento de Domain/Priority S4–S6; não exportar indiscriminadamente o banco nem excluir fatos históricos necessários.
- Manter o integrity checker read-only; S7 não antecipa o hardening adicional de integridade/compatibilidade de S8.
- UI mínima acessível: labels claros, teclado/foco, erros compreensíveis, confirmação explícita, estado/progresso quando aplicável e informação que não dependa só de cor; sem redesign geral.
- Migration decidida por auditoria; nenhuma migration artificial. A8 `deep` aprovado com Blocker 0/Major 0, verificações focadas/regressões e gate autoritativo GREEN; persistir evidências finais, incluindo resultado de portabilidade/recovery.

## Expected Scope

- Plano A4 completo em `tasks/plans/` antes de alterações funcionais.
- Mudanças mínimas necessárias em serviços de exportação/backup/restore, staging/validação, UI, documentação de `CEI-EXPORT-1.0` e testes diretamente relacionados, conforme A4.
- Reutilizar serviços e comandos existentes quando aplicável; qualquer necessidade de schema deve ser justificada no A4.
- Evidence final específica, por exemplo `quality/v05-s7-portability-result.md`; atualizar `PROJECT_STATE.md` e arquivar contrato apenas após evidência de encerramento.

## Protected Scope

- Sem redesign geral, API pública ou importação universal de terceiros.
- Não criar importação genérica de Excel/CSV, bancos externos, OCR ou importação massiva de terceiros.
- Não fazer overwrite implícito/arbitrário; não alterar o integrity checker para reparar estado.
- Não alterar semântica de fatos históricos S2A–S2D ou regras aprovadas fora do escopo; não exportar segredos.
- Não antecipar S8, S9, S10 ou V1.
- Não fazer commit, push, tag ou release sem autorização explícita posterior.

## Constraints

- Antes de qualquer edição funcional, fechar A4 auditando RF-069–072, RNF-034–043, CT-113–120, OD05, RNF-ABR-006, backup/restore e validators existentes, integrity checker, modelos S2A–S2D, derivados S4–S6, Workspace, filesystem/temp files, Windows, segurança, UI, testes e documentação de formato.
- OD05 permanece bloqueador de escolhas de formato até resolução sustentada. Se as fontes não resolverem uma escolha normativa, usar `BLOCKED_HUMAN_DECISION` antes de implementação dependente.
- Auditar path traversal, nomes/arquivos inesperados, tamanho/conteúdo/checksum, segurança ZIP se aplicável, staging, cleanup, falha parcial, memória/streaming, tempo, escrita temporária, recovery e retorno. Decisões técnicas devem seguir evidência e fontes; não definir budgets arbitrários sem base.
- O A4 deve decidir semântica de pertencimento/Workspace e de IDs: preservar, remapear ou validar apenas com respaldo. Auditar classificação de dados e reconciliação sem inventar listas fora das fontes.
- Pré-backup ou estratégia equivalente aprovada é obrigatório para restore sobre destino existente. CT-117 deve provar ausência de mistura parcial; CT-118 leitura UTF-8/versionamento/data/relações/totais por ferramenta independente; CT-119 round-trip semântico em ambiente vazio autorizado; CT-120 rejeição de versão futura/desconhecida/formato incompatível antes de mutação.
- Não executar ações de S8+ nem operações externas de publicação.

## Verification

- No início da execução, confirmar baseline Git e dependências concluídas; observar resultados, sem presumir.
- Completar A4 e decisão OD05 antes de código funcional; executar testes focados para exportação independente/reconciliação, Workspace/pertencimento, segurança de arquivos/staging/cleanup, validações pré-mutação, falha/retorno sem mistura, pré-backup, UI/acessibilidade e CT-117–120.
- Executar regressões aplicáveis, A8 deep e `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1`; registrar tentativas/exit codes e evidências. Não declarar GREEN sem exit 0 observado.

## Documentation Impact

Documentar `CEI-EXPORT-1.0` para leitor independente e atualizar documentação operacional da UI/export/backup/restore e recovery conforme comportamento implementado. Registrar A4, decisões e evidence; atualizar `PROJECT_STATE.md` no encerramento.

## Done When

- A4 completo antes das edições funcionais, OD05 resolvido com respaldo ou decisão humana documentada, e decisão de migration justificada.
- Exportação funcional aberta/versionada documentada e reconciliável, separada de backup operacional e restore.
- Backup/restore pela UI implementados com staging, validação anterior à mutação, confirmação reforçada, pré-backup/retorno aprovado e relatório verificável; entradas incompatíveis/corrompidas/inválidas não alteram dados e falhas não deixam mistura parcial.
- Segurança de arquivos, isolamento Workspace, histórico S2A–S2D, derivados, segredos, cleanup, acessibilidade e CT-117–120 verificados por evidência adequada.
- Testes/regressões focados aprovados, A8 deep `APPROVED` com Blocker 0/Major 0 e gate final GREEN com exit 0 observado; evidence concluída.
- `PROJECT_STATE.md` atualizado, tarefa arquivada em `tasks/completed/` e `tasks/current.md` retorna a `NO_TASK_AUTHORIZED`; nenhuma etapa S8+ iniciada ou autorizada.

## Closure evidence

- S7 concluída em 2026-09-25. A4 fechado em `tasks/plans/v05-s7-portability-plan.md`; OD05 resolvido por decisão humana nova; Migration: NO.
- A8 deep APPROVED, Blocker 0, Major 0. Gate final GREEN, exit 0, 498 passed, 86% de cobertura e pip-audit sem vulnerabilidades conhecidas. Evidência: `quality/v05-s7-portability-result.md`.
- Nenhuma etapa S8+ iniciada ou autorizada; sem commit, push, tag ou release.
