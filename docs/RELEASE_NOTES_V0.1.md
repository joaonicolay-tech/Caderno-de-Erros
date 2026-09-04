# Notas da versão V0.1 — Fundação executável

- **Estado:** PROMOVIDA
- **Data:** 2026-09-03
- **Gate:** aprovado
- **Instalação Windows limpa:** `CT-127` PASS
- **Chrome/Edge e acessibilidade base:** `CT-136` PASS

## Entregas

- toolchain Windows reproduzível com Python, Django, HTMX e dependências fixadas;
- perfis separados de desenvolvimento, teste e produção local;
- User UUID, Workspace local, locale `pt-BR` e fuso IANA explícito;
- dez categorias padrão com seed idempotente;
- interface local mínima para primeiro acesso, início e configuração de fuso;
- Clock/Calendar substituíveis em testes;
- logging estruturado e sanitizado, correlação e health local;
- migrações iniciais protegidas e verificadas desde banco vazio;
- backup, validação e restauração técnica mínima do SQLite;
- gate único com análise estática, testes, cobertura, segredos, vulnerabilidades,
  rastreabilidade e integridade de migrações.

## Evidências de promoção

- instalação isolada sem ambiente virtual, cache, runtime, banco ou configuração
  privada anteriores;
- 1 User, 1 Workspace, locale `pt-BR`, fuso `America/Sao_Paulo` e 10 categorias após
  bootstrap repetido;
- health saudável antes e depois da restauração isolada;
- `CT-127` aprovado;
- checklist integral de `CT-136` aprovada manualmente em Chrome `152.0.7977.65` e
  Edge `152.0.4191.53`;
- nenhum P0/P1 aplicável nem defeito S1/S2 conhecido na promoção;
- decisão formal em `ADR-009`.

## Limites

A V0.1 é uma fundação técnica, não o produto de estudo. Questões, tentativas,
revisões, dashboard, busca, métricas, categorias pessoais, autenticação remota, API,
notificações e PWA permanecem em versões posteriores. `CT-128` completo continua no
gate V0.4/V1. Não houve publicação externa.
