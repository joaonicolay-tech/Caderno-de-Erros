# Task Contract

Status: COMPLETED

## Identification

- Task ID: `V0.5-S4`
- Product version: `V0.5`
- Stage: S4
- Name: `DOM-HEUR-1.0` — política pura de Domain
- Task type: implementação de policy determinística e explicável
- Size: L
- Risk: high
- Migration: `UNLIKELY`; não criar migration salvo decisão humana posterior após A4
- Modelo recomendado: GPT-6 Luna; reasoning `xHigh`
- Review: A8 deep

## Goal

Definir e implementar a policy pura e versionada `DOM-HEUR-1.0` para calcular e explicar uma estimativa/índice de domínio de aprendizagem na granularidade de Question, com confidence e suficiência de evidência separadas do valor de Domain.

## Context and Authority

- Baseline concluído: V0.4.4, V0.5-P0, S1, S2A, S2B, S2C, S2D e S3. S3 acrescentou UI/gestão sem alterar semanticamente as regras S2A–S2D.
- Fontes normativas: `tasks/plans/v05-release-execution-plan.md`, `docs/V0.5_S1_Contratos_Normativos_e_Invariantes.md`, código, migrations, testes e evidências concluídas S2A–S2D/S3.
- Domain significa estimativa/índice de domínio de aprendizagem; não criar entidade/taxonomia paralela para Discipline, Subject, Category ou ErrorCategory.
- S4 deve consumir apenas fatos válidos autorizados pelas fontes. Distinguir fato, projeção, confidence, suficiência e explicação.
- Attempt `VOIDED` não é evidência corrente; respeitar a ponta efetiva `VALID` via selector/policy existente. Preservar o vínculo histórico de cada Attempt à QuestionRevision usada à época. Question permanentemente excluída não fornece fatos correntes.

## Required A4 Before Functional Edits

Criar e fechar `tasks/plans/v05-s4-domain-heuristic-plan.md` antes da primeira edição funcional. Auditar Attempts e efetividade S2B, QuestionRevision/correctness, fatos de Review, classifications, analytics, discipline/subject/subsubject, semântica temporal/review, policies, selectors, tests e regras canônicas S1/P0. Mapear precisamente os fatos consumíveis pela policy e justificar migration a partir da auditoria de schema.

Se qualquer elemento essencial não tiver regra canônica — em especial fórmula, pesos, thresholds, treatment of Review, suficiência, confidence ou agregação — não inventar uma regra nem iniciar sua implementação dependente. Registrar a lacuna, evidência, opções, impacto e recomendação técnica separada; parar para decisão humana (`BLOCKED_HUMAN_DECISION`). Se A4 indicar que persistência é necessária, parar antes de implementá-la para revisão do escopo.

## Acceptance Criteria

- Definir uma API pública pequena e tipada para evidence input, avaliação da policy, resultado e explicação; o núcleo não contém queries Django.
- Usar representação/vetor intermediário explícito com somente fatores autorizados; evitar passar modelos Django inteiros quando valores simples bastarem.
- Implementar fórmula, thresholds, classificação/estado, confidence, critério explícito de suficiência, comportamento de evidência insuficiente e explicação estruturada conforme regras aprovadas, com versão `DOM-HEUR-1.0` explícita.
- Evidência insuficiente deve ser distinguível de cálculo disponível, confidence limitada, zero domínio, erro e prioridade; não fabricar certeza nem converter ausência de dados em domínio zero/ruim ou prioridade alta.
- Determinismo: entradas iguais produzem Domain, confidence, suficiência e explicação iguais. Validar limites e evitar instabilidade numérica de thresholds quando aplicável.
- Difficulty não pesa o cálculo; mudar somente difficulty não altera Domain.
- Respeitar Attempt efetiva e replacement chain S2B sem dupla contagem; preservar avaliação histórica pela revision da Attempt S2C; exclusão S2D não reintroduz fatos.
- Auditar Review e temporalidade sem presumir equivalência INITIAL/REVIEW, decay ou pesos de D1/D7/D14/D30. ErrorCategory não vira fator quantitativo sem regra expressa.
- Definir semântica matemática pura de agregação para uso futuro em subsubject (se existente), subject e discipline, quando exigida para tornar a policy aplicável; explicitar unidade de evidência e impedir dupla contagem. Não implementar agregação operacional S5.
- Explicações computáveis identificam evidências/fatores usados, confidence e razão de suficiência/insuficiência; não depender de texto livre genérico no núcleo.
- Cobrir exemplos normativos, limites semanticamente aplicáveis, determinismo, invariantes, dificuldade, effective Attempt/replacement, revisão histórica e explicações em testes determinísticos.

## Expected Scope

- A4 e evidência de encerramento S4 em `quality/v05-s4-domain-heuristic-result.md`.
- Implementação pure-core tipada e, se necessário, builder/adaptador de evidência usando selectors existentes, com testes focados e regressões relacionadas.
- Atualizar `PROJECT_STATE.md`, registrar métricas A7 observáveis e arquivar S4 em `tasks/completed/` somente após todos os critérios e evidências de conclusão serem comprovados.

## Protected Scope and Constraints

- S4 é policy pura. Não implementar persistência/snapshot de Domain, migration, tabela, campo em Question, UI, dashboard, integração final de páginas, export/import, reopening operacional ou prioridade de estudo (`PRI-HEUR-1.0`).
- Não reescrever Attempts, Reviews, ErrorClassification, QuestionRevision ou analytics históricos.
- Não criar taxonomia, sinal, ponderação, threshold ou desempate por intuição. Sem ML, embeddings, LLM, serviço externo ou calibração com dados reais.
- Reutilizar selectors/policies existentes e evitar N+1 na construção em lote; não colocar queries no núcleo matemático.
- Não antecipar S5 ou etapas posteriores. S5+ permanecem não autorizadas.

## Verification

- Executar testes focados e regressões relevantes de Attempts/S2B/S2C/Reviews/analytics/classifications/question lifecycle; incluir S3 somente se interfaces/imports comuns forem tocados.
- Revisão A8 deep obrigatória: `APPROVED`, Blocker 0, Major 0, cobrindo fidelidade normativa, fórmula, fontes e vetores, effective Attempts, revisions históricas, exclusão de difficulty, confidence, suficiência, thresholds, determinismo, explicações, agregação, performance e ausência de persistência/UI/Priority/reopening/S5 leakage.
- Executar `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1` e registrar tentativas, RED real, retries, incidentes, first-pass e resultado observado.
- `git diff --check` não substitui testes ou gate.

## Documentation Impact

Persistir plano A4, resultado S4, métricas A7 observáveis, atualização de `PROJECT_STATE.md` e arquivamento do contrato conforme padrão do projeto. Registrar migration decision, fontes normativas, fatos/vetor, fórmula, thresholds, confidence, suficiência, agregação, explicação, invariantes, performance, testes, A8 e gate.

## Done When

- A4 fechado antes das mudanças funcionais e nenhuma regra essencial inventada; lacunas canônicas resolvidas por decisão humana antes de prosseguir.
- Policy `DOM-HEUR-1.0` pura, tipada, determinística, explicável e coberta por testes; migration comprovadamente desnecessária ou decisão de escopo revisada antes de qualquer persistência.
- S2B/S2C/S2D respeitadas, dificuldade excluída, confidence e suficiência distintas, agregação conceitual definida quando exigida, sem Priority, reopening operacional, persistência ou UI.
- Testes focados e regressões aplicáveis GREEN; A8 deep APPROVED com Blocker 0/Major 0; gate autoritativo GREEN; evidência persistida e métricas A7 observáveis registradas.
- S4 arquivada e `tasks/current.md` retornado a `NO_TASK_AUTHORIZED`; S5+ continuam não autorizadas. Nenhuma etapa posterior iniciada.

## Closure Evidence

- Plano A4: `tasks/plans/v05-s4-domain-heuristic-plan.md`, COMPLETED; três decisões humanas de 2026-09-24 registradas. RN-077 não alterada; migration NO.
- Implementação e evidência: `src/modules/domain/policy.py`, `src/modules/domain/selectors.py`, `tests/test_domain_policy.py`, `tests/test_domain_evidence.py` e `quality/v05-s4-domain-heuristic-result.md`.
- Testes focados finais: 32 passed; regressões selecionadas: 191 passed; gate autoritativo final GREEN na tentativa 2, exit 0, 455 passed, 87% de cobertura, duração 217.8 s. A primeira execução GREEN contou 454 testes antes de ajuste identificado por A8.
- A8 deep APPROVED, Blocker 0, Major 0, Minor 0. `git diff --check` aprovado.
- `PROJECT_STATE.md` atualizado. `tasks/current.md` retorna a `NO_TASK_AUTHORIZED`; S5+ permanecem não autorizadas.
- Sem commit, push, tag, release, UI, persistência, migration, Priority ou reopening operacional.
