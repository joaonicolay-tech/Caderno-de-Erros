# A1 — Baseline pós-V0.3 / pré-V0.4 da arquitetura operacional

## Identificação

- Data da inspeção: 11 de setembro de 2026.
- Referência funcional: `v0.3.0` (`041da9e6333bf6a15cdecf29a0dd16af9d740d64`), em `main`.
- Classificação: auditoria de arquitetura operacional; M; risco baixo.
- Escopo: registrar fatos existentes; não autoriza V0.4, A2 ou mudança funcional.

## Estado Git e inventário essencial

Na inspeção, `git status --short` não retornou entradas: a árvore estava limpa antes deste documento. O remoto configurado é `origin`, apontando para o repositório GitHub do projeto; nenhuma credencial é registrada aqui.

O repositório contém produto Django em `src/`, testes em `tests/`, gate e evidências em `scripts/` e `quality/`, documentação em `docs/`, e estado operacional em `AGENTS.md`, `PROJECT_STATE.md` e `tasks/`. Ambientes, caches e artefatos locais ignorados incluem `.venv`, `.tools`, caches e `var/`.

## Arquitetura operacional atual

`AGENTS.md` (174 linhas, aproximadamente 5 KB) é um mapa operacional conciso, não uma especificação duplicada. Ele define como fontes de verdade, em ordem: código/migrations, testes, ADRs, documentação formal, estado e tarefa atual; exige a leitura de `PROJECT_STATE.md`, `tasks/current.md`, `docs/README.md` e fontes diretamente aplicáveis. Também fixa escopo por tarefa, ADRs, testes, gate, atualização de estado/arquivamento e commit somente autorizado.

O fluxo efetivamente prescrito e materializado é:

`entrada da tarefa` → `AGENTS.md` → `PROJECT_STATE.md` → `tasks/current.md` → documentação/ADRs pertinentes → implementação → testes específicos → `scripts/quality.ps1` → estado → arquivamento em `tasks/completed/` → Git autorizado → novo chat.

O repositório é a memória permanente. A autorização pontual, a conversa, a escolha de modelo e o raciocínio permanecem externos; por isso, o início de uma atividade ainda depende de prompt/chat ou de atualização manual da tarefa atual.

## Estado, tarefas e documentação

`PROJECT_STATE.md` (114 linhas, cerca de 5 KB) declara V0.3 promovida, E5 concluída, sem P0/P1 aplicável, último gate GREEN, 280 testes e 87% de cobertura. Seu encerramento ADR-014 confirma explicitamente que V0.4 não foi iniciada. O arquivo preserva blocos históricos pré-ADR-013 que dizem “não promovida”; títulos cronológicos e o fechamento final resolvem a cronologia, mas tornam o resumo mais detalhado e repetitivo do que o necessário.

`tasks/current.md` tem 8 linhas e declara “Nenhuma tarefa autorizada”; registra V0.3 promovida e permite apenas planejamento futuro de V0.4 sob nova autorização. No estado observado, não possui campos estruturados de versão, etapa, objetivo, escopo, fora de escopo, documentos, ADRs, critérios, testes ou gate. `tasks/completed/` contém 15 Markdown, nomeados por versão/etapa ou assunto; são memória histórica, não insumo normal da execução atual, salvo consulta para auditoria, regressão ou recuperação de decisão.

Há uma divergência de rastreabilidade: A1 foi autorizada pela instrução externa desta execução, mas não está registrada em `tasks/current.md`. O arquivo não foi alterado porque A1 mede o formato atual. A2 deverá decidir como uma autorização externa passa a ser persistida antes da execução, sem tratar o chat como memória permanente.

`docs/README.md` (926 linhas, cerca de 23 KB) é o índice das dez etapas do produto, 14 ADRs, documentos de gate/release e três artefatos operacionais externos a `docs/`. ADRs, Roadmap, Plano de Testes e documentos formais ficam em `docs/`; `quality/` e tarefas concluídas são evidências históricas versionadas. Há sobreposição controlada entre AGENTS e o índice operacional, e entre estado, tarefas arquivadas e resultados de qualidade; os contratos são distintos, mas a manutenção manual permite desatualização.

## Gate e testes existentes

O gate autoritativo é `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1`. Ele valida lock e ambiente `uv`, runtime fixado, rastreabilidade contra `quality/v03-stage5-gate.json`, checks Django nos perfis development/test/production local, migrations inesperadas e banco vazio, Ruff format/lint, mypy estrito, pytest com cobertura e meta de domínio, detect-secrets e `pip-audit`. Usa diretório temporário GUID para pytest e falha em qualquer etapa obrigatória. Não foi alterado nem executado nesta inspeção.

A evidência promovida informa 280 testes e 87% de cobertura global. A suíte tem 20 módulos, incluindo contas/tempo/configuração, catálogo/interface/busca, backup-restauração, fundação e operações de aprendizagem, tentativa inicial, conclusão de revisão, fila/timeline, gate, BCR-1 e promoção E5. Há provas de migrations, isolamento de Workspace, rollback/idempotência, segurança/segredos, backup e BCR-1. Uma execução comparável do gate registrada na validação ADR-013 levou 89,9 s; é dado histórico, não medição desta A1.

## Métricas disponíveis

| Categoria | Situação observada |
| --- | --- |
| Testes, cobertura e resultado do gate | Versionados em `PROJECT_STATE.md` e `quality/` (280, 87%, GREEN). |
| Duração do gate | Registro histórico de 89,9 s na validação ADR-013. |
| Desempenho BCR-1 | Versionado em `quality/v03-bcr1-result.json`, com ambiente e tempos. |
| Modelo, reasoning, cotas de 5 h/semanais | Ausentes do repositório; conhecidos apenas no ambiente/chat. |
| Quantidade de arquivos por tarefa | Ausente como métrica versionada. |
| Gate na primeira tentativa, retrabalho, tentativas e escalonamento de modelo | Ausentes como métricas versionadas. |

## Comparação com a arquitetura operacional proposta

| Item futuro a avaliar | Situação A1 | Evidência ou limite |
| --- | --- | --- |
| Repositório como memória e fluxo sequencial | JÁ COMPATÍVEL | AGENTS, estado, tarefas arquivadas e gate. |
| Índice para documentos e ADRs | JÁ COMPATÍVEL | `docs/README.md`; não requer reorganização. |
| Tarefa atual como contrato estruturado | PARCIAL | Arquivo existe, mas sem campos e A1 foi autorizada externamente. |
| Gate único, bloqueante e evidenciável | JÁ COMPATÍVEL | Script, manifestos e resultados versionados. |
| Baseline de métricas de qualidade/desempenho | PARCIAL | Há testes/cobertura/gate/BCR-1, sem série por tarefa. |
| `.codex/config.toml` | AUSENTE | Não criar nesta A1. |
| `.agents/skills/` | AUSENTE | Não criar nesta A1. |
| `tasks/plans/` | AUSENTE | Não criar nesta A1. |
| `docs/review/code-review.md` ou equivalente formal | AUSENTE | Não criar nesta A1. |
| Telemetria de modelo, reasoning, cotas e escalonamento | AUSENTE | Exige decisão futura de escopo, privacidade e retenção. |
| Guia operacional e índice operacional | POSSÍVEL DUPLICAÇÃO | AGENTS e README se sobrepõem de modo controlado. |
| Taxonomia A2, formatos e governança de revisão | PRECISA DE DECISÃO FUTURA | Fora do escopo da baseline. |

## Riscos, preservações e critérios A1

Riscos: autorização pode existir apenas no chat; resumos históricos extensos podem parecer contraditórios fora de ordem; e métricas de processo não possuem coleta versionada. Permanecem preservados produto Django, arquitetura funcional, migrations, gate, manifestos, histórico de qualidade, estrutura de `docs/`, AGENTS, PROJECT_STATE, tarefa atual, Git e tag.

- [x] Referência funcional `v0.3.0` identificada.
- [x] Git, fluxo, AGENTS, estado, tarefas, docs, ADRs, gate e testes auditados.
- [x] Métricas existentes separadas das ausentes; itens futuros apenas classificados.
- [x] Nenhuma mudança funcional, A2 ou V0.4 iniciada.
- [x] Nenhum commit, branch, tag, push ou release realizado.
- [x] `git diff --check` após a criação do documento — aprovado (exit code 0).

## Recomendação objetiva para A2

Formalizar primeiro um contrato versionado mínimo de tarefa/planejamento que persista autorização, escopo, risco, evidência e resultado sem duplicar a documentação de produto; somente então decidir configuração, skills, revisão e métricas de processo.
