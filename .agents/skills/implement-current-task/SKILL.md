---
name: implement-current-task
description: "Execute somente a tarefa atualmente autorizada neste repositório, com mudança mínima e testes focados. Não use para escolher, autorizar ou encerrar tarefas."
---

# Implementar a tarefa atual

1. Leia `AGENTS.md` e `tasks/current.md`. Exija `Status: AUTHORIZED`; caso
   contrário, pare sem editar.
2. Trate Goal, Acceptance Criteria, Expected Scope, Protected Scope,
   Constraints e Verification do contrato como limites da execução. Um plano,
   Roadmap ou pedido incidental não os amplia; aplique
   `docs/A2_Contrato_de_Tarefa_Atual.md` diante de divergência.
3. Use `docs/A3_Progressive_Disclosure.md`: abra primeiro a implementação e os
   testes diretamente relacionados e amplie o contexto somente pelos gatilhos
   definidos ali. Leia um plano apenas quando autorizado conforme
   `tasks/plans/README.md`.
4. Preserve mudanças preexistentes e todo Protected Scope. Se houver conflito,
   ambiguidade material ou correção necessária fora do escopo, pare e reporte a
   decisão que precisa de nova autoridade.
5. Faça a menor mudança que satisfaça os critérios e adicione ou ajuste apenas
   a cobertura de comportamento aplicável.
6. Execute os testes focados relevantes e relate mudanças, resultados e pontos
   ainda não verificados.

Esta Skill não altera a autorização, não expande funcionalidade por
conveniência, não executa etapa futura e não encerra ou arquiva a tarefa. Testes
focados não substituem o gate autoritativo.
