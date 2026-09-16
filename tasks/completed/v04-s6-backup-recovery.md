# Task Contract

Status: AUTHORIZED

## Identification

- Task ID: V0.4-S6
- Product version: V0.4
- Stage: S6 — Backup, restauração e recuperação comprovada
- Task type: data protection / backup / restore / recovery validation
- Size: M
- Risk: high
- Recommended execution profile: GPT-5.6 Sol, High reasoning
- Expected review: deep
- Persistent A4 plan: required before implementation, conforme V0.4-P0
- Active A4 plan: `tasks/plans/v04-s6-backup-recovery.md`

## Goal

Consolidar e validar o fluxo de backup e recuperação da V0.4 para que o banco
local SQLite possa ser copiado como snapshot consistente, restaurado em destino
isolado, aberto com segurança, validado estruturalmente, reconciliado e
submetido ao invariant checker S5 antes de ser considerado recuperável.

O mecanismo existente deve evoluir pelo menor delta comprovadamente necessário
para tornar o processo operacional, documentado e apto a fornecer evidência
objetiva para o hardening e o piloto futuros, sem reescrever uma solução já
funcional nem prometer recuperação não testada.

## Context

- `docs/PROJECT_DEVELOPMENT_ARCHITECTURE_V1.md` permanece a baseline
  operacional aprovada e congelada. Autorização, plano, implementação, testes,
  review, gate e encerramento continuam fases distintas.
- `tasks/plans/v04-release-execution-plan.md` define S6 como a etapa de backup,
  restauração e recuperação comprovada, exige plano A4 e separa seu mecanismo da
  operação Windows S7, do hardening S8 e do piloto/promoção S9. O plano não
  amplia este contrato.
- `docs/ADR-007_Backup_e_Restauracao_Minima_SQLite_V0.1.md`,
  `modules.data_management`, seus management commands e
  `tests/test_backup_restore.py` são o baseline executável. Já existem backup
  pela SQLite backup API, manifesto/checksum, validação física, publicação sem
  sobrescrita, restore somente em destino novo, reconciliação até V0.3, logging
  correlacionado e failure modes cobertos. S6 deve auditar e fortalecer esse
  mecanismo, não substituí-lo sem lacuna concreta.
- `docs/V0.4_S5_Invariant_Checker.md` é o contrato operacional do checker:
  exit `0` significa execução saudável, exit `2` significa findings impeditivos
  e exit `3` significa falha operacional inconclusiva. S6 deve reutilizar sua
  interface, sem duplicar invariantes nem converter finding/falha em sucesso.
- `docs/V0.4_S1_Contratos_de_Metricas_e_Reconciliacao.md` permanece
  autoritativo para a semântica analítica. Uma `Attempt VALID` incorreta sem
  `ErrorClassification` é resíduo legítimo; a reconciliação legada de restore,
  hoje mais estrita, deve ser alinhada a esse contrato antes da integração com
  S5, sem alterar a semântica do checker.
- Antes de qualquer implementação, criar e ativar um plano persistente A4
  específico para S6 que cubra no mínimo: (1) auditoria do backup existente;
  (2) consistência do snapshot; (3) restore isolado; (4) abertura e validação;
  (5) integração com o checker S5; (6) reconciliação; (7) falhas e recuperação;
  (8) documentação; e (9) testes, review e gate. O plano não amplia Goal,
  Expected Scope ou Protected Scope.

## Central Principle

**Backup só é considerado válido se puder ser restaurado e validado.** A mera
existência de um arquivo `.sqlite3`, de manifesto ou de checksum não comprova
recuperabilidade. A evidência completa deve percorrer, em ambiente isolado:

`backup → restore → abertura → integridade física → checker S5 → reconciliação`

## Acceptance Criteria

- A auditoria inicial identifica comandos e serviços existentes, diretórios e
  destinos, naming/versionamento, comportamento com o banco em uso, validações,
  testes, logs, mensagens e proteções contra sobrescrita, classificando cada
  parte como adequada, parcial, ausente ou insegura.
- O backup usa a SQLite backup API ou mecanismo equivalente comprovadamente
  seguro para produzir um ponto consistente dos dados confirmados. Se a
  consistência não puder ser garantida, a operação falha de forma explícita e
  não publica artefato potencialmente corrompido.
- Destino e nome do backup são previsíveis e identificáveis; reexecução não
  sobrescreve silenciosamente banco, backup, manifesto ou outro arquivo. A
  conclusão informa o artefato no nível operacional necessário, sem expor
  conteúdo ou caminhos privados em logs.
- Metadados permanecem mínimos e úteis — instante, identificação do artefato,
  tamanho, formato/versão ou schema quando disponível e resultado — sem criar
  catálogo complexo, storage remoto ou conteúdo de estudo no manifesto.
- A validação de recuperação restaura em arquivo/ambiente isolado e nunca
  substitui automaticamente o banco principal. Falha do ensaio não altera o
  banco ativo nem o backup original.
- O banco restaurado abre com conexão SQLite e com a aplicação/configuração
  isolada aplicável, possui migrations/estrutura compatíveis com a versão
  corrente e passa por `PRAGMA integrity_check` e
  `PRAGMA foreign_key_check` ou verificações equivalentes documentadas. Não há
  migration automática para fazer um backup incompatível passar.
- O checker S5 é executado sobre o restore isolado pela interface existente.
  Exit `0` compõe a evidência saudável; exit `2` invalida a recuperação por
  inconsistência de dados; exit `3` torna a validação inconclusiva/falha. Nenhum
  desses resultados é mascarado.
- A reconciliação mínima comprova que o restore representa o backup esperado
  por contagens, IDs/markers, migrations, fingerprint/checksum ou outros sinais
  técnicos proporcionais. Integridade física, invariantes de domínio S5 e
  reconciliação são verificações distintas.
- A reconciliação cobre as entidades e fatos V0.4 já persistidos e respeita os
  contratos S1-S5, inclusive o resíduo sem classificação permitido por S1, sem
  duplicar o catálogo de invariantes nem recalcular analytics.
- Arquivo inexistente, manifesto/arquivo inválido, checksum divergente, SQLite
  corrompido, permissão negada, espaço insuficiente quando detectável, versão ou
  migrations incompatíveis, destino existente, banco bloqueado, findings do
  checker e falha operacional do checker terminam com status seguro e mensagem
  recuperável que indique o próximo passo possível.
- Se a auditoria encontrar algum fluxo existente capaz de substituir o banco
  ativo, ele preserva guards, origem explícita, fechamento de conexões, backup
  pré-restore ou proteção equivalente, substituição/rollback seguros quando
  aplicáveis. S6 não cria um novo restore destrutivo sobre o banco ativo.
- Backup, validação, restore, checker e resultado final reutilizam o logging
  estruturado e a correlação existentes, com eventos úteis de início, sucesso e
  falha. Logs não contêm enunciados, respostas, dados pessoais, secrets,
  traceback bruto ou paths privados desnecessários.
- O procedimento é reproduzível e idempotente dentro de sua semântica: repetir
  backup não sobrescreve artefato e repetir validação não modifica backup,
  restore nem banco principal.
- RPO máximo de 24 horas, RTO máximo de 4 horas e a retenção vigente de ao
  menos sete versões diárias e quatro semanais são tratados como objetivos
  operacionais locais das fontes atuais, associados ao procedimento realmente
  disponível e à evidência medida. Se não houver agendamento automático, o RPO
  depende da frequência manual; duração ausente ou não medida permanece
  `unknown`, sem SLA ou resultado inventado.
- A documentação operacional explica criação, localização/identificação,
  validação, restore isolado, salvaguardas, checker S5, resultados, falhas,
  RPO/RTO aplicáveis, ação diante de finding e ação diante de corrupção.
- A documentação identifica os comandos/passos que S7 deverá expor e as
  verificações que S8/S9 deverão consumir, sem implementar S7, executar S8 ou
  iniciar piloto/promoção.

## Expected Scope

- Auditar o serviço, os comandos, testes, documentos, logging, paths e failure
  modes de backup/restore já existentes.
- Criar o plano persistente A4 obrigatório antes da implementação.
- Corrigir somente lacunas comprovadas no snapshot consistente, validação,
  publicação segura, proteção contra overwrite, restore isolado, abertura,
  compatibilidade estrutural, reconciliação e mensagens recuperáveis.
- Integrar o checker S5 ao fluxo de validação do restore reutilizando sua
  interface e preservando seus exit codes e catálogo.
- Alinhar a reconciliação legada aos fatos e contratos V0.4, especialmente ao
  resíduo sem classificação permitido por S1, sem redefinir regra de domínio.
- Criar ou ajustar testes automatizados de backup saudável, escrita concorrente,
  restore isolado, abertura, checker saudável/com finding, corrupção, arquivo
  inexistente, destino existente, isolamento, logging e falhas seguras.
- Executar ensaio controlado com dados sintéticos/seguros: criar base, gerar
  backup, restaurar em destino isolado, abrir, executar checks SQLite, executar
  S5, reconciliar e registrar somente a evidência observada.
- Produzir ou atualizar documentação operacional, evidência de restore e
  rastreabilidade mínima; registrar métricas A7 de S6 separadamente do bootstrap
  e aplicar review A8 profundo.
- Atualizar plano, estado, arquivo da tarefa e métricas apenas no encerramento
  real, conforme a evidência obtida.

## Protected Scope

- Regras de domínio, contratos semânticos S1, analytics S2, dashboard S3 e
  consulta/detalhe/histórico S4.
- Semântica, catálogo, severidades e exit codes do checker S5, salvo correção de
  blocker concreto comprovado e explicitamente tratada sem ampliar S6.
- Schema, migrations, constraints históricas e política de revisão.
- Restore automático/destrutivo sobre o banco principal, nova GUI de backup,
  exportação CEI, storage remoto, nuvem, scheduler/serviço residente,
  criptografia própria e catálogo complexo de backups.
- Operação/packaging Windows S7, hardening e `BCR-1` S8, piloto/promoção S9 e
  qualquer funcionalidade V0.5+.
- `docs/PROJECT_DEVELOPMENT_ARCHITECTURE_V1.md`, Skills e
  `scripts/quality.ps1`.

## Constraints

- Não gerar migration nem alterar schema.
- Não copiar o arquivo SQLite arbitrariamente enquanto houver possibilidade de
  escrita; comprovar snapshot consistente ou recusar a operação.
- Não migrar, reparar, completar, normalizar, apagar ou fazer backfill no
  backup/restore para obter resultado saudável.
- Não sobrescrever arquivo existente nem aceitar destino que possa tocar banco
  ativo, backup original, manifesto ou caminho inesperado.
- Não duplicar lógica interna do checker S5 nem tratar findings/falha técnica
  como sucesso.
- Não reescrever mecanismo funcional sem lacuna concreta e evidência de que a
  menor correção não basta.
- Não depender somente de mocks para provar consistência SQLite, isolamento,
  ausência de corrupção ou preservação do banco principal.
- Não usar dados pessoais reais quando dados sintéticos/seguros bastarem; não
  expor conteúdo estudado, secrets ou paths privados desnecessários.
- Não inventar duração, RPO/RTO medido, evidência manual, observação humana,
  participante, métrica ou resultado. Fato indisponível permanece `unknown` ou
  pendente.
- Preferir paths e APIs portáveis e evitar solução obviamente incompatível com
  Windows, sem implementar o escopo operacional de S7.

## Verification

- Cobrir por testes automatizados: criação e validação do backup; snapshot sob
  escrita concorrente; conteúdo esperado; manifesto/checksum; corrupção e
  versão incompatível; falha antes da publicação; ausência de origem; permissão
  e bloqueio quando reproduzíveis; overwrite; cleanup; idempotência e logs
  sanitizados/correlacionados.
- Cobrir restore isolado, abertura SQLite e da aplicação, compatibilidade de
  migrations, `integrity_check`, `foreign_key_check`, reconciliação dos fatos
  V0.4, preservação do banco principal/backup original e destino preexistente
  byte a byte inalterado.
- Cobrir a integração com S5 em restore saudável, finding impeditivo e falha
  operacional, validando status/exit code sem duplicar toda a suíte S5.
- Executar ensaio manual controlado em banco descartável, registrar comandos,
  ambiente, tamanho e duração somente quando observados, checks físicos,
  checker, reconciliação, resultado e limitações. Dependência humana ou externa
  não executada permanece pendente.
- Executar review A8 profundo procurando especialmente falso senso de backup
  válido, snapshot inconsistente, restore destrutivo, falta de proteção
  pré-restore em fluxo existente, validação superficial, checker ignorado,
  finding mascarado, original alterado, path inseguro, logging sensível, erro
  oculto, cleanup/rollback incompleto e expansão para S7-S9. A conclusão exige
  `APPROVED`, sem Blocker ou Major aberto.
- Executar `git diff --check` e o gate autoritativo:
  `powershell -NoProfile -ExecutionPolicy Bypass -File
  .\scripts\quality.ps1`, ambos aprovados com exit code observado.

## Documentation Impact

Criar ou atualizar documentação operacional concisa de backup, validação,
restore e recuperação, incluindo salvaguardas, checker S5, reconciliação,
failure modes, RPO/RTO aplicáveis e handoffs futuros para S7-S9. Na conclusão
real, encerrar o plano A4, arquivar S6, atualizar `PROJECT_STATE.md` e registrar
métricas A7 com proveniência, sem alterar a Architecture v1.0 nem autorizar a
etapa seguinte.

## Done When

- O plano A4 foi criado antes da implementação, seguido e encerrado com os nove
  tópicos mínimos exigidos.
- O mecanismo existente foi auditado e cada componente foi classificado como
  adequado, parcial, ausente ou inseguro; somente lacunas comprovadas foram
  alteradas.
- O backup publicado é um snapshot SQLite consistente, validado, identificável
  e protegido contra overwrite, inclusive com banco em uso.
- O restore isolado abre com SQLite e com a aplicação aplicável, passa pelos
  checks físicos, executa o checker S5 com sucesso e reconcilia os fatos V0.4
  esperados sem rejeitar resíduo legítimo de S1.
- Findings S5, falha operacional, corrupção, incompatibilidade e demais falhas
  principais são impeditivos, recuperáveis e não alteram o banco principal nem
  o backup original.
- Logging/correlação, sanitização, mensagens, cleanup, proteção de paths e
  comportamento de reexecução estão adequados e cobertos por testes.
- A documentação operacional e a evidência real do ensaio cobrem criação,
  validação, restore, salvaguardas, reconciliação, checker, falhas, RPO/RTO e
  handoffs de S7-S9 sem alegações não observadas.
- Não houve migration, mudança de schema, alteração indevida de S1-S5, restore
  destrutivo, implementação de S7-S9 ou uso de dados pessoais reais.
- Testes focados estão GREEN; review A8 profundo está `APPROVED`, sem Blocker ou
  Major; `git diff --check` passa; gate autoritativo está GREEN com exit code
  `0`; nenhum P0/P1 aplicável permanece aberto.
- S6 está arquivada, plano/estado/métricas refletem somente evidência real,
  `tasks/current.md` retornou a `NO_TASK_AUTHORIZED` e S7 permanece não
  autorizada.

## Closure Evidence

- Encerrada em 2026-09-16 após plano A4 `COMPLETED`.
- Testes focados/relacionados: 65 passed, exit 0.
- Ensaio sintético: PASS; backup/restore de 655.360 bytes, checks SQLite,
  aplicação aberta, S5 exit 0, reconciliação e arquivos protegidos inalterados.
- Review A8 profundo: `APPROVED`, sem Blocker/Major aberto.
- `git diff --check`: exit 0.
- Gate autoritativo: GREEN, exit 0; 322 passed em 74,56 s; cobertura 88%;
  duração total 105,8 s.
- Sem P0/P1 aplicável, migration/schema, restore destrutivo, S7-S9 ou Git.
- Evidência: `quality/v04-s6-recovery-result.md` e
  `quality/v04-s6-recovery-drill.json`.
