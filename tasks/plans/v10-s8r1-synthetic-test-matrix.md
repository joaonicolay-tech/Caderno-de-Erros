# V1.0-S8R1 — matriz de testes sintéticos FUTUROS

Status: PLANNED / NOT EXECUTED. Os cálculos de conversão abaixo foram conferidos isoladamente por datetime/ZoneInfo do Python local, com literais UTC fixos; não são PASS de teste funcional, checker, SQLite, gate ou A8. Nenhum import Django, acesso SOURCE ou banco foi utilizado para essa conferência.

## Oráculos e fronteiras

Zonas exatas: `Brazil/Acre` e `America/Sao_Paulo`. Usar FixedClock(Instant(...)) e injetar Calendar/Clock; congelar também auto_now/created_at quando forem parte do oráculo. Não consultar SystemClock nem timezone do sistema. Locale de exibição não participa de cálculo.

| UTC fixo | Brazil/Acre | America/Sao_Paulo | Datas civis |
| --- | --- | --- | --- |
| 2026-10-05T02:59:59Z | 04/10 21:59:59 (-05) | 04/10 23:59:59 (-03) | iguais |
| 2026-10-05T03:00:00Z | 04/10 22:00:00 (-05) | 05/10 00:00:00 (-03) | diferentes; meia-noite SP |
| 2026-10-05T04:00:00Z | 04/10 23:00:00 (-05) | 05/10 01:00:00 (-03) | diferentes |
| 2026-10-05T04:59:59Z | 04/10 23:59:59 (-05) | 05/10 01:59:59 (-03) | diferentes; antes da meia-noite Acre |
| 2026-10-05T05:00:00Z | 05/10 00:00:00 (-05) | 05/10 02:00:00 (-03) | iguais; meia-noite Acre |
| 2026-10-05T12:00:00Z | 05/10 07:00:00 (-05) | 05/10 09:00:00 (-03) | iguais; controle |

Para avaliação fixa 2026-10-05T12:00:00Z, today=05/10 em ambos. REVIEW histórica no Acre às 04:00Z: 2026-09-06 tem local_date 05/09 (idade30), mas relocalização SP dá 06/09 (idade29); 2026-08-07 dá 06/08 (60) versus 07/08 (59); 2026-07-08 dá 07/07 (90) versus 08/07 (89). Cobrir 0/-1,29/30,59/60,89/90, além de mesmas datas. Oráculo A usa a data gravada independentemente do fuso novo.

Para novo schedule na fronteira 04:00Z de 05/10: data-base Acre 04/10, SP 05/10. Somar offsets +1/+7/+14/+30 resulta respectivamente em Acre 05/10,11/10,18/10,03/11 e SP 06/10,12/10,19/10,04/11. Isso é tabela de decisões possíveis conforme etapa/resultado, não as quatro datas de um único ciclo ancorado no mesmo instante. A trajetória deve usar instante real distinto por resposta; intervalos são sucessivos e erro reinicia D1.

## T1–T10 obrigatórios

| ID | Arrange/ação futura | Oráculo objetivo e negativos | Referências/testes-alvo |
| --- | --- | --- | --- |
| T1 | Workspace sintético Acre vazio; change_workspace_timezone com owner, confirmed=True, versão correta e Clock=12:00Z | Apenas timezone_name,lock_version,updated_at mudam; nenhum fato criado; checker 25/0 antes/depois. Cancelamento, mesmo fuso, IANA inválido, outro owner e stale version na mutação não gravam. | test_accounts.py; test_interface.py |
| T2 | Attempts INITIAL e REVIEW em cada instante da tabela, acerto/erro, VALID e cadeia VOIDED; trocar em Clock=12:00Z | occurred_at/timezone_name/local_date/is_correct/revision/IDs históricos iguais; ATT-002 saudável. Corromper local_date somente em cópia sintética negativa deve ser detectado; não confundir migração de fuso com repair. | test_initial_attempt.py; test_review_completion.py; test_integrity_checker.py |
| T3 | Criar ciclos QUESTION_ACTIVATION, INITIAL_ERROR, MANUAL INCLUSION e MASTERY_REOPEN em 04:00Z; MANUAL ligado a Attempt mais antiga com outro fuso | Acre D1=05/10, first/current_due_date imutáveis pela troca; REV-004 não rejeita fato válido pela configuração atual. INITIAL_ERROR prova pela própria âncora. Inaugurais sem contexto seguem H1, não PASS exato fictício. | test_question_catalog.py; test_v05_s2a.py; test_v05_s5_domain.py |
| T4 | Reagendar sinteticamente antes da troca com ReviewScheduleChange/AuditEvent timezone=Acre, motivo/correlação fixos; trocar | first_due_date intacta; previous/new_date e timezone do change/audit intactos. Reagendamento NOVO usa SP. Cópia com audit/change divergente continua finding, rollback do comando em falha do audit preservado. | test_v05_s2a.py; test_integrity_checker.py |
| T5 | Caminhos de sucesso D1→D7→D14→D30, erro em cada etapa/reset e D30 final; respostas em UTC fixos que cruzam datas; troca entre respostas | Reviews antigas preservadas; cada resposta nova usa contexto definido e +dias civis corretos; 25/0 em válidos; sequência/stage/offsets errados detectados. Cobrir respostas tardias sem compressão. | test_learning_foundation.py; test_review_completion.py; test_integrity_checker.py |
| T6 | >=3 Questions por Subject, revisão às 04:00Z nos três limites; controle às 12:00Z; evaluation fixo=05/10 12:00Z; mudar só Workspace | Com today igual, R/D mantêm membership pelo fato sob A/H2 aprovada; comparar IDs incluídos/contagens/R/D/score/state/reasons. Vetor D: única baseline para cada uma das 3 Questions em 06/09 04:00Z e recente em 04/10 12:00Z; implementação atual perde baseline ao relocalizar (3 comparáveis→0). Vetor R: evento 08/07 04:00Z e outro recente por Question muda 90→89, podendo 0→3 elegíveis. Confirmar thresholds 2 REVIEWs/3 Questions; pesos/frações/ties inalterados. Cenário 04:00Z de avaliação permite delta legítimo por today e deve atribuí-lo a O/Domain, não mascarar R/D. | test_priority_integration.py; test_priority_policy.py |
| T7 | Domain com evidência própria Acre e evaluated_on controlado igual; depois today diferente na virada; fronteiras idade60/61,120/121,180/181,365/366 | Datas/evidências e índice/suficiência equivalentes com mesmos inputs; confiança envelhece só pelo evaluated_on permitido, sem conversão do passado. No-op do GET, MasteryStateEvent preservado; eligible C_h=40 e mastery C_q=80 em fronteiras. Troca inversa com data de evidência “futura” registra decisão/erro explícito, não clamp inventado. | test_domain_evidence.py; test_domain_policy.py; test_v05_s5_domain.py |
| T8 | Checker completo nos mesmos bancos sintéticos antes/depois; positivo/negativo por origem e por instante; ambos runtimes canônicos Python/SQL | 25 checks/0 findings e exit0 nos válidos segundo regra aprovada; invalid sequence/transition/Attempt local_date/offset +1/+7/+14/+30 continuam detectados. Legacy sem contexto: caso válido e caso inválido com mesmas colunas demonstra limitação H1; nenhuma aceitação permissiva vendida como exatidão. Checker zero DML tentado/completado, native total_changes=0 e fingerprint igual. | test_integrity_checker.py; test_v05_s2a.py; test_v05_s5_domain.py |
| T9 | Snapshot canônico de todas as linhas históricas/IDs/FKs/timezones/datas antes/depois da troca isolada; cópia física de DB sintético se útil | Bytes serializados das linhas históricas iguais; equivalência semântica e timeline/order/event fields iguais. DB INTEIRO pode mudar por Workspace; não exigir mesmo hash físico global. Allowlist exata de três campos Workspace; nenhum novo AuditEvent funcional na troca atual. | test_accounts.py + regressão focada futura |
| T10 | Após troca, criar Attempt ordinária, ativação, inclusão/reopen e reagendamento em 04:00Z fixo; queue/dashboard/status e explicit-period analytics | Nova Attempt SP local_date=05/10; nova D1=06/10; novo schedule/change usam SP; pendências antigas conservam datas; today novo=05/10. Métricas de período explícito antigo iguais; completed_today/overdue podem mudar legitimamente. Sem operação real/PILOT. | test_initial_attempt.py; test_review_completion.py; test_analytics.py; test_question_search.py |

## Complementos indispensáveis

| ID | Escopo | Oráculo |
| --- | --- | --- |
| T11 | Replacement INITIAL/REVIEW após troca; void sem substituta, CORRECTION_PRESERVE_MANUAL; tip Acre e nova operação SP às 04:00Z | Resolver H3 antes: substituta e agenda usam a mesma semântica decidida; sem alteração de predecessora/fatos concluídos; checker saudável. Cenário atual REVIEW D1→D7 demonstra 11/10 versus 12/10; não ocultar por exceção ampla. |
| T12 | CEI V0.5/V1 e backup/restore/upgrade sintéticos, antes/depois da troca, todos origin_kind/manual_purpose e histórico misto | Regra canônica compartilhada em CLI/pre-DML/post-import/restore. Preservar formato CEI e allowlist se A/C; schema fingerprint/migrations iguais. Negativos rejeitados ANTES de DML, com attempted/completed=0, total_changes=0 e fingerprint; round trip sem reescrita histórica. B exige decisões e testes adicionais antes de executar. |
| T13 | Concurrency: duas mudanças com mesma expected_version e criação/correção/reagendamento concorrente com troca | Um CAS concorrente vence por versão; capturar timezone/data-base coerentes de cada operação. Não presumir atomicidade global nem adicionar locks sem evidência; faults/cancel/noop/owner invalid sem mutação indevida. |
| T14 | Virada anual, DST histórico, meses/ano bissexto e aliases IANA | Fixtures com instantes fixos e base tz local; +dias civis, não 24h/168h. Não presumir offset -05/-03 em TODAS as datas históricas; conferir vetores específicos antes de executar. |

Executar futuramente em `tmp_path`/DB de teste comprovadamente isolado. Confirmar DSN/paths sintéticos antes de manage.py/pytest; nenhuma descoberta/abertura de development.sqlite3. Não criar fixture que use dados pessoais. Negativos usam cópia descartável e não apagam evidência RED anterior. Gate integral `scripts/quality.ps1` e A8 deep somente após implementação autorizada, com evidência observada. Nenhum teste desta matriz foi executado nesta fase.
