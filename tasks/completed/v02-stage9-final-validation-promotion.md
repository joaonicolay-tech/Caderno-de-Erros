# V0.2 — Etapa 9 — Validação Final e Promoção

## Identificação

- Versão: V0.2.
- Etapa: 9.
- Status: formalmente liberada em 7 de setembro de 2026; não iniciada.
- Pré-requisito: Etapa 8 concluída e arquivada em
  `tasks/completed/v02-stage8-fixture-accessibility-backup-integration-regression.md`,
  com `CT-142` integralmente PASS e gate final GREEN, exit code 0.

## Objetivo

Confirmar de forma independente a prontidão completa da V0.2 e, somente se todos os
critérios permanecerem aprovados, registrar a decisão formal de promoção da versão.
A etapa é de validação e registro: não cria capacidade de produto nova.

## Escopo

- revisar a evidência consolidada das Etapas 0–8, com destaque para a evidência manual
  de `CT-142`, fixture (`CT-141`), backup/recovery (`CT-143`), instalação/upgrade e
  regressão;
- executar as verificações e smoke tests estritamente necessários à promoção, em
  ambientes isolados; repetir o gate autoritativo e exigir exit code 0;
- conferir a integridade da baseline `v0.1.0`, as migrations protegidas e a ausência
  de P0/P1 aplicável aberto;
- produzir o registro formal de validação/promoção V0.2, atualizar o estado e arquivar
  a própria tarefa somente após resultado GREEN;
- registrar explicitamente a decisão sobre qualquer commit ou tag local, sem executar
  commit, push, tag ou release sem autorização expressa.

## Fora de escopo

- implementar V0.3, incluindo `Attempt`, classificação de erro, ciclo/fila/revisões
  de aprendizagem, histórico, métricas, dashboard ou qualquer entidade futura;
- alterar funcionalidade, modelo, migrations, dependências, arquitetura ou interface
  sem defeito concreto que bloqueie a promoção;
- iniciar a V0.3, mesmo que a V0.2 seja promovida;
- commit, push, tag ou release.

## Fontes obrigatórias

- `docs/Caderno_de_Erros_Inteligente_Etapa_9_Roadmap (1).md`, §§5.1–5.7 e §6;
- `docs/ADR-010_Fronteira_Rastreabilidade_e_Dados_V0.2.md`, §§2.1–2.3 e §§4–6;
- `docs/ADR-008_Gate_Unico_de_Qualidade_V0.1.md` e
  `docs/ADR-009_Validacao_Final_e_Promocao_V0.1.md` como referência de gate e
  encerramento;
- `docs/Caderno_de_Erros_Inteligente_Etapa_10_Plano_de_Testes.md`, sobretudo
  `CT-081`, `CT-082`, `CT-122`, `CT-123`, `CT-141`, `CT-142`, `CT-143` e `CT-144`;
- `quality/v02-stage8-automated-result.md` e os resultados das Etapas 1–7.

## Critérios objetivos de aceite

- todos os critérios da V0.2 no Roadmap §5.4 e a evidência de avanço §5.7 estão
  demonstrados, sem capacidade de aprendizagem fictícia;
- `CT-141`, `CT-142` e `CT-143` estão PASS, e as provas de banco vazio/upgrade,
  regressão e migrations permanecem válidas;
- gate autoritativo GREEN com exit code 0, cobertura e metas de domínio atendidas;
- nenhum P0/P1 aplicável ou defeito crítico de integridade, segurança, backup,
  migração ou acessibilidade permanece aberto;
- decisão de promoção fica explícita e rastreável; a próxima versão não é iniciada.

## Gate obrigatório

`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1`

Exit code diferente de 0 bloqueia a promoção da V0.2.

## Resultado da execução

- evidência consolidada das Etapas 0–8 revisada, incluindo `CT-141`, `CT-142`,
  `CT-143`, instalação/upgrade, regressão, migrations e baseline `v0.1.0`;
- smoke isolado de promoção: 8 testes aprovados;
- gate autoritativo: GREEN, exit code 0, em 56 s, com 192 testes aprovados,
  86% de cobertura global e metas de domínio/regra atendidas;
- nenhum P0/P1 aplicável ou defeito crítico permanece aberto;
- V0.2 promovida formalmente; registro detalhado em
  `quality/v02-stage9-promotion-result.md`;
- nenhuma etapa futura foi antecipada. Não houve commit, tag, push ou release,
  pois não foram autorizados.
