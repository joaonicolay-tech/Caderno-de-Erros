# Planos persistentes de tarefas

## Finalidade e limites

`tasks/plans/` responde **como uma tarefa complexa já autorizada será decomposta**. É uma área prospectiva e opcional: não contém planos retroativos, nem transforma toda tarefa em planejamento formal.

As áreas de `tasks/` têm responsabilidades distintas:

- `tasks/current.md` responde **o que está autorizado agora**. Há somente uma tarefa corrente autorizada e ele não retém histórico nem planejamento extenso que possa ser apenas referenciado.
- `tasks/plans/` registra a decomposição e a sequência de uma tarefa complexa autorizada quando isso trouxer ganho concreto.
- `tasks/completed/` responde **quais tarefas foram encerradas**. É histórico e não integra o contexto normal.

## Quando usar

Não crie plano persistente para uma tarefa apenas por ela ser importante. Ele é apropriado quando houver, por exemplo, etapas dependentes, várias camadas/módulos, migration complexa, mudança arquitetural relevante, investigação anterior à edição, rollback importante, alto risco, provável continuidade por mais de uma execução coerente, ou necessidade de registrar a sequência antes de editar.

Em regra, não é necessário para correção textual, alteração documental simples, bug local evidente, teste isolado, template ou view pequenos, ajuste mecânico, ou tarefa cujo Goal, Acceptance Criteria e Expected Scope de `current.md` já sejam suficientes.

## Proporção por tamanho

| Tamanho | Tratamento inicial |
| --- | --- |
| XS | Sem plano persistente; o contrato corrente contém o necessário. |
| S | Normalmente sem plano persistente. |
| M | Preferir subtarefas ou checklist conciso em `current.md`; plano separado somente com ganho concreto. |
| L | Plano persistente pode ser apropriado, sem ser automático. |
| XL | Não implementar diretamente: decompor em tarefas menores e coerentes; plano persistente normalmente é apropriado. |

A quantidade de arquivos não é um critério absoluto.

## Autoridade e leitura

Um plano só existe para apoiar uma tarefa autorizada. `tasks/current.md` deve referenciá-lo quando aplicável e continua sendo a única autoridade para Goal, Expected Scope, Protected Scope e autorização. Um plano nunca os amplia. Em caso de divergência, `current.md` prevalece e a divergência deve ser resolvida antes da implementação.

Planos não são lidos por padrão. Abra apenas o plano explicitamente referido por `current.md` ou quando o contrato exigir esse contexto; planos concluídos não fazem parte do contexto normal.

## Ciclo de vida e registro mínimo

Use apenas os estados `DRAFT`, `ACTIVE`, `COMPLETED` e `SUPERSEDED`:

- `DRAFT`: decomposição ainda não utilizada para executar;
- `ACTIVE`: apoia a tarefa corrente autorizada;
- `COMPLETED`: a tarefa relacionada foi encerrada ou o plano cumpriu seu papel;
- `SUPERSEDED`: foi substituído; registre a referência ao sucessor e preserve o artefato relevante.

Ao encerrar uma tarefa, preserve o plano relevante como evidência e atualize seu estado, sem apagá-lo. Se for abandonado, use `SUPERSEDED` quando houver substituto; caso contrário, registre sucintamente a condição de saída. Quando parte dele se tornar uma nova tarefa, a nova tarefa precisa de sua própria autorização em `current.md`.

## Validação conceitual

| Caso | Resultado da política |
| --- | --- |
| XS — correção de texto em template | Sem plano. |
| S — bug local com teste | Normalmente sem plano. |
| M — feature coesa com vários passos | `current.md` pode bastar; plano é opcional se houver ganho concreto. |
| L — mudança multicamada ou arquitetural | Plano persistente provavelmente é apropriado. |
| XL — mudança extensa | Não implementar diretamente; decompor antes e normalmente registrar plano persistente. |

Um plano pode usar este formato enxuto, sem repetir o contrato:

```md
# Plano: <id>

- ID da tarefa relacionada: <id>
- Status: DRAFT | ACTIVE | COMPLETED | SUPERSEDED
- Objetivo: <propósito da decomposição>
- Premissas: <somente premissas materiais>

## Decomposição

- <item ordenado e delimitado>

## Dependências, riscos e verificação

- <somente itens materiais; referencie current.md para autorização e aceite>

## Condição de saída

<conclusão, substituição ou condição de transferência>
```

O plano deve referenciar o contrato corrente aplicável, em vez de duplicar seus Acceptance Criteria, Expected Scope, Protected Scope ou as regras do repositório.
