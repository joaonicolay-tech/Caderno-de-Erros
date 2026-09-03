# ADR-008 — Gate único de qualidade e automação da V0.1

- **Status:** Aceita
- **Data:** 2026-09-03
- **Escopo:** Etapa 8 da V0.1
- **Requisitos:** `RNF-052`, `RNF-056`, `RNF-058`, `RNF-074`–`RNF-080`
- **Regras:** `RN-001`–`RN-005`, `RN-029`
- **Testes:** `CT-001`, `CT-002`, `CT-073`, `CT-074`, `CT-081`, `CT-099`,
  `CT-104`, `CT-123`, `CT-127`, `CT-129`–`CT-136`
- **Decisões relacionadas:** `ERR-V01-001`–`ERR-V01-009`, `RD-DEC-002`

## Decisão

`scripts/quality.ps1` é o gate autoritativo, reproduzível e bloqueante da V0.1 no
Windows. Ferramentas individuais continuam úteis durante o desenvolvimento, mas
somente a execução integral desse script representa o resultado do gate.

O script usa `Set-StrictMode`, `$ErrorActionPreference = "Stop"` e verifica o exit
code de cada processo. Qualquer etapa obrigatória interrompe a execução com código
não zero. Não existe parâmetro para omitir auditoria de vulnerabilidades, testes,
segredos ou outra fase obrigatória e a mensagem final de sucesso só é emitida depois
da última verificação.

## Ordem do gate

1. conferir `uv.lock` e sincronizar com `uv sync --locked`;
2. validar versões de Python, Django e SQLite e ida/volta UTF-8;
3. validar links Markdown, IDs, matriz executável da V0.1 e hashes das migrações;
4. executar checks dos perfis desenvolvimento, teste e produção local;
5. rejeitar models sem migração e migrar um SQLite vazio/descartável;
6. validar Ruff format e lint;
7. executar mypy estrito sobre `src`, `tests` e `scripts`;
8. executar pytest, cobertura de linhas/branches e os smokes existentes;
9. aplicar o mínimo documental de 80% de linhas a cada módulo atual de
   domínio/regras;
10. procurar segredos nos arquivos versionados e novos;
11. rejeitar qualquer vulnerabilidade conhecida no ambiente resolvido;
12. emitir sucesso e duração total somente após todas as etapas anteriores.

Os testes de backup/restauração já exercitam snapshots e bancos inteiramente
descartáveis; o gate reutiliza essa evidência e não repete um smoke destrutivo.

## Cobertura

Não se cria percentual global. O relatório global e de branches permanece visível,
mas o único limiar numérico bloqueante é o aprovado em `RNF-076` e no Plano de
Testes: 80% de linhas para cada módulo atual de domínio ou regra crítica. A lista
explícita em `quality/v01-gate.json` cobre tempo/calendário, bootstrap, identidade,
Workspace e categorias padrão. Acrescentar novo módulo de regras exige incluí-lo na
lista e fornecer casos positivos, negativos e de fronteira.

Não há percentual mínimo inventado para branches. A exigência de não reduzir
branches críticos é tratada pela matriz de casos e pela revisão dos cenários
positivos, negativos, de fronteira, rollback, corrupção e isolamento.

## Rastreabilidade e migrações

`scripts/verify_v01.py` usa `quality/v01-gate.json` como contrato executável. A
verificação bloqueia:

- links Markdown locais inexistentes;
- definição duplicada de IDs canônicos `RF`, `RNF`, `RN`, `FL`, `CT`, `ERR-V01` e
  `ADR`;
- ID obrigatório da V0.1 sem definição;
- referência central da V0.1 a ID inexistente;
- CT aplicável sem teste, etapa do gate ou documentação permitida;
- alteração, remoção ou adição não registrada de migração histórica aprovada.

O escopo de referências é README e ADRs da implementação V0.1. Os problemas globais
de rastreabilidade formalmente adiados pelo Gate documental não são convertidos em
falhas artificiais desta versão.

Além dos hashes, `makemigrations --check --dry-run` comprova aderência entre models e
migrações, e `migrate` comprova ordem/aplicação desde banco vazio e inicialização do
Django. Uma mudança legítima futura deverá criar nova migração e atualizar o
manifesto por decisão revisada; alterar silenciosamente as migrações iniciais falha.

## Segurança

A política da ADR-001 permanece: `detect-secrets` não aceita segredo real e
`pip-audit --local --strict` bloqueia qualquer vulnerabilidade conhecida por padrão.
Exceção de vulnerabilidade exige registro e aprovação formal; o gate não oferece
switch de bypass. Bancos, backups, `.env` e relatórios locais continuam ignorados.

## Decisão sobre CI

Não foi criado workflow específico de GitHub Actions, Azure Pipelines ou outro
provedor. O repositório não possui remoto configurado e nenhum provedor foi aprovado;
escolher um nesta etapa introduziria infraestrutura externa sem requisito funcional.

Isso não adia o gate: `quality.ps1` é executável localmente e por qualquer runner
Windows. Quando um provedor for escolhido, seu workflow deverá somente preparar o
Windows e invocar o mesmo script, sem copiar etapas, reduzir checks ou usar segredos
de produção. A execução efetiva nesse provedor será evidência adicional, não uma
segunda definição de qualidade.

## Evidência negativa

Testes automatizados do verificador confirmam código de saída não zero para cobertura
abaixo de 80%, link quebrado, definição duplicada, evidência de CT inexistente e hash
de migração alterado. O próprio script PowerShell verifica todo processo filho e
interrompe por `throw`; os arquivos reais do repositório não são corrompidos para
produzir essas provas.

## Situação dos CTs

- `CT-001`, `CT-002`, `CT-073`, `CT-074`, `CT-081`, `CT-099`, `CT-104`, `CT-123` e
  `CT-129`–`CT-135` possuem evidência executável integrada ao gate.
- `CT-127` possui README e automação preparados, mas a instalação limpa independente
  e a aprovação definitiva pertencem à Etapa 9.
- `CT-136` possui evidência estrutural automatizada de semântica, foco, responsividade
  e contraste; o smoke final em Chrome/Edge, teclado e zoom permanece evidência da
  Etapa 9. Não é declarado integralmente encerrado nesta ADR.
- Capacidades futuras citadas por `RNF-075`, `RNF-077` e `RNF-078` — cálculos de
  tentativa/revisão/métricas/domínio, ciclo completo e `BCR-1` volumoso — só entram
  quando seus módulos existirem. Sua ausência planejada não falha a V0.1.

Esta etapa prepara uma decisão objetiva de promoção, mas não promove a V0.1, não cria
tag e não substitui a execução independente de instalação/smoke da Etapa 9.
