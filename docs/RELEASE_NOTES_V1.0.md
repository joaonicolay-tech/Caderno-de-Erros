# Caderno de Erros Inteligente V1.0 — RELEASE CANDIDATE

**Estado:** documentação candidata. V1.0 ainda não foi promovida nem publicada
como tag `v1.0.0` ou GitHub Release estável. Estas notas não são anúncio de
release nem instrução para baixar uma versão inexistente.

## Identidade e plataforma

- Produto: `V1.0`.
- Pacote/aplicação: `1.0.0`.
- Exportação funcional: `CEI-EXPORT-1.0`, `format_version=1.0`.
- Plataforma documentada: Windows 11 x64, uso individual local em loopback.
- Instalação pelo checkout fornecido, `uv 0.12.7`, Python `3.13.15`, lock
  `uv.lock` e `scripts/start-local.ps1`; não há instalador nativo.

## Capacidades

A candidata reúne catálogo local de questões e tentativas, ciclos e agenda de
revisão, classificação/taxonomia, recomendações explicáveis com limites de
evidência, exportação/importação CEI para destino compatível vazio, backup
SQLite, validação, restauração isolada e recovery offline preparado na interface.
Os procedimentos estão no [guia operacional V1](V1.0_Operacao_Local.md) e no
[índice documental](README.md).

## Compatibilidade e dados

- A cadeia de upgrade de dados comprovada em S6 parte de V0.4.4, passa por
  V0.5 e chega à aplicação V1. Não se promete downgrade automático.
- Export funcional CEI e backup SQLite têm finalidades diferentes. Importação
  CEI exige instalação compatível e vazia; não oferece merge, conversão,
  coerção, adaptação de schema, importação parcial ou repair.
- Backup requer manter arquivo e manifesto juntos. Restore de verificação usa
  sempre destino novo e isolado; recovery preparado é offline e exige aplicação
  parada e pré-backup validado.
- Não há agenda/rotação automática de backups nem cópia em nuvem.

## Navegadores

Conforme o [adendo S4](V1.0_Adendo_V10-D2_Matriz_de_Browsers_S4.md):

| Browser | Estado declarado para V1 |
| --- | --- |
| Brave 1.96.59, Windows 11 x64, configuração padrão e extensões desabilitadas | VALIDADO OFICIALMENTE PARA V1 |
| Chrome | NOT_EXECUTED / NOT VALIDATED |
| Edge | NOT_EXECUTED / OPTIONAL |
| Firefox atual e imediatamente anterior | NOT_EXECUTED / OPTIONAL |
| Safari | N/A — não aplicável à plataforma oficial Windows 11 x64 |

Não se declara suporte mobile nem amplia a matriz para outros navegadores.

## Segurança, integridade e limites conhecidos

O checker de integridade é read-only. A validação física de backup não
autentica o autor; o hash detecta alteração, mas não prova origem nem a escolha
do ponto de recuperação. Recovery requer ticket preparado, aplicação parada e
reconciliação após a retomada. A aplicação é individual/local: não oferece
autenticação remota, hospedagem pública, API pública ou operação remota
multiusuário. Não há update/downgrade automático, SLA operacional ou garantia
de RPO/RTO.

## Changelog

`NO_EXISTING_CHANGELOG_CONVENTION`: a busca pelo repositório não encontrou um
arquivo ou convenção de changelog. Estas release notes registram os fatos da
candidata sem criar uma convenção independente. Notas históricas V0.1 e
documentos V0.x permanecem preservados.

## Suporte e limitações

O suporte da candidata é documental. A página pública do projeto oferece
[GitHub Issues](https://github.com/joaonicolay-tech/Caderno-de-Erros/issues)
para registrar defeitos; isso não implica garantia de leitura, resposta, prazo,
suporte comercial, 24/7 ou manutenção contratual. Não há compromisso de SLA.

Use o [guia operacional V1](V1.0_Operacao_Local.md) e o [README do produto](../README.md).
