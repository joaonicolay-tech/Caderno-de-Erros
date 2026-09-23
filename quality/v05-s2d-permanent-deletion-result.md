# V0.5-S2D — exclusão permanente por agregado

## Autoridade e escopo

- Contrato executado: `tasks/current.md`, `V0.5-S2D`, `AUTHORIZED`.
- Plano A4: `tasks/plans/v05-s2d-permanent-deletion-plan.md`; decisões humanas em
  `quality/v05-s2d-human-decision-gate.md`.
- S3 e etapas posteriores não foram autorizadas nem iniciadas.

## Implementação e integridade

- Preview Workspace-scoped e sem escrita calcula elegibilidade, bloqueios,
  impacto, backup exigido, confirmação e fingerprint do estado completo. DRAFT
  sem histórico ou dependência relevante tem dispensa objetiva do backup;
  histórico exige S6 criado, validado e restaurado isoladamente com S5 aprovado.
- Delete revalida o grafo e a confirmação, executa CAS da Question e remove em
  transação durável as revisões, alternativas, Attempts e cadeias S2B,
  classifications/revisions, ciclos/Reviews/reagendamentos, origens, eventos
  antigos diretamente vinculados e recibos elegíveis. Categorias e taxonomia
  compartilhadas sobrevivem. Contagens, FKs e projeções derivadas são
  reconciliadas antes do commit; falha reverte tudo.
- `OperationReceipt` bloqueia antes de `created_at + 30 dias` e enquanto houver
  contexto transitório local válido. No limite de 30 dias, sem contexto, é
  removido junto com a Attempt. A remoção de AuditEvents antigos e recibos usa
  exceção interna e exclusiva à imutabilidade desses fatos para a exclusão S2D.
- O evento final é confirmado na mesma transação e guarda apenas ID técnico do
  evento, `workspace_id`, código, instante, correlação técnica independente,
  tipo de entidade e motivo codificado. Não guarda ID da Question ou de outro
  nó removido, texto, resposta, payload ou metadados de revisão. IDs do agregado
  são rejeitados também na correlação e no motivo.
- O comando manual `purge_question_deletion_audit` remove apenas eventos finais
  sanitizados em `created_at + 90 × 24 horas` UTC ou depois, inclusive no
  instante exato. É seletivo e idempotente; não há scheduler.
- Migration `operations.0004` é mínima e sem backfill; manifesto suplementar
  `quality/v05-s2d-migrations.json` protege seu hash sem alterar manifests
  anteriores. Reverse é seguro somente antes de fatos S2D; após delete, recovery
  usa backup compatível pré-exclusão, não reverse da migration.

## Provas

- `tests/test_v05_s2d.py`: 20 casos passaram, incluindo preview, limites de 30
  e 90 dias, sanitização, sete pontos de fault injection, dois deletes,
  interleavings de Attempt/S2B/S2C/Review, grafo R1/R2/R3, categorias
  compartilhadas, analytics, checker e S6 pré e pós-delete.
- `tests/test_v05_s2d_upgrade.py`: upgrade isolado V0.4.4-equivalent → S2A →
  S2B → S2C → S2D, fatos preservados, delete, recovery, `integrity_check`,
  `foreign_key_check` e checker S5: passou.
- Regressão de manifesto e restore S2C sob o schema atual: 21 testes focados
  passaram. `git diff --check`: passou.

## Review A8 deep

**APPROVED**; Blocker 0, Major 0, Minor 0 abertos. A revisão cobriu escopo,
grafo/FKs, perda de dados, sanitização, retenção, Workspace, concorrência,
atomicidade, backup/restore, migration, idempotência, checker read-only,
analytics e ausência de S3+.

Findings resolvidos antes da aprovação:

- [Major] O fingerprint inicial excluía conteúdo e timestamps; passou a cobrir
  todas as colunas do grafo. Teste prova rejeição de edição sem incremento de
  versão entre preview e confirmação.
- [Major] Correlação ou motivo fornecidos pelo chamador poderiam conter ID do
  agregado; a confirmação agora rejeita ambos e o teste prova a barreira.
- [Major] Faltava prova do limite de 30 dias do recibo; teste cobre o
  microssegundo anterior e o instante exato.

## Gate autoritativo

`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1`

- Passagem aceita: **GREEN**, exit code **0**, total **226,8 s**, 23/09/2026.
- **409 passed** em 182,52 s; cobertura global **87%**, mínimos de domínio
  aprovados. Dois `ResourceWarning` no teste histórico de origem não bloquearam
  o gate.
- Lock, três perfis, migration em banco vazio, `makemigrations --check`,
  rastreabilidade, formatação, Ruff, mypy, detect-secrets e pip-audit passaram;
  `pip-audit`: `No known vulnerabilities found`.
- Primeiro gate RED por formatação da migration; segundo por anotações mypy dos
  testes; terceiro por testes de manifesto/restore S2C ainda ligados ao schema
  anterior. Foram corrigidos no escopo. Três execuções posteriores foram
  interrompidas por novas correções A8 antes do gate final; nenhuma delas foi
  tratada como GREEN. `gate_first_pass: false`, tentativa aceita: 7.

Não houve operação de exclusão em banco de produção, commit, push, tag,
release ou início de S3.
