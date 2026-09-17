# V0.4-S7 — Operação Windows

Status: COMPLETED

## Contract preserved at closure

- Task ID: `V0.4-S7`; product V0.4; size M; risk medium.
- Goal: tornar a aplicação local Windows simples de iniciar, operar, proteger,
  diagnosticar e atualizar, reutilizando S5/S6 e priorizando o mínimo
  operacional confiável.
- Expected scope: auditoria do fluxo Windows, entry point PowerShell/batch ou
  mecanismo de atalho mínimo, mensagens recuperáveis, composição documental de
  S5/S6, guia, ensaio, métricas/review e encerramento.
- Protected scope: domínio, S1-S6, schema/migrations, S8/S9, Architecture v1.0,
  Skills, `quality.ps1`, instalador, serviço, daemon, auto-updater e launcher
  gráfico.
- Constraints: loopback por padrão; sem paths pessoais, Python global silencioso,
  porta aleatória, processo arbitrariamente encerrado, secret, restore
  destrutivo, commit/push/tag/release ou antecipação de S8.

## Closure evidence

- Auditoria e guia: `docs/V0.4_S7_Operacao_Windows.md`.
- Entry points: `scripts/start-local.ps1` e `scripts/start-local.cmd`.
- Testes focados: 3 passed, exit 0.
- Ensaio descartável: startup de diretório externo, health loopback, shutdown e
  porta liberada, S5 exit 0 e backup/validação S6 de 655.360 bytes.
- Review A8 padrão: **APPROVED**, sem Blocker/Major.
- `git diff --check`: exit 0.
- Gate: **GREEN**, exit 0; 325 passed em 70,31 s; cobertura 88%; duração total
  106,7 s. A primeira tentativa ficou inconclusiva no pip-audit por sandbox
  `WinError 10013`; a repetição autorizada com rede aprovou.

Nenhuma migration/schema, instalador, serviço, auto-updater, restore destrutivo,
S8/S9, commit, push, tag ou release foi realizado. S8 continua não autorizada.
