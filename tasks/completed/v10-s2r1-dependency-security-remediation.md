# Archived Task Contract — V1.0-S2R1

## Authorization

- Task ID: `V1.0-S2R1`
- Version: `V1.0`
- Stage: `S2R1` (return to S2 for a security finding discovered during S5)
- Status: `COMPLETED`
- Execution state: `COMPLETED`
- Type: `dependency security remediation`
- Size: `M`
- Risk: `high`
- Migration expected: `NO`
- Review A8: `standard`

## Goal

Remediate only the S5-F02 urllib3 dependency security finding through the smallest compatible, reproducible lockfile update, then verify with pip-audit and the full authoritative quality gate.

## Context

The preceding S5 contract is preserved byte-for-byte at `tasks/paused/v10-s5-performance-bcr.md`. S5 remains `AUTHORIZED / BLOCKED / RETOMÁVEL`, with BCR-1/BCR-2 and CT-105–112 evidence preserved and awaiting formal closure after this return-to-S2 task.

## Acceptance Criteria

- urllib3 2.7.0 is replaced by patched compatible 2.8.0 if the canonical resolver supports a lock-only change.
- All three recorded advisories are absent in post-fix pip-audit; no new known vulnerabilities are introduced.
- Dependency churn is limited to urllib3 and its required lock metadata; explain and stop on avoidable broader churn.
- Full `scripts/quality.ps1` gate is GREEN with exit code 0; migrations remain unchanged.
- A8 standard is APPROVED, Blocker 0 and Major 0 for this remediation.
- S5 historical FAIL and all raw evidence remain intact; S5 is not declared complete.
- S6–S10 remain NOT AUTHORIZED.

## Expected Scope

- `uv.lock`
- `tasks/current.md`
- `PROJECT_STATE.md`
- S5 result documentation appended with the remediation outcome, preserving earlier entries
- New S2R1 audit and result evidence as needed
- Archive this S2R1 contract and restore the preserved S5 contract after successful completion

## Protected Scope

- Product code, tests, migrations, BCR thresholds, datasets, CTs, and S5 benchmark artifacts
- The initial BCR-1 FAIL, profiling, final BCR-1 PASS, full BCR-2 PASS and CT-105–112 evidence
- No benchmark reruns absent concrete evidence the dependency affects the measured path

## Constraints

- No global dependency upgrade and no direct urllib3 pin unless technically necessary and justified.
- No commit, push, tag, or release.
- Synthetic/disposable benchmark data only; do not run benchmarks for this remediation.
- Migration expectation: `NO`.

## Verification

- Preserve pre-fix pip-audit result; run canonical uv lock and sync commands.
- Run equivalent post-fix pip-audit and verify all three advisories are fixed with no new findings.
- Run `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1`; require exit 0.
- Perform A8 standard review; finish with `git diff --check` and `git status --short`.

## Documentation Impact

Update `PROJECT_STATE.md`, preserve the S5 contract and history, append the S2R1 result to the S5 evidence report, and create a focused S2R1 result record.

## Done When

The patched dependency is locked and audited cleanly, the full gate is GREEN, A8 standard is APPROVED with no Blocker/Major, S2R1 is archived, and the authorized S5 contract is restored for a separate short formal resumption. Do not mark S5 complete.

---

## Human Authorization and Detailed Contract
# V1.0-S2R1 — REMEDIAÇÃO DE DEPENDÊNCIA DE SEGURANÇA
## urllib3 / gate RED encontrado durante V1.0-S5

Decisão humana explícita:

A V1.0-S5 encontrou um finding de segurança no gate final após concluir as
provas de desempenho.

A S5 deve permanecer preservada como:

`AUTHORIZED / BLOCKED / RETOMÁVEL`

Não apagar nem reexecutar sem necessidade:

- BCR-1 inicial FAIL;
- profiling;
- BCR-1 final PASS;
- BCR-2 completo;
- CT-105–112 PASS;
- artefatos raw;
- evidência de integridade.

O plano V1 determina que findings surgidos em S3–S6 retornem a S2 sob contrato
próprio.

Esta mensagem autoriza exclusivamente:

`V1.0-S2R1 — dependency security remediation`

---

# 1. FINDING A REMEDIAR

O gate final S5 encontrou vulnerabilidades em:

`urllib3 2.7.0`

Advisories observados:

- GHSA-8988-9cw3-xx77
- GHSA-gh4c-6fx4-qh6g
- GHSA-vxq7-64xx-v4gw

O upstream possui versão corrigida:

`urllib3 2.8.0`

Não alterar findings históricos.

---

# 2. ESCOPO

Objetivo:

remediar SOMENTE o finding de dependência `S5-F02` de forma mínima e
reproduzível.

Antes de alterar:

1. ler `AGENTS.md`;
2. ler `PROJECT_STATE.md`;
3. ler `tasks/current.md`;
4. ler o plano V1 relevante;
5. inspecionar:
   - `pyproject.toml`
   - `uv.lock`
   - scripts do quality gate
   - resultado bruto do pip-audit S5.

Confirmar a cadeia que introduz `urllib3`.

Não presumir que `urllib3` é dependência direta se não for.

---

# 3. ESTADO DOCUMENTAL

Atualizar de forma coerente:

`tasks/current.md`

e

`PROJECT_STATE.md`

para representar:

- S1–S4 concluídas;
- S5 com provas de desempenho concluídas, porém BLOCKED pelo finding S5-F02;
- V1.0-S2R1 = AUTHORIZED / IN EXECUTION;
- S6+ = NOT AUTHORIZED.

Preservar toda a rastreabilidade da S5.

Não declarar S5 concluída ainda.

---

# 4. REMEDIAÇÃO MÍNIMA

Preferir a menor mudança possível.

Como primeira hipótese, verificar se é possível atualizar somente o lock de:

`urllib3 2.7.0 → 2.8.0`

ou outra versão patched compatível estritamente necessária.

Preferir:

`2.8.0`

se ela resolver os advisories e for compatível, para minimizar churn.

Usar o fluxo `uv` canônico do projeto.

Uma possibilidade a verificar é:

`uv lock --upgrade-package urllib3`

Mas NÃO executar cegamente.

Primeiro confirmar a compatibilidade e depois inspecionar o diff.

---

# 5. CONTROLE DE CHURN

Após regenerar/atualizar o lock:

inspecionar exatamente quais pacotes mudaram.

Resultado ideal:

- apenas `urllib3`;
- hashes correspondentes;
- nenhuma alteração não relacionada.

Se outros pacotes forem atualizados:

não aceitar automaticamente.

Determinar por que mudaram.

Se o resolver produzir churn amplo e evitável:

PARAR e buscar a forma mínima compatível.

Não atualizar dependências em massa.

Não executar `uv lock --upgrade` global.

---

# 6. PYPROJECT

Não adicionar um pin direto de `urllib3` ao `pyproject.toml` apenas para forçar
o resolver, salvo necessidade técnica comprovada.

Se `urllib3` continuar sendo dependência transitiva e o lock puder ser atualizado
com segurança:

preferir alteração somente no `uv.lock`.

Se for necessária mudança em `pyproject.toml`, explicar primeiro a razão.

---

# 7. TESTES DE SEGURANÇA

Depois da atualização:

sincronizar o ambiente pelo fluxo canônico.

Executar a auditoria equivalente à usada pelo gate.

Confirmar:

- GHSA-8988-9cw3-xx77: resolvido;
- GHSA-gh4c-6fx4-qh6g: resolvido;
- GHSA-vxq7-64xx-v4gw: resolvido;
- nenhuma nova vulnerabilidade conhecida introduzida.

Preservar evidência da auditoria anterior e da nova.

---

# 8. TESTES FUNCIONAIS

Executar testes focados somente se necessários pela mudança de dependência.

Depois executar o gate autoritativo completo:

`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1`

Exigir:

- GREEN;
- exit code 0;
- testes PASS;
- coverage preservada;
- pip-audit limpo;
- nenhuma migration inesperada.

---

# 9. PERFORMANCE

Esta remediação NÃO autoriza refazer tuning ou alterar performance.

Não reexecutar BCR-1/BCR-2 nesta tarefa, salvo se houver evidência concreta de
que a mudança de dependência afeta o caminho medido.

Como `urllib3` é uma dependência de networking/tooling, verificar primeiro se
ela participa ou não dos fluxos BCR.

Se não participa:

documentar que BCR não foi afetado e não repetir benchmark.

Se participa de forma material:

PARAR e reportar antes de repetir prova extensa.

---

# 10. MIGRATION / CÓDIGO

Migration expectation:

`NO`

Não criar migration.

Não alterar código de produto salvo incompatibilidade concreta provocada pela
atualização.

Se houver incompatibilidade material:

retornar:

`HUMAN_DECISION_REQUIRED`

---

# 11. A8

Executar A8 standard da remediação.

Revisar:

- finding original;
- versão vulnerável;
- versão corrigida;
- cadeia transitiva;
- diff do lock;
- ausência de churn não relacionado;
- auditoria pós-fix;
- gate;
- ausência de regressão;
- ausência de migration;
- impacto ou não em BCR.

Resultado necessário:

`APPROVED`

---

# 12. FECHAMENTO S2R1

Se:

- advisories resolvidos;
- gate GREEN;
- pip-audit limpo;
- testes PASS;
- nenhuma regressão;
- A8 APPROVED;
- Blocker = 0;
- Major aberto desta remediação = 0;

então declarar:

`S2R1_COMPLETED`

Arquivar o contrato de remediação conforme convenção do projeto.

Depois restaurar a autoridade de execução para a retomada da S5, mantendo:

- BCR-1 final PASS;
- BCR-2 completo/PASS;
- CT-105–112 PASS;
- S5-F02 resolvido;
- S5 ainda aguardando seu fechamento formal;
- S6+ NOT AUTHORIZED.

Não declarar S5_COMPLETED dentro da remediação, salvo se o plano autoritativo
explicitamente permitir; preferir uma retomada curta da S5 para gate/A8 final.

---

# 13. GIT

NÃO executar:

- git add;
- commit;
- push;
- tag;
- release.

Checkpoint virá depois.

Ao final:

`git diff --check`

`git status --short`

---

# 14. RELATÓRIO

Reportar:

1. versão urllib3 antes;
2. versão depois;
3. cadeia que introduz urllib3;
4. arquivos alterados;
5. diff de dependências;
6. outros pacotes alterados, se houver;
7. motivo de cada alteração adicional;
8. auditoria antes;
9. auditoria depois;
10. advisories resolvidos;
11. novas vulnerabilidades;
12. testes;
13. coverage;
14. gate;
15. A8;
16. Blocker/Major/Minor;
17. migrations;
18. impacto em BCR;
19. PROJECT_STATE;
20. tasks/current;
21. S5 preservada;
22. S6+ NOT AUTHORIZED;
23. nenhum commit/push/tag/release;
24. decisão final:

`S2R1_COMPLETED`

ou

`BLOCKED`

ou

`HUMAN_DECISION_REQUIRED`

Depois PARAR.
## Closure — 2026-09-30

Decision: `S2R1_COMPLETED`. urllib3 2.7.0 was updated to 2.8.0 in uv.lock
only; post-fix pip-audit and the full quality gate passed. Gate: exit 0, 512
passed, 86.4013% coverage, 317.6 s; no migration changes. A8 standard:
APPROVED, Blocker 0 / Major 0 / Minor 0. Detailed evidence:
`quality/v10-s2r1-dependency-remediation-result.md`.

S5 remains authorized and awaits its separate formal closure. No S5 benchmark
was rerun; all earlier S5 evidence, including the initial BCR-1 FAIL, remains
preserved. S6–S10 remain NOT AUTHORIZED. No commit, push, tag, or release.