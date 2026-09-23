# V0.5-S2D — Human Decision Gate antes de código destrutivo

- Estado: Human Decision Gate liberado; S2D em implementação, não encerrada.
- Autoridade: `tasks/current.md` está `AUTHORIZED` para S2D; S3+ não está.
- Baseline: HEAD `654a9af885caa83610e9b32c1b8b73362220e9ec`, tag histórica
  `v0.4.4` anterior. A alteração preexistente em `tasks/current.md` foi
  preservada.
- A4: `tasks/plans/v05-s2d-permanent-deletion-plan.md`, `ACTIVE`.

## Achados que impedem implementação segura

1. O contrato S1 permite somente metadados mínimos no evento final e não
   define o destino dos `AuditEvent` S2A/S2B/S2C que apontam ao agregado.
   `src/modules/operations/models.py` é append-only e exige `entity_id` e
   `workspace_id`; `src/modules/operations/integrity.py`/AUD-001 exige alvos
   existentes. Apagar, sanitizar ou bloquear têm efeitos normativos diferentes.
2. `OperationReceipt.result_entity_id` aponta para Attempt sem FK, OPS-001
   exige alvo existente, e ADR-011 §7 exige pelo menos 30 dias e ausência de
   contexto transitório válido antes do descarte. O contrato S1 adia a
   expiração geral dos recibos para S8.
3. S1/RN-089 exigem backup prévio “aplicável” e confirmação reforçada, mas não
   fecham todos os bloqueios de histórico nem distinguem expressamente o
   backup obrigatório para histórico e rascunho simples. A decisão afeta a
   elegibilidade e o recovery.

## Decisão humana recebida nesta execução

- O evento final pode manter `workspace_id` técnico e não mantém Question ID.
- Expurgo manual S2D: elegível no instante exato
  `AuditEvent.created_at + 90 × 24 h` em UTC.
- Esta resposta resolve os itens 4 e 5 do A4. Os itens 1–3 acima permanecem
  pendentes naquele momento.

## Decisões adicionais recebidas

- Remover controladamente os `AuditEvent` antigos diretamente vinculados ao
  agregado no fluxo S2D; exceção explícita à regra append-only.
- Bloquear enquanto `OperationReceipt` tiver menos de 30 dias ou contexto
  transitório válido; após isso, removê-lo com o agregado.
- Histórico elegível após impacto, ausência de bloqueios, backup S6 validado
  por restore isolado/S5, confirmação reforçada e revalidação. Rascunho
  comprovadamente simples pode dispensar backup obrigatório.
- Human Decision Gate liberado exclusivamente para S2D. S3+ permanece sem
  autorização.

## Consequência operacional

As alternativas, seus efeitos, a recomendação técnica separada, o grafo e a
ordem condicional constam no A4. Antes da liberação, não foram criados serviço,
migration, teste funcional, comando de purge ou alteração do checker. Nenhum
banco ou backup foi alterado; não houve delete. Gate e A8 permanecem pendentes.
`PROJECT_STATE.md`, métricas e arquivamento aguardam conclusão comprovada.
