# Plano: V0.4-S6 — Backup e recuperação

- Task ID: V0.4-S6
- Status: COMPLETED
- Autoridade: `tasks/current.md`; este plano não amplia o contrato.
- Objetivo: comprovar recuperação isolada reutilizando o mecanismo existente.

## Decomposição

1. Auditar baseline, comandos, testes, ADR-007 e contratos S1/S5.
2. Comprovar snapshot consistente e falha limitada sob bloqueio SQLite.
3. Consolidar restore isolado, paths e publicação sem overwrite.
4. Verificar abertura, integridade física e compatibilidade de migrations.
5. Integrar interface read-only S5 ao arquivo isolado; distinguir 0/2/3.
6. Reconciliar artefato esperado e fatos V0.4, aceitando resíduo S1.
7. Provar preservação do original/principal, cleanup e proteção/rollback aplicáveis.
8. Exercitar corrupção, arquivo inexistente, incompatibilidade e falhas de filesystem.
9. Reutilizar logging sanitizado/correlacionado e mensagens recuperáveis.
10. Documentar operação, RPO/RTO, retenção e handoffs S7/S8/S9.
11. Executar testes focados e ensaio operacional sintético com evidência observada.
12. Revisar profundamente (A8), corrigir findings, executar diff check/gate e encerrar.

## Auditoria inicial

| Capacidade | Estado inicial | Ação |
| --- | --- | --- |
| Snapshot | adequada: SQLite backup API, origem read-only | Preservar; ampliar teste de bloqueio |
| Naming/destino | adequada: caminho explícito e sidecar determinístico | Documentar convenção |
| Overwrite | parcial: publicação exclusiva; resolução de symlink merece guarda | Testar e fortalecer proporcionalmente |
| Restore | adequada: somente destino novo, temporário no mesmo diretório | Preservar |
| Integridade física | adequada: integrity_check e foreign_key_check | Preservar e comprovar |
| Schema/abertura | adequada: migrations exatas e consultas reais | Preservar |
| S5 | ausente no restore | Integrar interface existente |
| Reconciliação | parcial: contagens V0.3; rejeição indevida de resíduo S1 | Alinhar e provar correspondência do artefato |
| Banco em uso | parcial: WAL coberto; backup pode aguardar bloqueio indefinidamente | Limitar operação com falha segura |
| Logging/mensagens | parcial: eventos existentes; falta resultado S5/ação específica | Reutilizar infraestrutura |
| Pré-restore/rollback | adequada ao escopo: não há substituição do ativo | Documentar salvaguarda e adoção fora do comando |
| Temporários/Windows | adequada: pathlib, close, publicação sem replace e cleanup | Regressão focada |
| Testes/documentação | parcial: baseline cobre fundação/V0.3 | Evidência S6 e guia operacional |

## Riscos e verificação

Checker no banco errado, falso PASS, mutação de origem e restore divergente exigem
testes negativos reais. Não alterar S5/schema/migrations, Architecture, Skills ou
gate. Nenhum dado real, Git ou etapa S7-S9 será executado.

## Condição de saída

Concluído em 2026-09-16: ensaio sintético PASS, review A8 profundo APPROVED,
65 testes focados/relacionados e gate autoritativo GREEN (322 testes, 88% de
cobertura, exit 0). A evidência e as limitações estão em
`quality/v04-s6-recovery-result.md`; S7-S9 não foram iniciadas.
