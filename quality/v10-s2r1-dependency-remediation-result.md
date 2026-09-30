# V1.0-S2R1 — Resultado da remediação de dependência

**Decisão:** `S2R1_COMPLETED`
**A8 standard:** `APPROVED` — Blocker 0 / Major 0 / Minor 0
**Migration expectation:** `NO`

## Finding e cadeia transitiva

O gate da S5 encontrou três advisories em urllib3 2.7.0: CVE-2026-97687 /
GHSA-8988-9cw3-xx77, CVE-2026-97688 / GHSA-gh4c-6fx4-qh6g e CVE-2026-97689 /
GHSA-vxq7-64xx-v4gw. A auditoria original está preservada em
`quality/v10-s5-pip-audit-result.json`.

`urllib3` não é dependência direta. A árvore uv é `requests 2.34.2 → urllib3`.
`requests` chega pelo grupo dev através de `pip-audit 2.10.1`, `detect-secrets
1.5.0` e `cachecontrol 0.14.4 → pip-audit[filecache]`. Nenhum import Python de
`requests`/`urllib3` foi encontrado no produto, testes ou harness BCR.

Requests 2.34.2 declara `urllib3 >=1.26,<3`; urllib3 2.8.0 requer Python >=3.10.
O runtime travado do projeto é Python 3.13.15. Portanto a versão corrigida é
compatível com o range transitivo e o runtime ([metadata PyPI de Requests
2.34.2](https://pypi.org/pypi/requests/2.34.2/json), [urllib3 2.8.0 no
PyPI](https://pypi.org/project/urllib3/2.8.0/)).

## Alteração mínima e churn

Fluxo canônico: `uv lock --upgrade-package urllib3`, seguido de `uv sync
--locked`. O diff de dependência altera somente a entrada `urllib3` em
`uv.lock`, de 2.7.0 para 2.8.0, incluindo URLs, hashes e metadados de tamanho/
data da sdist e wheel. O hash SHA-256 da wheel travada é
`0cf3cae568d36aa9576b28dfb35f11328f1cb974ca7647d9475ebb86c75ac6e3`; o da
sdist é `63bf2ead4c879426ebf22ef2a781eeb4aa3b4ae798a0435506f8687fd5bb9b63`.
O grafo e todos os outros 53 pacotes permaneceram iguais. `pyproject.toml` não
foi alterado e não foi adicionado pin direto.

## Auditoria de segurança

| Evidência | Resultado |
| --- | --- |
| Antes — `quality/v10-s5-pip-audit-result.json` | urllib3 2.7.0; os três advisories acima; fix indicado 2.8.0 |
| Depois — `quality/v10-s2r1-pip-audit-result.json` | urllib3 2.8.0; todas as dependências com `vulns: []`; `fixes: []` |
| Gate final | `No known vulnerabilities found` |

Os três advisories foram resolvidos; nenhum finding conhecido novo foi
introduzido. O relatório original S5 permanece intacto.

## Gate e migrations

Comando: `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1`.

- Gate `GREEN`, exit code 0; duração total reportada 317.6 s.
- 512 testes passaram em 238.07 s.
- Cobertura total: 86.4013267% (86% exibido); validação de cobertura de domínio PASS.
- Lock e sync PASS; runtime Python 3.13.15, Django 5.2.17 e SQLite 3.53.1.
- Perfis Django PASS; `makemigrations --check --dry-run`: `No changes detected`.
- Banco vazio/migrations, formato (407 arquivos), Ruff, mypy (195 arquivos),
  testes, cobertura, detect-secrets e pip-audit PASS.
- Nenhuma migration foi criada; código e testes de produto não foram alterados
  por S2R1.

## Revisão A8 standard

A8 `APPROVED`. Revistos: autorização restrita a S2R1; relatório pré-fix; cadeia
transitiva; compatibilidade Requests/Python; diff restrito a urllib3; hashes do
lock; auditoria pós-fix; gate integral; regressão funcional; migrations; impacto
BCR e fronteiras de escopo. Resultado: Blocker 0 / Major 0 / Minor 0 para S2R1.

A atualização afeta uma dependência de tooling/dev; não há import no caminho de
produto ou no harness BCR. BCR-1/BCR-2 não foram repetidos, pois não há evidência
concreta de impacto no caminho medido. O BCR-1 inicial FAIL, o BCR-1 final PASS,
o BCR-2 completo PASS, CT-105–112 e todos os JSONs/raw S5 foram preservados.
S5-F02 está resolvido; S5 continua aguardando fechamento formal separado e não
foi declarada `S5_COMPLETED`.

## Estado final e arquivos

S1–S4 concluídas. S2R1 concluída e arquivada em
`tasks/completed/v10-s2r1-dependency-security-remediation.md`. A autoridade foi
restaurada para S5 em `tasks/current.md` como `AUTHORIZED / IN EXECUTION /
AWAITING FORMAL CLOSURE`; a cópia exata do contrato S5 anterior à remediação
está em `tasks/paused/v10-s5-performance-bcr.md`. `PROJECT_STATE.md` registra
S2R1 concluída e S5 retomada, sem marcar S5 concluída. S6–S10 permanecem
`NOT AUTHORIZED`.

Arquivos S2R1 alterados/criados: `uv.lock`, `tasks/current.md`,
`tasks/paused/v10-s5-performance-bcr.md`, `tasks/completed/v10-s2r1-dependency-security-remediation.md`,
`PROJECT_STATE.md`, este relatório, `quality/v10-s2r1-pip-audit-result.json` e
`quality/v10-s5-performance-bcr-result.md` (somente esta seção foi anexada).
Os arquivos funcionais/testes e a evidência bruta anterior da S5 foram
preservados.

Nenhum benchmark foi executado. Nenhum commit, push, tag ou release foi feito.
Não houve início de S6 ou etapa futura.