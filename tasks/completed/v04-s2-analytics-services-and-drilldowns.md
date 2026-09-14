# Task Contract

Status: COMPLETED

## Identification

- Task ID: V0.4-S2
- Product version: V0.4
- Stage: S2 — Serviços analíticos e drill-down
- Task type: product implementation / analytics services / read models
- Size: L
- Risk: high
- Recommended execution profile: GPT-5.6 Sol, Medium reasoning
- Expected review: deep
- Persistent A4 plan: required before implementation, conforme V0.4-P0

## Goal

Implementar a camada analítica de leitura da V0.4 com base estrita nos
contratos semânticos aprovados em S1, fornecendo serviços, selectors, read
models e DTOs reutilizáveis para o dashboard S3 e seus drill-downs, sem lógica
de negócio em views ou templates.

Os resultados devem ser corretos, reconciliáveis, isolados por Workspace,
determinísticos, testáveis, eficientes no baseline esperado e compatíveis com
os contratos S1.

## Context

- `docs/V0.4_S1_Contratos_de_Metricas_e_Reconciliacao.md` é a autoridade sobre
  o significado das métricas. S2 decide como calcular, mas não redefine o que
  elas significam.
- `tasks/plans/v04-release-execution-plan.md` define a decomposição e as
  fronteiras da release sem substituir a autoridade normativa de S1.
- Antes da implementação, criar ou ativar plano persistente A4 que decomponha
  o trabalho conforme o repositório real, incluindo contratos/read models,
  atividade, revisão, agregações, drill-down, reconciliação e
  performance/verificação. O plano não amplia este contrato.
- Se a implementação revelar impossibilidade ou contradição em S1, registrar a
  divergência, não reinterpretar a regra silenciosamente e interromper apenas a
  parte afetada quando necessário.

## Acceptance Criteria

- Há leituras read-only para questões cadastradas, questões realizadas,
  tentativas, acertos, erros, taxa de acerto, revisões concluídas hoje,
  revisões devidas, atrasadas e futuras, desempenho por disciplina e assunto,
  frequência por categoria de erro, situação das questões no ciclo e resíduos
  explicitamente previstos por S1.
- Cada métrica que exige drill-down permite recuperar deterministicamente o
  conjunto subjacente com os mesmos filtros, período e referência, e a
  contagem do conjunto reconcilia com o agregado.
- Os exemplos determinísticos de S1 tornam-se evidência executável quando
  apropriado e comprovam a reconciliação entre cadastradas e realizadas,
  realizadas e tentativas relevantes, acertos e erros, taxa, estados de
  revisão, disciplina/assunto e categorias com seus resíduos.
- Todas as leituras, joins, relacionamentos indiretos, subqueries e
  drill-downs respeitam o Workspace corrente. Testes negativos detectam
  qualquer agregação ou vazamento cross-workspace, tratado como finding
  crítico.
- Analytics de eventos usa `Attempt.local_date` quando previsto em S1; a
  situação das pendências usa a data civil vigente do Workspace. Nenhum cálculo
  substitui essas regras por `created_at__date` ou UTC bruto.
- Revisões elegíveis respeitam `< hoje` como atrasada, `= hoje` como devida e
  `> hoje` como futura, além do evento S1 para concluída hoje, archive,
  suspensão, `ReviewCycle` e estados existentes, sem criar novo estado.
- Frequência por categoria preserva o resíduo sem classificação previsto em
  S1, sem ocultá-lo ou inventar uma categoria “Outros”.
- Agregações por disciplina e assunto usam a taxonomia atual definida em S1,
  preservam resíduos sem vínculo e oferecem agrupamento e drill-down coerentes.
- A interface interna de leitura é clara e reutilizável por S3, com tipos ou
  read models explícitos quando agregarem valor, sem API HTTP pública.
- O desenho evita N+1, queries por linha, agregações repetidas,
  materialização desnecessária e loops Python inadequados; drill-downs têm
  ordering determinístico e paginação quando aplicável, sem antecipar o
  hardening BCR-1 de S8.

## Expected Scope

- Criar ou ajustar selectors e serviços analíticos de leitura.
- Criar DTOs e read models.
- Criar queries ORM, agregações, filtros temporais e drill-downs de leitura
  exigidos por S1.
- Implementar e testar isolamento por Workspace e reconciliação entre
  agregados e conjuntos subjacentes.
- Criar testes unitários, de integração e de query, fixtures mínimas e
  instrumentação proporcional de desempenho de leitura.
- Atualizar documentação técnica, plano, estado e registros operacionais apenas
  conforme trabalho e conclusão reais; registrar métricas A7 e aplicar review
  A8 profundo.

## Protected Scope

- Significado dos contratos S1 e regras normativas existentes.
- Dashboard S3, templates, UI e CSS.
- Schema e migrations; se uma migration for realmente necessária, não criá-la
  automaticamente: registrar a necessidade, avaliar o impacto, interromper a
  parte dependente e solicitar nova decisão e autorização.
- Regras de negócio de escrita, ciclos de revisão e estados existentes.
- V0.3 promovida, `docs/PROJECT_DEVELOPMENT_ARCHITECTURE_V1.md`, Skills,
  políticas A7/A8 e `scripts/quality.ps1`.
- Cache, snapshots, escrita de analytics, categorias pessoais e itens V0.5+.
- S3 e qualquer etapa posterior.

## Constraints

- Preservar os universos, denominadores, filtros, datas, timezone, resíduos e
  regras de reconciliação definidos em S1.
- Não aceitar números isoladamente plausíveis que sejam incompatíveis entre
  si ou com seus drill-downs.
- Reutilizar `ReviewStatusPolicy` e as fronteiras aprovadas; Review pendente ou
  situação temporal não é tentativa, e REVIEW não conta como INITIAL.
- Arquivamento preserva fatos históricos e remove apenas a pendência
  executável conforme S1; correções de classificação usam a projeção atual sem
  duplicar ocorrências.
- Evitar dicionários anônimos espalhados, lógica repetida em views, queries
  duplicadas, cálculo em template e interface pública prematura.
- Não fazer commit, push, tag ou release sem autorização expressa.

## Verification

- Cobrir proporcionalmente os exemplos S1, zero/empty, dois Workspaces,
  múltiplas tentativas, initial versus review, revisões, timezone e bordas de
  data, archive/suspensão, disciplina/assunto, categorias e resíduos,
  drill-down, ordering e queries críticas.
- Os testes devem falhar quando universo ou denominador estiver errado; não
  testar somente o formato dos DTOs.
- Auditar explicitamente cross-workspace aggregation, joins e subqueries sem
  escopo, vazamento em drill-down, double counting, denominator mismatch,
  timezone incorreto, N+1 e divergência entre agregado e detalhe.
- Executar review A8 profundo. A conclusão exige `APPROVED`, sem finding
  Blocker ou Major aberto.
- Executar `git diff --check` e o gate autoritativo:
  `powershell -NoProfile -ExecutionPolicy Bypass -File
  .\scripts\quality.ps1`, ambos aprovados.

## Documentation Impact

Atualizar somente a documentação técnica e a rastreabilidade realmente
afetadas. Na conclusão, encerrar o plano A4, atualizar o estado aplicável,
arquivar S2 e registrar a execução real nas métricas A7; cotas indisponíveis
permanecem `unknown` e bootstrap não se mistura à execução.

## Done When

- Todos os contratos S1 aplicáveis têm implementação de leitura e reconciliam
  com os exemplos determinísticos e respectivos drill-downs.
- Isolamento por Workspace, datas/timezone, estados de revisão,
  disciplina/assunto, categorias e resíduos estão corretos e cobertos por
  testes capazes de detectar erro semântico real.
- A API interna read-only para S3 está estável, sem lógica analítica em UI e
  sem N+1 óbvio ou arquitetura de query inadequada.
- O plano A4 está encerrado, os testes focados estão GREEN, o review profundo
  está `APPROVED`, `git diff --check` está aprovado e o gate autoritativo está
  GREEN, sem P0/P1 aplicável aberto.
- S2 está arquivada, registros de estado e métricas A7 refletem evidência real
  e `tasks/current.md` retornou a `NO_TASK_AUTHORIZED`.
- S3 permanece não autorizada e não iniciada.

## Evidência de encerramento

- Plano A4: `tasks/plans/v04-s2-analytics-services.md`, encerrado como
  `COMPLETED`.
- Implementação: fachada `AnalyticsService`, DTOs/read models e selectors
  Workspace-scoped em `src/modules/analytics/`; reutilização explícita de
  `ReviewStatusPolicy` para a data civil de referência.
- Contratos S1: atividade, RN-057, revisões, disciplina, assunto, categorias,
  resíduo sem classificação, situação de ciclo e drill-downs reconciliados.
- Testes novos: 5 em `tests/test_analytics.py`; 27 testes focados aprovados em
  8,24 s, incluindo regressões da fila, policy e fundação de aprendizagem.
- Query baseline: desempenho e categorias observados com 2 queries cada nos
  testes; sem N+1 ou ordering instável encontrado.
- Review A8 profundo: **APPROVED**, sem Blocker ou Major aberto. O review
  reforçou filtros de Workspace em relacionamentos indiretos antes do gate.
- `git diff --check`: aprovado antes do gate.
- Gate autoritativo: GREEN na repetição de evidência, exit code 0, 285 testes
  aprovados em 62,62 s, 87% de cobertura global; analytics selectors 90% e
  services 95%; duração total do gate 90,9 s. Migrations, banco vazio,
  formatação, Ruff, mypy, cobertura de domínio, detect-secrets e pip-audit
  aprovados.
- A primeira execução do gate percorreu todos os controles e terminou com a
  mensagem de sucesso em 100,8 s, mas a sessão assíncrona não preservou o campo
  numérico do exit code; houve repetição apenas para captura elegível.
- Nenhuma migration, alteração de schema, regra de escrita, view, template,
  CSS, dashboard S3, commit, push, tag ou release foi criada ou executada.
