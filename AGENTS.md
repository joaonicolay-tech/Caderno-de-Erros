# AGENTS.md — Caderno de Erros

Este arquivo define as orientações operacionais gerais para agentes que trabalham neste repositório.

## 1. Antes de iniciar qualquer tarefa

Leia, nesta ordem:

1. `PROJECT_STATE.md` para entender o estado atual do projeto.
2. `tasks/current.md` para identificar a tarefa autorizada no momento.
3. `docs/README.md` para localizar as fontes documentais aplicáveis.
4. Apenas a documentação explicitamente relevante ou referenciada pela tarefa atual.
5. ADRs relacionados à área que será modificada.

Não reanalise todo o repositório sem necessidade.

---

## 2. Fonte de verdade

Use como fontes de verdade, nesta ordem:

1. Código e migrations existentes.
2. Testes automatizados.
3. ADRs aprovados.
4. Documentação formal do projeto.
5. `PROJECT_STATE.md`.
6. `tasks/current.md`, para o escopo específico da execução atual.

Caso exista contradição entre fontes, não escolha silenciosamente uma interpretação.

Identifique a divergência e trate-a antes de introduzir uma mudança estrutural.

---

## 3. Escopo da tarefa

Implemente somente o que estiver autorizado no contrato com
`Status: AUTHORIZED` em `tasks/current.md`. Chat não amplia silenciosamente o
escopo persistido; em caso de divergência, identifique-a antes de implementar.
O formato e o estado sem autorização estão em
`docs/A2_Contrato_de_Tarefa_Atual.md`.

Não:

* antecipe funcionalidades de etapas futuras;
* altere arquitetura sem necessidade;
* crie migrations fora do escopo;
* faça refatorações amplas não solicitadas;
* modifique requisitos já aprovados sem justificativa;
* introduza dependências novas sem necessidade clara.

Mudanças pequenas indispensáveis para concluir corretamente a tarefa são permitidas, desde que permaneçam compatíveis com a arquitetura e sejam relatadas.

---

## 4. Decisões arquiteturais

Consulte os ADRs antes de tomar decisões arquiteturais relevantes.

Uma decisão registrada em ADR deve ser considerada vigente enquanto não houver:

* contradição comprovada;
* requisito novo incompatível;
* problema técnico concreto;
* ADR posterior que a substitua.

Não rediscuta decisões já consolidadas apenas por preferência de implementação.

---

## 5. Qualidade

Uma tarefa não é considerada concluída apenas porque o código foi implementado.

Execute o gate de qualidade aplicável, em PowerShell, usando:

`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1`

Quando existirem verificações específicas da etapa, execute-as também.

A conclusão exige:

* testes aplicáveis passando;
* nenhuma falha relevante de lint ou checagem;
* critérios de aceite satisfeitos;
* ausência de P0/P1 aplicável aberto;
* gate autoritativo aprovado.

Não declare conclusão se o gate estiver vermelho.

---

## 6. Testes

Toda alteração de comportamento deve possuir cobertura de testes adequada.

Ao corrigir um bug, sempre que possível:

1. reproduza o problema;
2. crie ou ajuste um teste que detecte o comportamento incorreto;
3. implemente a correção;
4. confirme que o teste passa;
5. execute o gate aplicável.

Evite alterar testes apenas para fazer uma implementação incorreta passar.

---

## 7. Documentação

Atualize documentação somente quando a alteração realmente modificar:

* comportamento;
* arquitetura;
* contrato;
* regra de negócio;
* fluxo;
* decisão técnica;
* estado do projeto.

Não replique a mesma informação desnecessariamente em vários documentos.

---

## 8. Estado do projeto

Ao concluir uma etapa autorizada:

1. execute o gate final;
2. registre o resultado aplicável em `quality/`;
3. atualize `PROJECT_STATE.md`;
4. mova a tarefa concluída de `tasks/current.md` para `tasks/completed/`, conforme o padrão do projeto;
5. deixe claro qual é o próximo estado autorizado;
6. após revisão humana, faça somente o commit expressamente autorizado;
7. inicie a próxima etapa em um novo chat, usando a nova `tasks/current.md`.

Não inicie automaticamente a etapa seguinte.

---

## 9. Uso eficiente de contexto

O repositório é a memória permanente do projeto.

Leia somente os arquivos necessários para a tarefa atual.

Prefira:

* consultar índices e referências;
* abrir arquivos diretamente relacionados à mudança;
* reutilizar decisões já documentadas;
* evitar reanálises globais desnecessárias.

O histórico do chat não deve ser tratado como a única fonte de verdade.

---

## 10. Fluxo operacional obrigatório

O fluxo padrão do repositório é:

`AGENTS.md` → `PROJECT_STATE.md` → `tasks/current.md` → documentação relevante e ADRs → implementação → testes específicos → `scripts/quality.ps1` → atualização de estado → arquivamento da tarefa → commit autorizado → novo chat para a próxima etapa.

Preparar a próxima `tasks/current.md` autoriza apenas uma execução futura. Não autoriza iniciar essa tarefa na mesma execução que encerra a anterior.

---

## 11. Resposta final

Ao finalizar uma tarefa, responda de forma concisa contendo:

* o que foi alterado;
* arquivos principais criados ou modificados;
* testes executados;
* resultado do gate;
* bloqueadores ou ressalvas, se existirem;
* confirmação explícita de que nenhuma etapa futura foi antecipada.
