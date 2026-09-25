# Plano A4 — V0.5-S6 PRI-HEUR-1.0

- Tarefa: `V0.5-S6`; autoridade durante a execução: `tasks/current.md`, então `AUTHORIZED`; contrato concluído arquivado em `tasks/completed/v05-s6-priority-heuristic.md`.
- Status: `COMPLETED`; A4 concluído antes da implementação e decisões humanas abaixo aplicadas.
- Escopo: recomendação derivada, explicável e opcional por **Subject/Assunto**. O contrato e `RF-062`/`RN-081–084` não autorizam ranking de Discipline, Subsubject ou Question.
- Baseline observado: `main`; `HEAD = origin/main = 43f7a38c2e78d31ef10226beb8d99af63271a2d0`; somente `tasks/current.md` modificado no início; `git diff --check` exit 0. O commit contém os artefatos de encerramento S5; `PROJECT_STATE.md` ainda descreve o estado anterior à autorização S6, enquanto o contrato corrente autoriza S6. Essa divergência administrativa não amplia o escopo.

## Checklist de fontes e fatos

| Item | Auditoria e consequência |
| --- | --- |
| Normas e OD03 | `docs/Caderno_de_Erros_Inteligente_Etapa_5_Regras_de_Negocio.md` §12, RN-081–084 e RN-097–100 fixa fatores/pesos/elegibilidade, mas deixa `RN-ABR-003` aberto. `docs/V0.5_S1_Contratos_Normativos_e_Invariantes.md` registra OD03 `DEFERRED_TO_S6`; `tasks/plans/v05-release-execution-plan.md` exige OD03 antes de testes de prioridade. `PT-ABR-008`, `FL-ABR-010` e `RD-ABR-007` também deixam janelas/desempate abertos. `RF-062`, `FL-017` e CT-070–072 não os fecham. Busca no repositório não encontrou decisão aprovada posterior. |
| Domain S5 | `src/modules/domain/services.py::hierarchy_domain` é o seletor oficial para `M_h`/`C_h`, com `current_domains` em lote e `aggregate_hierarchy` de S4. `src/modules/domain/selectors.py::domain_inputs` usa apenas Questions ativas, Attempts válidas e data civil do Workspace. Planos/resultados S4/S5 consultados; fórmulas, suficiência, mastery e eventos ficam protegidos. Não chamar avaliação unitária em loop. |
| Taxonomy e Questions | `Subject` e `Question.subject` são Workspace-scoped; filtrar Questions `ACTIVE` por Subject corrente. Archived saem do conjunto corrente. Permanent delete S2D remove o agregado; auditoria sanitizada não é evidência. |
| Attempts e Reviews | `analytics.selectors.valid_attempts` seleciona `VALID` e tipo REVIEW com Review do mesmo Workspace; a cadeia S2B mantém somente a ponta válida. `Attempt.local_date` e `is_correct` preservam fato histórico ligado à revisão S2C, sem recalcular acerto. R deve contar Questions distintas, nunca número de erros, e excluir INITIAL, VOIDED/predecessores e Reviews planejadas. O significado operacional exato de "recorrente" para PRI ainda precisa de decisão. |
| Atraso e timezone | `reviews.policies.ReviewStatusPolicy` e `analytics.selectors.eligible_reviews` dão a semântica vigente de OVERDUE sobre Review PENDING, ciclo ACTIVE e Question ACTIVE; `review_reference_date` usa `Workspace.timezone_name`. Contar Questions distintas, mesmo se houver mais de uma Review. Não alterar fila/scheduling. |
| Analytics histórico | `analytics.read_models.AnalyticsPeriod`, `AttemptFilters`, `Ratio` e `analytics.selectors.valid_attempts` permitem períodos e acerto/erro histórico read-only. Não há definição aprovada de métrica, janelas, mínimo comparável ou ausência de baseline para D. Os percentuais existentes não fixam D automaticamente. |
| UI e testes | `reviews.views.queue`/`reviews.urls.py` e template da fila são operacionais separados; taxonomy e questions têm rotas de navegação. `tests/test_v05_s5_domain.py`, `tests/test_domain_policy.py`, `tests/test_domain_evidence.py`, `tests/test_analytics.py` e testes de Review/Attempt/taxonomy fornecem fixtures e regressões. UI PRI exigirá rota/template mínimos e estados acessíveis após a decisão. |
| Batching | S5 mediu 8 queries para 40 Questions no batch e 11 por Subject de 10 Questions na fixture registrada em `quality/v05-s5-domain-application-result.md`. S6 deverá medir uma lista representativa de Subjects, com captura de queries e sem N+1 por Subject. |
| Schema/migration | Modelos/migrations atuais contêm Question, Attempt, Review, Subject e dados S5 suficientes para projeção derivada. **Migration: NO para o desenho read-only/on-demand auditado**, sem snapshot, cache, campo de score ou plano persistido. Se decisão humana exigir schema, parar e reavaliar antes de qualquer migration. |

## Desenho condicionado à decisão

1. Entrada tipada com Subject, `M_h`, `C_h`, contagens distintas de Questions ativas/atrasadas, evidência temporal R/D e data local; núcleo puro sem ORM. Resultado tipado com policy `PRI-HEUR-1.0`, fatores W/O/R/D, score integral, códigos de explicação e estado de insuficiência.
2. `W = 100 - M_h`; `O` usa a proporção de Questions ativas com OVERDUE, limitada a 100. `R` e `D` seguem as decisões aprovadas abaixo. Fórmula fixa `0.40W + 0.30O + 0.20R + 0.10D`; somente exibição arredonda. `C_h < 40` ou componente necessário indisponível retorna `COLLECT_MORE_EVIDENCE`, fora do ranking; `C_h = 40` é elegível se os componentes estiverem disponíveis.
3. Adaptador em lote por Workspace seleciona Subjects e Questions ativas, consome Domain S5 e fatos válidos; separa a fila operacional. Ranking usa score integral DESC e UUID do Subject ASC para empate exato. GET não escreve em Question, Review, ReviewCycle, MasteryStateEvent, Domain ou plano de estudo.
4. UI mínima consulta serviço read-only e mostra fatores, explicação, versão, confiança/evidência, ausência/insuficiência e liberdade de escolher outro conteúdo. Sem redesign geral.

## V05-OD03 — Human Decision Gate

**Histórico:** `BLOCKED_HUMAN_DECISION` após a primeira auditoria, antes da implementação. As lacunas abaixo descrevem o estado anterior à decisão de 2026-09-24; não são requisitos ainda abertos.

### R — recorrência

- Fixo: proporção de **Questions distintas** com erro de **REVIEW** recorrente dentro do período de análise; Attempts efetivas, Question ativa e Workspace corrente.
- Lacunas: extensão e fronteiras inclusivas/exclusivas do período; se "recorrente" exige duas falhas REVIEW na janela, falhas em ciclos diferentes ou outra definição; denominador da proporção e tratamento quando não há observação suficiente.
- Opção de janela civil curta (ex.: 30 dias): responde mais rapidamente, mas oscila e perde erros espaçados. Opção mais longa (ex.: 90 dias): mais amostra, porém sinais antigos permanecem. Janela móvel por número de Reviews evita dias arbitrários, mas muda a comparabilidade entre Subjects. **Números são exemplos, não defaults aprovados.**
- Exemplo: duas falhas REVIEW da mesma Question contam no máximo uma Question no numerador; uma falha INITIAL não conta. Decisão adicional define se as duas falhas precisam estar dentro da janela e se pertencem ao mesmo ciclo.
- Recomendação técnica para decisão: preferir período civil explícito com boundary documentado, pois data local já é fato disponível, e definir recorrência/denominador separadamente. Não escolher duração sem aprovação.

### D — queda recente

- Fixo: redução positiva entre desempenho histórico comparável e desempenho recente, limitada a 100. D não é envelhecimento de confidence, atraso, quantidade de Reviews nem queda de `C_h`.
- Lacunas: métrica, janela recente, baseline histórico, população comparável, mínimo de observações e resultado sem baseline. `RN-099` impede transformar ausência silenciosamente em zero.
- Métrica candidata: taxa de acerto de Attempts REVIEW efetivas da mesma população de Questions. Alternativa: desempenho por Question distinta para evitar que uma Question com muitas tentativas domine a média. As métricas podem divergir: se Q1 tem quatro acertos e Q2 um erro, taxa por Attempt = 80%, taxa média por Question = 50%; a decisão é normativa.
- Opção temporal: duas janelas civis adjacentes e não sobrepostas (comparação compreensível, mas amostra pode faltar); opção por últimas N observações válidas versus N anteriores (amostra estável, duração variável); opção de baseline acumulado anterior (mais estável, mistura épocas antigas). Nenhuma duração ou N foi aprovado.
- Recomendação técnica para decisão: exigir períodos não sobrepostos, mesmo tipo de Attempt e população comparável, com mínimo explícito; quando baseline faltar, emitir estado de insuficiência ou regra neutra **explicitamente aprovada**, nunca zero silencioso.

### Empate exato

- Fixo: score integral para comparar e ranking determinístico; `FL-ABR-010` e `PT-ABR-008` não escolhem desempate.
- Alternativas: maior W (favorece domínio baixo), maior O (favorece urgência), maior confiança (favorece evidência), nome normalizado ou ID estável (ordem reproduzível sem preferência pedagógica). Exemplo: Subjects A e B com score 50 podem trocar de posição conforme critério. Escolher um fator como desempate cria prioridade secundária que a fórmula não expressa.
- Recomendação técnica para decisão: se nenhuma preferência pedagógica adicional for desejada, usar chave estável explicitamente aprovada e documentar colisões de nome; se houver preferência pedagógica, aprovar ordem de critérios e sua justificativa. Não aplicar ordem alfabética/ID por conveniência sem decisão.

### Ausência de R/D

`RN-099` permite valor neutro explícito ou impedir cálculo conforme regra específica, mas a regra específica PRI não existe. A decisão deve fixar se cada componente ausente torna o Subject insuficiente, impede Priority inteira ou recebe valor neutro aprovado, com explicação correspondente. O exemplo neutro de facilidade em RN-099 pertence a outra métrica e não se transfere para R/D.

## Decisões humanas aprovadas em 2026-09-24

Estas decisões novas fecham `V05-OD03`, `PT-ABR-008` e a parte operacional de `RN-ABR-003` para S6. Não são atribuídas retroativamente aos documentos originais.

1. **R:** janela civil inclusiva `[evaluation_date - 89 dias, evaluation_date]` no fuso do Workspace. Usar `occurred_at` convertido para data local, apenas Questions ACTIVE e Attempts REVIEW efetivas VALID. Denominador: Questions distintas com pelo menos duas REVIEWs na janela. Numerador: dentre elas, Questions distintas com pelo menos dois erros REVIEW na janela. Exigir no mínimo três Questions no denominador; abaixo disso R é `UNAVAILABLE`, não zero. Com amostra suficiente e nenhuma recorrência, R=0.
2. **D:** janelas inclusivas não sobrepostas `RECENT=[evaluation_date - 29, evaluation_date]` e `BASELINE=[evaluation_date - 59, evaluation_date - 30]`, em dias civis locais. Somente Questions ACTIVE com ao menos uma REVIEW VALID efetiva em **ambas**. Para cada Question, calcular taxa de acerto REVIEW em cada janela; fazer média das taxas por Question com pesos iguais. `D=min(100, max(0, baseline_performance - recent_performance))`. Exigir no mínimo três Questions comparáveis; abaixo disso D é `UNAVAILABLE`. Desempenho igual ou melhor com amostra suficiente produz D=0.
3. **Desempate:** score integral DESC, depois `subject_id` UUID imutável ASC somente como chave técnica. Nenhum componente, confiança, nome ou quantidade de atrasos ganha preferência secundária.
4. **Ausência:** qualquer componente necessário indisponível impede score e ranking normais; retornar `COLLECT_MORE_EVIDENCE` com reason codes que identifiquem R/D ou outro fato ausente. Não usar 0, 50 ou renormalizar 40/30/20/10. Distinguir zero observado de indisponível.
5. **Arquitetura:** `Migration: NO`; policy derivada/on-demand/read-only, sem snapshot, campo persistido, alteração da Review Queue, scheduling, Domain ou Mastery. S7+ não autorizadas.

## Matriz de verificação após liberação

- Núcleo: W em 0/intermediário/100, Decimal e `M_h` ausente; O em zero/parcial/todas, Question distinta, archive e fuso; vetores independentes 40/30/20/10, limites e precisão antes de arredondar.
- R/D: janelas e boundaries aprovados, falhas REVIEW recorrentes por Question, INITIAL/VOIDED fora, S2C prospectivo, sem baseline/amostra e melhora/estabilidade/queda.
- Elegibilidade e explicação: `C_h=39.99` versus `40`, confidence ausente, motivos W/O/R/D, múltiplos fatores, estado vazio/insuficiente e Review overdue ainda na queue.
- Integração: Workspace isolado, S2B/S2C/S2D, GET read-only, batching/query count, UI teclado/foco/labels, regressões Domain S4/S5, Reviews, Attempts, taxonomy e analytics.
- Depois: A8 deep com Blocker 0/Major 0, gate `scripts/quality.ps1` GREEN, evidence em `quality/`, atualização de `PROJECT_STATE.md` e arquivamento somente quando Done When for comprovado.

## Condição de saída atual

A4 de fontes/schema/fronteiras e decisões humanas concluído. Implementação S6, A8 deep e gate final GREEN comprovados em `quality/v05-s6-priority-heuristic-result.md`. S7+ não executadas; sem commit, push, tag ou release.
