# V0.2 — Etapa 4 — Catálogo de Questões

## Identificação

- Versão: V0.2.
- Etapa: 4.
- Nome: Catálogo de Questões.
- Status: liberada, não iniciada.
- Execução: deve começar em novo chat.

## Objetivo

Criar a fundação persistente e interna do catálogo de questões da V0.2 em
`SDD-MOD-003`, composta por `Question`, `QuestionRevision`, `Alternative` e
`QuestionOrigin`, sobre o catálogo de origem já aprovado.

## Escopo

- implementar as quatro entidades conforme o modelo e `ADR-010`;
- criar a migration congelada `questions/0002_question_catalog`, dependente de
  `questions/0001_origin_catalog` e `taxonomy/0001_initial`;
- implementar somente os validadores, serviços e selectors necessários às
  invariantes persistentes e transacionais desta etapa;
- garantir isolamento por Workspace, estados, origem opcional, revisões
  imutáveis, alternativas pertencentes à revisão e gabarito da própria revisão;
- cobrir instalação limpa, upgrades, constraints, rollback e regressão.

## Fora de escopo

- views, URLs, forms ou templates de questões;
- busca/listagem funcional e filtros;
- tags e `QuestionTag`;
- `Attempt`, classificação de erro, ciclos, revisões de aprendizagem, métricas,
  dashboard, domínio ou prioridade;
- qualquer capacidade da Etapa 5 ou posterior.

## Fontes obrigatórias

- `docs/ADR-010_Fronteira_Rastreabilidade_e_Dados_V0.2.md`, especialmente
  `ERR-V02-006`, `ERR-V02-007` e a ordem de migrations;
- requisitos, regras, SDD, Modelo de Dados §§3.6 e 6.4–6.7, fluxos, Roadmap e
  Plano de Testes referenciados por `ADR-010` para esta parcela;
- `ADR-001`, `ADR-002`, `ADR-003` e `ADR-008` nos recortes aplicáveis.

## Restrições

- preservar todas as migrations existentes e seus hashes aprovados;
- não alterar `questions/0001_origin_catalog`;
- não criar entidades de aprendizagem ou capacidades de interface/busca;
- não iniciar automaticamente a etapa seguinte.

## Critérios de aceite

- models, constraints, índices e FKs correspondem ao contrato aprovado;
- rascunho apenas com título pode existir sem revisão e conteúdo versionável
  sempre cria revisão imutável;
- existe no máximo uma revisão corrente e a troca é atômica;
- alternativas e gabarito permanecem na própria revisão;
- `QuestionOrigin` é 0..1, opcional, Workspace-scoped e respeita a exclusão
  mútua de `exam_id`/`board_id`;
- migration limpa e upgrades preservam os dados existentes;
- testes específicos e gate autoritativo retornam exit code 0;
- nenhum P0/P1 aplicável permanece aberto.

## Gate obrigatório

`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1`

Exit code diferente de 0 bloqueia a conclusão da Etapa 4.
