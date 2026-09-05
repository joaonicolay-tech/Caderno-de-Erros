# Caderno de Erros Inteligente

## Gate de Implementação — Auditoria Final da Documentação

| Campo | Valor |
|---|---|
| Documento | Relatório do Gate de Implementação |
| Projeto | Caderno de Erros Inteligente |
| Versão | 1.0.2 — registro da Etapa 0 V0.2 |
| Data | 1º de setembro de 2026 |
| Status | Auditoria concluída; saneamento V0.2 registrado em 5 de setembro de 2026 |
| Documentos auditados | Etapas 1 a 10, todas em versão 1.0 aprovada |
| Decisão | **GO COM RESSALVAS** |
| Nota de maturidade | **84/100** |
| Liberação | V0.1 autorizada; baseline integral condicionada às correções P1 |

---

# A. Resumo Executivo

A documentação forma uma especificação madura, tecnicamente viável e muito acima do mínimo necessário para iniciar um projeto individual. O problema, o público, o ciclo de valor, o MVP, as regras temporais, a arquitetura, os fatos históricos, a recuperação e os critérios de qualidade estão claramente definidos.

Os principais pilares são coerentes entre si:

- aplicação individual de estudo, sem expansão silenciosa para plataforma educacional;
- monólito modular em Python/Django, templates/HTMX e SQLite no MVP local;
- separação entre questão, versão de conteúdo, tentativa, erro, ciclo e revisão;
- política fixa `REV-FIXA-1.0`, com D1/D7/D14/D30 contados da conclusão válida anterior;
- tentativa e conclusão de revisão atômicas e idempotentes;
- domínio `DOM-HEUR-1.0` e prioridade `PRI-HEUR-1.0` somente na V1;
- métricas derivadas de fatos, com denominador e confiança explícitos;
- backup/restauração comprovados antes de uso real;
- implementação incremental V0.1 → V0.4 MVP → V0.5 beta V1 → V1.0.

A auditoria não encontrou contradição crítica na regra central, inviabilidade arquitetural ou lacuna que impeça o início da V0.1. Encontrou, porém, um problema documental relevante: o Plano de Testes possui bons casos e resultados esperados, mas várias referências apontam para regras ou decisões erradas, inclusive identificadores inexistentes. Também existem três fronteiras de escopo/fluxo que precisam ser corrigidas antes das funcionalidades relacionadas: tags antecipadas para V0.2, inclusão manual de questão inicialmente correta e gestão de categorias pessoais.

Portanto, o projeto pode começar pela V0.1, mas ainda não deve ser declarado uma baseline integral sem ressalvas.

# B. Decisão do Gate

## **GO COM RESSALVAS**

A implementação da **V0.1 — Fundação Executável** pode começar porque:

1. sua finalidade e seus limites estão claros;
2. stack, estilo arquitetural, banco e estratégia de migração estão escolhidos;
3. `User`, `Workspace`, fuso, relógio controlável, configuração, logs e backup mínimo estão especificados;
4. os riscos da V0.1 possuem respostas adequadas;
5. nenhuma pendência funcional avançada é necessária para iniciar o repositório, as migrações e a infraestrutura de testes.

As ressalvas não autorizam ignorar os problemas. Elas significam que as correções podem acompanhar o início do desenvolvimento, respeitando os marcos do Plano de Correção. Nenhuma funcionalidade V0.2/V0.3/V0.5 afetada deve ser implementada usando uma ligação documental sabidamente errada.

## Condição de liberação

- **V0.1:** liberada.
- **V0.2:** liberável após decidir a fase das tags e corrigir a rastreabilidade dos testes relacionados.
- **V0.3:** condicionada à correção das referências de tentativas/revisões e aos casos detalhados de idempotência, contexto transitório e concorrência.
- **V0.5:** condicionada aos fluxos ausentes de inclusão manual e categorias pessoais, além das decisões V1 abertas.
- **Baseline de Implementação 1.0 integral:** ainda não declarada; depende das correções P1.

# C. Nota de Maturidade

## **84/100**

| Dimensão | Nota | Evidência resumida |
|---|---:|---|
| Visão e escopo | 9/10 | Problema, valor, público, não objetivos e MVP claros; duas divergências de fase. |
| RFs, RNFs e regras | 18/20 | 71 RFs, 80 RNFs e 100 regras claros e testáveis; pequenas referências erradas e itens V1 órfãos. |
| Arquitetura e dados | 18/20 | Monólito modular, transações, histórico e integridade bem definidos; uma inconsistência de estado e alguns detalhes operacionais abertos. |
| Fluxos | 8/10 | 22 fluxos com falhas e alternativas; faltam fluxos próprios para capacidades específicas. |
| Roadmap | 9/10 | Ordem incremental e gates sólidos; tags antecipadas e V0.5 ampla. |
| Testes e rastreabilidade | 12/20 | 128 casos abrangentes, mas com várias ligações semânticas erradas e IDs inexistentes. |
| Operação, segurança e riscos | 10/10 | Segurança condicionada à exposição, backup testado, logs privados e riscos explícitos. |
| **Total** | **84/100** | Projeto implementável com correções controladas. |

# D. Pontos Fortes

## D.1 Visão e escopo

- Problema central e proposta de valor permanecem consistentes até o Plano de Testes.
- O sistema não promete “ensinar” ou garantir aprovação; organiza evidências e revisões.
- IA, integrações, colaboração, OCR, anexos, API e revisão adaptativa estão fora do MVP.
- “Ciclo concluído” é corretamente separado de “questão dominada”.
- O MVP formal é V0.4; versões anteriores são incrementos técnicos controlados.

## D.2 Requisitos e regras

- Os 71 RFs têm ator, prioridade, pré-condições, comportamento, pós-condições, exceções e critérios de aceitação.
- Os 80 RNFs evitam termos vagos e usam metas verificáveis, incluindo p95 e `BCR-1`.
- As 100 regras cobrem tempo, hierarquia, conteúdo, tentativas, erros, revisão, métricas, domínio, prioridade, histórico e insuficiência.
- As regras temporais são consistentes: próximo intervalo parte da conclusão real; atraso não é erro; erro reinicia em D1.
- `M_q`, `C_q`, `M_h`, `C_h` e prioridade possuem fórmulas, fronteiras, versões e tratamento de evidência insuficiente.

## D.3 Arquitetura

- Monólito modular é proporcional ao produto e evita microserviços, broker, cache distribuído e SPA sem necessidade.
- Apresentação, aplicação, domínio e infraestrutura possuem responsabilidades explícitas.
- Políticas críticas são isoladas de HTTP e do relógio global.
- Escrita por comandos e leitura por selectors é uma separação lógica, não CQRS distribuído.
- SQLite tem gatilhos claros para reavaliação e PostgreSQL só entra antes de implantação remota/multi-espaço ou por evidência.
- Tratamento de erros, configuração, logging, backup e segurança estão presentes no SDD.

## D.4 Modelo de dados

- `Question` é identidade estável e `QuestionRevision` preserva conteúdo/gabarito usado.
- `Attempt` é evento imutável e referencia a versão apresentada.
- `ErrorClassification` mantém projeção atual e histórico append-only.
- `ReviewCycle` e `Review` materializam a política sem persistir “atrasada” como estado obsoleto.
- Unicidades críticas são previstas: revisão corrente, inicial válida, tentativa por revisão, ciclo ativo e pendência por ciclo.
- `OperationReceipt` permite idempotência com hash de requisição.
- Métricas e snapshots não substituem os fatos autoritativos.
- Exportação e restauração têm manifesto, checksum, ordem de carga e reconciliação.

## D.5 Fluxos e testes

- Fluxos centrais incluem caminho ideal, alternativas, concorrência, rollback, privacidade e abandono.
- Abrir ou abandonar revisão não cria tentativa parcial.
- Gabarito é protegido antes do envio.
- O Plano de Testes cobre unitário, integração, funcional, UI, banco, regras, datas, estatística, domínio, regressão, desempenho, segurança, backup e usabilidade.
- Os 128 casos possuem objetivo, pré-condição/dados, passos, esperado, prioridade e fase.
- Desempenho, restauração e acessibilidade são gates, não atividades deixadas apenas para o fim.

# E. Problemas Encontrados

## E.1 Críticos

**Nenhum.**

Não foi encontrada regra central contraditória, ausência de persistência, arquitetura inviável, risco de perda de dados não tratado ou indefinição que impeça criar a V0.1.

## E.2 Altos

### `GATE-ALT-001` — Rastreabilidade semântica incorreta no Plano de Testes

O Plano de Testes contém casos tecnicamente úteis, porém parte das referências não corresponde ao comportamento testado. Exemplos:

| Caso | Referência atual | Problema | Referência coerente mínima |
|---|---|---|---|
| `CT-003` | `RN-004` | `RN-004` trata data prevista, não normalização de nomes. | `RN-008` |
| `CT-005` | `RN-013` | `RN-013` trata tipo de questão, não rascunho. | `RN-011` |
| `CT-006` | `RN-014` | `RN-014` trata origem opcional, não ativação mínima. | `RN-012` |
| `CT-009` | `RN-019` | `RN-019` trata edição não crítica. | `RN-020` |
| `CT-014` | `RN-024`, `RN-037` | `RN-024` é acerto inicial; `RN-037` é reinício após erro de revisão. | `RN-025`, `RN-033`, `RN-035`, `RN-046` |
| `CT-017` | `RN-031` | `RN-031` trata categorias pessoais. | `RN-030` |
| `CT-019` | `RN-033` | `RN-033` cria ciclo. | `RN-032` |
| `CT-024`–`027` | `RN-038` | `RN-038` trata facilidade sem efeito no calendário. | `RN-036`, `RN-047` conforme o caso |
| `CT-031`, `CT-032` | `RN-042`, `RN-043` | Tratam início sem efeito e proteção de gabarito, não situação temporal. | `RN-040` |
| `CT-043` | `RN-047` | `RN-047` trata ciclo concluído. | `RN-052`, `RN-053` |
| `CT-045`–`054` | `RN-051`–`059` em sequência | Os números foram associados por posição, não por semântica. | `RN-056`–`067`, `RN-097`–`100` conforme cada métrica |
| `CT-075` | `MD-DEC-007` | A decisão 007 trata histórico de diagnóstico. | `MD-DEC-004` e invariantes do modelo |
| `CT-076` | `MD-DEC-011` | A decisão 011 trata pontos-base. | Invariante “uma inicial válida” e `RN-021` |
| `CT-078` | `MD-DEC-013` | A decisão 013 trata exclusão por agregado. | Invariante “um ciclo ativo” |
| `CT-079` | `MD-DEC-014` | A decisão 014 trata limites de texto/ano. | Invariante “uma pendência por ciclo” e `RN-039` |

Isso não invalida o objetivo dos casos, mas impede usar o documento como matriz autoritativa sem correção.

### `GATE-ALT-002` — Identificadores inexistentes no Plano de Testes

Foram encontradas oito ocorrências inválidas:

- o documento declara `RN-001` a `RN-105`, mas as regras existentes terminam em `RN-100`;
- `SDD-DEC-003`, `SDD-DEC-012`, `SDD-DEC-013` e `SDD-DEC-014` não existem no SDD;
- os IDs válidos do SDD usam, entre outros, `SDD-ADR-*`, `SDD-MOD-*`, `SDD-SVC-*`, `SDD-ABR-*` e `SDD-RIS-*`.

Ocorrências afetadas: `CT-022`, `CT-038`, `CT-080`, `CT-084`, `CT-101`, `CT-111` e o caso expandido `CT-039`, além da declaração de faixa de regras.

### `GATE-ALT-003` — Capacidades V1 sem fluxo e teste próprios

Duas capacidades aprovadas não estão suficientemente fechadas:

1. `RF-033` — gerenciar categorias pessoais: existe entidade e item de roadmap, mas o fluxo permanece como `FL-ABR-004` e não há caso detalhado para criar, renomear, arquivar, consolidar e preservar históricos.
2. `RF-045` — incluir manualmente questão inicialmente correta em revisão: `FL-019` trata reabertura de questão **dominada**, que é condição diferente; `CT-044` também cobre somente a reabertura dominada.

Essas lacunas não bloqueiam V0.1–V0.4, mas bloqueiam as capacidades correspondentes da V0.5-A.

### `GATE-ALT-004` — Tags antecipadas sem RF e sem teste dedicado

O Escopo coloca tags em `ESC-V1-008` e afirma que não pertencem ao conjunto mínimo do MVP. Entretanto:

- o Modelo de Dados classifica `Tag` e `QuestionTag` como MVP;
- `FL-002`, `FL-005` e `FL-020` usam tags;
- o Roadmap inclui tags na V0.2;
- não existe RF específico para gerenciar tags;
- não existe caso de teste específico para ciclo de vida, unicidade, arquivamento e filtro por tags.

Isso é crescimento de escopo entre documentos. A opção mais simples é retirar tags da V0.2 e devolvê-las à V0.5-A/V1. Se forem mantidas no MVP, será necessária mudança formal no Escopo, um RF, regras e testes.

## E.3 Médios

### `GATE-MED-001` — Casos detalhados insuficientes para alguns critérios da V0.1

Os gates mencionam, mas o catálogo não possui CTs próprios para:

- seed idempotente das categorias padrão;
- rota de diagnóstico/health local;
- separação dos perfis de configuração;
- instalação limpa pelo README na própria V0.1;
- backup/restauração do banco vazio ou mínimo na V0.1.

`CT-127`, `CT-113` e `CT-115` aparecem em fases posteriores. A V0.1 deve criar casos próprios ou antecipar formalmente os aplicáveis.

### `GATE-MED-002` — Estado de reagendamento diverge entre SDD e Modelo de Dados

O SDD, seção 12.3, lista “substituída por reagendamento” como exemplo de estado estrutural. O Modelo de Dados e `FL-DEC-011` determinam que reagendamento mantém a mesma revisão `PENDING`, atualiza `current_due_date` e cria `ReviewScheduleChange`.

Correção recomendada: remover “substituída por reagendamento” do SDD e declarar que o histórico está no evento, não em uma nova revisão/estado.

### `GATE-MED-003` — Pontos abertos resolvidos continuam marcados como abertos

Exemplos:

- `SDD-ABR-003` e `MD-ABR-001` foram resolvidos por `FL-DEC-001`;
- `MD-ABR-002` foi resolvido por `FL-DEC-002`/`003`;
- `SDD-ABR-007` foi fechado por `CEI-EXPORT-1.0`/`MD-DEC-015`;
- `RN-ABR-001` foi resolvido pela seção 3.6 do Modelo de Dados.

O conteúdo final é identificável, mas falta status central “resolvido por”. Isso aumenta o risco de uma pessoa implementar a decisão antiga como ainda aberta.

### `GATE-MED-004` — Personalização de intervalos possui fronteira inconsistente

`ESC-V1-005` menciona “eventual personalização dos intervalos fixos”. Regras, SDD e Roadmap mantêm `REV-FIXA-1.0` na V1 e colocam revisão adaptativa no Pós-V1. Não existe RF, modelo de configuração, fluxo ou teste para personalização.

Correção recomendada: declarar personalização de intervalos como Pós-V1, salvo nova mudança formal de escopo.

### `GATE-MED-005` — Fluxo de configuração/fuso não está formalizado

`RF-001`–`003`, `RN-001`–`005`, `Workspace`, V0.1 e `CT-001`/`002` cobrem a capacidade, mas os 22 fluxos não incluem um fluxo próprio para primeiro acesso, escolha de fuso, confirmação de mudança e recálculo da fila.

Não bloqueia a estrutura inicial, porém deve existir antes da interface definitiva da configuração.

### `GATE-MED-006` — Parâmetros operacionais ainda não fixados

Permanecem corretamente agendados, mas devem ser decididos antes dos respectivos gates:

- versões exatas de Python/Django/HTMX e ferramentas — início da V0.1;
- hardware do `TST-PERF` — antes do benchmark V0.4;
- duração do contexto transitório — antes de finalizar V0.3;
- expiração de recibos e política de contenção SQLite — antes da promoção V0.3/V0.5-A;
- janela de recorrência/queda e desempate de prioridade — antes de V0.5-B;
- autenticação e disponibilidade — antes de qualquer exposição remota.

## E.4 Baixos

### `GATE-BAI-001` — Referência incorreta em `RF-023`

O texto diz que inclusão manual em revisão usa `RF-044`; o requisito correto é `RF-045`.

### `GATE-BAI-002` — Referência incorreta em `FL-018`

O fluxo de determinar questão dominada referencia `FL-DEC-003`, que trata contexto transitório. A decisão relacionada à marcação automática de domínio é `FL-DEC-005`.

### `GATE-BAI-003` — Matriz de rastreabilidade do Plano de Testes é ampla demais

A seção 11.2 associa documentos inteiros a faixas de casos. Ela serve como resumo, mas não demonstra cobertura requisito por requisito. Uma matriz gerada a partir de metadados reduziria erros manuais.

# F. Contradições

| ID | Documentos | Afirmações incompatíveis | Severidade | Resolução recomendada |
|---|---|---|---|---|
| `CON-001` | Escopo × Modelo × Fluxos × Roadmap | Tags são V1/não mínimas, mas aparecem como MVP/V0.2. | Alta | Deferir tags para V0.5-A ou formalizar mudança completa. |
| `CON-002` | SDD × Modelo × Fluxos | SDD admite “substituída por reagendamento”; modelo mantém a mesma revisão pendente. | Média | Adotar `current_due_date` + evento, sem estado substituído. |
| `CON-003` | Escopo × Regras × Roadmap | Personalização de intervalos aparece como V1 eventual, mas a V1 continua fixa e adaptação é Pós-V1. | Média | Mover personalização para Pós-V1. |
| `CON-004` | RF × Fluxos | `RF-045` é inclusão de questão inicialmente correta; `FL-019` exige questão já dominada. | Alta | Criar fluxo separado ou ampliar formalmente com duas entradas distintas. |
| `CON-005` | Plano de Testes × Regras/SDD/Modelo | Casos citam IDs inexistentes ou semanticamente não relacionados. | Alta | Refazer somente a coluna de rastreabilidade e validar automaticamente. |
| `CON-006` | RF interno | `RF-023` aponta para `RF-044`, embora a capacidade seja `RF-045`. | Baixa | Corrigir referência. |
| `CON-007` | Fluxos interno | `FL-018` aponta para decisão de contexto transitório em vez da decisão de domínio. | Baixa | Trocar por `FL-DEC-005`. |

## Afirmações comparadas e consideradas consistentes

- Visão × Escopo: produto individual, foco em erros e revisão, sem IA obrigatória.
- Escopo × Roadmap: V0.4 é o primeiro MVP utilizável.
- Regras × SDD × Dados × Fluxos: D1/D7/D14/D30 sucessivos e ancorados na conclusão real.
- Requisitos × Dados: tentativa referencia versão da questão; correção não reescreve o passado.
- SDD × Roadmap: monólito, SQLite local, PostgreSQL condicionado e sem microserviços.
- RNFs × Testes: metas p95, `BCR-1`, segurança, acessibilidade e recuperação possuem estratégia de verificação.

# G. Lacunas

## G.1 Críticas

**Nenhuma.**

## G.2 Altas

| ID | Lacuna | Impacto | Momento-limite |
|---|---|---|---|
| `LAC-ALT-001` | Fluxo e testes de `RF-033` — categorias pessoais. | Consolidação pode corromper comparabilidade/histórico. | Antes de V0.5-A. |
| `LAC-ALT-002` | Fluxo e testes de `RF-045` — incluir questão inicialmente correta. | Implementação pode confundir inclusão manual com reabertura de domínio. | Antes de V0.5-A. |
| `LAC-ALT-003` | RF/regra/teste para tags, caso permaneçam na V0.2. | Funcionalidade sem contrato e sem critério de conclusão. | Antes de implementar tags. |
| `LAC-ALT-004` | Rastreabilidade correta dos 128 casos. | Teste pode validar regra diferente da pretendida. | Antes da funcionalidade relacionada. |

## G.3 Médias

| ID | Lacuna | Impacto | Momento-limite |
|---|---|---|---|
| `LAC-MED-001` | CTs próprios para critérios técnicos da V0.1. | Gate depende de critérios narrativos sem IDs executáveis. | Durante a primeira iteração V0.1. |
| `LAC-MED-002` | Fluxo de primeiro acesso/configuração/fuso. | Interface poderá omitir confirmação e impacto temporal. | Antes de fechar UI de V0.1/V0.3. |
| `LAC-MED-003` | Registro central do status dos pontos abertos. | Decisões resolvidas podem ser rediscutidas/implementadas errado. | Durante V0.1. |
| `LAC-MED-004` | Valores exatos de timeout/retry/expiração operacional. | Comportamento de concorrência fica pouco reproduzível. | Antes do gate V0.3. |

## G.4 Baixas

- Padronizar “aprovado”, “aceitar” e “status proposto” em decisões já congeladas.
- Acrescentar versionamento do próprio gerador de `BCR-1`.
- Criar verificador automático de IDs e referências em Markdown.

# H. Matriz de Rastreabilidade

Esta matriz agrupa capacidades coerentes. “LACUNA” significa ausência real ou ligação insuficiente; não foi criada relação artificial.

| Requisito | Regra | Fluxo | Componente/serviço | Entidade/dado | Teste principal | Situação |
|---|---|---|---|---|---|---|
| `RF-001`–`003` | `RN-001`–`005` | `FL-023` | `SDD-MOD-001`, `Clock`, `Calendar` | `User`, `Workspace` | `CT-001`, `002`, `129`, `135` | Coberta para V0.1; fila completa em V0.3 |
| `RF-004`–`008` | `RN-006`–`010` | `FL-001` | `SDD-MOD-002` | `Discipline`, `Subject`, `Subsubject` | `CT-003`, `004`, `010` | Coberta; corrigir citações |
| `RF-009`–`020` | `RN-011`–`020`, `085`–`090`, `093`–`094` | `FL-002`, `004`–`007` | `SDD-MOD-003`, `SDD-SVC-001` | `Question`, `QuestionRevision`, `Alternative`, `QuestionOrigin` | `CT-005`–`012`, `075` | Coberta; corrigir citações |
| **LACUNA: RF de tags** | **LACUNA** | `FL-002`, `005`, `020` | Questions/Search | `Tag`, `QuestionTag` | **LACUNA** | Escopo divergente |
| `RF-021`–`027` | `RN-021`–`027`, `091`–`096` | `FL-003`, `004`, `021` | `SDD-MOD-004`, `SDD-SVC-002`, `011` | `Attempt`, `OperationReceipt` | `CT-013`–`022`, `037`–`040`, `076`, `077` | Conteúdo coberto; links falhos |
| `RF-028`–`032` | `RN-028`–`032` | `FL-003`, `008` | `SDD-MOD-005` | `ErrorCategory`, `ErrorClassification`, revisão | `CT-014`, `017`–`019`, `051` | Conteúdo coberto; links falhos |
| `RF-033` | `RN-031` | **LACUNA:** gestão/consolidação | Errors | `ErrorCategory` | **LACUNA** | Alta |
| `RF-034`–`036` | `RN-033`–`040` | `FL-003`, `009`, `010`, `013` | `SDD-MOD-006`, `SDD-SVC-003`–`006` | `ReviewCycle`, `Review` | `CT-023`–`036` | Conteúdo coberto; links falhos |
| `RF-037`–`039` | `RN-040`, `041`, `063` | `FL-013` | ReviewStatusPolicy/selectors | `Review.current_due_date` | `CT-031`, `032`, `049` | Coberta; corrigir citações |
| `RF-040`–`044` | `RN-042`–`050` | `FL-009`–`011` | CompleteReviewService | `Review`, `Attempt`, recibo | `CT-030`, `037`–`042`, `093` | Coberta; corrigir citações |
| `RF-045` | Regra manual implícita | `FL-019` cobre somente dominada | ReviewCycleService | ciclo `origin_kind=MANUAL` | `CT-044` cobre somente dominada | **LACUNA** |
| `RF-046` | `RN-052`–`054` | `FL-012` | Reviews | `ReviewScheduleChange` | `CT-043` | Coberta; referência errada |
| `RF-047`–`056` | `RN-056`–`067`, `097`–`100` | `FL-014`–`016` | `SDD-MOD-007`, `SDD-SVC-007` | fatos + DTOs | `CT-045`–`054` | Conteúdo coberto; links falhos |
| `RF-057`–`061` | `RN-068`–`080` | `FL-018`, `019` | `SDD-MOD-008`, `SDD-SVC-008`, `009` | snapshots condicionais, eventos | `CT-055`–`069` | Coberta |
| `RF-062` | `RN-081`–`084` | `FL-017` | `SDD-SVC-010` | `PrioritySnapshot` condicional | `CT-070`–`072` | Coberta; acrescentar RF nos casos |
| `RF-063`–`066` | regras de escopo/filtros | `FL-020` | `SDD-MOD-009` | projeção de busca, `SavedFilter` V1 | `CT-085`–`087` | Coberta |
| `RF-067`, `068` | integridade e recuperação | `FL-022` técnico | DataManagement/infraestrutura | banco/manifesto | `CT-081`, `127`, `130`–`133`; casos ampliados `CT-082`–`084`, `113`–`117`, `122` nas fases próprias | Coberta para V0.1 |
| `RF-069`, `070` | portabilidade | `FL-022` | `SDD-MOD-010`, `SDD-SVC-012` | `CEI-EXPORT-1.0` | `CT-118`–`120` | Coberta |
| `RF-071` | `RN-085`, `089`–`096` | fluxos sensíveis | `SDD-MOD-011` | `AuditEvent` | casos dos fluxos + `CT-100` | Parcial; falta caso auditável dedicado |
| `RNF-001`–`005` | N/A | fluxos de leitura/escrita | selectors/índices | `BCR-1`, `BCR-2` | `CT-105`–`112` | Coberta |
| `RNF-012`–`024` | `RN-001` e fronteiras | comuns a todos | Accounts/Security/Audit | Workspace, sessão, logs | `CT-095`–`104` | Coberta |
| `RNF-025`–`033` | `RN-021`–`055`, `092`–`096` | `FL-003`, `006`, `010`, `021`, `022` | serviços transacionais | fatos, recibos, locks | `CT-037`–`040`, `073`–`084`, `122` | Coberta |
| `RNF-034`–`043` | regras de preservação | `FL-022` | DataManagement | backup/exportação | `CT-113`–`120` | Coberta |
| `RNF-044`–`050` | N/A | regras comuns de UI | apresentação | DOM/semântica | `CT-088`–`094`, `124`–`128` | Coberta |
| `RNF-051`–`058` | versionamento e separação | todos | camadas/módulos/pipeline | código, ADRs, migrações | `CT-081`–`084`, `122`, `123` | Parcial; faltam links individuais |
| `RNF-059`–`067` | regras de escala/tempo | filas, busca e dashboard | banco, selectors, Clock | `BCR-1`, datas IANA | `CT-035`, `036`, `085`, `086`, `105`–`112`, `128` | Coberta |
| `RNF-068`–`080` | N/A | transversais | Audit/Operations, testes | logs, correlação, fixtures | `CT-099`, `104`, `123`, `130`, `131`, `134`, `135`; demais nas fases próprias | Coberta para V0.1 |

# I. Avaliação da V0.1

## Objetivo da V0.1

Criar uma fundação executável no Windows que inicia, migra, testa, registra configuração segura e pode ser restaurada, sem implementar ainda o caderno de questões.

## Prontidão

**PRONTA PARA INICIAR COM RESSALVAS.**

A V0.1 é pequena o suficiente para uma fundação e possui resultado demonstrável. Ela não é uma versão de estudo real, o que está claramente comunicado.

## Funcionalidades incluídas

- repositório e projeto Django;
- dependências fixadas e ambientes separados;
- configurações por perfil;
- `User` customizado UUID e `Workspace` local padrão;
- escolha/persistência de fuso;
- `Clock` e `Calendar` controláveis;
- seed idempotente de categorias padrão;
- layout/navegação mínima;
- logging estruturado e sanitizado;
- rota de diagnóstico local;
- comando único de qualidade;
- migração limpa;
- backup/restauração mínima;
- README para Windows.

## Requisitos necessários

- `RF-001`–`003`;
- base técnica de `RF-067` e `RF-068`;
- `RNF-012`–`013`, `018`, `022`, `027`, `030`, `033`–`038`, `051`–`058`, `063`, `066`–`070`, `072`, `074`–`080`, conforme aplicabilidade da fundação.

## Regras necessárias

- `RN-001`–`005` para espaço e tempo;
- `RN-029` para códigos das categorias padrão semeadas;
- normalização somente onde houver dado correspondente;
- nenhuma regra de tentativa, revisão, domínio ou prioridade precisa ser implementada ainda.

## Componentes necessários

- configuração Django e perfis;
- Accounts/Workspace mínimo;
- adaptadores `Clock`/`Calendar`;
- ORM/migrações;
- logging/Audit operacional mínimo;
- scripts de seed e backup/restauração;
- health/diagnóstico local;
- pipeline/test runner.

## Entidades necessárias

- `User`;
- `Workspace`;
- `ErrorCategory` somente para o seed aprovado;
- demais entidades devem ser introduzidas na versão em que se tornam necessárias.

## Testes necessários

- `CT-001`, `CT-002`, `CT-073`, `CT-074`, `CT-081`;
- `CT-127` e `CT-129`–`CT-136`, formalizados pela errata 1.0.1 para instalação, seed, perfis/configuração, health local, backup/restauração mínima, logs, relógio e layout base;
- verificação de segredo/conteúdo em logs;
- migração do zero e banco isolado.

## Dependências

- Python e Git instalados;
- teste curto de compatibilidade para fixar versões;
- decisões de ferramentas de qualidade;
- ambiente sem dados reais;
- rastreabilidade dos casos V0.1 saneada; as referências de fases posteriores seguem o marco de `COR-P1-001`.

## O que explicitamente NÃO deve entrar

- `Question`, alternativas e cadastro completo;
- tentativa, classificação de erro, ciclo e revisão;
- dashboard e estatísticas;
- domínio, confiança e prioridade;
- busca/FTS;
- tags;
- API, autenticação remota e PostgreSQL de produção;
- IA, integrações, anexos, OCR, PWA ou notificações;
- criação dos onze módulos como pacotes vazios sem uso imediato.

## Redução recomendada

Não é necessário reduzir os resultados da V0.1, mas sua estrutura física deve ser incremental. Criar apenas os módulos realmente usados na V0.1 evita scaffolding vazio e mantém o objetivo de 1–2 semanas.

# J. Correções Obrigatórias Antes da Programação

## Para iniciar a V0.1

**Nenhuma correção P0 bloqueia a criação do repositório e da fundação.**

As seguintes ações devem integrar a primeira iteração, antes de declarar V0.1 concluída:

1. corrigir os links dos testes aplicáveis à V0.1;
2. criar IDs de teste para seed, health, perfis e backup mínimo;
3. fixar versões exatas da stack;
4. provar instalação limpa, migração e restauração.

## Antes de versões posteriores

- tags: decidir/deferir antes de implementá-las na V0.2;
- tentativa/revisão: corrigir toda rastreabilidade relacionada antes de V0.3;
- categorias pessoais e inclusão manual: criar fluxo/regras/testes antes de V0.5-A.

# K. Melhorias Recomendadas

1. Criar um registro único de decisões e pontos abertos com status `ABERTO`, `RESOLVIDO POR`, `ADIADO` ou `REMOVIDO`.
2. Gerar a matriz de rastreabilidade a partir de metadados próximos aos testes, evitando digitação manual de IDs.
3. Adicionar um linter documental que rejeite identificadores inexistentes.
4. Manter uma fixture pequena de versão anterior para testar migrações desde V0.2.
5. Criar orçamento de duração da suite e limite de testes instáveis.
6. Registrar ADR curto para cada decisão de V0.1: versões, CSS, backup SQLite e empacotamento Windows.
7. Revisar o tamanho da V0.5 após o piloto V0.4; checkpoints A/B/C não devem virar uma única entrega longa.

# L. Ordem Recomendada de Implementação

| Ordem | Entrega | Dependências | Evidência de saída |
|---:|---|---|---|
| 1 | Errata inicial e backlog V0.1 | Gate concluído | IDs/testes V0.1 vinculados e tags fora da V0.1 |
| 2 | Spike de compatibilidade e versões | Python/Git | `pyproject`/lock com versões reproduzíveis |
| 3 | Estrutura mínima Django e perfis | item 2 | dev/test/prod-local iniciam sem segredo no código |
| 4 | `User` UUID, `Workspace` e migração inicial | item 3 | migração limpa e isolamento testado |
| 5 | `Clock`/`Calendar` e fuso | item 4 | dois fusos/datas reproduzidos por testes |
| 6 | Seed idempotente de categorias | item 4 | duas execuções sem duplicação |
| 7 | Logging sanitizado e health local | itens 3–5 | rota local e logs sem conteúdo privado |
| 8 | Backup/restauração mínima SQLite | migração + workspace | checksum e restauração em diretório descartável |
| 9 | Layout/navegação base acessível | itens 3–4 | teclado, foco e estado inicial compreensível |
| 10 | Comando único de qualidade e CI | todos anteriores | lint, análise, testes e migrações bloqueiam falha |
| 11 | README/instalação Windows | build V0.1 | instalação limpa por instrução escrita |
| 12 | Gate e tag V0.1 | todos | demo de criação do espaço, fuso, health e recuperação |

Depois da V0.1, seguir o caminho já aprovado:

`taxonomia/questão versionada → tentativa → erro → ciclo/revisão → fila → métricas/dashboard → domínio/prioridade V1`.

# M. Checklist Final do Gate

| Item | Avaliação | Justificativa |
|---|---|---|
| Visão clara | ✅ APROVADO | Problema, público, valor, limites e evolução definidos. |
| Escopo fechado | ⚠️ APROVADO COM RESSALVAS | Tags e personalização de intervalos divergem de fases posteriores. |
| MVP definido | ✅ APROVADO | V0.4 e seu fluxo mínimo estão inequívocos. |
| Requisitos funcionais completos | ⚠️ APROVADO COM RESSALVAS | Tags sem RF e duas capacidades V1 sem fechamento. |
| Requisitos funcionais testáveis | ✅ APROVADO | Critérios de aceitação observáveis. |
| Requisitos não funcionais suficientes | ✅ APROVADO | 80 RNFs verificáveis e baseline de capacidade. |
| Regras de negócio consistentes | ✅ APROVADO | Núcleo temporal, histórico e fórmulas são coerentes. |
| Arquitetura compatível com requisitos | ✅ APROVADO | Monólito modular proporcional e testável. |
| Responsabilidades dos componentes claras | ✅ APROVADO | Camadas, módulos e serviços possuem fronteiras. |
| Modelo de dados suficiente | ✅ APROVADO | Entidades, cardinalidades, invariantes e histórico adequados. |
| Fluxos principais documentados | ⚠️ APROVADO COM RESSALVAS | Faltam configuração, categorias pessoais e inclusão manual própria. |
| Fluxos de erro considerados | ✅ APROVADO | Rollback, concorrência, abandono e arquivos inválidos cobertos. |
| Roadmap tecnicamente coerente | ⚠️ APROVADO COM RESSALVAS | Ordem é sólida; tags foram antecipadas e V0.5 é ampla. |
| V0.1 claramente delimitada | ✅ APROVADO | Objetivo, entregas, exclusões e critérios claros. |
| Testes suficientes | ⚠️ APROVADO COM RESSALVAS | Conteúdo amplo, mas rastreabilidade e alguns CTs V0.1 precisam correção. |
| Rastreabilidade aceitável | ⚠️ APROVADO COM RESSALVAS | Ligações existem, porém há IDs inexistentes e associações semânticas erradas. |
| Ausência de contradições críticas | ✅ APROVADO | Nenhuma contradição bloqueadora encontrada. |
| Ausência de lacunas críticas | ✅ APROVADO | Lacunas são altas/médias e têm momento de correção. |
| Tecnologias necessárias definidas | ⚠️ APROVADO COM RESSALVAS | Stack escolhida; versões exatas serão fixadas no início da V0.1. |
| Estratégia de persistência definida | ✅ APROVADO | ORM, migrações, SQLite e gatilho PostgreSQL definidos. |
| Estratégia de tratamento de erros definida | ✅ APROVADO | Taxonomia, exceções, feedback e rollback documentados. |
| Estratégia de logging definida | ✅ APROVADO | Estrutura, níveis, correlação e privacidade definidos. |
| Configuração do projeto definida | ✅ APROVADO | Perfis e parâmetros externos separados de regras congeladas. |
| Dependências externas conhecidas | ⚠️ APROVADO COM RESSALVAS | Categorias conhecidas; versões e ferramentas exatas ainda abertas. |
| Critérios de aceitação suficientes | ⚠️ APROVADO COM RESSALVAS | Suficientes no geral; faltam CTs próprios para alguns gates V0.1. |

# N. Overengineering

## Achados

### `OVER-001` — Criar todos os módulos antes de serem usados

O catálogo de onze módulos é adequado como mapa arquitetural, mas criar onze pacotes vazios na V0.1 geraria estrutura sem comportamento. Criar Accounts/Workspace, configuração e infraestrutura compartilhada primeiro; adicionar módulos por versão.

### `OVER-002` — Snapshots, FTS e PostgreSQL antecipados

Os documentos já mitigam corretamente esse risco ao condicioná-los a benchmark ou implantação. A auditoria confirma que não devem ser implementados preventivamente.

### `OVER-003` — Abstrações genéricas de repositório

O SDD já rejeita repositório genérico para todo CRUD. Manter interfaces apenas para tentativa, revisão, estatística, busca e exportação quando houver benefício real.

## Conclusão

Não há overengineering estrutural grave. O principal risco é transformar o mapa futuro em scaffolding antecipado.

# O. Underengineering

## Achados

### `UNDER-001` — Política operacional de contenção SQLite ainda qualitativa

Timeout, tentativas de repetição e mensagens precisam de valores e testes antes da V0.3.

### `UNDER-002` — CTs técnicos da V0.1 incompletos

Seed, health, configuração e recuperação mínima precisam de casos identificados.

### `UNDER-003` — Governança de rastreabilidade manual

Sem validação automática, IDs errados já entraram no documento aprovado. O linter documental deve ser parte da qualidade da V0.1.

## Conclusão

Persistência, erros, logging, validação e testes críticos não foram esquecidos. O underengineering está na operacionalização e na governança das ligações, não no desenho do produto.

# P. Dívida Técnica Previsível

| ID | Problema | Consequência | Quando aparece | Como evitar | Prioridade |
|---|---|---|---|---|---|
| `DIV-001` | Módulos vazios antecipados | Navegação e manutenção desnecessárias | V0.1/V0.2 | Criar por capacidade entregue | P2 |
| `DIV-002` | Lógica em views/ORM | Regras duplicadas e testes difíceis | V0.2/V0.3 | Services/policies e revisão de dependências | P1 |
| `DIV-003` | SQLite sem política medida | Falhas em duas abas e mensagens inconsistentes | V0.3 | Lock/version, transações curtas e `CT-111` corrigido | P1 |
| `DIV-004` | Referências documentais manuais | Testes ligados à regra errada | Desde V0.1 | Metadados e linter de IDs | P1 |
| `DIV-005` | Métricas em consultas distintas | Dashboard não reconcilia com drill-down | V0.4 | Selector autoritativo e DTO com denominador | P1 |
| `DIV-006` | FTS/snapshots prematuros | Invalidação e migração sem benefício | V0.4/V0.5 | Só adotar após benchmark | P2 |
| `DIV-007` | Retenção indefinida de recibos/auditoria | Crescimento e política inconsistente | V0.5 | Fechar retenção antes do checkpoint A | P1 |
| `DIV-008` | V0.5 como entrega única | Longo período beta e risco de regressão | Após MVP | Tratar A/B/C como marcos demonstráveis | P2 |

# Q. Plano de Correção

## P0 — bloqueia implementação

**Nenhuma correção P0.** A V0.1 pode começar.

## P1 — corrigir antes da funcionalidade relacionada

| ID | Documento/seção | Problema | Correção proposta | Documentos relacionados |
|---|---|---|---|---|
| `COR-P1-001` | Plano de Testes, seções 3, 9, 10 e 11 | IDs inexistentes e referências erradas | Corrigir somente rastreabilidade, preservando objetivos/esperados; validar todos os IDs | RFs, regras, SDD, modelo, fluxos |
| `COR-P1-002` | Plano de Testes, V0.1 | Falta de CTs para seed, health, perfis, instalação e backup mínimo | Criar casos antes de fechar a primeira iteração | Roadmap V0.1, RNFs |
| `COR-P1-003` | Escopo/Modelo/Fluxos/Roadmap | Tags em fases incompatíveis | Recomendado: remover da V0.2 e mover para V0.5-A; se mantidas, criar RF/RN/CT e mudança de escopo | Etapas 2, 3, 5, 7, 8, 9, 10 |
| `COR-P1-004` | Fluxos e Testes | `RF-045` confundido com reabertura dominada | Criar fluxo “incluir questão inicialmente correta em ciclo” e casos próprios | RFs, regras, modelo, roadmap |
| `COR-P1-005` | Fluxos e Testes | `RF-033` sem fluxo/testes de ciclo de vida | Definir criar/renomear/arquivar/consolidar e efeito histórico | Regras, modelo, roadmap |
| `COR-P1-006` | SDD 12.3 | Estado “substituída por reagendamento” contraditório | Manter mesma revisão `PENDING`; histórico em `ReviewScheduleChange` | Modelo, FL-012 |

## P2 — corrigir durante o desenvolvimento

| ID | Documento/seção | Problema | Correção proposta | Relacionados |
|---|---|---|---|---|
| `COR-P2-001` | RF-023 | Referência `RF-044` incorreta | Trocar por `RF-045` | Fluxos/Testes |
| `COR-P2-002` | FL-018 | Referência `FL-DEC-003` incorreta | Trocar por `FL-DEC-005` | Regras de domínio |
| `COR-P2-003` | Pontos abertos das etapas 3–8 | Itens resolvidos continuam abertos | Acrescentar status e decisão que resolveu | Todas as etapas |
| `COR-P2-004` | Fluxos | Configuração/fuso sem fluxo | Criar fluxo curto de primeiro acesso e alteração | RF-001–003, V0.1 |
| `COR-P2-005` | Escopo V1 | Personalização de intervalos órfã | Mover para Pós-V1 ou formalizar nova especificação | Regras, roadmap, testes |
| `COR-P2-006` | SDD/Plano | Parâmetros operacionais abertos | Fixar nos marcos já definidos | Roadmap |

## P3 — melhoria futura

| ID | Melhoria | Benefício |
|---|---|---|
| `COR-P3-001` | Gerar matriz de rastreabilidade automaticamente | Evita divergência entre código e Markdown. |
| `COR-P3-002` | Mutation testing seletivo | Mede força real das regras críticas. |
| `COR-P3-003` | Dashboard de saúde da suite | Controla duração, flakiness e cobertura. |
| `COR-P3-004` | Registro consolidado de ADRs/decisões | Facilita entrada no Codex e manutenção futura. |

# R. Status da Baseline

Como a decisão é **GO COM RESSALVAS**, o conjunto ainda não é declarado formalmente como **Baseline de Implementação 1.0 integral**.

Os dez documentos aprovados formam uma **baseline candidata**, suficiente para orientar a V0.1:

1. Visão do Projeto 1.0;
2. Escopo 1.0;
3. Requisitos Funcionais 1.0;
4. Requisitos Não Funcionais 1.0;
5. Regras de Negócio 1.0;
6. SDD 1.0;
7. Modelo de Dados 1.0;
8. Fluxos Principais 1.0;
9. Roadmap 1.0;
10. Plano de Testes 1.0.

Após concluir `COR-P1-001` a `COR-P1-006`, executar uma verificação curta de consistência e declarar a Baseline de Implementação 1.0. Mudanças posteriores em requisitos, regras, arquitetura, modelo de dados ou interfaces importantes deverão usar controle de mudança e análise de impacto.

---

# S. Registro da Etapa 0 — Saneamento da Baseline Aplicável à V0.1

## S.1 Escopo e decisões controladas

Esta execução trata somente a documentação necessária para iniciar a V0.1. Não implementa aplicação, não fixa versões da stack e não antecipa V0.2 ou fases posteriores.

| ID | Decisão/errata | Efeito |
|---|---|---|
| `ERR-V01-001` | O catálogo de testes passa de `CT-001`–`128` para `CT-001`–`136`; `CT-129`–`136` cobrem exclusivamente lacunas técnicas da V0.1. | Resolve `COR-P1-002` sem criar requisito de produto. |
| `ERR-V01-002` | `CT-127` passa a validar instalação limpa já na V0.1 e deixa de usar `RD-ABR-003` como rastreabilidade principal. | Instalação pelo README torna-se evidência da fundação; empacotamento continua aberto para V0.4. |
| `ERR-V01-003` | `CT-122` não se aplica à primeira release; `CT-123` executa somente capacidades existentes na versão. | Impede que funcionalidades futuras sejam exigidas no smoke V0.1. |
| `ERR-V01-004` | `FL-023` formaliza primeiro acesso, criação idempotente de `User`/`Workspace`/categorias e alteração de fuso. | Trata `COR-P2-004`; a reconciliação real de filas permanece para V0.3. |
| `ERR-V01-005` | Health V0.1 é diagnóstico local restrito, cobrindo aplicação e persistência sem revelar configuração. | Não antecipa observabilidade remota da V1. |
| `ERR-V01-006` | Backup/restauração V0.1 cobre banco vazio ou mínimo, manifesto e checksum em ambiente descartável. | Não equivale à exportação `CEI-EXPORT-1.0` nem à restauração pela interface. |
| `ERR-V01-007` | Logging V0.1 é operacional, estruturado e sanitizado; `AuditEvent` funcional persistente não é entidade obrigatória desta versão. | Mantém somente as entidades exigidas pelo Gate: `User`, `Workspace` e `ErrorCategory`. |
| `ERR-V01-008` | Versões de Python/Django/HTMX, ferramentas, estratégia CSS e demais parâmetros continuam decisões da Etapa 1 ou dos marcos já definidos. | A Etapa 0 não inicia spike nem congela tecnologia por iniciativa própria. |
| `ERR-V01-009` | Ficam definidos os nomes e as descrições canônicas iniciais das dez categorias padrão de `RF-029`; códigos permanecem imutáveis e textos podem evoluir sem troca de código. | Fecha a lacuna textual de `RF-029` sem criar funcionalidade ou alterar o escopo da V0.1. |

## S.2 Status das correções

| Correção | Status após Etapa 0 | Evidência/limite |
|---|---|---|
| `COR-P1-001` | **Concluída para a V0.1; pendente para a baseline integral.** | Referências aplicáveis corrigidas; matriz V0.1 criada; IDs futuros ainda serão corrigidos antes da funcionalidade relacionada. |
| `COR-P1-002` | **Concluída.** | `CT-129`–`CT-136` formalizados e `CT-127` antecipado. |
| `COR-P1-003` | Pendente, não bloqueia V0.1. | Decidir tags antes da V0.2; nenhuma tag entra na V0.1. |
| `COR-P1-004` | Pendente, não bloqueia V0.1. | Criar fluxo/testes de inclusão manual antes da V0.5-A. |
| `COR-P1-005` | Pendente, não bloqueia V0.1. | Criar fluxo/testes de categorias pessoais antes da V0.5-A. |
| `COR-P1-006` | Pendente, não bloqueia V0.1. | Corrigir estado de reagendamento antes da V0.5-A. |
| `COR-P2-003` | **Parcialmente tratada.** | Este registro centraliza o estado dos pontos V0.1; saneamento global das Etapas 3–8 continua pendente. |
| `COR-P2-004` | **Concluída.** | `FL-023` formaliza primeiro acesso e alteração de fuso. |
| `COR-P2-006` | Pendente no marco previsto. | Versões/ferramentas no início da Etapa 1; parâmetros de V0.3/V0.4/V0.5 permanecem em seus marcos. |

`COR-P2-001`, `COR-P2-002` e `COR-P2-005` não afetam a V0.1 e permanecem para o saneamento das capacidades relacionadas.

## S.3 Rastreabilidade final da V0.1

A matriz autoritativa detalhada está na seção 8.1 do Plano de Testes 1.0.1. O conjunto mínimo de gate é:

| Entrega | Requisitos/regras principais | Testes |
|---|---|---|
| Perfis, dependências e isolamento de testes | base de `RF-067`; `RNF-018`, `019`, `052`–`056`, `079`, `080` | `CT-099`, `104`, `127`, `130` |
| Usuário UUID, espaço e migração | `RF-001`, `067`; `RN-001`; `RNF-013`, `027`, `033` | `CT-001`, `073`, `074`, `081`, `129` |
| Primeiro acesso, fuso e relógio | `RF-002`, `003`; `RN-002`–`005`; `RNF-030`, `067`, `074` | `CT-002`, `135` |
| Categorias padrão | `RF-029`; `RN-029`; `RNF-027` | `CT-129` |
| Layout/configuração base | `RF-001`–`003`; `RNF-044`–`049`, `063`, `065`, `066` | `CT-002`, `136` |
| Logs e health local | base de `RF-067`, `068`; `RNF-018`, `022`, `068`–`072` | `CT-099`, `131`, `134` |
| Backup/restauração mínima | `RF-068`; `RNF-034`–`038`; parte técnica de `FL-022` | `CT-132`, `133` |
| Gate e instalação Windows | `RNF-053`, `056`, `058`, `080`; `RD-DEC-002` | `CT-081`, `104`, `123`, `127`, `129`–`136` |

## S.4 Resultado da Etapa 0

- Não existe P0 nem contradição crítica que bloqueie a Etapa 1.
- A V0.1 possui casos P0/P1 próprios para todos os critérios técnicos narrativos apontados pelo Gate.
- Tags, módulos futuros, tentativas, revisões, dashboard, domínio, prioridade, exportação V1, PostgreSQL e integrações permanecem fora da V0.1.
- A baseline integral 1.0 continua condicionada a `COR-P1-003`–`006` e ao restante de `COR-P1-001`; somente a baseline aplicável à V0.1 está saneada.
- A Etapa 1 pode iniciar mediante nova instrução, começando pela decisão de versões/ferramentas; nenhuma dessas decisões foi antecipada aqui.

---

# **PROJETO LIBERADO PARA IMPLEMENTAÇÃO**

**Escopo da liberação:** V0.1 — Fundação Executável, com as ressalvas e marcos de correção definidos neste relatório.

---

# T. Registro controlado — Etapa 0 da V0.2

Este registro, datado de 5 de setembro de 2026, preserva integralmente o
diagnóstico histórico do Gate e acrescenta o estado das pendências após
`ADR-010`.

## T.1 Erratas V0.2

| Errata | Resultado |
|---|---|
| `ERR-V02-001` | `Tag` e `QuestionTag` retiradas da V0.2 e adiadas para V0.5-A/V1. |
| `ERR-V02-002` | Faixa V0.2 corrigida para `RF-004`–`019`, `RF-063`, `RF-064` e recorte de `RF-065`; `RF-020` e `RF-066` ficam fora. |
| `ERR-V02-003` | Rastreabilidade/fase dos CTs V0.2 corrigida no Plano de Testes e consolidada em `ADR-010`. |
| `ERR-V02-004` | Recortes de `RF-016`–`019` e `FL-004`–`006` formalizados sem aprendizagem fictícia. |
| `ERR-V02-005` | `RF-065` limitado a disciplina, assunto e subassunto; capacidades futuras separadas. |
| `ERR-V02-006` | Gestão mínima de origem definida dentro do contexto da questão. |
| `ERR-V02-007` | Rascunho e conteúdo passam a usar revisões imutáveis conforme o Modelo. |
| `ERR-V02-008` | `CT-137`–`CT-144` formalizados. |
| `ERR-V02-009` | Contrato do futuro gate/migrations V0.2 definido sem enfraquecer a V0.1. |

## T.2 Status das correções do Gate

| Correção | Status após a Etapa 0 V0.2 | Evidência/limite |
|---|---|---|
| `COR-P1-001` | **Concluída para todas as capacidades da V0.2.** | Casos existentes corrigidos por semântica e fase; parcelas futuras permanecem explicitamente pendentes para seus marcos. A correção integral global ainda acompanha capacidades V0.3+. |
| `COR-P1-003` | **Concluída.** | Tags formalmente adiadas por `ERR-V02-001`; não há model, migration, fluxo obrigatório ou teste de tags na V0.2. |
| `COR-P1-004` | Pendente para V0.5-A. | Inclusão manual de questão correta em ciclo não pertence à V0.2. |
| `COR-P1-005` | Pendente para V0.5-A. | Gestão de categorias pessoais não pertence à V0.2. |
| `COR-P1-006` | Pendente para V0.5-A. | Reagendamento não pertence à V0.2. |

## T.3 Decisão de liberação

- Não existe P0/P1 documental aberto que impeça iniciar a Etapa 1 da V0.2.
- A liberação abrange somente **V0.2 — Etapa 1 — Taxonomia e migrations**.
- `Attempt`, respostas, erros, ciclos, revisões, fila, métricas, tags,
  SavedFilter, exclusão física, reativação e demais capacidades posteriores
  continuam proibidos.
- O gate V0.1 permanece a verificação de regressão até que o gate V0.2 seja
  implementado na etapa prevista.

# **V0.2 — ETAPA 1 DOCUMENTALMENTE LIBERADA**

**Limite:** a liberação não inicia a Etapa 1 automaticamente e não autoriza
qualquer funcionalidade V0.3 ou posterior.
