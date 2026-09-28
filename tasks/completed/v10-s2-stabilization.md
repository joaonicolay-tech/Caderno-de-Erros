# Task Contract

Status: AUTHORIZED

## Identification

- Task ID: `V1.0-S2`
- Product version: `V1.0`
- Stage: `S2 — Estabilização e identidade do candidato`
- Task type: `stabilization / release candidate / identity`
- Size: `M`
- Risk: `high`
- Migration: `NO` prevista

## Goal

Estabilizar o candidato V1 sobre os contratos congelados pela S1, corrigindo
somente findings reais e reproduzíveis dentro do escopo e reconciliando a
identidade/versionamento do produto, sem introduzir funcionalidade nova.

## Context

- V1.0-P0 está `COMPLETED / APPROVED`; o plano em
  `tasks/plans/v10-release-execution-plan.md` é a autoridade de planejamento.
- V1.0-S1 está concluída com decisão `CONTRACTS_FROZEN_FOR_V1`, registrada em
  `docs/V1.0_S1_Contratos_e_Compatibilidade.md` e
  `quality/v10-s1-contracts-compatibility-result.md`.
- A S1 congelou `REV-FIXA-1.0`, `DOM-HEUR-1.0`, `PRI-HEUR-1.0`,
  `CEI-EXPORT-1.0`, V10-D1 e V10-D2. Não reabrir esses contratos sem finding
  concreto que torne a execução S2 impossível; diante de conflito material,
  parar e registrar `HUMAN_DECISION_REQUIRED`.
- Gap de identidade conhecido: produto `V1.0`, pacote `1.0.0`, formato CEI
  `1.0`; `pyproject.toml` e o log de inicialização ainda declaram `0.1.0`.
- Aplicar `docs/A3_Progressive_Disclosure.md`; começar por código, testes e
  documentação diretamente relacionados e ampliar a leitura apenas quando
  tarefa, risco ou evidência exigirem.

## Acceptance Criteria

- Findings beta ainda aplicáveis e novos findings reproduzíveis do recorte S2
  foram triados por severidade, distinguindo achados resolvidos, observações
  sem evidência, dívida não bloqueante e itens Pós-V1.
- Não há Blocker ou Major aplicável em aberto no fechamento; defeitos
  funcionais corrigidos têm reprodução/evidência e teste focado quando
  tecnicamente possível, com falha inicial e reteste preservados.
- Correções limitam-se a defeitos reproduzíveis ou mudanças necessárias à
  estabilização; nenhuma funcionalidade nova foi introduzida.
- A identidade do candidato é coerente e diferencia produto `V1.0`, pacote/
  release `1.0.0`, schema e CEI `format_version = 1.0`; as superfícies
  pertinentes seguem a decisão da S1, sem versionamento redundante.
- Compatibilidade e validação permanecem preservadas, inclusive o pacote V0.5
  compatível; nenhum ajuste silencioso, merge ou relaxamento de validação.
- Nenhuma migration foi criada. Se uma correção exigir schema, a execução para
  antes da migration e registra finding, justificativa, impacto, compatibilidade
  e necessidade de A4/decisão correspondente.
- Testes focados passam, gate autoritativo termina GREEN com exit code 0, A8 é
  aprovado e evidência S2 registra findings, mudanças e resultados observados.
- Documentação diretamente afetada e `PROJECT_STATE.md` ficam coerentes; o
  contrato é arquivado ao concluir e o próximo estado não autoriza S3+.
- O candidato fica identificável para a validação de S3, sem tag ou release.

## Expected Scope

- Revisar findings beta e investigar findings novos reproduzíveis diretamente
  relacionados à estabilização S2; reproduzir antes de corrigir quando possível.
- Corrigir minimamente problemas observáveis em fluxos, mensagens de erro e
  recuperação; tratar flag/configuração temporária somente se comprovadamente
  existente e pertencente ao candidato.
- Auditar e harmonizar, quando tecnicamente apropriado, identidade/versionamento
  em metadados do pacote, log de inicialização, UI, metadados do produto,
  manifesto/export no limite da S1 e documentação diretamente relacionada.
- Atualizar testes afetados e adicionar regressões para defeitos reais; registrar
  findings e evidências originais e de reteste.
- Atualizar evidência S2 em `quality/`, `PROJECT_STATE.md` e arquivar este
  contrato ao satisfazer os critérios de conclusão.

## Protected Scope

- Contratos congelados `REV-FIXA-1.0`, `DOM-HEUR-1.0`, `PRI-HEUR-1.0`,
  `CEI-EXPORT-1.0`, V10-D1 e V10-D2, salvo finding concreto que impeça S2 e
  nova decisão explícita.
- Schema, migrations, dados e fatos históricos; CEI fora do ajuste mínimo de
  identidade do produtor previsto pela S1.
- Features novas, redesign, identidade visual nova, design system, FTS, tuning
  especulativo e mudanças nas fórmulas de Domain/Priority ou regra REV-FIXA.
- Prova completa de importação CEI V0.5→V1 e cadeia de upgrade/recovery de S6;
  regressão de banco/segurança de S3; auditoria final de browsers de S4;
  BCR-1/BCR-2 de S5; piloto real de S8; promoção de S9; publicação de S10.
- Os `ResourceWarning` históricos ficam para investigação futura de regressão/
  banco em S3, salvo se bloquearem diretamente uma mudança necessária S2.
- Commit, push, tag e release não estão autorizados por esta tarefa.

## Constraints

- Identidade conforme S1: produto visível `V1.0`; versão SemVer do pacote e
  artefato `1.0.0`; `format_version` CEI permanece `1.0`. Não confundir com
  versão de schema nem criar fonte redundante de versionamento.
- Preservar CEI-EXPORT-1.0 e V10-D1: `application_version` identifica o
  produtor; exports V0.5 preservam `V0.5`, exports V1 usam `V1.0`; sem
  conversão silenciosa, merge, adaptação de schema ou relaxamento da validação.
  A prova completa V0.5→V1 pertence à S6.
- Preservar a matriz V10-D2 e as demais decisões congeladas da S1.
- Migration `NO` prevista. Se surgir necessidade de schema, parar antes de
  criar migration e registrar a decisão necessária.
- Não reabrir achado histórico sem evidência de aplicabilidade/regressão; não
  corrigir observação ou dívida não bloqueante por impulso.
- A7 inicial: `GPT-6 Luna xHigh` para análise, triagem, documentação e correções
  pequenas/localizadas. Escalar para `GPT-6 Sol Medium` somente se surgir
  alteração funcional material, reconstrução de estado, raciocínio transacional
  complexo, correção cross-module relevante, risco real de integridade ou
  comportamento não local difícil de provar; não escalar preventivamente.
- A8: `standard` por padrão; `deep` somente se houver alteração funcional
  material que justifique profundidade adicional. Registrar a decisão real no
  fechamento.
- Preservar backups/exportações e caminho de recuperação anterior; nunca
  inferir segurança de operação destrutiva sem evidência direta.

## Verification

- Reproduzir e registrar evidência para defeitos funcionais quando possível;
  executar testes focados correspondentes e preservar falha inicial/reteste.
- Verificar identidade/versionamento nas superfícies realmente aplicáveis e
  compatibilidade sem enfraquecer validação.
- Executar verificações específicas da etapa e A8; ao fechar, executar o gate
  autoritativo: `powershell -NoProfile -ExecutionPolicy Bypass -File
  .\scripts\quality.ps1`, exigindo exit code 0.
- Registrar em `quality/` o resultado observado, findings, A8 e ressalvas; não
  declarar PASS por expectativa.

## Documentation Impact

Atualizar somente documentação diretamente afetada por comportamento ou
identidade/versionamento; registrar evidência S2 em `quality/` e atualizar
`PROJECT_STATE.md` e arquivar este contrato ao concluir. Preservar a cronologia
e os registros históricos da S1.

## Done When

- Findings aplicáveis foram triados e nenhum Blocker/Major aplicável permanece
  aberto; toda correção está ligada a defeito reproduzível ou necessidade
  demonstrada da estabilização.
- Identidade do candidato está coerente, compatibilidade preservada, nenhuma
  feature nova ou migration foi introduzida e testes focados passam.
- Gate autoritativo GREEN (exit code 0), A8 aprovado e evidência S2 registrada.
- Documentação e `PROJECT_STATE.md` atualizados, tarefa arquivada e próximo
  estado registrado sem autorizar S3 ou etapa posterior.
- Nenhuma tag ou release V1 foi criada; nenhuma publicação ocorreu.

## Closure Record

- Estado: `COMPLETED`; decisão: `S2_COMPLETED` — `V1 candidate stabilized for S3`.
- Evidência: `quality/v10-s2-stabilization-result.md`.
- Gate final após atualização do estado, arquivamento e retorno do contrato
  corrente: GREEN, exit code 0, 510 testes, 86% de cobertura, 316.3 s (suíte
  em 256.86 s); 2 ResourceWarning SQLite históricos registrados.
- A8: `deep`, `APPROVED`; Blocker 0, Major 0, Minor novo 0. O Minor histórico
  S9 de evidência manual de acessibilidade permanece para validação V1.
- Sem migration, nova dependência ou funcionalidade nova; lock sincronizado
  apenas para a versão local do projeto `1.0.0`.
- `PROJECT_STATE.md` atualizado; próximo estágio possível S3 sob contrato
  independente. `tasks/current.md` retornou a `NO_TASK_AUTHORIZED`.
- S3+ não autorizado. Nenhuma etapa posterior foi iniciada.
- Sem commit, push, tag, release ou publicação.
