# V1.0-S7R2 — Prova operacional de update e encerramento

START_TIME: 2026-10-03 18:02:20 -03:00
END_TIME: 2026-10-03 18:45:01 -03:00
Baseline: HEAD == origin/main == ac13fb2c5023fbb1c6ccc69ab4059d0367f899ea

## Decisão

S7-F02 RESOLVED. S7-F01 permanece RESOLVED por S7R1. Os critérios documentais e operacionais do contrato S7 foram satisfeitos. A revisão A8 padrão concluiu APPROVED WITH NOTES, sem Blocker ou Major aberto (0/0; 2 Minor não bloqueadores). S7 COMPLETED. Ver `quality/v10-s7r2-update-proof.json` e `quality/v10-s7r2-a8-standard.json`.

## Prova de update

Origem sintética isolada criada do tag histórico real `v0.5.0` (commit `c772a341f5cc25e270da8811d93074beb2506f95`), sem metadados `.git`; banco development sintético com 34 migrations aplicadas, 1 workspace, 1 disciplina, 1 matéria, 1 questão, 1 tentativa válida e 1 ciclo/revisão. Pré-backup físico validado; aplicação anterior parada antes do update. Bundle candidato final identificado por SHA-256 `2CD75AD46819E07CBDCB2205091F5711C07445BC31BBD33B25D861055BF100BC`.

`uv 0.12.7`; `uv sync --locked` concluído; Python 3.13.15. O hash de `uv.lock` da extração coincide com o bundle. `makemigrations --check --dry-run`: No changes detected; migrations antes/depois: 34; `migrate`: No migrations to apply. Checker antes/depois: 25 checks, 0 findings, exit 0. Health saudável e HTTP 200 em Início, Dados e questões; produto V1.0 e registro sintético visíveis.

Reconciliação física e semântica pós-update e pós-smoke: SHA do banco, SHA semântico das linhas, SHA do schema, contagens e IDs iguais à linha de base; `integrity_check=ok`; zero violações FK. O servidor candidato foi parado. Nenhuma restauração foi necessária nesta prova de update; os PASS prévios de backup, restore isolado e recovery offline permanecem referenciados no histórico S7.

## Documentação e auditoria

Guia operacional reconcilia instalação limpa, primeiro uso, update, backup, restore isolado, recovery offline, checker, troubleshooting e limites. O procedimento de update trata snapshots sem `.git`, valida SHA do bundle, extrai em pasta nova e preserva a origem; fixa perfil/banco em caminho absoluto e orienta a execução de migrations e checker. Links/comandos reconciliados com os alvos disponíveis e o comportamento documentado. Nenhum código, modelo, migration ou dependência foi alterado nesta retomada.

## Findings não bloqueadores

1. Minor: upload/seleção de arquivo na interface foi exercitado via cliente Django; a seleção manual em navegador continua não validada. O apply offline foi executado de ponta a ponta em prova anterior.
2. Minor: não foram fault-injected todos os ramos negativos de troubleshooting; referências foram comparadas com ajuda/código. Isso não contradiz as afirmações limitadas do guia.

Tentativa inicial de backup sem pasta de destino e erros intermediários de harness (captura de snapshot/comparador/PowerShell e guarda do processo) foram corrigidos e registrados como incidentes do harness; os dados permaneceram inalterados. Não são defeitos funcionais. Falhas e bloqueios históricos F01 e A8 anterior permanecem inalterados nos arquivos originais.

## Estado ao encerrar

A4 encerrado; inventory reconciliado; S7-F01/F02 RESOLVED; S7 COMPLETED. `tasks/current.md` retorna a NO_TASK_AUTHORIZED. Próxima etapa requer autorização própria. S8–S10 seguem NOT AUTHORIZED. CHECKPOINT_REQUIRED para decisão administrativa futura; nenhum `git add`, commit, push, tag ou release executado.
