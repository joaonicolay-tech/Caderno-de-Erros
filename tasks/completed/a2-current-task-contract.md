# A2 — Contrato formal de `tasks/current.md`

Status final: concluída e arquivada em 11 de setembro de 2026.

## Identification

- Task ID: A2
- Product version: pós-V0.3 / pré-V0.4; V0.4 não iniciada
- Stage: A2 — contrato formal de `tasks/current.md`
- Task type: operational architecture
- Size: M
- Risk: low

## Goal

Estabelecer um contrato versionado, mínimo e inequívoco para a autorização de
trabalho em `tasks/current.md`.

## Context

Esta tarefa foi persistida em `tasks/current.md` com `Status: AUTHORIZED`
antes das alterações efetivas e é o primeiro uso do novo contrato. A V0.3
permanece promovida e congelada; a V0.4 não foi iniciada.

## Auditoria do formato anterior

Antes da alteração, `tasks/current.md` tinha oito linhas: o título “Nenhuma
tarefa autorizada”, a referência à promoção V0.3/ADR-014 e a proibição de
iniciar V0.4, nova implementação ou ações Git sem nova autorização. O que já
funcionava era o estado sem tarefa e a preservação de V0.3.

Faltavam identificação, versão, etapa, tipo, tamanho, risco, objetivo, escopo
esperado/protegido, restrições, critérios verificáveis, verificação, impacto
documental e definição de encerramento. Assim, não podia registrar uma tarefa
autorizada nem resolver a divergência entre uma autorização no chat e o estado
persistido. Referências ao estado da V0.3 duplicavam `PROJECT_STATE.md`; o
fluxo de trabalho duplicava `AGENTS.md`; requisitos, ADRs e contexto extenso
devem permanecer em `docs/`, por referência quando necessários.

## Acceptance Criteria

- [x] contrato claro, proporcional e versionável definido em documentação operacional;
- [x] identificação, Goal e Acceptance Criteria obrigatórios definidos;
- [x] Expected Scope e Protected Scope disponíveis quando aplicáveis;
- [x] tamanhos `XS`, `S`, `M`, `L` e `XL` definidos sem regra rígida de arquivos;
- [x] riscos `low`, `medium`, `high` e `critical` definidos por impacto;
- [x] relação com `AGENTS.md`, `PROJECT_STATE.md`, `docs/`, código e testes definida;
- [x] regra de autorização persistida e divergência com chat tratada explicitamente;
- [x] estado `NO_TASK_AUTHORIZED` definido de forma não confundível com tarefa incompleta;
- [x] A2 executada usando o próprio contrato e arquivada;
- [x] tarefas históricas não migradas ou reformatadas;
- [x] nenhuma funcionalidade Django alterada e A3 não iniciada.

## Expected Scope Executed

- `docs/A2_Contrato_de_Tarefa_Atual.md`: contrato durável;
- `AGENTS.md`: descoberta mínima da regra;
- `docs/README.md`: índice e referência ao contrato;
- `tasks/current.md`: contrato A2 durante a execução e estado final sem autorização;
- este arquivo: registro histórico da A2.

## Protected Scope Preserved

Produto Django, testes, migrations, gate, evidências, tarefas históricas, ADRs,
manifests, V0.4, A3 e ações Git externas permaneceram fora de escopo.

## Verification

- [x] `git diff --check` aprovado antes do gate e novamente após o registro
  final;
- [x] `powershell -NoProfile -ExecutionPolicy Bypass -File
  .\\scripts\\quality.ps1` — GREEN, exit code 0, 280 testes aprovados,
  87% de cobertura; migrations, Ruff, mypy, segredos e vulnerabilidades
  aprovados;
- [x] `tasks/current.md` inspecionado no estado final e este registro presente
  em `tasks/completed/`.

## Documentation Impact

Foram alterados somente `AGENTS.md`, `docs/README.md`,
`docs/A2_Contrato_de_Tarefa_Atual.md`, `tasks/current.md` e este registro.
`PROJECT_STATE.md` não mudou: o estado funcional e de versão permanece V0.3
promovida, sem etapa de implementação autorizada.

## Done When

- [x] contrato e documentação de descoberta criados;
- [x] A2 arquivada;
- [x] `tasks/current.md` retornado ao estado sem implementação autorizada;
- [x] verificações registradas após a execução.
