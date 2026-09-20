# Plano executável da Release V0.5

- Task: `V0.5-P0`; status do plano: `COMPLETED`.
- Release: `V0.5 — Beta das capacidades V1`.
- Autoridade: este plano não autoriza execução. Cada estágio requer um novo
  contrato `AUTHORIZED` em `tasks/current.md` e encerra de volta em
  `NO_TASK_AUTHORIZED`.
- Baseline verificado: `main`, `HEAD` e `origin/main` em
  `46e887e0c4fa4dd6f7e128ab63802223d99c9e29`; tag anotada `v0.4.4` é o
  objeto `1938283f8a473054f443fc2733aaf462b861f713`, cujo commit apontado é
  esse mesmo HEAD. A árvore iniciou com a alteração não commitada do contrato
  V0.5-P0, preservada como autorização fornecida.

## 1. Fontes, baseline e correção de drift

Fontes normativas, em ordem aplicada: Roadmap §8 e §11
(`docs/Caderno_de_Erros_Inteligente_Etapa_9_Roadmap (1).md`); RF-027,
033, 035/036, 057--062, 066, 069--072 e requisitos de auditoria
(`docs/Caderno_de_Erros_Inteligente_Etapa_3_Requisitos_Funcionais.md`);
RN-027, 055, 068--084 e regras de correção/exportação
(`docs/Caderno_de_Erros_Inteligente_Etapa_5_Regras_de_Negocio.md`);
RNF de migração, segurança, portabilidade, performance e testes; Modelo de
Dados, Fluxos, Plano de Testes (em particular CT-109, 117--120 e 119), ADRs
007/012--014, Architecture v1.0, `PROJECT_STATE.md`, plano/evidências V0.4,
código e testes indicados na matriz.

Drift confirmado e simples: `PROJECT_STATE.md` e Roadmap ainda afirmam que
`v0.4.4` não existe/candidato sem tag; Git prova a tag anotada acima. Este P0
corrige somente essa declaração de estado, sem tocar tags, commits ou release.
Não há divergência material que invalide o planejamento: V0.4.4 é o baseline
de dados/código para a futura verificação de upgrade; V0.5 continua não
implementada.

## 2. V0.5_OFFICIAL_SCOPE

| Item | Fonte principal | Resultado esperado | Dependências conhecidas |
| --- | --- | --- | --- |
| Gestão e integridade avançadas | Roadmap §8.2 | reagendar preservando data/motivo; inserir questão inicialmente correta; categorias pessoais; filtros salvos; anular/substituir, corrigir gabarito, excluir com auditoria | decisões FL-ABR-001--004, 009--010; retenção; backup pré-migração |
| Domínio explicável | Roadmap §8.3; RF-057--061; RN-068--080 | `DOM-HEUR-1.0`, confiança, agregação taxonômica, domínio/reabertura e explicações | fatos V0.4 preservados; vetores normativos; decisão de recalculo |
| Prioridade recomendatória | Roadmap §8.3; RF-062; RN-081--084 | `PRI-HEUR-1.0`, dados insuficientes, fatores e desempate aprovado; nunca ordem obrigatória | domínio/confiança e PT-ABR-008 |
| Portabilidade e operação | Roadmap §8.4; RF-069--072; RNF-040--042 | `CEI-EXPORT-1.0`, manifesto/checksums, UI de backup/restore segura e relatórios | formato/versionamento, staging temporário, backup pré-restore |
| Compatibilidade e qualidade beta | Roadmap §§8.5--8.6, 11 | migrações conservam cópia V0.4.4; PostgreSQL crítico testado; BCR recalibrado; S5/S6 e documentação aplicáveis | dataset sintético, upgrade fixture, stages anteriores |

### V0.5_OUT_OF_SCOPE

- **V1.0:** estabilização, congelamento de esquema/regras, piloto final, release
  notes/changelog e fechamento de falhas beta (Roadmap §9). V0.5 produz beta,
  não promoção V1.
- **Pós-V1:** revisão adaptativa, calibração com dados reais, FTS se a busca
  simples falhar, API/integrações, hospedagem/PostgreSQL de produção e IA
  assistiva (Roadmap §10).
- **Sem compromisso de Roadmap:** cursos/tarefas/calendário amplo, turmas,
  compartilhamento, banco público, gamificação, OCR/importação massiva e app
  nativo. Autenticação remota, notificações e anexos também ficam excluídos.

## 3. Matriz de rastreabilidade e auditoria real

`COMPLETE` significa atender ao item V0.5, não apenas possuir uma base parecida.

| Item oficial | Fonte | Estado | Evidência código/teste | Lacuna e estágio | Migração/risco |
| --- | --- | --- | --- | --- | --- |
| Reagendamento/inclusão manual | Roadmap A; RF-035/036 | NOT_STARTED | `reviews/models.py` só tem origens INITIAL_ERROR/QUESTION_ACTIVATION; `test_review_completion.py` cobre ciclo fixo | novo caso de uso e fatos de motivo, S2 | EXPECTED/high |
| Categorias pessoais | Roadmap A; RF-033 | NOT_STARTED | `errors/models.py` tem categorias/classificação padrão e revisão; testes de classificação | entidades/lifecycle/consolidação, S2--S3 | EXPECTED/high |
| Filtros salvos | Roadmap A; RF-066 | NOT_STARTED | `search/forms.py`, `test_question_search.py` cobrem filtros transitórios | modelo e UI de filtros nomeados, S3 | EXPECTED/medium |
| Anular/substituir tentativa | Roadmap A; RF-027; RN-027 | PARTIAL | `Attempt.status`, `replaces_attempt`, `voided_*` e constraints existem; `Attempt.save/update/delete` proíbem mutação | serviço transacional, reconstrução/auditoria, S2 | EXPECTED/high |
| Corrigir gabarito pós-histórico | Roadmap A; RF-018 | PARTIAL | QuestionRevision preserva versões e bloqueio atual é testado | regra de correção, impacto/reconstrução/auditoria, S2 | UNLIKELY/UNKNOWN design, high |
| Exclusão permanente | Roadmap A; RN-009/055 | NOT_STARTED | arquivamento existente em questions/reviews e testes; FKs PROTECT | política, confirmação, impacto e retenção, S2--S3 | EXPECTED/high |
| Auditoria/retenção | Roadmap A; RF-072 | PARTIAL | OperationReceipt e revisões de classificação; `operations/events.py` é técnico, não auditoria funcional | eventos sensíveis e retenção decidida, S1--S2 | EXPECTED/high |
| DOM-HEUR-1.0 | Roadmap B; RF-057--061; RN-068 | NOT_STARTED | fatos históricos/taxonomia existem; sem símbolo DOM-HEUR | política pura, vetores e explicação, S4--S5 | UNLIKELY then UNKNOWN snapshots, high |
| Domínio agregado/reabertura | Roadmap B; RN-074--080 | NOT_STARTED | taxonomy e ReviewCycle já são Workspace-scoped | selectors/persistência somente se justificada, S5 | UNKNOWN/high |
| PRI-HEUR-1.0 | Roadmap B; RF-062; RN-081--084 | NOT_STARTED | fila usa ReviewStatusPolicy; sem score/prioridade | política pura, decisão PT-ABR-008 e recomendação, S6 | UNLIKELY/medium-high |
| Exportação versionada | Roadmap C; RF-069; RNF-040--042 | NOT_STARTED | S6 faz backup SQLite técnico e valida/restore isolado; `test_backup_*` | formato funcional/manifests/leitor/round-trip, S7 | UNLIKELY/medium-high |
| Backup/restore pela UI | Roadmap C | PARTIAL | comandos `backup_sqlite`, `validate_backup`, `restore_backup`; S6 provado | autorização UI, staging, pré-backup, erro recuperável, S7 | UNLIKELY/high |
| S5/S6 e compatibilidade | Roadmap §8.6 | EXISTING_BUT_NEEDS_HARDENING | checker read-only de 17 invariantes e S6 isolado; `test_integrity_checker.py`, `test_backup_recovery.py` | ampliar somente para fatos V0.5 e upgrade/restore, S8 | UNLIKELY/high |
| BCR/busca/PG crítico | Roadmap C; CT-109 | EXISTING_BUT_NEEDS_HARDENING | BCR-1 e testes SQLite V0.4 existem | medir novas operações; PG constraints críticas; FTS somente se medido, S9 | UNLIKELY/medium |

## 4. REUSED_FROM_V0.4 e semânticas congeladas

Reutilizar, sem reabrir: Workspace e timezone/IANA; Questions e revisões
versionadas; alternativas; Attempts e ReviewCycles/Reviews; ErrorClassification
e seus históricos; Analytics/dashboard/drill-down; consulta, detalhe, timeline,
filtros e paginação; fila; S5 read-only; S6 backup/restore isolado; S7
start-local Windows; acessibilidade/hardening; BCR-1; logs técnicos e CTA.
Cada nova consulta e mutação preservará isolamento de Workspace.

Congeladas até requisito V0.5 explícito: `registered` inclui draft/active/
archived; `performed` é questão distinta com INITIAL válida e REVIEW não a
aumenta; percent sem denominador é `None`, não zero; estados overdue/due/future
vêm de `ReviewStatusPolicy` e do fuso do Workspace; D1/D7/D14/D30 e
`REV-FIXA-1.0`; classificação residual não vira categoria inventada; fatos e
histórico não são reescritos; filtros transitórios continuam Workspace-scoped.

## 5. Domínio, prioridade, gestão, integridade e portabilidade

**Domínio.** Normativamente é índice de aprendizagem, não entidade acadêmica
nem sinônimo de disciplina/categoria/score automático. Começa por questão e
agrega por subassunto, assunto e disciplina (RN-068/074); DOM-HEUR-1.0 separa
domínio de confiança/suficiência. Dificuldade não pesa. A regra requer fatos
válidos, estado ativo e explicação/versionamento. Não há fonte que autorize
editar domínio manualmente nem que determine snapshots; criação, edição e
recalculo/versionamento ficam em OPEN_DECISIONS. Filtros/ordenação só serão
definidos quando fontes explicitarem os critérios, sem alterar analytics V0.4.

**Prioridade.** É recomendação de estudo, não campo manual, fila obrigatória ou
algoritmo novo de scheduling. PRI-HEUR-1.0 usa os fatores normativos, exibe
motivos e deve classificar evidência insuficiente em vez de fraqueza. A fórmula
normativa existe, mas desempate/janela de recorrência permanecem PT-ABR-008;
não há choices/default/editabilidade/filtro persistente autorizados fora do
desenho posterior fundamentado.

**Gestão avançada.** Somente itens do Checkpoint A entram: reagendar, inclusão
manual, categorias pessoais, filtros salvos, anulação/substituição, correção
de gabarito, exclusão permanente e auditoria. Arquivamento existente não é
exclusão; repair mutável do checker não entra.

**Integridade.** S5 continua diagnóstico read-only. S8 acrescentará invariantes
para apenas os novos fatos/modelos aprovados; guards preventivos ficam nos
serviços/constraints, e repair não é inferido. Cada migration exige upgrade de
cópia V0.4.4, defaults/backfill explícitos, reversibilidade classificada e
backup anterior; backups antigos são restaurados pelo software compatível que
os produziu, sem promessa de downgrade automático.

**Portabilidade/operação.** Backup é snapshot operacional; restore repõe banco
em destino isolado; exportação é formato funcional versionado/lido
independentemente; importação é somente a contrapartida explicitamente
necessária de exportar→ambiente vazio→reexportar, nunca overwrite implícito;
transferência entre máquinas depende desse formato e do guia. S7 continua
start-local/loopback; V0.5 só acrescenta UI segura e procedimentos de upgrade.

## 6. OPEN_DECISIONS

| ID | Pergunta e fonte ambígua | Opções/impacto | Bloqueia | Resolver |
| --- | --- | --- | --- | --- |
| V05-OD01 | política final de anulação, exclusão, reconstrução e retenção (RF-ABR-007, RN-ABR-005) | **RESOLVED em S1:** arquivamento padrão; lifecycle transacional; auditoria sanitizada de exclusão por 90 dias, com expurgo obrigatório posterior | — | contrato `docs/V0.5_S1_Contratos_Normativos_e_Invariantes.md` |
| V05-OD02 | FL-ABR-001--004, 009--010 não fechados pelo Roadmap | **PARTIALLY_RESOLVED em S1:** correção prospectiva sem reinterpretar histórico, retenção e consolidação pessoal→pessoal ativa definidas; reativação fora do P0/S2; recibos deferidos a S8; prioridade a S6 | S2A--S2D/S6/S8 conforme item | contrato S1 e futura autorização aplicável |
| V05-OD03 | desempate e janela PRI (PT-ABR-008) | determinismo da recomendação | S6, não S1--S5 | antes de testes de prioridade |
| V05-OD04 | recalcular domínio em nova fórmula (RN-ABR-004) | cálculo on-demand versus versão/snapshot; compatibilidade | S5, não política pura S4 | antes de persistência/snapshot |
| V05-OD05 | formato final export/backup (RNF-ABR-006) | schema/manifesto/importabilidade | S7 | durante plano A4 S7 |
| V05-OD06 | matriz móvel V1 (PT-ABR-005) | evidência de UI, não escopo de feature | S9 | antes do gate beta se UI móvel mudar |

## 7. Decomposição executável

| ID | Objetivo/escopo e exclusões | Deps | Size/risk/migration | A4; A7; A8 | Done When resumido |
| --- | --- | --- | --- | --- | --- |
| S1 | Fechar decisões normativas V0.5 aplicáveis e contrato de invariantes/dados; sem feature/migration | P0 | M/high/UNLIKELY | checklist; Terra High; deep | decisões resolvidas/registradas sem inventar regra; matriz e vetores futuros definidos |
| S2A | Fundação auditável e gestão não destrutiva: auditoria funcional, categorias pessoais, consolidação pessoal→pessoal, reagendamento e inclusão manual; sem void, gabarito ou delete | S1 mandatory | L/high/EXPECTED | plano; Sol High; deep | dados V0.4.4 preservados, auditoria/Workspace/agenda reconciliados e upgrade/rollback provados |
| S2B | Correção estrutural de Attempt: anulação, substituição, reconstrução e reconciliação; sem gabarito/delete | S2A mandatory | L/high/EXPECTED | plano; Sol High; deep | cadeia acíclica, fatos imutáveis, fila/métricas reconstruídas e upgrade/rollback provados |
| S2C | Correção prospectiva e auditável de gabarito por nova revisão; sem reinterpretar Attempt histórico ou delete | S2A mandatory | L/high/EXPECTED | plano; Sol High; deep | versão usada preservada, futuro usa revisão corrente e nenhuma métrica/review histórica muda implicitamente |
| S2D | Exclusão permanente por agregado e retenção sanitizada de auditoria por 90 dias; sem export/import/UI geral | S2A mandatory | L/high/EXPECTED | plano; Sol High; deep | elegibilidade, transação, expurgo futuro, backup/recovery e ausência de órfãos provados |
| S3 | Gestão UI: confirmações, categorias e filtros salvos; sem algoritmo/polimento geral | S2A--S2D mandatory; S1 for filters | M/high/EXPECTED | checklist; Sol Medium; standard (deep if deletion UI changes data) | fluxos Workspace-scoped, keyboard/error/empty states e testes UI passam |
| S4 | Política pura DOM-HEUR-1.0, confiança, vetores e explicações; sem persistência/snapshots/UI | S1 mandatory | L/high/UNLIKELY | plano; Sol High; deep | vetores normativos/bordas determinísticos e nenhuma semântica V0.4 alterada |
| S5 | Aplicar domínio/reabertura/agregações e explicação consultável; snapshots apenas se benchmark justificar | S2A--S2D + S4 mandatory | L/high/UNKNOWN | plano; Sol High; deep | isolamento, compatibilidade, recálculo e invariantes novos provados |
| S6 | PRI-HEUR-1.0 e recomendação explicável; sem substituir fila/scheduling | S5 + OD03 mandatory | M/high/UNLIKELY | checklist; Sol Medium; deep | insuficiência/motivos/desempate determinísticos e UI acessível |
| S7 | CEI-EXPORT-1.0, UI backup/restore e staging seguro; sem API/overwrite | S1/OD05 + S2A--S2D mandatory | L/high/UNLIKELY | plano; Sol High; deep | validação antes da mutação, round-trip/rejeição, pré-backup e relatórios |
| S8 | Evoluir S5/S6, testar upgrade V0.4.4 e PostgreSQL crítico; sem repair/checker mutável | S2A--S2D, S5, S7 mandatory | L/high/UNLIKELY | plano; Sol High; deep | invariantes/read-only, restore e migration/compatibility evidence GREEN |
| S9 | Hardening beta: BCR aplicável, acessibilidade, segurança/local operation e documentação; FTS só com falha medida | S3, S6, S7, S8 mandatory | L/high/UNLIKELY | plano; Sol Medium; deep | evidência medida, UX central, Windows e docs beta completos |
| S10 | Piloto controlado e decisão documental V0.5; sem V1/tag/release | S9 mandatory | L/high/UNLIKELY | plano; Sol High; deep | cópia protegida, backup/restore, findings tratados e promoção decidida |

S2 foi reavaliada em S1 como **XL** e, por isso, não permanece executável como
unidade. S2A é sua fundação; S2B, S2C e S2D são checkpoints L/high independentes
depois dela. S3 e S4 podem avançar em paralelo quando suas dependências forem
satisfeitas; S7 pode planejar formato após S1, mas só manipula dados após
S2A--S2D. Caminho crítico: `S1 → S2A → (S2B, S2C, S2D) → S4 → S5 → S6 → S9 →
S10`, com `S2A--S2D → S7 → S8 → S9` também obrigatório. Relações citadas como
mandatory são bloqueantes; as demais são convenient e não autorizam estado
parcial compartilhado.

## 8. Risks, testes, recovery e promoção

| ID | Risco | Prob./impacto | Dono/mitigação/evidência |
| --- | --- | --- | --- |
| V05-R01 | migration/backfill perde ou mistura fatos | medium/high | S2; cópia V0.4.4, backup, upgrade/rollback e reconciliação |
| V05-R02 | reconstrução altera histórico/métricas | medium/high | S2; eventos imutáveis, transação, vetores e analytics reconciliation |
| V05-R03 | fórmula trata baixa evidência como certeza | medium/high | S4--S6; confiança explícita, testes negativos e motivos |
| V05-R04 | vazamento entre Workspaces em agregação/importação | low/high | S2--S8; filtros/constraints/checker e testes estrangeiros |
| V05-R05 | export/import parcial ou incompatível | medium/high | S7; staging, manifest/checksum, reject-before-mutation, round-trip |
| V05-R06 | backup confundido com export/rollback | medium/high | S7--S8; documentação, pré-backup, restore isolado e S5 |
| V05-R07 | checker não cobre fato novo ou vira mutável | medium/high | S8; catálogo versionado/read-only e fixtures inválidas |
| V05-R08 | regressão de performance/acessibilidade | medium/medium | S9; BCR sem threshold inventado, keyboard/focus/200%/360px |

Testes por camada: política unitária e vetores; serviço/ORM, transação,
idempotência e Workspace; migrations em fixture/cópia V0.4.4; integração/UI
para gestão/recomendação; comandos, S5/S6 e recovery; export/import negativo e
round-trip; PostgreSQL somente constraints críticas; BCR e acessibilidade das
superfícies novas; piloto em cópia sanitizada. Cada estágio roda focados e
regressão relacionada; dados, integridade, migration, portabilidade, hardening
e piloto exigem gate completo. BCR-1 é reutilizado e ampliado apenas para
operações V0.5 medidas; nenhum threshold novo é definido neste P0.

Rollback: S1/S4/S6/S9 documental/pura são reversíveis; S3 geralmente
reversível; S2/S5/S7/S8 requerem backup e restore isolado, e migration rollback
é classificada por migration, não presumida segura. O teste explícito é
`database equivalente a V0.4.4 → candidate V0.5`, seguido de S5 e
reconciliação. Recovery de backup V0.4.4 após update é suportada pelo fluxo de
restore da versão compatível; suporte a downgrade automático não é prometido.

### Gate de promoção V0.5

Exigir S1--S10 arquivados, testes/Gate GREEN, migrations limpas e upgrade
evidenciado, S5 read-only saudável, S6/restore isolado, compatibilidade V0.4.4,
portabilidade round-trip/rejeições, documentação beta, BCR aplicável medido,
acessibilidade e operação Windows das telas novas, segurança de arquivos/logs,
piloto em cópia, A8 profundo final APPROVED e nenhum Blocker/Major/P0/P1.
Falha de integridade, perda, cross-Workspace, duplicação, export/backup
irrecuperável ou migration destrutiva bloqueia. Isto é gate beta V0.5, não
tag/release V1.0.

## 9. Documentação, UX e operação

S1 atualiza contratos/decisões apenas se autorizados; S2/S3 documentam gestão e
auditoria; S4--S6 explicam fórmula, confiança e limites; S7/S8 atualizam
backup/recovery/export/upgrade; S9 atualiza README, uso, Windows e evidência;
S10 registra piloto/promoção e PROJECT_STATE. Roadmap só muda se o estado real
exigir, nunca para marcar feature antecipada.

UI nova/modificada deve manter teclado, foco visível, labels, 200%, 360px,
empty/error/recovery states e explicações não dependentes só de cor. S7 não
reimplementa start-local/shutdown/loopback; só documenta a operação adicional
que for comprovadamente alterada. Segurança permanece local: validar input e
arquivos, paths e versão, não logar conteúdo/segredos, e não inventar modelo de
ameaça de serviço público.

## 10. A8 profundo de P0

Revisão realizada contra contrato, fontes e este plano: scope V0.5 coberto;
V1/Pós-V1 excluídos; estados distinguem base de entrega; nenhuma etapa XL ou
ciclo; migrations, dados, checker, backup, compatibilidade, open decisions,
testes, A4/A7/A8 e gate estão tratados. Finding resolvido no plano: drift da
tag V0.4.4 foi explicitado para correção documental. Não há Blocker, Major ou
Minor aberto neste plano.

**Resultado A8: APPROVED (deep).**

## 11. P0 closure evidence

- Auditoria: fontes acima, Git/tag e busca focal de modelos, serviços, comandos
  e testes V0.4.
- Não ações: nenhum código funcional, migration, backfill, dados operacionais,
  tag, commit, push, release ou autorização de V0.5-S1.
- Verificações finais e métricas prospectivas: registradas no contrato
  arquivado, artefato de review e `quality/operational-execution-metrics.jsonl`.

## 12. Atualização normativa S1

S1 fechou OD01 pela decisão humana de retenção sanitizada por 90 dias e
expurgo obrigatório, e fechou as parcelas de OD02 necessárias para lifecycle:
consolidação exclusiva categoria pessoal→categoria pessoal ativa, métricas
atuais pelo alvo e histórico append-only preservado. Não houve feature,
migration, schema, backfill, dado operacional ou autorização de S2A--S2D.
O contrato canônico é `docs/V0.5_S1_Contratos_Normativos_e_Invariantes.md`.
