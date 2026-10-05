# V1.0-S8R1 — matriz de superfícies

Classes dizem respeito à sensibilidade na troca do timezone do Workspace. PROSPECTIVE_ONLY inclui projeções correntes dependentes de today, sem reconversão do fato antigo. UNAFFECTED se refere à operação de troca isolada, não a todas as possíveis mutações do produto. UNKNOWN registra contexto histórico irrecuperável ou decisão ainda não tomada.

| Superfície | Classe | Base auditada | Efeito e limite de remediação |
| --- | --- | --- | --- |
| Attempt persistida, ATT-002 | UNAFFECTED | attempts/models.py:117/219; integrity.py:1374 | UTC+timezone próprio+local_date preservados; validar sempre no contexto próprio. |
| Nova Attempt INITIAL/REVIEW ordinária | PROSPECTIVE_ONLY | attempts/services.py:116/260; reviews/services.py:651 | Usa contexto da operação futura; novo fuso após troca. |
| Attempt replacement | HISTORICAL_TIMEZONE_SENSITIVE | attempts/corrections.py:181–193 | Nova Attempt herda timezone da ponta; decidir interação com cálculo futuro, sem reescrever predecessora. |
| REV-004 SQL INITIAL_ERROR e transições ancoradas | UNAFFECTED | integrity.py:856–910 | Deriva de local_date da âncora; sequência/transições/offsets preservados. |
| REV-004 complemento QUESTION_ACTIVATION | HISTORICAL_TIMEZONE_SENSITIVE | integrity.py:1439–1453 | started_at reconvertido pelo timezone atual; falso finding/masking na virada. |
| REV-004 complemento MANUAL INCLUSION/MASTERY_REOPEN | HISTORICAL_TIMEZONE_SENSITIVE | mesmo complemento; reviews/services.py:206–238; domain/services.py:314 | Timezone da criação não é o da Attempt histórica necessariamente. |
| Timezone original de ReviewCycle inaugural | UNKNOWN | reviews/models.py:57–109 e migrations | Não persistido universalmente; requer decisão sobre legacy/exatidão. |
| first_due_date/current_due_date já calculadas | UNAFFECTED | reviews/models.py; accounts/services.py:155–165 | Troca não grava Reviews; datas civis não podem ser “corrigidas”. |
| Novos ciclos QUESTION_ACTIVATION/MANUAL | PROSPECTIVE_ONLY | reviews/services.py:208/263; domain/services.py:314 | Data-base atual e +1; contexto inaugural ainda não persistido. |
| D1/D7/D14/D30 e reset ordinários | PROSPECTIVE_ONLY | reviews/policies.py:87–155; services.py:471/716 | +1/+7/+14/+30 desde resposta real; +dias civis, não duração UTC ou marcos acumulados. |
| Nova agenda após replacement REVIEW | HISTORICAL_TIMEZONE_SENSITIVE | reconstruction.py:155–184 | Workspace novo vs substituta com timezone antigo: possível checker FAIL em fato novo. |
| Retentativa void/preservação manual | UNAFFECTED | reconstruction.py:90–104/250–288 | Conserva data operacional em projeção nova; preservar exceções normativas e validar relação. |
| ReviewScheduleChange antigo | UNAFFECTED | reviews/models.py:500–562 | Datas e timezone explícitos imutáveis; não usar como prova inaugural. |
| Reagendamento novo | PROSPECTIVE_ONLY | reviews/services.py:106/124–143 | Validação hoje/futuro no fuso novo; novo change/audit registram fuso do comando. |
| AuditEvent antigo | UNAFFECTED | operations/models.py:48–65/99–151 | Append-only; contexto explícito somente quando cabível; não alterar linhas. |
| Histórico de timezone do Workspace | UNKNOWN | accounts/services.py, operations/events.py | Logs operacionais sem trilha durável completa; nenhum AuditEvent TIMEZONE_CHANGE existente. |
| Serviço oficial change_workspace_timezone | PROSPECTIVE_ONLY | accounts/services.py:119–192 | Owner, IANA, confirmação, CAS; somente 3 campos Workspace, logs; não recomputa história. |
| Domain seleção de evidência, suficiência e índice | UNAFFECTED | domain/selectors.py:45–62, policy.py | Preserva datas e ordem UTC; mesma referência e mesma seleção ⇒ equivalência. |
| Domain aging, confiança, mastery corrente | PROSPECTIVE_ONLY | domain/policy.py:382–395/448; selectors.py:34/99 | Today novo pode alterar idade e atraso; C_h/elegibilidade podem variar legitimamente. |
| Domain na troca inversa / idade negativa | HISTORICAL_TIMEZONE_SENSITIVE | domain/policy.py:385 | Evaluated_on pode anteceder local_date; borda adicional, não fix silencioso. |
| MasteryStateEvent anterior e agregação estática | UNAFFECTED | domain/models.py; services.py:71/129 | Nenhuma reescrita de evento; GET não cria evento. |
| Priority R/D seleção temporal | HISTORICAL_TIMEZONE_SENSITIVE | priority/services.py:95–114 | Reinterpreta REVIEW histórica; janelas e denominadores/score podem mudar sem novo fato. |
| Priority W/O/C_h/evaluated_on correntes | PROSPECTIVE_ONLY | priority/services.py:70–85/119–142 | Today/Domain/overdue legítimos; separar deltas desses parâmetros dos de R/D. |
| Priority policy pura/weights/ties | UNAFFECTED | priority/policy.py | Não tem timezone; alterações no adapter afetam inputs; não recalibrar fórmula. |
| Analytics histórico/período explícito | UNAFFECTED | analytics/selectors.py:19–43; services.py | Filtro por local_date gravada; contagens/taxonomia acerto existentes. |
| Analytics completed_today | PROSPECTIVE_ONLY | analytics/services.py:reviews/completed_reviews_today | Intervalo solicitado usa novo today, fato não muda. |
| Queue/status due/overdue/future | PROSPECTIVE_ONLY | reviews/selectors.py:82; analytics/selectors.py:71–108 | Due dates estáveis, today novo; resultados correntes podem mudar. |
| Timeline/read model/ordem dos eventos | UNAFFECTED | reviews/selectors.py:144–185/275–309 | Mantém timezone/local_date da Attempt; ciclos sem contexto; UTC não muda. |
| Timeline/renderização atual | UNAFFECTED | templates/reviews/timeline.html:9; settings/base.py:56/58 | UTC configurado; não usa Workspace para converter; UI não expõe todos os campos temporais históricos. |
| Catálogo e filtros textuais/taxonomia | UNAFFECTED | search/selectors.py:39–104 | Não dependem do fuso; relações correntes não devem ser confundidas com histórico temporal. |
| Review status filter / SavedFilter aplicado | PROSPECTIVE_ONLY | search/selectors.py:64–70 e saved_filter_services.py | Parâmetro status usa today; SavedFilter persistido fica igual. |
| Ano corrente em validação de Question | PROSPECTIVE_ONLY | questions/validators.py:84/155 | Novo Calendar/ano; incluir fronteira anual sem alterar regras. |
| CEI bytes/campos históricos | UNAFFECTED | docs/CEI_EXPORT_1_0.md:46–55 | NO FORMAT CHANGE para A; manifest timezone atual varia de modo legítimo. |
| CEI validação semântica / import | HISTORICAL_TIMEZONE_SENSITIVE | data_management/portability.py:688–715/866 | Reutiliza REV-004: possível rejeição pre-DML de legado válido; garantir regra canônica única. |
| Backup físico existente | UNAFFECTED | data_management/services.py | Não reinterpretado pela troca; bytes históricos não ganham contexto faltante. |
| Restore/recovery e upgrade com checker | HISTORICAL_TIMEZONE_SENSITIVE | data_management/services.py:789; portability.py | Validação herda falso positivo; fixtures antigas exigem teste de compatibilidade sintético. |
| Schema/migration/CEI para B | UNKNOWN | models/migrations/CEI fechado | Nova informação futura exige desenho e decisão; não presumir zero mudança. |
| Relógio/timezone de servidor/browser | UNAFFECTED | shared/domain/time.py, UTC/USE_TZ | Não substituir IANA explícito; não depender de relógio real em testes. |

Investigação detalhada e decisões: `quality/v10-s8r1-timezone-investigation.md` e A4. Nenhuma linha UNKNOWN foi convertida em PASS ou usada para autorizar acesso real.
