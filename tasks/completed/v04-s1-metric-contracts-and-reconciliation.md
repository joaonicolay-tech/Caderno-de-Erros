# Task Contract

Status: COMPLETED

## Identification

- Task ID: V0.4-S1
- Product version: V0.4
- Stage: S1 â€” Contratos de mÃ©tricas e exemplos de reconciliaÃ§Ã£o
- Task type: product semantics / analytics contracts / requirements
- Size: M
- Risk: medium
- Recommended execution profile: GPT-5.6 Terra, High reasoning
- Expected review: deep

## Goal

Formalizar os contratos semÃ¢nticos autoritativos das mÃ©tricas da V0.4 antes da
implementaÃ§Ã£o dos serviÃ§os analÃ­ticos e do dashboard, eliminando ambiguidade
sobre populaÃ§Ã£o, eventos, perÃ­odo, estados temporais, filtros, zero, empty
state, drill-down e reconciliaÃ§Ã£o.

## Context

- Aplicar `docs/PROJECT_DEVELOPMENT_ARCHITECTURE_V1.md` e a polÃ­tica de leitura
  proporcional de `docs/A3_Progressive_Disclosure.md`.
- `tasks/plans/v04-release-execution-plan.md` Ã© rastreabilidade e planejamento,
  nÃ£o autoridade normativa; S1 deve verificar requisitos formais, ADRs, cÃ³digo
  e testes aplicÃ¡veis conforme a precedÃªncia do repositÃ³rio.
- Antes de formalizar a interpretaÃ§Ã£o de `RN-057`, localizar sua fonte
  normativa e confrontÃ¡-la com ADRs, regras, cÃ³digo e testes. Classificar
  explicitamente se o plano P0 apenas esclareceu regra existente, fez inferÃªncia
  compatÃ­vel, ou introduziu mudanÃ§a de requisito.
- Os contratos devem ser suficientes para S2 implementar a leitura e S3
  apresentÃ¡-la sem redefinir o significado das mÃ©tricas.

## Acceptance Criteria

- HÃ¡ contrato explÃ­cito para questÃµes cadastradas, questÃµes realizadas,
  tentativas, acertos, erros, taxa de acerto, revisÃµes concluÃ­das hoje,
  revisÃµes devidas, atrasadas e futuras, desempenho por disciplina e assunto,
  frequÃªncia por categoria de erro e demais mÃ©tricas V0.4 rastreadas pelo P0
  cuja semÃ¢ntica pertenÃ§a a S1.
- Para cada mÃ©trica, o contrato define nome, propÃ³sito, fonte de dados, unidade,
  numerador e denominador quando aplicÃ¡veis, perÃ­odo, timezone ou data de
  referÃªncia, filtros, inclusÃµes, exclusÃµes, zero, empty state, drill-down,
  relaÃ§Ãµes com mÃ©tricas vizinhas e exemplos positivos, negativos e de
  reconciliaÃ§Ã£o. NÃ£o hÃ¡ fÃ³rmula ou denominador implÃ­cito.
- A distinÃ§Ã£o entre questÃ£o cadastrada e realizada Ã© comprovada no domÃ­nio real;
  criaÃ§Ã£o da entidade nÃ£o Ã© tratada como tentativa sem evidÃªncia.
- Tentativas iniciais, revisÃµes e outros fatos histÃ³ricos sÃ£o diferenciados
  quando o domÃ­nio exigir; acertos, erros e taxa reconciliam com o universo
  correto, inclusive em mÃºltiplas tentativas e revisÃµes.
- Estados de revisÃ£o concluÃ­da hoje, devida, atrasada e futura usam a polÃ­tica,
  datas civis, timezone, ciclos, arquivamento e suspensÃ£o reais; suas relaÃ§Ãµes
  e exclusividade sÃ£o explicitadas.
- AgregaÃ§Ãµes por disciplina, assunto e categoria de erro definem populaÃ§Ã£o,
  agrupamento, ausÃªncia de dados, vÃ­nculo taxonÃ´mico e tratamento de
  classificaÃ§Ã£o ausente ou corrigida, sem antecipar categorias pessoais V0.5.
- `RN-057` recebe classificaÃ§Ã£o de origem e precedÃªncia. Uma mudanÃ§a normativa
  real nÃ£o Ã© incorporada silenciosamente: a divergÃªncia Ã© registrada e somente
  o restante seguro da S1 Ã© formalizado.
- CenÃ¡rios pequenos, determinÃ­sticos e reconciliÃ¡veis demonstram inclusÃµes,
  exclusÃµes, bordas temporais, zero e relaÃ§Ãµes entre nÃºmeros, prontos para
  orientar testes S2, dashboard S3 e investigaÃ§Ã£o futura.

## Expected Scope

- Auditar requisitos e regras de analytics, ADRs, models, services e testes
  existentes estritamente necessÃ¡rios para os contratos.
- Criar ou atualizar a documentaÃ§Ã£o normativa ou explicativa de contratos e os
  exemplos de reconciliaÃ§Ã£o; criar teste documental/contratual ou mecanismo
  leve de validaÃ§Ã£o somente se compatÃ­vel e necessÃ¡rio.
- Atualizar rastreabilidade, estado e plano somente para refletir conclusÃ£o real
  da S1, registrar mÃ©tricas A7 e aplicar review A8 profundo.

## Protected Scope

- Comportamento funcional Django, queries analÃ­ticas finais de S2 e dashboard
  de S3.
- Templates funcionais, CSS, migrations, schema, ciclos de revisÃ£o e regras de
  negÃ³cio existentes sem autorizaÃ§Ã£o especÃ­fica.
- V0.3 promovida, `docs/PROJECT_DEVELOPMENT_ARCHITECTURE_V1.md`, Skills e
  `scripts/quality.ps1`.
- S2 e itens V0.5, incluindo categorias personalizadas.

## Constraints

- S1 Ã© uma etapa de contrato semÃ¢ntico: nÃ£o implementar serviÃ§os analÃ­ticos
  completos, dashboard ou queries S2 antecipadas.
- Aplicar a precedÃªncia: requisito/regra formal, ADR, comportamento executÃ¡vel,
  testes, documentaÃ§Ã£o explicativa e, por Ãºltimo, P0 como planejamento.
- NÃ£o alterar requisito normativo, inventar evidÃªncia, fabricar mÃ©tricas ou
  escolher silenciosamente uma fonte divergente.
- NÃ£o fazer commit, push, tag ou release sem autorizaÃ§Ã£o expressa.

## Verification

- Verificar internamente os contratos, exemplos e reconciliaÃ§Ãµes: populaÃ§Ãµes,
  denominadores, zero/empty state, timezone, bordas de data e exclusividade dos
  estados temporais.
- Executar review A8 profundo para ambiguidade semÃ¢ntica, conflitos de fonte,
  dupla contagem, revisÃ£o versus tentativa inicial, scope creep e mudanÃ§a
  normativa silenciosa.
- Executar verificaÃ§Ãµes focadas proporcionais, `git diff --check` e o gate
  autoritativo: `powershell -NoProfile -ExecutionPolicy Bypass -File
  .\scripts\quality.ps1`.

## Documentation Impact

Criar ou atualizar a fonte durÃ¡vel dos contratos semÃ¢nticos e exemplos de S1,
com rastreabilidade necessÃ¡ria para S2/S3; ao encerrar, atualizar apenas os
registros operacionais elegÃ­veis, arquivar a tarefa e registrar A7.

## Done When

- Todos os contratos e exemplos de reconciliaÃ§Ã£o exigidos estÃ£o explÃ­citos,
  coerentes e suficientes para S2/S3 sem decisÃ£o semÃ¢ntica implÃ­cita.
- `RN-057` foi auditada e classificada, sem alteraÃ§Ã£o normativa silenciosa.
- Review A8 profundo, verificaÃ§Ãµes proporcionais, `git diff --check` e gate
  autoritativo estÃ£o aprovados; nÃ£o hÃ¡ P0/P1 aplicÃ¡vel aberto.
- A documentaÃ§Ã£o e os registros A7 elegÃ­veis estÃ£o atualizados; S1 foi
  arquivada e `tasks/current.md` retornou a `NO_TASK_AUTHORIZED`.
- S2 nÃ£o foi iniciada nem autorizada.


## Evidência de encerramento

- Fonte criada: \`docs/V0.4_S1_Contratos_de_Metricas_e_Reconciliacao.md\`.
- Auditoria RN-057: **A — esclarecimento comprovado**; nenhuma mudança
  normativa foi aplicada silenciosamente.
- Review A8 profundo: **APPROVED**, sem Blocker/Major aberto.
- Validação documental: contratos obrigatórios, escopo protegido e UTF-8
  aprovados; \`git diff --check\` aprovado.
- Testes focados: 69 aprovados em 11,91 s
  (\`test_learning_foundation\`, \`test_initial_attempt\`,
  \`test_review_completion\`, \`test_stage4_learning\`).
- Gate autoritativo: GREEN, exit code 0; 280 testes aprovados em 57,68 s,
  cobertura global 87%, migrations, formatação, Ruff, mypy, cobertura de
  domínio, detect-secrets e pip-audit aprovados.
- S2 não foi iniciada nem autorizada. Não houve implementação de query,
  serviço analítico, dashboard, view, migration ou alteração de regra.
- Não houve commit, push, tag ou release.
