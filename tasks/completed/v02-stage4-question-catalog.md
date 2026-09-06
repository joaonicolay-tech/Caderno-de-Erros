# V0.2 — Etapa 4 — Catálogo de Questões

## Identificação

- Versão: V0.2.
- Etapa: 4.
- Nome: Catálogo de Questões.
- Status: concluída.
- Execução: realizada em novo chat, conforme o fluxo operacional.

## Objetivo concluído

Foi criada a fundação persistente e interna de `Question`, `QuestionRevision`,
`Alternative` e `QuestionOrigin` em `SDD-MOD-003`, sobre os catálogos de
taxonomia e origem aprovados.

## Escopo autorizado e executado

- implementados models, enums, constraints, índices e FKs protegidas das quatro
  entidades;
- criada e congelada `questions/0002_question_catalog`, dependente de
  `questions/0001_origin_catalog` e `taxonomy/0001_initial`;
- implementado `QuestionCommandService` para rascunho, ativação, nova revisão,
  edição de metadados/origem e arquivamento;
- implementados validadores de Unicode, ausência canônica, limites textuais,
  alternativas e ano civil do Workspace;
- implementados selectors internos de agregado, revisão corrente e histórico de
  revisões;
- garantidos isolamento por Workspace, hierarquia ativa, estados, concorrência
  otimista e rollback integral;
- ampliado o manifesto intermediário V0.2 com hashes e rastreabilidade da etapa;
- cobertos banco vazio, upgrade da Etapa 3, rollback para `questions/0001`,
  constraints, FKs, regressão e cobertura.

## Invariantes comprovadas

- rascunho apenas com `draft_title` não cria revisão;
- qualquer conteúdo versionável real cria `QuestionRevision` corrente;
- ativação exige taxonomia ativa, enunciado, duas alternativas distintas e um
  único gabarito;
- revisões e alternativas não são sobrescritas; edição de conteúdo cria versão
  crescente e troca a corrente atomicamente;
- existe no máximo uma revisão corrente por questão;
- `correct_alternative_id` sempre referencia alternativa da própria revisão no
  serviço/model guard;
- `QuestionOrigin` é opcional, 0..1, eliminada quando vazia e integralmente
  Workspace-scoped;
- `exam_id`/`board_id` são mutuamente exclusivos, e ano com prova deriva de
  `Exam`;
- anos aceitam 1900 até o ano civil corrente do Workspace + 2;
- arquivamento preserva revisões e origem;
- enunciados iguais não sofrem bloqueio semântico.

## Evidência final

- testes específicos: 39 aprovados em `tests/test_question_catalog.py` e
  `tests/test_origin_catalog.py`, dos quais 20 pertencem à nova etapa;
- CTs com evidência ampliada: `CT-005`, `CT-006`, `CT-007`, `CT-008`, `CT-010`,
  `CT-011`, `CT-012`, `CT-073`, `CT-074`, `CT-075`, `CT-081`, `CT-082`,
  `CT-122`, `CT-138`, `CT-139`, `CT-140` e `CT-144`;
- regressão/gate: 164 testes aprovados;
- cobertura: 85% global; Questions Models 85%, Services 84%, Selectors 100% e
  Validators 90%;
- `makemigrations --check --dry-run`: sem alterações;
- instalação limpa: `questions.0002_question_catalog` aplicada com sucesso;
- upgrade/rollback: dados de taxonomia e origem da Etapa 3 preservados;
- gate autoritativo: GREEN, exit code 0;
- Ruff, mypy, detecção de segredos e `pip-audit`: aprovados;
- migrations históricas: hashes de `accounts/0001_initial`,
  `errors/0001_initial`, `taxonomy/0001_initial` e
  `questions/0001_origin_catalog` preservados;
- P0/P1 aplicável aberto: nenhum.

## Fora de escopo preservado

Nenhuma view, URL, form, template, busca, tag, tentativa, classificação de erro,
ciclo, revisão de aprendizagem, métrica, dashboard, domínio ou prioridade foi
criada. Nenhuma capacidade da Etapa 5 ou posterior foi antecipada.

## Próximo estado autorizado

Nenhuma tarefa nova está formalmente liberada. A Etapa 5 não foi preparada nem
iniciada; o repositório aguarda revisão humana e uma nova `tasks/current.md`.
