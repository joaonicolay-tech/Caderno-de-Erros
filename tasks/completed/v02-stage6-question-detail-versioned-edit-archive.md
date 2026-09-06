# V0.2 — Etapa 6 — Detalhe, Edição Versionada e Arquivamento de Questões

## Identificação

- Versão: V0.2.
- Etapa: 6.
- Nome: Detalhe, Edição Versionada e Arquivamento de Questões.
- Status: concluída.
- Execução: realizada em novo chat, conforme o fluxo operacional.

## Objetivo

Disponibilizar o recorte V0.2 de consulta, enriquecimento/edição e
arquivamento de questões do catálogo, com detalhe fiel ao conteúdo persistido,
revisões imutáveis, controle de concorrência e isolamento por Workspace. A
etapa não introduz tentativa, ciclo ou informação fictícia de aprendizagem.

## Escopo

- criar o detalhe somente-leitura para questão `DRAFT`, `ACTIVE` ou `ARCHIVED`,
  mostrando estado, classificação acadêmica, origem, dificuldade, conteúdo
  atual, campos opcionais como “não informado” e histórico de revisões;
- permitir editar hierarquia válida, dificuldade, origem, enunciado,
  alternativas, gabarito, explicação, pegadinha e observações de questão não
  arquivada, usando `lock_version` e o `QuestionCommandService`;
- criar `QuestionRevision` imutável ao alterar conteúdo versionável, preservando
  revisões/alternativas anteriores; metadados e origem usam operações próprias;
- permitir alternativas/gabarito somente no estado estrutural sem `Attempt`,
  sempre em nova revisão válida;
- apresentar confirmação, revalidar estado/lock e marcar a questão como
  `ARCHIVED`, preservando origem e revisões de conteúdo;
- integrar somente a navegação mínima entre cadastro/rascunho e detalhe,
  edição/arquivamento; não criar listagem, busca, paginação ou filtros;
- aplicar Forms, views finas, PRG, CSRF, escaping e feedback fiel, preservando
  entrada corrigível e a baseline acessível;
- criar testes de serviço, selector, form, view e template dos caminhos desta etapa.

## Fora de escopo

- lista pesquisável, busca textual, paginação e filtros: Etapa 7;
- fixture sintética, recuperação integral e validação manual integral de
  acessibilidade de `CT-142`: Etapa 8;
- `Attempt`, resposta, resultado, classificação de erro, ciclo, revisão de
  aprendizagem, fila, histórico de aprendizagem, métricas, dashboard, domínio
  ou prioridade;
- bloqueio de alteração crítica após tentativa (V0.3) e correção auditável
  (V1); não existe `Attempt` na V0.2;
- suspensão de ciclo, revisão pendente ou fila no arquivamento;
- exclusão física/de rascunho, reativação, administração independente de
  origem, tags, `SavedFilter`, FTS/FTS5, OCR, anexos, importação, API, PWA ou
  autenticação remota;
- novos models, schema ou migrations.

## Fontes obrigatórias

- `docs/Caderno_de_Erros_Inteligente_Etapa_9_Roadmap (1).md`, §§5.1–5.7;
- `docs/ADR-010_Fronteira_Rastreabilidade_e_Dados_V0.2.md`, §§2.1–2.3,
  `ERR-V02-001` a `ERR-V02-009`, especialmente `ERR-V02-004`/`007`, e §§5–6;
- `docs/Caderno_de_Erros_Inteligente_Etapa_3_Requisitos_Funcionais.md`,
  `RF-015`–`RF-019`, conforme o recorte V0.2 do ADR-010;
- `docs/Caderno_de_Erros_Inteligente_Etapa_5_Regras_de_Negocio.md`,
  `RN-006`, `RN-007`, `RN-014`–`RN-020`, `RN-086` e recorte de `RN-087`;
- `docs/Caderno_de_Erros_Inteligente_Etapa_8_Fluxos_Principais.md`, recortes
  V0.2 de `FL-004`, `FL-005` e `FL-006`;
- `docs/Caderno_de_Erros_Inteligente_Etapa_6_SDD.md`, `SDD-MOD-003`,
  `SDD-SVC-001`, `SDD-ADR-009` e §32;
- `docs/Caderno_de_Erros_Inteligente_Etapa_4_Requisitos_Nao_Funcionais.md`,
  `RNF-007`, `010`, `013`, `016`, `017`, `027`, `028`, `031`, `032`,
  `044`–`049`, `063`, `065`, `066` e `074`;
- `docs/ADR-003_Identidade_Workspace_e_Tempo_V0.1.md`, nos recortes de
  Workspace, autorização e tempo; `docs/ADR-006_Interface_Acessivel_da_Fundacao_V0.1.md`;
  `docs/ADR-008_Gate_Unico_de_Qualidade_V0.1.md`;
- `docs/Caderno_de_Erros_Inteligente_Etapa_10_Plano_de_Testes.md`, nos CTs
  desta tarefa.

## RF, RN, RNF e fluxos aplicáveis

### Requisitos funcionais

- `RF-015`: enriquecer questão existente sem criar tentativa; o conteúdo aparece
  no detalhe e em revisões posteriores.
- `RF-016`: consultar conteúdo/metadados, estado e revisões sem alterar dados
  nem criar valores ausentes fictícios.
- `RF-017`: editar metadados e conteúdo não crítico com hierarquia válida.
- `RF-018`: permitir alternativas/gabarito apenas antes de tentativa e criar
  revisão válida; a parcela pós-tentativa não é executável nesta versão.
- `RF-019`: confirmar arquivamento, preservar conteúdo/revisões e manter a
  questão consultável; efeitos de aprendizagem são futuros.

### Regras de negócio

- `RN-006`/`RN-007`: taxonomia ativa, coerente e do Workspace; subassunto é
  opcional e pertence ao assunto.
- `RN-014`/`RN-015`: origem e dificuldade opcionais, porém válidas quando
  informadas.
- `RN-016`, `RN-019` e `RN-086`: edição/enriquecimento não cria tentativa,
  revisão de aprendizagem ou métrica; conteúdo versionável gera revisão.
- `RN-017`: somente `DRAFT`, `ACTIVE` e `ARCHIVED`; `RN-018`: não bloquear
  similaridade semântica.
- `RN-020`: alteração crítica apenas sem tentativa e sempre troca a revisão
  corrente atomicamente na V0.2.
- `RN-087` (recorte V0.2): arquivamento preserva catálogo e não oferece
  reativação, ciclo, fila ou pendência fictícia.

### Requisitos não funcionais

- preservar entrada, feedback contextual e ausência de confirmação falsa
  (`RNF-007`, `RNF-010`, `RNF-032`);
- isolar IDs e leituras/escritas por Workspace, validar entrada/integridade e
  usar CSRF/escaping (`RNF-013`, `RNF-016`, `RNF-017`, `RNF-027`);
- manter histórico imutável, operação atômica e concorrência otimista
  (`RNF-028`, `RNF-031`);
- cumprir semântica, rótulos, erros, foco, teclado, responsividade, navegadores
  e português/Unicode (`RNF-044`–`049`, `RNF-063`, `065`, `066`), e o limite
  temporal de origem com `Clock`/`Calendar` se a origem for alterada (`RNF-074`).

### Fluxos

- `FL-004` (V0.2): detalhe somente leitura de conteúdo/metadados, estado,
  origem, dificuldade e revisões, sem linha do tempo de aprendizagem.
- `FL-005` (V0.2): carregar estado/lock, validar edição e trocar revisão quando
  aplicável, preservando a anterior.
- `FL-006` (V0.2): confirmar/arquivar atomicamente, mantendo detalhe e
  revisões, sem criar ou suspender entidades futuras.

## Componentes existentes a reutilizar

- `Question`, `QuestionRevision`, `Alternative`, `QuestionOrigin`, `Board`,
  `Exam`, `Source`, `Discipline`, `Subject` e `Subsubject`;
- `QuestionCommandService.save_revision`, `update_question_metadata`,
  `set_question_origin` e `archive_question`, exceções, inputs e validadores;
- `get_question`, `get_current_revision`, `list_question_revisions` e selectors
  de taxonomia/origem;
- `QuestionQuickEntryForm`/`DraftActivationForm` e conversão de dados quando
  compatíveis, `base.html`, `app.css`, PRG, mensagens e Workspace local.

## Áreas prováveis de implementação

- `src/modules/questions/forms.py`, `views.py`, `urls.py`, `services.py` e
  `selectors.py`, apenas para expor/adaptar o recorte autorizado;
- templates sob `src/templates/questions/` para detalhe, edição e confirmação;
- `src/templates/base.html`, `src/static/css/app.css` e `src/config/urls.py`
  apenas para a navegação mínima;
- `tests/test_question_interface.py`, `tests/test_question_catalog.py` e testes
  focados estritamente necessários.

Nenhum desses arquivos deve ser criado ou alterado nesta preparação.

## Restrições

- não alterar migrations históricas, inclusive `questions/0002_question_catalog`,
  nem criar migration;
- não criar entidades/módulos futuros ou dependência nova;
- views são finas; escrita passa por services e leitura por selectors;
- não confiar em IDs/`lock_version` do cliente: revalidar Workspace, estado,
  referências e concorrência no servidor;
- não editar arquivada, reativar ou excluir fisicamente;
- não introduzir `Attempt` nem alegar efeitos de aprendizagem inexistentes;
- não implementar a Etapa 7/8, HTMX ou JavaScript sem base documental;
- não fazer commit, push, tag ou release sem autorização expressa.

## CTs e testes obrigatórios

- `CT-008`, `CT-010` (parcela V0.2), `CT-012`, `CT-075` e `CT-094`;
- `CT-095`, `CT-096` e `CT-097` para Workspace, CSRF e escaping;
- `CT-124` (parcela automatizável), `CT-138`, `CT-139`, `CT-140` e `CT-144`;
- `CT-142` (parcela automatizável): semântica, rótulos, erros, foco, teclado e
  responsividade; a validação manual integral permanece na Etapa 8;
- regressão do catálogo, cadastro rápido e isolamento de Workspace; todos os
  caminhos P0/P1 aplicáveis cobertos, sem reduzir as metas do gate.

## Critérios de aceite

- questão dos três estados é encontrada somente no próprio Workspace; detalhe
  somente leitura identifica estado e ausências, sem tentativa/ciclo/fila/métrica;
- edição válida mantém metadados/origem coerentes e cria nova revisão para
  conteúdo versionável, com anterior e alternativas imutáveis;
- alternativas/gabarito antes de tentativa geram exatamente uma revisão
  corrente; conflito/falha preserva a corrente anterior;
- referências inválidas, arquivadas, incoerentes ou de outro Workspace são
  rejeitadas sem persistência parcial e a entrada válida permanece no form;
- arquivamento confirmado revalida lock/estado, muda para `ARCHIVED`, preserva
  detalhe/origem/revisões e não reativa, exclui ou simula ciclo/fila;
- mutações usam CSRF, escaping, PRG e feedback fiel; telas atendem labels, erros
  associados, foco, teclado e layout em 360–1920 px/200% de zoom aplicáveis;
- nenhuma migration muda, `makemigrations --check --dry-run` fica limpo, CTs e
  regressão passam, não há P0/P1 aplicável e o gate retorna exit code 0;
- ao encerrar, registrar evidência/estado e arquivar a tarefa sem iniciar Etapa 7.

## Gate obrigatório

`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1`

Exit code diferente de 0 bloqueia a conclusão da Etapa 6.

## Resultado da execução

- detalhe fiel implementado para `DRAFT`, `ACTIVE` e `ARCHIVED`, com conteúdo
  atual, classificação, origem e histórico de revisões, sem fatos de
  aprendizagem inexistentes;
- edição de metadados, origem e conteúdo executada por comando atômico do
  `QuestionCommandService`, com `lock_version`, rollback e nova revisão somente
  quando conteúdo versionável muda;
- alternativas e gabarito permanecem pertencentes à própria revisão; revisão
  anterior é preservada e existe exatamente uma revisão corrente;
- arquivamento confirmado marca `ARCHIVED`, preserva identidade, origem e
  revisões e não oferece exclusão ou reativação;
- testes focados: 38 aprovados; suíte completa: 182 aprovados;
- coverage: 85% global; Questions Models 86%, Services 83%, Selectors 98%,
  Validators 90% e Views 87%;
- Ruff, mypy, `detect-secrets`, `pip-audit`, migrations e `git diff --check`:
  aprovados;
- gate autoritativo: GREEN, exit code 0;
- P0/P1 aplicável aberto: nenhum;
- validação manual integral de `CT-142` permanece reservada à Etapa 8.
