# V1.0-S7 — documentação operacional e candidato de release

- **Estado:** `BLOCKED` — prova obrigatória de update a partir de instalação anterior não executada.
- **START_TIME:** 2026-10-03 17:16:05 -03:00
- **END_TIME:** 2026-10-03 17:46:13 -03:00
- **Duração observada:** 0:30:08
- **Baseline:** `HEAD == origin/main == ac13fb2c5023fbb1c6ccc69ab4059d0367f899ea` (sem publicação durante a execução).
- **A4:** aprovado, `quality/v10-s7-a4-review.json`; plano ACTIVE.
- **A8:** `BLOCKED`, 0 blocker / 1 major / 2 minor, `quality/v10-s7-a8-standard.json`.
- **Classificação:** M / medium / migration expectation NO / dados reais NO / A7 conforme seleção registrada no contrato; identidade runtime não verificada.

## Trabalho concluído

- Reconciliados README, índice de documentação, guia operacional V1 e notas de release candidata; guias V0.4/V0.5 foram marcados como históricos sem reescrever seu conteúdo. CEI foi alinhado ao código/testes para produtores V0.5 e V1.0 sem mudar contrato ou comportamento.
- Versões, browser claims S4, suporte, limitações, estado de candidato/não promoção, instalação, primeiro uso, update, backup, restore, recovery e troubleshooting foram documentados. Nenhuma convenção de changelog foi localizada; release notes específicas foram usadas.
- CT-127 executado em cópia sintética Windows 11 25H2 x64, sem `.git`, `.venv`, banco ou configuração herdados: uv 0.12.7, Python 3.13.15, Django 5.2.17, `uv sync --locked` exit 0, migrations exit 0, servidor local/health e primeiro uso sintético PASS.
- Checker: HEALTHY, 25 checks, 0 findings. Backup SQLite e manifesto criados/validados; restore em arquivo novo passou, `integrity_check=ok`, zero violações FK e SHA-256 igual.
- Recovery de interface: endpoint Django `preview` e `confirm` passaram usando o cliente de teste porque o navegador disponível não expôs seletor de upload suportado; com o servidor parado, `apply_prepared_restore` retornou `RESTORED` e hashes do banco ativo, candidato e pré-backup coincidiram. Isto não equivale a validação manual do upload no navegador.
- `makemigrations --check --dry-run`: `No changes detected`.
- Hashes de `src/config/settings/base.py`, `src/templates/base.html`, `tests/test_interface.py`, `src/shared/application/context_processors.py`, `pyproject.toml` e `uv.lock` coincidem com os hashes registrados antes do trabalho; o gate funcional S7R1 mantém validade e não foi repetido.
- Auditoria local de links/âncoras e comparação de comandos com `manage.py help`: PASS. `git diff --check`: PASS.

## Finding aberto

**S7-F02 — Major — update operacional de instalação anterior não comprovado.**

O contrato S7 e o A4 exigem prova de atualização de código/dependências/migrations, partindo de instalação anterior isolada. A execução verificou os passos documentados e instalou o candidato do zero, mas não executou upgrade a partir de candidato previamente instalado. A checagem de migrations e o histórico S6 não substituem essa prova específica. Manter S7 `BLOCKED`; a documentação pode ser revisada, mas os critérios de conclusão ainda não foram satisfeitos.

## Limitações menores

1. O fluxo de upload e confirmação foi exercitado pelo cliente HTTP real do Django, não por seleção de arquivos em navegador; o apply offline foi executado de ponta a ponta.
2. Os ramos de falha de troubleshooting foram revisados contra código/ajuda/documentação, mas não todos fault-injected.

Uma checagem exploratória não documentada `manage.py check --deploy --settings=config.settings.production_local` foi tentada antes de se restringir ao perfil candidato development e falhou por ausência de segredo local exigido pelo perfil de produção; não foi tratada como prova de instalação ou falha do fluxo documentado, e sua saída não foi preservada em artefato versionável.

Nenhum gate integral foi repetido: os arquivos funcionais e de dependências mantiveram hashes iguais aos inputs aprovados no S7R1. Nenhuma alteração de modelo, schema, migration, dependência, comportamento funcional ou publicação Git foi realizada. S8–S10 continuam `NOT AUTHORIZED`.

**Decisão de encerramento desta retomada:** `BLOCKED`. Não declarar `S7_COMPLETED` enquanto S7-F02 não for fechado por prova autorizada e review A8 subsequente.

## Registro histórico preservado — tentativa inicial interrompida por S7-F01

Em 2026-10-02, a primeira execução documental foi interrompida às 19:57:56 -03:00 após 0:03:34, antes de alterações documentais ou CT-127. Seu baseline era `HEAD == origin/main == ac13fb2c5023fbb1c6ccc69ab4059d0367f899ea`; a árvore inicial continha os quatro artefatos planejados de S7 e `git diff --check` estava limpo.

**S7-F01 — Major — `V1.0` do produto não estava visível na interface HTML.** O contrato S1 exige versão visível ao usuário antes da entrega estável. `src/shared/application/version.py` já definia `PRODUCT_VERSION = "V1.0"`, consumida por logging e manifesto CEI, mas a busca nos templates não encontrou identidade de produto em HTML. O impacto era descumprimento contratual da superfície UI. A execução parou sem alterar código por falta de autorização funcional. A remediação autorizada e verificada consta em `quality/v10-s7r1-ui-product-version-result.md` e `tasks/completed/v10-s7r1-ui-product-version.md`; F01 está RESOLVED.

Naquela tentativa não foram executados CT-127, instalação, primeiro uso, update, backup, restore, recovery, troubleshooting, audit final de links, migration check ou A8. Nenhum dado real, configuração, dependência, schema ou migration foi alterado. O registro anterior permanece aqui como história; os resultados desta retomada estão acima e não convertem a falha histórica em PASS.

## S7R2 — fechamento posterior do bloqueio F02 (2026-10-03)

O estado BLOCKED acima é o resultado histórico da retomada anterior. S7-F02 foi fechado pela prova operacional isolada documentada em `quality/v10-s7r2-update-proof.json`; decisão A8 mais recente: APPROVED WITH NOTES, 0 Blocker / 0 Major / 2 Minor em `quality/v10-s7r2-a8-standard.json`. O relatório e os detalhes estão em `quality/v10-s7r2-execution-report.md`. S7 COMPLETED; F01/F02 RESOLVED. A evidência histórica de falha F01 e o A8 bloqueado inicial não foram reescritos.

No bundle final, `uv sync --locked` passou, migrations ficaram inalteradas (34; `No changes detected`; `No migrations to apply`), checker retornou 25/0, health e telas-chave responderam 200, e hashes/IDs/contagens do banco e schema ficaram iguais. Origem e dados eram sintéticos e isolados. O servidor foi parado após o smoke.

Dois findings Minor permanecem sem bloquear: seleção manual de arquivo no navegador não validada (cliente Django exercitou UI e recovery offline passou em prova anterior); nem todos os ramos de troubleshooting foram fault-injected. Nenhum gate integral foi repetido pois hashes funcionais e de dependências permaneceram iguais aos inputs S7R1 aprovados. Nenhuma operação Git de publicação ocorreu. S8–S10 seguem NOT AUTHORIZED.
