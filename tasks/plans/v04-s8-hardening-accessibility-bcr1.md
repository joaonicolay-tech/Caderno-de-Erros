# Plano: V0.4-S8 — Hardening, acessibilidade e BCR-1

- ID da tarefa relacionada: V0.4-S8
- Status: COMPLETED
- Autoridade: `tasks/current.md`; este plano não amplia o contrato.
- Objetivo: decompor a validação integrada do candidato V0.4 e sustentar a
  decisão `READY_FOR_PILOT` ou `NOT_READY_FOR_PILOT` sem executar S9.
- Princípio: validar → medir → corrigir somente defeitos comprovados → revalidar.

## Decomposição

1. Registrar baseline do commit, working tree, testes focados, fontes e
   critérios; classificar fatos como defeito, limitação, melhoria ou fora do
   escopo antes de editar comportamento.
2. Auditar acessibilidade automatizável nas superfícies V0.4: teclado, foco,
   labels, headings, landmarks, forms, tabelas, listas, links, botões, mensagens,
   contraste e informação não dependente apenas de cor.
3. Validar manualmente em navegador as jornadas principais, zoom 200% e larguras
   representativas, registrando versões, observações e itens não validados sem
   alegar conformidade WCAG integral.
4. Confirmar a fonte oficial, dataset, seed, metodologia e thresholds do BCR-1;
   executar as três repetições das gravações sem alterar seus parâmetros.
5. Ampliar de forma reproduzível o executor para medir somente as leituras V0.4
   previstas: dashboard/analytics, listagem, busca, filtros, paginação,
   drill-downs e detalhe/histórico, aplicando thresholds oficiais existentes e
   deixando novas medições como observacionais quando não houver threshold.
6. Auditar query counts, N+1 e paginação em 10.000 questões, incluindo ordering
   total, páginas posteriores, busca, filtros e combinações sem duplicação ou
   omissão; corrigir apenas gargalos impeditivos comprovados.
7. Executar o checker S5 no candidato, preservar seu contrato read-only e
   registrar comando, saída sanitizada, findings e exit code.
8. Reexecutar S6 com backup, validação, restore em destino isolado, checks
   SQLite, abertura/reconciliação, S5 exit 0 e hashes que provem a preservação do
   banco principal e do backup.
9. Revalidar S7 em Windows a partir de diretório externo: entry point e wrapper,
   loopback, porta, startup, shutdown, ausência de órfão, checker e backup.
10. Reexecutar regressões semânticas S1-S4, Workspace isolation, CSRF, logs,
    paths, secrets, migrations e demais controles de segurança aplicáveis;
    adicionar testes sustentáveis para cada defeito corrigido.
11. Consolidar findings, evidências de acessibilidade/BCR-1/candidato, executar
    review A8 profundo, `git diff --check` e gate autoritativo; somente com toda
    a evidência elegível encerrar o plano, atualizar estado/métricas, arquivar S8
    e retornar `tasks/current.md` a `NO_TASK_AUTHORIZED`.

## Dependências, riscos e verificação

- S1-S7 são handoffs consumidos, não escopo para redesenho; semântica, schema,
  migrations, thresholds, Architecture v1.0, Skills e `quality.ps1` permanecem
  protegidos.
- Leakage entre Workspaces, finding S5, recovery inconclusiva, operação Windows
  com órfão, threshold oficial excedido, gate vermelho ou Blocker/Major aberto
  impedem `READY_FOR_PILOT`.
- Benchmarks usarão banco descartável e dados sintéticos; restore nunca terá o
  banco ativo como destino. Resultados brutos e exit codes serão preservados.
- Acessibilidade manual só será afirmada para ações realmente executadas em UI;
  limitações ficarão explícitas.
- A verificação detalhada e o aceite permanecem exclusivamente no contrato
  corrente. S9, piloto, promoção, commit, push, tag e release não serão feitos.

## Condição de saída

Marcar `COMPLETED` somente depois que as evidências duráveis registrarem o
resultado de cada eixo, o review profundo estiver sem Blocker/Major, o gate
autoritativo tiver exit 0 e o candidato receber exatamente um estado. Se um
requisito impeditivo persistir, encerrar honestamente como
`NOT_READY_FOR_PILOT`, sem autorizar ou iniciar S9.

## Encerramento observado — 17 de setembro de 2026

- Candidato classificado como `READY_FOR_PILOT` com base em BCR-1 oficial,
  acessibilidade assistida, S5/S6/S7, regressões e gate documentados em
  `quality/v04-s8-candidate-result.md`.
- Review A8 profundo `APPROVED`, sem Blocker/Major/Minor aberto.
- Gate autoritativo final exit `0`: 327 testes, 88% de cobertura, migrations,
  Ruff, mypy, detect-secrets e pip-audit GREEN.
- Limitações manuais permaneceram explícitas; não houve alegação de WCAG
  integral, piloto, promoção, migration, commit, push, tag ou release.
