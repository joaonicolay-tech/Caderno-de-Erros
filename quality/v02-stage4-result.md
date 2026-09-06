# Resultado de qualidade — V0.2 — Etapa 4

- Gate: `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1`.
- Resultado: GREEN, exit code 0.
- Testes: 164 aprovados; 39 específicos de Questions/Origin.
- Cobertura global: 85%.
- Cobertura de Questions: Models 85%, Services 84%, Selectors 100%, Validators 90%.
- Migration: `questions/0002_question_catalog` aplicada em banco vazio; upgrade e
  rollback preservaram os dados da Etapa 3.
- Migrations históricas: hashes aprovados preservados.
- Ruff, mypy, rastreabilidade, segredos e vulnerabilidades: aprovados.
- P0/P1 aplicável aberto: nenhum.
- Observação ambiental: o sandbox exigiu um `basetemp` descartável novo para o
  pytest e acesso externo para `pip-audit`; nenhuma etapa do gate foi omitida.
