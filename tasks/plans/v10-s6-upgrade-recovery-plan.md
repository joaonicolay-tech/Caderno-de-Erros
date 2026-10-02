# V1.0-S6 — A4 / cadeia de upgrade e recuperação

**Estado:** A4 fechado para a execução funcional futura; nenhuma prova S6 foi executada nesta sessão.
**Classificação:** L / high; impacto potencial em dados HIGH; migration expectation NO.
**Modelo A7 previsto no plano:** GPT-6 Sol High. O runtime desta sessão não expõe metadados verificáveis de modelo/esforço; confirmar antes da execução funcional. **A8:** deep.
**Override humano de execução — 30/09/2026:** GPT-6.1 Sol High, registrado como human-authorized execution-model override for V1.0-S6. Substitui somente o modelo previsto nesta S6; o restante do A4 e os modelos do plano global permanecem vigentes. Execução funcional explicitamente autorizada após aprovação S6_A4_READY_FOR_EXECUTION.
**Dados permitidos na execução:** somente fixtures sintéticas, cópias verificadas e targets isolados. Nenhum banco original ou ativo é alvo.

## 1. Autoridade e baseline

- Autorização humana desta sessão: exclusivamente V1.0-S6. O contrato persistido em tasks/current.md é a autoridade para a próxima execução; S7–S10 continuam NOT AUTHORIZED.
- Baseline inicial observado em 30/09/2026: HEAD = origin/main = 5eb6930aba35a0d1083c92816a83c7c4c2451830; git status --short vazio; git diff --check exit 0.
- Pré-requisitos S1, S2, S2R1, S3, S4 e S5 estão concluídos segundo PROJECT_STATE.md e respectivos contratos/evidências. Qualquer mudança de identidade ou schema do candidato após este baseline exige reavaliar o recorte das provas.
- Fontes: AGENTS.md, A2/A3, PROJECT_STATE.md, plano V1, contratos V1 S1 e CEI, ADR-007, documentação V0.4-S6 e V0.5-S7, A4/resultado V0.5-S8, plano de testes CT-113–120/122, requisitos RNF-033–043/057, código e testes apontados abaixo.
- Nenhum PASS novo da S6 decorre apenas do resultado V0.5-S8.

## 2. Inventário executável e riscos prévios

| Área | Fonte encontrada; uso planejado |
| --- | --- |
| V0.4.4 e V0.5 | Tags anotadas v0.4.4 e v0.5.0 resolvem, respectivamente, para 46e887e0c4fa4dd6f7e128ab63802223d99c9e29 e d24cde1d3c25f7ff0e23306ce7e15e7ea85fd228. tests/test_v05_s2a_upgrade.py constrói estado equivalente V0.4.4 pelas seis leaves e ProjectState do MigrationExecutor; contém Workspace, categorias, Question/revision/alternativas, Attempt, classificação, ciclo, Review e OperationReceipt. Confirmar representatividade e registrar lacunas antes da prova. O pacote CEI V0.5 deve ser emitido pelo runtime fixado da tag V0.5, não por um manifesto V1 apenas editado. |
| Evolução | tests/test_v05_s2a_upgrade.py, test_v05_s2b_upgrade.py, test_v05_s2c_upgrade.py, test_v05_s2d_upgrade.py, test_v05_s3_upgrade.py e test_v05_s5_upgrade.py; A4/resultado V0.5-S8. Usar migrations reais e checkpoints distintos V0.4.4, V0.5 e V1, sem simular avanço por mera troca de rótulo. |
| Backup | modules.data_management.services: create_sqlite_backup, validate_sqlite_backup e restore_sqlite_backup; comandos backup_sqlite, validate_backup e restore_backup. Snapshot via sqlite3 backup; manifesto CEI-SQLITE-BACKUP, tamanho/SHA-256, integrity_check e foreign_key_check. Restore exige migrations atuais e publica somente destino novo. Backup V0.4.4 exige software/schema compatível; não usar restore atual para forçar upgrade do snapshot antigo. |
| Adoção/recovery | modules.data_management.ui_services: prepare_restore e apply_prepared_restore; comando apply_prepared_restore e guia V0.5_S7_Portabilidade_e_Restore.md. O mecanismo real troca banco offline; o ensaio S6 só pode exercitá-lo contra um caminho sintético descartável previamente isolado e guardado. |
| CEI | docs/CEI_EXPORT_1_0.md; modules.data_management.portability: FORMAT CEI-EXPORT, VERSION 1.0, APPLICATION_VERSION do produto, allowlist V0.5/V1.0, validate_export e import_into_empty; comando import_cei; tests/test_v05_s7_portability.py. CEI é ZIP/JSON funcional, distinto de backup físico. |
| Checker | modules.operations.integrity.INVARIANT_CATALOG contém 25 entradas InvariantSpec no candidato atual; run_integrity_check reporta checks_executed = len(INVARIANT_CATALOG). Esperado 25 checks/zero findings. Confirmar novamente no preflight funcional; qualquer catálogo legitimamente alterado deve ser documentado antes da prova, sem hardcode silencioso. |

Riscos a auditar antes da primeira mutação: import_into_empty verifica Workspace vazio e backend antes de transaction.atomic, mas o checker final roda após INSERTs dentro da transação e faz rollback em finding. A prova de rejeição de pacote deve distinguir validação integral pré-escrita de rollback transacional; não chamar rollback de reject-before-write. Também verificar que o schema/migrations do destino real são inspecionados antes de import_into_empty, e não apenas comparados ao runtime pelo manifesto. Se a implementação não cumprir a exigência de validação pré-escrita, registrar finding e parar; correção funcional fica para execução posterior autorizada, nunca para este A4.

## 3. Pré-condições comuns à execução futura

1. Verificar tasks/current.md AUTHORIZED para S6, modelo/esforço A7 exigido, HEAD/árvore sem alterações alheias, identidade do candidato, graph de migrations e ausência de migration nova. Se alguma precondição falhar, parar antes de dados.
2. Criar diretório exclusivo para cada ensaio e resolver caminhos absolutos de origem, backup, staging e destino. Guard: todos os alvos de escrita são novos, sob raiz de teste explicitamente escolhida; não são symlink/junction; são diferentes do banco original/ativo e de qualquer path em configuração de desenvolvimento/produção. Conferir esta relação antes de cada comando.
3. Dados determinísticos, relógio/fuso fixos e IDs capturados antes da evolução. Gerar manifest de fixture/protocolo com origem, commit/tag, leaves por checkpoint, seed, contagens, fingerprints e versões de policy. Nunca usar dados pessoais.
4. Preservar backup pré-operação e seu manifesto, imutáveis, até fechamento de cada prova. Aferir tamanho, hash, SQLite e FK antes de considerar o par recuperável.
5. Capturar saída bruta, exit code, hashes e contagens por fase; logs sanitizados sem conteúdo de estudo, segredo ou paths privados. Inconclusivo e tentativa interrompida não viram PASS.

## 4. Cadeia CT-122: V0.4.4 → V0.5 → candidato V1

1. Construir fixture representativa no estado real de migrations V0.4.4 pelo MigrationExecutor; conferir tag resolvida, tabela de migrations, schema, IDs, contagens e fatos históricos. Incluir ao menos vínculo de taxonomia/origem, revisão/gabarito, Attempt e classificação, ciclo/Review/due date, política aplicável e receipt legado. Registrar ausência intencional de entidades ainda inexistentes.
2. Registrar baseline lógico por tabela: conjunto ordenado de UUIDs, contagens, campos semânticos, relações, timestamps/datas, estado de ciclos e policy_code. Obter fingerprint canônico por serialização determinística de fatos; comparar também SHA-256 do SQLite quando a exigência for identidade física do snapshot.
3. Gerar e validar backup pré-upgrade. Verificar restore físico em cópia V0.4.4 isolada com software/schema compatível, integrity_check, foreign_key_check e fatos baseline; manter par pré-upgrade.
4. Migrar somente cópia de trabalho até leaves V0.5, em checkpoint explícito. Registrar migrations aplicadas e comprovar que as aditivas previstas correspondem ao grafo. Reconciliar IDs e fatos legados sem reescrever história; defaults V0.5 e derivados legítimos são classificados separadamente.
5. Capturar novo backup/checkpoint V0.5 e suas impressões. Evoluir até leaves do candidato V1 pelas migrations reais. Se não houver migrations adicionais V1, registrar explicitamente a igualdade do graph/schema relevante e que nenhuma mudança de schema foi necessária para compatibilidade V0.5→V1.
6. Rodar PRAGMA integrity_check = ok, foreign_key_check vazio, checker com catálogo atual/zero findings. Comparar contagens, UUIDs e fatos históricos pre/post, inclusive QuestionRevision/Attempt/Review, policy_code, categorias, SavedFilter, AuditEvent, MasteryStateEvent e OperationReceipt onde aplicáveis. Receipt pertence ao backup físico, não ao CEI.
7. Recalcular analytics, Domain, Priority e fila sob clock fixo para comparar projeções derivadas, distinguindo mudança de produto esperada de perda de fato. Nenhuma diferença sem explicação documentada é aceita. Capturar fingerprints após checks e verificar que checker/leituras não alteraram dados.

## 5. Provas independentes

| Prova | Procedimento e aceite |
| --- | --- |
| Instalação limpa V1 | Em banco novo isolado, aplicar migrations atuais, validar schema/leaves/defaults de usuário/Workspace/categorias pelo fluxo canônico, integrity_check, FK, checker 25/0 se catálogo confirmar, abrir aplicação e executar smoke mínimo de leitura/criação sintética. Registrar que não depende da fixture de upgrade. |
| Backup CT-113/114 | Em origem sintética V1, produzir snapshot consistente e manifesto, conferir tamanho/hash/checks físicos; alterar byte somente em cópia do backup para provar rejeição antes de qualquer destino. Provar que origem e par válido permanecem intactos. |
| Restore CT-115/117 | Restaurar par válido para caminho novo isolado; validar staging, migrations/schema, fundação, checker, abertura e fingerprints de IDs/contagens/fatos e hash físico. Em destino ocupado ou par inválido, provar recusa sem alteração do destino. Nunca restaurar sobre original/ativo. |
| Recovery CT-116 | Simular falha em cópia ativa sintética com pré-backup validado. Encerrar todas as conexões antes de qualquer troca offline; exercitar retorno apenas dentro da raiz isolada, abrir aplicação, validar SQLite/FK/checker e fingerprints do ponto escolhido. Registrar instantes de backup/falha/retorno e tempo observado, confrontando RPO 24 h e RTO 4 h apenas para o ambiente exercitado, sem extrapolar para instalação real. |
| CEI CT-118/119 | Produzir pacote de export em runtime V0.5 compatível, com application_version V0.5, CEI-EXPORT/format_version 1.0 e migrations/policies aceitas; verificar o pacote independentemente; importar no V1 em banco vazio compatível e reexportar. Comparar UUIDs, relações, contagens, fatos e versões de policy por projeção semântica; generated_at e bytes ZIP podem diferir. Repetir export V1→import V1 se aplicável. |

## 6. CEI: validação pré-escrita e matriz negativa CT-120

Sequência exigida: validar contêiner/membros exatos e seguros; JSON UTF-8 e chaves; manifesto, format, format_version, application_version na allowlist; schema_migrations e policies reconhecidas; nomes/quantidade/tamanho/SHA-256 de arquivos; schema e tipos fechados; UUIDs únicos/canônicos, referências e Workspace; contagens; invariantes que possam ser verificados do pacote; backend, schema/migrations efetivamente aplicadas e destino vazio/compatível. Só depois é permitida transação de importação no target isolado. Pós-import, checker e reconciliação devem passar; falha pós-escrita é rollback comprovado, categoria distinta de rejeição pré-escrita.

Para cada negativo, registrar fingerprint completo do destino antes/depois (incluindo tabela de migrations, linhas/timestamps, SQLite e sidecars quando estáveis), contagem de INSERT/UPDATE/DELETE por instrumentação ou trace, ausência de AuditEvent/receipt, exit/error e pacote fonte imutável. O aceite reject-before-write requer zero escrita observada, não só destino final equivalente.

| Caso | Mutação controlada do pacote/ambiente; resultado exigido |
| --- | --- |
| N1 produtor não suportado | application_version desconhecido; rejeitar antes de escrita. |
| N2 migration incompatível | lista de schema_migrations alterada ou destino com graph divergente; rejeitar antes de escrita. |
| N3 policy desconhecida | review/domain/priority fora da allowlist; rejeitar antes de escrita. |
| N4 schema incompatível | campo ausente/extra/tipo incompatível ou destino schema divergente; rejeitar antes de escrita. |
| N5 checksum incorreto | byte alterado sem atualizar sha256; rejeitar antes de escrita. |
| N6 obrigatório ausente | remover um membro requerido do ZIP ou do manifesto; rejeitar antes de escrita. |
| N7 extra proibido | acrescentar membro ou path ZIP; rejeitar antes de escrita. |
| N8 UUID/referência inválida | UUID malformado/duplicado, vínculo ausente ou cross-Workspace com checksum atualizado; rejeitar antes de escrita. |
| N9 destino incompatível | Workspace existente, backend ou migrations incompatíveis; rejeitar antes de escrita. |

Não converter, coagir, importar parcialmente, fazer merge, remapear IDs, adaptar schema ou “reparar” o pacote. Pacote incompatível permanece evidência negativa; novo pacote válido exige nova origem/prova.

## 7. Fingerprints, decisões e recuperação de falha

- Fingerprint lógico: export determinístico de tuplas por tabela/UUID, relações, valores e timestamps, com SHA-256 e contagens separados. Classificar como fatos imutáveis, estado operacional, policies, dados derivados e dados técnicos; não comparar bytes de CEI ZIP nem confundir receipt excluído do CEI com perda de fato.
- Fingerprint físico: SHA-256 do backup e manifesto antes/depois, PRAGMAs e migrações. SQLite de banco migrado pode mudar bytes legitimamente; nesse caso o critério é reconciliação lógica, não hash físico idêntico entre versões.
- Cada fase tem PASS/FAIL/INCONCLUSIVE próprio. Qualquer diferença exige explicação baseada em contrato/migration e evidência; não ajustar expected a posteriori para passar.
- Em falha: preservar pré-backup, pacote, logs e fingerprints; marcar target comprometido como não candidato; abandonar apenas o target isolado verificado; reconstruir target novo da origem preservada; repetir só prova metodologicamente válida. Não corrigir manualmente original, não reutilizar destino ocupado e não apagar única cópia recuperável.
- Parada imediata: perda semântica, ID alterado, contagem não reconciliada, backup inválido, restore não reconciliável, checker finding, integrity_check diferente de ok, FK finding, CEI incompatível sem decisão, escrita antes de validação completa, necessidade de migration, target original/ativo, modelo A7 não confirmado, ou alteração não autorizada. Migration real necessária → HUMAN_DECISION_REQUIRED com motivo, dados afetados, reversibilidade, compatibilidade, riscos e alternativas; não criar automaticamente.

## 8. Artefatos, testes, gate e revisão

Nomes canônicos planejados, criados somente na execução funcional conforme necessidade: este A4 tasks/plans/v10-s6-upgrade-recovery-plan.md; fixture/protocolo tests/test_v10_s6_upgrade_recovery.py (ou harness próprio se necessário); bruto quality/v10-s6-upgrade-result.json; backup/restore/recovery quality/v10-s6-recovery-result.json; CEI quality/v10-s6-cei-result.json; consolidado quality/v10-s6-upgrade-recovery-result.md; contrato final arquivado tasks/completed/v10-s6-upgrade-recovery.md. Evitar artefato duplicado quando um arquivo rastreia a mesma prova com clareza.

Testes focados planejados: tests/test_v10_s6_upgrade_recovery.py; tests/test_v05_s2a_upgrade.py e demais upgrades S2B/S2C/S2D/S3/S5 relevantes; tests/test_backup_restore.py, tests/test_backup_recovery.py, tests/test_v05_s7_portability.py e tests/test_integrity_checker.py. Mapear CT-113–120/122 a casos novos ou repetidos no candidato V1; teste histórico isolado não basta.

Após execução funcional, rodar gate integral canônico powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1 e registrar exit code real. O script cobre lock/dependências, runtime, rastreabilidade, Django checks em três perfis, migrations inesperadas, banco vazio isolado, Ruff format/lint, mypy, pytest/coverage, cobertura de domínio, detect-secrets e pip-audit. GREEN só com exit 0 observado. Não rodar gate nesta sessão documental.

A8 deep final deve revisar cadeia V0.4.4→V0.5→V1, instalação limpa, backup/restore/recovery, CEI e rejeição antes de escrita, IDs/contagens/fingerprints, SQLite/FK/checker, policies, histórico/derivados, migrations, segurança dos dados, escopo e proveniência de cada PASS. Findings Blocker/Major e P0/P1 aplicáveis impedem fechamento. Decisão funcional futura só poderá ser upgrade/recuperação V1 comprovados após todas as provas independentes, gate e A8 aprovados.
