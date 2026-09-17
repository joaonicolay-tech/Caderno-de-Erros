# Task Contract

Status: AUTHORIZED

## Identification

- Task ID: `V0.4-S8`
- Product version: `V0.4 — Primeiro MVP local realmente utilizável`
- Stage: `S8 — Hardening transversal, acessibilidade e BCR-1`
- Task type: release hardening / accessibility / performance / candidate validation
- Size: `L`
- Risk: `high`
- Recommended execution model: `GPT-5.6 Sol`
- Recommended reasoning: `High`
- Required review: A8 `profundo`
- Required plan: A4 persistent plan, as established by `V0.4-P0`

## Goal

Executar o hardening transversal da V0.4 antes do piloto, validando, medindo e
corrigindo somente defeitos comprovados dentro do escopo já aprovado de S1–S7,
para produzir um candidato tecnicamente endurecido e classificado objetivamente
como `READY_FOR_PILOT` ou `NOT_READY_FOR_PILOT`, sem executar o piloto S9.

## Context

- `docs/PROJECT_DEVELOPMENT_ARCHITECTURE_V1.md` é a baseline operacional
  `APPROVED/FROZEN` e rege autorização, contexto proporcional, evidência,
  review, gate, encerramento e checkpoints Git separados.
- `tasks/plans/v04-release-execution-plan.md` é a decomposição autoritativa da
  V0.4. S8 depende de S1–S7, é `L/high`, exige plano A4 e integra
  acessibilidade, segurança, performance, integridade e regressão antes de S9.
- Os handoffs encerrados de S1–S7 devem ser consumidos sem redefini-los:
  contratos semânticos S1; serviços/read models S2; dashboard S3; consulta,
  filtros, paginação, detalhe e timeline S4; checker read-only S5; recuperação
  isolada S6; e operação Windows S7.
- A definição e os parâmetros oficiais do `BCR-1` devem ser confirmados nas
  fontes vigentes, especialmente
  `docs/ADR-012_Parametros_Executaveis_BCR-1_e_CT-125_V0.3.md`, requisitos,
  Plano de Testes, executor existente e evidência V0.3. O baseline vigente
  inclui 10.000 questões, 100.000 attempts e 100.000 reviews; a execução deve
  confirmar dataset, seed, ambiente, runs, warm-ups, amostras, cálculo e
  thresholds antes de medir.
- A baseline de encerramento S7 está GREEN: 325 testes, 88% de cobertura,
  S5 exit `0`, backup/validação S6 e operação loopback com shutdown limpo.
  Esses fatos são handoff, não substituem a revalidação S8.

## Acceptance Criteria

- O plano A4 específico de S8 é criado antes do hardening, permanece dentro
  deste contrato e decompõe pelo menos: baseline e critérios; acessibilidade;
  responsividade/zoom; performance/`BCR-1`; queries/paginação; integridade S5;
  recuperação S6; operação S7; regressão; candidato/evidência; review/gate.
- A baseline funcional identifica os fluxos S1–S7 do candidato, executa testes
  relevantes, mede a performance inicial e registra somente defeitos reais.
- As superfícies principais — login/home quando aplicável, dashboard, consulta,
  filtros, paginação, detalhe, timeline e operações principais — são auditadas
  quanto a teclado, ordem lógica, ausência de keyboard trap, ativação, foco
  visível/coerente, labels, headings, landmarks, forms, tables, lists, links,
  buttons e mensagens, preferindo HTML nativo e sem ARIA redundante.
- Contraste e informação não dependente apenas de cor recebem evidência
  objetiva; zoom 200% e larguras representativas são validados nas superfícies
  principais sem conteúdo cortado, sobreposição, controles inacessíveis ou
  scroll horizontal inadequado. Limitações manuais/assistidas são registradas
  sem alegar conformidade WCAG integral não demonstrada.
- Empty states e mensagens recuperáveis de S3/S4 são revalidados: ausência de
  dados não vira sucesso, métrica falsa ou `0%` indevido, e falha conhecida não
  aparece somente como traceback.
- O `BCR-1` oficial é executado de forma reproduzível com dados sintéticos e
  seus parâmetros, metodologia e thresholds preservados. A evidência registra
  operação, dataset, ambiente, quantidade de execuções, métrica oficial
  aplicável, resultados brutos, p50/p95 quando aplicável, queries e decisão.
- As leituras V0.4 previstas são medidas conforme o escopo real: dashboard,
  analytics S2, listagem, busca, filtros, paginação, drill-downs e
  detalhe/histórico quando aplicável, sem transformar o benchmark em medição de
  toda view.
- Threshold oficial existente é aplicado sem alteração. Se uma nova leitura
  não possuir threshold oficial, a medição é registrada sem PASS/FAIL
  arbitrário e qualquer necessidade de decisão fica explicitamente separada.
- Queries críticas são auditadas para N+1, query por linha, duplicação,
  agregação repetida e paginação/drill-down caro. A paginação em escala preserva
  ordering total, filtros, busca e páginas posteriores sem duplicação ou omissão.
- O dashboard é validado na escala `BCR-1` quanto a tempo, queries,
  reconciliação e estados empty/zero, sem alteração de semântica.
- O checker S5 é executado no candidato apropriado e retorna exit `0`. Exit `2`
  exige investigação de findings sem mascaramento; exit `3` é falha operacional
  ou validação inconclusiva e não comprova saúde.
- O ensaio S6 comprova backup, validação, restore em destino isolado, abertura e
  reconciliação da aplicação, checks físicos e checker S5 exit `0`, sem restore
  destrutivo sobre o banco principal.
- A operação Windows S7 é revalidada quanto a entry point, startup, loopback,
  shutdown, ausência de processo órfão, checker e backup/validation.
- A regressão relevante cobre questões, attempts, review cycles, dashboard,
  consulta, backup, checker e operação; defeitos corrigidos recebem teste de
  regressão adequado.
- Permanecem comprovados CSRF, secrets, Workspace isolation, ausência de
  exposição de dados, path handling seguro e logs sanitizados. Leakage entre
  Workspaces é Blocker.
- Coverage e controles vigentes são preservados; migrations continuam limpas;
  detect-secrets e pip-audit ficam GREEN. Indisponibilidade externa de
  pip-audit é infraestrutura/inconclusiva até repetição autorizada com resultado
  real, nunca PASS presumido.
- Toda correção possui problema, evidência, alteração mínima e revalidação.
  Quando houver gargalo corrigido, medir antes quando possível e medir depois.
- O review A8 profundo termina `APPROVED`, sem Blocker/Major aberto. Minor é
  tratado conforme a política vigente e permanece explicitamente registrado.
- Existe evidência durável e enxuta do candidato reunindo gate, testes,
  cobertura, `BCR-1`, acessibilidade automatizada/manual e limitações, S5, S6,
  S7, findings e estado final.
- `git diff --check` e o gate autoritativo terminam GREEN com exit code `0`.
- O estado final é explicitamente `READY_FOR_PILOT` ou
  `NOT_READY_FOR_PILOT`, baseado em evidência objetiva. S8 não autoriza S9.

## Expected Scope

- Criar e encerrar o plano A4 persistente específico de S8.
- Auditar transversalmente e executar testes focados dos fluxos S1–S7 que
  formam o candidato V0.4.
- Executar e ampliar o executor `BCR-1` apenas para as leituras V0.4 previstas
  no plano P0, preservando o benchmark e seus thresholds oficiais.
- Medir performance e query count; validar paginação, drill-downs e
  reconciliação na escala prevista.
- Auditar e corrigir defeitos comprovados de acessibilidade, teclado, foco,
  labels, semântica HTML, contraste, cor, zoom 200%, responsividade, empty/error
  states, integração, segurança e isolamento por Workspace.
- Corrigir somente gargalos e N+1/query paths comprovadamente inadequados para
  a escala `BCR-1`, sem reinterpretar regras de negócio.
- Executar o checker S5, ensaio isolado de backup/restore S6 e revalidação da
  operação Windows S7.
- Criar testes de regressão para defects encontrados e produzir evidências
  duráveis de acessibilidade, benchmark e candidate readiness.
- Atualizar somente documentação necessária, registrar métricas A7 com fatos
  disponíveis e executar review A8 profundo.

## Protected Scope

- Não alterar semântica S1, significado de métricas, regra de negócio, política
  de revisão, requisitos oficiais ou ADRs vigentes sem decisão específica.
- Não alterar arquitetura analítica S2, escopo funcional do dashboard S3,
  escopo funcional da consulta S4, catálogo S5, contrato de recuperação S6 ou
  escolha operacional S7 sem bug comprovado e evidenciado.
- Não alterar schema nem criar migrations. Se necessidade real surgir, registrar
  blocker/decisão e não ampliar a autorização.
- Não alterar Roadmap, Project Development Architecture v1.0, Skills,
  `scripts/quality.ps1` nem thresholds oficiais do `BCR-1`.
- Não introduzir feature nova, filtros novos, redesign, refatoração cosmética ou
  ampla, renomeação generalizada, V0.5, `BCR-2`, gráfico, FTS, cache ou snapshot
  sem necessidade comprovada e autoridade compatível.
- Não executar piloto humano/final, promover V0.4 nem iniciar S9.

## Constraints

- Seguir o ciclo `validar → medir → corrigir defeitos comprovados → revalidar`.
  Uma lista de melhorias desejáveis não constitui findings nem autorização.
- Ler primeiro contrato, plano P0 e handoffs necessários; ampliar contexto
  somente conforme A3, riscos, findings e referências formais aplicáveis.
- Usar ferramentas de acessibilidade já disponíveis/coerentes; não introduzir
  dependência grande para uma auditoria pontual sem necessidade comprovada.
- Usar dados sintéticos controlados, sem dados pessoais reais quando
  desnecessários, e realizar somente ensaios manuais seguros.
- Não fabricar validações visuais, humanas, métricas, ambiente, resultados,
  tempos, queries ou observações que não tenham sido realmente executados.
- Não baixar cobertura, enfraquecer teste, alterar threshold ou modificar gate
  para obter PASS.
- Não criar gerenciamento JavaScript de foco, sistema global de erros ou
  redesign mobile sem necessidade comprovada dentro do MVP.
- Commit, push, tag e release exigem autorização expressa separada.

## Verification

- Criar baseline com testes focados relevantes antes das correções e repetir os
  conjuntos afetados após cada correção material.
- Executar os testes previstos pelo plano P0, incluindo conforme aplicável
  `CT-105/106/108/110/112`, regressão `CT-107`, `CT-121/123`, `CT-128`,
  acessibilidade automatizável e protocolo manual, checker, logs, migrations e
  backup smoke.
- Executar o `BCR-1` oficial e as leituras V0.4 com dataset, ambiente, runs,
  amostras, warm-ups, método p95 e thresholds confirmados nas fontes vigentes.
- Verificar query count e estabilidade da paginação com dataset grande.
- Executar `python manage.py check_integrity` no candidato e no restore isolado;
  somente exit `0` é saudável.
- Executar o procedimento S6 em artefatos/destinos isolados e o smoke S7 em
  Windows, comprovando startup, loopback, shutdown e ausência de órfão.
- Executar validação real das superfícies principais por teclado, foco,
  contraste, zoom 200%, responsividade e Chrome/Edge quando disponíveis,
  separando evidência automatizada, manual e limitações.
- Executar review A8 profundo e resolver todo Blocker/Major aplicável.
- Executar `git diff --check`.
- Executar o gate autoritativo:
  `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1`.

## Documentation Impact

- Criar o plano A4 S8 em `tasks/plans/` e encerrá-lo com evidência real.
- Produzir artefato durável S8 para `BCR-1`, acessibilidade, integrações S5/S6/S7,
  findings, review, gate e decisão do candidato.
- Atualizar documentação operacional somente se um defeito corrigido mudar o
  comportamento ou procedimento efetivo.
- Registrar métricas A7 de S8 separadas de bootstrap/infraestrutura, usando
  `unknown` para duração, quotas ou fatos indisponíveis.
- No encerramento comprovado, atualizar `PROJECT_STATE.md`, arquivar este
  contrato em `tasks/completed/` e retornar `tasks/current.md` a
  `NO_TASK_AUTHORIZED`, sem autorizar S9.

## Done When

- O plano A4 foi criado antes da implementação e encerrado.
- A baseline e as superfícies principais foram auditadas; teclado, foco,
  labels, semântica, contraste, cor, zoom 200%, responsividade e empty/error
  states possuem evidência objetiva e limitações explícitas.
- O `BCR-1` oficial e as leituras V0.4 previstas foram medidos de forma
  reproduzível, sem alteração de thresholds; gargalos impeditivos comprovados
  foram corrigidos e revalidados.
- Query paths e paginação em escala foram validados sem N+1 impeditivo,
  duplicação, omissão ou ordering instável.
- Checker S5 está saudável; recuperação S6 está saudável em restore isolado; a
  operação Windows S7 está revalidada sem processo órfão.
- Workspace isolation, segurança, logs sanitizados, migrations, cobertura e
  regressões permanecem saudáveis.
- Evidências S8 existem; review A8 profundo está `APPROVED`; não há
  Blocker/Major ou P0/P1 aplicável aberto.
- `git diff --check` passa e o gate autoritativo está GREEN, exit code `0`.
- Nenhuma migration ou mudança de schema foi criada.
- O candidato está explicitamente `READY_FOR_PILOT` ou
  `NOT_READY_FOR_PILOT` com base em fatos observados.
- S8 está arquivada, `tasks/current.md` retornou a `NO_TASK_AUTHORIZED` e S9
  permanece não autorizada e não iniciada.
