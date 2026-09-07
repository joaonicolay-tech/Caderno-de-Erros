# V0.2 — Etapa 9 — Validação final e promoção

Data: 7 de setembro de 2026 (UTC)

## Decisão

**V0.2 está formalmente promovida.** A decisão baseia-se exclusivamente nas
capacidades do Catálogo de Conteúdo aprovadas para esta versão; nenhuma capacidade
de aprendizagem foi inferida ou criada.

## Evidências revisadas

- Roadmap §§5.1–5.7: taxonomia, origem, rascunho/ativação, alternativas com um
  único gabarito, versionamento, detalhe, arquivamento, busca/filtros, formulário
  acessível e fixture estão demonstrados.
- Roadmap §6 e ADR-010 §§2.1–2.3 e 4–6: a fronteira V0.2 permanece preservada;
  `Attempt`, classificações de erro, ciclos/revisões, fila, histórico, métricas,
  dashboard, domínio e demais capacidades futuras não foram introduzidos.
- `CT-141`: PASS — fixture sintética, determinística, idempotente e restrita ao
  perfil de teste.
- `CT-142`: PASS integral — evidência manual em Chrome e Edge vigentes no Windows,
  incluindo teclado, foco, labels/erros/feedback, viewport aproximado de 360 px e
  zoom de 200%, além da cobertura automatizável.
- `CT-143`: PASS — backup/recovery em destino isolado, com reconciliação das
  entidades V0.2 e rejeição de corrupção antes de alterar o destino.
- `CT-081`, `CT-082`, `CT-122` e `CT-123`: PASS — banco vazio, instalação/upgrade,
  regressão e migrations continuam válidos.
- Evidências das Etapas 1–8: revisadas; não há P0/P1 aplicável aberto.

## Verificações desta etapa

- Smoke isolado de promoção: **8 PASS** — fixture, acessibilidade automatizável,
  banco vazio e upgrades V0.1 → V0.2.
- Baseline protegida: tag `v0.1.0` resolve para
  `cc7c382d2db8474eaee6005b71b7d01d40481611`.
- Gate autoritativo executado em 7 de setembro de 2026:
  `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1`
  - **GREEN**, exit code **0**, em 56 s;
  - 192 testes aprovados;
  - 86% de cobertura global e mínimo de 80% por módulo de domínio/regra atendido;
  - Ruff, mypy, rastreabilidade, hashes de migrations protegidas, banco vazio,
    `makemigrations --check --dry-run`, detect-secrets e `pip-audit` aprovados.

## Decisão operacional

- Nenhum P0/P1 aplicável ou defeito crítico de integridade, segurança, backup,
  migração ou acessibilidade permanece aberto.
- Nenhum commit, tag local, push ou release foi executado: tais ações não foram
  autorizadas nesta etapa.
- A V0.3 não foi iniciada e permanece sem autorização de execução.
