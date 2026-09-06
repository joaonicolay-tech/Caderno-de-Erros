# V0.2 — Etapa 5 — Rascunho, Ativação e Cadastro Rápido

## Identificação

- Versão: V0.2.
- Etapa: 5.
- Nome: Rascunho, Ativação e Cadastro Rápido.
- Status: concluída.
- Execução: realizada em novo chat, conforme o fluxo operacional.

## Objetivo

Entregar o fluxo web acessível de `FL-002` para criar uma questão objetiva
textual como rascunho ou como ativa, retomar um rascunho para ativá-lo e
confirmar o resultado real da gravação, reutilizando o agregado e os serviços
internos concluídos na Etapa 4, sem criar tentativa ou qualquer estado fictício
de aprendizagem.

## Escopo

- criar a interface de cadastro rápido de questão com Django Forms, Templates e
  views finas no módulo `questions`;
- permitir salvar `DRAFT` com enunciado parcial ou `draft_title` mínimo e
  permitir retomar esse rascunho somente para completar os mínimos e ativá-lo;
- permitir criar `ACTIVE` diretamente quando todos os mínimos de ativação forem
  válidos;
- coletar disciplina e assunto ativos, subassunto opcional e coerente,
  enunciado, duas ou mais alternativas ordenadas e exatamente um gabarito;
- aceitar, sem tornar obrigatórios, dificuldade, origem mínima, explicação,
  pegadinha e observações no mesmo fluxo;
- criar ou reutilizar `Board`, `Exam` e `Source` exclusivamente no contexto do
  cadastro, conforme `ERR-V02-006`;
- preservar os valores válidos do formulário em erro corrigível e apresentar
  erros de campo, estado de processamento e feedback textual de sucesso/falha;
- aplicar Post/Redirect/Get, CSRF, escaping, semântica, foco, teclado e layout
  responsivo conforme a baseline de interface;
- garantir que IDs enviados pelo cliente sejam novamente limitados e validados
  pelo Workspace atual;
- integrar a navegação mínima necessária para alcançar o cadastro, sem criar a
  busca/listagem funcional da Etapa 7;
- criar testes de forms, views e templates para os caminhos autorizados.

## Fora de escopo

- detalhe completo, enriquecimento posterior de questão ativa, edição não
  crítica e edição/versionamento completo, reservados à Etapa 6;
- listagem pesquisável, busca textual, paginação e filtros de estado ou
  taxonomia, reservados à Etapa 7;
- fixture/demonstração final, recuperação completa do catálogo e validação
  manual integral de acessibilidade, reservadas à Etapa 8;
- arquivamento de questão e qualquer reativação ou exclusão física;
- `Attempt`, resposta de questão, resultado correto/incorreto e proteção do
  gabarito durante prática;
- classificação de erro, tentativa, ciclo, revisão de aprendizagem, fila,
  histórico de aprendizagem, métricas, dashboard, domínio ou prioridade;
- correção pós-tentativa, revisão adaptativa ou qualquer capacidade de V0.3+;
- tags, `QuestionTag`, filtros salvos, FTS/FTS5, OCR, anexos, importação em massa,
  API, PWA ou autenticação remota;
- administração independente de `Board`, `Exam` ou `Source`;
- novas entidades, alterações de schema ou migrations.

## Fontes obrigatórias

- `docs/Caderno_de_Erros_Inteligente_Etapa_9_Roadmap (1).md`, §§5.1–5.7;
- `docs/ADR-010_Fronteira_Rastreabilidade_e_Dados_V0.2.md`, §§2.1–2.3,
  `ERR-V02-001` a `ERR-V02-007`, §§5–6;
- `docs/Caderno_de_Erros_Inteligente_Etapa_3_Requisitos_Funcionais.md`,
  `RF-009`–`RF-014`;
- `docs/Caderno_de_Erros_Inteligente_Etapa_5_Regras_de_Negocio.md`,
  `RN-006`, `RN-007` e `RN-011`–`RN-017`, observados os recortes do `ADR-010`;
- `docs/Caderno_de_Erros_Inteligente_Etapa_8_Fluxos_Principais.md`, `FL-002`;
- `docs/Caderno_de_Erros_Inteligente_Etapa_6_SDD.md`, `SDD-MOD-003`,
  `SDD-SVC-001`, `SDD-ADR-009` e §32;
- `docs/Caderno_de_Erros_Inteligente_Etapa_4_Requisitos_Nao_Funcionais.md`,
  `RNF-003`, `RNF-007`, `RNF-008`, `RNF-010`, `RNF-013`, `RNF-016`,
  `RNF-017`, `RNF-027`, `RNF-032`, `RNF-044`–`RNF-049`, `RNF-063`,
  `RNF-065` e `RNF-066`;
- `docs/ADR-003_Identidade_Workspace_e_Tempo_V0.1.md`, nos recortes de
  Workspace, autorização e tempo;
- `docs/ADR-006_Interface_Acessivel_da_Fundacao_V0.1.md`;
- `docs/ADR-008_Gate_Unico_de_Qualidade_V0.1.md`;
- `docs/Caderno_de_Erros_Inteligente_Etapa_10_Plano_de_Testes.md`, casos e
  parcelas listados na seção de testes desta tarefa.

## Requisitos e regras aplicáveis

### Requisitos funcionais

- `RF-009`: salvar questão incompleta como rascunho recuperável, sem efeitos de
  aprendizagem;
- `RF-010`: ativar somente com taxonomia ativa, enunciado e gabarito válidos;
- `RF-011`: preservar a ordem de duas ou mais alternativas distintas e exigir
  exatamente uma correta para ativação;
- `RF-012`: aceitar origem opcional e validar seus dados quando informados;
- `RF-013`: aceitar dificuldade opcional apenas como fácil, média ou difícil;
- `RF-014`: priorizar os dados essenciais, permitir metadados opcionais e não
  perder entrada após erro corrigível.

### Regras de negócio

- `RN-006` e `RN-007`: questão ativa exige disciplina/assunto ativos e coerentes;
  subassunto é opcional, único e pertencente ao assunto;
- `RN-011`: questão incompleta permanece `DRAFT` e não recebe tentativa,
  revisão de aprendizagem, domínio ou contagem de questão realizada;
- `RN-012` e `RN-013`: ativação mínima de questão objetiva textual exige duas ou
  mais alternativas distintas e exatamente um gabarito; discursiva e múltiplas
  corretas não são suportadas;
- `RN-014` e `RN-015`: origem e dificuldade são opcionais e não afetam ativação;
- `RN-016`: explicação, pegadinha e observações podem ser informadas agora sem
  criar tentativa; enriquecimento posterior fica para a Etapa 6;
- `RN-017`: somente os estados `DRAFT`, `ACTIVE` e `ARCHIVED` existem; esta etapa
  cria rascunho ou ativa e não implementa arquivamento.

### Requisitos não funcionais

- confirmação fiel e contextual de gravação/falha (`RNF-003`, `RNF-010`,
  `RNF-032`), sem confirmação otimista irreversível;
- preservação da entrada após validação e proteção contra abandono acidental
  (`RNF-007`, `RNF-008`);
- isolamento/autorização por Workspace e integridade das referências
  (`RNF-013`, `RNF-027`);
- validação no servidor, escaping e CSRF (`RNF-016`, `RNF-017`);
- baseline acessível e responsiva em português do Brasil, com Unicode preservado
  (`RNF-044`–`RNF-049`, `RNF-063`, `RNF-065`, `RNF-066`).

### Fluxo

- implementar somente o recorte de `FL-002`: abrir o formulário, validar e
  gravar o agregado atomicamente como `DRAFT` ou `ACTIVE`, ou retornar erros sem
  perda dos campos;
- rascunho pode existir só com `draft_title`; qualquer conteúdo versionável real
  usa a política imutável já implementada na Etapa 4;
- ativação não cria `Attempt`, revisão de aprendizagem, métrica ou outro efeito
  futuro;
- tags mencionadas historicamente em `FL-002` são inaplicáveis por
  `ERR-V02-001`.

## Entidades e componentes existentes a reutilizar

- `Question`, `QuestionRevision`, `Alternative` e `QuestionOrigin`;
- `Board`, `Exam` e `Source`, sem tela administrativa independente;
- `Discipline`, `Subject` e `Subsubject` e seus selectors de disponibilidade;
- `QuestionCommandService.create_draft` e `create_active`, e somente a operação
  existente indispensável para completar/ativar um rascunho sem ampliar a
  edição da Etapa 6;
- `AlternativeInput`, `QuestionOriginInput`, validadores e exceções existentes;
- selectors de questão, revisão corrente e catálogos de origem existentes;
- resolução do Workspace local, padrão Post/Redirect/Get, feedback e tratamento
  de conflito já usados nas interfaces de Accounts/Taxonomy;
- `base.html`, `static/css/app.css` e os padrões de acessibilidade do `ADR-006`.

## Áreas prováveis de implementação

- criar `src/modules/questions/forms.py`;
- criar `src/modules/questions/views.py`;
- criar `src/modules/questions/urls.py` e incluí-lo em `src/config/urls.py`;
- criar templates estritamente necessários sob `src/templates/questions/`;
- ajustar `src/templates/base.html` e `src/static/css/app.css` somente no recorte
  necessário à navegação e ao formulário;
- reutilizar, e ajustar apenas se indispensável, `questions/services.py`,
  `questions/selectors.py` e `taxonomy/selectors.py`;
- criar testes de interface, preferencialmente em
  `tests/test_question_interface.py`, e ajustar o manifesto de gate vigente
  somente se o contrato operacional exigir a nova rastreabilidade.

Nenhum desses arquivos deve ser criado ou alterado durante a preparação desta
tarefa; a lista apenas orienta a futura implementação.

## Restrições

- não alterar migrations históricas, inclusive
  `questions/0002_question_catalog`, nem criar migration nova;
- preservar integralmente o isolamento por Workspace em leitura, escolhas e
  escrita; não confiar em IDs enviados pelo cliente;
- manter views finas e encaminhar gravações do agregado aos services existentes;
- usar selectors existentes para leituras e opções, ampliando-os apenas quando
  estritamente necessário ao recorte;
- não duplicar no form/view regras já encapsuladas no domínio ou serviço;
- não introduzir `Attempt` nem qualquer pacote ou entidade de aprendizagem;
- não implementar resposta, aprendizagem, revisão, fila ou métricas;
- não implementar busca, listagem pesquisável ou filtros da Etapa 7;
- não implementar detalhe, enriquecimento ou edição/versionamento completo da
  Etapa 6; a retomada permitida limita-se a completar e ativar um rascunho;
- não carregar HTMX ou criar JavaScript de aplicação sem necessidade documental
  concreta; formulários completos no servidor são a baseline aprovada;
- não criar dependência nova sem decisão explícita;
- não iniciar a Etapa 6 nem qualquer etapa seguinte automaticamente;
- não fazer commit, push, tag ou release sem autorização expressa.

## CTs e testes obrigatórios

- `CT-005` (parcela V0.2 desta etapa): rascunho recuperável, distinguível e fora
  do estado ativo, sem `Attempt` ou métricas;
- `CT-006`: campos ausentes ou inválidos impedem ativação, mantêm `DRAFT` e
  exibem mensagens claras;
- `CT-007`: zero ou múltiplos gabaritos, alternativas vazias ou indistinguíveis
  são rejeitados; duas ou mais válidas preservam ordem e uma correta;
- `CT-011`: cadastro rápido válido cria questão ativa no pai correto sem campos
  inconsistentes;
- `CT-012`: limites textuais, fronteiras e Unicode são preservados no formulário
  e na persistência;
- `CT-094`: erro de validação preserva toda entrada válida e não cria duplicata;
- `CT-095`: adulteração de qualquer ID não lê nem grava referências de outro
  Workspace;
- `CT-096`: mutações sem CSRF/contexto válido são rejeitadas sem alterar estado;
- `CT-097` (parcela aplicável): conteúdo potencialmente perigoso é exibido
  escapado no formulário/feedback, sem execução;
- `CT-124` (parcela funcional automatizável): criar questão válida e corrigir
  erro no fluxo contínuo; a avaliação formal com participantes fica para o
  marco de validação final da V0.2;
- `CT-138` (parcela de interface): origem opcional é criada/reutilizada no
  contexto da questão, validada por Workspace e nunca bloqueia ativação quando
  ausente;
- `CT-139` (parcela de estado/feedback): o resultado apresentado distingue
  fielmente `DRAFT` de `ACTIVE`, sem valores ou capacidades fictícias; o detalhe
  completo fica para a Etapa 6;
- `CT-142` (parcela automatizável desta interface): semântica, rótulos, erros,
  foco e responsividade do cadastro; a validação manual integral permanece
  reservada à Etapa 8;
- regressão explícita das parcelas de `CT-003`/`CT-004` necessárias aos seletores
  de hierarquia e dos testes da Etapa 4 que protegem o agregado e o Workspace;
- cobertura mínima: views/forms com pelo menos 75% de linhas e todos os caminhos
  P0/P1 aplicáveis cobertos, sem reduzir as metas vigentes de domínio/serviços.

## Critérios de aceite

- a navegação oferece o cadastro de questão somente quando existe Workspace
  local e o fluxo não cria registros antes da submissão válida;
- o usuário salva um rascunho mínimo, recebe confirmação fiel e consegue
  retomá-lo para completar e ativar;
- cadastro direto válido cria um único agregado `ACTIVE`, com revisão corrente,
  alternativas ordenadas, um gabarito e origem opcional coerentes;
- dados insuficientes nunca produzem questão ativa inválida; a ação escolhida e
  os erros são claros, e os demais campos permanecem preenchidos;
- taxonomia e origem arquivadas, incoerentes ou de outro Workspace são rejeitadas
  sem persistência parcial;
- origem e dificuldade permanecem opcionais; campos opcionais não bloqueiam a
  ativação;
- falha de validação, conflito ou persistência não anuncia sucesso nem duplica
  agregado/revisão;
- o fluxo usa CSRF, escaping, labels persistentes, associação de erros, foco
  visível/lógico, teclado e layout funcional entre 360 e 1920 px e a 200% de
  zoom nas verificações aplicáveis;
- nenhum `Attempt`, revisão de aprendizagem, busca/filtro, edição completa,
  arquivamento ou capacidade futura é criado;
- nenhuma migration existente muda e `makemigrations --check --dry-run` não
  aponta alteração;
- testes específicos e regressão passam, nenhum P0/P1 aplicável permanece
  aberto e o gate obrigatório retorna exit code 0;
- ao concluir, registrar evidência, atualizar o estado e arquivar esta tarefa,
  sem iniciar automaticamente a Etapa 6.

## Gate obrigatório

`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1`

Exit code diferente de 0 bloqueia a conclusão da Etapa 5.
