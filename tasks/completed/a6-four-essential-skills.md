# A6 — Quatro Skills essenciais

Status final: concluída e arquivada em 11 de setembro de 2026.

## Identification

- Task ID: A6
- Product version: pós-V0.3 / pré-V0.4; V0.4 não iniciada
- Stage: A6 — quatro Skills essenciais
- Task type: operational architecture / Codex workflow automation
- Size: M
- Risk: medium
- Modelo observado: `gpt-5.6-sol`
- Reasoning observado: `medium`

## Resultado e necessidade

A auditoria de A2–A5, `AGENTS.md`, tarefas encerradas e `scripts/quality.ps1`
confirmou quatro workflows repetitivos significativos que antes precisavam ser
recompostos em cada tarefa. As quatro candidatas foram, portanto, criadas:

- `start-task`: valida e prepara uma tarefa já autorizada; nunca autoriza;
- `implement-current-task`: executa somente o contrato corrente e seus limites;
- `run-quality-gate`: executa e interpreta `scripts/quality.ps1` sem duplicá-lo;
- `finish-task`: exige evidência de conclusão antes de arquivar e não autoriza a próxima tarefa.

Cada Skill tem uma responsabilidade e pode ser invocada separadamente. A
sequência conceitual `start-task` → `implement-current-task` →
`run-quality-gate` → `finish-task` não é pipeline automático.

## Formato, fontes e duplicação

O Codex CLI 0.153.0 e a documentação oficial vigente confirmaram
`.agents/skills/<nome>/SKILL.md` como localização de repositório. Cada arquivo
usa somente o frontmatter obrigatório `name` e `description`, seguido das
instruções; nenhum script, referência auxiliar ou metadata de UI foi necessário.

As Skills referenciam `AGENTS.md`, `tasks/current.md`, A2, A3, a política A4,
`PROJECT_STATE.md` quando aplicável e `scripts/quality.ps1`, sem copiar essas
fontes. A duplicação qualitativa final é baixa nas quatro Skills.

## Descoberta e testes operacionais

- Discovery: `codex debug prompt-input` listou as quatro Skills sob a raiz
  `C:/src/Projeto/.agents/skills`, com nomes, descrições e caminhos corretos.
- Teste A — sem tarefa: aprovado após o encerramento contra o
  `NO_TASK_AUTHORIZED` real; `start-task` impede implementação.
- Teste B — A6 autorizada: aprovado; Goal, Expected Scope, Protected Scope e
  Verification foram reconhecidos.
- Teste C — escopo protegido: aprovado; `implement-current-task` exige parada e
  reporte quando a correção estiver fora do escopo.
- Teste D — gate: aprovado; a Skill contém o comando de `scripts/quality.ps1` e
  não possui implementação ou script paralelo.
- Teste E — encerramento: aprovado; ausência, inconclusão ou falha da evidência
  impede arquivamento.
- Validação estrutural: `quick_validate.py` aprovou os quatro diretórios.

## Verificação

- `git diff --check`: aprovado antes e depois do gate.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1`:
  GREEN na primeira execução, exit code 0, em 128,6 s; 280 testes aprovados em
  82,49 s; cobertura global 87%; migrations, Ruff, mypy, detect-secrets,
  cobertura de domínio e auditoria de vulnerabilidades aprovados.

## Métricas

- Duração medida até o início do fechamento: aproximadamente 15 minutos
  (autorização persistida às 17:17:43; fechamento iniciado às 17:32:08,
  America/Sao_Paulo).
- Gate first pass: GREEN.
- Retrabalho: baixo e somente operacional — ajuste de quoting de metadata e
  correções no comando/harness de dry-run; nenhuma reescrita de responsabilidade.
- Arquivos finais alterados pela A6: 7, além da transição temporária de
  `tasks/current.md` que retornou ao baseline sem tarefa.
- Skills efetivamente criadas: 4.
- Falha de descoberta: nenhuma no Codex; o helper sandboxado desta sessão
  falhou ao fazer refresh dinâmico, contornado por sondagem direta somente leitura.

## Escopo preservado e próximo estado

Nenhum código Django, teste funcional, migration, gate, threshold, baseline ou
evidência histórica foi alterado. Não houve configuração pessoal, MCP,
integração, commit, push, tag ou release. A7 e V0.4 não foram iniciadas.

Não há tarefa autorizada. A7 ou qualquer trabalho posterior exige nova
autorização formal em `tasks/current.md` e nova execução.
