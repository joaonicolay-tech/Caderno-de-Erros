# V1.0-S8 — proteção, riscos, preflight e temporários

Status: PLANNED / NO REAL DATA ACCESSED
Fonte, paths privados, perfil, retenção/descarte: HUMAN_DECISION_REQUIRED

Esta matriz complementa o A4; não concede acesso. Nenhuma decisão privada foi preenchida nem nenhuma contagem/hash de banco real calculada.

## Matriz de risco e proteção

| Risco | Prevenção planejada | Sinal/parada e resposta |
| --- | --- | --- |
| Origem errada/consentimento insuficiente | PILOT_SOURCE e caminho inequívocos aprovados; propriedade/controle, leitura/cópia/uso definidos | HUMAN_DECISION_REQUIRED antes de acesso/cópia |
| Mutação do original por fallback/alias | source offline/read-only; paths efetivos absolutos verificados em cada processo, code/config separados; root distinta sem links | diferença/hash/alvo/source writable: Blocker, parar, preservar; sem recovery no original |
| WAL/journal, copia inconsistente | freeze normal da origem antes baseline, rejeitar estado vivo/sidecars pendentes; backup API read-only do produto | não apagar/checkpoint sidecar original; decisão humana por procedimento específico |
| Backup fisicamente válido mas irrecuperável | manifesto/SHA/bytes/integrity/FK + restore novo/checker/questões/histórico/pendências antes de uso, RNF-038 | falha restore: Blocker/Major, proibir primeira mutação |
| Recovery substitui alvo errado | RECOVERY_TARGET novo próprio; ticket/perfil/arquivo/fingerprint iguais; app parado; pré-backup restaurável | alvo incerto/servidor vivo: não aplicar; perda/mutação original = incidente Blocker |
| Cross-Workspace/associação indevida | escopo e comparação de relações/UUID; dados somente dos Workspaces aprovados | IMMEDIATE_STOP / MAJOR OR BLOCKER; não repetir ataque/fluxo |
| Inconsistência/corrupção | checkpoints 25/0, integrity ok/FK 0 e reconciliação/ledger | qualquer crítico/inexplicado: parar, sem repair/expurgo |
| Representatividade insuficiente | contagens/diversidade naturais e cobertura qualitativa após consentimento; fases temporais distinguidas | PILOT_NOT_REPRESENTATIVE sem PASS; nenhum mínimo artificial |
| Privacidade em logs, uploads/downloads, screenshot | raiz privada/TEMP/TMP/browser dedicado, allowlist, revisão antes de copiar para quality | exposição = finding, parar; bruto protegido, nenhuma publicação |
| Evidência desaparece por limpeza do produto/harness | registro pré-run e cópias+SHA antes de apply/cancel/TemporaryDirectory/cleanup | ausente = evidência ausente, conclusão afetada INCONCLUSIVE; nenhuma exceção PRES-01 herdada |
| Schema/source incompatível/migration nova | IDs/schema/migrations auditados sem executar source; migration existente só cópia previamente aprovada | HUMAN_DECISION_REQUIRED; remediação separada, nunca migrar original |
| Métrica temporal imprecisa | Stopwatch + UTC/offset, evento incident→ready inclui validação e reconciliação; snapshot efetivo provado | INCONCLUSIVE sem PASS; não inventar RPO/RTO/idade/perda |
| Opinião tratada como Major | defeito funcional, observação e limitação separados, severidade com critério de impacto | Major só com impacto demonstrado; preservar observação qualitativa |

## Preflight obrigatório futuro

Todos os itens estão NOT EXECUTED nesta fase. Pendência impeditiva não é aprovação por silêncio.

1. Autorizações de dez itens do gate A4 recebidas, registradas e sincronizadas no contrato antes do acesso; baseline candidata revalidada e lista de mudanças documentais aprovada.
2. Identificação da fonte/versão/schema/perfil/Workspace sem ambiguidade; dados legitimamente controlados; não buscar outros bancos.
3. Usuário confirma app original parado, período de freeze e captura de baseline após parada normal; WAL/journal não pendentes. Não tratar pausa desconhecida como offline.
4. PRIVATE_ROOT e RETENTION_ROOT novas/aprovadas/protegidas, fora do Git/nuvem/fonte; espaço livre adequado aos bytes observados futuramente; ACL/acesso e cópia separada de backup verificados. Sem links/junctions/hardlinks/paths sobrepostos.
5. Registrar classes temporárias antes de criar arquivo; manifest privado com ID/alias/path/hash/status/responsável/destinação; retained copies independentes do scratch.
6. Candidato/runtime/lock/migrations identificados, settings efetivos e alvo esperado conferidos em cada processo; nenhuma impressão de secrets; TEMP/TMP sob raiz privada; downloads/uploads privados.
7. SOURCE apenas processos read-only aprovados; nenhuma app/bootstrap/migrate contra original; SHA/tamanho/sidecars/contagens/semântico conforme A4, sem dump.
8. BACKUP_SOURCE + manifesto validado e restaurado em novo destino; checker 25/0, SQLite ok/FK 0 e UI questões/histórico/pendências/health antes de uso real (RNF-038).
9. PILOT gerado e reconciliado, pré-backup próprio validado/restaurável antes de qualquer mutação, ledger/cobertura/representatividade iniciados; SOURCE pós intacto.
10. CEI_IMPORT vazio e destinos restore/recovery/return novos distintos, code/settings separados; sem bootstrap no CEI_IMPORT; migrations existentes somente onde autorizadas.
11. Plano de medição RNF-035 e retorno revisados; estado pré-operação retido; autorização e operador conscientes de quais cópias podem ser substituídas pelo recovery.
12. Browser/loopback/porta e notificações controlados; seleção manual de arquivos realmente observável ou limitação registrada; políticas de logs/screenshot e sanitização conferidas.
13. STOP/finding/resposta/retention acordados; nenhum Blocker/Major aberto; evidência suficiente e revisão antes da primeira operação relevante.

## Allowlist exata para quality/

Permitidos somente artefatos Markdown/JSON canônicos do A4 contendo: task/run/scenario/checkpoint IDs técnicos; commit e hashes de código/lock/schema; aliases SOURCE/PILOT/BACKUP/CEI_IMPORT/RESTORE/RECOVERY/RETURN; nomes de tabelas/conjuntos/colunas/policies públicas; counts agregados aprovados; códigos/enum/status/exit; igualdade ou diferença de fingerprints; SHA-256 de arquivos inteiros/manifestos/recibos aprovados; tamanho; tempos de eventos técnicos/elapsed/offset; checker totals/IDs de invariantes/SQLite ok/FK count; severidade, descrição de defeito sanitizada, deltas agregados e limitações/proveniência. Fuso/configuração pessoal exata somente no privado por padrão, alias/validity no público. Counts de conjuntos pequenos passam por revisão humana de sensibilidade antes de publicação.

UUIDs reais ficam privados; evidência versionável usa aliases estáveis W01/Q01/A01 e relações entre aliases ou booleanos de preservação. Mapeamento privado não acompanha Git. Não usar hash de enunciado/resposta/nome/email/segredo para aparentar sanitização. Hash integral identifica artefato, não anonimiza seu conteúdo; DB/ZIP continua proibido no Git.

Proibidos: texto real de questões/alternativas/respostas/explanations/notas, nomes/títulos/razões em texto livre, dados sensíveis, email, username Windows, caminhos pessoais/absolutos privados, tokens/secrets/env/credenciais/cookies/sessões, dumps DB, SQLite real ou ZIP CEI real, tickets/result.json brutos contendo active_path, stack traces/URLs com conteúdo/UUID real e screenshots sem sanitização. Logs do checker podem conter IDs técnicos e contexto: não copiar saída bruta para quality. Campo sensitive redacted pelo produto não prova ausência de username/path/email em toda string de mensagem; revisão adicional obrigatória.

Logs: capture bruto apenas quando necessário, protegido e classificado antes da execução. Gerar resumo estruturado por allowlist, sem modificar bruto histórico. Produto emitindo conteúdo sensível → privacy finding e parada; não esconder pela remoção do log. Saídas de comandos/harness também são brutas até revisão.

Screenshots opcionais. Preferir evidência técnica agregada quando suficiente. Se necessárias, captura só janela/página pertinente, sem outras apps/notificações; ocultação prévia e revisão antes da captura; bruto protegido se indispensável; derivado com máscara opaca irreversível, removendo nomes/conteúdo/paths/email/UUID e metadados. Reabrir a derivada para verificar; nenhuma figura necessária neste planejamento.

## Mapa de classes temporárias antes da futura execução

| Classe | Designação padrão planejada | Retenção/prova e descarte |
| --- | --- | --- |
| ORIGINAL | PROTECTED SOURCE / NEVER DISPOSABLE | Nunca descartar/mutar no escopo S8; nenhum cleanup inclui fonte |
| Snapshot/cópia inicial provada | DESIGNATED_FOR_RETENTION | Versão/ID/SHA/bytes e equivalência source; cópia protegida antes de uso/harness |
| PILOT DB e estado final | DESIGNATED_FOR_RETENTION | Baseline/prebackup e final/failure state; preservar com SHA após parar servidor, WAL conforme procedimento seguro |
| SOURCE/pre-PILOT/pré-operação/final backup | DESIGNATED_FOR_RETENTION | SQLite+manifesto inseparáveis, SHA ambos, restore provado; guardar separado do scratch |
| Manifestos de backup/recibos | DESIGNATED_FOR_RETENTION | SHA/método/proveniência/tempos; paths privados só registry privado |
| CEI ZIP real | DESIGNATED_FOR_RETENTION | ZIP/manifest/checksums/contagens privados e verificados; Git só resumo allowlist |
| Restore pré-uso e RESTORE_TARGET final | DESIGNATED_FOR_RETENTION | Destino validado e recibos/snapshots essenciais, SHA e reconciliação |
| RECOVERY/RETURN DB e estados pré/pós | DESIGNATED_FOR_RETENTION | Checkpoints/hash/timing/result essenciais; nenhuma prova destrutiva no original |
| Ticket/candidato/prebackup de UI | DESIGNATED_FOR_RETENTION | Copiar e conferir SHA em retention antes do apply/cancel; ticket bruto contém active_path privado |
| Logs necessários/failure receipts | DESIGNATED_FOR_RETENTION | Brutos privados quando necessários, resumos sanitizados versionáveis; preservar FAIL e reteste separados |
| Screenshots necessárias | DESIGNATED_FOR_RETENTION | Bruto protegido somente se necessário; derivado revisado, política de descarte aprovada |
| Screenshots opcionais não usadas | DISPOSABLE / NOT_REQUIRED_FOR_FINAL_EVIDENCE | Só se declaradas não necessárias antes; não descartar incidental privacy leak sem decisão |
| Temp de upload/apply/SQLite API/harness | DISPOSABLE / NOT_REQUIRED_FOR_FINAL_EVIDENCE | A cópia essencial/recibo já deve estar designada e retida independentemente; não contar temp autoapagado como preservado |
| Pytest/cache scratch sintético futuro | DISPOSABLE / NOT_REQUIRED_FOR_FINAL_EVIDENCE | Só em ensaio/gate autorizado separado, basetemp novo; manifests/logs/receipts necessários retidos |

Manifest privado por artefato: run/scenario/class/alias/private_path/source_alias/created_at/size_bytes/sha256/designation/retained_path/verified_sha/owner/disposition_event/status. Espelho quality/v10-s8-retention-map.json só aliases e metadados permitidos. Nenhum path absoluto privado publicado. Registro antes do run; completar hashes à criação e cópia; conferir após cada prova, antes de cleanup e encerramento.

Retenção/descarte não definido automaticamente: responsável deve escolher local/ACL, quem acessa e evento/prazo. Retained artifacts permanecem até aceite humano, reconciliação/retention verificadas e A8 deep; findings/incident mantêm retenção até decisão específica. Nenhuma exclusão de backup/user DB/raw necessária nesta fase. Futuro descarte só lista explícita aprovada e path resolvido comprovadamente dentro da raiz destinada; sem glob que alcance original, sem suposição de secure erase. Ausência deve ser reportada honestamente e seu impacto avaliado; 11 artefatos sintéticos PRES-01 históricos não isentam qualquer artefato real S8.
