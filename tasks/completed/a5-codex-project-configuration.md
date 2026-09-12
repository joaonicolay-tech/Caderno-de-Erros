# A5 — Configuração versionada do Codex

Status final: concluída e arquivada em 11 de setembro de 2026.

## Identification

- Task ID: A5
- Product version: pós-V0.3 / pré-V0.4; V0.4 não iniciada
- Stage: A5 — configuração versionada do Codex
- Task type: operational architecture
- Size: M
- Risk: low

## Resultado

Nenhum `.codex/config.toml` ou arquivo `.codex/rules/*.rules` foi criado. A
configuração mínima correta para este repositório continua sendo o
`AGENTS.md` raiz, descoberto nativamente pelo Codex, com
`tasks/current.md` como autoridade de escopo e as demais fontes consultadas
por referência. Criar uma camada `.codex/` sem efeito útil tornaria a política
menos clara, não mais reproduzível.

O `.gitignore` passou a excluir explicitamente `.codex/auth.json`. O arquivo
de autenticação pessoal existente permaneceu fora do repositório, não foi
lido e nenhum segredo foi versionado.

## Ambiente e recursos verificados

- Codex CLI `0.153.0`, fornecido pela extensão OpenAI ChatGPT para VS Code;
- Codex Desktop instalado em `26.903.9818.0`;
- `codex doctor --json --all`: configuração pessoal carregada e parseada,
  repositório Git reconhecido e sandbox restrita operacional; o status global
  `fail` veio apenas de `TERM=dumb` na execução não interativa, sem falha de
  configuração;
- `.codex/config.toml` é uma camada oficial de projeto e só é carregada em
  projeto confiável;
- `project_doc_fallback_filenames` é suportada como lista de nomes adicionais
  tentados depois de `AGENTS.override.md` e `AGENTS.md` em cada diretório;
- rules project-scoped são carregadas de `.codex/rules/` em projeto confiável,
  usam Starlark, podem ser verificadas por `codex execpolicy check` e são
  classificadas pela documentação oficial como experimentais.

Fontes oficiais verificadas em 11 de setembro de 2026:

- <https://developers.openai.com/codex/config-basic>
- <https://developers.openai.com/codex/config-reference>
- <https://developers.openai.com/codex/guides/agents-md>
- <https://developers.openai.com/codex/rules>

## Classificação das opções

| Classe | Opções avaliadas | Decisão A5 |
| --- | --- | --- |
| Versionável no projeto | `project_doc_fallback_filenames`, `project_doc_max_bytes`, sandbox/approval defaults e rules | Todas suportadas, mas nenhuma justificada no estado atual; não versionar configuração sem efeito concreto. |
| Pessoal/global | autenticação, tokens, conta, modelo padrão, reasoning, service tier, plugins, MCP, interface, notificações, paths e confiança do checkout | Permanecem em `~/.codex/` ou na gestão do ambiente; nunca copiar ao repositório. |
| Temporária por execução | modelo, reasoning, perfil, sandbox, approval e overrides `-c` usados para uma execução específica | Permanecem em flags, perfil pessoal ou contexto da execução. |
| Não suportada/não justificada | tratar `PROJECT_STATE.md` como fallback universal; repetir `AGENTS.md` no fallback; features experimentais sem necessidade | Não adicionar. A configuração não deve alterar a hierarquia de fontes nem antecipar A6/A7. |

## Decisão sobre descoberta de instruções

A proposta
`project_doc_fallback_filenames = ["AGENTS.md", "PROJECT_STATE.md"]` não foi
adotada. `AGENTS.md` já precede fallbacks e repeti-lo não muda a descoberta.
`PROJECT_STATE.md` só seria lido quando não houvesse `AGENTS.md` no mesmo
diretório; isso o promoveria indevidamente de estado consultado sob as regras
de A3 para instrução automática. O `AGENTS.md` raiz tem aproximadamente 5,4 KB,
abaixo do limite padrão de 32 KiB, portanto `project_doc_max_bytes` também não
precisa de override.

Um novo agente deve iniciar por `AGENTS.md`, que o encaminha ao contrato
`tasks/current.md` e à política de progressive disclosure. A ausência de
`.codex/config.toml` não é uma lacuna: indica que nenhum override de cliente é
necessário para interpretar o repositório.

## Decisão sobre rules

Não foram criadas rules. O mecanismo controla comandos solicitados fora da
sandbox; não substitui as restrições do contrato, o gate nem autorização Git.
Os comandos de leitura (`git diff/status/log/show`, `Get-ChildItem`,
`Get-Content`, `Select-String` e `Test-Path`) já cabem na sandbox. `pytest` e
`python -m pytest` escrevem apenas artefatos locais previstos e continuam sob a
política normal. `git add` altera o índice e `git commit` altera o histórico;
não devem receber autorização automática, especialmente porque commits exigem
autorização expressa. A natureza experimental das rules reforça a ausência de
benefício arquitetural para versioná-las nesta etapa.

## `.gitignore`

Antes de A5, `.venv/`, `.pytest_cache/`, `.coverage` e `htmlcov/` já estavam
ignorados sem duplicação. Foi acrescentada somente `.codex/auth.json`. Nenhuma
regra foi reorganizada por estética.

## Escopo preservado

Não houve alteração em código Django, testes, migrations, regras de negócio,
gate ou evidência histórica. A6–A10 e V0.4 não foram iniciadas. Não houve
commit, push, tag ou release.

## Verificação

- `git diff --check`: aprovado antes do gate;
- `powershell -NoProfile -ExecutionPolicy Bypass -File
  .\scripts\quality.ps1`: GREEN em 92,7 s, exit code 0, 280 testes aprovados
  em 59,13 s e 87% de cobertura global; migrations, Ruff, mypy,
  detect-secrets e auditoria de vulnerabilidades aprovados;
- `.codex/auth.json` confirmado como ignorado, sem arquivo Codex rastreado;
- inspeção final de escopo e de `tasks/current.md`: concluída após o gate.

## Próximo estado

Após a verificação final, não haverá tarefa autorizada. A6 e qualquer etapa
posterior exigem nova autorização formal em novo chat.
