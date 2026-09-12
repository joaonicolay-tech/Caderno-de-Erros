---
name: finish-task
description: "Valide e registre o encerramento da tarefa atualmente autorizada neste repositório. Use somente após implementação e gate; recuse arquivamento quando faltar evidência."
---

# Encerrar a tarefa atual

1. Leia `AGENTS.md` e `tasks/current.md`; exija `Status: AUTHORIZED` e identifique
   Acceptance Criteria, Expected Scope, Protected Scope, Verification e Done
   When conforme `docs/A2_Contrato_de_Tarefa_Atual.md`.
2. Revise o diff e confirme, com evidência, critérios de aceite, testes
   relevantes, escopo esperado, escopo protegido, documentação afetada e
   ausência de P0/P1 aplicável aberto.
3. Exija resultado elegível e atual do gate definido por `AGENTS.md` e
   `scripts/quality.ps1`, com exit code 0, além de `git diff --check` aprovado.
   Se a evidência estiver ausente, inconclusiva ou vermelha, não arquive.
4. Quando todos os requisitos estiverem satisfeitos, atualize
   `PROJECT_STATE.md` somente se o estado operacional mudou, preserve no
   registro em `tasks/completed/` o contrato e a evidência de encerramento e
   substitua `tasks/current.md` pelo estado `NO_TASK_AUTHORIZED` definido em A2.
5. Revise o estado final e reporte arquivos, testes, gate, ressalvas e ações
   explicitamente não realizadas.

Esta Skill não executa automaticamente as outras Skills, não altera critérios
depois da implementação e não autoriza nem inicia a próxima tarefa. Commit,
push, tag e release só podem ocorrer sob autorização separada e expressa.
