# V0.4-S8 — Candidate readiness

- Data: 17 de setembro de 2026.
- Estado final: **READY_FOR_PILOT**.
- Review A8 profundo: **APPROVED**, sem Blocker, Major ou Minor aberto.
- S9/piloto: não autorizado e não executado.

## Evidência integrada

- Baseline focada antes das correções: 90 testes passaram em 18,20 s.
- Regressão focada final: 127 testes passaram em 26,21 s; o subconjunto final
  após review passou 21 testes em 4,23 s e os 8 testes BCR passaram em 2,75 s.
- Migrations: `makemigrations --check --dry-run`, exit 0, `No changes detected`.
- BCR-1 oficial: três execuções `PASS`; gravações abaixo de 2 s, telas/buscas
  abaixo dos thresholds existentes, novas leituras apenas `OBSERVED`, query
  counts constantes e paginação completa sem duplicação ou omissão.
- S5 no candidato BCR: exit 0, `HEALTHY`, 17 checks, 0 findings e 18 queries em
  conexão SQLite `mode=ro`.
- S6: `quality/v04-s8-recovery-result.json` registra backup, validação, restore
  isolado, abertura/reconciliação da aplicação, checks físicos, foreign keys 0,
  S5 exit 0 e hashes preservados; resultado `PASS`. O ensaio foi sintético e
  não constitui RTO/SLA nem validação humana.
- S7: startup pelo entry point a partir de diretório externo, HTTP 200 somente
  em loopback, shutdown por Ctrl+C e porta 8128 sem listener/processo órfão.
  No candidato BCR, `backup_sqlite` e `validate_backup` retornaram exit 0 sobre
  snapshot de 210.259.968 bytes com manifesto.
- Segurança: isolamento por `Workspace` permaneceu nos caminhos de leitura;
  CSRF, escaping, logs sanitizados, paths e secrets foram cobertos por regressão
  e gate. Nenhum dado pessoal real foi usado.
- Acessibilidade: teclado/foco, semântica, nomes de tabelas, navegação de
  retorno, contraste, 360 px e reflow equivalente a 200% foram revalidados. As
  limitações de browser, zoom nativo e leitor de tela constam no artefato
  específico, sem alegação de WCAG integral.

## Findings encerrados

| ID | Severidade | Evidência | Resultado |
| --- | --- | --- | --- |
| S8-F001 | Major | dashboard 9,6338 s > 3 s | resolvido e medido novamente |
| S8-F002 | Major | 108.026 findings S5 no gerador BCR | resolvido; S5 final exit 0 |
| S8-F003 | Minor | tabelas sem nome acessível | resolvido e revalidado |
| S8-F004 | Minor | retorno do detalhe perdia consulta | resolvido e coberto por teste |
| S8-F005 | Minor | landmarks `main` aninhados | resolvido e coberto por teste |

O primeiro gate final interrompeu em `detect-secrets` porque os fingerprints
SHA-256 sintéticos eram hexadecimais contínuos. O formato foi tornado agrupado,
com conteúdo completo e reversível; isso foi tratado como correção de evidência,
não como falha de segurança nem PASS presumido.

## Gate autoritativo final

Comando:

`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1`

Resultado final sobre a árvore encerrada: exit code `0`, 327 testes aprovados
em 78,92 s, 88% de
cobertura global, runtime/perfis, baseline documental, migrations, banco vazio,
formatação, Ruff, mypy, cobertura de domínio, `detect-secrets` e `pip-audit`
GREEN; nenhuma vulnerabilidade conhecida encontrada. Duração total do gate:
114,3 s. Uma tentativa imediatamente anterior dentro do sandbox ficou
inconclusiva somente no `pip-audit` por `WinError 10013`; a repetição autorizada
com rede real produziu o exit 0 acima. `git diff --check` também terminou exit 0.

Os bancos e manifests sintéticos descartáveis usados no candidato/S7 foram
removidos depois da captura; os artefatos duráveis sanitizados permanecem em
`quality/`.

## Decisão

Todos os critérios impeditivos observáveis estão verdes e não há P0/P1,
Blocker/Major, finding S5, threshold oficial excedido, migration inesperada ou
falha de recuperação/operação aberta. Portanto o candidato é
**READY_FOR_PILOT**. Essa classificação não promove a V0.4, não executa o
piloto, não autoriza S9 e não autoriza commit, push, tag ou release.
