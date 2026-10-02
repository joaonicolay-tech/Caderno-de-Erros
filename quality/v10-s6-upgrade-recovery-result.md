# V1.0-S6 — resultado de execução de upgrade e recuperação

Decisão: BLOCKED. S6 não concluída. Execução funcional interrompida no primeiro finding real de rejeição CEI após escrita, conforme seção 13 da autorização humana. Nenhum PASS final foi inferido da evidência histórica ou da preparação da fixture.

## Autoridade, tempo e baseline

- START_TIME: 2026-09-30 19:32:27 -03:00. Horário final e duração total observados são registrados no relatório final da sessão; não são estimados aqui.
- Modelo autorizado da execução: GPT-6.1 Sol High; human-authorized execution-model override for V1.0-S6. Substitui somente a seleção original GPT-6 Sol High desta etapa. O processo não expõe metadados independentes do modelo/esforço selecionados.
- A4 aprovado: tasks/plans/v10-s6-upgrade-recovery-plan.md; contrato ativo em tasks/current.md. Estado foi sincronizado para AUTHORIZED / IN EXECUTION antes dos ensaios e para AUTHORIZED / BLOCKED após o finding.
- Baseline inicial observado: HEAD = origin/main = 5eb6930aba35a0d1083c92816a83c7c4c2451830. Working tree inicial somente PROJECT_STATE.md, tasks/current.md e A4 S6; git diff --check exit 0. Aviso de normalização CRLF em PROJECT_STATE.md, sem erro de whitespace.
- S1–S5 e S2R1 permanecem COMPLETED. S7–S10 NOT AUTHORIZED.

## S6-F01 — Major — destino CEI incompatível recebe escrita antes da falha

Esperado: o caminho oficial import_cei deve recusar destino incompatível antes de INSERT/UPDATE/DELETE. Resultado observado: FAILED_REJECT_BEFORE_WRITE, exit 1.

O probe usa pacote válido emitido pelo candidato V1, sem adulterar application_version, e um destino vazio real no schema histórico V0.4.4. As migrations foram aplicadas pelo MigrationExecutor somente em dois SQLite novos e sintéticos. O destino contém 24 migrations aplicadas; o manifesto/runtime V1 requer 34. Nenhum banco original/ativo do operador foi acessado.

Antes da importação, validate_export aceitou o pacote CEI-EXPORT / format_version 1.0 / produtor V1.0. O destino tinha zero Workspace e passou integrity_check=ok / foreign_key_check vazio. O comando oficial import_cei foi chamado com esse destino configurado e comprovado pelo guard.

Foram executados com sucesso oito INSERTs: User (1), Workspace (1), Discipline (1), Subject (1), Question (1), QuestionRevision (1) e Alternative (2). O wrapper registra apenas execuções retornadas com sucesso, sem conteúdo SQL ou parâmetros privados. O contador SQLite total_changes aumentou exatamente oito. A importação só então lançou OperationalError: table errors_error_category has no column named category_kind.

O rollback deixou contagens, schema e migrations iguais ao baseline e preservou o hash físico. Fingerprint semântico pre/post: 38247fd82d3e3ca50dd22a08892caea6aeb71c6bed401ada40d28b707a6bcd97. SHA-256 físico pre/post: 0c0cdf051848fa081e9e980f930a339937c2dc4f7203691f041851df78ebefff. Esses resultados provam rollback; oito escritas observadas impedem classificar o caso como REJECTED_BEFORE_WRITE.

Causa identificada no código: portability.py:166–167 enumera migrations disponíveis em disco via MigrationLoader(None); validate_export:422 compara o manifesto com essa lista. import_into_empty:560–595 confere identidade/Workspace vazio/backend, abre transaction.atomic e começa os INSERTs sem validar o schema/migrations efetivamente aplicados no destino. A incompatibilidade aparece na execução SQL. Não foi necessária nem criada migration para reproduzir o defeito.

A correção proposta para futura retomada é validar migrations e schema reais do destino por leituras antes de entrar no trecho que escreve, acompanhada de regressão que conte zero DML. Não foi aplicada nesta sessão: a autorização determina PARAR e reportar quando a rejeição ocorre após escrita. Validação pré-escrita dos demais invariantes ainda requer a prova prevista no A4.

## Ensaios, evidência e limites

Comando observado:

    .\.venv\Scripts\python.exe tests/probe_v10_s6_cei_prewrite.py --root <novo diretório absoluto s6-cei-prewrite-*>

O perfil efetivo foi development com caminho explícito para origem/destino dentro da raiz nova do ensaio; nenhuma operação usou o fallback var/development.sqlite3. PYTHONDONTWRITEBYTECODE=1 foi configurado. O guard confirmou backend SQLite, produto V1.0, paths distintos e alvos sem symlink/junction antes das migrations e da importação. Diretórios usados, sob work/ do workspace da sessão:

- s6-cei-prewrite-20260930-run1: preservado NON-CANDIDATE. Falha de preparação do harness por ausência de discipline_id/subject_id em create_active; importação não iniciada. Exit 1; tempo do processo 6,5023904 s. O harness foi corrigido e a repetição usou raiz nova.
- s6-cei-prewrite-20260930-run2: preservado NON-CANDIDATE após S6-F01. Exit 1; tempo do processo 8,1934114 s; intervalo interno de preparação/prova 6,8207885 s. Source, target, ZIP e result.json foram preservados. Nenhum target comprometido foi reaproveitado e nenhum arquivo de evidência foi apagado.

A origem V1 sintética recebeu as 34 migrations existentes, bootstrap de usuário/Workspace/dez categorias, taxonomia, uma Question ativa, revisão, duas alternativas, ciclo e Review. Checker read-only na origem: 25 checks / zero findings; integrity_check=ok e foreign_key_check vazio. Export/validação e tentativa de import não alteraram a origem: hash físico e fingerprint lógico iguais após o ensaio.

O pacote tem policies REV-FIXA-1.0, DOM-HEUR-1.0 e PRI-HEUR-1.0. Seu SHA-256 é e18905025d4ee1b7c45a647175acb4a09d0901d6ead89fe233ae195337976588. O campo raw independent_validation_before_import do JSON designa uma chamada separada a validate_export do produto; não é um leitor independente nem prova CT-118. O probe é uma reprodução negativa mínima, não a fixture representativa completa do upgrade, nem instalação limpa oficial, nem prova de backup.

## Matriz de resultado S6

| Prova | Resultado desta execução |
| --- | --- |
| Fixture representativa V0.4.4 / checkpoint A | NOT_EXECUTED. O destino vazio V0.4.4 do negativo não é a fixture representativa aprovada. |
| V0.4.4 → V0.5 / checkpoint B | NOT_EXECUTED após parada. |
| V0.5 → V1 / checkpoint C | NOT_EXECUTED após parada. Não declarar compatibilidade comprovada ou zero migrations necessárias como resultado de cadeia não executada. |
| Instalação limpa independente V1 | NOT_EXECUTED como prova completa. Preparação saudável da origem não encerra esse critério. |
| Backup, restore isolado e recovery | NOT_EXECUTED; não houve pré-backup/restore nesta reprodução negativa mínima. |
| RPO/RTO | NOT_MEASURED; nenhuma promessa/SLA ou extrapolação. |
| CEI V0.5 → V1 e round-trip | NOT_EXECUTED. O pacote usado para N9 é V1.0, não V0.5. |
| IDs/contagens/histórico/policies/derivados da cadeia | NOT_EXECUTED. Somente imutabilidade da origem e rollback do negativo reconciliados. |
| SQLite/FK | PASS no escopo restrito de origem e destino do probe, antes/depois; não é PASS consolidado S6. |
| Checker | Catálogo atual confirmado 25; origem V1 25/0. Não rodado como checker V1 em destino V0.4.4 incompatível; checker da cadeia ainda pendente. |
| Migration nova | Zero criada; código/migrations funcionais existentes preservados. |

| Negativo CEI | Resultado |
| --- | --- |
| N1 produtor não suportado | NOT_EXECUTED após parada. |
| N2 manifesto com migration incompatível | NOT_EXECUTED após parada; N9 cobre migrations/schema incompatíveis do destino. |
| N3 policy desconhecida | NOT_EXECUTED após parada. |
| N4 schema do pacote incompatível | NOT_EXECUTED após parada. |
| N5 checksum incorreto | NOT_EXECUTED após parada. |
| N6 obrigatório ausente | NOT_EXECUTED após parada. |
| N7 extra proibido | NOT_EXECUTED após parada. |
| N8 UUID/referência inválida | NOT_EXECUTED após parada. |
| N9 destino incompatível | FAIL: oito escritas antes da falha; rollback observado. S6-F01 Major. |

## Verificação e fechamento

- Testes focados: um ensaio negativo concluído com FAIL reproduzível; primeira tentativa foi erro de harness e não resultado de produto. Nenhuma suite pytest foi executada após a parada.
- Lint focado do novo probe: Ruff PASS com --no-cache. Tentativa anterior do lint sem esse parâmetro encontrou acesso negado em .ruff_cache; não foi tratada como defeito do produto.
- Mudanças funcionais da aplicação: nenhuma. Novo harness e evidências somente; nenhuma migration nova, schema novo, formato novo, merge ou conversão.
- Gate integral NOT_EXECUTED porque as provas prévias estão incompletas e a parada é obrigatória. Total de testes do gate, coverage, Django checks do gate, mypy do gate, pip-audit e secrets da S6 não medidos/executados. O GREEN histórico S5 não é gate S6.
- A8 deep final NOT_EXECUTED: depende de provas e gate concluídos. Não há APPROVED S6.
- Findings abertos: Blocker 0 / Major 1 (S6-F01) / Minor 0. S6-F01 impede conclusão.
- Artefatos: tests/probe_v10_s6_cei_prewrite.py; quality/v10-s6-cei-result.json; este relatório; contrato/estado sincronizados. Os resultados upgrade/recovery e contrato completed não foram criados porque as respectivas provas/fechamento não ocorreram.
- tasks/current.md permanece AUTHORIZED / BLOCKED e não foi arquivado. PROJECT_STATE.md registra S6 bloqueada, com S1–S5/S2R1 concluídas e S7–S10 NOT AUTHORIZED.
- Verificação final administrativa observada: git diff --check exit 0, apenas avisos CRLF em PROJECT_STATE.md e tasks/current.md. HEAD e origin/main permanecem no baseline. git status --short contém somente os seis arquivos abaixo; bancos/ZIPs/targets/cache não estão no conjunto de arquivos versionáveis.
- Nenhum git add, commit, push, tag ou release foi executado. Nenhum banco original/ativo ou dado real foi migrado, importado, restaurado ou sobrescrito. Parada funcional preservada após S6-F01.

    M PROJECT_STATE.md
    M tasks/current.md
    ?? quality/v10-s6-cei-result.json
    ?? quality/v10-s6-upgrade-recovery-result.md
    ?? tasks/plans/v10-s6-upgrade-recovery-plan.md
    ?? tests/probe_v10_s6_cei_prewrite.py
