# A4 — Organização de tarefas e planos

Status final: concluída e arquivada em 11 de setembro de 2026.

## Identification

- Task ID: A4
- Product version: pós-V0.3 / pré-V0.4; V0.4 não iniciada
- Stage: A4 — organização de tarefas e planos
- Task type: operational architecture
- Size: S
- Risk: low

## Resultado

Foi formalizada a separação prospectiva entre `tasks/current.md`, `tasks/plans/` e `tasks/completed/`. `current.md` permanece a única autoridade da autorização corrente; `plans/` é opcional e só descreve decomposição de uma tarefa autorizada; `completed/` preserva o histórico fora do contexto normal.

## Auditoria e decisão de estrutura

Antes de A4, `tasks/` continha `current.md` e `completed/`, sem subpastas de planos. Foram encontrados 15 arquivos históricos, com convenções de nomes `v02-...`, `v03-...`, `a2/a3` e um registro operacional anterior. Não havia plano persistente prévio nem duplicação material. Como a reorganização traria apenas simetria estética, nenhum histórico foi movido, convertido ou reescrito.

`tasks/plans/README.md` foi criado como explicação operacional principal e template enxuto. Nenhum plano artificial foi criado para A4.

## Política aplicada

- XS e S não exigem plano persistente; M pode usar checklist em `current.md`.
- L pode justificar plano; XL deve ser decomposta antes da implementação e normalmente justifica plano.
- Um plano é usado apenas quando houver ganho concreto, como dependências, multicamada, migration complexa, mudança arquitetural, investigação, rollback, risco alto ou continuidade entre execuções.
- Plano não amplia Goal, Expected Scope, Protected Scope nem autorização; conflito é resolvido em favor de `current.md`.
- Estados mínimos do plano: `DRAFT`, `ACTIVE`, `COMPLETED` e `SUPERSEDED`. Artefatos relevantes são preservados quando há encerramento, substituição ou desdobramento em nova tarefa autorizada.

## Validação e escopo preservado

- Os casos conceituais XS, S, M, L e XL estão registrados em `tasks/plans/README.md`; não foram criadas cinco tarefas reais.
- `docs/A3_Progressive_Disclosure.md` recebeu somente a regra de que planos são contexto opcional e planos concluídos ficam fora do contexto normal.
- Nenhuma funcionalidade Django, teste, migration ou gate foi alterado.
- A5 não foi iniciada. Não houve commit, push, tag ou release.

## Verificação

- `git diff --check`: aprovado.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1`: GREEN, exit code 0; 280 testes aprovados, 87% de cobertura e nenhuma vulnerabilidade conhecida reportada.

## Arquivos alterados

- `tasks/current.md` (autorização transitória de A4 e retorno ao estado sem tarefa);
- `tasks/plans/README.md`;
- `docs/A3_Progressive_Disclosure.md`;
- `PROJECT_STATE.md`;
- este registro de encerramento.

## Próximo estado

Não há tarefa autorizada. A5 e qualquer trabalho posterior requerem nova autorização formal em `tasks/current.md` e novo chat.
