# V1.0-S8R1 — investigação da semântica histórica de timezone

Data: 2026-10-05. Escopo: auditoria estática e cálculo de contrafactuais fixos, sem importar Django, inicializar aplicação ou conectar banco. Nenhuma implementação funcional. Decisão de planejamento: HUMAN_DECISION_REQUIRED.

## Evidência e limites

HEAD e ref local origin/main confirmados em dcccb8950a7752d03461665e0a4952c8a9bc663b; sem fetch. Os oito paths iniciais estão no inventário `quality/v10-s8r1-initial-paths.json`. O contrato S8 e o PROJECT_STATE anteriores foram preservados como sufixos de bytes; seis artefatos S8 permanecerão byte a byte. Não houve abertura, consulta, cópia ou stat deliberado da SOURCE/development.sqlite3. Nem configuração executável pessoal foi aberta. O configuration preflight anterior continua histórico; seu registro disponível no contrato S8 foi preservado, sem rerun ou reconstrução de artefato inexistente no inventário.

W01 Brazil/Acre, intenção America/Sao_Paulo, SQLite ok, FK 0, migrations 34/34, W01 único, checker 25/0, SOURCE fisicamente inalterada e zero divergências na amostra são evidência humana/histórica do contrato S8, não medições desta tarefa. Nenhuma corrupção real observada no relato anterior; situação atual da SOURCE não foi inspecionada. Zero divergências na amostra não reduz severidade do risco latente.

## REV-004: regra SQL e complemento Python

`src/modules/operations/integrity.py:413` cataloga REV-004 como ERROR. O SQL em `:856–910` verifica sequência contígua, origem/transição, INITIAL_ERROR e agenda ancorada. D1 após erro inicial deriva de `Attempt.local_date + 1`; reset/avanços usam essa data persistida com +1/+7/+14/+30 dias civis. MANUAL com Attempt âncora verifica origem/transição, mas não deriva a data inaugural da data dessa Attempt. CORRECTION_RETRY_VOIDED e CORRECTION_PRESERVE_MANUAL têm exceções explícitas. `current_due_date` não é congelada nem comparada à primeira agenda, pois reagendamento é permitido.

O complemento `_append_inaugural_schedule_findings` (`:1432–1471`) lê `r.id, c.started_at, w.timezone_name, r.first_due_date`, para QUESTION_ACTIVATION e MANUAL com sequence_number=1. Converte started_at no timezone ATUAL do Workspace, soma um dia civil e compara à first_due_date histórica. O join atual é a única fonte de timezone nesse cálculo, não um histórico temporal. Isso tenta reconstruir a data civil da ativação/inclusão/reabertura no instante original. O erro não está na soma +1, e sim na fonte do contexto da conversão.

`_append_attempt_date_findings` (`:1374–1399`, ATT-002) já usa o timezone da própria Attempt; `_append_workspace_timezone_findings` (`:1412`) valida a configuração atual. REV-004 deve continuar detectando sequência, transições, escopo e datas incorretas sem depender de Workspace mutável para fatos passados. O parsing assume UTC para timestamps sem tzinfo e ignora TypeError/ValueError; são comportamentos existentes, não corrigidos aqui. Planejar negativos para eles sem tratar skip como prova de saúde.

`docs/V0.4_S5_Invariant_Checker.md:102–104` menciona o mesmo IANA do domínio, mas não documenta como recuperar o timezone original após mudança. `docs/ADR-013_Ciclo_de_Revisao_na_Ativacao_da_Questao_V0.3.md:45–47` fixa D1 no próximo dia civil do Workspace à ativação. RN-005 proíbe reescrever datas já calculadas. Interpretar “Workspace” retrospectivamente como sua configuração atual produz a contradição semântica.

## Criação e disponibilidade de contexto

| Fato/origem | Fonte existente | Suficiente para semântica original? |
| --- | --- | --- |
| Attempt INITIAL/REVIEW | occurred_at UTC, timezone_name e local_date; models.py:117/219–225, services.py:260–263 e reviews/services.py:651–665 | Sim: contexto da própria Attempt, sujeito à validação ATT-002. |
| INITIAL_ERROR legado | origin/scheduled_from Attempt e local_date; reconstruction.py:224–248 | Sim para agenda ancorada; SQL REV-004 já o utiliza. |
| QUESTION_ACTIVATION | started_at UTC, origin_revision, first_due_date civil; reviews/services.py:246–281 e models.py:57–109 | Não guarda timezone/data-base independente. first_due_date-1 informa o dia declarado, não comprova o fuso que o produziu. |
| MANUAL INCLUSION | started_at do comando, first_due_date do Calendar atual, origin_attempt antiga; reviews/services.py:184–238 | Não. Timezone da Attempt antiga pode ser diferente do timezone do comando atual. |
| MANUAL MASTERY_REOPEN | domínio/services.py:306–337 usa agora + Calendar atual; anchor é evidência anterior | Não. MasteryStateEvent guarda instante/contexto de lifecycle, não timezone inaugural. |
| Review posterior ordinária | scheduled_from_attempt; first_due_date persistida; reviews/services.py:710–720 | Sim para a agenda derivada da resposta com seu contexto. |
| ReviewScheduleChange | previous/new_due_date, timezone_name explícito e correlation_id; models.py:500–562 e services.py:124–143 | Sim para o reagendamento, não para o timezone de criação de um ciclo anterior. |
| AuditEvent REVIEW_RESCHEDULED | previous/new_date e timezone_name explícito | Sim para esse evento; não se generaliza a toda auditoria. |
| AuditEvent MANUAL_REVIEW_INCLUDED | comando passa reason/correlação, sem timezone; operations/models.py:48–65 | Não prova timezone da inclusão. |
| Troca de timezone | Workspace atualizado e eventos estruturados de logging | Não há histórico durável completo de intervalos de vigência do timezone. |

Migrations de reviews 0001–0005 e listas fechadas CEI confirmam ausência de timezone em Review/ReviewCycle. Não inferir contexto por Attempt mais próxima, current_due_date, timezone de reagendamento posterior, relógio do servidor ou logs incompletos. Também não obter esse contexto abrindo SOURCE nesta tarefa.

Exemplo de impossibilidade: em 2026-10-05T04:00:00Z, Acre produz data-base 04/10 e D1 05/10; São Paulo produz data-base 05/10 e D1 06/10. Um ciclo que guarda somente instante, D1 e Workspace agora em São Paulo pode representar tanto uma D1 válida criada no Acre como uma D1 incorreta criada em São Paulo. Sem contexto independente, o checker não pode distinguir ambos com exatidão. Usar first_due_date-1 como sua própria prova seria validação circular; aceitar ambas amplia falso negativo.

## Priority: janelas, suficiência, confiança e elegibilidade

`src/modules/priority/services.py:47–49` busca Workspace e cria ZoneInfo atual. `:95–114` seleciona question_id, tipo, occurred_at, is_correct; descarta local_date e timezone_name históricos na projeção. REVIEW é convertida por `occurred_at.astimezone(zone).date()`, e age=today-data_reconvertida. R inclui idades 0–89; D RECENT 0–29, BASELINE 30–59. INITIAL apenas marca questão realizada; VOIDED não entra por valid_attempts. Review pendente não vira evidência.

Uma mudança de timezone pode deslocar uma REVIEW entre dias e janelas mesmo quando today é igual nos dois fusos. Aos limites 29/30, 59/60 e 89/90, isso muda denominadores, recorrência, comparáveis e R/D. `priority/policy.py:95–199` exige >=2 REVIEWs por Question e >=3 elegíveis para R; >=1 REVIEW em cada janela e >=3 comparáveis para D; ausência produz COLLECT_MORE_EVIDENCE; C_h>=40 e todos W/O/R/D presentes são necessários para score. Pesos 40/30/20/10 e desempate UUID ficam protegidos. Score é leitura corrente, não snapshot histórico persistido.

W vem de Domain; O vem da agenda corrente com today do Workspace. C_h vem de Domain agregado; não é calculada diretamente pela relocalização de R/D. Mudança legítima de today pode mudar idade/confiança/atraso e por isso W/O/C_h/eligibilidade. Não exigir score sempre idêntico após a troca: exigir identidade das datas históricas e isolamento dos deltas permitidos do parâmetro de avaliação corrente.

Conflito formal a resolver: `tasks/plans/v05-s6-priority-heuristic-plan.md:59–67` registra decisões HUMANAS aprovadas em 2026-09-24; R explicitamente usa occurred_at convertido no fuso do Workspace. `quality/v05-s6-priority-heuristic-result.md:13` registra conversão no fuso atual. `docs/V1.0_S1_Contratos_e_Compatibilidade.md:93–110` congela PRI-HEUR-1.0 referenciando essas decisões. Trocar para Attempt.local_date é tecnicamente compatível com os campos atuais, mas altera seleção de evidência em fronteiras e deve receber decisão formal sobre errata ou identificador conforme RN-095. Nenhuma dessas fontes foi reescrita neste planejamento.

## Domain e consultas derivadas

`domain/selectors.py:34–62` preserva occurred_at e local_date da Attempt; não relocaliza passado. Seleciona ciclo por UTC e monta referência atual via review_reference_date. `domain/policy.py:382–395,448–449` calcula idade com evaluated_on - last_attempt.local_date; fronteiras 60/61,120/121,180/181,365/366; idade negativa levanta ValueError. Índice, suficiência, confiança e mastery são conceitos distintos. Para o mesmo evaluated_on e elegibilidade operacional, fatos antigos devem produzir avaliação equivalente; com novo today o envelhecimento/atraso podem mudar prospectivamente. RN-079 pode refletir confiança/atraso atuais sem reescrever evento anterior. Há risco adicional em troca inversa para fuso anterior ao dia da última Attempt: planejar negativo para idade <0, sem mudar a policy silenciosamente.

analytics.valid_attempts/performed_questions/activity usam local_date armazenada para períodos; métricas históricas com intervalo explícito permanecem. completed_today usa today novo como parâmetro do filtro: diferença corrente permitida. eligible_reviews e review queue comparam current_due_date imutável pela troca com today novo. Filtros de review_status e SavedFilters que chamam essa projeção podem mudar resultados atuais; bytes do SavedFilter não mudam.

Timeline em reviews/selectors.py:144–185 mantém Attempt.timezone_name/local_date e ordena por instante/precedência/id; eventos de ciclo não têm timezone. Template reviews/timeline.html:9 exibe datetime, sem reconversão pelo Workspace; base.py:56/58 usa UTC/USE_TZ. Não alegar que a UI já expõe o timezone histórico: os campos estão no read model, mas o template atual não os imprime. A troca do Workspace sozinha não transforma essa renderização.

## Outra superfície crítica: correções após a troca

`AttemptCorrectionService.replace` em attempts/corrections.py:181–193 cria substituta com instante NOVO e timezone da ponta antiga. `AttemptDerivedStateRebuilder._rebuild_review` em reviews/reconstruction.py:155–184 agenda decisão no timezone ATUAL e clock atual. REV-004 SQL exige first_due_date derivada da substituta.local_date. Após Acre→São Paulo em 04:00Z, substituta tem dia 04/10, mas schedule usa 05/10: um avanço D1→D7 agenda 12/10 enquanto a âncora implica 11/10. É contrafactual estático, não teste funcional observado. Desalinhamento pode produzir um fato novo que o checker rejeita; não basta corrigir só o complemento inaugural.

Retentativa por void e CORRECTION_PRESERVE_MANUAL preservam current_due_date e têm exceções existentes; INITIAL replacement incorreta deriva +1 da sua própria local_date. Não alterar contratos de correção sem decidir o timezone da NOVA substituta versus seu contexto de cadeia. Esta superfície integra T11 e a decisão H3 do A4.

## Serviço oficial de mudança

`accounts/services.py:119–192` valida IANA, resolve owner, exige confirmed para mutação, trata mesmo fuso como no-op e usa compare-and-swap owner/id/expected_lock_version. Uma mudança atualiza somente timezone_name, lock_version+1, updated_at do Clock; refresh_from_db; emite SUCCEEDED/CANCELLED/CONFLICT/FAILED por correlation_scope e structured_logging.emit_event. Cancelamento e mesmo valor retornam antes do CAS, portanto não exigir conflito de versão para esses no-ops sem alterar contrato. O service valida IANA antes de confirmed; o fluxo HTTP de cancelar usa o timezone já existente. Não inicia revisão, repair, export, backup ou recomputação histórica.

Não chama record_audit_event e AuditEventCode não contém TIMEZONE_CHANGE. Os eventos são logs operacionais; não existe garantidamente before/after timezone persistido no banco ou no CEI. Não usar logs como reconstrução histórica oficial. Testes existentes em test_accounts.py e test_interface.py cobrem owner, confirmação/cancelamento, valor inválido, versão stale, persistência e correlação; não cobrem invariância completa de REV-004/Priority após troca.

Não é necessária mudança no service para uma troca prospectiva que preserve o histórico. Se a alternativa B escolher contexto durável futuro, isso requer mecanismo de persistência e decisão própria; somente auditar schema e constraints evita reutilização indevida de AuditEvent como payload genérico. Concorrência entre troca e criação de fatos é cenário futuro: a operação deve capturar um contexto consistente e testes precisam observar o resultado, sem presumir serialização que o código não prova.

## Compatibilidade e propagação

`data_management/portability.py:154–166,442–455` e `docs/CEI_EXPORT_1_0.md:46–55` definem campos fechados para ReviewCycle/Review; nenhum timezone inaugural. Attempts e schedule_changes carregam o próprio contexto. Manifest.workspace_timezone é ATUAL, não histórico. Validação pre-DML em portability.py:688–715 reutiliza SQL e complemento Python de REV-004; import pós-carga (:866) e restore em services.py:789 também usam checker. Portanto falso finding pode rejeitar um CEI/restore semanticamente válido após troca. Corrigir apenas CLI ou apenas import criaria divergência entre interfaces oficiais; futuro ajuste deve usar regra canônica única e manter rejeição antes de escrita em negativos.

Alternativa A para Priority/Attempts não exige migration/schema/CEI. Contexto exato inaugural não existe universalmente. Alternativa B com campo em ReviewCycle implica schema+migration e revisão dos campos CEI fechados; com registro em AuditEvent existente não implica necessariamente coluna nova, mas o enum/constraints, semântica, produtores/leitores e CEI fechado ainda precisam de avaliação/decisão — não é solução gratuita e não recupera legado. Backup físico não ganha informação ausente; upgrade também não recupera fatos perdidos. Nenhuma necessidade universal de migration foi comprovada: há trade-off semântico, não aprovação para criar uma.

## Finding e decisão

S8R1-F01: Major / latent semantic risk — REV-004 inaugural usa contexto mutável e pode criar falsos positivos ou mascarar data incorreta se o novo fuso coincidir com ela; impacto propaga a checker/CEI/restore. S8R1-F02: Major / latent semantic risk — R/D podem mudar por relocalização do passado; existe decisão anterior explícita a reconciliar. S8R1-F03: Major / latent semantic risk — correção REVIEW mistura contexto antigo da substituta e atual do schedule. Severidade segue docs/review/code-review.md: comportamento incorreto e integridade; nenhuma corrupção real é declarada nem testada. Bloqueiam aceitação funcional futura enquanto abertos; o planejamento pode ser concluído.

Recomendação: estratégia A para fatos com contexto próprio; B somente prospectiva se aprovada para origens sem contexto; C somente para regras efetivamente independentes de timezone. Rejeitar derivação circular, uso da Attempt antiga como timezone de MANUAL, remoção cega do complemento ou intervalo permissivo apresentado como prova exata. HUMAN_DECISION_REQUIRED para limite do checker legado, contexto futuro/schema/CEI, regra/versionamento de Priority e coerência de correções. Nenhuma solução completa NO MIGRATION / NO FORMAT CHANGE / exatidão inaugural universal foi demonstrada.
