# Task Contract

Status: AUTHORIZED

## Identification

- Task ID: `V0.4-S9`
- Product version: `V0.4 — Primeiro MVP local realmente utilizável`
- Stage: `S9 — Piloto controlado e promoção`
- Task type: controlled pilot / release validation / promotion
- Size: `M`
- Risk: `high`
- Recommended execution model: `GPT-5.6 Sol`
- Recommended reasoning: `Medium`
- Required review: A8 `profundo`
- Required plan: A4 persistent plan, as established by `V0.4-P0`

## Goal

Executar o piloto local controlado da V0.4 sobre ambiente e dados protegidos e,
somente com todas as evidências impeditivas satisfeitas, decidir formalmente
entre `V0.4 PROMOTED` e `V0.4 NOT PROMOTED`.

O princípio da etapa é: **piloto antes de promoção; evidência antes de
conclusão**. Testes aprovados, candidato `READY_FOR_PILOT`, startup funcional ou
aparente completude, isoladamente, não promovem a versão.

## Context

- `docs/PROJECT_DEVELOPMENT_ARCHITECTURE_V1.md` é a baseline operacional
  `APPROVED/FROZEN` e rege autorização, contexto proporcional, evidência,
  review, gate, encerramento e checkpoints Git separados.
- `tasks/plans/v04-release-execution-plan.md` é a decomposição autoritativa da
  V0.4. S9 é `M/high`, exige plano A4, piloto real controlado, recuperação,
  review profundo, gate final e decisão explícita de promoção.
- S1–S8 estão concluídas. O handoff S8 em
  `quality/v04-s8-candidate-result.md` classifica o candidato como
  `READY_FOR_PILOT`, com gate GREEN, BCR-1 satisfatório, S5 exit `0`, S6 e S7
  saudáveis, nenhuma migration inesperada e nenhum Blocker/Major aberto.
- O piloto deve consumir, sem redefinir, o checker read-only S5, o fluxo de
  backup/restore isolado S6, a operação Windows S7 e as evidências de hardening,
  acessibilidade e BCR-1 S8.
- Os critérios oficiais de promoção são os de P0 e do Roadmap V0.4. A promoção
  não é automática e qualquer fato não observado permanece `NOT OBSERVED`,
  `unknown` ou pendente, conforme aplicável; nunca vira PASS inferido.

## Preconditions

- Antes de iniciar o piloto, confirmar documentalmente que o candidato S8 está
  `READY_FOR_PILOT` e que seu gate final está GREEN.
- Confirmar BCR-1 satisfatório, S5 saudável, S6 saudável, S7 saudável, ausência
  de Blocker/Major e ausência de migration inesperada.
- Se qualquer pré-condição não estiver realmente satisfeita, não executar o
  piloto nem declarar promoção; registrar a condição impeditiva.
- Criar, antes da execução do piloto, plano A4 persistente específico para S9.
  O plano deve cobrir no mínimo: pré-condições; preparação; backup pré-piloto;
  cópia/isolamento; baseline; cenários; coleta de evidência; defects; retestes;
  pós-piloto; gate final; decisão de promoção; e checkpoint/tag/release somente
  quando posteriormente autorizados. O plano não amplia este contrato.

## Acceptance Criteria

- Um backup S6 real do estado relevante é criado imediatamente antes do piloto,
  validado física e logicamente, restaurado somente em destino novo e isolado,
  aberto/reconciliado pela aplicação e verificado por S5. Existência ou checksum
  do arquivo, sem restore aprovado, não prova recuperação.
- O piloto usa ambiente local e cópia controlada dos dados reais ou conjunto
  equivalente aprovado pelo plano. Nunca opera sobre a única cópia importante.
  Origem, destino, método, proteção e cleanup são registrados sem expor dados
  pessoais.
- Se dados pessoais forem necessários, sua exposição é minimizada e nenhum
  conteúdo pessoal é incluído em logs, relatórios ou documentos versionados.
- Antes do primeiro cenário, a baseline registra candidato/versão ou commit
  disponível, totais de questões, attempts e reviews, estado S5, backup, banco
  piloto e gate/candidato S8, sem conteúdo pessoal desnecessário.
- O piloto percorre, conforme os fluxos reais existentes: startup e acesso pela
  operação Windows S7; dashboard e métricas; listagem, busca, filtros,
  paginação, detalhe e timeline; questão existente, tentativa inicial, resultado,
  erro e classificação quando aplicável; revisão e atualização temporal do
  ciclo; reflexo/reconciliação no analytics; S5 após cenários relevantes; e S6
  quando previsto no plano.
- Cada cenário registra objetivo, pré-condição, ações, resultado esperado,
  resultado observado, `PASS`/`FAIL` e evidência. “Pareceu funcionar” não é
  evidência suficiente.
- Capacidades inexistentes no escopo V0.4 não são criadas para completar o
  roteiro; a fronteira é registrada.
- Feedback, participantes, ações, observações e julgamentos humanos não são
  fabricados. Critério dependente de julgamento humano real não fornecido fica
  `NOT OBSERVED` ou equivalente.
- Todo defect recebe ID, severidade, cenário, evidência, impacto, reprodução e
  decisão conforme A8/convenção vigente. Blocker ou Major impede promoção.
- Correções durante S9 limitam-se a defects comprovados pelo piloto, dentro da
  V0.4, proporcionais e sem nova decisão normativa. Não incluem feature,
  redesign, refatoração desejável ou V0.5. Expansão de escopo interrompe a
  correção e é registrada.
- Toda correção autorizada recebe teste específico, repetição do cenário
  afetado, regressões relacionadas e revalidação de checker/recovery/gate quando
  afetados. Minor só pode permanecer se a política vigente permitir, com impacto
  conhecido e sem comprometer integridade, dados ou fluxo principal.
- Ao final do piloto, S5 retorna obrigatoriamente exit `0` para promoção. Exit
  `2` com finding impeditivo bloqueia promoção; exit `3` é inconclusivo e também
  bloqueia promoção.
- O estado pós-piloto é comparado ao esperado: dados, analytics e reviews
  coerentes, sem corrupção ou relação inválida entre Workspaces.
- O backup pré-piloto permanece válido, é restaurável isoladamente e passa os
  checks necessários. Nenhum restore destrutivo é feito no banco principal.
- S7 é revalidada quanto a startup, acesso, shutdown e ausência de processo
  órfão, sem redesenhar os scripts.
- Defeito evidente de teclado, foco, zoom, layout ou labels encontrado no piloto
  é registrado e tratado conforme severidade. A auditoria S8 inteira e o BCR-1
  inteiro só são repetidos se uma correção puder afetá-los ou se o plano exigir.
- A documentação executável cobre iniciar, usar, consultar, backup, validar
  backup, checker, recuperação suportada, atualização e troubleshooting, sem
  documentar features inexistentes.
- Existe artefato durável S9, sanitizado, contendo candidato, backup pré-piloto,
  ambiente, cenários, resultados, defects, correções, retestes, S5, S6, S7,
  gate, review e decisão final.
- Se a decisão for `V0.4 PROMOTED`, existe também resumo final de promoção com
  escopo, S1–S9, testes, cobertura, BCR-1, acessibilidade, checker, recuperação,
  Windows, piloto, findings, gate e status.
- O review A8 profundo termina `APPROVED`, sem Blocker/Major aberto para uma
  promoção, e verifica piloto, evidência, defects, gate, documentação,
  integridade, recovery, ausência de scope creep e ausência de promoção
  prematura.
- A decisão final é exatamente `V0.4 PROMOTED` ou `V0.4 NOT PROMOTED`, sem
  status intermediário ambíguo.

## Promotion Gate

Para decidir `V0.4 PROMOTED`, confirmar explicitamente, sem omitir itens:

1. S1–S9 concluídas com critérios, evidências e contratos arquivados no fluxo de
   encerramento;
2. suite aplicável e cobertura conforme política vigente, incluindo ao menos
   80% nos módulos críticos de domínio;
3. migrations coerentes/limpas e atualização desde a release anterior suportada
   preservando dados, backup e caminho de retorno;
4. Ruff, mypy, detect-secrets, `pip-audit` e demais controles do gate GREEN;
5. BCR-1 satisfatório e reproduzível sob os thresholds oficiais vigentes;
6. invariant checker saudável no candidato e nas cópias restaurada/piloto;
7. backup/restore, RPO/RTO aplicáveis e documentação comprovados;
8. acessibilidade S8 registrada para teclado, foco, labels, contraste,
   Chrome/Edge quando disponíveis, responsividade e zoom 200%, sem alegação não
   demonstrada;
9. operação Windows S7 validada;
10. piloto real controlado `PASS` e retestes necessários concluídos;
11. documentação de uso, instalação, atualização, backup e recuperação
    executável e consistente;
12. review profundo final `APPROVED`, sem Blocker/Major, P0/P1 ou defect
    impeditivo aberto;
13. working tree, `PROJECT_STATE.md`, Roadmap/matriz de release e artefatos de
    qualidade coerentes;
14. `git diff --check` e gate autoritativo final com exit code `0`.

Falha crítica de integridade, perda de dados, acesso cruzado, duplicação de
tentativa, gabarito exposto, backup irrecuperável ou migration destrutiva
bloqueia promoção. Nenhum threshold novo é criado durante S9.

Se qualquer critério impeditivo permanecer, decidir `V0.4 NOT PROMOTED`,
registrar blockers, critérios pendentes, correções necessárias e estado seguro
do repositório; não iniciar V0.5 nem criar tag/release da V0.4.

Se todos os critérios forem satisfeitos, decidir `V0.4 PROMOTED` e atualizar os
artefatos oficiais necessários para registrar conclusão, piloto, promoção,
evidências e gate final; não iniciar V0.5.

## Expected Scope

- Criar e encerrar o plano A4 persistente específico de S9.
- Preparar ambiente/cópia piloto protegidos e executar backup S6 pré-piloto com
  validação e restore isolado.
- Registrar baseline sanitizada e executar os cenários reais do MVP definidos
  no plano, ajustados às capacidades existentes.
- Coletar evidência objetiva, classificar defects, aplicar somente correções de
  piloto permitidas e executar retestes proporcionais.
- Revalidar S5, S6, S7 e, quando afetados, BCR-1 e acessibilidade S8.
- Executar o gate de promoção, produzir evidência S9 e, se promovida, o resumo
  final da V0.4.
- Atualizar somente a documentação oficial de uso/release, Roadmap e
  `PROJECT_STATE.md` necessários à decisão realmente observada.
- Registrar métricas A7 de S9 separadamente do bootstrap/infraestrutura, sem
  estimar duração ou cotas; valores indisponíveis permanecem `unknown`.
- Encerrar e arquivar S9 conforme o workflow oficial.

## Protected Scope

- Não operar sobre a única cópia dos dados importantes nem restaurar sobre o
  banco principal.
- Não incluir dados pessoais, enunciados, respostas, explicações, credenciais ou
  conteúdo sensível em logs/evidências versionadas.
- Não alterar critérios, thresholds ou classificação depois de observar os
  resultados para obter PASS.
- Não fabricar evidência humana, observações, participantes, métricas, retestes
  ou resultados.
- Não criar capacidade ausente, feature, redesign, refatoração ampla, migration,
  mudança normativa, V0.5 ou trabalho de etapa futura para completar o piloto.
- Não alterar Project Development Architecture v1.0, Skills ou
  `scripts/quality.ps1`.
- Não esconder Minor nem promover com P0/P1, Blocker/Major ou condição
  impeditiva aberta.
- Não fazer commit, push, tag `v0.4.0`, GitHub Release ou publicação externa sem
  autorização expressa posterior e específica, mesmo após `V0.4 PROMOTED`.

## Constraints

- Seguir progressive disclosure e consumir as fontes S5–S8 já encerradas sem
  reabrir indiscriminadamente o projeto.
- Preservar o banco original, o backup exigido e as evidências duráveis. Remover
  somente banco/cópia sintética ou descartável quando apropriado e documentar o
  cleanup.
- Não deixar servidor, listener ou processo órfão e não deixar temporários
  desnecessários após o piloto.
- Correção de Blocker/Major só é permitida quando claramente dentro da V0.4,
  proporcional e sem nova decisão normativa; caso contrário, interromper e
  registrar.
- Promoção documental e checkpoint Git são decisões separadas. A promoção não
  autoriza commit, push, tag ou release.

## Verification

- Executar os cenários do plano A4 com resultados observados e evidência por
  cenário, incluindo `CT-124`–`126` quando aplicáveis.
- Executar o checker S5 nos pontos definidos pelo plano e ao final; somente exit
  `0` é saudável para promoção.
- Executar e comprovar o fluxo S6 de backup, validação, restore isolado,
  abertura/reconciliação e S5, sem restore destrutivo.
- Revalidar S7 com startup, acesso loopback, shutdown e ausência de órfão.
- Retestar toda correção e repetir BCR-1/acessibilidade somente quando o risco ou
  o plano exigirem.
- Executar review A8 profundo e resolver todo Blocker/Major aplicável antes de
  uma promoção.
- Executar `git diff --check`.
- Executar o gate autoritativo:
  `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1`.

## Documentation Impact

- Criar e encerrar o plano A4 S9 em `tasks/plans/`.
- Produzir evidência durável S9 sanitizada e, somente se promovida, resumo final
  de promoção/release notes da V0.4.
- Atualizar documentação de uso/operação apenas quando necessário para refletir
  o comportamento real e os procedimentos comprovados.
- Atualizar Roadmap/estado somente nas fontes oficiais aplicáveis e somente após
  a decisão final; marcar V0.4 concluída/promovida apenas se a decisão for
  `V0.4 PROMOTED`.
- Atualizar `PROJECT_STATE.md`, registrar métricas A7, arquivar este contrato e
  retornar `tasks/current.md` a `NO_TASK_AUTHORIZED` no encerramento comprovado.

## Done When

- O plano A4 foi criado antes do piloto e encerrado com fatos observados.
- A pré-condição `READY_FOR_PILOT`, o gate S8 e a saúde de BCR-1/S5/S6/S7 foram
  confirmados antes do piloto.
- Existe backup pré-piloto válido, restaurável e verificado por S5; ambiente e
  cópia piloto foram protegidos e documentados.
- Baseline, cenários principais, resultados observados e evidências sanitizadas
  foram registrados sem fabricar julgamento humano.
- Todos os defects foram classificados; defects impeditivos foram resolvidos e
  revalidados ou causaram a decisão de não promover.
- Checker S5 pós-piloto, recuperação S6, operação S7 e estado pós-piloto foram
  confirmados no nível exigido para a decisão.
- Documentação aplicável foi atualizada, review A8 profundo foi concluído e o
  gate final foi executado.
- Para promoção, `git diff --check` e gate autoritativo estão GREEN, exit code
  `0`, e não existe Blocker/Major ou P0/P1 aplicável aberto.
- A decisão final exata `V0.4 PROMOTED` ou `V0.4 NOT PROMOTED` está registrada
  e sustentada pela matriz completa de promoção.
- A evidência S9 existe; se promovida, a promotion evidence final também existe.
- Dados/cópias descartáveis e processos foram limpos sem remover backup ou
  evidência obrigatória.
- Nenhum commit, push, tag ou release foi executado sem autorização específica.
- S9 foi arquivada, `tasks/current.md` retornou a `NO_TASK_AUTHORIZED` e V0.5
  permaneceu não autorizada e não iniciada.

## Closure Evidence

- Encerrada em 19 de setembro de 2026 com a decisão exata
  `V0.4 PROMOTED`.
- Plano A4: `tasks/plans/v04-s9-controlled-pilot-promotion.md`, status
  `COMPLETED`.
- Piloto: `quality/v04-s9-pilot-result.md`; ambiente isolado, cenários PASS,
  S5 exit 0 e backups pré/pós-piloto validados e restaurados.
- Finding S9-F001 Major foi resolvido no banco piloto e revalidado; review A8
  profundo `APPROVED`, com Blocker 0, Major 0 e Minor 0 abertos.
- Testes: 127 regressões focadas passaram; nenhuma alteração de código e nenhum
  teste novo foram necessários.
- `git diff --check`: exit 0.
- Gate autoritativo: GREEN na primeira passagem, exit 0 em 124,3 s; após os
  registros de encerramento, a árvore final repetiu GREEN, exit 0 em 109,8 s,
  com 327 testes em 76,53 s, cobertura global 88%, migrations, formatação,
  Ruff, mypy, cobertura de domínio, `detect-secrets` e `pip-audit` aprovados.
- Promoção: `quality/v04-promotion-result.md`; tag `v0.4.0` ainda não criada.
- Cleanup: cópias descartáveis e processos removidos; backups pré e pós-piloto
  finais preservados; porta 8000 sem listener.
- Nenhum commit, push, tag ou release foi executado. V0.5 permaneceu
  `NOT AUTHORIZED` e não foi iniciada.
