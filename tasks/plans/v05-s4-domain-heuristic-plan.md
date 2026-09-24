# Plano A4: V0.5-S4 DOM-HEUR-1.0

- ID da tarefa relacionada: `V0.5-S4` (`tasks/current.md`)
- Status: COMPLETED
- Objetivo: decompor e auditar a implementação da policy pura de domínio na granularidade de Question.
- Premissas: `tasks/current.md` é a autoridade; S4 não persiste resultados nem executa agregação operacional S5.

## Auditoria normativa e de fatos

- `docs/Caderno_de_Erros_Inteligente_Etapa_5_Regras_de_Negocio.md` §11.2–11.4 e RN-068–080 define DOM-HEUR-1.0, componentes, elegibilidade, teto de recuperação, confiança/atualidade, rótulos e agregação hierárquica. §14 RN-097–100 define ausência e insuficiência; §15 contém exemplos.
- `docs/Caderno_de_Erros_Inteligente_Etapa_3_Requisitos_Funcionais.md` RF-057–061 requer valor ou insuficiência, confiança separada, explicação/versionamento e distingue domínio de ciclo concluído.
- `tasks/plans/v05-release-execution-plan.md` §§4–5 e `docs/V0.5_S1_Contratos_Normativos_e_Invariantes.md` §§1–3 congelam histórico, Workspace, exclusão, revisão prospectiva, semântica de Attempts e Reviews.
- Attempts têm `status`, `attempt_type`, `occurred_at`, `perceived_ease`, `question_revision`, `review` e `replaces_attempt` em `src/modules/attempts/models.py`; `src/modules/attempts/selectors.py::resolve_attempt_chain` valida a cadeia e sua ponta terminal. Apenas fatos `VALID` entram na policy; em uma cadeia de correção a ponta válida é o fato corrente e ancestrais anulados ficam fora dos componentes.
- `QuestionRevision` é imutável e cada Attempt referencia a revisão apresentada; `Attempt` valida `is_correct` contra essa revisão. A policy usa o resultado histórico já validado, sem reinterpretar tentativas após correção prospectiva.
- Reviews/Cycles preservam estágio, resultado, datas e estados em `src/modules/reviews/models.py`; `src/modules/reviews/policies.py` e selectors definem temporalidade. Somente Attempts válidas concluídas fornecem sinais: ciclo/Review aberta não é tentativa. Atraso e estado da fila não são novos pesos; estágio correto alimenta progressão conforme §11.2.
- `src/modules/questions/deletion.py::PermanentQuestionDeletionService` remove o agregado e seus fatos dependentes; a policy recebe apenas a Question ainda disponível e não reconstrói fatos da auditoria sanitizada.
- Classificação/categoria de erro é mantida por `src/modules/errors/models.py` e selectors; não integra a fórmula DOM-HEUR-1.0.
- A taxonomia Workspace-scoped está em `src/modules/taxonomy/models.py`; dificuldade de Question não é fator. `perceived_ease` é o sinal separado de fluência explicitamente definido no contrato normativo.
- Migration: **NO**. O escopo implementa valores imutáveis de entrada, cálculo puro e explicações em memória; não requer coluna, tabela, índice, backfill, snapshot ou persistência própria. A decisão decorre do escopo e do schema auditado, sem usar `UNLIKELY` como conclusão automática.

## Decomposição

1. Criar API tipada de entrada por Question e vetor explícito de componentes; validar datas, ordenação, valores e ausência de evidência.
2. Implementar cálculo puro e versionado: `Aq`, `Pq`, `Fq`, `Eq`, fórmula `M_q`, teto pós-erro, confiança `C_q`, suficiência/estado e explicações estruturadas com códigos semânticos.
3. Criar adaptador de evidências que consuma fatos existentes de uma Question, preservando Workspace, ponta válida de replacement, revisão histórica e Review concluída; não consultar tabelas no núcleo matemático.
4. Cobrir fórmula, bordas, insuficiência, confiança, explicações, dificuldade, anulação/substituição, revisões, Reviews abertas/concluídas, exclusão e determinismo em testes focados; executar regressões pertinentes S2B/S2C/S2D/Reviews/analytics.
5. Revisar diff e documentos, executar A8 deep e gate autoritativo; registrar evidência e só então fechar S4.

## Riscos, invariantes e critérios

- Não contar Attempt `VOIDED` nem duplicar ancestrais e ponta de replacement; ordenar fatos de forma determinística.
- Não trocar o gabarito histórico da revisão usada; não recuperar fatos depois de exclusão permanente.
- Não confundir ciclo operacional ou agenda com Domain; não usar `difficulty`, categorias, atraso ou fila como fator sem regra expressa.
- Domínio ausente/insuficiente não vira zero, resultado ruim, erro ou prioridade. Confidence e suficiência permanecem dimensões distintas.
- Domínio hierárquico seguirá as equações normativas de peso igual por Question e `C_h`, se exposto como função matemática pura; nenhuma consulta/agregação operacional S5 será incluída.
- As decisões humanas de 2026-09-24 resolveram as condições normativas de `C_q`, suficiência/maturity de Question, ciclo efetivo de `Eq` e reinício da base após erro em REVIEW. `RN-077` permanece inalterada e exclusiva a `C_h`; não foi identificada lacuna normativa restante dentro do escopo S4. A data de avaliação de recência permanece entrada explícita do núcleo puro.

## Human Decision Gate 1 — resolvido: RN-077 e `C_q`

- **Decisão humana registrada em 2026-09-24:** não aplicar `40` nem outro valor de `C_h` a `C_q`; manter confidence e suficiência separadas; não criar threshold numérico para suficiência; usar apenas condições estruturais já normatizadas e não inferir a condição caso elas não a definam. `C_q` mantém sua fórmula vigente.
- **Status: APROVADO.** O limite `40` permanece exclusivo de `C_h`; `C_q` segue a fórmula vigente, sem decidir suficiência. Não alterar RN-077.

## Decisão humana 2 — suficiência estrutural por Question

- **Status: APROVADO.** Sem Attempts `VALID`, retornar `NO_DATA`. Com somente Attempt `INITIAL` válida, calcular `M_q` e manter maturity `PROVISIONAL`. A evidência torna-se estruturalmente suficiente quando há ao menos uma `INITIAL` válida e uma `REVIEW` válida posterior; então maturity é `ESTABLISHED`/não provisória. Não chamar esse estado de final. A suficiência não depende de `C_q`. `DOMINATED` é independente e obedece somente a RN-079.

## Decisão humana 3 — ciclo efetivo para `Eq`

- **Status: APROVADO.** Usar o ciclo efetivo mais recente da Question, incluindo `COMPLETED`; excluir ciclo `SUPERSEDED` ou inválido à projeção corrente. Incluir `SUSPENDED` somente enquanto o ciclo for estruturalmente válido e não superseded; ciclos suspensos não contêm Review pendente executável, mas seus Attempts concluídos do ciclo podem contribuir para `Eq`. Contar somente Attempts REVIEW `VALID` ligadas ao ciclo selecionado; nunca somar erros entre ciclos. Selecionar de forma determinística por `(started_at, created_at, id)` decrescente. Se não houver ciclo e houver menos de duas Attempts válidas, `Eq=50` pela regra existente.

## Decisão humana 4 — base `C_q` após erro em REVIEW

- **Status: APROVADO.** Erro válido de REVIEW torna-se nova âncora de “desde o último erro” e reinicia a base em 20. A partir dali, etapa tentada D1/D7/D14/D30 eleva a base para 40/60/80/100. Aplicar o fator de atualidade normalmente; não preservar base de ciclo anterior após novo erro.

## Continuação após as decisões humanas

- As decisões acima liberam implementação da policy completa e seu adaptador read-only. Nenhuma persistência, estado operacional de reopening, Priority ou S5 é autorizada.
- Migration permanece **NO** para o escopo puro.

## Resultado A4 e implementação S4

- Migration **NO**; o escopo persiste somente código e teste, sem resultado, snapshot, coluna ou tabela de Domain.
- `src/modules/domain/policy.py` contém a API pura versionada, componentes exatos, fórmula/teto de `M_q`, bandas RN-078, confidence vigente, suficiência/maturity aprovada, mastery exclusivamente RN-079 e agregação hierárquica matemática RN-074/075. Não recebe modelos, difficulty nem consultas.
- `src/modules/domain/selectors.py` é adaptador read-only Workspace-scoped para Question ativa; reutiliza `valid_attempts`, `eligible_reviews` e temporalidade vigente, escolhe ciclo não superseded mais recente incluindo completed/suspended válidos, registra fatos descartados e não executa mutações. A seleção tem quantidade constante de consultas por Question.
- `tests/test_domain_policy.py` cobre fórmula, limites, determinismo independente do contexto Decimal, suficiência separada de confidence, reset de confidence após erro, ciclo `Eq`, RN-079 e agregação sem dupla contagem/omissão de `C_q` ausente. A evidência ORM cobre isolamento/Question ativa, INITIAL provisional, ciclo completed e exclusão de ciclo superseded.
- Migration audit: `makemigrations --check --dry-run` observou `No changes detected`; banco vazio migrou com schema existente, sem migration S4.
- Regressão selecionada de S4/S2B/S2C/S2D/Reviews/Attempts/analytics/classificações/taxonomia: **191 passed** antes do último ajuste de agregação. Testes focados após o ajuste: **32 passed**; `ruff check`, `ruff format`, mypy focado e `git diff --check` aprovados.
- A8 deep: **APPROVED**, Blocker 0, Major 0, Minor 0 abertos. Revisão final conferiu fidelidade às fórmulas RN-068–079, fontes históricas efetivas e replacement, revisão histórica, não uso de difficulty/categorias/atraso como sinal, ausência de threshold `C_q`, determinismo/limites, explicações de incluídos/excluídos, agregação por Question, consulta sem N+1 dentro da avaliação de uma Question, ausência de persistência/UI/Priority/reopening operacional e nenhum início de S5.
- Durante a revisão foram corrigidos: escopo das evidências explicativas de `Eq` por ciclo; seleção de ciclo completed versus superseded; precisão Decimal externa nos pesos de `Aq`; preservação dos IDs que justificam `Eq=50` abaixo de duas tentativas; e omissão silenciosa de `C_q` ausente em `Cob_h`.
- Gate autoritativo: tentativa 1 GREEN (454 passed); após ajuste identificado por A8, tentativa 2 final GREEN, exit **0**, **455 passed** em 178.44 s, cobertura global **87%**, validação de cobertura de domínio, perfis, migrations, Ruff, mypy, detect-secrets e pip-audit aprovados; `No known vulnerabilities found`; duração observada **217.8 s**. Nenhuma tentativa RED. Permaneceram dois `ResourceWarning` de conexão SQLite em teste S2D existente, sem falhas. Duração total da sessão e quotas A7: `unknown`, não estimadas.

## Condição de saída

As decisões humanas dos Gates 1–4 foram aprovadas e registradas acima. A4 e V0.5-S4 estão concluídas e comprovadas em `quality/v05-s4-domain-heuristic-result.md`. Este plano não autoriza commit, push, tag, release nem início de S5.
