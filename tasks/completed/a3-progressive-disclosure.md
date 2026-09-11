# A3 — AGENTS.md e política de Progressive Disclosure

Status final: concluída e arquivada em 11 de setembro de 2026.

## Identification

- Task ID: A3
- Product version: pós-V0.3 / pré-V0.4; V0.4 não iniciada
- Stage: A3 — AGENTS.md e política de Progressive Disclosure
- Task type: operational architecture
- Size: M
- Risk: low

## Resultado

A política durável foi centralizada em `docs/A3_Progressive_Disclosure.md`.
`AGENTS.md` ficou como entrada curta e obrigatória; `docs/README.md` passou a
declarar explicitamente sua função de índice e mecanismo de descoberta. Não
houve mudança funcional, migration, alteração do gate ou criação de AGENTS
local.

## Auditoria do AGENTS anterior

| Seção | Classificação principal | Decisão A3 |
| --- | --- | --- |
| 1. Antes de iniciar | MUST READ EVERY TASK | Mantida como regra de entrada, com `current.md` antes de implementação. |
| 2. Fonte de verdade | MUST READ EVERY TASK | Mantida; define como tratar conflitos, sem duplicar fontes. |
| 3. Escopo da tarefa | MUST READ EVERY TASK | Mantida; A2 já fornece o contrato referenciado. |
| 4. Decisões arquiteturais | REFERENCE ONLY | Consultar ADRs somente quando a decisão arquitetural se aplicar. |
| 5. Qualidade | MUST READ EVERY TASK | Mantida; continua exigindo gate aplicável para conclusão. |
| 6. Testes | TASK-SPECIFIC | Aplica-se a mudança de comportamento e correção de bug. |
| 7. Documentação | TASK-SPECIFIC | Aplica-se quando o contrato ou comportamento realmente mudar. |
| 8. Estado do projeto | TASK-SPECIFIC | Aplica-se ao encerramento de etapa; não exige alterar estado funcional imutável. |
| 9. Uso eficiente de contexto | CANDIDATE FOR REFERENCE/LINK | Reduzida à regra curta e ligada à política durável. |
| 10. Fluxo operacional | MUST READ EVERY TASK | Mantido, agora aponta para o contexto proporcional. |
| 11. Resposta final | REFERENCE ONLY | Mantida como formato de handoff. |

Não há seção candidata à remoção. As sobreposições entre seções 1, 8 e 10 são
intencionais (entrada, encerramento e sequência) e não duplicam regras em
extenso. A classificação `DUPLICATED ELSEWHERE` foi evitada como decisão de
remoção: as referências curtas a A2 e A3 substituem reprodução integral.

## Fluxo e política aprovados

O fluxo histórico era `AGENTS.md` → `PROJECT_STATE.md` → `tasks/current.md` →
`docs/README.md` → documentação/ADRs → código/testes. Ele assegurava contexto
amplo, mas tornava estado e índice leituras universais mesmo em mudanças locais.

O fluxo A3 é `AGENTS.md` → `tasks/current.md` → código/testes diretamente
relacionados → fontes proporcionais. `PROJECT_STATE.md` é MUST READ para
planejamento, release, encerramento, conflito de estado, bloqueador e
dependência de versão/etapa; SHOULD READ para tarefa multicamada ou de alto
risco; ON-DEMAND para mudança local já delimitada. O README é índice, não
checklist. Requisitos, ADRs, Roadmap e histórico seguem regras explícitas de
consulta; context escalation e context stop impedem tanto omissão de evidência
quanto contexto preventivo infinito.

`tasks/current.md` permanece autoridade persistida: deve ser lido antes da
implementação; `NO_TASK_AUTHORIZED` bloqueia-a; `AUTHORIZED` limita-a ao escopo
descrito. Tarefas documentais que exigirem contexto devem referenciar as fontes
indispensáveis sem copiá-las.

## Acceptance Criteria

- [x] fluxo de progressive disclosure, escalation e stop explícito;
- [x] papéis de `current.md`, `PROJECT_STATE.md` e `docs/README.md` definidos;
- [x] regras para requisitos, ADRs, Roadmap, histórico, código e testes;
- [x] AGENTS raiz permaneceu enxuto e nenhum AGENTS local foi criado;
- [x] A3 arquivada e `current.md` retornado a `NO_TASK_AUTHORIZED`;
- [x] nenhuma funcionalidade Django, migration, gate, A4 ou V0.4 iniciados.

## Arquivos alterados

- `AGENTS.md`;
- `docs/A3_Progressive_Disclosure.md`;
- `docs/README.md`;
- `tasks/current.md` durante a execução e este registro histórico.

`PROJECT_STATE.md` não mudou: V0.3 continua promovida e congelada; não houve
transição funcional ou de release a registrar.

## Verificação

- [x] `git diff --check` aprovado antes do gate;
- [x] `powershell -NoProfile -ExecutionPolicy Bypass -File
  .\scripts\quality.ps1` — GREEN, exit code 0, 280 testes aprovados,
  cobertura global de 87%; migrations, Ruff, mypy, segredos e vulnerabilidades
  aprovados;
- [x] contrato final e arquivamento inspecionados após a execução.

## Próximo estado

Não há tarefa autorizada. A4 e qualquer trabalho posterior exigem nova
autorização formal em `tasks/current.md` e novo chat. Nenhum commit, push, tag
ou release foi realizado.
