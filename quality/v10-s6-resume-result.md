# V1.0-S6 — Retomada após S2R2

## Decisão final

**S6-F02 Major OPEN:** o pacote incoerente foi aceito e commitado, com 24 INSERTs e total_changes +24; checker pós-commit encontrou quatro violações. Parada obrigatória aplicada. Nenhuma correção de produto foi feita.

BLOCKED. Evidências funcionais desta retomada são novas; S6-F01 FAIL, N9 original e S2R2 continuam intactos. Nenhum PASS foi atribuído a browser manual: a abertura funcional abaixo usa Django Client e respostas HTTP reais.

## Relatório final — 56 campos

| Nº / campo | Resultado observado |
| --- | --- |
| 1 START_TIME | 2026-09-30 21:31:07 -03:00 |
| 2 END_TIME | 2026-09-30 22:16:47 -03:00 |
| 3 Duração | 0:45:40 |
| 4 Modelo | GPT-6.1 Sol High, override humano específico da S6 registrado no contrato |
| 5 Baseline | HEAD = origin/main = 5eb6930aba35a0d1083c92816a83c7c4c2451830 |
| 6 S6-F01 | RESOLVED por S2R2; FAIL original preservado |
| 7 S2R2 incorporada | Import/preflight e seus testes byte a byte preservados; 32 focados, gate GREEN/532 PASS/86.5747% e A8 deep anteriores são evidência S2R2, não gate S6 |
| 8 N1 | PASS / REJECTED_BEFORE_WRITE — produtor não suportado |
| 9 N2 | PASS / REJECTED_BEFORE_WRITE — lista de migrations incompatível |
| 10 N3 | PASS / REJECTED_BEFORE_WRITE — policy desconhecida |
| 11 N4 | PASS / REJECTED_BEFORE_WRITE — campo obrigatório ausente; checksum recalculado para isolar schema |
| 12 N5 | PASS / REJECTED_BEFORE_WRITE — checksum inválido com mesmo tamanho; primeira variante também recusou tamanho inválido |
| 13 N6 | PASS / REJECTED_BEFORE_WRITE — arquivo obrigatório ausente |
| 14 N7 | PASS / REJECTED_BEFORE_WRITE — arquivo extra proibido |
| 15 N8 | PASS / REJECTED_BEFORE_WRITE — UUID inválido; caso complementar de referência ausente com checksum recalculado |
| 16 N9 histórico | FAIL: oito INSERTs bem-sucedidos, total_changes +8 antes de OperationalError; rollback não prova rejeição pré-escrita |
| 17 N9 final | PASS / REJECTED_BEFORE_WRITE por S2R2: attempts 0/0/0, total_changes 0, contagens e fingerprints iguais; incorporado sem repetição formal |
| 18 Escrita nos negativos | Novo caso A8-INV-ATT-001: **24 INSERTs tentados/concluídos, total_changes +24, aceito/commitado**. N1–N8 e complementares: INSERT/UPDATE/DELETE attempts = 0/0/0; successful = 0/0/0; total_changes delta = 0; contagens e fingerprints semântico/schema/físico antes/depois iguais |
| 19 V0.4.4 baseline | PASS: migrations reais (24), fixture histórica aprovada com origem acrescentada no registry histórico; 17 checks do runtime V0.4.4 / 0 findings; pré-backup e restore históricos válidos |
| 20 V0.4.4→V0.5 | PASS: dez migrations aditivas previstas, 34 aplicadas; todos os campos legados/UUIDs/contagens/fatos reconciliados |
| 21 V0.5→V1 | PASS: plano de migrations vazio; nenhuma migration V1 nova necessária; fontes de migrations dos módulos iguais; tabelas, fingerprints e derivados iguais |
| 22 Clean install | CLEAN_INSTALL_PASS em arquivo novo: 34 migrations, dez categorias STANDARD/ACTIVE/lock_version 1, operação mínima e HTTP 200 em /, /questions/, /reviews/ |
| 23 Backup | PASS independente em cópia sintética conhecida com fatos históricos; SHA/tamanho/manifesto/SQLite/FK válidos; origem e par válido intactos; corrupção de cópia rejeitada |
| 24 Restore | ISOLATED_RESTORE_PASS em destino novo; fatos completos e derivados iguais; destino ocupado recusado sem alteração; backup corrompido não criou destino |
| 25 Recovery | RECOVERY_PASS: aplicação offline real em cópia sintética; ramo de retorno automático exercitado por falha injetada após adoção, estado anterior reconciliado; novo ticket restabeleceu ponto escolhido, HTTP 200 e pré-backups preservados |
| 26 RPO/RTO | RPO observado 0.378565 s; RTO observado 1.707174 s; limites existentes de 24 h/4 h atendidos somente neste exercício isolado; nenhuma inferência de SLA real |
| 27 CEI V0.5→V1 | PASS: pacote realmente produzido pelo runtime v0.5.0, identificado V0.5; leitor independente stdlib, validator oficial e preflight antes de escrita; import compatível no V1 |
| 28 Round-trip | PASS: V0.5→V1→reexport e V1→segundo V1; todos os 21 record sets funcionais, UUIDs, relações, contagens e policies iguais |
| 29 IDs | PASS: preservados por projeção de todas as colunas legadas na cadeia e em todos os conjuntos funcionais CEI; backup/recovery preservam tabelas completas |
| 30 Contagens | PASS: por tabela em cada fase e por conjunto CEI; 1 Workspace, 10 categorias, 1 disciplina, 1 assunto, 1 fonte/origem/Question/revisão/Attempt/classificação/ciclo/review/receipt e 2 alternativas na fixture histórica |
| 31 Fingerprints | PASS: fingerprints lógico/schema/físico observados; V0.4.4→V0.5 reconcilia projeção legada devido a schema aditivo; V0.5→V1 idêntico; CEI usa equivalência funcional e backup/recovery equivalência de fatos mais hash exato do artefato adotado |
| 32 Histórico | PASS: timestamps, gabarito/revisão usada, tentativa VALID, classificação ATTENTION, origem, ciclo INITIAL_ERROR, review D1 PENDING/due 2026-09-21 e receipt legado preservados na cadeia/backup/recovery |
| 33 Policies | REV-FIXA-1.0 preservada; DOM-HEUR-1.0 e PRI-HEUR-1.0 observadas na V0.5/V1; manifesto compatível; versão/política desconhecida recusada |
| 34 Derivados | Analytics/fila iguais V0.4.4→V0.5; Domain/Priority introduzidos na V0.5, não inventados na V0.4.4; todos iguais V0.5→V1, CEI, restore e recovery sob clock fixo 2026-09-20 15:00 UTC |
| 35 SQLite integrity | PASS: integrity_check = ok em cada target validado; cópia corrompida recusada |
| 36 FK | PASS: foreign_key_check sem linhas em cada target validado |
| 37 Checker | Novo target S6-F02: **25 checks / 4 findings** ATT-001, ERR-001, REV-001, REV-002. Nas fontes/provas válidas: 25 checks / 0 findings; V0.4.4 usa seu catálogo histórico real de 17; leituras/checker sem mutação do snapshot |
| 38 Testes focados | 90 PASS, pytest 162.74 s, comando completo abaixo; wall time observado 164.5584492 s; 11 avisos sobre metadados JUnit xunit2, sem falha de produto |
| 39 Findings | S6-F02 Major/P1 OPEN: pacote semanticamente incoerente aceito e commitado; causas e reprodução na A8 abaixo. S6-F01 continua RESOLVED; dois incidentes de harness preservados |
| 40 Migrations | Novas migrations de produto = 0; nenhuma mudança de schema/CEI/producer policy ou import/preflight nesta retomada |
| 41 Gate S6 | GREEN / exit 0 observado antes da A8, 491.4 s; finding material posterior impede aprovação/fechamento S6; nenhuma rodada nova após finding |
| 42 Total de testes | 532 PASS em 407.57 s |
| 43 Coverage | 86.5746664% (bruto 86.5746664229574) |
| 44 pip-audit | PASS / 0 vulnerabilidades, JSON oficial preservado |
| 45 A8 deep | CHANGES_REQUESTED / NOT APPROVED, deep da própria S6 após gate; S6-F02 reproduzido; revisão pelo próprio Codex |
| 46 Blocker/Major/Minor | 0 / 1 / 0 abertos |
| 47 Artefatos | Adicionais: quality/v10-s6-resume-a8-invariant-result.json e tests/probe_v10_s6_a8_invariant.py. Novo harness tests/probe_v10_s6_resume.py; quality/v10-s6-resume-{cei,upgrade,recovery}-result.json e quality/v10-s6-resume-result.md; logs/tabelas/pacotes/manifests/índice de 72 artefatos preservados |
| 48 Targets | Novo work/s6-resume-20260930-a8-invariant preservado NON-CANDIDATE após 24 INSERTs commitados, nunca reutilizado. Novos roots work/s6-resume-20260930-run1 e work/s6-resume-20260930-recovery2 preservados; primeiro recovery NON-CANDIDATE por comparação física inadequada; todos os targets S6/S2R2 anteriores preservados; nenhum banco real tocado |
| 49 .secrets.baseline | Somente ela permanece staged pela exceção humana anterior; 59 registros revisados anteriores preservados; zero entradas novas e nenhum staging nesta retomada |
| 50 git diff --check | PASS / exit 0 observado antes e após registro da parada |
| 51 git status --short | Somente alterações autorizadas S6/S2R2 e métricas S6; lista completa abaixo; apenas .secrets.baseline staged |
| 52 PROJECT_STATE | S6 AUTHORIZED / BLOCKED; S6-F02 Major OPEN; S6-F01 RESOLVED; S1–S5/S2R1/S2R2 COMPLETED; S7–S10 não autorizadas |
| 53 tasks/current | AUTHORIZED / BLOCKED / A8 NEW FINDING S6-F02; não arquivado e não retornado a NO_TASK_AUTHORIZED |
| 54 S7–S10 | NOT AUTHORIZED; nenhuma etapa futura iniciada |
| 55 Git/publicação | Nenhum commit, push, tag ou release; HEAD/origin/main intactos |
| 56 Decisão | BLOCKED |

## Provas e rastreabilidade

| Caso | Prova nova no candidato V1 |
| --- | --- |
| CT-113/114 | Backup físico independente, manifesto/checksum, corrupção rejeitada e origem intacta |
| CT-115/117 | Restore isolado, staging/compatibilidade/checker; destino ocupado e backup corrompido recusados |
| CT-116 | Tickets reais, pré-backup, adoção offline, falha pós-adoção injetada/retorno automático e recuperação bem-sucedida |
| CT-118/119 | Export real V0.5, leitor independente, import V1 e 21 conjuntos iguais em duas idas e voltas |
| CT-120 | N1–N8 novos + N9 final S2R2; tentativas contadas antes de execute, não apenas após rollback |
| CT-122 | MigrationExecutor real V0.4.4→V0.5→V1 e instalação limpa V1; reconciliação completa e regressões selecionadas |

### Semântica das diferenças previstas

- V0.4.4 contém 24 migrations. As dez aditivas V0.5 acrescentam campos/defaults e tabelas; todos os campos legados permanecem iguais. Os novos eventos/auditorias/filtros não foram fabricados para a fixture histórica.
- CEI-EXPORT-1.0 exclui OperationReceipt e credenciais do usuário local. O receipt legado continua na cadeia/backup/recovery; sua ausência nos destinos CEI e a fundação de usuário recriada são exclusões contratuais. Todos os fatos funcionais dos 21 conjuntos permanecem iguais.
- O snapshot físico SQLite pode alterar somente contadores técnicos do cabeçalho nos offsets 24–27, 40–43 e 92–95. Tabelas/schema/fatos iguais e identidade física com o backup escolhido provam a adoção/retorno; não se exige identidade entre arquivo fonte e snapshot produzido pela API sqlite3.backup.
- RPO/RTO usam instantes UTC efetivamente capturados no JSON recovery. A única mutação após backup foi o nome sintético do Workspace; a restauração ao ponto anterior a elimina deliberadamente. Todos os fatos desse ponto foram reconciliados.

### Incidentes de harness preservados

1. O leitor stdlib inicialmente tentou ler README.txt como JSON antes de criar o destino de import. A seleção foi corrigida para membros JSON. O pacote válido e a origem permaneceram intactos; não foi finding de produto.
2. O primeiro recovery exigiu identidade física original/pré-backup. O retorno real deixou os fatos/schema/contagens iguais e o arquivo idêntico ao pré-backup. A investigação somente leitura identificou a normalização técnica do cabeçalho SQLite. Primeira tentativa e log permanecem preservados, NON-CANDIDATE. A comparação corrigida foi executada em nova raiz com fixture histórica completa e passou; nenhuma alteração de produto foi feita.

## Reprodução e comandos

Os códigos históricos foram extraídos de git archive v0.4.4 e v0.5.0 para diretórios exclusivos, sem checkout ou Git write. Cada processo usa o .venv Python 3.13.15/Django 5.2.17/SQLite 3.53.1 e sys.path apontando para o runtime escolhido; CEI_DEVELOPMENT_DB é guardado dentro da raiz sintética.

```powershell
# Raiz nova para outra execução; nunca reutilizar targets preservados.
python tests/probe_v10_s6_resume.py --root <raiz-nova-s6-resume> --repo C:/src/Projeto --runtime C:/src/Projeto --phase negatives
python tests/probe_v10_s6_resume.py --root <mesma-raiz> --repo C:/src/Projeto --runtime C:/src/Projeto --phase negatives-extra
python tests/probe_v10_s6_resume.py --root <mesma-raiz> --repo C:/src/Projeto --runtime <runtime-v05> --phase seed
python tests/probe_v10_s6_resume.py --root <mesma-raiz> --repo C:/src/Projeto --runtime <runtime-v044> --phase v044
python tests/probe_v10_s6_resume.py --root <mesma-raiz> --repo C:/src/Projeto --runtime <runtime-v05> --phase v05
python tests/probe_v10_s6_resume.py --root <mesma-raiz> --repo C:/src/Projeto --runtime C:/src/Projeto --phase v1
python tests/probe_v10_s6_resume.py --root <mesma-raiz> --repo C:/src/Projeto --runtime C:/src/Projeto --phase positive
python tests/probe_v10_s6_resume.py --root <mesma-raiz> --repo C:/src/Projeto --runtime C:/src/Projeto --phase clean
python tests/probe_v10_s6_resume.py --root <outra-raiz-nova-s6-resume> --repo C:/src/Projeto --runtime C:/src/Projeto --phase recovery --fixture-db <mesma-raiz>/chain.sqlite3
python -m pytest tests/test_v05_s2a_upgrade.py tests/test_v05_s2b_upgrade.py tests/test_v05_s2c_upgrade.py tests/test_v05_s2d_upgrade.py tests/test_v05_s3_upgrade.py tests/test_v05_s5_upgrade.py tests/test_backup_restore.py tests/test_backup_recovery.py tests/test_v05_s7_portability.py tests/test_integrity_checker.py tests/test_cei_destination_compatibility.py --basetemp=<novo-temp> --junitxml=<novo-xml>
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1
```

O probe usa assertions para os critérios; recusa Python -O. A reconciliação independente por projeção de todos os campos legados, defaults/migrations e comparação de V0.5/V1 está materializada no JSON upgrade. Digests de evidência novos usam a notação explícita SHA256:hex; bytes/manifestos CEI não foram alterados.

## A8 deep final S6

Decision: CHANGES_REQUESTED / NOT APPROVED — S6-F02 Major OPEN.

Revisão deep da própria S6 pelo Codex, executada após o gate integral S6 exit 0. Nenhum revisor independente é alegado.

| Área revisada | Resultado / evidência |
| --- | --- |
| A4/autorização/isolamento | PASS: contrato específico, targets novos e sintéticos, runtimes históricos reais, nenhum banco real; raízes anteriores preservadas |
| S6-F01 / S2R2 / N9 | PASS para o escopo resolvido: FAIL original preservado, correção e reteste final intactos; N9 não repetido formalmente; importer/testes S2R2 com hashes idênticos aos do início |
| N1–N8 | PASS dos casos planejados e complementares: contadores antes de execute, zero attempts/total_changes, contagens/fingerprints iguais; esses casos não cobrem toda a coerência semântica das invariantes |
| Cadeia/clean install | PASS: 24→34 migrations, dez aditivas identificadas, nenhuma migration V1; todos os campos legados preservados; instalação independente com defaults e HTTP 200 |
| Backup/restore/recovery | PASS dos cenários válidos e negativos previstos; retorno/adopção offline reais em cópia; preservação física do par escolhido e equivalência de fatos; RPO/RTO limitados ao exercício |
| CEI positivo/round-trip | PASS para pacotes provenientes de fatos coerentes: runtime V0.5 real, formato 1.0, validação independente, 21 conjuntos iguais; receipt/credencial excluídos conforme contrato |
| Histórico/IDs/contagens/policies/derivados | PASS nas fontes válidas, cadeia, restore, recovery e CEI; projeções completas/fixed clock, sem reinterpretação de fatos legados |
| SQLite/FK/checker | 25/0 nas fontes/provas válidas, SQLite/FK ok. Novo target S6-F02: SQLite/FK continuam ok, mas checker pós-commit real executa 25 checks e encontra 4 violações semânticas |
| Gate/migrations/escopo | Gate técnico S6 GREEN: 532 PASS, 86.5746664229574%, pip-audit 0, 491.4 s. Não elimina o finding reproduzido depois na A8. Nenhuma alteração de produto/migration/preflight nesta retomada; S7–S10 não autorizadas |
| Invariantes CEI antes da escrita | FAIL material S6-F02: pacote de checksum correto, UUIDs/referências válidos e producer/policies/migrations corretos, com Attempt.is_correct=True e alternativa escolhida diferente do gabarito da revisão, foi aceito e commitado |

## S6-F02 — incoerência semântica CEI aceita e commitada

- Classificação: **Major / P1**, OPEN. Blocker/Major/Minor abertos = **0/1/0**. Os quatro findings do checker têm suas próprias severidades no catálogo; não são quatro bugs independentes.
- Reprodução: pacote V0.5 sintético válido preservado, cópia nova com somente `Attempt.is_correct` false→true, checksum/tamanho do membro recalculados. `validate_export` aceita. `import_cei` retorna sucesso (nenhuma exception).
- Escrita observada: **24 INSERT attempts e 24 INSERTs concluídos; UPDATE/DELETE 0/0; SQLite total_changes delta +24**. Contagens e fingerprints semântico/físico passam do target vazio para fatos persistidos. **Não ocorreu rejeição nem rollback**.
- Checker independente após commit: **25 checks / 4 findings**, ATT-001, ERR-001, REV-001, REV-002. Sua execução somente leitura não altera o target.
- Causa confirmada no código: `validate_export`/`_validate_relations` verificam tipos, enums, UUIDs e existência de referências, mas não esta coerência relacional do resultado. `import_into_empty` invoca `run_integrity_check` dentro de `transaction.atomic`; o checker abre **outra conexão sqlite3 mode=ro** para o arquivo e enxerga o estado commitado anterior, vazio. Logo, o checker chamado ali não protege as linhas ainda não commitadas.
- Impacto: aceitação silenciosa de fatos contraditórios pode corromper contagens de acerto, classificação e ciclos/derivados. Viola a exigência humana/A4 de validar invariantes antes de qualquer escrita.
- A correção S2R2 continua correta no seu escopo de destino/migrations/schema. S6-F01 permanece RESOLVED; S6-F02 é finding novo e não foi corrigido silenciosamente.
- Evidências: `quality/v10-s6-resume-a8-invariant-result.json`, `tests/probe_v10_s6_a8_invariant.py`, log e pacote/target sob `work/s6-resume-20260930-a8-invariant`. Target preservado **NON-CANDIDATE**, nunca reutilizado. Nenhum original foi tocado.
- Parada aplicada imediatamente após a reprodução; diagnóstico posterior apenas por leituras e registro de evidências/estado. Sem novas provas funcionais, nova rodada do gate ou mudanças de produto depois do finding.
- Próximo requisito: remediação material sob autorização própria, com rejeição semântica pré-escrita comprovada e revisão da visibilidade transacional do checker. A8 não aprovada; S6 não pode ser fechada/arquivada. Nenhuma migration ou mudança estrutural CEI foi demonstrada necessária nesta investigação.

## Reprodução do finding em outra raiz nova

```powershell
& .\.venv\Scripts\python.exe tests/probe_v10_s6_a8_invariant.py --repo C:/src/Projeto --root <novo-s6-resume-a8> --source <raiz-s6-preservada>/real-v05-export.zip
```

O probe opt-in recusa raiz existente, symlink/junction ou fonte fora de raiz sintética irmã. O processo observado original usou os mesmos dados/algoritmo com caminhos fixados exclusivamente no workspace de execução; os parâmetros foram acrescentados depois apenas para persistir reprodução segura, sem repetir a prova ou alterar o produto.


## Estado Git final observado

```text
M  .secrets.baseline
 M PROJECT_STATE.md
 M quality/operational-execution-metrics.jsonl
 M src/modules/data_management/portability.py
 M tasks/current.md
?? quality/v10-s2r2-cei-destination-result.md
?? quality/v10-s2r2-n9-retest.json
?? quality/v10-s6-cei-result.json
?? quality/v10-s6-resume-a8-invariant-result.json
?? quality/v10-s6-resume-cei-result.json
?? quality/v10-s6-resume-recovery-result.json
?? quality/v10-s6-resume-result.md
?? quality/v10-s6-resume-upgrade-result.json
?? quality/v10-s6-upgrade-recovery-result.md
?? tasks/completed/v10-s2r2-cei-destination-compatibility.md
?? tasks/paused/v10-s6-upgrade-recovery.md
?? tasks/plans/v10-s6-upgrade-recovery-plan.md
?? tests/probe_v10_s6_a8_invariant.py
?? tests/probe_v10_s6_cei_prewrite.py
?? tests/probe_v10_s6_resume.py
?? tests/test_cei_destination_compatibility.py
```

As evidências antigas/A4/probe/importer e testes S2R2 foram verificados byte a byte contra o mapa capturado no início da retomada. Os três JSONs novos são snapshots do checkpoint funcional anterior ao gate; o resultado final do gate/A8 está neste relatório e no contrato arquivado.

## Verificações dos registros finais

A primeira varredura documental identificou três UUIDs sintéticos do contexto do checker em representação hexadecimal sem hífens. A entrega usa notação canônica UUID com hífens, preservando identidade; saída bruta permanece intacta na raiz do finding. Não foi alterada a baseline, nenhum detector/filtro ou valor de fato. Ruff/mypy do novo probe PASS; não houve nova execução funcional nem gate integral após o finding.

Verificação final dos registros: detect-secrets-hook exit 0; git diff --check exit 0; somente .secrets.baseline staged, sem diferenças dela fora do index.
