# Plano: V0.4-S9 — Piloto controlado e promoção

- ID da tarefa relacionada: `V0.4-S9`
- Status: `COMPLETED`
- Objetivo: executar o piloto local em cópia protegida e decidir, por evidência,
  entre `V0.4 PROMOTED` e `V0.4 NOT PROMOTED`.
- Autoridade: `tasks/current.md`; este plano não amplia o contrato.
- Baseline operacional: Project Development Architecture v1.0.
- Base inicial observada: branch `main`, commit
  `03a6afd240efc485e9cb29c7f1f00e68c5008ba3`; `tasks/current.md` é a única
  alteração local inicial e pertence à autorização administrativa de S9, não ao
  candidato S8.

## Decomposição

1. **Pré-condições:** confirmar S8 `COMPLETED`, candidato `READY_FOR_PILOT`, A8
   `APPROVED`, Blocker/Major zero, gate GREEN, BCR-1, S5, S6 e S7 saudáveis e
   migrations coerentes; interromper antes do piloto diante de contradição.
2. **Dados e ambiente:** identificar o banco principal sem expor conteúdo;
   manter o original protegido e preparar banco piloto separado em diretório
   controlado.
3. **Backup pré-piloto:** executar S6 sobre o estado relevante, preservar banco
   e manifesto e nunca restaurar sobre o principal.
4. **Baseline:** validar backup e restore isolado com SQLite, compatibilidade,
   reconciliação e S5 exit 0; registrar contagens sanitizadas e estado da
   aplicação antes dos cenários.
5. **Cenários:** operar pela superfície Windows S7 e cobrir dashboard, consulta,
   busca/filtros/paginação, detalhe/timeline, tentativa inicial, erro e
   classificação ou resíduo legítimo, revisão/estado temporal, analytics,
   isolamento por Workspace, checker, backup e shutdown/restart.
6. **Coleta de evidências:** registrar por cenário ID, objetivo, pré-condições,
   passos, esperado, observado, PASS/FAIL e referência objetiva; julgamento
   humano ausente permanece `NOT OBSERVED`.
7. **Defects:** registrar cada desvio antes de correção, com severidade A8,
   impacto, causa conhecida e decisão; Blocker/Major aberto impede promoção.
8. **Retestes:** corrigir somente defeito V0.4 comprovado, pequeno e autorizado;
   executar teste focado, repetir cenário e regressões relacionadas.
9. **Validação pós-piloto:** comparar baseline final, executar S5 exit 0,
   confirmar recovery S6 e operação S7, além de ausência de perda, inconsistência
   e leakage.
10. **Gate:** executar `git diff --check` e o `scripts/quality.ps1` autoritativo;
    registrar first pass e exigir exit 0 para promoção.
11. **Review:** realizar A8 profundo do piloto, defects, correções, evidências,
    checklist oficial, documentação e estado final.
12. **Decisão de promoção:** mapear todos os critérios P0 para evidências e
    registrar exatamente `V0.4 PROMOTED` ou `V0.4 NOT PROMOTED`.
13. **Encerramento:** concluir evidências, atualizar somente estado/Roadmap/docs
    aplicáveis, registrar A7, limpar cópias descartáveis e processos, preservar
    backup, arquivar S9 e restaurar `NO_TASK_AUTHORIZED`, sem V0.5, commit, push,
    tag ou release.

## Dependências, riscos e verificação

- O banco principal nunca será o único exemplar nem destino de restore.
- Evidências usarão IDs, contagens, estados e resultados; não incluirão conteúdo
  pessoal, respostas, enunciados, secrets ou dumps.
- S5: exit `0` saudável; `2` findings; `3` falha operacional. Somente `0` atende
  os gates relevantes.
- BCR-1 e acessibilidade S8 serão reutilizados enquanto nenhuma correção de S9
  invalidar essas evidências.
- Correções que toquem S5, S6, S7, analytics ou UI exigem a revalidação indicada
  no contrato.
- O gate e o review são controles separados; ambos devem aprovar a promoção.

## Condição de saída

Concluída em 19 de setembro de 2026. As treze etapas foram executadas: backups
pré e pós-piloto foram validados e restaurados isoladamente; os cenários
terminaram PASS; S5 permaneceu saudável; S9-F001 foi resolvido e revalidado; o
gate ficou GREEN na primeira passagem, exit 0; o review A8 profundo foi
`APPROVED`, sem Blocker/Major/Minor aberto; a decisão foi `V0.4 PROMOTED`.
Cópias descartáveis e processos foram removidos, os dois backups finais foram
preservados e não houve commit, push, tag, release nem início/autorização V0.5.
