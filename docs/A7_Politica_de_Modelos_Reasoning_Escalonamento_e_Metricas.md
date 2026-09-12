# A7 — Política inicial de modelos, reasoning, escalonamento e métricas

## Finalidade e limites

Esta é a versão inicial, observável e calibrável da política operacional para
execuções deste repositório. Ela orienta a escolha de modelo e de reasoning,
sem alterar a autorização funcional: `tasks/current.md` continua definindo
Goal, escopo e risco da tarefa. Disponibilidade de modelos, cotas, perfil,
sandbox e aprovações pertencem ao ambiente da execução e não são configurados
por este documento.

O princípio é usar o modelo menos dispendioso que seja plausivelmente
suficiente para concluir a tarefa com qualidade aceitável e baixo retrabalho.
Uma escolha inicial não é promessa de consumo nem substitui decomposição,
critérios claros, revisão ou gate.

## Escolha inicial de modelo

A decisão considera, em conjunto, tamanho, risco, tipo de trabalho,
dificuldade real, invariantes, contexto necessário, ferramentas, testes e
evidência comparável já registrada. Portanto, `task_size != model`.

| Situação inicial | Candidato | Observação |
| --- | --- | --- |
| XS, baixo risco, resultado mecânico e inequívoco | Luna, se disponível e suficiente | Low ou Medium; texto, ajuste local ou mudança documental trivial. |
| S/M, baixo ou médio risco | Terra | Medium é o centro de gravidade para documentação, planejamento e implementação coesa moderada. |
| M/L com raciocínio substancial | Terra High ou Sol Medium | Escolher pelo tipo de invariantes e pela evidência, não só pelo tamanho. |
| Alta criticidade ou dificuldade comprovada | Sol High | Para integridade, migration sensível, concorrência, arquitetura estrutural ou debugging difícil. |
| Exceção concretamente justificada | Astra | Não compensa prompt fraco, contexto excessivo, critérios vagos ou falta de decomposição. |

Uma tarefa pequena e crítica pode exigir escolha forte; uma tarefa grande e
mecânica pode ser decomposta e executada economicamente. XL deve ser
decomposta antes de se concluir que precisa de modelo maior.

## Reasoning, separadamente do modelo

- **Low:** somente para trabalho realmente mecânico e inequívoco.
- **Medium:** padrão para a maior parte do trabalho normal do projeto.
- **High:** múltiplas invariantes, ambiguidade estrutural, arquitetura complexa,
  migrations sensíveis, debugging difícil ou risco elevado.

High não é consequência automática de duração ou tamanho. A decisão de
reasoning é registrada independente da decisão de modelo.

## Escalonamento por evidência

O fluxo é `escolha inicial adequada → execução → avaliação → escalonamento
somente se necessário`. Não se reinicia automaticamente uma tarefa com modelo
superior. Escalonar exige evidência registrável, como tentativa anterior que
não resolveu o problema, erro arquitetural, invariantes ainda conflitantes,
complexidade real maior que a prevista ou revisão que detecte risco relevante.

Quando ocorrer, registrar `escalated_from`, `escalated_to` e a evidência. Uma
falha de infraestrutura, ambiente ou contrato não é evidência contra um modelo.

## Risco e autonomia

- **low:** alta autonomia dentro do contrato autorizado;
- **medium:** autonomia no repositório com verificações fortes;
- **high:** implementação delimitada e revisão mais intensa;
- **critical:** preferir análise, plano e revisão antes de side effects
  importantes.

Isto é orientação operacional, não regra automática de sandbox ou aprovação.

## Métricas versionadas

O registro canônico é `quality/operational-execution-metrics.jsonl`. JSONL foi
escolhido por ser versionável, append-friendly, legível linha a linha e simples
de consultar sem banco, ferramenta externa ou dashboard. Cada linha é um objeto
independente com `schema_version` e `record_type`.

Registros `execution` usam, quando conhecidos: `task_id`, `stage`, `task_type`,
`task_size`, `risk`, `model`, `reasoning`, `started_at`, `duration`,
`quota_5h_delta`, `quota_weekly_delta`, `files_changed`, `tests_run`,
`gate_result`, `gate_first_pass`, `attempt_number`, `rework`, `accepted`,
`escalated_from`, `escalated_to`, `infrastructure_incident` e `notes`.
Campos desconhecidos recebem `"unknown"` (ou `null` quando o tipo exigir);
eles nunca são estimados pela duração.

Todo valor manual ou inferido inclui proveniência em `sources` e, quando
necessário, uma limitação de precisão. Dados de quota são externos e podem ser
adicionados manualmente depois; porcentagens possivelmente arredondadas não
devem ser tratadas como medidas exatas. Duração também não é proxy confiável de
consumo: tipo de tarefa, ferramentas, testes, gates, retrabalho, contexto,
arquivos e investigação afetam o resultado.

`record_type: "incident"` separa incidentes de `model_task`,
`infrastructure`, `environment` e `scope_contract`. Assim, falhas de sandbox
ou de contrato não entram em first-pass failure, retrabalho funcional ou taxa
de escalonamento de modelo.

O registro é prospectivo: ao encerrar uma tarefa, adicionar uma linha com os
fatos disponíveis após o gate, sem preencher lacunas. Métricas técnicas já
versionadas em `quality/` e `PROJECT_STATE.md` continuam sendo suas fontes
primárias; o JSONL as referencia, não as substitui.

## Base inicial e calibração

Os benchmarks A1–A6 existentes no JSONL distinguem dados informados
manualmente pelo usuário, evidência de arquivo e lacunas. A4 não recebe
métricas de modelo/cota inventadas. O incidente ACL de sandbox anterior à A7 é
classificado como infraestrutura, e o bloqueio administrativo de bootstrap é
classificado como contrato/processo; nenhum é falha de modelo ou retrabalho
funcional.

Possíveis leituras futuras incluem first-pass success por tipo/tamanho,
retrabalho, taxa de escalonamento, duração, quota, Pareto de causas e
incidentes. Não há dashboard nesta etapa. Ajustar esta política requer
evidência comparável suficiente, mudança na oferta/limites dos modelos,
evidência consistente de qualidade ou retrabalho, ou mudança significativa no
projeto — sem limiar numérico arbitrário.

## Casos de calibração conceitual

| Caso | Decisão inicial | Motivo |
| --- | --- | --- |
| A — correção documental XS/low | Luna Low/Medium, se suficiente | Resultado localizado e inequívoco. |
| B — planejamento M/low | Terra Medium | Trabalho normal, com raciocínio moderado e baixo impacto. |
| C — feature Django M/medium | Terra Medium | Implementação coesa com validação forte; elevar apenas por evidência. |
| D — migration de integridade L/high | Sol High | Integridade e reversibilidade exigem raciocínio e revisão mais altos. |
| E — tarefa XL | Decompor antes; escolher por subparte | XL não determina modelo e não deve ser compensado por escala. |
| F — Terra Medium falhou duas vezes em M | Escalar com registro da causa | Duas tentativas são evidência para reavaliar reasoning/modelo, não para reinício cego. |

## Integração mínima ao workflow

As Skills existentes permanecem fontes de fluxo, não cópias desta política.
`start-task` pode reconhecer tamanho e risco já presentes no contrato;
`implement-current-task` aplica a escolha como orientação não autorizativa;
`run-quality-gate` fornece o resultado técnico; e `finish-task` exige a
evidência antes do registro final. Nenhuma Skill é transformada em sistema de
telemetria nem exige alteração para esta política funcionar.

Restrições temporárias da sessão de autorização não devem ser persistidas como
restrições duráveis da tarefa. `Done When` deve descrever a conclusão real; a
fase administrativa de autorização é distinta da execução, mas o contrato
persistido precisa continuar executável.
