# Etapa 6 — Adoção definitiva do novo fluxo operacional

## Identificação

- Tipo: melhoria de arquitetura operacional.
- Status: concluída.
- Produto: nenhuma funcionalidade alterada.
- Próxima etapa de produto: V0.2 — Etapa 3 — Catálogo de Origem, liberada e não iniciada.

## Objetivo

Tornar o repositório a memória operacional permanente do projeto por meio do fluxo:

`AGENTS.md` → `PROJECT_STATE.md` → `tasks/current.md` → documentação relevante e ADRs → implementação → testes → gate autoritativo → atualização de estado → arquivamento da tarefa → commit autorizado → novo chat.

## Escopo executado

- validação de `AGENTS.md`, `PROJECT_STATE.md`, `tasks/current.md`, `docs/README.md`, `tasks/completed/` e `scripts/quality.ps1`;
- correção do estado corrente da V0.2;
- criação da estrutura permanente de tarefas;
- formalização do encerramento desta melhoria;
- preparação, sem execução, da tarefa da V0.2 — Etapa 3.

## Fora de escopo

- qualquer funcionalidade nova do produto;
- implementação da V0.2 — Etapa 3;
- alteração de models ou migrations;
- commit, push, tag ou release.

## Situação encontrada

- `PROJECT_STATE.md` ainda indicava a Etapa 1 como último marco, 112 testes e 86% de cobertura;
- `tasks/current.md` e `tasks/completed/` não existiam;
- `AGENTS.md` ainda não explicitava todo o encadeamento de encerramento e novo chat;
- `docs/README.md` correspondia aos documentos reais existentes;
- o gate oficial já agregava runtime, rastreabilidade, perfis, migrations, Ruff, mypy, testes, cobertura, segredos e vulnerabilidades.

Como não havia `tasks/current.md` para preservar, este registro reconstrói de forma explícita a tarefa operacional autorizada pela instrução de execução.

## Critérios de aceite

- [x] fluxo operacional completo documentado;
- [x] estado real da V0.2 registrado;
- [x] tarefa operacional arquivada;
- [x] nova tarefa da Etapa 3 preparada sem ser iniciada;
- [x] índice de documentação conferido contra os arquivos reais;
- [x] nenhuma funcionalidade da Etapa 3 criada;
- [x] migrations preservadas;
- [x] gate autoritativo final executado com exit code 0;
- [x] `git diff --check` aprovado.

## Evidência final

- gate: `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1`;
- resultado: GREEN, exit code 0;
- testes: 125 aprovados;
- cobertura: 84% global, com metas específicas aplicáveis aprovadas;
- Ruff, mypy, detecção de segredos e `pip-audit`: aprovados;
- migrations: sem alterações inesperadas e aplicadas em banco vazio isolado;
- `git diff --check`: aprovado;
- P0/P1 aplicável aberto: nenhum.
