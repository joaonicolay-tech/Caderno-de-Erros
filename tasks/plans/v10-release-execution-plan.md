# V1.0-P0 — plano executável da V1.0

- Status do plano: `COMPLETED`.
- Decisão do P0: `APPROVED` (aprovação humana final registrada em 2026-09-28).
- Baseline auditada em 2026-09-28: `main`, `HEAD = origin/main =
  c542b4fb6783f5488bece21542199a88303ee013`. No início do planejamento P0, a
  única alteração era a autorização em `tasks/current.md`; no preflight desta
  revisão, os três arquivos deste P0 eram os únicos artefatos modificados.
- Este plano não autoriza S1, implementação, tag ou release. Cada estágio requer
  contrato próprio `AUTHORIZED` em uma execução posterior.
- Objetivo normativo: converter a beta V0.5 em produto individual estável para
  uso pessoal regular; estabilizar, validar, documentar, pilotar e liberar,
  sem acrescentar uma camada funcional (Roadmap §9).

## 1. Autoridade, precedência e limites

Fontes canônicas aprovadas: Visão (Etapa 1), Escopo (Etapa 2), RF (Etapa 3), RNF
(Etapa 4), Regras de Negócio (Etapa 5), SDD (Etapa 6), Modelo de Dados (Etapa 7),
Fluxos (Etapa 8), `docs/Caderno_de_Erros_Inteligente_Etapa_9_Roadmap (1).md`
(Etapa 9, sobretudo §§8–11) e `docs/Caderno_de_Erros_Inteligente_Etapa_10_Plano_de_Testes.md`
(Etapa 10, sobretudo §§3–9). Valem suas erratas controladas e os ADRs aceitos;
para esta auditoria foram aplicáveis ADR-002/003 (Workspace/tempo), ADR-006
(acessibilidade), ADR-007 (backup), ADR-008 (gate), ADR-010/011 (fronteiras
históricas), ADR-012/014 (BCR/CT-125) e a arquitetura operacional aprovada.
`docs/README.md` serviu apenas de índice. O plano V0.5, o contrato S10 arquivado,
`quality/v05-s8-integrity-compatibility-result.md`,
`quality/v05-s9-beta-hardening-result.md` e
`quality/v05-s10-controlled-pilot-result.md` registram entregas/evidências, não
ampliam o Roadmap. O código, migrations e testes atuais confirmam o executável.

O Escopo §11 e outros textos de 2026-08 descrevem capacidades V1 que a V0.5
antecipou validamente pelo Roadmap §8; seu rótulo histórico não cria trabalho
novo. Exemplos: categorias, SavedFilter, lifecycle/correções, Domain, Priority,
export/restore. O Modelo de Dados §16.1 contém uma proposta anterior de ZIP
com `tags.json`; o contrato posterior `docs/CEI_EXPORT_1_0.md`, aprovado na S7,
e `src/modules/data_management/portability.py` definem o formato realmente
entregue. A errata `ERR-V02-001` apenas adiou tags e condicionou seu retorno a
RF/RN/CT próprios; o Roadmap §9.6 veda nova funcionalidade em V1. Portanto,
tags, aviso novo de duplicidade, modos novos de revisão, templates de cadastro
e API não são gaps automáticos. Correção de usabilidade de um fluxo existente
exige finding observável.

Fora da V1: redesign visual completo, identidade visual nova, design system
novo, launcher/executável de um clique, instalador simplificado, IA assistiva,
revisão adaptativa, API pública, integrações, multiusuário, hospedagem pública,
PWA, OCR, anexos, gamificação, FTS e snapshots sem falha medida. Não criar V0.6–V0.9.
Sequência: V0.1 → V0.2 → V0.3 → V0.4 → V0.5 → V1.0 → Pós-V1.

## 2. Baseline real V0.5 e limites da evidência

- `PROJECT_STATE.md`, `README.md` e S10 registram V0.5
  `PROMOTION_APPROVED`, S10 `COMPLETED`, tag beta anotada `v0.5.0` e pre-release
  publicada. O piloto S10 P01–P18 passou após retestes separados de P01/P12/P15,
  mas usou **base sintética integrada**, aprovada por D1 somente para o objetivo
  técnico. Não prova uso pessoal real. O gate S10 final foi GREEN, exit 0,
  505 testes/86%, A8 deep APPROVED, Blocker/Major 0 e P0/P1 aplicável aberto 0.
- Serviços e testes confirmam `REV-FIXA-1.0` (`src/modules/reviews/policies.py`),
  `DOM-HEUR-1.0` (`src/modules/domain/policy.py`), `PRI-HEUR-1.0`
  (`src/modules/priority/policy.py`), lifecycle e correções S2A–S2D/S5,
  SavedFilter, CEI e restore S7, checker read-only de 25 invariantes S8.
  `tests/test_review_completion.py`, `tests/test_domain_policy.py`,
  `tests/test_priority_policy.py`, `tests/test_v05_s7_portability.py`,
  `tests/test_v05_s7_ui.py` e `tests/test_integrity_checker.py` contêm provas
  focadas. S8 comprovou V0.4.4→V0.5 por migrations históricas, backup,
  recovery, CEI round trip e uma matriz crítica PostgreSQL descartável; isto
  não é ainda prova da cadeia até o candidato V1 nem operação PostgreSQL total.
- S9 preservou BCR-1 original com falha de leitura no run 3 e reprodução oficial
  posterior PASS (`TRANSIENT_NOT_REPRODUCED`), sem causa confirmada. Busca simples
  passou e FTS ficou `NOT_JUSTIFIED`. A evidência de zoom/teclado S9 foi relato
  humano `MANUAL_USER_OBSERVED`, sem versão exata do browser/detalhe por página;
  permanece Minor histórico de precisão. V1 requer nova auditoria final direta.
- A UI de dados separa exportação CEI, backup SQLite e restore offline; não
  existe merge de importação. `README.md` e os guias S6/S7/Windows já instruem
  operação beta. `src/modules/data_management/portability.py` emite
  `application_version = V0.5` e exige essa string e `schema_migrations` exatas
  na importação. A decisão V10-D1 mantém `CEI-EXPORT-1.0` e `format_version =
  1.0`, reconhecendo `V0.5` e `V1.0` como produtores somente quando toda a
  validação estrita for satisfeita. `pyproject.toml` e o log de inicialização
  ainda usam `0.1.0`; essa discrepância de identidade é gap de release e sua
  correção deve preservar compatibilidade de pacotes e lock. Nenhuma flag temporária própria foi
  identificada na busca dirigida em `src/`/`scripts/`; confirmar no candidato.
- Auditoria estática dos modelos/migrations não identificou requisito de schema
  novo para estabilizar o conjunto entregue. **Previsão V1: nenhuma migration
  nova**, sujeita a finding concreto e A4 antes de qualquer mudança. V0.5 já
  contém migrations; a cadeia de upgrade e compatibilidade ainda exige prova.

## 3. Matriz de gaps V0.5 → V1.0

Estado usa `DONE_BY_V0.5`, `PARTIALLY_DONE`, `OPEN_FOR_V1` ou
`NOT_APPLICABLE`. `DONE_BY_V0.5` significa capacidade entregue, não dispensa
repetição de uma prova de release.

| Capacidade/obrigação | Fonte normativa | Estado real V0.5 | Gap V1 | Evidência | Ação necessária |
| --- | --- | --- | --- | --- | --- |
| Gestão, lifecycle, correções, filtros | Roadmap §8.2/§9.4; RF-018/020/027/044/046/066/071 | `DONE_BY_V0.5` | Regressão final | S2A–S3/S5; serviços/testes citados; S10 P04–P08/P12 | Reusar, testar casos críticos; corrigir só finding. |
| Domain e Priority explicáveis | Roadmap §8.3/§9.2; RN-068–084; CT-055–072 | `DONE_BY_V0.5` | Congelamento e vetores finais | S4–S6, policies e testes; S10 P11/P12 | Verificar versões, fronteiras, history e ausência de finding; congelar documentalmente. |
| `REV-FIXA-1.0` | Roadmap §9.2; RN-033–051 | `PARTIALLY_DONE` | Congelamento V1 | `reviews/policies.py`; `test_review_completion.py` | Validar calendários, fuso, reset, idempotência e código histórico; registrar congelamento. |
| `CEI-EXPORT-1.0` | Roadmap §9.2; RF-069; RNF-040–043; CT-118–120 | `PARTIALLY_DONE` | Congelamento V1 e prova explícita de compatibilidade V0.5→V1 | S7/S8; contrato CEI; `portability.py:34–35,414–420`; V10-D1 resolvida | Manter `format_version=1.0`; aceitar produtor `V0.5`/`V1.0` apenas sob validação estrita de manifesto, policies, migrations, schema, UUIDs, referências, contagens, checksums, arquivos, destino e invariantes, sempre antes de escrita. Sem conversão, coerção, merge ou adaptação de schema. |
| Backup, restore, recovery | Roadmap §9.4; RNF-034–039; CT-113–117 | `PARTIALLY_DONE` | Exercício final/periódico com dados protegidos | S7/S8/S10; guia S6/S7; testes de restore | Validar backup pré, staging, adoção offline, retorno e reconciliação em cópia; medir RPO/RTO aplicável. |
| Upgrade V0.4→V0.5→V1 | Roadmap §§9.2/9.4; RNF-033/057; CT-122 | `OPEN_FOR_V1` | Etapa V1 não exercitada | S8 prova V0.4.4→V0.5; `test_v05_s2a_upgrade.py` | Reusar fixture histórica, migrar até candidato V1 e reconciliar fatos. |
| Banco/constraints/checker | Roadmap §11; CT-073–083; RNF-025–033 | `PARTIALLY_DONE` | Revalidação V1/instalação limpa | S8 checker 25, PostgreSQL crítico; `operations/integrity.py` | SQLite/fks/invariantes, regressão e backend apenas no alcance aprovado. |
| Regressão/segurança/privacidade | Roadmap §§9.2/9.4/11; CT-099–104/121/123/130/134 | `PARTIALLY_DONE` | Release V1 exige execução e cobertura aplicável | S10 gate 505/86%; testes e settings | Matriz P0/P1/P2, gate, isolamento, CSRF, logs, dependências e dados privados; corrigir findings. |
| Acessibilidade, browser, usabilidade | RNF-006–011/044–050/063–065; CT-090–092/124–128 | `PARTIALLY_DONE` | Auditoria final direta e matriz de suporte | S9 relato humano limitado; testes UI; V10-D2 resolvida | Windows 11 x64: Chrome/Edge estáveis vigentes; Firefox estável vigente e imediatamente anterior; Brave estável vigente, padrão e sem extensões; Safari `N/A / NOT TECHNICALLY APPLICABLE TO THE SUPPORTED V1 PLATFORM`, com exceção publicada antes da entrega. Auditar teclado, foco, labels, contraste, zoom 200%, 360–1920 px e jornadas. |
| BCR-1 e BCR-2 | Roadmap §9.4/§11; RNF-001–005; CT-105–112 | `PARTIALLY_DONE` | BCR-1 final e BCR-2 ausente | S9 FAIL original + PASS reprodução; `scripts/run_bcr1.py` | Reexecutar BCR-1 oficial; criar/executar BCR-2 determinístico e relatar degradação sem limiar inventado. |
| Erros e recuperação | Roadmap §9.2; RNF-009/010/032; Fluxos §10 | `PARTIALLY_DONE` | Clareza V1 não auditada integralmente | UI S7/S9; `tests/test_v05_s7_ui.py` | Inspecionar validação, conflito, arquivo inválido, restore e ações destrutivas; corrigir apenas falhas observadas. |
| Flags/dívida bloqueante | Roadmap §9.2/§11.2 | `PARTIALLY_DONE` | Inventário final | Busca dirigida sem flag temporária identificada; findings S9/S10 | Confirmar configuração/flags; registrar dívida com impacto, prazo e evidência; resolver bloqueante. |
| Instalação/Windows/docs/changelog | Roadmap §§9.2/9.4/9.7; RNF-053/056; CT-127/128 | `PARTIALLY_DONE` | Guia V1, versão coerente e artefatos de release | README/guia Windows beta; `pyproject.toml` 0.1.0; V10-D2 resolvida | Plataforma oficial Windows 11 x64; distribuição por GitHub Release estável `v1.0.0`; instalar via fluxo atual `uv`/runtime Python gerenciado/`scripts/start-local.ps1`, em loopback. Documentar instalação limpa e suporte; launcher, instalador, exe, serviço e tray ficam Pós-V1. |
| Piloto local real controlado | Roadmap §§9.2/9.4; RNF-035/038; CT-121/126 | `OPEN_FOR_V1` | S10 foi sintético | D1/S10 explícitos | Piloto privado com uso/dados reais protegidos, roteiro e recovery, aprovação humana. |
| Publicação `v1.0.0` | Roadmap §9.7; AGENTS §8 | `OPEN_FOR_V1` | Nenhuma promoção V1 | Apenas tag/pre-release V0.5 publicados; V10-D2 define canal | Separar implementação, promoção documental e publicação estável autorizada; somente GitHub Release estável após promoção e autorização próprias. |
| Camada funcional nova/Pós-V1 | Roadmap §§9.1/9.6/10; Escopo §11 | `NOT_APPLICABLE` | Nenhum | Escopo + erratas; ausência de RF/RN/CT próprios para tags | Não planejar feature nova. |

### Recorte da Etapa 10 para a release

| Casos | Situação no baseline | Prova V1 exigida |
| --- | --- | --- |
| CT-055–072 (Domain/Priority) e CT de `REV-FIXA-1.0` | Vetores e serviços V0.5 automatizados; S4–S6 e S10 deram evidência beta | Reconciliar oráculos independentes, bordas, versões e história antes do congelamento; repetir regressão no candidato. |
| CT-073–083, 099–104, 129–136 (banco/segurança) | Testes existentes e S8/S10; cobertura PostgreSQL limitada à matriz crítica | Executar P0/P1 aplicáveis no candidato e abrir teste novo só para lacuna concreta; PostgreSQL total apenas se suporte o exigir. |
| CT-105–108, 110–112 (BCR-1) | S9 contém FAIL original e PASS posterior, S10 reutilizou essa prova beta | Repetir três runs oficiais no candidato V1 e preservar resultados brutos. |
| CT-109 (`BCR-2`) | Sem execução identificada | Criar prova de 2× BCR-1, com integridade e degradação registrada; sem SLA novo. |
| CT-113–120 (backup/CEI/restore) | S7/S8/S10 cobriram fluxos beta e rejeições | S6 é owner da prova completa: repetir no candidato V1, provar pacote CEI V0.5 → import V1 sob V10-D1, rejeições antes de escrita, cópia isolada e recovery final. |
| CT-121/123 (jornada e regressão aplicável) | Jornada S10 sintética; provas beta não substituem candidato V1 | S3 é owner da regressão aplicável; pode compartilhar smoke com S6, sem duplicar provas completas de upgrade/backup/restore/CEI/recovery. |
| CT-122 (upgrade entre versões) | S8 provou V0.4.4→V0.5, sem cadeia até V1 | S6 é owner: repetir a cadeia completa até o candidato V1 e reconciliar fatos. |
| CT-127/128 (instalação e browsers) | Jornada S10 sintética; matriz de browsers incompleta | S7 é owner da instalação limpa e documentação; S4/S7 cobrem a matriz de browsers de V10-D2. |
| CT-090–092/124–126 (acessibilidade/usabilidade) | Automação/revisão estática e relato humano S9 com precisão limitada | Sessões/inspeção final observadas com ambiente, páginas e resultados; aplicar protocolo/limiares aprovados quando pertinentes, sem inventar participantes. |

O plano de testes §7.2 exige 100% dos P0/P1 **aplicáveis** executados e
aprovados; a matriz final deve relacionar cada ID ao teste/observação, indicar
`COVERED`, `PARTIAL`, `MISSING` ou `RELEASE_RERUN`, justificar N/A e não usar
contagem bruta de testes como substituto de cobertura relevante.

## 4. Estágios propostos e dependências

Dez estágios resultam de dez decisões/evidências separáveis: contrato e versão,
correção de findings, prova automatizada, auditoria humana de interface,
desempenho, upgrade/recovery, documentação, piloto real, promoção e publicação.
Nenhum é XL. O grafo é `S1 → S2 → S3 → {S4, S5, S6} → S7 → S8 → S9 → S10`.
S3 valida regressão, integridade e segurança antes das provas de S4/S5/S6. Esses
estágios usam o mesmo candidato identificado; não criar paralelismo que misture
versões. Se S3–S6 encontrarem falhas, voltar a S2 sob contrato próprio e repetir
somente provas afetadas, além do gate final integral. S10 exige autorização
externa explícita mesmo após `V1_PROMOTION_APPROVED`.

Rastreabilidade principal por estágio; cada contrato futuro detalhará os casos
aplicáveis e justificará exclusões sem ampliar requisitos:

| Estágio | RF/RN/RNF e fluxos | Casos centrais |
| --- | --- | --- |
| S1 | RN-033–051/068–084; RNF-041/055/064; FL-009–013/019/022 | CT-055–072, 128; revisão dos critérios CT-118–120, cuja prova de compatibilidade é executada em S6 |
| S2 | RF-018/020/027/044/046/066/069–071; RNF-009/010/032/055; FL-005/007/010/012/019/021/022 | Regressões dos CT afetados pelo finding |
| S3 | RNF-013/018–033/068–080; FL-003/010/021/022 | CT-073–083, 099–104, 121/123/129–136 |
| S4 | RNF-006–011/044–050/063–065; FL-002/003/010/020/022 | CT-090–092, 124–128 |
| S5 | RNF-001–005/059–061/078–079; fluxos de leitura/escrita medidos | CT-105–112 |
| S6 | RF-067–070; RNF-033–043/057; FL-022 e histórico FL-003/010/021 | CT-113–120, 122 |
| S7 | RF-067–070; RNF-053/056/063–065; FL-022 | CT-127/128; smoke CT-123 reutiliza a regressão de S3 |
| S8 | Jornadas RF-001–071 aplicáveis; RNF-006–011/025–043/044–050; FL-001–022 aplicáveis | CT-121/126, checker, backup/CEI/recovery |
| S9 | Roadmap §§9.4/11 e Etapa 10 §7.2; toda rastreabilidade aplicável | P0/P1, gate completo e evidências S1–S8 |
| S10 | Roadmap §9.7; política operacional de release | Verificação de alvo/tag/release após promoção |

### Modelo/esforço A7 e revisão A8

Modelo/esforço recomenda a capacidade de execução futura; A8 define a
profundidade da revisão e permanece separado. Nenhuma configuração autoriza o
estágio por si só. A7 deve usar o modelo mais barato plausivelmente suficiente;
número de release, nome do estágio, quantidade de testes ou duração aparente do
trabalho não justificam Sol sem evidência concreta de complexidade.

| Estágio | Modelo / esforço recomendado | A8 |
| --- | --- | --- |
| S1 | GPT-6 Luna High | standard |
| S2 | GPT-6 Luna xHigh | standard por padrão; deep somente se houver alteração funcional material |
| S3 | GPT-6 Luna xHigh | deep |
| S4 | GPT-6 Luna High | standard |
| S5 | GPT-6 Luna High | standard |
| S6 | GPT-6 Sol High | deep |
| S7 | GPT-6 Luna Medium | standard |
| S8 | GPT-6 Sol High | deep |
| S9 | GPT-6 Sol High | deep |
| S10 | GPT-6 Luna Medium | nenhuma revisão adicional ou revisão administrativa standard |

Escalonamento por evidência: a sequência de preferência é `Luna Medium →
Luna High → Luna xHigh → Sol Medium → Sol High`, sem obrigação de passar por
cada nível. S2 fica em Luna xHigh para triagem, confirmação, documentação e
correções pequenas; sobe a Sol Medium somente ante alteração funcional
material, reconstrução, transação complexa, risco de integridade ou correção
cross-module. S3 fica em Luna xHigh para regressão, testes, banco, segurança,
privacidade e comparação; sobe a Sol Medium diante de vulnerabilidade ou
finding material que exija mudança de segurança/integridade. S4 pode subir de
Luna High para Luna xHigh diante de ambiguidade de acessibilidade, browser,
usabilidade, interface ou exceção. S5 sobe de Luna High para Sol Medium só após
falha/regressão de desempenho comprovada, gargalo investigado ou otimização
necessária. S6/S8/S9 mantêm Sol High pela combinação de upgrade/restore/CEI e
risco de integridade de dados, piloto real controlado com dados pessoais, e
gate integrado de promoção respectivamente. Registrar modelo e motivo real na
evidência; este plano apenas recomenda.

### S1 — Contratos V1 e decisões de compatibilidade

- Objetivo/escopo: persistir as addenda V10-D1/D2 resolvidas; auditar versões e
  compatibilidade de `REV-FIXA-1.0`, `DOM-HEUR-1.0`, `PRI-HEUR-1.0`,
  `CEI-EXPORT-1.0`; fechar matriz de suporte, findings beta e requisitos
  aplicáveis. Fora: alterar regra, schema, formato ou lançar produto.
- Dependência: P0 aprovado e addenda humanas persistidas. Artefatos: contratos S1,
  matriz CT/RF/RN/RNF, política de versão/suporte. `M/high`, migration `NO`,
  dados somente leitura. Modelo/esforço A7: `GPT-6 Luna High`; A8: standard.
- Testes/validação: revisão de vetores CT-055–072, política REV, critérios
  CT-118–120 (prova executada em S6), decisões S7/S8 e matriz de browsers; sem
  suíte nova se só documental. Aceite:
  códigos, fronteiras, compatibilidade e suporte determinados sem reescrever
  história. Se surgir novo conflito ou decisão material, pausar e registrar
  `HUMAN_DECISION_REQUIRED`. Recovery: preservar exports/backups históricos.
  Documentar contrato e matriz; estado final: `CONTRACTS_FROZEN_FOR_V1` somente
  com aprovação formal.

### S2 — Estabilização e identidade do candidato

- Objetivo/escopo: triagem por severidade dos findings beta e novos; correções
  mínimas reproduzidas de fluxo, mensagens/recuperação, flags comprovadamente
  temporárias, versões de UI/log/pacote/manifesto conforme S1. Fora: redesign,
  features novas, FTS e tuning especulativo.
- Dependência: S1. Artefatos: código/testes/guia afetados e registro de findings.
  `M/high`, migration `NO` prevista; dados: compatibilidade e histórico devem
  permanecer. Modelo/esforço A7: `GPT-6 Luna xHigh`; A8: standard por padrão,
  deep somente se houver alteração funcional material. Permanecer em Luna xHigh
  para análise e correções pequenas/localizadas. Escalar a `GPT-6 Sol Medium`
  somente se finding exigir alteração funcional material, reconstrução de
  estado, raciocínio transacional complexo, correção cross-module, risco real
  de integridade ou comportamento não local difícil de provar.
- Testes: reprodução RED quando possível, regressões focadas de lifecycle,
  export, restore, isolamento, versões e mensagens; gate autoritativo ao fechar.
  Aceite: Blocker/Major aplicáveis resolvidos e candidato identificável sem
  quebrar pacote V0.5 compatível ou afrouxar validação. Parada: mudança de
  schema ou compatibilidade fora da política → A4/decisão, sem migration
  automática. Recovery:
  backup pré-upgrade validado e fallback de release anterior. Documentação:
  comportamento/versionamento; estado final: candidato estabilizado.

### S3 — Regressão, banco, segurança e privacidade

- Objetivo/escopo: mapear Etapa 10 aos testes existentes, preencher somente
  lacunas críticas, provar instalação limpa, migrations atuais, constraints,
  checker read-only, idempotência, Workspace, CSRF, segurança de entradas,
  logs e dependências. A prova completa de upgrade, backup, restore, recovery e
  CEI pertence a S6. Fora: novas funcionalidades e operação PostgreSQL remota.
- Dependência: S2. Artefatos: matriz CT, testes focados, evidência de gate.
  `M/high`, migration `NO` prevista; dados em bases descartáveis. Modelo/esforço
  A7: `GPT-6 Luna xHigh`; A8: deep por risco de integridade/segurança.
- Escalar para `GPT-6 Sol Medium` se surgir vulnerabilidade real, finding
  material de privacidade/integridade, mudança de código de segurança,
  comportamento transacional complexo ou correção cross-module. Luna xHigh pode
  executar regressão, revisar testes e comparar evidências sem escalonamento.
- Testes: CT-073–083, 099–104, 121, 123, 129–136 (ou subconjunto aplicável),
  vetores de políticas,
  `quality.ps1` com exit 0; PostgreSQL crítico somente se requisito/backend
  aplicável, sem extrapolar S8. Aceite: P0/P1 do recorte S3 100% executados e
  aprovados, domínio ≥80% conforme Etapa 10, nenhum S1/S2 aberto; registrar
  exceções reais. Parada: corrupção, cross-Workspace, exposição de segredo ou
  gate RED. Recovery: descartar fixtures isoladas, preservar evidência.
  Documentação: matriz/gate; estado final: regressão crítica V1 provada.

### S4 — Acessibilidade, navegadores e usabilidade

- Objetivo/escopo: auditar jornadas centrais reais em browser, teclado, foco,
  labels, contraste, zoom 200%, 360–1920 px, leitor de tela quando aplicável,
  estados vazios, erros e recuperação; corrigir findings de fluxo existente.
  Fora: identidade visual/design system/novo fluxo de produto.
- Dependência: S3 concluída sobre o candidato estabilizado em S2. S3 é a
  baseline obrigatória da sessão final. Artefatos: roteiro,
  capturas/observações sanitizadas, testes apenas para defeitos, revisão de UI.
  `M/medium`, migration `NO`, dados fictícios para auditoria; modelo/esforço
  A7: `GPT-6 Luna High`; A8: standard. Se houver ambiguidade relevante de
  acessibilidade, diferenças entre browsers, usabilidade, visual ou exceção,
  subir primeiro para `GPT-6 Luna xHigh`.
- Testes: CT-090–092/124–128 aplicáveis; Windows 11 x64: Chrome e Edge estáveis
  vigentes; Firefox estável vigente e imediatamente anterior; Brave estável
  vigente, configurações padrão e sem extensões. Brave exige fluxos centrais,
  smoke visual/funcional, acessibilidade, usabilidade e responsividade; falha
  funcional reproduzível em fluxo central impede declarar suporte. Não exigir
  versão anterior do Brave. Safari: `N/A / NOT TECHNICALLY APPLICABLE TO THE
  SUPPORTED V1 PLATFORM`, justificar e documentar antes da entrega; nunca
  declarar testado, certificado ou suportado. Separar automação, relato humano
  e inspeção visual. Aceite: critérios RNF-044–050/063–065 e usabilidade
  observados com versões e páginas identificadas, desvios resolvidos ou decisão
  formal.
  Parada: perda de ação/dado, navegação central inacessível. Recovery: reverter
  alterações UI localizadas. Documentar evidência e limites; estado final:
  auditoria final aplicável aprovada.

### S5 — Desempenho BCR-1 e BCR-2

- Objetivo/escopo: repetir `BCR-1` oficial no candidato e medir `BCR-2` (2×
  dataset) conforme RNF-005/CT-109, inclusive regressão e integridade.
  Otimizar apenas gargalo medido. Fora: FTS, snapshots ou limites novos por
  inferência.
- Dependência: S3 concluída (com candidato estabilizado em S2), para consumir a
  prova de integridade dos dados. Artefatos: harness/JSON de
  execução e análise, código/testes só se falha provada. `M/medium`, migration
  `NO` prevista, dados sintéticos descartáveis; modelo/esforço A7:
  `GPT-6 Luna High`; A8: standard. Escalar para `GPT-6 Sol Medium` somente se
  benchmark falhar, regressão de desempenho for comprovada, houver investigação
  de gargalo ou otimização de código necessária.
- Testes: CT-105–112; 20 warm-ups, 100 amostras, 3 runs, nearest-rank para
  CT-107/ADR-012; registrar ambiente, seed e percentis; no BCR-2 verificar
  ausência de corrupção/duplicação/falha silenciosa e relatar degradação.
  Aceite: metas BCR-1 aplicáveis PASS em cada run e BCR-2 sem violar RNF-005.
  Parada: FAIL reproduzível ou medição incompleta; não chamar inconclusivo de
  PASS. Recovery: descartar apenas alvo sintético verificado. Documentar
  resultados brutos e decisão; estado final: desempenho V1 comprovado.

### S6 — Cadeia de upgrade e recuperação

- Objetivo/escopo: provar V0.4.4 representativa → V0.5 → candidato V1,
  instalação limpa, backup, restore, recovery e CEI em provas independentes.
  Fora: restore sobre banco original/ativo, downgrade automático ou merge CEI.
- Dependência: S1, S2 e S3 concluídas sobre o mesmo candidato estável. Pode
  avançar junto de S4/S5 somente se a identidade do candidato for preservada;
  qualquer mudança volta ao fluxo de S2 e exige repetir as provas afetadas.
  Artefatos: fixture/protocolo/relatório de upgrade e recovery; `L/high`,
  migration `NO` prevista, alto impacto potencial em dados; modelo/esforço A7:
  `GPT-6 Sol High`; A8: deep. A4 completo antes de operação destrutiva mesmo
  em cópia.
- Testes CT-113–120 e CT-122: reutilizar `MigrationExecutor` S8/fixtures
  históricas e provar
  `export V0.5 válido → import V1 válido`. Manter `CEI-EXPORT-1.0` e
  `format_version=1.0`; `application_version` identifica o produtor, aceitando
  explicitamente no mínimo `V0.5` e `V1.0` somente se compatíveis. Validar
  manifesto, producer version, format, policies reconhecidas, migrations
  compatíveis, schema, UUIDs, referências, contagens, checksums, arquivos
  esperados/ausência de extras proibidos, destino compatível, invariantes,
  checker final, validação antes de escrita e round-trip quando aplicável.
  Testar rejeição antes de qualquer escrita para produtor não suportado,
  migration incompatível, policy desconhecida, schema incompatível e checksum
  incorreto. Sem conversão, coerção, tentativa parcial, merge ou adaptação de
  schema. Na ausência de migration nova, registrar que nenhuma mudança de schema
  facilita compatibilidade V0.5→V1; se finding real exigir migration, reavaliar
  a política explicitamente. Em paralelo, validar backup pré, migrations,
  IDs/contagens, checks SQLite/FK, checker 25/0, histórico, políticas e
  derivados; restaurar em destino isolado e reconciliar fingerprints; CEI
  CT-118–120 segue V10-D1; incompatibilidades são rejeitadas antes de mutação.
  Aceite: cadeia reproduzível
  sem perda semântica e recovery conforme RNF-035/038; nenhum PASS baseado só
  em S8. Parada: diferença inexplicada, backup inválido, checker finding ou
  pacote incompatível sem decisão. Recovery: preservar pré-backup e executar
  retorno offline validado em cópia. Documentar matriz/procedimento; estado
  final: upgrade/recuperação V1 comprovados.

### S7 — Documentação operacional e candidato de release

- Objetivo/escopo: reconciliar README e guias oficiais de instalação, uso,
  atualização, backup/restore/recovery, troubleshooting e suporte, mais
  changelog e release notes; identificar versão na UI/manifesto conforme S1.
  Publicar matriz de browsers incluindo exceção formal Safari. Suporte é
  documental; GitHub Issues pode ser usado para defeitos se habilitado, sem SLA,
  suporte comercial, 24/7 ou garantia de resposta. Fora: publicar ou criar
  instalador, launcher, exe, serviço ou tray.
- Dependência: S3–S6 e V10-D2 resolvida. Artefatos: guias e notas V1; `M/medium`,
  migration `NO`, sem dados reais; modelo/esforço A7: `GPT-6 Luna Medium`;
  A8: standard. Se surgir conflito normativo real, escalar a `GPT-6 Luna High`.
- Testes: CT-127 instalação limpa Windows 11 x64 seguindo apenas docs, no fluxo
  atual com `uv`, runtime Python gerenciado, `scripts/start-local.ps1` e
  loopback; smoke Chrome/Edge estáveis vigentes, Firefox estável vigente e
  anterior e Brave estável vigente em padrão/sem extensões. Exercitar
  procedimentos em cópia e checar links/versão. O canal de distribuição é a
  futura GitHub Release estável `v1.0.0`, após promoção e autorização. Não
  acrescentar empacotamento nativo ou experiência de um clique; esses itens são
  Pós-V1. Safari permanece formalmente N/A conforme V10-D2.
  Aceite: usuário consegue instalar, usar, atualizar e recuperar com
  instruções verificadas; riscos/limitações e notas correspondem ao candidato.
  Parada: procedimento não reproduzível ou suporte indefinido. Recovery:
  preservar guia beta e backup pré. Estado final: release candidate documentado.

### S8 — Piloto final local real controlado

- Objetivo/escopo: uso pessoal real privado do candidato em instalação local
  controlada, com dados próprios autorizados, backup e recuperação comprováveis.
  Fora: exposição pública, multiusuário e operação no banco original sem plano
  de proteção específico.
- Dependência: S3–S7 aprovados e autorização própria do piloto. Artefatos:
  A4, roteiro, logs sanitizados, findings e relatório; `L/high`, migration
  `NO` prevista, dados pessoais protegidos; modelo/esforço A7: `GPT-6 Sol High`;
  A8: deep.
- Entrada mínima qualitativa: instalação local representativa do uso do
  responsável, Workspace/fuso/configuração identificados, questões e tentativas
  provenientes de uso normal e ciclos/revisões suficientes para percorrer os
  fluxos centrais. Registrar contagens e diversidade efetivas sem inventar
  mínimo numérico ou duração. A4 decide origem, consentimento, isolamento,
  proteção, backup/retorno, checkpoints e stop antes de tocar dados. Se a
  representatividade não puder ser obtida, piloto permanece sem PASS.
- Roteiro: cadastro→tentativa→erro→revisão D1/D7/D14/D30 quando observáveis,
  consulta, filtros, Domain/Priority, correções, categorias, CEI, backup,
  restore/recovery em **cópia isolada**, Windows e observação de usabilidade.
  Verificar checker, contagens, integridade, erros, logs e hashes antes/depois;
  pré-backup validado e retorno ensaiado. Medir RPO/RTO conforme RNF-035.
  Aceite: uso e recuperação observados, original protegido, Blocker/Major 0 e
  aprovação explícita do responsável. Parada imediata por corrupção, perda de
  dados, cross-Workspace, backup irrecuperável, checker crítico ou incerteza de
  origem. Recovery conforme A4; estado final: piloto real aprovado ou bloqueado.

### S9 — Gate final e decisão de promoção

- Objetivo/escopo: auditar todos os critérios de Roadmap §9.4/§11, Etapa 10,
  evidências S1–S8 e estado de findings; registrar decisão documental.
  Fora: tag/release/publicação. Dependência: S8.
- Artefatos: checklist de promoção, quality result, A8 e estado; `M/high`,
  migration `NO`, leitura de dados/evidências; modelo/esforço A7:
  `GPT-6 Sol High`; A8: deep.
- Testes: gate autoritativo `quality.ps1` exit 0 no candidato, regressão,
  clean install, upgrade, backup/restore/recovery, CEI, checker, segurança,
  privacidade, desempenho, acessibilidade, usabilidade e piloto diretamente
  evidenciados. Aceite: todos os P0/P1 aplicáveis PASS, S1/S2 aberto 0,
  Blocker/Major 0, A8 APPROVED e aceitação humana do piloto. Parada: qualquer
  prova obrigatória FAIL/ausente/ambígua → `PROMOTION_BLOCKED`. Recovery: nenhuma
  mutação de dados neste gate; preservar candidato/evidência. Documentar decisão;
  estado final **`V1_PROMOTION_APPROVED`** somente se comprovado, distinto de
  `V1_IMPLEMENTATION_COMPLETE` e de publicação.

### S10 — Publicação estável autorizada

- Objetivo/escopo: após promoção, preparar checkpoint revisável, alvo de commit,
  tag anotada esperada `v1.0.0`, release estável (não pre-release), changelog e
  notas finais; publicar apenas por autorização explícita adicional. Fora:
  correção funcional silenciosa ou mudança de critérios de promoção.
- Dependência: S9 `V1_PROMOTION_APPROVED` e revisão humana de alvo/artefatos.
  Artefatos: checklist de publicação, commit/tag/release e reconciliação de
  estado; `S/medium`, migration `NO`, sem dados de usuário; modelo/esforço A7:
  `GPT-6 Luna Medium`; A8: nenhuma adicional ou revisão administrativa standard.
- Testes/validação: conferir HEAD, working tree, tag inexistente, artefatos,
  hash do alvo, release notes e checks já aprovados; após publicação verificar
  referência remota e metadados. Aceite: tag aponta ao candidato promovido,
  release estável e documentação coerentes. Parada: alvo divergente, tag já
  existente ou falta de autorização. Recovery: não reescrever tag/release
  histórica; registrar incidente e obter decisão. Estado final:
  **`v1.0.0 TAG/RELEASE PUBLISHED`** somente após observação direta.

## 5. Gates, findings e critérios de promoção

`V1_IMPLEMENTATION_COMPLETE` significa estágios de estabilização executados;
não equivale a piloto aprovado. `V1_PROMOTION_APPROVED` exige checklist final
com evidência própria V1 de S1–S8, regressão completa, migrations/instalação
limpa, upgrade V0.4→V0.5→V1, backup/restore/recovery, export/import CEI,
checker read-only, segurança/privacidade, BCR-1/BCR-2, acessibilidade,
usabilidade, documentação, piloto real, A8 deep e gate GREEN exit 0. Publicação
é terceiro estado separado, posterior e explicitamente autorizado. A8 e gate
são independentes. Nenhum resultado histórico V0.5 é convertido em PASS V1.

Findings preservam primeira falha e reteste. **Blocker:** perda/corrupção,
cross-Workspace, backup/restore irrecuperável, migration destrutiva,
integridade crítica, upgrade inseguro ou vulnerabilidade crítica aplicável.
**Major:** falha reproduzível em fluxo obrigatório ou gate V1. **Minor:**
problema não bloqueante, com impacto, responsável e aceitação explícita.
Nenhum Blocker/Major aberto na promoção; P0/P1 aplicáveis devem passar.
Falha ambiental/inconclusiva não vira PASS nem defeito de produto sem prova.
Achados fora de escopo são registrados e não corrigidos por impulso.

## 6. Decisões humanas resolvidas e riscos

As addenda abaixo foram decididas pelo responsável do produto e ficam
registradas neste plano V1.0-P0. As decisões se aplicam à V1; os documentos
normativos congelados, inclusive o Roadmap, não foram editados.

### V10-D1 — compatibilidade CEI (`RESOLVED`)

- V1 deve importar pacotes comprovadamente compatíveis `CEI-EXPORT-1.0`
  produzidos por V0.5. O formato permanece `format = CEI-EXPORT` e
  `format_version = 1.0`; não criar `CEI-EXPORT-1.1` só pela mudança de versão
  da aplicação.
- `application_version` continua identificando o produtor. A política futura
  reconhecerá explicitamente no mínimo `V0.5` e `V1.0` como produtores
  permitidos, somente quando todas as condições forem satisfeitas.
- Permanecem obrigatórias as validações de formato e manifesto, versão do
  produtor, policies reconhecidas, migrations compatíveis, schema válido,
  UUIDs e referências, contagens, checksums, arquivos esperados e extras
  proibidos, destino compatível e invariantes funcionais. Toda validação ocorre
  antes de qualquer escrita. Pacote incompatível falha sem conversão silenciosa,
  coerção, tentativa parcial, merge ou adaptação de schema.
- A previsão V1 continua sem migration nova; registrar que a ausência de
  mudança de schema facilita compatibilidade V0.5→V1. Não criar migration para
  distinguir V1. Se um finding real exigir migration, reavaliar explicitamente
  a política de compatibilidade.
- Prova futura obrigatória: `export V0.5 válido → import V1 válido`, cobrindo
  manifesto, produtor, policies, migrations, checksum, dados, UUIDs, invariantes,
  checker final e round-trip quando aplicável. Casos negativos devem rejeitar,
  antes de escrita, produtor não suportado, migration incompatível, policy
  desconhecida, schema incompatível e checksum incorreto. Rastrear em
  CT-118–120/S6 e na matriz final de Etapa 10.

### V10-D2 — plataforma, distribuição e suporte (`RESOLVED`)

- Plataforma oficial: Windows 11 x64. O produto permanece local, individual,
  em loopback, sem hospedagem pública ou multiusuário remoto.
- Canal: futura GitHub Release estável `v1.0.0`, após promoção e autorização
  próprias. Não será pre-release após promoção.
- Execução local: `uv`, ambiente reproduzível, runtime Python gerenciado pelo
  fluxo atual, `scripts/start-local.ps1` e loopback. Launcher `.exe`, instalador
  gráfico, empacotamento nativo, auto-installer, ação adicional de um clique,
  serviço Windows e tray ficam Pós-V1.
- Matriz Windows 11 x64: Chrome estável vigente; Edge estável vigente; Firefox
  estável vigente e imediatamente anterior; Brave estável vigente, configuração
  padrão e sem extensões. Os quatro exigem fluxos centrais; Brave também exige
  smoke visual/funcional, acessibilidade/usabilidade e responsividade; falha
  funcional reproduzível em fluxo central impede declarar seu suporte. Não
  exigir versão anterior do Brave.
- Safari: `N/A / NOT TECHNICALLY APPLICABLE TO THE SUPPORTED V1 PLATFORM`, pois
  o escopo oficial se limita a Windows 11 x64 e Safari não é suportado nessa
  plataforma. Expandir para macOS só para testar Safari ampliaria o escopo. A
  exceção deve aparecer na documentação antes da entrega; não declarar Safari
  testado, certificado ou suportado.
- Preservar responsividade de 360–1920 px; isso não adiciona suporte oficial a
  aplicativo móvel, PWA, browser móvel, Android ou iOS.
- Suporte oficial via README e guias de instalação, uso, atualização,
  backup/restore/recovery, troubleshooting e documentação técnica aplicável.
  GitHub Issues poderá receber defeitos se estiver habilitado. Não declarar SLA,
  suporte comercial, 24/7, tempo garantido de resposta ou manutenção contratual.
- `RD-ABR-010 = RESOLVED` no nível do planejamento V1, refletido por esta
  addenda e pela matriz de suporte; não alterar silenciosamente o Roadmap
  congelado.

Não há outra decisão material aberta identificada nesta revisão. Permanecem
riscos de execução futura, com os critérios de parada correspondentes: (1)
confundir prova sintética S10 com piloto real; (2) quebrar CEI ao trocar versão;
(3) concluir upgrade por fixture V0.5 sem etapa V1; (4) inferir acessibilidade
de relato incompleto; (5) confundir `BCR-2` com novo SLA; (6) restaurar sobre
banco ativo; (7) publicar antes da promoção. Esses riscos não reabrem V10-D1/D2.

## 7. Review P0 e handoff

Revisão profunda documental de P0: Roadmap §§8–11, Etapa 10 §§3–9, escopo e
erratas, código/migrations/testes dirigidos, S8–S10 e fronteiras do contrato
foram comparados; addenda V10-D1/D2 e todos os estágios S1–S10 foram
reexaminados. A matriz cobre os itens do Roadmap §9.2, nenhum estágio está
classificado XL, não há feature Pós-V1 antecipada e a tabela A7 está limitada
às recomendações aprovadas. S3 é owner da regressão aplicável CT-121/123;
S6 é owner das provas CT-113–120/122. Dependências, A7/A8, CEI, browsers,
suporte e publicação estão consistentes com as decisões. Nenhum finding material
ou decisão humana adicional foi identificado no plano. Após as correções
menores da revisão, o responsável aprovou o plano em 2026-09-28. Estado final
do P0: **`COMPLETED / APPROVED`**. Esta aprovação valida o plano como autoridade
de planejamento, mas não autoriza S1 ou qualquer implementação; cada estágio
futuro exige contrato próprio `AUTHORIZED`.
