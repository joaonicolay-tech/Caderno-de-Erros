# A2 — Contrato de tarefa atual

## Finalidade

`tasks/current.md` é o contrato versionado da autorização de trabalho presente:
responde, de forma suficiente e persistida, o que o agente pode executar agora.
Ele é proporcional à tarefa e não substitui fontes de verdade do produto.

## Relação entre fontes

- `tasks/current.md`: o que está autorizado agora;
- `PROJECT_STATE.md`: onde o projeto está;
- `AGENTS.md`: como trabalhar no repositório;
- `docs/`: requisitos, decisões e contexto quando necessários;
- código e testes: comportamento executável e comprovado.

Assim, `current.md` referencia contexto necessário, mas não replica requisitos,
ADRs, estado, plano de projeto, checklist universal ou histórico extenso.

## Regra de autorização

Implementação só pode começar quando `tasks/current.md` declarar uma tarefa com
`Status: AUTHORIZED` e os campos obrigatórios preenchidos. Um prompt ou chat
não amplia silenciosamente o escopo persistido. Uma autorização externa clara
pode instruir uma sessão administrativa de bootstrap a criar ou substituir o
contrato antes da execução. Essa sessão pode editar somente o contrato e deve
parar depois de deixá-lo completo; ela não executa a tarefa recém-autorizada.

O contrato criado pelo bootstrap deve representar a tarefa real e ficar
imediatamente executável por uma sessão posterior. Restrições exclusivas do
bootstrap, como "não implemente nesta sessão", não são persistidas em
`Constraints`; `Done When` descreve sempre a conclusão real da tarefa, não o
fim da autorização administrativa. O fluxo legítimo é:

`NO_TASK_AUTHORIZED` → autorização administrativa explícita → contrato
`AUTHORIZED` executável → nova sessão de execução.

Sem autorização administrativa explícita, `NO_TASK_AUTHORIZED` continua
bloqueando qualquer implementação. Uma Skill de execução não cria nem amplia
autorização.

Se chat e contrato divergirem, o agente deve identificar a divergência e pedir
ou registrar a correção antes de implementar. Ao concluir, a tarefa é arquivada
em `tasks/completed/` e `current.md` retorna ao estado sem tarefa autorizada.
Uma tarefa concluída não permanece como atual.

## Formato para uma tarefa autorizada

```md
# Task Contract

Status: AUTHORIZED

## Identification

- Task ID:
- Product version:
- Stage:
- Task type:
- Size:
- Risk:

## Goal

<um objetivo primário observável>

## Context

<somente contexto indispensável>

## Acceptance Criteria

- <critério objetivo e verificável>

## Expected Scope

- <arquivos, módulos, camadas ou tipos de mudança autorizados>

## Protected Scope

- <áreas que não podem ser alteradas, quando aplicável>

## Constraints

- <restrições específicas>

## Verification

- <testes focados, comandos e gate aplicável>

## Documentation Impact

<documentos que podem/devem mudar, ou `none`>

## Done When

- <condição objetiva de encerramento>
```

`Identification`, `Goal` e `Acceptance Criteria` são obrigatórios e devem ser
compreensíveis. Os demais campos também são usados quando aplicáveis; para
uma tarefa pequena, bastam linhas curtas. `Expected Scope` não exige uma lista
exata de arquivos quando ela ainda não é conhecida com segurança.

## Tamanho e risco

| Valor | Definição operacional inicial |
| --- | --- |
| `XS` | alteração mecânica e inequívoca. |
| `S` | objetivo local. |
| `M` | objetivo funcional ou operacional coeso. |
| `L` | mudança ampla ou multicamadas. |
| `XL` | deve ser decomposta antes da implementação. |

A classificação é uma orientação inicial, não uma ciência exata nem uma regra
rígida de número de arquivos.

| Valor | Impacto característico |
| --- | --- |
| `low` | documentação isolada ou alteração facilmente reversível. |
| `medium` | feature local ou impacto controlado que requer validação. |
| `high` | migrations, integridade, histórico ou impacto amplo. |
| `critical` | operação potencialmente destrutiva ou difícil de recuperar. |

O risco considera impacto, não apenas quantidade de arquivos, e nesta etapa
não seleciona modelo de execução.

## Sem tarefa autorizada

O único estado sem autorização é o formato abaixo. Ele não representa tarefa
incompleta e não contém campos de uma tarefa:

```md
# Task Contract

Status: NO_TASK_AUTHORIZED

No implementation is authorized. A clear external authorization must first be
persisted here as an `AUTHORIZED` contract.
```

Tarefas históricas permanecem registros em `tasks/completed/`; não precisam ser
migradas para este formato, que vale prospectivamente.
