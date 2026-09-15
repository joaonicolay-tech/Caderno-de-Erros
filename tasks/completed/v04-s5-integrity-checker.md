# Task Contract

Status: AUTHORIZED

## Identification

- Task ID: V0.4-S5
- Product version: V0.4
- Stage: S5 â€” Integridade operacional, logs e invariant checker
- Task type: product integrity / diagnostics / invariant checker / operational logging
- Size: L
- Risk: high
- Recommended execution profile: GPT-5.6 Sol, High reasoning
- Expected review: deep
- Persistent A4 plan: required before implementation, conforme V0.4-P0

## Goal

Implementar a camada de integridade operacional da V0.4: um invariant checker
read-only que detecte estados inconsistentes, produza diagnÃ³stico estruturado e
sanitizado, reutilize o logging e a correlaÃ§Ã£o existentes e retorne exit codes
Ãºteis, sem corrigir ou reescrever dados silenciosamente.

O resultado deve fornecer evidÃªncia operacional suficiente para uso posterior
nos exercÃ­cios de restore, no candidato de release, no hardening e no piloto,
sem executar nem antecipar essas etapas.

## Context

- `tasks/plans/v04-release-execution-plan.md` define a decomposiÃ§Ã£o da release,
  as invariantes mÃ­nimas de S5 e as fronteiras com S6â€“S9; o plano nÃ£o amplia
  este contrato.
- `docs/V0.4_S1_Contratos_de_Metricas_e_Reconciliacao.md` permanece
  autoritativo para a semÃ¢ntica analÃ­tica. S5 pode detectar estados que
  comprometam S1/S2/S3, mas nÃ£o redefinir universos, datas, denominadores,
  resÃ­duos ou reconciliaÃ§Ãµes.
- `docs/V0.4_S2_Interface_Analitica_Interna.md` e a implementaÃ§Ã£o em
  `modules.analytics` sÃ£o a fronteira read-only existente; nÃ£o recalcular o
  dashboard nem criar consultas analÃ­ticas paralelas sem necessidade
  demonstrada.
- `docs/ADR-005_Logging_Correlacao_e_Health_Local_V0.1.md`,
  `modules.operations` e `tests/test_operations.py` sÃ£o a baseline vigente de
  logging JSON, eventos, correlaÃ§Ã£o transitÃ³ria e sanitizaÃ§Ã£o. S5 deve
  estendÃª-la, nÃ£o criar um segundo sistema.
- `docs/ADR-007_Backup_e_Restauracao_Minima_SQLite_V0.1.md` e os comandos/testes
  de `modules.data_management` demonstram os padrÃµes existentes de comando
  operacional, diagnÃ³stico read-only, integridade SQLite, correlaÃ§Ã£o e falha
  segura. S5 nÃ£o modifica nem executa a etapa de restore S6.
- Os modelos, migrations, validators, serviÃ§os, policies, selectors e testes
  existentes sÃ£o a fonte executÃ¡vel para decidir quais invariantes realmente
  existem. NÃ£o inferir relaÃ§Ãµes ou regras apenas de exemplos conceituais.
- Antes da implementaÃ§Ã£o, criar e ativar um plano persistente A4 que decomponha
  no mÃ­nimo: (1) baseline e catÃ¡logo de invariantes; (2) interface/resultados;
  (3) checker read-only; (4) logging/saÃ­da; (5) exit codes; (6) testes;
  (7) documentaÃ§Ã£o; e (8) validaÃ§Ã£o/review/gate. O plano nÃ£o amplia Goal,
  Expected Scope ou Protected Scope.

## PrincÃ­pio central

O invariant checker Ã© **detector, nÃ£o reparador**. Ele deve somente ler,
validar, reportar e retornar status/exit code. NÃ£o pode alterar banco, corrigir
registros, criar objetos, apagar dados, fazer backfill nem reescrever histÃ³rico.
Qualquer capacidade de reparo exige trabalho futuro e autorizaÃ§Ã£o prÃ³pria.

## Acceptance Criteria

- Existe uma superfÃ­cie operacional coerente com o repositÃ³rio, preferencialmente
  um Django management command se a auditoria confirmar esse padrÃ£o, que
  executa o checker sem efeitos persistentes.
- Existe catÃ¡logo explÃ­cito que distingue invariantes jÃ¡ impostas por schema,
  constraints, validators, serviÃ§os, policies e testes das inconsistÃªncias que
  ainda podem existir ou merecem diagnÃ³stico operacional. ValidaÃ§Ã£o nÃ£o Ã©
  duplicada sem justificativa.
- O catÃ¡logo cobre, quando sustentado pelo domÃ­nio real, integridade SQLite e
  FKs, isolamento/coerÃªncia de Workspace, question/versionamento, taxonomia,
  Attempts, ErrorClassification, ReviewCycle, Reviews, receipts/idempotÃªncia,
  estados e datas, e condiÃ§Ãµes que comprometam a reconciliaÃ§Ã£o analÃ­tica.
- InconsistÃªncia cross-workspace Ã© detectada e tratada como severidade alta.
  RelaÃ§Ãµes indiretas tambÃ©m sÃ£o verificadas onde o schema/domÃ­nio as exigir.
- Invariantes de Attempt respeitam os tipos INITIAL/REVIEW, status, resultado,
  Question/revisÃ£o relacionada, datas locais e combinaÃ§Ãµes realmente
  suportadas, sem redefinir contratos S1/S2.
- Invariantes de ReviewCycle/Review respeitam a polÃ­tica existente de
  D1/D7/D14/D30, origem, estado, data, pendÃªncia executÃ¡vel, progressÃ£o,
  archive/suspensÃ£o e relaÃ§Ã£o com tentativa inicial, sem introduzir nova
  polÃ­tica de revisÃ£o.
- VerificaÃ§Ãµes analÃ­ticas detectam somente dados/relacionamentos impossÃ­veis,
  ausentes ou inconsistentes que possam quebrar S1/S2/S3; nÃ£o recalculam o
  dashboard inteiro sem necessidade nem transformam resÃ­duo sem classificaÃ§Ã£o
  permitido por S1 em corrupÃ§Ã£o.
- Invariantes de versionamento, encadeamento, revisÃ£o corrente e histÃ³rico sÃ³
  sÃ£o verificadas quando aplicÃ¡veis ao modelo existente; nÃ£o se implementa
  histÃ³rico de correÃ§Ãµes V0.5.
- Invariantes de taxonomia preservam as relaÃ§Ãµes e o Workspace existentes,
  sem criar nova taxonomia ou inventar obrigatoriedade que o domÃ­nio nÃ£o tem.
- HÃ¡ poucas severidades claras, preferencialmente alinhadas Ã s convenÃ§Ãµes
  existentes, e o efeito de cada severidade sobre o exit code Ã© documentado.
- O contrato de exit codes Ã© explÃ­cito: `0` nunca esconde inconsistÃªncia
  impeditiva; cÃ³digos nÃ£o zero diferenciam, quando Ãºtil, checker concluÃ­do com
  findings e falha tÃ©cnica/operacional. Os valores concretos devem ser coerentes
  com os padrÃµes observados no projeto.
- A saÃ­da Ã© determinÃ­stica, legÃ­vel no terminal, identificÃ¡vel por
  invariante e suficiente para diagnÃ³stico, com IDs tÃ©cnicos e contexto mÃ­nimo.
  NÃ£o expÃµe respostas, textos integrais de questÃ£o, credenciais, secrets,
  tokens, dados pessoais, paths privados, payloads ou stack trace bruto.
- O checker reutiliza `modules.operations` para eventos estruturados e
  sanitizaÃ§Ã£o. Registra eventos Ãºteis de inÃ­cio, conclusÃ£o, quantidade de
  checks, findings por severidade e falha tÃ©cnica, sem spam por registro
  saudÃ¡vel e sem criar auditoria funcional persistente.
- A correlaÃ§Ã£o existente Ã© reutilizada quando coerente com comandos/operaÃ§Ãµes.
  Se ela nÃ£o se aplicar a uma superfÃ­cie confirmada, nÃ£o se cria subsistema
  novo somente para S5.
- Falhas do checker produzem mensagem recuperÃ¡vel com prÃ³xima aÃ§Ã£o possÃ­vel,
  mantÃªm detalhes tÃ©cnicos sanitizados nos logs apropriados e nÃ£o confirmam
  sucesso nem emitem exit `0` de forma enganosa.
- O desenho Ã© adequado ao baseline local e evita O(NÂ²) Ã³bvio, N+1 e queries
  por registro quando relaÃ§Ãµes, anotaÃ§Ãµes ou consultas em lote resolverem,
  sem antecipar otimizaÃ§Ã£o extrema de S8/BCR-1.
- A documentaÃ§Ã£o operacional explica como executar, o que o checker verifica e
  nÃ£o verifica, severidades, exit codes, leitura dos findings, carÃ¡ter
  read-only, limitaÃ§Ãµes e integraÃ§Ã£o futura em S6, S8 e S9.

## Expected Scope

- Auditar o logging estruturado/correlaÃ§Ã£o existentes, comandos
  administrativos, models/constraints, validators, serviÃ§os/policies,
  isolamento por Workspace, ReviewCycle/Reviews, Attempts,
  ErrorClassification, Question/versionamento, taxonomia, timeline,
  analytics S1/S2, backup/restore e testes de integridade relacionados.
- Criar o plano persistente A4 obrigatÃ³rio antes da implementaÃ§Ã£o.
- Criar camada read-only de invariantes e DTOs/resultados diagnÃ³sticos quando
  agregarem clareza e seguranÃ§a ao contrato.
- Criar ou ajustar um comando operacional coerente com os padrÃµes existentes.
- Definir severidades, exit codes, saÃ­da humana sanitizada e mensagens
  recuperÃ¡veis.
- Estender somente o catÃ¡logo de eventos/logs existente necessÃ¡rio a S5,
  preservando seu formatter, sanitizaÃ§Ã£o e correlaÃ§Ã£o.
- Criar testes unitÃ¡rios, de integraÃ§Ã£o e de banco que comprovem invariantes,
  failure modes, saÃ­da, logs, exit codes, escala proporcional e read-only.
- Criar documentaÃ§Ã£o operacional e atualizar plano, estado, rastreabilidade e
  mÃ©tricas A7 somente conforme execuÃ§Ã£o e conclusÃ£o reais.
- Aplicar review A8 profundo antes do encerramento.

## Protected Scope

- Contratos semÃ¢nticos S1, serviÃ§os/read models analÃ­ticos S2 e dashboard S3.
- Consulta, filtros, detalhe e histÃ³rico S4, salvo referÃªncia mÃ­nima necessÃ¡ria
  para verificar integridade; nenhuma mudanÃ§a funcional Ã© autorizada.
- Schema e migrations, inclusive constraints novas. Se uma constraint ou
  migration parecer necessÃ¡ria, registrar o finding e avaliar trabalho futuro,
  sem implementÃ¡-la nem ampliar este contrato.
- Regras funcionais, serviÃ§os de escrita, polÃ­tica de revisÃ£o, fatos
  histÃ³ricos e significado das mÃ©tricas.
- Reparo automÃ¡tico/manual, mutaÃ§Ã£o, backfill, exclusÃ£o, correÃ§Ã£o estrutural e
  novo sistema de auditoria funcional.
- Backup/restore S6, operaÃ§Ã£o Windows S7, hardening/BCR-1 S8 e piloto/promoÃ§Ã£o
  S9. Nenhuma dessas etapas Ã© autorizada por S5.
- Monitoramento remoto, alertas/notificaÃ§Ãµes, telemetria, JSON mode adicional
  sem convenÃ§Ã£o ou necessidade real, e funcionalidades V0.5+.
- `docs/PROJECT_DEVELOPMENT_ARCHITECTURE_V1.md`, Skills,
  `scripts/quality.ps1` e configuraÃ§Ãµes pessoais/globais.

## Constraints

- NÃ£o usar `.save()`, `.update()`, `.delete()`, criaÃ§Ã£o automÃ¡tica, bootstrap
  corretivo nem helper com side effect durante a verificaÃ§Ã£o.
- NÃ£o enfraquecer constraint, validator, regra ou produÃ§Ã£o para fabricar
  corrupÃ§Ã£o de teste. Quando o ORM impedir um estado invÃ¡lido, usar tÃ©cnica de
  teste apropriada, limitada e isolada.
- NÃ£o tratar exemplo conceitual como invariante sem confirmar o domÃ­nio real.
  DivergÃªncia entre cÃ³digo, migration, teste, ADR e documento deve ser exposta
  e resolvida antes de decisÃ£o estrutural.
- NÃ£o depender somente de mocks para provar invariantes de banco ou o carÃ¡ter
  read-only.
- NÃ£o imprimir nem registrar conteÃºdo sensÃ­vel integral. Testes devem usar
  sentinelas e provar sua ausÃªncia tanto da saÃ­da humana quanto dos logs.
- NÃ£o criar modo machine-readable novo sem convenÃ§Ã£o existente ou necessidade
  demonstrada; a saÃ­da padrÃ£o deve servir ao operador humano.
- NÃ£o estimar duraÃ§Ã£o, cotas, observaÃ§Ãµes ou mÃ©tricas ausentes. S5 deve ser
  registrada em A7 separadamente do bootstrap, com `unknown` quando aplicÃ¡vel.
- NÃ£o fazer commit, push, tag ou release sem autorizaÃ§Ã£o expressa.

## Verification

- Cobrir base consistente com sucesso e violaÃ§Ãµes sintÃ©ticas isoladas e
  mÃºltiplas para Workspace, Attempt, ReviewCycle/Review, versionamento/taxonomia
  quando aplicÃ¡veis e condiÃ§Ãµes que comprometam analytics.
- Testar finding identificÃ¡vel, ordenaÃ§Ã£o/saÃ­da determinÃ­stica, severidades,
  sucesso, findings e falha operacional nos exit codes quando testÃ¡vel.
- Provar sanitizaÃ§Ã£o da saÃ­da e dos logs com sentinelas, correlaÃ§Ã£o quando
  aplicÃ¡vel e ausÃªncia de traceback/conteÃºdo privado desnecessÃ¡rio.
- Provar read-only por contagens e estado antes/depois, incluindo cenÃ¡rios de
  finding e falha; auditar o caminho executÃ¡vel para qualquer helper mutÃ¡vel.
- Testar com pelo menos dois Workspaces e dados persistidos reais sempre que a
  invariante depender do banco; incluir volume proporcional e auditoria de
  queries para evitar O(NÂ²)/N+1 Ã³bvio.
- Executar review A8 profundo procurando especialmente mutaÃ§Ã£o, falso
  positivo estrutural, falso negativo Ã³bvio, invariante inventada, regra em
  conflito, isolamento incompleto, saÃ­da sensÃ­vel, exit code enganoso, logging
  duplicado, O(NÂ²), teste incapaz de provar corrupÃ§Ã£o e expansÃ£o para repair
  tool. A conclusÃ£o exige `APPROVED`, sem Blocker ou Major aberto.
- Executar `git diff --check` e o gate autoritativo:
  `powershell -NoProfile -ExecutionPolicy Bypass -File
  .\scripts\quality.ps1`, ambos aprovados com exit code observado.

## Documentation Impact

Criar documentaÃ§Ã£o operacional concisa para o checker e atualizar somente a
rastreabilidade realmente afetada. Na conclusÃ£o real, encerrar o plano A4,
arquivar S5, atualizar `PROJECT_STATE.md` e registrar mÃ©tricas A7 com
proveniÃªncia, sem alterar a Architecture v1.0 nem iniciar etapas posteriores.

## Done When

- O plano A4 foi criado antes da implementaÃ§Ã£o, seguido e encerrado com a
  decomposiÃ§Ã£o mÃ­nima exigida.
- O catÃ¡logo de invariantes estÃ¡ documentado, fundamentado no domÃ­nio real e
  coberto por testes proporcionais de Workspace, relaÃ§Ãµes, tempo/review,
  versionamento/taxonomia e analytics onde aplicÃ¡veis.
- O checker read-only estÃ¡ implementado como detector, nunca reparador; sua
  execuÃ§Ã£o nÃ£o altera contagens, estado, schema nem histÃ³rico.
- Severidades e exit codes estÃ£o definidos; exit `0` nÃ£o mascara finding
  impeditivo nem falha operacional.
- SaÃ­da e logs sÃ£o determinÃ­sticos, estruturados, correlacionados quando
  aplicÃ¡vel, sanitizados e recuperÃ¡veis, sem conteÃºdo privado desnecessÃ¡rio.
- A documentaÃ§Ã£o operacional cobre execuÃ§Ã£o, escopo, exclusÃµes, severidades,
  exit codes, findings, read-only, limitaÃ§Ãµes e integraÃ§Ã£o futura em S6/S8/S9.
- NÃ£o houve migration, mudanÃ§a de schema, reparo de dados, alteraÃ§Ã£o de
  contratos/regras protegidos nem implementaÃ§Ã£o de S6â€“S9.
- Testes focados estÃ£o GREEN; review A8 profundo estÃ¡ `APPROVED`, sem Blocker
  ou Major; `git diff --check` passa; gate autoritativo estÃ¡ GREEN com exit
  code `0`; nenhum P0/P1 aplicÃ¡vel permanece aberto.
- S5 estÃ¡ arquivada, plano/estado/mÃ©tricas refletem somente evidÃªncia real,
  `tasks/current.md` retornou a `NO_TASK_AUTHORIZED` e S6 permanece nÃ£o
  autorizada.

## Evidência de encerramento

- Auditoria inicial: `modules.operations` confirmou logging JSON/correlação e
  os comandos Django existentes confirmaram a superfície operacional.
  Constraints/validators/services foram separados das relações compostas que
  ainda exigem diagnóstico. A validação legada de restore que rejeita todo erro
  sem classificação foi registrada como divergência para a futura S6; S5
  preserva o resíduo permitido por S1.
- Implementação: `python manage.py check_integrity` executa 17 invariantes em
  snapshot SQLite aberto com `mode=ro`; não há repair, write, migration,
  bootstrap, recalculadora de analytics ou serviço mutável no caminho
  executável.
- Contrato operacional: exit `0` para base saudável, `2` para findings
  impeditivos e `3` para falha operacional. Saída limitada preserva o total;
  findings carregam somente IDs/códigos/datas/contexto técnico permitido.
- Logging: eventos agregados `INTEGRITY_CHECK_STARTED`,
  `INTEGRITY_CHECK_SUCCEEDED`, `INTEGRITY_CHECK_FINDINGS` e
  `INTEGRITY_CHECK_FAILED` reutilizam sanitização e correlação existentes.
- Testes: 10 testes específicos GREEN; 153 regressões diretamente relacionadas
  GREEN; cobertura focada de 90% (checker 88%, comando 95%). Foram provados
  base saudável, duas Workspaces, FK órfã, taxonomia, versionamento, Attempt,
  data civil, ReviewCycle/Review, ErrorClassification e resíduo legítimo,
  recibos, limite/ordenação/query count, read-only, sanitização, logs e exit
  codes.
- Teste manual seguro: comando real em SQLite descartável retornou exit `0`,
  formato `HEALTHY` e SHA-256 do banco idêntico antes/depois.
- Review A8 profundo: **APPROVED**, sem Blocker ou Major aberto. A revisão
  corrigiu antes do gate a sanitização de valores técnicos corrompidos, a
  transição histórica `INITIAL_ERROR_TO_D1` e a contagem completa do
  `integrity_check`.
- `git diff --check`: aprovado. Primeiro gate ficou inconclusivo somente no
  `pip-audit` por `WinError 10013` do sandbox; repetição autorizada fora do
  sandbox: **GREEN**, exit code `0`, 302 testes em 62,55 s, 87% de cobertura
  global e duração total do gate 91,5 s.
- Nenhuma migration, mudança de schema, alteração de S1-S4, repair, execução de
  restore, BCR-1, piloto, commit, push, tag ou release foi realizada. S6 não foi
  iniciada nem autorizada.

