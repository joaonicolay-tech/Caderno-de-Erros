# V1.0-S8 — roteiro futuro do piloto

Status: PLANNED / NOT EXECUTED
REAL_DATA_ACCESS: NOT YET AUTHORIZED
PILOT_EXECUTION: NOT YET AUTHORIZED

Este roteiro depende integralmente do gate final de v10-s8-controlled-real-pilot-plan.md e do preflight de v10-s8-data-protection.md. Nenhum passo é autorização de execução atual. Fonte ainda HUMAN_DECISION_REQUIRED; nenhum registro, contagem ou resultado real observado.

## Registro por cenário

ID, checkpoint, alias do alvo/perfil efetivo, pré-condição, ação consentida, instante/relógio, deltas esperados/observados, evidência privada e sanitizada, resultado (NOT_STARTED / EXECUTED_PASS / FAIL / INCONCLUSIVE / NOT_OBSERVABLE / NOT_APPLICABLE justificado), limitações e finding. Não preencher PASS sem observação; um cenário pode ter observações read-only e mutações distintas. Alterações naturais só em PILOT, com pré-backup restaurável e ledger que explique mudanças de contagens/history. Nenhuma remediação durante roteiro.

| ID / checkpoint | Ação futura e pré-condição | Observação e critério |
| --- | --- | --- |
| P00 / CP0 | Conferir consentimento completo, fonte/paths/perfil, parada original, raiz nova/ACL/TEMP/retention | Fonte inequívoca, ORIGINAL read-only, nenhum alvo de escrita ali; snapshot e provas físicas sem alteração inexplicada |
| P01 / CP1 | Criar/validar backup SOURCE e restaurar em novo PRE_USE_RESTORE, antes de uso normal | Manifesto/SHA/bytes, SQLite ok/FK 0, checker 25/0, estado reconciliado; abrir questões/histórico/pendências/health na cópia de prova RNF-038 |
| P02 / CP2 | Preparar PILOT, baseline/representatividade e pré-backup próprio validado/restaurável | Workspace/fuso/configuração, contagens/diversidade reais e lacunas; 25/0/ok/0, ORIGINAL intacto, perfil/caminho efetivos iguais aos autorizados |
| P03 / CP3 | Cadastro de questão no uso natural autorizado na PILOT; se não houver necessidade natural, registrar limite | Question/revisão/alternativas e estado coerentes; erro/validação compreensíveis, IDs privados e deltas registrados; nenhum dado criado no original |
| P04 / CP3 | Tentativa consentida de questão elegível | Resposta/tipo/data civil/fuso/revisão usados preservados, resultado observado; sem imprimir resposta em relatório |
| P05 / CP3 | Erro e classificação naturalmente aplicáveis | Tentativa/classificação/categoria e agenda coerentes; se erro não ocorrer legitimamente, NOT_OBSERVABLE; não marcar alternativa falsa para fabricar falha |
| P06 / CP3 | Correção de tentativa/classificação aplicável e consentida | Cadeia de substituição/anulação/histórico preservada, sem sobrescrever fato antigo; delta e invariantes comprovados |
| P07 / CP3 | Revisão disponível legitimamente | Pendência/ciclo/questão/agenda escopados; conclusão/avanço/reset pela REV-FIXA-1.0; registrar etapa e data/fuso sem manipular relógio |
| P08 / CP3 | D1 disponível, ou histórico existente | EXECUTED ou HISTORY_OBSERVED_ONLY distintos; ausência NOT_OBSERVABLE; expected próximo estado conforme resposta real |
| P09 / CP3 | D7 disponível, ou histórico existente | Mesma distinção; nenhuma inferência de execução D7 por observar D1 |
| P10 / CP3 | D14 disponível, ou histórico existente | Mesma distinção; histórico não alterado para avançar fase |
| P11 / CP3 | D30 disponível, ou histórico existente | Conclusão só se resposta correta legitimamente observada; ausência de fase não vira PASS |
| P12 / CP3 | Consulta/lista/detalhes/histórico existentes | Consistência entre questões, tentativas/revisões/histórico; paginação/navegação escopadas; sem conteúdo pessoal em evidência |
| P13 / CP3 | Filtros e SavedFilter aplicáveis | Estado/critério/resultado correspondentes; referências antigas incompatíveis explicitadas sem repair; nome de filtro privado |
| P14 / CP3 | Categorias: observar; editar/arquivar/mesclar somente ação natural aprovada | Categoria/histórico/filtros mantêm semântica e Workspace; action ledger e checkpoint após mutação; sem mudança original |
| P15 / CP3 | Domain e explicação sobre dados disponíveis | Índice/confiança/suficiência/DOMINATED distinguíveis; NO_DATA/limites não viram zero; leitura não cria lifecycle silencioso |
| P16 / CP3 | Priority e explicação quando elegível | Recomendação opcional, não altera fila/agenda; COLLECT_MORE_EVIDENCE aceitável quando legítimo; fórmula/policy congeladas |
| P17 / CP3 | Edição/enriquecimento/correção de gabarito quando naturalmente necessária e autorizada | Revisão usada por Attempt preservada; correção com motivo/história; distinguir edição não crítica e correção crítica sem conteúdo em Git |
| P18 / CP4–5 | Export funcional CEI pela tela Dados na PILOT, validar e importar em CEI_IMPORT novo/migrado/vazio | Formato/manifest/checksums/21 sets/tipos/UUID/policies/invariantes; reconciliar função/história e derived separadamente; checker 25/0/ok/0; nunca merge/source |
| P19 / CP4–5 | Backup pós-fluxos da PILOT, validate_backup e restore_backup em novo RESTORE_TARGET | Par/SHA/bytes/contagens/fingerprint; restore funcional provado, questões/histórico/pendências; backup e original preservados |
| P20 / CP6 | Recovery preparado na UI somente RECOVERY_TARGET próprio, preservar ticket/candidato/prebackup, parar servidor e aplicar offline | Seleção manual realmente observada ou limitada; RESTORED, banco/ticket corretos, RPO/RTO observados, 25/0/ok/0, health/reconciliação; pré-backup disponível |
| P21 / CP6 | Provar retorno ao estado pré-operação em NOVO RETURN_TARGET a partir do pré-backup validado | Retorno sem mutar ORIGINAL, SHA/contagens/semântico equivalentes e app saudável; não exigir provocar corrupção/perda ou fault injection em dado real |
| P22 / todos | Usabilidade cotidiana, Windows/browser/loopback e prevenção de erro humano | Passos confusos, mensagens/recuperação/navegação/velocidade percebida; observações separadas de defeitos/limitações; registrar browser/versão/proveniência reais |
| P23 / CP7 | Encerrar, checker/SQLite/FK finais, ORIGINAL pós, backup final/ledger/retention verificada, findings/cobertura | Original intacto e artefatos designados presentes com SHA; avaliar representatividade e limites RNF-035; revisão A8 deep futura, sem promoção S9 |

## Encerramento e limites

Sem mínimo de registros, duração ou participantes. Avaliação qualitativa deve mostrar que dados/estado permitiram jornadas centrais e recuperação. P08–P11 legítimos podem ser história/ausência, com justificativa; se isso ou outras lacunas impedir representatividade, PILOT_NOT_REPRESENTATIVE sem PASS, sem criar dados no original. Histórico S3–S7 continua histórico e não substitui uso real S8.

Cross-Workspace indicado, privacidade exposta, checker crítico/inexplicado, corrupção/perda, backup/restore inválido, original mudado, fonte/alvo/consentimento ambíguos ou migration nova: IMMEDIATE_STOP; preservar evidência privada, classificar Blocker/Major e pedir remediação separada. Não executar próximo cenário para confirmar novamente.
