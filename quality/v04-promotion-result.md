# V0.4 — Evidência de promoção

- Data: 19 de setembro de 2026.
- Objetivo: promover o primeiro MVP local utilizável somente após piloto e
  controles objetivos.
- Base avaliada: branch `main`, commit inicial
  `03a6afd240efc485e9cb29c7f1f00e68c5008ba3`, acrescido apenas dos artefatos
  documentais S9 ainda não commitados.
- Decisão: **V0.4 PROMOTED**.

## Escopo entregue

S1 congelou a semântica; S2 implementou analytics read-only; S3 entregou o
dashboard; S4 entregou consulta/detalhe/timeline; S5 entregou o checker; S6
comprovou backup e recuperação; S7 consolidou operação Windows; S8 endureceu e
classificou o candidato; S9 executou o piloto protegido e a decisão final.

## Checklist oficial P0/S9

| Critério | Evidência | Resultado |
| --- | --- | --- |
| S1–S8 concluídas | contratos encerrados e `quality/v04-s8-candidate-result.md` | PASS |
| S9 concluída | plano, piloto, review, gate e arquivamento | PASS |
| Jornada contínua do MVP | cenários S9-P01–S9-P13 | PASS |
| Dashboard e drill-down reconciliáveis | S2/S3, cenários P02/P03/P08 | PASS |
| Zero distinto de ausência de dados | S1/S3 e P02 | PASS |
| Fuso e estados de revisão | S4 e P07 | PASS |
| Busca/filtros/paginação/Workspace | P03/P04/P09 | PASS |
| BCR-1 | três execuções S8 PASS; sem mudança invalidante | PASS |
| Backup/restore/RPO/RTO documentados | S6 e P11; restaurações pré e pós-piloto | PASS |
| S5 no candidato e cópias | 17 checks, zero findings, exit 0 | PASS |
| Acessibilidade essencial | evidência assistida S8, limitações preservadas | PASS |
| Operação Windows | S7 e P01/P12/P13 | PASS |
| Logs/dados sensíveis | evidências sanitizadas e gate `detect-secrets` | PASS |
| Suite, cobertura, migrations e análise estática | gate autoritativo S9 | PASS |
| Documentação e status | README, índice, Roadmap e `PROJECT_STATE.md` | PASS |
| Blocker/Major/P0/P1 abertos | review A8 final | PASS: zero abertos |

## Evidências integradas

- Piloto: `quality/v04-s9-pilot-result.md`.
- S5/S6/S7: checker exit 0; backups pré e pós-piloto validados e restaurados;
  operação loopback e persistência confirmadas.
- BCR-1: evidência S8 oficial preservada, sem repetição desnecessária.
- Acessibilidade: evidência S8 preservada; nenhuma superfície UI foi alterada.
- Defects: S9-F001 foi resolvido e revalidado; nenhum defect de produto ou
  finding Blocker/Major permanece aberto.
- Feedback humano subjetivo: `NOT OBSERVED`; não é gate obrigatório registrado.

## Gate, review e decisão

`git diff --check` terminou exit 0. O gate autoritativo ficou GREEN na primeira
passagem real, exit 0 em 124,3 s: 327 testes passaram em 77,91 s. Depois dos
registros de encerramento, a árvore final foi revalidada: exit 0 em 109,8 s,
327 testes em 76,53 s, cobertura global 88%, migrations `No changes detected`,
banco vazio, formatação, Ruff, mypy, cobertura de domínio, `detect-secrets` e
`pip-audit` aprovados. Nenhuma falha do gate ocorreu em S9.

O review A8 profundo examinou piloto, findings, retestes, backups, baseline,
checklist, documentação, diff final, ausência de schema/migration e fronteira
de escopo. Resultado: **APPROVED**, com Blocker 0, Major 0 e Minor 0 abertos.
S9-F001 foi Major durante o ensaio, mas está resolvido e integralmente
revalidado; os incidentes de PTY/harness não são defects de produto.

Todos os gates impeditivos estão satisfeitos. A decisão exata é:

**V0.4 PROMOTED**

Esta é uma promoção documental/de produto. Nenhum commit, push, tag ou GitHub
Release foi criado; a tag `v0.4.0` pode ser criada somente depois do checkpoint
humano. V0.5 permanece `NOT AUTHORIZED` e não foi iniciada.
