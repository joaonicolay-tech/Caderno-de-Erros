# Project State

Versão atual: V0.2
Situação da versão: em andamento; promoção final pendente
Etapa atual: V0.2 — Etapa 9 — Validação Final e Promoção
Status da etapa atual: formalmente liberada, preparada e não iniciada

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
GREEN — V0.2 Etapa 8 final, exit code 0, com isolamento temporário do pytest preservado

Testes:
192 aprovados (mais 1 verificação focada de `CT-142` aprovada)

Coverage:
86% global; metas específicas aplicáveis atendidas

Bloqueadores:
Nenhum

P0/P1 aplicável aberto:
Nenhum

Evidência de encerramento:
`CT-142` manual está integralmente PASS em Chrome e Edge vigentes no Windows, incluindo
teclado, foco, labels/erros/feedback, fluxos do catálogo, viewport aproximado de 360 px
e zoom de 200%, sem rolagem horizontal indevida. A evidência está em
`quality/v02-stage8-automated-result.md`; não há P0/P1 aplicável aberto.

Próximo objetivo:
Executar exclusivamente a V0.2 — Etapa 9 — Validação Final e Promoção em novo chat,
conforme `tasks/current.md`. A V0.3 não está autorizada.

ADRs relevantes:

ADR-001
ADR-002
ADR-003
ADR-008
ADR-010
