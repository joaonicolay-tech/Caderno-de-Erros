# CURRENT TASK

ID: V1.0-S4
Version: V1.0
Stage: S4
Status: AUTHORIZED
Type: acessibilidade / navegadores / usabilidade
Size: M
Risk: medium
Migration: NO prevista

## Goal

Auditar as jornadas centrais reais do candidato V1 em navegadores suportados,
acessibilidade, teclado, foco, contraste, zoom, responsividade, estados vazios,
erros e recuperação, corrigindo somente findings reproduzíveis do fluxo
existente.

Não criar novo fluxo de produto, redesign ou design system.

## Context

V1.0-S1 foi concluída com:

`CONTRACTS_FROZEN_FOR_V1`

V1.0-S2 foi concluída com:

`S2_COMPLETED`

V1.0-S3 foi concluída e checkpointada com:

- regressão crítica aprovada;
- banco/integridade aprovados;
- segurança e privacidade aprovadas no recorte S3;
- gate final GREEN;
- working tree limpa após checkpoint.

S5+ não estão autorizadas.

## Authoritative Sources

- `AGENTS.md`
- `PROJECT_STATE.md`
- `tasks/plans/v10-release-execution-plan.md`
- `quality/v10-s3-regression-security-result.md`
- `quality/v10-s2-stabilization-result.md`
- `docs/V1.0_S1_Contratos_e_Compatibilidade.md`
- documentação de acessibilidade/usabilidade aplicável
- critérios de aceite/Etapa 10 aplicáveis
- ADRs aplicáveis
- templates/views/forms/CSS/testes diretamente relacionados
- `scripts/quality.ps1`

Aplicar progressive disclosure.

## Browser Matrix

A matriz V1 aprovada é:

- Chrome current stable — Windows 11
- Edge current stable — Windows 11
- Firefox current — Windows 11
- Firefox immediately previous — Windows 11
- Brave current stable — Windows 11, configuração padrão, sem extensões
- Safari: N/A / não tecnicamente aplicável ao escopo oficial Windows 11

Não expandir suporte para macOS.

Responsividade requerida:

`360–1920 px`

## Allowed Scope

S4 está autorizada a:

- mapear jornadas centrais reais;
- validar navegação por teclado;
- validar ordem de tabulação;
- validar foco visível;
- validar foco após ações/erros quando aplicável;
- validar labels;
- validar associação label/campo;
- validar nomes acessíveis;
- validar mensagens de erro;
- validar estados vazios;
- validar confirmação de ações;
- validar recuperação de erro;
- validar contraste;
- validar zoom 200%;
- validar responsividade entre 360 e 1920 px;
- validar ausência de dependência horizontal indevida;
- validar semântica HTML aplicável;
- validar leitor de tela quando tecnicamente aplicável e disponível;
- validar jornadas centrais nos browsers suportados;
- identificar diferenças entre browsers;
- corrigir findings reproduzíveis do fluxo existente;
- adicionar testes somente para defeitos reais ou lacunas críticas;
- produzir evidência S4;
- executar A8 standard;
- executar quality gate;
- atualizar `PROJECT_STATE.md`;
- arquivar o contrato ao concluir.

## Core Journeys

Identificar as jornadas centrais reais a partir da documentação e aplicação.

Priorizar, conforme existirem no produto:

- inicialização;
- dashboard;
- navegação principal;
- cadastro/edição de erro;
- tentativa/correção;
- revisão;
- taxonomia;
- pesquisa/consulta;
- export;
- import;
- backup/restore somente na superfície de UI necessária;
- mensagens de erro;
- confirmações;
- estados vazios;
- operações destrutivas existentes.

Não inventar jornada inexistente.

## Accessibility

Validar, conforme aplicável:

- teclado sem mouse;
- Tab / Shift+Tab;
- Enter / Space;
- foco visível;
- foco lógico após navegação;
- labels;
- headings;
- landmarks;
- nomes acessíveis;
- botões e links;
- formulários;
- erros de validação;
- required fields;
- contraste;
- zoom 200%;
- conteúdo reflow;
- ausência de informação transmitida somente por cor;
- estados de erro;
- estados vazios;
- confirmação;
- semântica nativa.

Não criar ARIA desnecessária quando elemento HTML nativo resolver.

## Screen Reader

Quando tecnicamente aplicável e disponível:

- realizar smoke das jornadas principais com leitor de tela suportado no
  ambiente;
- verificar nomes acessíveis;
- headings;
- labels;
- feedback de erro;
- controles interativos.

Se não houver leitor de tela disponível no ambiente automatizado:

- não inventar aprovação;
- registrar a limitação;
- usar evidência automatizada/semântica disponível;
- registrar necessidade de validação manual quando aplicável.

## Contrast

Validar combinações reais usadas pelo produto.

Não alterar identidade visual por preferência.

Corrigir apenas combinação que realmente viole o requisito aplicável.

Preservar evidência da combinação antes/depois quando houver correção.

## Zoom / Responsive

Validar:

- zoom 200%;
- viewport mínimo de 360 px;
- pontos intermediários quando úteis;
- viewport até 1920 px;
- ausência de perda de conteúdo;
- ausência de clipping funcional;
- ausência de scroll horizontal obrigatório indevido;
- controles utilizáveis;
- tabelas/componentes existentes conforme desenho aprovado.

Não transformar S4 em redesign mobile.

V1 continua sendo produto oficial para Windows 11.

## Browser Validation

Executar a matriz suportada conforme ambiente disponível.

Para cada browser registrar:

- browser;
- versão;
- ambiente;
- jornadas executadas;
- resultado;
- finding, se houver.

Não declarar browser validado sem execução real.

Se algum browser da matriz não estiver disponível:

registrar claramente:

`NOT_EXECUTED`

com motivo.

Não substituir execução real por suposição.

## Brave

Brave current stable:

- configuração padrão;
- sem extensões;
- smoke das jornadas centrais;
- diferenças reais devem ser registradas.

Não exigir versão anterior do Brave.

## Firefox

Validar:

- current;
- immediately previous;

quando ambos estiverem tecnicamente disponíveis.

Se somente uma versão estiver disponível:

não inventar a segunda.

Registrar limitação factual.

## Safari

Safari permanece:

`N/A`

porque a plataforma oficial V1 é Windows 11.

Não expandir para macOS.

## Findings Policy

Classificar findings como:

- Blocker;
- Major;
- Minor;
- observation;
- environment limitation;
- browser-specific finding;
- accessibility finding;
- usability finding.

Para finding reproduzível, quando possível:

1. preservar estado inicial;
2. reproduzir;
3. registrar browser/viewport/ação;
4. identificar causa;
5. aplicar menor correção necessária;
6. testar novamente;
7. executar regressão afetada;
8. registrar evidência.

Não corrigir observação estética sem requisito.

## Model / A7

Modelo inicial:

`GPT-6 Luna High`

Luna High pode executar:

- auditoria;
- análise de HTML/CSS/forms;
- testes;
- pequenas correções;
- comparação de browsers;
- documentação;
- evidências.

Escalar para:

`GPT-6 Luna xHigh`

se houver:

- ambiguidade relevante de acessibilidade;
- diferença real entre browsers difícil de explicar;
- comportamento visual não trivial;
- problema de foco complexo;
- usabilidade com múltiplas interpretações;
- exceção difícil de classificar;
- correção com impacto visual/comportamental mais amplo.

Nesses casos:

PARAR antes da correção material e reportar:

`MODEL_ESCALATION_RECOMMENDED: GPT-6 Luna xHigh`

com:

- finding;
- reprodução;
- browser/viewport;
- impacto;
- arquivos afetados;
- motivo do escalonamento.

## A8

A8 prevista:

`standard`

A8 deve revisar:

- escopo;
- jornadas;
- browsers;
- teclado;
- foco;
- labels;
- semântica;
- contraste;
- zoom;
- responsividade;
- findings;
- testes;
- evidências;
- ausência de redesign;
- ausência de feature nova;
- ausência de migration.

Se surgir alteração material ou ambiguidade que justifique revisão maior:

seguir a regra de escalonamento antes de ampliar a profundidade.

## Protected Scope

Preservar:

- `REV-FIXA-1.0`
- `DOM-HEUR-1.0`
- `PRI-HEUR-1.0`
- `CEI-EXPORT-1.0`
- V10-D1
- V10-D2
- schema atual
- identidade V1
- resultados concluídos de S1–S3

## Forbidden Scope

NÃO:

- redesign;
- criar design system;
- refazer identidade visual;
- criar fluxo novo;
- criar feature nova;
- alterar regra de negócio;
- alterar heurísticas;
- alterar CEI;
- criar migration;
- tuning de performance;
- executar BCR-1/BCR-2;
- executar cadeia completa de upgrade/recovery;
- executar prova CEI V0.5→V1;
- executar piloto;
- promover V1;
- criar tag/release;
- iniciar S5+.

## Migration Policy

Migration:

`NO`

Se qualquer correção exigir mudança de schema:

PARAR.

Não criar migration.

Registrar finding e solicitar nova decisão.

## Testing

Usar testes existentes quando suficientes.

Adicionar/alterar teste apenas quando:

- existe finding reproduzível;
- existe lacuna crítica de regressão;
- a correção precisa de proteção.

Não criar testes apenas para aumentar contagem.

Executar testes focados após correções.

## Quality Gate

Antes de encerrar:

executar:

`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1`

Gate final deve ser:

`GREEN`

com exit code 0.

Preservar qualquer tentativa RED e respectivos retestes.

## Evidence

Criar artefato consistente, preferencialmente:

`quality/v10-s4-accessibility-browser-usability-result.md`

Registrar:

- baseline;
- fontes lidas;
- jornadas;
- matriz de browsers;
- versões observadas;
- teclado;
- foco;
- labels;
- semântica;
- contraste;
- zoom;
- responsividade;
- screen reader;
- estados vazios;
- erros/recuperação;
- findings;
- correções;
- testes;
- limitações ambientais;
- gate;
- A8;
- resultado final.

Não inventar execução manual não realizada.

## Acceptance Criteria

S4 só pode concluir quando:

- jornadas centrais aplicáveis foram auditadas;
- teclado aprovado no recorte;
- foco aprovado no recorte;
- labels/semântica aprovados;
- contraste aplicável aprovado;
- zoom 200% aprovado ou exceção documentada;
- 360–1920 px aprovado no recorte;
- browsers executáveis da matriz foram avaliados;
- limitações reais foram registradas;
- nenhum Blocker aberto;
- nenhum Major aberto;
- testes focados verdes;
- gate final GREEN;
- A8 standard APPROVED;
- nenhuma migration;
- nenhuma feature nova;
- nenhum redesign;
- candidato apto a seguir para S5/S6.

## Stop Conditions

PARAR se surgir:

- necessidade de migration;
- necessidade de redesign material;
- necessidade de novo fluxo;
- mudança de contrato congelado;
- ambiguidade relevante que exige Luna xHigh;
- incompatibilidade grave entre browsers;
- finding que exija mudança arquitetural;
- drift inesperado;
- gate obrigatório RED não resolvido.

## Project State

No fechamento, se S4 concluir:

atualizar `PROJECT_STATE.md` com fatos observados.

Registrar:

- S1 concluída;
- S2 concluída;
- S3 concluída;
- S4 concluída;
- S5+ não autorizadas.

Não iniciar próxima etapa.

## Closure

Somente se os critérios forem satisfeitos:

- criar evidência;
- atualizar estado;
- arquivar contrato;
- retornar `tasks/current.md` para:

`NO_TASK_AUTHORIZED`

Não criar contrato S5 ou S6.

## Git

NÃO executar:

- git add;
- commit;
- push;
- tag;
- release.

Checkpoint Git será separado.

## Expected Result

`S4_COMPLETED`

ou:

`MODEL_ESCALATION_RECOMMENDED`

ou:

`HUMAN_DECISION_REQUIRED`

ou:

`BLOCKED`.


## Human Decision Addendum — Browser Support V1

Explicit human decision made during V1.0-S4:

The browser requirement of V10-D2 is amended for V1.

New rule:

- V1 release validation requires one complete supported-browser validation on
  Windows 11 using:
  - Brave current stable; OR
  - Google Chrome current stable.
- A complete PASS in either one is sufficient for the V1 browser release gate.
- The browser that actually passes the complete matrix becomes the browser
  officially validated for V1.
- Do not claim official validation/support for a browser that was not actually
  executed and passed.
- Edge and Firefox are no longer blocking requirements for V1 promotion.
- Edge and Firefox become optional / best-effort compatibility targets.
- Safari remains N/A because the official platform remains Windows 11 x64.
- Responsive requirement 360–1920 px remains unchanged.
- Accessibility, keyboard, focus, zoom 200%, usability and central-flow
  requirements remain unchanged for the browser used to satisfy the release
  gate.

This human decision explicitly authorizes the S4 execution to:

- record a traceable amendment to V10-D2 without rewriting historical S1/P0
  evidence;
- update current V1 documentation/state to reflect the amended browser policy;
- use the manual Brave validation performed by the project owner as human
  evidence, clearly identified as manual/user-provided evidence;
- close S4 if all remaining acceptance criteria are satisfied;
- record future automated coverage for special states and responsiveness as a
  deferred follow-up only.

This authorization does NOT permit:

- rewriting historical evidence;
- claiming Chrome, Edge or Firefox were tested when they were not;
- implementing the future automated tests now;
- starting S5 or S6;
- redesign;
- feature changes;
- migration creation;
- commit/push/tag/release.

## Manual Human Evidence Available

The project owner manually validated the current stable Brave on Windows 11
after bringing the development database to the existing current migrations.

Reported result:

- application opens correctly;
- dashboard works;
- central navigation works;
- keyboard navigation works;
- focus is visible and usable;
- forms and labels work;
- validation errors are understandable;
- zoom 200% works;
- responsive checks performed successfully;
- central states checked showed no observed problem;
- Windows Narrator smoke showed no observed problem;
- no functional, visual, keyboard or accessibility issue was reported.

Treat this as HUMAN/MANUAL evidence.

Do not present it as independently executed by Codex.

## Deferred Follow-up Requested by Project Owner

Record, but DO NOT implement now, future automated regression coverage for:

1. special UI states:
   - empty states;
   - validation errors;
   - success/error messages;
   - confirmation;
   - cancellation;
   - recovery paths;

2. responsiveness:
   - 360 px;
   - 768 px;
   - representative desktop viewport;
   - 1920 px;
   - overflow;
   - clipping;
   - overlap;
   - inaccessible controls;
   - unintended whole-page horizontal dependency.

This follow-up is not authorized for implementation during S4.
## Closure Record

- State: COMPLETED; result: S4_COMPLETED.
- Evidence: quality/v10-s4-accessibility-browser-usability-result.md.
- Human evidence: Brave 1.96.59 official, Windows 11 x64, all extensions disabled;
  final smoke PASS for Dashboard/Início, cadastro de erro/questão, tentativa,
  revisão, lista/consulta and dados, with no problems found. Earlier ten-journey,
  accessibility and responsive HME remains preserved with its session context.
- Official V1 browser validated: Brave 1.96.59 (manual human evidence).
  Chrome is not validated; Edge/Firefox remain NOT_EXECUTED / OPTIONAL;
  Safari is N/A.
- A8 standard: APPROVED; Blocker 0, Major 0, Minor 0.
- Final quality gate: GREEN, exit code 0; 510 passed in 227.29 s, 86% global
  coverage, domain coverage passed, total gate duration 285.8 s; no unexpected
  migrations and no known dependency vulnerabilities.
- No new migration, functional change, new feature, redesign or future test.
  The requested automated special-state and responsive coverage remains
  DEFERRED FOLLOW-UP.
- S5/S6 remain NOT AUTHORIZED; none was started.
- No commit, push, tag or release.