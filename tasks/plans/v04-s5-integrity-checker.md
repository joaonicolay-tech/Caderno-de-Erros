# Plano: V0.4-S5

- ID da tarefa relacionada: V0.4-S5
- Status: COMPLETED
- Resultado: 10 testes específicos e 153 regressões relacionadas GREEN;
  review A8 profundo `APPROVED`; teste manual read-only aprovado;
  `git diff --check` aprovado; gate autoritativo GREEN com 302 testes e exit 0.
- Objetivo: decompor a camada read-only de integridade operacional sem ampliar
  `tasks/current.md` e sem antecipar S6-S9.
- Princípio: detector, não reparador; nenhuma etapa executável pode persistir,
  normalizar, migrar ou corrigir dados.

## Baseline auditado

- `modules.operations` já fornece eventos estruturados, sanitização central e
  `correlation_scope`; S5 estenderá esse catálogo sem criar outro subsistema.
- Os comandos Django existentes confirmam a superfície operacional e o padrão
  `--correlation-id`/`CommandError`.
- Constraints de schema garantem FKs, enumerações, unicidades e combinações de
  estado locais; não garantem coerência funcional entre Workspaces/tabelas,
  gabarito, data civil nem encadeamento completo.
- Models e services validam essas relações na escrita normal, mas SQL direto,
  restauração defeituosa ou corrupção podem contornar essas proteções.
- A validação legada de restore contém uma regra mais estrita para erro sem
  classificação. S5 seguirá o contrato S1: esse resíduo é legítimo. O alinhamento
  do restore permanece para S6 e não será implementado nesta tarefa.

## Decomposição

1. Consolidar o catálogo explícito: classificar candidatas como garantidas
   estruturalmente, verificáveis operacionalmente, redundantes ou não aplicáveis.
2. Definir DTOs imutáveis para especificação, finding e resultado, com poucas
   severidades e contexto técnico mínimo.
3. Implementar checker read-only em consultas em lote para SQLite/FKs,
   Workspace, taxonomia, question/versionamento, Attempt, ReviewCycle/Review,
   ErrorClassification/revisões e recibos.
4. Validar tempo e progressão apenas contra os helpers e a política existentes;
   não recalcular dashboard nem introduzir regra de revisão.
5. Expor management command com saída humana determinística, limite explícito,
   correlação reutilizada e exit codes distintos para saudável, findings
   impeditivos e falha operacional.
6. Estender somente os eventos operacionais necessários, com resumo agregado e
   sanitização central; não registrar conteúdo de estudo nem um log por objeto.
7. Criar testes de base saudável, duas Workspaces, corrupção isolada/múltipla,
   temporal/review, resíduo sem classificação, read-only, sanitização, logs,
   ordenação/limite, exit codes e query count proporcional.
8. Criar documentação operacional e catálogo fundamentado; registrar a
   integração futura, sem executar restore, hardening ou piloto.
9. Revisar diff profundamente, confirmar ausência de migration/write/N+1,
   executar testes focados, `git diff --check` e gate autoritativo.
10. Somente após evidência GREEN: marcar este plano `COMPLETED`, atualizar estado
    e métricas A7, arquivar S5 e retornar `tasks/current.md` a
    `NO_TASK_AUTHORIZED`.

## Riscos e controles

- Falso positivo: cada check terá fonte explícita; erro válido sem classificação
  será cenário saudável obrigatório.
- Falso negativo: fixtures corrompidas por SQL localizado provarão relações que
  o ORM/model normalmente rejeita.
- Side effect oculto: o caminho produtivo usará apenas conexão/cursor e leitura;
  testes compararão contagens e valores antes/depois.
- Vazamento: findings conterão somente IDs, tipos, códigos, estados e datas; as
  sentinelas de conteúdo não poderão aparecer em stdout, stderr ou logs.
- Escala: consultas serão agregadas/em lote, com limite de exibição sem ocultar
  a contagem total e sem loop de query por registro.
- Falha técnica: será separada de corrupção por evento, mensagem e exit code.

## Verificação e condição de saída

A autoridade de escopo e verificação permaneceu integralmente em
`tasks/current.md`. A condição de saída foi atendida: testes focados e manual
seguro aprovados, review A8 profundo `APPROVED`, ausência de migration,
`git diff --check` e gate autoritativo GREEN com exit code 0. S6 permanece não
autorizada.
