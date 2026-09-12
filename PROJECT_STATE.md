# Project State

Versão atual: V0.3 (promovida)
Situação da versão: Etapas 0–5 concluídas; promoção formal registrada em 10 de setembro de 2026.
Etapa atual: nenhuma etapa de implementação autorizada.
Status da etapa atual: E5 concluída; V0.3 **PROMOVIDA**.

Etapas concluídas:

- V0.2 — Etapa 0 — Saneamento e Baseline da V0.2;
- V0.2 — Etapa 1 — Taxonomia e Migrations;
- V0.2 — Etapa 2 — Gestão e Interface da Taxonomia;
- V0.2 — Etapa 3 — Catálogo de Origem;
- V0.2 — Etapa 4 — Catálogo de Questões;
- V0.2 — Etapa 5 — Rascunho, Ativação e Cadastro Rápido;
- V0.2 — Etapa 6 — Detalhe, Edição Versionada e Arquivamento de Questões;
- V0.2 — Etapa 7 — Listagem, Busca e Filtros de Conteúdo;
- V0.2 — Etapa 8 — Fixture, Acessibilidade, Backup, Integração e Regressão;
- V0.3 — Etapa 0 — Saneamento, Fronteira e Rastreabilidade;
- V0.3 — Etapa 1 — Fundação de Aprendizagem: Schema, Constraints e Políticas Puras;
- V0.3 — Etapa 2 — Resposta Inicial Protegida, Contexto Transitório e Finalização Inicial Atômica.
- V0.3 — Etapa 3 — Política e Conclusão de Revisões.
- V0.3 — Etapa 4 — Fila Derivada, Linha do Tempo, Diagnóstico Auditável e Suspensão por Arquivamento;
- V0.3 — Etapa 5 — Integração, Migração, Regressão, Carga/Concorrência e Promoção.

Melhoria operacional:
Etapa 6 — adoção definitiva do novo fluxo operacional concluída.

Adaptação operacional pós-V0.3 / pré-V0.4:
A2, A3, A4, A5 e A6 concluídas. `tasks/current.md` é a autoridade da tarefa corrente;
`tasks/plans/` é opcional e prospectivo; `tasks/completed/` preserva o
histórico. As quatro Skills essenciais estão em `.agents/skills/`. Nenhuma
tarefa está autorizada; A7 exige nova autorização formal.

Baseline protegida:
`v0.2.0` (`a756b6d`)

Último gate:
GREEN — V0.3 Etapa 5, exit code 0.

Testes:
280 aprovados; regressões do candidato ADR-013 e os CTs automatizados
aplicáveis à E5 estão GREEN.

Coverage:
87% global; todos os módulos de domínio/regra do manifesto E5 acima de 80%.

Bloqueadores:
Nenhum P0/P1 aplicável aberto para a V0.3.

P0/P1 aplicável aberto:
Nenhum.

Evidência de encerramento:
`quality/v03-stage5-validation-result.md` registra CT-107 PASS e CT-125 PASS
(9/10, 90%). ADR-014 documenta a aceitação limitada da evidência histórica de
CT-125 sem alegar nova sessão humana pós-ADR-013. As migrations E1 e os
manifestos E1–E4 permanecem intactos.

Próximo objetivo autorizado:
Somente planejamento futuro da V0.4 em nova autorização formal; V0.4 não foi
iniciada.

ADRs relevantes:

ADR-001
ADR-002
ADR-003
ADR-008
ADR-010
ADR-011
ADR-012

## Atualização histórica — ADR-013 (10 de setembro de 2026)

Esta atualização substitui o estado operacional anterior a partir deste ponto.

Situação da versão: a validação E5 anterior permanece evidência histórica,
mas não é suficiente para promoção após a correção arquitetural ADR-013.
Etapa atual: V0.3 — correção autorizada: ciclo de revisão na ativação da
questão. Status: ADR-013 aprovada; implementação corretiva ainda não iniciada;
V0.3 **NÃO PROMOVIDA**.

O próximo objetivo autorizado é exclusivamente schema, migration, serviços,
correção comprovada de mojibake, testes e gate da regra ADR-013. Não autoriza
promoção, V0.4, commit, push, tag ou release.

`CT-125` preserva o resultado humano histórico de 9/10 (90%), mas a mudança
estrutural requer reteste do candidato final; não há PASS inferido. Os CTs
funcionais/estruturais afetados também exigem regressão contra a nova regra.
As migrations E1 e manifestos E1–E4 continuam protegidos.

ADRs relevantes adicionais: ADR-013.

## Encerramento histórico — ADR-013 (10 de setembro de 2026)

A correção ADR-013 foi implementada e validada pelo gate autoritativo: GREEN,
exit code 0, 280 testes aprovados e 87% de cobertura global. A migration
`reviews.0002_activation_review_cycle` evolui apenas o schema e referencia a
revisão de origem dos ciclos existentes; não cria ciclos retroativos para
questões `ACTIVE` históricas.

As três transições efetivas para `ACTIVE` agora criam atomicamente um ciclo de
origem `QUESTION_ACTIVATION` e uma D1 no próximo dia civil do Workspace, sem
`Attempt` artificial. Acerto e erro INITIAL preservam essa D1; somente erro de
Review a reinicia. Arquivamento, fila e timeline foram cobertos para a âncora
de ativação sem tentativa.

`CT-125` mantém a evidência humana histórica de 9/10 e permanece PENDENTE de
reteste no candidato corrigido. V0.3 continua **NÃO PROMOVIDA**; não houve
promoção, V0.4, commit, push, tag ou release. Os manifestos E1–E4 e suas
migrations históricas permanecem preservados. A próxima etapa exige nova
autorização formal em novo chat.
## Fechamento final — ADR-014 (10 de setembro de 2026)

ADR-014 aceitou a evidência humana histórica completa de CT-125 para este
fechamento, sem reescrever ADR-013 ou alegar reteste. CT-107/BCR-1 está PASS
por medição real; CT-125 está PASS por 9/10 (90%). O gate final retornou exit
code 0, não restam P0/P1 aplicáveis e V0.3 está **PROMOVIDA**. V0.4 permanece
não iniciada e exige nova autorização formal.

## Encerramento — A5 (11 de setembro de 2026)

A5 verificou Codex CLI 0.153.0 e a documentação oficial vigente. Nenhum
`.codex/config.toml` ou arquivo de rules foi criado: `AGENTS.md` já é descoberto
nativamente, `PROJECT_STATE.md` não deve virar fallback universal e rules são
experimentais e não agregariam uma fronteira além da sandbox/aprovações atuais.
`.codex/auth.json` passou a ser ignorado explicitamente. O gate autoritativo
ficou GREEN, exit code 0, com 280 testes e 87% de cobertura. A6 não foi iniciada.

## Encerramento — A6 (11 de setembro de 2026)

A6 criou quatro Skills de projeto concisas em `.agents/skills/`: início de
tarefa autorizada, implementação do contrato corrente, execução/interpretação
do gate existente e validação de encerramento. O Codex 0.153.0 descobriu as
quatro pelo caminho de repositório e a validação estrutural aprovou todos os
`SKILL.md`. Os cinco dry-runs operacionais passaram. O gate autoritativo ficou
GREEN na primeira execução, exit code 0, com 280 testes e 87% de cobertura.
Não houve mudança funcional, migration ou início de A7/V0.4.

## Encerramento — A7 (12 de setembro de 2026)

A7 formalizou uma política inicial e calibrável de seleção de modelo,
reasoning e escalonamento por evidência em
`docs/A7_Politica_de_Modelos_Reasoning_Escalonamento_e_Metricas.md`. As
métricas operacionais têm registro versionado, append-friendly e com
proveniência em `quality/operational-execution-metrics.jsonl`; valores
desconhecidos permanecem explícitos e dados de quota externos não são
estimados.

O gate autoritativo elegível ficou GREEN no contexto de rede autorizado, exit
code 0, com 280 testes e 87% de cobertura. A primeira execução no sandbox foi
inconclusiva apenas no `pip-audit` por `WinError 10013`, classificado como
infraestrutura e não como falha de modelo ou retrabalho funcional. Não houve
mudança em Django, migrations, gate, baseline, configuração pessoal ou Skills.
A8 e V0.4 não foram iniciadas; não há tarefa autorizada.

## Encerramento — A8 (12 de setembro de 2026)

A8 formalizou a política principal em `docs/review/code-review.md`: revisão
proporcional e orientada a risco, focada em findings concretos, com prioridade,
profundidades, severidades, decisões de aprovação e tratamento de escopo. O
índice passou a apontar para essa fonte; as Skills existentes permaneceram
inalteradas porque já se integram ao fluxo sem duplicar a política.

O gate autoritativo ficou GREEN na primeira execução, exit code 0, com 280
testes aprovados e 87% de cobertura. Não houve mudança de Django, migration,
schema, gate, configuração pessoal ou Skills. A9 e V0.4 não foram iniciadas;
não há tarefa autorizada.

## Encerramento - A9 (12 de setembro de 2026)

O piloto real auditou e corrigiu o `README.md` raiz: ele ainda apresentava V0.2
e o ciclo de aprendizagem/revisao como futuro, embora V0.3 esteja promovida.
O README agora descreve as capacidades V0.3 comprovadas e informa que V0.4 nao
foi iniciada. A revisao A8 leve foi APPROVED, sem findings, e o gate
autoritativo terminou GREEN na primeira execucao, exit code 0, com 280 testes
aprovados e 87% de cobertura.

As quatro Skills A6 foram uteis e suficientes como passos independentes:
`start-task` delimitou autoridade e arvore preexistente; `implement-current-task`
sustentou a alteracao minima; `run-quality-gate` preservou a evidencia tecnica;
e `finish-task` orientou o encerramento. A3 evitou leitura excessiva; A7
permitiu registro append-only sem estimativas; e A8 proporcionou revisao leve
sem burocracia adicional. Nao houve conflito de fontes nem workaround. A
duplicacao residual entre AGENTS, A2/A3 e Skills permaneceu limitada a papeis
distintos. Candidatas para A10: revisar a redacao historica acumulada de
`PROJECT_STATE.md` e padronizar captura externa de duracao, reasoning e quotas.
Nenhuma alteracao arquitetural foi feita nesta A9. Nao houve mudanca funcional,
migration, alteracao de Skills/politicas/gate, inicio de A10 ou V0.4, commit,
push, tag ou release. Nao ha tarefa autorizada.
