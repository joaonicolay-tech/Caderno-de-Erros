# V0.4-S7 — Evidência operacional e review A8

Data: 2026-09-16. Autoridade: contrato V0.4-S7; M/medium. A baseline Project
Development Architecture v1.0 foi preservada.

## Resultado observado

- Auditoria: o `uv`/lock, Python 3.13.15, perfis SQLite `CEI_*`, logs JSON e
  interfaces S5/S6 existentes são adequados; startup/Explorer e guia operacional
  eram parciais. Não havia instalador ou serviço.
- Escolha: `scripts/start-local.ps1`, com `.venv` obrigatória, raiz derivada de
  `$PSScriptRoot`, Python 3.13.15, loopback `127.0.0.1`, porta 8000 e
  `--noreload`. O wrapper `scripts/start-local.cmd` aplica ExecutionPolicy Bypass
  somente ao processo aberto pelo Explorer. Não há fallback silencioso ao Python
  global, migração, bootstrap, backup, download ou abertura de navegador no
  startup.
- Ensaio descartável: banco development temporário migrado/bootstrapado apenas
  para o ensaio; entry point iniciado de diretório externo; `GET /health/` em
  `127.0.0.1:8017` retornou saudável; shutdown controlado liberou a porta.
  S5 retornou exit 0 (17 checks, 0 findings); S6 criou e validou backup de
  655.360 bytes. Diretórios descartáveis foram removidos. Não foi realizado
  restore destrutivo, teste com banco real, piloto ou S8.

## Review A8 padrão

Revisão pelo agente executor do contrato, diff, scripts, documentação, testes e
ensaio; não é aprovação humana independente. Resultado: **APPROVED**, sem
Blocker/Major aberto.

- Paths: derivados do script; nenhum caminho pessoal foi implementado.
- Rede e lifecycle: loopback explícito, porta ocupada falha com orientação sem
  matar processo; `--noreload` evita filho do autoreloader e o exit do Django é
  preservado.
- Segurança: sem segredo versionado; `production_local` exige chave de processo;
  wrapper não reduz ExecutionPolicy global.
- S5/S6: apenas compõe comandos e documenta exits/restore isolado; não duplica
  lógica nem introduz restauração sobre o banco principal.
- Atualização: sem auto-update, `git pull` implícito, reset ou migrations no
  startup. Não foram criados MSI, instalador, serviço, daemon ou launcher gráfico.

## Verificação e encerramento

- Testes focados: `tests/test_windows_operation.py`: **3 passed**, exit 0.
- `git diff --check`: exit 0.
- Gate autoritativo final fora da sandbox: **GREEN**, exit 0, **325 passed** em
  70,31 s, cobertura global **88%**, duração total 106,7 s; migrations,
  formatação, Ruff, mypy, detect-secrets e pip-audit aprovados, sem
  vulnerabilidades conhecidas. A primeira execução local ficou inconclusiva no
  pip-audit por `WinError 10013`; não foi considerada GREEN.

Sem P0/P1 aplicável, migration/schema, instalação sofisticada, restore
destrutivo, mudança de S1-S6, S8/S9, commit, push, tag ou release.
