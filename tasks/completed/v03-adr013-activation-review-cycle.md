# V0.3 — Correção: ciclo de revisão na ativação da questão

## Autorização e objetivo

Implementar exclusivamente ADR-013. Toda questão que efetivamente transicionar
para `ACTIVE` deve criar atomicamente um `ReviewCycle` `ACTIVE` de origem
`QUESTION_ACTIVATION` e uma única `Review` D1 para o próximo dia civil do
Workspace, sem fabricar `Attempt`.

Antes de iniciar, ler `AGENTS.md`, `PROJECT_STATE.md`, este arquivo,
`docs/README.md`, ADR-011, ADR-013 e somente as fontes/testes diretamente
afetados.

## Escopo autorizado

- schema e migration evolutiva para a modelagem definida em ADR-013;
- serviços de questão/ativação e de tentativas/revisões estritamente
  necessários para a nova regra;
- correção apenas dos literais comprovadamente com mojibake em código,
  templates e testes afetados, preservando UTF-8 real;
- testes da regra: três caminhos de ativação, data civil/Workspace,
  atomicidade, rollback, idempotência/concorrência, constraints, fila/timeline,
  arquivamento, `Attempt INITIAL` correta/incorreta, erro de Review e migração
  sem ciclo retroativo para questões `ACTIVE` históricas;
- atualização de evidência de qualidade aplicável e gate autoritativo.

## Invariantes obrigatórios

- `QUESTION_ACTIVATION` não possui `origin_attempt`; toda origem
  `INITIAL_ERROR` continua exigindo tentativa inicial incorreta válida.
- A D1 inaugural de ativação é a única situação semanticamente válida para
  `Review.scheduled_from_attempt = NULL`; conservar rastreabilidade por
  `origin_question_revision`.
- Manter no máximo um ciclo ativo por questão e no máximo uma Review pendente
  por ciclo.
- Edição de questão já `ACTIVE` não cria/reinicia ciclo. Arquivamento continua
  suspendendo ciclo/pendência. Reativação continua fora de escopo.
- Acerto INITIAL mantém D1; erro INITIAL registra tentativa/classificação sem
  criar ou resetar D1; erro de Review continua reiniciando D1.
- Não criar ciclos retroativos para questões `ACTIVE` históricas.
- Preservar Workspace, Clock/Calendar, `REV-FIXA-1.0`, contexto transitório,
  idempotência, transações curtas, política SQLite, migrações e manifestos
  históricos protegidos.

## CT-125 e promoção

Preservar o resultado humano histórico: P01–P09 PASS, P07–P09 com compreensão
parcial dos termos, P10 FAIL, total 9/10 (90%). Não inventar observações. A
mudança estrutural requer reteste do candidato final; não declarar CT-125 PASS
por esta evidência e não promover V0.3.

## Validação e encerramento

Executar testes específicos, depois:

`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1`

O gate deve retornar exit code 0. Registrar somente evidência real. Após gate
GREEN, atualizar o estado e arquivar esta tarefa conforme `AGENTS.md`; não
iniciar nova etapa no mesmo chat.

## Proibido

Não implementar capacidade V0.4, reativação, reagendamento, dashboard,
métricas, prioridade, domínio, recomendação, exportação ou refatoração ampla.
Não alterar documentos históricos congelados silenciosamente. Não criar ciclo
ou `Attempt` artificial para dados históricos. Não promover V0.3, nem fazer
commit, push, tag ou release.
