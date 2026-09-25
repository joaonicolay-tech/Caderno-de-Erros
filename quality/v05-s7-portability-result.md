# V0.5-S7 — resultado de portabilidade e recuperação

## Baseline, A4 e decisão

- Baseline inicial em 2026-09-25: `main`, `HEAD = origin/main = 461e2bd1f1abe7321726d30e7e5e47737faa6be2`; somente `tasks/current.md` estava modificado. O contrato S7 era `AUTHORIZED`. Não houve commit, push, tag ou release.
- Modelo recomendado no contrato: GPT-6 Sol / High. Variante e nível efetivos, quotas e duração total da sessão não possuem telemetria observável: `unknown`. Tempos de gate e benchmark abaixo foram medidos.
- A4 em `tasks/plans/v05-s7-portability-plan.md` foi criado antes da primeira edição funcional e fechado após a nova decisão humana de S7. `V05-OD05 = RESOLVED` por esse adendo, sem atribuir escolhas novas às fontes históricas. Auditoria do schema atual e `makemigrations --check --dry-run` indicaram `Migration: NO`; não há migration nova.

## Implementação, formatos e reconciliação

- `CEI-EXPORT-1.0` é ZIP com manifesto, README e 21 conjuntos JSON UTF-8. O documento `docs/CEI_EXPORT_1_0.md` define schema, campos, nullability, enums, relações, UUIDs, datas civis, instantes UTC, decimais, ausências, versão e exclusões. O manifesto contém versão de aplicação/migrations, Workspace, políticas, contagens, tamanhos e SHA-256 de cada payload. O leitor independente dos testes usa apenas ZIP/JSON da biblioteca padrão.
- A exportação lê um Workspace local autorizado, conserva fatos S2A–S2D e S5, inclusive VOIDED/replacement, revisões prospectivas, filtros e auditoria sanitizada. A exclusão permanente não reaparece: teste específico comprova ausência de Question, UUID e conteúdo eliminados apesar do evento final. Domain/Priority correntes, recibos técnicos, caches, sessões, credenciais e logs não são exportados; os fatos e códigos de policy permanecem para recálculo.
- O validator recusa formato/versão/migrations/policies incompatíveis, checksums/tamanhos/contagens divergentes, membros ZIP extras/duplicados/paths, tipos, UUIDs, relações, escopo e payload de filtro salvo malformado antes de escrever. A importação aceita apenas instalação SQLite compatível sem Workspace, preserva IDs, vincula owner ao usuário local, usa transação, confere FKs e checker read-only e recusa merge/remapeamento. O round-trip reexportado conservou fatos e relações semanticamente.
- `/dados/` oferece export funcional, backup operacional SQLite com manifesto em ZIP de transporte, preview de restore isolado com contagens atual/backup, confirmação por checkbox e `RESTAURAR`, ticket e pré-backup validado. A adoção ocorre somente em comando offline com servidor parado, revalidação e relatório JSON persistido; falha após troca tenta retorno ao pré-backup. Cancelamento remove staging pendente, candidato e pré-backup antes da adoção. GET e preview preservam o banco ativo. UI usa POST/CSRF, labels, mensagens textuais, navegação por controles nativos e link existente de salto ao conteúdo. Não houve observação em navegador assistivo/zoom; a evidência de acessibilidade é de markup e testes de interface.
- Testes de recovery usaram cópia isolada: adulteração do candidato foi recusada sem alterar destino; falha injetada após a troca retornou o hash do pré-backup; sucesso gerou `RESTORED`, hashes, contagens e relatório. Sem overwrite do banco aberto nem alteração do checker S5. Procedimento Windows e operação estão em `docs/V0.5_S7_Portabilidade_e_Restore.md`.

## Testes e performance

- Focados: leitor independente/CT-118, round-trip/CT-119, versão desconhecida/CT-120, checksum/path/payload, histórico S2B/S2C/S2D/S5, UI/CSRF/cancelamento, CT-117 e falha/retorno; **7 testes de portabilidade e 4 de UI passaram** na revisão final. Regressões completas de backup/restore, operations, S2A–S2D, Questions, Attempts, Reviews, taxonomy, S5, S6, interface e upgrades estão no gate de 498 testes.
- Medição proporcional em Windows, Python 3.13.15/Django 5.2.17/SQLite 3.53.1, banco de teste isolado: 50 Questions ativas, 50 revisões, 100 alternativas, 50 ciclos, 50 Reviews e 10 categorias; ZIP 27.251 bytes. Exportação 0,070 s, validação 0,056 s, importação 0,037 s, reexportação 0,055 s; equivalência semântica `true`. São tempos de uma única execução, sem promessa de escala. O processo da medição emitiu aviso de limpeza do SQLite temporário no encerramento Windows após imprimir o resultado; não afetou a equivalência nem o gate.

## A8 deep

- Revisados OD05, schema/manifesto/checksums/versões, reader aberto, fatos autoritativos e derivados, Workspace, staging/paths, exclusão de credenciais, pré-backup, confirmação, limite de mutação, retorno, round-trip, S2A–S2D/S5/S6, UI, Windows, migration e fronteira S8+.
- Findings corrigidos: expectativa exata de links de navegação omitia `/dados/`; validação estrutural do payload de SavedFilter foi reforçada e coberta com ZIP adulterado e SHA-256 recalculado. Varredura de segredos sinalizou palavra documental no A4; redação esclarecida e varredura repetida. Sem P0/P1 aplicável aberto.
- **APPROVED** após correções: Blocker 0, Major 0. Ressalvas menores registradas: dois `ResourceWarning` de conexões SQLite em testes existentes e ausência de ensaio visual assistivo; não impediram o gate.

## Gate autoritativo

Comando em todas as tentativas: `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1`.

1. RED, exit 1: 495 passed, 1 failed, por expectativa de navegação sem `/dados/`; rota acrescentada ao teste.
2. RED, exit 1: 496 passed; varredura de segredos sinalizou falso positivo em frase do A4; redação corrigida.
3. GREEN, exit 0: 497 passed, 86% de cobertura; `pip-audit` sem vulnerabilidades conhecidas; duração 275,6 s. Após A8, adicionada validação estrutural de SavedFilter.
4. **Final GREEN, exit 0**: 498 passed em 241,92 s, cobertura global 86%, meta de domínio aprovada, perfis/migrações/banco vazio, Ruff, mypy (192 arquivos), detect-secrets e `pip-audit` aprovados; `No known vulnerabilities found`. Duração total do gate: **293 s**. Dois `ResourceWarning` de SQLite, sem falhas.

`gate_first_pass=false`. `git diff --check` aprovado. S7 é a única etapa executada; S8+ continuam não autorizadas. Sem commit, push, tag ou release.
