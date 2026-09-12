---
name: start-task
description: "Valide e prepare o início de uma tarefa já autorizada neste repositório. Use antes de implementar; não use para criar ou autorizar uma nova tarefa."
---

# Iniciar tarefa autorizada

1. Leia `AGENTS.md` e `tasks/current.md` na raiz do repositório.
2. Verifique o `Status` antes de qualquer implementação. Se for
   `NO_TASK_AUTHORIZED`, pare e informe que nenhuma implementação é permitida.
   Não transforme chat, Roadmap ou plano em autorização.
3. Se for `AUTHORIZED`, extraia Goal, Acceptance Criteria, Expected Scope,
   Protected Scope, Constraints, Verification, Documentation Impact e Done
   When. Trate campos ausentes ou contraditórios conforme
   `docs/A2_Contrato_de_Tarefa_Atual.md`.
4. Inspecione a working tree sem alterá-la e preserve mudanças existentes que
   não pertençam à tarefa.
5. Carregue somente o contexto exigido pelo contrato e pela política
   `docs/A3_Progressive_Disclosure.md`. Leia `PROJECT_STATE.md` quando essa
   política exigir. Consulte `tasks/plans/` apenas se o contrato o referenciar
   ou se a regra de A4 em `tasks/plans/README.md` justificar decomposição.
6. Identifique os testes focados e o gate aplicáveis sem executá-los por padrão.
7. Resuma a tarefa realmente autorizada, o escopo protegido, a verificação e
   qualquer bloqueador.

Esta Skill apenas valida e prepara. Não modifica autorização, estado do projeto,
arquivos da tarefa ou Git; não inicia implementação nem etapa futura.
