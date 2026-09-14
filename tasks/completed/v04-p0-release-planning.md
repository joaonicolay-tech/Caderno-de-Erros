# Task Contract

Status: COMPLETED

## Identification

- Task ID: V0.4-P0
- Product version: V0.4
- Stage: P0 — Planejamento da Release V0.4
- Task type: product release planning / decomposition / traceability
- Size: L
- Risk: medium

## Goal

Produzir um plano executável da V0.4 do Caderno de Erros Inteligente, baseado
no Roadmap oficial, no estado promovido da V0.3, na Project Development
Architecture v1.0, no comportamento real do produto e nos testes, ADRs e
dependências técnicas relevantes. O plano deve decompor a release em etapas
coerentes, verificáveis e proporcionais, sem implementar funcionalidade V0.4.

## Context

- O Roadmap oficial é a autoridade sobre o escopo planejado da V0.4; código,
  migrations e testes são a autoridade sobre o que já existe.
- `PROJECT_STATE.md` registra a V0.3 promovida e a Project Development
  Architecture v1.0 aprovada/congelada como baseline operacional.
- Aplicar `docs/PROJECT_DEVELOPMENT_ARCHITECTURE_V1.md`, inclusive autorização,
  progressive disclosure, separação `current`/`plans`/`completed`, Skills,
  testes focados, review proporcional, gate, métricas, `finish-task` e
  checkpoint Git somente quando expressamente autorizado.
- Consultar, sob progressive disclosure, o Roadmap oficial, requisitos, plano
  de testes, código, testes e ADRs necessários para auditar escopo, estado real,
  dependências, riscos e divergências.
- Aplicar `docs/A7_Politica_de_Modelos_Reasoning_Escalonamento_e_Metricas.md`
  às recomendações iniciais por etapa e `docs/review/code-review.md` à
  profundidade de review.
- Se Roadmap e estado executável divergirem, registrar a divergência e seu
  tratamento no plano, sem inventar uma resolução.

## Acceptance Criteria

- O escopo oficial da V0.4 e o estado real pós-V0.3 são auditados.
- Cada requisito obrigatório da V0.4 aparece em pelo menos uma etapa do plano,
  sem desaparecimento silencioso, e duplicações ou requisitos que devam ser
  implementados conjuntamente são identificados.
- A release é decomposta na quantidade de etapas que melhor equilibre coesão,
  independência, verificabilidade, risco e uso eficiente de contexto/cota, sem
  assumir exatamente dez etapas e sem criar etapas enormes ou microtarefas
  artificiais.
- Para cada etapa, o plano define ID, nome, objetivo, escopo, fora de escopo
  relevante, dependências, tamanho, risco, critérios de aceite,
  testes/verificações, documentação afetada, recomendação inicial de
  modelo/reasoning, review leve/padrão/profundo e evidência de encerramento.
- A ordem é justificada por dependências reais: contratos de métricas antes da
  apresentação; consultas/dados antes das telas dependentes; integridade antes
  da promoção; backup antes do piloto; acessibilidade durante a construção e
  no hardening final; BCR1 e invariant checker no release gate; empacotamento
  após estabilidade suficiente do fluxo local. Hipóteses são ajustadas ao
  repositório real.
- A estratégia de testes, verificações, gates e pontos de revisão profunda é
  definida, incluindo quais etapas exigem plano persistente.
- Os critérios de promoção final cobrem etapas concluídas, testes, cobertura,
  migrations, gate, BCR1, invariant checker, backup/restore, acessibilidade,
  piloto local controlado, documentação e ausência de P0/P1 ou equivalente
  impeditivo.
- O plano permite avaliar ao final da V0.4 se o usuário consegue cadastrar e
  consultar material, compreender desempenho e revisões, navegar histórico,
  operar sem métricas enganosas, recuperar dados, executar localmente com
  documentação e usar o produto com acessibilidade básica.
- Exclusões e fronteiras permanecem explícitas; itens fora da V0.4 podem ser
  citados apenas como fronteira.
- Nenhum código funcional, schema, migration, regra de negócio, teste funcional
  ou baseline V0.3 é alterado durante P0.
- O plano executável fica registrado em fonte durável apropriada em
  `tasks/plans/`.

## Expected Scope

- Auditar o Roadmap oficial, o estado real pós-V0.3, o comportamento do produto
  e os testes, ADRs e dependências técnicas relevantes.
- Construir o mapa de rastreabilidade, identificar dependências, riscos,
  divergências e requisitos duplicados/conjuntos, decompor a release e definir
  ordem, critérios, verificações, evidências e promoção final.
- Planejar integralmente o dashboard básico e as definições explicáveis de
  métricas com drill-down.
- Planejar questões cadastradas versus realizadas; tentativas, acertos, erros e
  taxa com período e denominador claros; revisões concluídas hoje, devidas,
  atrasadas e futuras; desempenho por disciplina e por assunto; e frequência
  por categoria de erro.
- Planejar listagem de questões, busca, filtros básicos, paginação estável,
  detalhe completo, histórico navegável, empty states e ausência de métricas
  falsas.
- Planejar backup SQLite consistente, restauração tecnicamente documentada e
  testada, escolha operacional de empacotamento/atalho local Windows, logs e
  mensagens recuperáveis.
- Planejar teclado, foco, labels, contraste e zoom 200% como requisitos de
  acessibilidade incorporados às etapas pertinentes e ao hardening final.
- Planejar BCR1 e invariant checker como gate, documentação de
  uso/backup/update e piloto local controlado com dados copiados e backup
  prévio.
- Classificar cada etapa por tamanho e risco, recomendar inicialmente
  modelo/reasoning segundo A7 e definir review proporcional segundo A8.
- Criar e manter o plano durável da V0.4 e os registros documentais necessários
  ao encerramento de P0.

## Protected Scope

- Código Django, templates funcionais e CSS funcional.
- Migrations, schema, regras de negócio e testes funcionais.
- Baseline V0.3 e tag protegida `v0.3.0`.
- Project Development Architecture v1.0, salvo referência.
- Skills, políticas A7/A8 e `scripts/quality.ps1`.
- Configuração pessoal e `.codex/config.toml`.
- Implementação funcional de qualquer etapa da V0.4.

## Constraints

- Não implementar nenhuma funcionalidade da V0.4 durante P0.
- Não redesenhar a Project Development Architecture v1.0; problemas
  arquiteturais encontrados devem ser registrados, não corrigidos
  silenciosamente.
- Não ordenar etapas apenas por preferência visual nem assumir que a release
  precisa ter exatamente dez etapas.
- Não fabricar decisões, evidências, parâmetros, resultados de testes ou
  resolução de divergências.
- Não autorizar nem iniciar etapa funcional da V0.4 ao encerrar P0.
- Não fazer commit, push, tag ou release sem autorização expressa própria.
- Não planejar como implementação da V0.4: domínio/prioridade;
  mastered/reopen; reagendamento avançado; histórico de correções; categorias
  pessoais; filtros salvos; exclusão permanente; exportação CEI pela UI;
  autenticação; API pública; integrações externas; IA; OCR; anexos;
  notificações; gamificação.

## Verification

- Verificar a cobertura de todos os requisitos obrigatórios no mapa de
  rastreabilidade e a presença dos campos mínimos de cada etapa.
- Verificar links/referências, coerência das dependências e compatibilidade com
  Roadmap, baseline pós-V0.3 e arquitetura v1.0.
- Executar review proporcional segundo A8, incluindo os pontos classificados
  como profundos.
- Executar `git diff --check`.
- Executar o gate autoritativo:
  `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1`.
- Confirmar que o diff de P0 não contém mudança funcional nem alteração do
  escopo protegido.

## Documentation Impact

- Criar o plano executável da release em `tasks/plans/`.
- Ao encerrar P0 com evidência elegível, atualizar somente os registros
  operacionais aplicáveis, incluindo `PROJECT_STATE.md`, o contrato arquivado
  em `tasks/completed/`, `tasks/current.md` e a métrica A7.
- Referenciar fontes existentes sem duplicar desnecessariamente Roadmap,
  requisitos, ADRs ou políticas.

## Done When

- O escopo oficial da V0.4 foi auditado e a baseline V0.3 foi considerada.
- Todos os requisitos V0.4 possuem rastreabilidade e todas as exclusões estão
  explícitas.
- A release está decomposta em etapas coerentes, com dependências e ordem
  justificadas e, para cada etapa, objetivo, escopo, risco, critérios,
  verificações, documentação, recomendação A7, review A8 e evidência de
  encerramento.
- A estratégia de testes/gates, os pontos de review profundo e os critérios de
  promoção final estão definidos.
- O plano está registrado em fonte durável apropriada e passou pelo review e
  pelas verificações aplicáveis, inclusive gate autoritativo GREEN.
- Nenhum código funcional ou escopo protegido foi alterado e nenhuma etapa
  funcional da V0.4 foi autorizada ou iniciada.
- P0 foi arquivada com evidência elegível e `tasks/current.md` retornou a
  `Status: NO_TASK_AUTHORIZED`.

## Resultado do planejamento

O plano durável `tasks/plans/v04-release-execution-plan.md` audita a baseline
executável V0.3, registra sete divergências tratadas sem alterar fontes
congeladas e cobre integralmente o escopo V0.4 em uma matriz de rastreabilidade.
A release foi decomposta em nove etapas: contratos de métricas; serviços
analíticos e drill-down; dashboard; consulta/detalhe/histórico; integridade e
logs; backup/restore; operação Windows; hardening/acessibilidade/`BCR-1`; e
piloto/promoção.

As dependências não têm ciclo e mantêm backup antes do piloto, serviços antes
das telas dependentes, semântica antes das queries e candidato GREEN antes de
dados copiados. S2, S5, S6, S8 e S9 exigem inicialmente plano persistente A4.
Cada etapa tem objetivo, valor, Expected/Protected Scope, exclusões,
dependências, tamanho/risco, modelo/reasoning, review A8, testes,
documentação, aceite, evidência, encerramento e decisão A4.

O plano separa zero válido de `sem dados`, define numerador, denominador,
período, filtros, inclusões/exclusões, drill-down e interpretação das métricas;
preserva os thresholds vigentes do `BCR-1`; trata o invariant checker como
comando operacional read-only; diferencia backup, restore, teste de restore e
documentação; incorpora acessibilidade em cada tela e novamente no hardening;
e define piloto controlado, rollback e gate final de promoção.

## Review, verificação e evidência de encerramento

Review A8: `profundo`, adequado a P0 L/medium e ao impacto sobre toda a release.
Resultado: **APPROVED**, sem finding Blocker, Major ou Minor. A revisão cobriu
baseline, requisitos, rastreabilidade, exclusões, semântica, dependências,
modelos/reasoning, riscos, verificabilidade, promoção e Protected Scope. Uma
imprecisão foi corrigida antes do gate: `RN-057` usa tentativa inicial válida
para “questões realizadas”; `RN-056` inclui rascunhos, ativas e arquivadas; e
`BCR-2` permaneceu fora do gate V0.4.

- Validação focada: 29 termos obrigatórios presentes, nove etapas encontradas e
  campos mínimos de cada etapa inspecionados; nenhuma dependência circular ou
  requisito órfão.
- `git diff --check`: aprovado; o novo arquivo não rastreado também foi
  verificado separadamente sem erro de whitespace.
- Gate autoritativo inicial: GREEN na primeira passagem, exit code 0, 99 s.
- Testes: 280 aprovados em 55,56 s; cobertura global 87%.
- Demais checks: lock/runtime, três perfis, rastreabilidade, migrations
  inesperadas e banco vazio, formatação, Ruff, mypy, cobertura de domínio,
  detect-secrets e `pip-audit` aprovados.
- P0/P1 aplicável aberto: nenhum.

Métricas A7: modelo `gpt-5` conforme identidade disponível; reasoning,
início, duração total e cotas não foram capturados e permanecem `unknown`;
uma tentativa; gate first pass `true`; baixo retrabalho documental pela
correção semântica pré-gate; sem escalonamento ou incidente de infraestrutura.

## Estado final e não ações

P0 produziu somente documentação e registros operacionais. Nenhum código
Django, template/CSS funcional, teste funcional, migration, schema, regra de
negócio, baseline/tag V0.3, Architecture v1.0, Skill, política ou gate foi
alterado. Nenhuma funcionalidade V0.4 foi implementada; nenhuma etapa funcional
foi iniciada ou autorizada. Não houve commit, push, tag, release, Project
Starter, piloto ou uso de dados reais.

A primeira etapa recomendada é `V0.4-S1 — Contratos de métricas e exemplos de
reconciliação`, com `Terra High` e review profundo. Essa recomendação não é
autorização; qualquer execução exige um novo contrato `AUTHORIZED` em sessão
futura.
