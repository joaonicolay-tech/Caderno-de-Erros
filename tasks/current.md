# V0.2 — Etapa 7 — Listagem, Busca e Filtros de Conteúdo

## Identificação

- Versão: V0.2.
- Etapa: 7.
- Nome: Listagem, Busca e Filtros de Conteúdo.
- Status: liberada / não iniciada.
- Execução: deve ocorrer em novo chat; esta liberação não inicia a etapa.

## Objetivo

Disponibilizar a consulta simples e somente leitura do catálogo de questões do
Workspace atual: listagem paginada, busca textual simples e filtros de estado e
taxonomia, com ordenação estável, estado vazio e acesso ao detalhe já existente.
Não introduzir fatos, filtros ou indicadores de aprendizagem.

## Escopo

- listar questões `ACTIVE` por padrão, com acesso explícito a `DRAFT` e
  `ARCHIVED`, distinguindo corretamente os três estados;
- mostrar identificação, conteúdo acadêmico e estado, permitindo abrir o detalhe
  correto sem alterar registros;
- implementar paginação funcional com ordenação e desempate estáveis, sem
  duplicação ou omissão entre páginas;
- permitir busca textual simples por palavra ou trecho no enunciado e, quando
  suportado pelo recorte implementado, na explicação; busca vazia restaura o
  comportamento padrão e a limpeza restaura a lista;
- aplicar somente filtros de disciplina, assunto e subassunto, com opções
  hierárquicas coerentes, filtros ativos visíveis, contagem correspondente e
  estado vazio para combinação sem resultado;
- aceitar estado como seleção de listagem de `RF-063`, sem tratá-lo como filtro
  de aprendizagem;
- garantir que toda leitura, referência de filtro e detalhe aberto permaneça no
  Workspace atual;
- criar os testes automatizados estritamente necessários para os CTs aplicáveis
  e a regressão do catálogo.

## Fora de escopo

- FTS/FTS5, busca semântica, alertas ou bloqueio de similaridade;
- `Tag`, `QuestionTag`, `SavedFilter`, salvar filtros e o `RF-066`;
- filtros de dificuldade ou origem, que podem ser exibidos mas não são filtros
  obrigatórios na V0.2;
- situação de revisão, resultado inicial, classificação de erro, tentativas,
  ciclos, revisões de aprendizagem, fila, histórico, métricas, dashboard,
  domínio ou prioridade;
- fixture sintética, recuperação integral e validação manual integral de
  acessibilidade de `CT-142`, reservadas à Etapa 8;
- qualquer model, migration, alteração de schema, dependência nova, API, PWA,
  OCR, anexos, importação, autenticação remota, commit, push, tag ou release;
- qualquer capacidade da Etapa 8 ou posterior.

## Fontes obrigatórias

- `docs/Caderno_de_Erros_Inteligente_Etapa_9_Roadmap (1).md`, §§5.1–5.7;
- `docs/ADR-010_Fronteira_Rastreabilidade_e_Dados_V0.2.md`, §§2.1–2.3,
  `ERR-V02-001` a `ERR-V02-009`, especialmente `ERR-V02-002`, `004`, `005` e
  §§5–6;
- `docs/Caderno_de_Erros_Inteligente_Etapa_3_Requisitos_Funcionais.md`,
  `RF-063`, `RF-064` e subconjunto V0.2 de `RF-065`;
- `docs/Caderno_de_Erros_Inteligente_Etapa_5_Regras_de_Negocio.md`,
  `RN-006`, `RN-007`, `RN-017`, `RN-018` e `RN-086`;
- `docs/Caderno_de_Erros_Inteligente_Etapa_8_Fluxos_Principais.md`, recorte
  V0.2 de `FL-020`;
- `docs/Caderno_de_Erros_Inteligente_Etapa_6_SDD.md`, `SDD-MOD-009` e a
  decisão de views finas/selectors de leitura;
- `docs/Caderno_de_Erros_Inteligente_Etapa_4_Requisitos_Nao_Funcionais.md`,
  `RNF-002`, `RNF-013`, `RNF-016`, `RNF-044`–`RNF-049`, `RNF-061`, `RNF-063`,
  `RNF-065` e `RNF-066`;
- `docs/ADR-003_Identidade_Workspace_e_Tempo_V0.1.md` para isolamento por
  Workspace; `docs/ADR-006_Interface_Acessivel_da_Fundacao_V0.1.md`; e
  `docs/ADR-008_Gate_Unico_de_Qualidade_V0.1.md`;
- `docs/Caderno_de_Erros_Inteligente_Etapa_10_Plano_de_Testes.md`, nos CTs
  abaixo.

## RFs, RNs, RNFs e fluxos aplicáveis

### Requisitos funcionais

- `RF-063`: listar ativas por padrão; permitir acesso explícito a rascunhos e
  arquivadas; distinguir estado, mostrar vazio e abrir o detalhe correto.
- `RF-064`: busca textual simples no próprio Workspace, com indicação de
  ausência e limpeza que restaura a lista; pesquisa semântica não é autorizada.
- `RF-065` (subconjunto V0.2): disciplina, assunto e subassunto, opções
  hierárquicas atualizadas, filtros ativos, total correspondente e vazio.

### Regras de negócio

- `RN-006`/`RN-007`: a hierarquia filtrada deve ser coerente, pertencer ao
  Workspace e manter o subassunto opcional vinculado ao assunto.
- `RN-017`: o estado aplicável é exclusivamente `DRAFT`, `ACTIVE` ou
  `ARCHIVED`; ativas são a listagem padrão.
- `RN-018`: não criar bloqueio, alerta ou comparação por similaridade textual.
- `RN-086`: a consulta não cria tentativa, revisão de aprendizagem ou métrica.

### Requisitos não funcionais

- `RNF-002`: busca/filtros válidos com meta p95 de até 2 s no `BCR-1`; a prova
  de carga integral pertence à fase indicada no Plano de Testes.
- `RNF-013` e `RNF-016`: isolamento/autorização por Workspace e validação de
  entradas, IDs e saídas.
- `RNF-044`–`RNF-049`, `RNF-063`, `RNF-065` e `RNF-066`: semântica, rótulos,
  foco/teclado, Chrome/Edge, responsividade e português/Unicode.
- `RNF-061`: paginação ou carregamento limitado; o teste de 10.000 questões é
  parcela de carga da V0.4, sem dispensar a paginação funcional desta etapa.

### Fluxo

- `FL-020` (recorte V0.2): listar paginado e ordenado de forma estável no
  Workspace; aplicar texto, estado e taxonomia; mostrar total, página, filtros
  ativos e vazio; remover filtros e abrir detalhe. Página inválida volta a uma
  página válida com aviso discreto, sem expor outro Workspace.

## Componentes existentes a reutilizar

- `Question`, `QuestionStatus`, `QuestionRevision`, `Discipline`, `Subject` e
  `Subsubject`;
- `get_question`, selectors de taxonomia e os QuerySets já restritos por
  `workspace_id`;
- workspace local, URLs e detalhe de questões já existentes;
- `base.html`, `app.css`, padrões de mensagens, templates e acessibilidade da
  fundação.

## Áreas prováveis de implementação

- novo módulo `search` de `SDD-MOD-009` somente quando a implementação iniciar,
  limitado à leitura de Questions/Taxonomy;
- selectors/projeções de leitura e testes focados de busca/listagem;
- views, URLs e templates de listagem de questões; `base.html`, `app.css` e
  `src/config/urls.py` apenas se indispensáveis à navegação autorizada;
- testes de selector, view, template e regressão do catálogo.

Nenhuma dessas áreas deve ser alterada por esta tarefa de preparação.

## Restrições

- não criar nem alterar migrations, models, schema ou entidades futuras;
- views permanecem finas e leitura passa por selectors/projeções; nenhuma
  operação de consulta poderá gravar dados;
- filtrar e buscar sempre a partir do Workspace no servidor; IDs fornecidos pelo
  cliente não autorizam atravessar Workspace;
- usar ORM, índices existentes e paginação; FTS só poderia ser considerado após
  violação medida de `RNF-002` e nova decisão formal;
- não antecipar qualquer filtro de aprendizagem, tags, filtros salvos ou
  capacidade da Etapa 8;
- não fazer commit, push, tag ou release sem autorização expressa.

## CTs e testes aplicáveis

- `CT-005` (parcela de rascunho recuperável, distinguível e fora da lista ativa);
- `CT-085` (parcela V0.2): texto com acentos, estado, filtros taxonômicos,
  limpeza, resultados estáveis e isolamento por Workspace;
- `CT-086` (parcela V0.2): paginação funcional, ordenação e desempate estáveis,
  sem duplicação ou omissão;
- `CT-095` e `CT-097`: isolamento de referências/saídas e escaping do conteúdo
  renderizado;
- `CT-142` (parcela automatizável): nomes, rótulos, filtros, foco, teclado e
  responsividade; validação manual integral continua na Etapa 8;
- regressão de cadastro, ativação, detalhe, edição, arquivamento e isolamento
  de Workspace; todos os caminhos P0/P1 aplicáveis devem permanecer cobertos.

`CT-087`, a carga de 10.000 questões de `CT-086`, `CT-106` e qualquer teste de
filtros de aprendizagem permanecem nas fases futuras indicadas.

## Critérios objetivos de aceite

- a lista padrão mostra somente questões `ACTIVE` do Workspace atual; `DRAFT` e
  `ARCHIVED` são acessíveis apenas pela seleção de estado e ficam distinguíveis;
- cada item apresenta identificação, conteúdo acadêmico e estado e abre somente
  o detalhe pertencente ao mesmo Workspace;
- busca por trecho existente, inclusive com acentos, retorna somente itens do
  Workspace; busca vazia/limpa restaura o padrão e ausência gera estado vazio;
- filtros de disciplina, assunto e subassunto funcionam isolados e combinados,
  não formam hierarquia inválida, exibem filtros ativos e total correto;
- nenhum filtro de revisão, resultado inicial, classificação de erro, tags,
  origem, dificuldade ou SavedFilter é criado;
- paginação possui ordenação e desempate determinísticos, sem duplicação ou
  omissão, e página fora do intervalo retorna a uma página válida com aviso;
- consulta não grava nem cria tentativa, ciclo, revisão de aprendizagem,
  métrica ou informação fictícia;
- nenhuma migration muda; `makemigrations --check --dry-run` permanece limpo;
  CTs/regressões aplicáveis passam, não existe P0/P1 aplicável aberto e o gate
  retorna exit code 0;
- ao encerrar, registrar evidência/estado e arquivar a tarefa sem iniciar a
  Etapa 8.

## Gate obrigatório

`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1`

Exit code diferente de 0 bloqueia a conclusão da Etapa 7.
