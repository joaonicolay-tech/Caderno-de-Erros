# Plano: V0.4-S2

- ID da tarefa relacionada: V0.4-S2
- Status: COMPLETED
- Resultado: 27 testes focados e 285 testes no gate GREEN; review A8
  `APPROVED`; `git diff --check` aprovado; nenhum Blocker/Major aberto.
- Objetivo: decompor a implementação read-only dos contratos S1 sem ampliar
  `tasks/current.md`.
- Premissas: schema V0.3 suficiente; `Attempt.local_date`, taxonomia atual,
  `ReviewStatusPolicy` e projeção atual de classificação são as bases existentes.

## Decomposição

1. Definir filtros, DTOs e fachada interna estável.
2. Implementar atividade e drill-downs reconciliáveis.
3. Implementar revisões e situação de ciclo com data civil do Workspace.
4. Implementar disciplina, assunto, categoria e resíduos explícitos.
5. Reproduzir reconciliações S1, isolamento e bordas temporais em testes.
6. Inspecionar queries, ordering, diff, ausência de migration e de UI S3.
7. Executar review A8 profundo, verificações focadas e gate autoritativo.
8. Encerrar plano, estado, métricas e contrato somente após evidência GREEN.

## Dependências, riscos e verificação

- Autoridade semântica: `docs/V0.4_S1_Contratos_de_Metricas_e_Reconciliacao.md`.
- Riscos centrais: double counting, denominator mismatch, vazamento de
  Workspace, data civil incorreta, resíduo oculto e ordering instável.
- Verificação e escopo protegido permanecem os de `tasks/current.md`.

## Condição de saída

Marcar `COMPLETED` somente após testes focados, review profundo aprovado,
`git diff --check` e gate autoritativo GREEN; S3 permanece não autorizada.
