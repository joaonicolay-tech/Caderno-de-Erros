# V1.0-S8 — A4 piloto final local real controlado

Status: READY FOR HUMAN DATA AUTHORIZATION
Decision: S8_A4_READY_FOR_HUMAN_DATA_AUTHORIZATION
Stage: AUTHORIZED / PLANNING
REAL_DATA_ACCESS: NOT YET AUTHORIZED
PILOT_EXECUTION: NOT YET AUTHORIZED
S9–S10: NOT AUTHORIZED

## 1. Baseline, classificação e autoridade

Em 2026-10-03, START_TIME 20:46:39 -03:00: HEAD == origin/main == dcccb8950a7752d03461665e0a4952c8a9bc663b; git status --short vazio; git diff --check exit 0. Referência remota local verificada, sem fetch. S7 checkpoint 6879e6ad e reconciliação posterior dcccb895 distinguem-se; não há mismatch.

S1–S7, S2R1–S2R5, S6R1, S7R1/S7R2 concluídos documentalmente. S6_REVALIDATED; S7-F01/F02 RESOLVED; A8 S7 APPROVED WITH NOTES (0/0/2). tasks/current era NO_TASK_AUTHORIZED; S8–S10 não autorizadas antes desta mensagem.

S8: L / critical (override humano do L/high do plano V1); migration NO; dados pessoais futuros YES, acesso atual NO. A7 autorizado GPT-6.1 Sol High (override humano); runtime não verificável independentemente. A8 futura deep, não executada agora. Sem modificação funcional, migration, testes, gate integral, Git publication ou piloto.

Objetivo futuro: uso pessoal real privado do candidato em Windows 11 x64/local/loopback, com original protegido, recuperação comprovada e evidência sanitizada. Fora: público, deploy/hosting, multiusuário, feature/redesign, migration nova, promoção, tag/release, S9/S10. Fontes da auditoria e achados de planejamento: quality/v10-s8-planning-result.md. Roteiro: v10-s8-pilot-route.md. Proteção/riscos/checklist/temporários: v10-s8-data-protection.md.

## 2. Origem e consentimento — decisões pendentes

PILOT_SOURCE: HUMAN_DECISION_REQUIRED
SOURCE_PATH_OR_ID: HUMAN_DECISION_REQUIRED
PILOT_PROFILE: HUMAN_DECISION_REQUIRED
PRIVATE_ROOT / RETENTION_ROOT: HUMAN_DECISION_REQUIRED
COUNTS / DIVERSITY / REPRESENTATIVENESS: NOT OBSERVED

Classes possíveis: instalação pessoal atual; cópia explícita fornecida pelo usuário; banco derivado de uso pessoal autorizado; outro source especificamente aprovado. Nenhuma selecionada. Não procurar bancos nem aceitar identificação por probabilidade. Caminhos padrão do produto são configuração, nunca identificação de uma fonte real.

A próxima autorização deve identificar classe, arquivo/caminho absoluto ou identificação inequívoca, instalação/revisão produtora, perfil, Workspace escopado (identificação privada), fuso conhecido se disponível, responsável e limites. Não solicitar conteúdo de questões, respostas, senha ou segredo para identificar a origem. IDs/caminhos permanecem em registro privado, aliases no Git. Se versão/schema ou fonte forem incertos, parar antes de copiar/inicializar.

Consentimento deve declarar propriedade/controle legítimo, leitura necessária para validação e representatividade, cópia, uso em cópia isolada, export/backup/restore/recovery em destinos aprovados e evidência sanitizada. Proibição de publicação de dados pessoais é obrigatória. O responsável aprova também quem terá acesso local, local protegido, retenção/descarte e passos de retorno. Ausência de qualquer campo mantém acesso e piloto bloqueados.

## 3. Isolamento e identidade de alvos

Desenho futuro: ORIGINAL → prova física/semântica read-only → BACKUP_SOURCE + manifesto → restore pré-uso validado → cópia PILOT → fluxos → BACKUP_PILOT → destinos novos CEI/RESTORE/RECOVERY → reconciliação → retenção/descarte aprovado.

Sob PRIVATE_ROOT aprovado, fora do repositório/Git, nuvem/sincronização e diretório da fonte: source-snapshot/, pilot/, backups/, cei-import/, restore/, recovery/, logs/, tmp/. RETENTION_ROOT separado, protegido, não descartável junto com scratch. Cada run tem ID aleatório e raiz nova inexistente. Destinos absolutos, sem links/junctions/hardlinks ou sobreposição com fonte; comprovar identidade de arquivos, volume/pasta e origem, não apenas comparar strings. Não reutilizar destinos nem sidecars existentes. ACL Windows verificada pelo operador: mode=0700 do Python não prova ACL restrita no Windows.

Code/runtime do candidato identificado por baseline e hashes do lock/schema/migrations, com instalação isolada sem bancos/config pessoal herdados. Perfil humano explicitamente selecionado: development (CEI_DEVELOPMENT_DB) ou production_local (CEI_PRODUCTION_LOCAL_DB, segredo somente no ambiente privado). Nunca fallback aos padrões var/development.sqlite3 ou var/production_local.sqlite3. DJANGO_SETTINGS_MODULE explícito em cada processo/--settings; start-local recebe -Profile e porta loopback escolhidos. Não selecionar perfil automaticamente nem alterar código para criar perfil novo.

Antes de cada comando, registrar privadamente DATABASES.default.NAME resolvido e comparação com o alias esperado, CEI_PROFILE, settings, PID/porta; evidência pública apenas igualdade esperada/observada e aliases. Leitura de configuração sem abrir conexão só após gate humano. Variáveis não bastam: conferir settings efetivos. Nenhum processo de app contra SOURCE, snapshot protegido ou BACKUP_SOURCE. Recovery é configurado apenas para arquivo ativo sob recovery/; seu cei-recovery/ fica ali. Import CEI tem outro processo/destino, não compartilhar configuração da fonte.

TEMP/TMP e download directory do navegador ficam sob a raiz privada do run; navegador dedicado sem sincronização/extensões e notificações. Registrar local de upload/download: CEI/backup podem cair na pasta padrão do navegador. Não enumerar/matar processos alheios. O responsável confirma parada da aplicação original e estabilidade, mantendo-a parada durante o intervalo de prova.

## 4. Proteção do original e pré-backup

Original: READ-ONLY SOURCE / DO NOT MUTATE. O piloto usa ISOLATED PILOT COPY. Depois da autorização, usuário encerra normalmente a origem antes do primeiro hash de referência. Capturar SHA-256 físico, tamanho, LastWriteTimeUtc e estado de sidecars privadamente. Timestamp isolado não demonstra igualdade; LastAccessTime não é prova de mutação. Registrar hashes/ausência dos sidecars relevantes, sem interpretar SHM transitório como fato de domínio.

Fonte offline estável e sem WAL/journal pendente é pré-condição do procedimento normal. Nunca apagar sidecars, executar checkpoint, mudar journal_mode ou usar immutable=1 em banco vivo/com WAL para contornar. Se parada normal não deixar estado inequivocamente consistente ou houver WAL que exija outro procedimento, HUMAN_DECISION_REQUIRED antes de captura/cópia; nenhuma exclusão manual. Diferença física sem explicação documentada é parada, mesmo com igualdade semântica.

Provas source pré/pós read-only, somente após autorização: PRAGMA integrity_check; PRAGMA foreign_key_check; catálogo checker 25/0; contagens por conjunto/tabela e fingerprint semântico escopado. Fonte compatível offline: conexão SQLite URI mode=ro; immutable=1 apenas sobre artefato estável validado sem WAL. Se checker exigir schema ausente na origem, parar e pedir plano específico de compatibilidade em cópia; não migrar original, não tratar incompatibilidade como PASS. Para minimizar abertura da fonte, validar primeiro snapshot preservado e ligar contagens/fingerprints à origem por igualdade física comprovada; registrar explicitamente essa proveniência, sem alegar consulta direta não realizada.

Pré-backup SOURCE usando backup_sqlite (serviço abre source mode=ro, SQLite backup API; não é cópia casual de arquivo vivo). Configuração SOURCE apenas nesse processo read-only, sem runserver/migrate/bootstrap. Comandos futuros, executados da instalação candidata, após gate e resolução privada de settings/paths:

```powershell
& $pilotPython $pilotManage backup_sqlite --output $sourceBackup --settings=$approvedSettings
& $pilotPython $pilotManage validate_backup --backup $sourceBackup --settings=$approvedSettings
& $pilotPython $pilotManage restore_backup --backup $sourceBackup --destination $preUseRestore --settings=$approvedSettings
```

$pilotPython/$pilotManage identificam runtime/código; $approvedSettings é perfil aprovado; paths absolutos novos provados no preflight. O processo de backup tem SOURCE como banco efetivo; restore não adota SOURCE e exige destino novo distinto. Checkers/abertura de app subsequentes só com configurações separadas para cópias. Comandos são templates não executados e não fornecem autorização. Conferir $LASTEXITCODE imediatamente após cada comando (0 exigido), preservar saída privada sem conteúdo em Git. Não usar --database para passar um caminho: é alias Django.

Manifesto físico CEI-SQLITE-BACKUP / 1.0 contém format, format_version, created_at UTC, size_bytes e sha256. Guardar SQLite e .manifest.json juntos, SHA de ambos, tamanho, contagens/fingerprint/schema/migrations em recibo privado suplementar. O manifesto do produto não contém checker, FK ou contagens; não alterar manifesto para acrescentá-los. Validar par com validate_backup (integrity=ok/FK=0) e restore em destino novo; no destino comprovar checker 25/0, questões/histórico/pendências na UI (RNF-038), reconciliação e health. Hash isolado não autentica origem nem prova recuperabilidade.

RNF-038 deve passar ANTES da primeira mutação de uso real na cópia PILOT. Não abrir a cópia PILOT para uso normal antes disso; smoke de recuperação acontece só em destino restaurado destinado a essa prova, com pré/pós de possíveis sessões/receipts. Em seguida gerar PILOT a partir de backup válido, provar equivalência e criar/validar seu pré-backup próprio antes da primeira mutação. Pré-backup também antes de CEI/restore preparado/recovery relevante. Backups retidos até aceite humano, A8 e reconciliação, nunca limpeza automática.

Original pós-captura, pós-provas e encerramento: SHA/tamanho + contagens/fingerprint aplicável iguais ao baseline congelado, nenhuma diferença inexplicada. Estado semântico pode ser derivado de snapshot idêntico com método explícito. Não comparar SHA físico de snapshot gerado pela backup API com SOURCE como requisito: reorganização física pode existir; source deve permanecer fisicamente igual a si mesmo, snapshot/restore iguais no escopo contratual e semanticamente equivalentes ao SOURCE.

## 5. Fingerprints e reconciliação

Recibo privado antes/depois: revisão candidata, hashes schema/migrations, SHA físico/manifesto, bytes, timestamps, contagens, SHA semântico e versão do algoritmo. Serialização canônica: tabelas/colunas em ordem fixa, linhas por PK estável, tipos/null preservados (null distinto de vazio; decimal sem conversão float), instantes normalizados com significado preservado; hash incremental sem dump textual em log. Script/harness somente na futura autorização, revisado antes de ler dados; nenhum script que opere dados criado/executado agora.

SQLite backup/restore compara todas as tabelas persistidas, distinguindo metadados operacionais legitimamente alterados no smoke por ledger de ações. CEI compara os 21 conjuntos fechados, UUID/relações/policies/história; exclui usuários/sessões/receipts/cache/derived conforme contrato, nunca exigir igualdade byte-a-byte do ZIP. Recalcular Domain/Priority por mesma policy/fuso/data de avaliação e registrar diferenças legítimas; sem modificar relógio global. Igualdade semântica não autoriza descartar diferença inexplicada do original. Hashes publicados apenas de artefatos inteiros/recibos aprovados, sem hashes por pergunta/resposta suscetíveis a identificação.

## 6. Representatividade e tempo

Após autorização, observar Workspace/fuso/configuração, questões, tentativas, erros/categorias, histórico, ciclos/revisões e diversidade de estados/fluxos. Registrar contagens reais observadas, cobertura e lacunas sem texto pessoal; nenhum mínimo numérico inventado. Uso real significa dados de uso normal do responsável; criação natural no PILOT deve ficar distinguida de dados existentes. Não fabricar registros no original nem usar complemento sintético para declarar representatividade real.

D1/D7/D14/D30 observadas somente se disponíveis legitimamente na agenda/história. Não manipular relógio, datas ou dados reais para produzir fases. Histórico observável de etapa não equivale a executar revisão daquela etapa. Cada etapa registra EXECUTED / HISTORY_OBSERVED_ONLY / NOT_OBSERVABLE, com justificativa. Ausências avaliadas qualitativamente; se impedirem percorrer fluxos centrais, PILOT_NOT_REPRESENTATIVE e sem PASS. Sem obrigação de X dias/horas. Terminar quando fluxos representativos observáveis, recuperação e evidência forem suficientes; cobertura insuficiente permanece sem PASS.

## 7. Roteiro e checkpoints

Executar futuramente roteiro separado v10-s8-pilot-route.md; cada cenário anota pré-condição, ação natural/consentida, expectativa de delta, resultado observado, checker/SQLite/FK e evidência privada/sanitizada. Sem resultado de teste por presença de código. Qualquer indicação cross-Workspace → IMMEDIATE_STOP / MAJOR OR BLOCKER; não repetir com dados reais. Não criar segundo Workspace pessoal para injetar ataque; ausência de diversidade limita conclusão do piloto, evidências sintéticas S3/S6 permanecem atribuídas a seus próprios escopos.

| Checkpoint | Momento | Evidência exigida no futuro |
| --- | --- | --- |
| CP0 | gate humano + freeze source | origem/perfis/paths/retention; source estável, SHA e proveniência; 25/0, SQLite ok/FK 0 na source ou snapshot ligado explicitamente |
| CP1 | backup SOURCE e restore pré-uso | manifesto/SHA/bytes, restore novo, reconciliação, checker 25/0, SQLite ok/FK 0, questões/histórico/pendências/health |
| CP2 | PILOT preparado, antes de uso | banco efetivo, pré-backup restaurável, baseline contagens/semântico/schema/migrations, 25/0/ok/0, source igual |
| CP3 | após cadastro/tentativa/erro e após correções/revisões/categorias | ledger de deltas legítimos e história preservada; checker 25/0, SQLite ok/FK 0; parar antes de próxima ação se divergir |
| CP4 | antes de cada backup/export/operação relevante | quiescência, alvo, checker 25/0/ok/0, hashes/contagens e pré-backup válido |
| CP5 | após import CEI e restore | destino novo/vazio adequado, round trip semântico/UUID/policies, 25/0/ok/0, smoke em cópia |
| CP6 | pré/pós recovery offline e retorno | parada comprovada, ticket/prebackup/destino, RESTORED, RPO/RTO, reconciliação, 25/0/ok/0 e health |
| CP7 | encerramento | checker 25/0/ok/0, ledger final, original intacto, retenção verificada, findings/cobertura/usabilidade e A8 deep |

Check_integrity exit 0 só aceito junto de 25 checks/0 findings; exit 2 ou 3 impede continuar. Integrity_check deve retornar apenas ok; foreign_key_check zero linhas. Qualquer finding crítico/inexplicado encerra imediatamente; não reparar dados, expurgar auditoria ou reduzir checker para obter PASS.

## 8. CEI, restore e recovery

CEI export somente PILOT, pela tela Dados/export funcional do produto (não existe comando management export_cei). Guardar ZIP real privado. Validate_export/import_into_empty verificam formato/manifesto/membros/checksums/contagens/UUIDs/relações/policies/tipos/migrations/schema e invariantes antes de DML. Não prometer que texto genérico de erro da CLI prova zero-write. Import em destino NOVO funcionalmente vazio (sem Workspace), previamente migrado somente com migrations existentes do candidato, sem bootstrap. Registrar vazio antes de import; preservar UUID e história; comparar 21 conjuntos e derived separadamente. Sem merge/original, remapeamento, coerção ou repair.

```powershell
# Configuração efetiva exclusivamente CEI_IMPORT; nunca SOURCE/PILOT.
& $pilotPython $pilotManage migrate --settings=$approvedSettings
& $pilotPython $pilotManage import_cei --package $privateCeiZip --settings=$approvedSettings
```

Migrate de destino vazio e aplicação de migrations já existentes em cópia compatível só poderão ocorrer na autorização futura específica. Fonte com migration pendente/necessidade de conversão exige decisão humana; nenhuma migration nova S8. Negativos/fault injection não são obrigatórios no dado real; evidência sintética S6 mantém seus limites e eventual novo ensaio exige alvo descartável e autorização específica.

Backup PILOT após fluxos: processo de backup configurado PILOT, arquivo novo privado, validate + restore em destino novo. Restore é SEMPRE novo destino e não muda banco ativo. Recovery utiliza outro banco ativo isolado previamente gerado por restore (RECOVERY_TARGET), nunca SOURCE nem o PILOT de uso. Preparar preview/confirm do par, confirmar RESTAURAR, preservar candidato/ticket e pré-backup antes do apply. Seleção manual de arquivo no browser deve ser registrada como realmente observada ou limitada (Minor S7 não é PASS manual).

Apply offline apenas com servidor RECOVERY_TARGET comprovadamente parado, mesmo perfil/settings/arquivo do ticket, sem sidecars; comando apply_prepared_restore --ticket usa seu alvo configurado e não tem opção --destination. Ticket contém active_path privado. Antes do apply, preservar cópia+SHA dos candidatos/ticket em RETENTION_ROOT: o sucesso remove candidate.sqlite3/manifest e temporários; cancelamento remove ticket/pré-backup. Não cancelar ou confiar no TemporaryDirectory como retenção.

Provar estado anterior e estado recuperado, status RESTORED, hashes, contagens, histórico, revisões e health pós-restart. Se não houver diferença legítima entre estados, registrar recuperação de estado equivalente, não inventar perda. Retorno do próprio piloto: parar servidor PILOT, preservar cópia falha, restaurar pré-backup em NOVO arquivo, validar checker/SQLite/FK/fingerprints/UI e aprovar apontamento explícito do PILOT para novo arquivo. Nenhum copy-over/original/downgrade automático. Retorno automático interno de apply é tentativa do produto, não evidência suficiente; validar seu resultado. Se original precisar recovery, incidente material Blocker, interromper e solicitar plano separado.

## 9. RPO/RTO — RNF-035, sem SLA novo

Metas normativas existentes: RPO máximo 24 h; RTO máximo 4 h no ambiente de validação. RNF-038 exige recuperação isolada com questões/histórico/pendências consistentes antes do uso real. Exercício S8 mede estes limites, sem inferir backup agendado/garantia de produção.

Planejar timeline privada: t_snapshot (ponto confirmado do backup com source parado; created_at é recibo após snapshot e não prova sozinho o último fato); t_last_durable_fact (última ação/fato legítimo identificado no ledger, se houver); t_incident (declaração controlada de indisponibilidade RECOVERY_TARGET); t_ready (health HTTP 200 + checker 25/0 + SQLite ok/FK 0 + reconciliação/abertura de questões/histórico/pendências concluídas). RTO começa em t_incident, incluindo validação/preparação/aplicação/restart e reconciliação, termina em t_ready; preparação essencial não pode ficar fora do cronômetro silenciosamente. Backup prévio anterior ao incidente é distinguido da preparação posterior.

Relógios: System.Diagnostics.Stopwatch monotônico para elapsed RTO; DateTimeOffset.UtcNow ISO8601 para eventos/correlação e exibição America/Sao_Paulo (-03:00), offset documentado. Não confiar só em subtraction de relógio de parede sujeito a ajustes. RPO: janela entre t_incident e ponto de dados comprovadamente recuperável t_snapshot; registrar também intervalo/fatos legítimos perdidos e última ação durável recuperada, sem usar simplesmente max(occurred_at) de fatos importados ou retrodatados. Nenhum novo dado fabricado para medir RPO. Se não houver perda, provar equivalência e registrar zero perda observada; reportar idade do snapshot separadamente. Tempo/estado não demonstrável → INCONCLUSIVE, sem PASS. Valores futuros em quality/v10-s8-rpo-rto.json, com eventos/relógio/estado/evidência/limites e decisão observada.

## 10. Findings, parada, usabilidade e conclusão futura

Blocker: perda/corrupção/exposição ou mutação original, recuperação impossível, alvo/origem/consentimento indefinido. Major: fluxo central ou restore/recovery inconsistente, isolamento/cross-Workspace, checker crítico, SQLite/FK inválido, backup não restaurável, privacy leak. Cross-Workspace pode ser Blocker conforme extensão; ambos param imediatamente. Minor: limitação localizada sem perda/risco/impedimento central, com evidência/justificativa. Opinião de usabilidade separada de defeito; não elevar confusão estética a Major sem critério funcional.

STOP por corrupção, perda, mudança original/hash inexplicado, cross-Workspace, backup inválido/irrecuperável, restore divergente, finding crítico/inexplicado, integrity failure/FK, origem/consentimento/alvo incerto, privacidade em evidência/log, migration nova ou incompatibilidade não prevista. Parar processos próprios, preservar artefatos/receipts protegidos, registrar S8-Fxx, estado/escopo/severidade/proveniência, solicitar remediação separada. Não repetir cenário nem corrigir silenciosamente. Falha histórica permanece FAIL; reteste futuro é novo resultado. Sem apagar conteúdo bruto para ocultar incidente.

Usabilidade: passos confusos, mensagens, navegação, recuperação, velocidade percebida, ações frequentes e erros humanos prováveis; observações qualitativas pelo responsável, sem participantes/duração/threshold inventados. Separar observação, defeito e limitação de evidência. Piloto termina com representatividade suficiente, fluxos observáveis percorridos, restore/recovery comprovados, metas RNF-035 medidas e cumpridas, original intacto, 25/0/ok/0 e revisão A8 deep aprovada sem Blocker/Major. Não declarar aprovação humana, A8 ou S8_COMPLETED antecipadamente.

Gate futuro: manter evidência S7R1 e S6R1 atribuída às revisões históricas; planejar checks operacionais do piloto e A8 deep. Gate integral aplicável em instalação/scratch sintéticos separados, nunca perfil real: powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1, se exigido pela futura autorização/fechamento ou alteração funcional separadamente autorizada. Capturar exit/timing/receipts e retenção, não inferir GREEN de diff. Nenhum gate executado nesta fase documental; S9 promoção/revisão integrada não antecipada.

## 11. Paths canônicos e artefatos

| Papel | Path canônico | Estado nesta fase |
| --- | --- | --- |
| Contrato S8 | tasks/current.md | criado, AUTHORIZED / PLANNING |
| A4 | tasks/plans/v10-s8-controlled-real-pilot-plan.md | criado, gate humano pendente |
| Roteiro | tasks/plans/v10-s8-pilot-route.md | criado; cenários não executados |
| Proteção/riscos/preflight/temporários | tasks/plans/v10-s8-data-protection.md | criado; decisões privadas pendentes |
| Auditoria/resultado do planejamento | quality/v10-s8-planning-result.md | criado; somente fatos documentais |
| Resultado futuro do piloto | quality/v10-s8-controlled-real-pilot-result.md | PLANNED / NOT CREATED |
| Evidência sanitizada/checkpoints | quality/v10-s8-checkpoints.json | PLANNED / NOT CREATED |
| Registry privado e espelho lógico de retenção | RETENTION_ROOT/private-registry.json; quality/v10-s8-retention-map.json | PLANNED / NOT CREATED |
| RPO/RTO | quality/v10-s8-rpo-rto.json | PLANNED / NOT CREATED |
| Findings/usabilidade | quality/v10-s8-findings.json | PLANNED / NOT CREATED |
| A8 execução deep | quality/v10-s8-a8-deep.json | PLANNED / NOT CREATED |

Nenhum DB/ZIP real/raw/ticket/path pessoal em quality/. Detalhes de privacidade e retenção na matriz de proteção; artefatos essenciais designados antes da execução, cópias+SHA verificadas antes de limpeza pelo produto/harness. Falta de artefato não vira preservação retroativa; PRES-01 histórico é exceção só de 11 targets sintéticos, não se aplica a S8.

## S8_REAL_DATA_AUTHORIZATION_REQUIRED

O A4 está pronto para decisão humana. Não acessar dados até autorização posterior inequívoca para todos os itens:

1. **Fonte — PILOT_SOURCE:** classe escolhida e instalação/revisão produtora; nenhuma seleção automática.
2. **Caminho/identificação:** arquivo exato/caminho absoluto ou ID inequívoco; perfil/Workspace e PRIVATE_ROOT/RETENTION_ROOT/destinos separados; fornecer privadamente, nunca texto pessoal.
3. **Consentimento:** declarar dados próprios ou legitimamente sob controle, limites e responsável; proibir publicação de dados pessoais.
4. **Cópia:** autorizar snapshot/backup da fonte read-only, cópias PILOT/restore/CEI/recovery e confirmar freeze/parada da origem; sem mutação do original.
5. **Leitura:** autorizar hashes, integrity/FK, checker, contagens, fingerprints e observação necessária de questões/histórico/pendências nas cópias; limites de acesso à fonte explicitados.
6. **Uso isolado:** autorizar execução futura em cópia, fluxos naturais/consentidos do roteiro, perfil/settings/porta/browser e import em destino vazio; nenhuma execução no original.
7. **Evidência:** aprovar allowlist agregada de quality/, raw só privado; UUID aliases, logs/screenshots sanitizados, sem DB/ZIP/conteúdo/prefixos pessoais/secrets no Git.
8. **Retenção/descarte:** escolher local protegido/ACL/responsável, evento ou prazo para retained artifacts, tratamento de incidente; nenhuma limpeza designada antes de aceite humano e hashes verificados.
9. **Backup:** aprovar SOURCE/pré-PILOT/pré-operação, manifesto/SHA e restore pré-uso RNF-038, local e condições de remoção; nenhuma mutação sem recuperação validada.
10. **Retorno/recovery:** aprovar ensaio offline somente RECOVERY_TARGET novo isolado, ticket/prebackup preservados, medição RNF-035 e retorno do PILOT a novo arquivo validado; Blocker/Major param para remediação própria. Original não é alvo de recovery; necessidade disso é incidente material.
