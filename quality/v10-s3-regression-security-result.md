# V1.0-S3 — Regressão, banco, segurança e privacidade: resultado

## Baseline e autorização

- Data da execução: 28 de setembro de 2026 (America/Sao_Paulo).
- Tarefa: `V1.0-S3`, `AUTHORIZED` em `tasks/current.md`; Size `M`, Risk `high`,
  migration `NO` prevista.
- Baseline: branch `main`; `HEAD = origin/main =
  b0db74620c7884dc164a609208ed23253d70cafd`.
- No início, somente `tasks/current.md` estava alterado, com a autorização
  persistida. A divergência antiga em `PROJECT_STATE.md` sobre S3 não autorizada
  era conhecida e explicitamente dispensada como blocker pelo pedido de
  execução; foi reconciliada aqui após a evidência S3.
- Candidato preservado: produto `V1.0`, pacote `1.0.0`, CEI format `1.0`,
  produtores `V0.5` e `V1.0`. Sem tag/release V1.
- S4/S5/S6 não foram iniciadas. Nenhuma publicação, commit, push ou tag ocorreu.

## Fontes consultadas

- `AGENTS.md`, contrato S3 em `tasks/current.md`, `PROJECT_STATE.md`,
  `docs/A2_Contrato_de_Tarefa_Atual.md` e `docs/A3_Progressive_Disclosure.md`.
- Seção S3 de `tasks/plans/v10-release-execution-plan.md` e
  `quality/v10-s2-stabilization-result.md`.
- `docs/V1.0_S1_Contratos_e_Compatibilidade.md` para contratos congelados,
  candidato e fronteiras V1; `docs/Caderno_de_Erros_Inteligente_Etapa_10_Plano_de_Testes.md`
  para casos oficiais e aplicabilidade; RNFs de segurança, privacidade,
  integridade, migração, logging e testabilidade em
  `docs/Caderno_de_Erros_Inteligente_Etapa_4_Requisitos_Nao_Funcionais.md`.
- `docs/V0.4_S5_Invariant_Checker.md` e
  `quality/v05-s8-integrity-compatibility-result.md` para o contrato read-only
  do checker e a matriz PostgreSQL crítica histórica.
- Código e testes diretamente relacionados; `scripts/quality.ps1`.

## Matriz de CTs e aplicabilidade

Os IDs `CT-129`–`CT-136` existem no catálogo oficial da Etapa 10. Foram usados
somente quando aplicáveis a S3; `CT-136` e auditoria final de navegadores ficam
com S4. A matriz não usa quantidade de testes como substituto de rastreabilidade.

| CT | Prioridade | Estado S3 | Evidência / limite |
| --- | --- | --- | --- |
| `CT-073` | P0 | COVERED / RELEASE_RERUN | FKs e constraints: testes dirigidos em `test_learning_foundation.py`, `test_question_catalog.py` e `test_origin_catalog.py`; gate migrou o banco SQLite vazio. |
| `CT-074` | P0 | COVERED / RELEASE_RERUN | Guards de modelo, serviços, seletores e Workspace em `test_learning_foundation.py`, `test_question_catalog.py`, `test_origin_catalog.py`, `test_initial_attempt.py` e `test_review_completion.py`. |
| `CT-075` | P0 | COVERED / RELEASE_RERUN | Troca atômica da revisão current em `test_question_catalog.py`. |
| `CT-076` | P0 | COVERED / RELEASE_RERUN | Unicidade da tentativa inicial válida em `test_learning_foundation.py`; atomicidade/replay em `test_initial_attempt.py`. |
| `CT-077` | P0 | COVERED / RELEASE_RERUN | Tentativa válida única por Review em `test_learning_foundation.py`. |
| `CT-078` | P0 | COVERED / RELEASE_RERUN | Ciclo ativo único e histórico concluído em `test_learning_foundation.py`. |
| `CT-079` | P0 | COVERED / RELEASE_RERUN | Review pendente única por guard e constraint em `test_learning_foundation.py`. |
| `CT-080` | P0 | COVERED / RELEASE_RERUN | Receipt idempotente e colisão em `test_learning_foundation.py`, mais replay/rollback em `test_initial_attempt.py` e `test_review_completion.py`. |
| `CT-081` | P0 | COVERED / RELEASE_RERUN | Grafo/schema congelado em testes de `test_learning_foundation.py` e `test_question_catalog.py`; `makemigrations --check --dry-run` e migration completa em banco descartável passaram no gate. |
| `CT-082` | P0 | N/A S3; S6 | Não houve delta de schema/migration na S2 ou S3. Upgrade representativo de release e reconciliação de histórico integram a prova S6/`CT-122`; não foi repetida nesta etapa. |
| `CT-083` | P0 | N/A S3 | Não há migration nova nem alteração de schema para falha injetada. Recovery de migração/cadeia de releases fica no recorte S6; gate confirmou ausência de migration pendente. |
| `CT-099` | P0 | COVERED / RELEASE_RERUN | `detect-secrets-hook` do gate autoritativo passou. |
| `CT-100` | P0 | COVERED / RELEASE_RERUN | Sanitização de conteúdo privado/segredos e erros em `test_operations.py`; falha de backup sanitizada em `test_backup_restore.py`. |
| `CT-101` | P0 | COVERED / RELEASE_RERUN | Token/contexto inválido, alterado, expirado e de outro Workspace em `test_initial_attempt.py` e `test_review_completion.py`; nenhuma tentativa indevida. |
| `CT-102` | P0 | COVERED NO LIMITE LOCAL | V1 é local/individual/loopback. A view de portabilidade fixa o Workspace local e não recebe ID arbitrário; `test_v05_s7_ui.py` verificou CSRF nos downloads e ausência de mutação do banco ativo. Não existe modo remoto/compartilhado autorizado nesta versão. |
| `CT-103` | P0 | SECURITY RECUT PASS; S6 FULL PROOF DEFERRED | ZIP traversal/checksum/schema hostil em `test_v05_s7_portability.py`; manifesto incompatível, destino existente e falha segura em `test_backup_restore.py`. Um restore mínimo foi validado somente em destino `tmp_path` descartável. Sem prova completa de recovery. |
| `CT-104` | P0 | COVERED / RELEASE_RERUN | `pip-audit --local --strict` passou no gate: `No known vulnerabilities found`. |
| `CT-121` | P0 | COVERED / RELEASE_RERUN | `test_stage5_promotion.py` percorre D1/D7/D14/D30, confere histórico e então abre a view real do dashboard com os mesmos fatos: 1 questão realizada, 5 tentativas (1 inicial/4 revisão), 4 acertos/1 erro e razão 4/5. |
| `CT-123` | P0 | COVERED / RELEASE_RERUN | Perfis/checks, bootstrap/jornada, migration em banco vazio, criação de backup mínimo e downloads foram cobertos pelo gate e testes focados. Só smoke de backup; backup/restore/recovery integral é S6. |
| `CT-129` | P0 | COVERED / RELEASE_RERUN | Bootstrap/seed repetido sem duplicação e com códigos/IDs estáveis em `test_error_categories.py`. |
| `CT-130` | P0 | COVERED / RELEASE_RERUN | Perfil de teste separado, banco sentinela intocado, segredo de produção ignorado no perfil de teste em `test_settings_profiles.py`; checks dos três perfis passaram no gate. |
| `CT-131` | P1 | COVERED / RELEASE_RERUN | Health só pronto com banco disponível e resposta/log sanitizados em `test_operations.py`. |
| `CT-132` | P0 | SHARED SMOKE PASS; S6 OWNER | Teste `test_ct132_creates_consistent_backup_and_minimal_manifest` e download local validaram criação/manifesto. Não equivale a restore/recovery integral. |
| `CT-133` | P0 | SECURITY SMOKE PASS; S6 OWNER | `test_ct133_restores_and_reconciles_minimal_foundation` restaurou fixture mínima em destino temporário isolado; rejeições hostis também passaram. Cadeia completa, recovery e banco real não foram exercitados. |
| `CT-134` | P0 | COVERED / RELEASE_RERUN | Structured logging, correlação, startup, erros sem traceback/conteúdo privado em `test_operations.py` e logs de backup inválido em `test_backup_restore.py`. |
| `CT-135` | P0 | COVERED / RELEASE_RERUN | Instantes controlados, fusos IANA, data local e ausência de alteração do relógio real em `test_time.py`. |
| `CT-136` | P1 | N/A S3; S4 OWNER | Layout, teclado, browser, zoom e acessibilidade final não foram auditados em S3. |

Casos de segurança transversais diretamente necessários também passaram: acesso
cross-Workspace/objeto (`CT-095`), CSRF (`CT-096`), escaping de saída (`CT-097`),
resposta correta/transitória (`CT-093/101`) e testes de perfil isolado
(`RNF-079`). Os P0/P1 do recorte S3 ficaram cobertos ou têm N/A com proprietário
e limite explícitos; não foi inventado CT nem renumerado caso.

## ResourceWarnings SQLite

- Reprodução inicial, antes de editar: o teste
  `test_historical_question_requires_retention_and_real_s6_restore` passou,
  mas emitiu dois `ResourceWarning: unclosed database`. A repetição com
  `-X tracemalloc=8` localizou as alocações precisamente nas conexões de leitura
  em `tests/test_v05_s2d.py` (linhas originais 571 e 580).
- A causa foi cleanup incompleto do teste: o context manager de
  `sqlite3.Connection` gerencia commit/rollback, mas não fecha a conexão. Os
  dois handles apenas liam cópias SQLite temporárias; não havia chamada de
  produção nos pontos de alocação. Não se observou lock, falha, alteração do
  banco real ou interferência entre testes.
- Correção mínima: envolver as duas conexões de leitura com
  `contextlib.closing`. Reteste com `-W always::ResourceWarning`: **1 passed**;
  nenhum warning SQLite. A suíte/gate posterior também passou.
- Classificação: `TEST_CLEANUP_FINDING`, resolvido; sem `PRODUCT_RESOURCE_FINDING`.
- A execução diagnóstica ampla mostrou um aviso separado do
  `TemporaryDirectory` global em `config.settings.test`, limpo implicitamente
  pelo Python ao encerrar o processo. É infraestrutura do perfil de testes,
  sem conexão SQLite, produto ou dado real; foi registrado como observação, sem
  alteração de configuração fora do finding recorrente autorizado.

## Banco, integridade, Workspace e migrations

- Perfis e gate usam SQLite; bancos e fixtures de teste foram descartáveis. O
  teste de perfil com database sentinela confirmou que a suíte usa outro
  caminho e preserva os bytes do sentinela.
- FKs, `CHECK`/`UNIQUE`, vínculos entre Workspaces, revisão corrente, estados de
  tentativa/ciclo/Review, rollback, receipt, idempotência, replay, concorrência
  relevante e consistência de fatos/derivados foram exercitados pelos testes
  focados e pela suíte completa.
- Invariant checker: testes confirmaram catálogo atual de 25 invariantes,
  execução SQLite `mode=ro`, saída sanitizada, códigos de saída e ausência de
  reparo/mutação em casos saudáveis e negativos.
- Gate: `makemigrations --check --dry-run` → `No changes detected`; migração
  completa de banco vazio passou. Nenhuma migration criada ou pendente.
- Configuração de produto usa `django.db.backends.sqlite3`. PostgreSQL não é
  backend de produto suportado/configurado no recorte V1 nem houve requisito ou
  alteração de backend nesta tarefa; por isso a matriz PostgreSQL crítica não
  foi executada. A matriz descartável PostgreSQL de V0.5-S8 permanece somente
  evidência histórica, sem alegação de rerun V1.

## Segurança, privacidade, logs e dependências

- Testes dirigidos cobriram isolamento por Workspace/objeto, CSRF e rejeição
  cross-site, validação de contexto/token, escaping, ZIP traversal/checksum,
  rejeição antes de mutação, perfil local, health, logs e integridade read-only.
- O produto permanece local, individual e loopback conforme V10-D2; não foi
  introduzido tráfego, telemetria, serviço externo ou modo remoto. Fixtures
  usaram dados sintéticos. A evidência registra somente resumos, sem conteúdo de
  estudo, credenciais ou tokens.
- `detect-secrets-hook`: passou. `pip-audit --local --strict`: passou sem
  vulnerabilidades conhecidas. Nenhuma dependência foi atualizada.
- `CEI-EXPORT-1.0`, V10-D1/D2, `REV-FIXA-1.0`, `DOM-HEUR-1.0`, `PRI-HEUR-1.0`,
  histórico V0.5 e schema permaneceram intactos.

## Findings

| ID | Finding | Severidade inicial | Resultado |
| --- | --- | --- | --- |
| `S3-F01` | Dois handles SQLite abertos por teste de leitura, encontrados por ResourceWarning recorrente. | Minor / cleanup de teste | Resolvido com `closing`; reteste warning-clean para SQLite. |
| `S3-F02` | A jornada D1/D7/D14/D30 não abria a dashboard real com os mesmos fatos, apesar de testes separados para jornada e dashboard. | Major / lacuna de prova P0 | Resolvido ampliando o smoke existente e conferindo os valores reconciliados da view. |

Blocker aberto: **0**. Major aberto: **0**. Minor novo aberto: **0**. Nenhuma
vulnerabilidade, finding material de privacidade/integridade, corrupção, perda
de dados, vazamento cross-Workspace ou necessidade de decisão de schema foi
observada. O Minor histórico S9 de evidência manual de acessibilidade não foi
reaberto; a auditoria final pertence a S4.

## Alterações e testes

- `tests/test_v05_s2d.py`: fecha explicitamente as duas conexões SQLite de
  asserção do teste; nenhum código de produto foi alterado.
- `tests/test_stage5_promotion.py`: amplia o smoke para abrir a dashboard real
  e reconciliar métricas com os fatos da jornada.
- Sem feature nova, alteração de fórmula, migration ou dependência.
- Reproduções pré-correção: teste S2D passou com 2 warnings SQLite e um aviso
  separado de TemporaryDirectory; tracemalloc confirmou as duas linhas de
  origem. A ausência dos warnings SQLite foi confirmada após a correção.
- Matriz focada de banco, security, logging, profiles, checker, políticas e
  regressão: **116 passed em 29,52 s**.
- CT-121 após a ampliação: **1 passed em 4,43 s**.
- CT-133 security smoke em destino temporário: **1 passed em 3,86 s**.
- Reteste final do finding SQLite, `-W always::ResourceWarning`:
  **1 passed em 4,94 s**, nenhum warning SQLite.
- Ruff check: passou; Ruff format check: 2 arquivos já formatados.
- Primeiro gate completo da implementação: GREEN, exit 0, 510 testes em
  219,48 s, 86% cobertura global, cobertura mínima de domínio aprovada;
  lock/sync, runtime, rastreabilidade, perfis, migrations, banco vazio,
  formatação, Ruff, mypy (194 fontes), detect-secrets e pip-audit passaram.
  Duração total 282,7 s; `No known vulnerabilities found`.
- Gate final após atualização de `PROJECT_STATE.md`, arquivamento do contrato e
  retorno de `tasks/current.md` a `NO_TASK_AUTHORIZED`: **GREEN, exit code 0**;
  510 testes em **218,07 s**, cobertura global **86%**, cobertura mínima de
  domínio aprovada. Lock/sync, runtime, rastreabilidade, três perfis, ausência
  de migration, banco vazio, formatação, Ruff, mypy (194 fontes),
  detect-secrets e pip-audit passaram. Duração total **272,3 s**;
  `No known vulnerabilities found`.

## A8 deep

Revisão profunda do contrato, diff, risco de falha, integridade, segurança,
privacidade, validade dos testes, migrations, dependências, warnings, fronteiras
S3/S4/S5/S6 e evidência. O finding de recursos está restrito ao teste e agora
fecha em sucesso ou exceção; o novo assert usa a view/read model real e os mesmos
fatos sintéticos do fluxo. Nenhum impacto de produto, schema ou escopo protegido
foi encontrado.

Resultado: **APPROVED**. Blocker 0, Major 0, Minor novo aberto 0. Nenhum gatilho
de escalonamento para GPT-6 Sol Medium. A7 solicitado: GPT-6 Luna xHigh; a
telemetria do modelo efetivo não estava disponível para verificação
independente.

## Decisão e fronteiras

Decisão final: **`S3_COMPLETED`**; S1/S2/S3 concluídas; S4/S5/S6 continuam NÃO
AUTORIZADAS e não iniciadas. A prova integral de
`CT-113–120/122`, backup/restore/recovery, cadeia V0.4.4→V0.5→V1 e round-trip CEI
V0.5→V1 continua reservada à S6. Não houve browser/a11y final de S4, BCR/tuning
de S5, piloto, promoção, tag, release, commit ou push.
