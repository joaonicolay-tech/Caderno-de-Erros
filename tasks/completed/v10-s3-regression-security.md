# CURRENT TASK

ID: V1.0-S3
Version: V1.0
Stage: S3
Status: AUTHORIZED
Type: regressão / banco / segurança / privacidade
Size: M
Risk: high
Migration: NO prevista

## Goal

Provar que o candidato V1 estabilizado pela S2 preserva regressão crítica,
integridade de banco, isolamento, segurança e privacidade antes de avançar
para S4, S5 e S6.

## Context

S1 foi concluída com:

`CONTRACTS_FROZEN_FOR_V1`

S2 foi concluída com:

`S2_COMPLETED`

Checkpoint Git atual corresponde ao commit iniciado por:

`b0db746`

O candidato V1 está identificado como:

- produto: `V1.0`
- pacote/release: `1.0.0`
- CEI format: `1.0`
- produtores CEI permitidos: `V0.5` e `V1.0`

S4+ não estão autorizadas.

## Authoritative Sources

- `AGENTS.md`
- `PROJECT_STATE.md`
- `tasks/plans/v10-release-execution-plan.md`
- `quality/v10-s2-stabilization-result.md`
- `docs/V1.0_S1_Contratos_e_Compatibilidade.md`
- `quality/v10-s1-contracts-compatibility-result.md`
- Etapa 10 / Plano de Testes aplicável
- RNFs de banco, segurança e privacidade aplicáveis
- ADRs aplicáveis
- código e testes diretamente relacionados
- `scripts/quality.ps1`

Aplicar progressive disclosure.

## Allowed Scope

A S3 está autorizada a:

- mapear CTs aplicáveis aos testes existentes;
- preencher somente lacunas críticas reais;
- executar regressão do recorte S3;
- validar SQLite;
- validar constraints;
- validar migrations existentes;
- confirmar ausência de migration pendente;
- validar invariant checker;
- validar atomicidade e idempotência aplicáveis;
- validar isolamento de Workspace;
- validar CSRF e controles de segurança aplicáveis;
- validar arquivos/ZIP/import no recorte de segurança;
- validar logs e sanitização;
- validar privacidade;
- validar dependências;
- executar matriz PostgreSQL crítica quando realmente aplicável;
- investigar findings reais;
- investigar os `ResourceWarning` SQLite recorrentes;
- corrigir findings pequenos/localizados dentro do escopo;
- adicionar ou alterar testes quando necessário para provar/corrigir finding;
- produzir evidência S3;
- atualizar `PROJECT_STATE.md`;
- arquivar o contrato ao concluir;
- executar A8 deep;
- executar o quality gate autoritativo.

## CT Ownership

S3 possui principalmente:

- `CT-073–083`
- `CT-099–104`
- `CT-121`
- `CT-123`
- `CT-129–136`, somente quando realmente existentes/aplicáveis conforme a
  fonte autoritativa
- outros CTs diretamente necessários ao recorte de regressão, banco,
  segurança ou privacidade.

S3 NÃO assume a prova completa de:

- `CT-113–120`
- `CT-122`

Esses permanecem principalmente sob S6 para:

- backup;
- restore;
- recovery;
- CEI integrado;
- upgrade entre versões.

## SQLite ResourceWarnings

Existem dois `ResourceWarning` recorrentes relacionados a conexões SQLite não
fechadas observados em gates anteriores.

S3 deve:

- reproduzir quando possível;
- identificar a origem;
- distinguir defeito de produto, defeito de teste, cleanup incompleto ou
  warning ambiental;
- verificar risco de lock, leak, comportamento não determinístico ou
  interferência entre testes;
- corrigir minimamente se houver causa reproduzível dentro do escopo.

Não presumir automaticamente que warning equivale a defeito de produto.

Preservar evidência.

## Database / Integrity

Validar conforme aplicável:

- SQLite;
- foreign keys;
- constraints;
- migrations existentes;
- migration drift;
- invariant checker;
- atomicidade;
- idempotência;
- concorrência relevante;
- Workspace isolation;
- consistência entre fatos e derivados;
- transações;
- rejeição segura de dados inválidos.

Usar somente bases/fixtures descartáveis.

Não usar dados pessoais reais.

## PostgreSQL

Não expandir suporte PostgreSQL.

Executar somente a matriz crítica já aprovada quando aplicável.

Não adicionar:

- operação remota;
- hosting;
- multiusuário;
- cobertura PostgreSQL total sem requisito.

## Security

Validar quando aplicável:

- autorização por Workspace/objeto;
- CSRF;
- validação de input;
- validação de arquivos;
- segurança de ZIP/path;
- import seguro;
- exposição de segredos;
- logs;
- dados privados;
- dependências;
- sessão;
- mensagens/erros que possam revelar informação indevida.

## Privacy

Validar:

- isolamento entre Workspaces;
- ausência de dados pessoais indevidos em logs;
- ausência de segredos/tokens em evidências;
- sanitização;
- operação local/loopback;
- ausência de exposição pública;
- uso de dados descartáveis nos testes.

## Protected Scope

Preservar:

- `REV-FIXA-1.0`
- `DOM-HEUR-1.0`
- `PRI-HEUR-1.0`
- `CEI-EXPORT-1.0`
- V10-D1
- V10-D2
- schema atual, salvo nova decisão explícita
- histórico V0.5
- decisões concluídas da S1 e S2

## Forbidden Scope

NÃO:

- criar feature nova;
- criar migration sem nova autorização;
- redesign;
- alterar fórmula Domain;
- alterar fórmula Priority;
- alterar regra REV-FIXA;
- criar CEI 1.1;
- alterar formato CEI;
- executar cadeia completa V0.4.4 → V0.5 → V1;
- executar prova completa CEI V0.5 → V1;
- executar auditoria final de browsers;
- executar auditoria final de acessibilidade/usabilidade;
- executar BCR-1/BCR-2;
- realizar tuning especulativo;
- executar piloto;
- promover V1;
- criar tag/release;
- iniciar S4+.

## Migration Policy

Migration prevista:

`NO`

Se qualquer finding exigir mudança de schema:

PARAR antes de criar migration.

Registrar:

- finding;
- causa;
- schema afetado;
- impacto;
- risco;
- compatibilidade;
- proposta.

Aguardar nova decisão.

## Findings Policy

Distinguir:

- finding reproduzível;
- regressão real;
- warning sem impacto comprovado;
- falha ambiental;
- vulnerabilidade;
- finding de privacidade;
- finding de integridade;
- dívida não bloqueante.

Quando tecnicamente possível:

1. preservar primeira falha;
2. reproduzir;
3. identificar CT/teste;
4. aplicar correção mínima;
5. retestar;
6. executar regressão afetada;
7. registrar evidência.

## Model / A7

Modelo inicial:

`GPT-6 Luna xHigh`

Escalar para:

`GPT-6 Sol Medium`

se surgir:

- vulnerabilidade real exigindo correção material;
- finding material de privacidade;
- finding material de integridade;
- mudança relevante de código de segurança;
- comportamento transacional complexo;
- correção cross-module significativa;
- reconstrução de estado difícil de provar.

Nesses casos, parar antes da mudança material e reportar:

`MODEL_ESCALATION_RECOMMENDED: GPT-6 Sol Medium`

## A8

Obrigatório:

`deep`

A8 deve revisar:

- regressão;
- banco;
- integridade;
- segurança;
- privacidade;
- findings;
- testes;
- migrations;
- dependências;
- ResourceWarnings;
- escopo;
- evidências.

## Acceptance Criteria

S3 poderá ser concluída somente quando:

- CTs do recorte S3 estiverem mapeados;
- P0/P1 aplicáveis do recorte estiverem aprovados;
- Blocker = 0;
- Major = 0;
- regressão crítica estiver verde;
- constraints/integridade estiverem aprovadas;
- isolamento estiver aprovado;
- segurança aplicável estiver aprovada;
- privacidade aplicável estiver aprovada;
- logs e dependências estiverem aprovados;
- ResourceWarnings tiverem sido investigados;
- coverage mínima aplicável estiver preservada;
- quality gate estiver GREEN;
- A8 deep estiver APPROVED;
- nenhuma migration não autorizada existir;
- nenhuma feature nova existir;
- candidato estiver apto para S4/S5/S6.

## Stop Conditions

PARAR se houver:

- corrupção;
- perda de dados;
- cross-Workspace;
- exposição de segredo;
- vulnerabilidade material;
- finding material de privacidade;
- finding material de integridade;
- necessidade de migration;
- necessidade de mudança de contrato congelado;
- necessidade de mudança cross-module complexa;
- working tree inesperadamente alterada;
- gate obrigatório RED não resolvido.

## Git

Durante a execução S3 NÃO:

- commit;
- push;
- tag;
- release.

O checkpoint Git será autorizado separadamente.

## Done When

Se todos os critérios forem satisfeitos:

- criar evidência S3;
- atualizar `PROJECT_STATE.md`;
- arquivar o contrato em `tasks/completed/`;
- retornar `tasks/current.md` para `NO_TASK_AUTHORIZED`;
- não iniciar S4/S5/S6.

Resultado esperado:

`S3_COMPLETED`

## Closure Record

- Estado: `COMPLETED`; decisão: `S3_COMPLETED` — recorte de regressão, banco,
  segurança e privacidade V1 aprovado.
- Evidência: `quality/v10-s3-regression-security-result.md`.
- Gate de implementação GREEN, exit code 0; 510 testes, 86% cobertura global,
  cobertura mínima de domínio aprovada; duração total 282,7 s.
- A8: `deep`, `APPROVED`; Blocker 0, Major 0, Minor novo aberto 0.
- Nenhuma migration, dependência nova, feature, alteração dos contratos S1/S2,
  fórmula ou schema.
- S4/S5/S6 continuam não autorizadas; nenhuma etapa futura iniciada.
- Sem commit, push, tag, release ou publicação.
- Gate final após estado/arquivamento: GREEN, exit code 0; 510 testes em
  218,07 s, cobertura global 86%, cobertura mínima de domínio aprovada; duração
  total 272,3 s. Lock/sync, runtime, rastreabilidade, perfis, migrations,
  formatação, Ruff, mypy, detect-secrets e pip-audit aprovados.
