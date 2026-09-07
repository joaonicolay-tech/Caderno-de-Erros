# Project State

Versão atual: V0.2
Situação da versão: formalmente promovida
Etapa atual: nenhuma tarefa autorizada
Status da etapa atual: V0.2 encerrada; V0.3 não iniciada

Etapas concluídas:

- V0.2 — Etapa 0 — Saneamento e Baseline da V0.2;
- V0.2 — Etapa 1 — Taxonomia e Migrations;
- V0.2 — Etapa 2 — Gestão e Interface da Taxonomia;
- V0.2 — Etapa 3 — Catálogo de Origem;
- V0.2 — Etapa 4 — Catálogo de Questões;
- V0.2 — Etapa 5 — Rascunho, Ativação e Cadastro Rápido;
- V0.2 — Etapa 6 — Detalhe, Edição Versionada e Arquivamento de Questões.
- V0.2 — Etapa 7 — Listagem, Busca e Filtros de Conteúdo.
- V0.2 — Etapa 8 — Fixture, Acessibilidade, Backup, Integração e Regressão.

Melhoria operacional:
Etapa 6 — adoção definitiva do novo fluxo operacional concluída.

Baseline protegida:
`v0.1.0` (`cc7c382d2db8474eaee6005b71b7d01d40481611`)

Último gate:
GREEN — V0.2 Etapa 9 final, exit code 0, em 56 s

Testes:
192 aprovados no gate final; smoke isolado de promoção com 8 aprovados

Coverage:
86% global; metas específicas aplicáveis atendidas

Bloqueadores:
Nenhum

P0/P1 aplicável aberto:
Nenhum

Evidência de encerramento:
V0.2 promovida formalmente após revisão consolidada das Etapas 0–8. `CT-141`,
`CT-142` (manual integral em Chrome e Edge no Windows) e `CT-143` estão PASS;
o banco vazio, o upgrade V0.1 → V0.2, a regressão e as migrations protegidas foram
reconfirmados. A evidência está em `quality/v02-stage9-promotion-result.md`.

Próximo objetivo:
Não há execução autorizada. A V0.3 não está autorizada e não foi iniciada.

ADRs relevantes:

ADR-001
ADR-002
ADR-003
ADR-008
ADR-010
