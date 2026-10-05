# A4 — V1.0-S8R1 Timezone Semantics Remediation

Status: PLANNING_COMPLETE / HUMAN_DECISION_REQUIRED
Execution authorization: NOT AUTHORIZED
V1.0-S8R1: AUTHORIZED / PLANNING
V1.0-S8: AUTHORIZED / PAUSED / RESUMABLE AFTER S8R1
REAL_DATA: NO
PILOT_EXECUTION: NOT YET AUTHORIZED
S9–S10: NOT AUTHORIZED

## Objetivo e fontes

Permitir mudança futura Acre→São Paulo sem reescrever fatos históricos, sem falsos findings do checker e sem reinterpretação indevida de evidência de Priority. A autorização atual cobre somente contrato, investigação, comparação, matrizes e critérios; não libera código/testes funcionais/schema/migration, gate ou execução real. Modelo/esforço humano autorizado: GPT-6.1 Sol High, runtime não verificável. A8 futura: deep.

Baseline observada: HEAD == origin/main local == dcccb8950a7752d03461665e0a4952c8a9bc663b. Inventário exato dos oito paths iniciais em `quality/v10-s8r1-initial-paths.json`; nenhum foi descartado/sobrescrito. Conteúdo anterior de current/PROJECT_STATE conservado integralmente em seção histórica; os demais seis artefatos S8 são imutáveis nesta tarefa. Manter TIMEZONE_CORRECTION_REQUIRES_SEPARATE_REMEDIATION e toda cronologia S8, inclusive os resultados pré-existentes 25/0,34/34,FK0,SQLite ok,W01 único e SOURCE fisicamente inalterada como HISTÓRICOS, não revalidação atual.

Fontes decisivas: RN-002/003/004/005/095 em `docs/Caderno_de_Erros_Inteligente_Etapa_5_Regras_de_Negocio.md`; ADR-013; `docs/V1.0_S1_Contratos_e_Compatibilidade.md`; `docs/V0.4_S5_Invariant_Checker.md`; `docs/CEI_EXPORT_1_0.md`; decisão humana V05-OD03 em `tasks/plans/v05-s6-priority-heuristic-plan.md`; fontes executáveis e testes referenciados no relatório de investigação. A2/A3 e AGENTS aplicados; autorização humana expressa permite planejamento na mesma sessão administrativa.

Artefatos complementares: `quality/v10-s8r1-timezone-investigation.md`, `tasks/plans/v10-s8r1-timezone-surfaces.md` e `tasks/plans/v10-s8r1-synthetic-test-matrix.md`. Estes contêm rastreabilidade e oráculos; o A4 não inventa resultados futuros.

## Causa raiz e invariantes

REV-004 SQL já usa Attempt.local_date para agenda ancorada; complemento Python para QUESTION_ACTIVATION/MANUAL reconverte started_at com Workspace.timezone_name ATUAL. Review/ReviewCycle não guardam timezone da criação. Origin Attempt de MANUAL não prova o timezone da inclusão/reabertura; schedule change e audit posteriores também não provam. Não há reconstrução exata universal com as colunas atuais.

Priority converte occurred_at de REVIEW antiga no ZoneInfo atual antes de R/D; sua decisão anterior aprovada explicitamente usa essa base. Fronteiras 29/30,59/60,89/90 podem mudar amostra/score/eligibilidade mesmo com today igual. Domain usa local_date histórica corretamente; seu aging e agenda corrente usam today atual legitimamente. Correção REVIEW acrescenta um terceiro risco: nova substituta herda timezone antigo, mas schedule usa timezone atual, criando discrepância de data da âncora após a troca.

Invariantes propostas para aprovação:

1. Troca isolada preserva todas as linhas históricas, IDs/FKs, UTC, timezone da Attempt/change, local_date, first_due_date/current_due_date, eventos, versões e resultados de acerto. Nenhum repair/backfill retroativo.
2. Regras de criação/scheduling permanecem REV-FIXA-1.0: novos cálculos no contexto autorizado do comando, dias civis sucessivos +1/+7/+14/+30, erro reinicia D1, sem compressão ou timezone do servidor.
3. Checker nunca usa um contexto atual mutável como prova de data civil de um fato antigo. Onde há âncora/contexto independente, comparação exata; onde falta contexto, comportamento exige H1 explícita.
4. Priority, sob H2, usa data própria histórica para membership de evidência; today/O/aging/confiança continuam correntes. Com mesmo evaluated_on e mesmos inputs, invariância de R/D; com today diferente, deltas prospectivos identificados. Não exigir score global idêntico em todos os instantes.
5. Regra canônica compartilhada entre checker, projeção CEI pre-DML, import pós-carga e restore/recovery. Nenhum fork permissivo só numa interface.
6. GET/validação continuam sem DML e nenhum evento novo de mastery/repair; nenhuma ausência convertida em zero; fatores, pesos, thresholds e ordem técnica protegidos.

## Estratégias A/B/C

| Dimensão | A — contexto do próprio fato | B — contexto adicional só futuro | C — regra independente de timezone |
| --- | --- | --- | --- |
| Correctness | Exata para Attempts e agendas ancoradas; local_date validada por ATT-002. Não resolve origem inaugural sem contexto. | Exata para origem futura quando guarda contexto consistente; legado continua sem prova e sem backfill. | Exata para estrutura/sequência/transições/relações; data inaugural exata não pode ser provada usando somente a própria due date. |
| Compatibilidade | Campos V0.5/V1 existentes; mudança do adapter Priority altera resultados em boundaries, exige H2. | Novos produtores/leitores precisam preservar contexto no transporte/restauração; não inventar contexto antigo. | Pode manter schema/formato; mudar cobertura histórica do checker exige autorização explícita H1 e documentação futura. |
| Churn | Baixo no adapter Priority; já aplicada por ATT-002/SQL ancorado. | Médio/alto: writers de ativação/manual/reopen, schema ou estrutura durável, export/import/restore/upgrade e testes. | Baixo/médio em checker e docs, mas custo semântico alto se retirar uma validação temporal existente. |
| Migration | NO para A com campos atuais. | Campo em ReviewCycle: YES; outra representação: decisão de desenho necessária, não presumir NO. Nunca backfill fabricado. | NO se apenas validação; não garante exatidão perdida. |
| Risco | Usar timezone de âncora antiga como contexto MANUAL seria incorreto. Mistura de datas de fusos distintos é intencional como fato civil, deve ser documentada. | Quebrar allowlist CEI/compatibilidade; capturar instante e timezone em momentos diferentes; informação presente só em logs; falsas inferências de legado. | Falso senso de segurança/aceitação de agenda corrompida; não passar coverage reduzida por exatidão universal. |
| Falso positivo | Evita FP por troca nos fatos com contexto. Não resolve FP de inaugurais. | Evita FP futuro com contexto; não elimina FP legado sem regra adicional. | Remove FP por mudança apenas nas condições expressamente enfraquecidas; não deve aceitar qualquer data. |
| Falso negativo | Não amplia quando contexto validado; fallback ao fuso atual/âncora errada pode mascarar erro. | Negativos devem detectar contexto inválido/due date errada; legado permanece limitado. | Remover comparação ou aceitar intervalo de dias cria FN adicionais; grau precisa de aprovação e teste. |
| Checker | Manter SQL+ATT-002 e usar âncora apropriada. Não usar first_due_date-1 como prova circular. | Comparar started_at com contexto futuro armazenado e devido histórico; distinguir legado sem contexto. | Preservar todas regras realmente estruturais; eventual resultado não verificável precisa contrato/outcome explícito. |
| Priority | Recomendada: membership por Attempt.local_date, preservando today novo e fórmula; decisão sobre identificação/errata é H2. | Não precisa de campo adicional para Priority ordinária: Attempt já guarda contexto. | Janelas por UTC absoluto/N observações mudam conceito civil, pesos temporais e contrato; não recomendadas aqui. |

**Recomendação técnica:** A para fatos com contexto e Priority; B prospectiva para contexto inaugural caso seja exigida validação exata futura; C somente para regras já semanticamente estruturais e eventual limitação LEGADA autorizada. Essa combinação não é implementação aprovada. A sozinha não resolve tudo; B não recupera passado; C não pode prometer detectar toda corrupção de data sem informação independente. Preferência NO MIGRATION/NO FORMAT CHANGE permanece; ainda não há solução demonstrada que atenda simultaneamente essa preferência e exatidão inaugural universal.

Não recomendadas: fuso atual retroativo; timezone da Attempt origin antiga em MANUAL; deduzir fuso por due date; procurar dados reais para escolher fallback; alterar agenda histórica; retirar REV-004 inteiro; usar intervalo plausível como prova de correctness; reutilizar AuditEvent genérico sem verificar enum/constraints/CEI; usar logs transitórios como fonte normativa.

## Decisões humanas necessárias antes da execução

| ID | Decisão concreta | Recomendação para avaliação |
| --- | --- | --- |
| H1 | Qual garantia exigir para datas inaugurais LEGADAS sem contexto? Aceitar limitação explícita de validação, ou manter exigência exata e reconhecer que o legado permanece sem prova? | Registrar incapacidade de validar data original, conservar checks estruturais e comparação exata nas âncoras confiáveis. Isso altera cobertura/contrato do checker; não implementar sem aprovação. Se resultado não verificável deve ser finding/WARNING/outcome separado ou pode integrar 25/0, definir explicitamente — nenhum PASS por omissão. |
| H2 | Substituir a base temporal aprovada de Priority (occurred_at no fuso atual) pela local_date histórica? Manter PRI-HEUR-1.0 por errata controlada ou adotar identificador novo segundo RN-095? | Aprovar A para R/D, preservando fórmula/limiares; registrar semântica e vigência. Não editar decisão anterior como se sempre tivesse sido essa regra. |
| H3 | Para NOVA replacement após troca, preservar timezone da cadeia e agenda na data da substituta, ou usar timezone atual consistentemente para ambos? | Preferir contexto atual coerente para um evento novo, sujeito a contrato de correção e decisão humana; manter predecessor intocado. Avaliar se herança antiga é intenção normativa. Não escolher só mudar checker para tolerar discrepância. |
| H4 | Persistir contexto inaugural para fatos futuros? Autorizar exceção de schema/migration/CEI caso o desenho exato exija? | Se exatidão futura for essencial, analisar B explícita e portável. Campo em ReviewCycle exige migration e análise da versão/allowlist CEI. Se exceção não for aceita, formalizar limitação do checker futuro sob H1, sem prometer exatidão. |

Essas decisões não estão respondidas pelo simples pedido de PLANEJAMENTO. Não é pedido de acesso real ou autorização de PILOT. Enquanto pendentes: HUMAN_DECISION_REQUIRED; parar após entregar o A4. Uma nova autorização funcional deve persistir as escolhas e o escopo antes de editar código. Não iniciar A8 deep ou subagente de execução nesta fase.

## Plano condicional de execução futura

1. Confirmar nova autorização, H1–H4 e baseline/working tree; preservar todos os artefatos/RED históricos. Confirmar runtime/modelo autorizado quando disponível e isolamento de testes. Não usar SOURCE.
2. Reproduzir RED em banco sintético: REV-004 inaugural na virada, Priority com today igual e correction REVIEW com timezone misto. Preservar evidência antes de qualquer fix; construir vetores independentes da implementação.
3. Aplicar somente desenho aprovado no código canônico. Priority pode projetar local_date armazenada em lote; remover relocalização somente após H2. Checker mantém SQL/transições/âncoras e implementa H1/H4 sem validação circular. Corrections/writers somente se H3/H4 aprovadas.
4. Testar T1–T14 e compatibilidade CEI/restore/upgrade, incluindo negativos antes de DML e concurrency/contexto consistente. Nenhuma escrita real, repair ou alteração de configuração pessoal.
5. Reconciliar somente documentação formal expressamente autorizada; registrar errata/decisão nova com cronologia. Se schema/CEI/migration emergir fora de H4, STOP/HUMAN_DECISION_REQUIRED antes da mudança.
6. Gate integral GREEN observado, A8 deep APPROVED, critério de dados históricos preservados e checker saudável conforme contrato decidido. Encerrar S8R1 somente então; retomada de S8 e eventual troca real continuam exigindo autorização específica.

Potenciais fontes de implementação futura: operations/integrity.py e testes checker; priority/services.py e testes integração/policy; attempts/corrections.py, reviews/reconstruction.py e respectivos testes se H3; writers/models/data_management se H4. Não é allowlist de edição nesta sessão. Migrations, schema, CEI, policy version e contratos congelados são STOP até decisão explícita. Não alterar REV-FIXA-1.0, D1/D7/D14/D30, fórmulas de Domain ou dependências.

## Matriz sintética e compatibilidade

T1–T10 cobrem vazio, Attempt virada, Review inaugural, schedule change, fases, Priority, Domain, REV-004, preservação e uso futuro SP. T11 cobre replacement/reconstrução; T12 V0.5/V1/CEI/backup/restore/upgrade; T13 concurrency; T14 bordas adicionais. Instantes fixos e oráculos detalhados no arquivo de matriz. Mesmas datas e diferentes datas explicitamente separadas, meia-noite 03:00Z SP e 05:00Z Acre nessa data; não extrapolar offsets a todo histórico IANA. Nenhum teste funcional executado no A4.

| Fronteira de compatibilidade | Impacto previsto / decisão |
| --- | --- |
| V0.5/V1 existentes | A lê campos existentes sem reescrita. Legado inaugural tem limitação H1; upgrade não inventa contexto. |
| CEI-EXPORT-1.0 | A/C sem campo adicional podem manter formato; todos os validadores devem compartilhar a regra. B precisa tratar sets fechados/manifest/versões/consumidores; não declarar NO CHANGE sem desenho aprovado. |
| Backup/restore/recovery | Bytes físicos históricos preservados; checker reutilizado pode mudar admissibilidade. Testar em alvo isolado; nenhum recovery real. |
| Checker | 25 checks existentes preservados; comportamento de falta de contexto e 25/0 precisa H1. Negativos reais conhecidos continuam findings, sem repair. |
| Upgrade/migrations/schema | Nenhuma criada/executada agora; A não requer. B em campo futuro implica exceção H4; nenhuma migration automática/adaptação de banco pessoal. |
| Contratos congelados | REV-FIXA-1.0 integralmente preservada. Priority e checker exigem reconciliação prospectiva da decisão semântica; RN-095 orienta identificação de mudança de regra. |

## Critérios de aceite FUNCIONAIS futuros

- Acre→São Paulo suportado pelo serviço oficial com owner, confirmação, CAS, no-op/cancel e logs preservados; mudança real permanece fora deste plano de execução sintética.
- Linhas e fatos históricos semanticamente/byte-equivalentes sob snapshot canônico; allowlist só timezone_name/lock_version/updated_at de Workspace na troca isolada; nenhuma reescrita/repair/perda.
- REV-004 correto na semântica expressamente aprovada; checks estruturais e datas com contexto exato continuam detectando corrupção. Falta de contexto jamais escondida como prova exata.
- Checker 25/0 nos casos válidos segundo H1 resolvida; inválidos relevantes com finding/exit correto; leitura zero DML tentado/completado e total_changes=0.
- Priority R/D não reinterpreta passado pelo timezone atual sob H2; mesmas datas de avaliação produzem membership estável; deltas correntes de today/O/Domain explicitados; thresholds/pesos/frações/ties protegidos.
- Nova operação usa SP coerentemente conforme H3/H4; agenda antiga e AuditEvent anterior preservados. Corrections/retentativas/exceções mantêm contratos aprovados.
- NO MIGRATION / NO FORMAT CHANGE ou exceções H4 expressamente aprovadas; nenhuma migration inesperada; fixtures V0.5/V1 e CEI/restore/upgrade passam sem inventar contexto.
- T1–T10 e complementos indispensáveis PASS observados, gate integral GREEN exit0, A8 deep APPROVED sem Major/Blocker aberto. Teste ausente ou outcome INCONCLUSIVE não é aprovação.
- Evidência RED inicial preservada; SOURCE real nunca acessada na remediação sintética; S8/S9/S10/PILOT sem execução automática.

## Severidade, estado e saída

Major / latent semantic risk: REV-004, Priority e coerência de replacement/scheduling. Nenhuma observed user-data corruption é afirmada; zero divergências na amostra real anterior não reduz finding. Migração não determinada para solução completa; preferência NO mantida e qualquer exceção depende de humano. A8 deep é FUTURA e NOT EXECUTED.

V1.0-S8R1 = AUTHORIZED / PLANNING; V1.0-S8 = AUTHORIZED / PAUSED / RESUMABLE AFTER S8R1; PILOT_EXECUTION = NOT YET AUTHORIZED; S9–S10 = NOT AUTHORIZED. Não arquivar S8/S8R1 como remediação concluída. Nenhum add/commit/push/tag/release.

Decision: HUMAN_DECISION_REQUIRED. A4 produzido e verificável, execução funcional bloqueada pelas escolhas H1–H4. Depois PARAR.
