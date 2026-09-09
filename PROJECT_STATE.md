# Project State

Versão atual: V0.3 (implementação incremental)
Situação da versão: Etapas 0, 1, 2, 3 e 4 concluídas; Etapa 5 aberta, com validação parcial registrada
Etapa atual: V0.3 — Etapa 5 — Integração, Migração, Regressão, Carga/Concorrência e Promoção
Status da etapa atual: E5 aberta; gate técnico GREEN, mas CT-107 aguarda execução e CT-125 aguarda execução humana; V0.3 não promovida

Etapas concluídas:

- V0.2 — Etapa 0 — Saneamento e Baseline da V0.2;
- V0.2 — Etapa 1 — Taxonomia e Migrations;
- V0.2 — Etapa 2 — Gestão e Interface da Taxonomia;
- V0.2 — Etapa 3 — Catálogo de Origem;
- V0.2 — Etapa 4 — Catálogo de Questões;
- V0.2 — Etapa 5 — Rascunho, Ativação e Cadastro Rápido;
- V0.2 — Etapa 6 — Detalhe, Edição Versionada e Arquivamento de Questões;
- V0.2 — Etapa 7 — Listagem, Busca e Filtros de Conteúdo;
- V0.2 — Etapa 8 — Fixture, Acessibilidade, Backup, Integração e Regressão;
- V0.3 — Etapa 0 — Saneamento, Fronteira e Rastreabilidade;
- V0.3 — Etapa 1 — Fundação de Aprendizagem: Schema, Constraints e Políticas Puras;
- V0.3 — Etapa 2 — Resposta Inicial Protegida, Contexto Transitório e Finalização Inicial Atômica.
- V0.3 — Etapa 3 — Política e Conclusão de Revisões.
- V0.3 — Etapa 4 — Fila Derivada, Linha do Tempo, Diagnóstico Auditável e Suspensão por Arquivamento.

Melhoria operacional:
Etapa 6 — adoção definitiva do novo fluxo operacional concluída.

Baseline protegida:
`v0.2.0` (`a756b6d`)

Último gate:
GREEN — V0.3 Etapa 5, exit code 0 (a promoção permanece bloqueada)

Testes:
269 aprovados; os CTs automatizados aplicáveis à E5 estão GREEN. CT-107 e
CT-125 não possuem PASS.

Coverage:
86% global; todos os módulos de domínio/regra do manifesto E4 acima de 80%

Bloqueadores:
`CT-107`/`BCR-1` (P0), aguardando benchmark real sob ADR-012; `CT-125` (P1),
aguardando evidência humana sob o protocolo atualizado.

P0/P1 aplicável aberto:
`CT-107` (P0) e `CT-125` (P1).

Evidência de encerramento:
O resultado integrado E5 está em `quality/v03-stage5-validation-result.md`.
ADR-012 torna `CT-107` e `CT-125` executáveis sem ambiguidade, sem preencher
qualquer resultado. As migrations E1 e os manifestos E1–E4 permanecem
intactos. Nenhuma promoção da versão foi realizada.

Próximo objetivo autorizado:
Executar exclusivamente as provas pendentes da V0.3 — Etapa 5: benchmark real
`CT-107` conforme ADR-012 e sessão humana `CT-125` conforme protocolo. V0.4
não está preparada, autorizada nem iniciada; V0.3 continua não promovida.

ADRs relevantes:

ADR-001
ADR-002
ADR-003
ADR-008
ADR-010
ADR-011
ADR-012
