# A3 — Progressive Disclosure para execução segura

## Finalidade e fonte durável

Esta política torna a consulta do repositório proporcional à tarefa: ler menos
quando possível e aumentar o contexto somente quando necessário. Não substitui
as fontes de verdade nem autoriza trabalho fora do contrato.

- `REPOSITÓRIO` é a memória permanente;
- chat/Codex é memória temporária;
- `tasks/current.md` é a autoridade persistida da execução atual.

`AGENTS.md` contém a regra curta e obrigatória. Este documento é a fonte
durável das condições de leitura; `docs/README.md` é o índice para descobri-las.
Nenhum deles substitui código, migrations, testes, ADRs ou requisitos formais
como fontes de verdade.

## Ordem operacional

1. Leia `AGENTS.md` e `tasks/current.md`.
2. Se `current.md` for `NO_TASK_AUTHORIZED`, não implemente. Se for
   `AUTHORIZED`, extraia objetivo, escopo, escopo protegido, critérios,
   verificação e referências explícitas.
3. Localize e leia o código e os testes diretamente relacionados ao objetivo.
4. Consulte `PROJECT_STATE.md`, o índice, requisitos, ADRs e demais fontes
   somente conforme as regras abaixo ou as referências do contrato.
5. Aumente o contexto se houver gatilho de escalation; pare quando a regra de
   stop for atendida.

Uma tarefa autorizada que exige contexto documental deve referenciar em
`current.md` os documentos/ADRs indispensáveis. A referência não transforma o
contrato em cópia de requisitos, decisões ou histórico.

## Papel de `PROJECT_STATE.md`

| Nível | Consultar quando |
| --- | --- |
| MUST READ | planejamento, promoção/release, encerramento de etapa, definição de versão/etapa, conflito de estado, bloqueador, pré-requisito ou escopo protegido dependente do estado. |
| SHOULD READ | tarefa multicamada, de risco alto, ou cuja verificação possa ser afetada por marco, gate ou P0/P1 atuais. |
| ON-DEMAND | alteração local e suficientemente delimitada pelo contrato, código, testes e referências, sem efeito sobre versão, etapa, gate ou bloqueadores. |

O arquivo informa onde o projeto está; não é a autorização da tarefa. Sua
repetição histórica deve ser preservada e interpretada cronologicamente. A3 não
autoriza uma refatoração ampla dele; eventual melhoria fica para tarefa futura.

## Descoberta documental

`docs/README.md` é prioritariamente um índice e mecanismo de descoberta, não
leitura integral obrigatória. Consulte-o para localizar uma fonte fora das
referências diretas do contrato ou confirmar qual documento cobre um tema. Sua
estrutura por assunto deve apontar para a fonte, sem reproduzi-la.

| Fonte | Regra de leitura |
| --- | --- |
| Requisitos | Ler apenas quando a tarefa tocar comportamento funcional ou a regra aplicável. |
| ADRs | Ler quando a tarefa tocar a arquitetura coberta, parecer contrariar decisão existente, o contrato os referenciar, ou for preciso entender o porquê. |
| Roadmap | Normalmente dispensável em tarefa funcional já autorizada; ler em planejamento, delimitação de escopo, conflito entre versões ou risco de antecipação. |
| Histórico de tarefas | Fora do contexto normal; consultar apenas para regressão, rastreabilidade específica ou decisão ausente de fonte mais autoritativa. |

## Código, testes e busca

Após entender o contrato, a busca normal é:

`objetivo` → símbolos/arquivos → implementação relacionada → testes
correspondentes → documento ou ADR aplicável.

Evite ler apps inteiras, todos os testes, todo o Roadmap ou toda a documentação
“por segurança”. Código e testes diretamente relacionados têm precedência para
compreender o comportamento executável; isso não permite contrariar uma fonte
formal mais autoritativa quando ela se aplica.

## Context escalation

O agente DEVE ampliar o contexto ao encontrar regra de negócio ambígua,
conflito entre teste e documentação, migration, integridade, segurança,
comportamento temporal, mudança entre módulos, tentativa de tocar escopo
protegido, regressão sem explicação, ou requisito/ADR explicitamente citado por
`current.md`. Deve também escalar para a fonte de verdade relevante antes de
tomar decisão estrutural. Economia de contexto nunca justifica ignorar
evidência necessária.

## Context stop rule

Pare de abrir contexto quando contrato, implementação relacionada, testes,
critérios de aceite e fontes exigidas pelos gatilhos acima forem suficientes
para uma mudança segura e verificável. Não abra ADRs não relacionados, Roadmap,
histórico, documentos gerais ou outras apps preventivamente. Retome a expansão
somente se surgir nova evidência ou um gatilho de escalation.

## AGENTS locais

Não crie `AGENTS.md` locais por padrão. Uma tarefa futura só pode justificá-lo
com regras recorrentes e específicas de uma subtree, comandos diferentes,
constraints próprias ou convenção que já tenha causado erros repetidos. A
justificativa deve ser explícita e o arquivo local não deve duplicar o AGENTS
raiz.
