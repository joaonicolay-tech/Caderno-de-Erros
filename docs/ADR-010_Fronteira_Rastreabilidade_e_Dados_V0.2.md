# ADR-010 — Fronteira, Rastreabilidade e Dados da V0.2

| Campo | Valor |
|---|---|
| Status | Aprovada — decisão controlada da V0.2 |
| Data | 5 de setembro de 2026 |
| Versão documental | 1.0 |
| Marco | V0.2 — Etapa 0 — Saneamento e Baseline |
| Baseline anterior | `v0.1.0` (`cc7c382d2db8474eaee6005b71b7d01d40481611`) |
| Decisão | Catálogo de conteúdo liberado para implementação após o saneamento descrito neste ADR |

---

## 1. Contexto

A V0.1 foi formalmente promovida e permanece uma baseline imutável. A V0.2
expande o produto apenas até um catálogo experimental de conteúdo: taxonomia,
origem, questões objetivas textuais versionadas e consulta simples. Não existe
ainda ciclo de aprendizagem.

O Gate de Implementação registrou divergências históricas de fase e
rastreabilidade. Este ADR resolve somente as divergências aplicáveis à V0.2,
sem apagar o diagnóstico original, reescrever a V0.1 ou antecipar capacidades
posteriores.

## 2. Decisão de escopo

### 2.1 Capacidades incluídas

| Capacidade | RF | RN principal | RNF principal | Fluxo | Entidades/serviço | Testes principais | Parcela futura |
|---|---|---|---|---|---|---|---|
| Taxonomia: criar, consultar e editar | `RF-004`–`RF-007` | `RN-006`–`RN-008` | `RNF-013`, `RNF-016`, `RNF-027`, `RNF-031`, `RNF-066` | `FL-001` | `Discipline`, `Subject`, `Subsubject`; Taxonomy services/selectors | `CT-003`, `CT-004`, `CT-137` | Métricas por classificação: V0.4; exclusão: V1 |
| Arquivar taxonomia | `RF-008` | `RN-009` | `RNF-013`, `RNF-027`, `RNF-031` | `FL-001` | Taxonomy service | `CT-137` | Exclusão física/migração de vínculos: V1 |
| Rascunho e ativação | `RF-009`, `RF-010` | `RN-006`, `RN-007`, `RN-011`, `RN-012`, `RN-017` | `RNF-003`, `RNF-007`, `RNF-010`, `RNF-013`, `RNF-016`, `RNF-027`, `RNF-032` | `FL-002` | `Question`, `QuestionRevision`; `QuestionCommandService` | `CT-005`, `CT-006` | Prática, contagens e revisões: V0.3/V0.4 |
| Alternativas e gabarito | `RF-011`, recorte de `RF-018` | `RN-012`, `RN-013`, recorte de `RN-020` | `RNF-016`, `RNF-027`, `RNF-028`, `RNF-031`, `RNF-032`, `RNF-076` | `FL-002`, `FL-005` | `QuestionRevision`, `Alternative`; version policy | `CT-007`, `CT-008`, `CT-075`, `CT-140` | Bloqueio após tentativa: V0.3; correção auditável: V1 |
| Origem | `RF-012`, `RF-015`, `RF-017` | `RN-014`, `RN-019`, `RN-086` | `RNF-013`, `RNF-016`, `RNF-027`, `RNF-031`, `RNF-066`, `RNF-074` | `FL-002`, `FL-005` | `Board`, `Exam`, `Source`, `QuestionOrigin`; OriginCatalogService | `CT-138`, `CT-139` | Análises e filtros não aprovados: versões posteriores |
| Dificuldade | `RF-013`, `RF-015`, `RF-017` | `RN-015`, `RN-019`, `RN-086` | `RNF-016`, `RNF-066` | `FL-002`, `FL-005` | `Question` | `CT-139` | Uso em métricas/filtro não é requisito V0.2 |
| Cadastro rápido | `RF-014` | `RN-011`–`RN-013`, `RN-016` | `RNF-003`, `RNF-007`, `RNF-008`, `RNF-010`, `RNF-044`–`RNF-049`, `RNF-065` | `FL-002` | `QuestionCommandService`, forms | `CT-011`, `CT-094`, `CT-124`, `CT-142` | Atalho/modelo de preenchimento: V1 |
| Enriquecimento e edição | `RF-015`, recorte de `RF-017` e `RF-018` | `RN-016`, `RN-019`, `RN-020`, `RN-086` | `RNF-007`, `RNF-010`, `RNF-016`, `RNF-028`, `RNF-031`, `RNF-032` | recorte de `FL-005` | `QuestionCommandService`, version policy | `CT-008`, `CT-140`, `CT-144` | Efeitos sobre tentativas/métricas: V0.3/V0.4 |
| Detalhe | recorte de `RF-016` | `RN-014`–`RN-017` | `RNF-013`, `RNF-016`, `RNF-044`–`RNF-049`, `RNF-063`, `RNF-065`, `RNF-066` | recorte de `FL-004` | Question selectors | `CT-139`, `CT-142` | Linha do tempo de aprendizagem: V0.3/V0.4 |
| Arquivar questão | recorte de `RF-019` | `RN-017`, recorte de `RN-087` | `RNF-010`, `RNF-013`, `RNF-027`, `RNF-028`, `RNF-031`, `RNF-032` | recorte de `FL-006` | Question archive service | parcela V0.2 de `CT-010` | Suspensão de ciclo/revisão/fila: V0.3 |
| Lista e estados | `RF-063` | `RN-017` | `RNF-013`, `RNF-044`–`RNF-049`, `RNF-061`, `RNF-063`, `RNF-065`, `RNF-066` | recorte de `FL-020` | Search selectors | `CT-005`, parcela V0.2 de `CT-085`, `CT-086`, `CT-142` | Consultas analíticas: V0.4 |
| Busca textual simples | `RF-064` | N/A | `RNF-002`, `RNF-013`, `RNF-016`, `RNF-061`, `RNF-066` | recorte de `FL-020` | ORM SearchBackend/selector | parcela V0.2 de `CT-085` | FTS somente após benchmark |
| Filtros taxonômicos | recorte de `RF-065` | `RN-006`–`RN-009` | `RNF-002`, `RNF-013`, `RNF-061`, `RNF-066` | recorte de `FL-020` | Search selectors | parcela V0.2 de `CT-085` | Revisão/resultado/erro: V0.4; `RF-066`: V0.5-A/V1 |
| Integridade, migração e recuperação | base de `RF-067`, `RF-068` | N/A | `RNF-018`, `RNF-019`, `RNF-027`, `RNF-033`, `RNF-034`, `RNF-036`, `RNF-038`, `RNF-052`–`RNF-058`, `RNF-076`, `RNF-078`–`RNF-080` | parte técnica de `FL-022` | migrations, gate, backup | `CT-073`–`CT-075`, `CT-081`, `CT-082`, `CT-122`, `CT-123`, `CT-143` | Capacidades futuras entram apenas em seus marcos |

### 2.2 Entidades aprovadas para a V0.2

- `Discipline`, `Subject`, `Subsubject`;
- `Board`, `Exam`, `Source`;
- `Question`, `QuestionRevision`, `Alternative`, `QuestionOrigin`.

### 2.3 Entidades e capacidades adiadas

Não serão criadas na V0.2:

- `Tag`, `QuestionTag` — V0.5-A/V1, após RF, RN e CT próprios;
- `Attempt` — V0.3;
- `ErrorClassification`, `ErrorClassificationRevision` — V0.3 ou posterior;
- `ReviewCycle`, `Review` — V0.3;
- `ReviewScheduleChange` — V1;
- `SavedFilter` — V0.5-A/V1;
- entidades de analytics, domínio, confiança, prioridade e snapshots — V0.4/V0.5/V1;
- demais entidades de aprendizagem V0.3+.

Também ficam proibidos: responder questão, calcular resultado, classificação de
erro, categorias pessoais, D1/D7/D14/D30, fila, histórico de aprendizagem,
dashboard, métricas, domínio, prioridade, correção pós-tentativa, exclusão
física, reativação, FTS/FTS5, OCR, anexos, importação em massa, API, PWA e
autenticação remota.

## 3. Erratas controladas

### `ERR-V02-001` — Tags fora da V0.2

`Tag` e `QuestionTag` não pertencem à V0.2. Menções anteriores a tags nas
funcionalidades, critérios e recortes V0.2 de `FL-002`, `FL-005` e `FL-020` são
inaplicáveis. As definições podem permanecer como desenho futuro V0.5-A/V1,
mas nenhum RF, RN, CT, módulo, model ou migration de tags será criado agora.

Esta decisão resolve `COR-P1-003`.

### `ERR-V02-002` — Faixa funcional

A faixa autoritativa da V0.2 é `RF-004`–`RF-019`, `RF-063`, `RF-064` e o
subconjunto de `RF-065` definido neste ADR. `RF-020` permanece V1. `RF-066` e
`SavedFilter` não pertencem à V0.2.

### `ERR-V02-003` — Rastreabilidade dos testes

A matriz da seção 6 deste ADR e o catálogo corrigido do Plano de Testes são a
leitura autoritativa para os CTs V0.2. Casos mistos não ganham entidades
fictícias: sua parcela futura permanece não executável até a fase indicada.

### `ERR-V02-004` — Recortes parcialmente futuros

- `RF-016`/`FL-004`: V0.2 mostra conteúdo e metadados atuais, estado, origem,
  dificuldade e revisões de conteúdo; não mostra tentativa, revisão de
  aprendizagem, ciclo, fila ou indicadores.
- `RF-017`/`FL-005`: V0.2 edita conteúdo, hierarquia, origem e dificuldade e
  preserva `QuestionRevision`; efeitos sobre tentativas, dashboard e métricas
  não são executáveis.
- `RF-018`/`FL-005`: V0.2 permite e versiona alteração crítica somente no
  estado sem tentativa. O bloqueio após tentativa será comprovado na V0.3 e a
  correção auditável continuará V1.
- `RF-019`/`FL-006`: V0.2 confirma, marca `ARCHIVED`, retira da lista ativa e
  preserva revisões de conteúdo. Suspender ciclo, revisão pendente e fila é
  V0.3.

### `ERR-V02-005` — Subconjunto de `RF-065`

São obrigatórios somente filtros por disciplina, assunto e subassunto,
atualização hierárquica das opções, indicação de filtros ativos, estado vazio e
contagem correspondente. `ACTIVE`, `DRAFT` e `ARCHIVED` pertencem a `RF-063`;
busca textual e sua limpeza pertencem a `RF-064`.

Situação de revisão, resultado inicial, classificação de erro, métricas, tags,
filtros salvos e filtros genéricos de `RF-066` não entram. Origem e dificuldade
podem ser exibidas, mas não são filtros obrigatórios sem mudança formal.

### `ERR-V02-006` — Gestão mínima de origem

`Board`, `Exam`, `Source` e `QuestionOrigin` suportam criação e reuso no
contexto do cadastro/edição de questão. Não haverá módulo funcional
independente de administração de origem.

- nomes usam `name_key`: trim, espaços internos reduzidos, normalização Unicode
  e comparação sem diferença de caixa, preservando acentos;
- todas as entidades e referências pertencem ao mesmo `Workspace`;
- `reference_year`/`Exam.year` aceitam 1900 até ano corrente do Workspace + 2;
  o mínimo é constraint estática e o limite superior dinâmico usa
  `Clock`/`Calendar` no serviço;
- origem é opcional e não bloqueia ativação;
- `QuestionOrigin` é 0..1 por questão e inexiste quando nenhum dado foi
  informado;
- `exam_id` e `board_id` não coexistem; com prova, a banca deriva de `Exam`;
- `Source`, `Exam` e `Board` são opcionais, com FKs protegidas e validação de
  pertencimento no serviço.

### `ERR-V02-007` — Rascunho e versionamento

A política é compatível com `MD-DEC-004`, `MD-DEC-006` e as invariantes das
seções 6.4–6.7 do Modelo de Dados:

- toda persistência de conteúdo versionável cria `QuestionRevision` imutável;
- edição posterior cria nova revisão; nenhuma revisão anterior é sobrescrita;
- alternativas pertencem exclusivamente à revisão;
- `correct_alternative_id` aponta para alternativa da própria revisão;
- `(question_id, version_number)` é único e há uma só revisão corrente;
- rascunho apenas com `draft_title` pode existir sem revisão;
- ao persistir enunciado, alternativas, explicação, pegadinha ou observações,
  passa a existir revisão, mesmo enquanto a questão estiver `DRAFT`;
- a versão corrente é trocada atomicamente; falha preserva a corrente anterior.

Não é necessário introduzir estado de publicação ou tornar revisão mutável.

### `ERR-V02-008` — Casos `CT-137` a `CT-144`

Os oito casos são formalizados no catálogo canônico do Plano de Testes. Eles
preenchem as lacunas de taxonomia, origem, detalhe, edição crítica pré-tentativa,
fixture, acessibilidade, recuperação e não bloqueio semântico.

### `ERR-V02-009` — Gate e migrations

- migrations V0.1 são imutáveis e seus hashes continuam protegidos;
- migrations V0.2 serão registradas em manifesto próprio quando existirem;
- o gate V0.2 testará banco vazio e upgrade `v0.1.0 → V0.2`;
- o manifesto V0.2 deverá separar hashes históricos protegidos dos hashes da
  release corrente;
- `quality/v01-gate.json` e `scripts/verify_v01.py` continuam utilizáveis para
  a própria baseline V0.1;
- o gate V0.2 poderá usar verificador novo/parametrizado, sem reduzir as
  verificações de IDs, links, evidências, cobertura e migrations;
- nesta Etapa 0 não se cria o gate final nem qualquer migration.

## 4. Ordem congelada das migrations futuras

1. `taxonomy/0001_initial`: `Discipline`, `Subject`, `Subsubject`; depende de
   `accounts/0001_initial`.
2. `questions/0001_origin_catalog`: `Board`, `Exam`, `Source`; depende de
   `accounts/0001_initial`.
3. `questions/0002_question_catalog`: `Question`, `QuestionRevision`,
   `Alternative`, `QuestionOrigin`; depende das duas anteriores. Criará
   `QuestionRevision`, depois `Alternative`, e só então adicionará o FK
   `correct_alternative_id`, seguido das constraints e índices finais.

As FKs de referências históricas usam `PROTECT`. Constraints SQLite cobrirão
estados, faixas estáticas, unicidades e cardinalidades expressáveis. Mesmo Workspace,
hierarquia completa/ativa, validade da questão ativa e gabarito pertencente à
revisão são também invariantes obrigatórias do serviço transacional, pois não
podem depender exclusivamente de `CHECK` entre tabelas no SQLite.

Fixture de demonstração não será data migration e nunca será carregada
automaticamente em dados reais.

## 5. Arquitetura de implementação aprovada

- `SDD-MOD-002` será o módulo `taxonomy`.
- `SDD-MOD-003` será o módulo `questions` e abrigará também origem.
- `SDD-MOD-009` será criado somente quando a busca for implementada; lerá
  somente Questions/Taxonomy na V0.2.
- comandos de questão passam pelo `SDD-SVC-001`/`QuestionCommandService`;
  origem terá serviço interno do módulo Questions.
- selectors produzem projeções de leitura; views permanecem finas.
- busca inicial usa ORM, índices e paginação. FTS depende de violação medida de
  `RNF-002` e nova decisão.
- nenhum módulo futuro vazio será criado.

## 6. Matriz autoritativa dos testes existentes

| CT | Rastreabilidade V0.2 | Execução V0.2 | Parcela futura |
|---|---|---|---|
| `CT-003` | `RF-004`–`RF-006`; `RN-008`; `FL-001`; `SDD-MOD-002` | Integral | Nenhuma |
| `CT-004` | `RF-005`–`RF-007`; `RN-006`, `RN-007`; `FL-001`, `FL-002`; `SDD-MOD-002`, `SDD-MOD-003` | Integral | Nenhuma |
| `CT-005` | `RF-009`, `RF-063`; `RN-011`, `RN-017`; `FL-002`, recorte de `FL-020` | Rascunho recuperável, distinguível e fora da lista ativa | Tentativa: V0.3; métricas: V0.4 |
| `CT-006` | `RF-009`–`RF-011`, `RF-014`; `RN-006`, `RN-007`, `RN-011`–`RN-013`; `FL-002` | Integral | Nenhuma |
| `CT-007` | `RF-010`, `RF-011`; `RN-012`, `RN-013`; `FL-002`; `MD-DEC-006` | Integral | Proteção durante resposta: V0.3 |
| `CT-008` | `RF-015`, `RF-017`, recorte de `RF-018`; `RN-016`, `RN-019`, `RN-020`, `RN-086`; `FL-005`; `MD-DEC-004` | Integral no estado sem tentativa | Pós-tentativa: `CT-009`, V0.3 |
| `CT-009` | `RF-018`; `RN-020`; `FL-005`; Question/Attempt | Não executável | Execução efetiva V0.3 |
| `CT-010` | `RF-019`; `RN-017`, `RN-087`; recorte de `FL-006` | Confirmação, `ARCHIVED`, saída da lista ativa e revisões preservadas | Tentativas/ciclo/revisão/fila: V0.3 |
| `CT-011` | `RF-014`; `RN-011`–`RN-013`, `RN-016`; `FL-002`; `SDD-SVC-001` | Integral | Nenhuma |
| `CT-012` | `RNF-016`, `RNF-066`; Modelo §3.6; `FL-002`, `FL-005` | Integral | Exportação Unicode: V1 |
| `CT-073` | `RNF-027`; modelo físico V0.2 | Integral | Ampliado por entidade em cada versão |
| `CT-074` | `RNF-013`; `MD-DEC-003`; entidades V0.2 | Integral | Ampliado por entidade em cada versão |
| `CT-075` | `RF-015`, `RF-017`, `RF-018`; `RN-019`, `RN-020`; `MD-DEC-004`; Modelo §6.6 | Integral | Nenhuma |
| `CT-081` | `RNF-033`, `RNF-057` | Banco vazio V0.2 | Reexecutado em cada versão |
| `CT-082` | `RNF-033`; upgrade `v0.1.0 → V0.2` | Integral | Reexecutado em cada versão |
| `CT-085` | `RF-063`–`RF-065`; recorte de `FL-020`; `RNF-002` | Texto, estado e taxonomia | Filtros de aprendizagem/carga: V0.4 |
| `CT-086` | `RF-063`; `RNF-061`; recorte de `FL-020` | Paginação funcional e ordenação estável | Carga de 10.000: V0.4 |
| `CT-087` | `RF-066`; `SavedFilter` | Não executável | V0.5-A/V1 |
| `CT-094` | `RF-014`; `RNF-007`; `FL-002`, `FL-005` | Integral | Nenhuma |
| `CT-095` | `RNF-012`, `RNF-013`; todas as referências V0.2 | Integral | Contínuo |
| `CT-096` | `RNF-017`; mutações V0.2 | Integral | Contínuo a partir da V0.2 |
| `CT-097` | `RNF-016`; conteúdo V0.2 renderizado | Integral | Contínuo a partir da V0.2 |
| `CT-098` | `RNF-012`–`RNF-015` | Não aplicável ao local estrito | Antes de implantação remota |
| `CT-099` | `RNF-018` | Integral | Contínuo |
| `CT-104` | `RNF-019`, `RNF-080` | Integral | Contínuo |
| `CT-122` | `RNF-033`, `RNF-057` | Upgrade desde V0.1 | Cada release posterior |
| `CT-123` | `RNF-080`; matriz de capacidades V0.2 | Integral e sensível à fase | Cada release |
| `CT-124` | `RF-014`; `RNF-006`, `RNF-007` | Integral | Repetição V0.4 |

Todos os CTs V0.1 permanecem na regressão, sem serem reclassificados como
funcionalidade V0.2. `CT-127` mantém a fase documental V0.1 e sua repetição
formal em V0.4/V1; a instalação/migração V0.2 é coberta por `CT-081`, `CT-082`,
`CT-122` e `CT-123`.

## 7. Critério de liberação da Etapa 1

A Etapa 1 — Taxonomia e migrations está liberada quando:

- este ADR e as nove erratas estiverem presentes nos documentos afetados;
- `COR-P1-001` estiver resolvido para a V0.2 e `COR-P1-003` concluído;
- os validadores documentais e o gate V0.1 continuarem verdes;
- os hashes das migrations V0.1 permanecerem iguais;
- não existir código, módulo ou migration V0.2 criado durante a Etapa 0;
- não houver P0/P1 documental aberto aplicável ao início da taxonomia.
