# Project Development Architecture v1.0

Status: **APPROVED/FROZEN** em 12 de setembro de 2026.

## Propósito e princípios

Esta é a visão operacional concisa para desenvolver o Caderno de Erros com
escopo explícito, contexto proporcional e evidência verificável. Ela liga as
fontes A1–A9 sem copiá-las e preserva cinco princípios:

1. autorização persistida antes da execução;
2. menor contexto e menor mecanismo suficientes;
3. mudança mínima dentro do contrato e do escopo protegido;
4. testes, review e gate complementares;
5. fatos desconhecidos permanecem desconhecidos.

Freeze significa baseline estável e evolutiva, não imutabilidade. Mudança
futura exige problema concreto ou evidência de ganho, atualização versionada e
validação proporcional. Preferência estética ou completude não bastam.

## Componentes e fontes de verdade

Cada fonte tem uma responsabilidade principal. Quando fontes comparáveis se
contradisserem, a divergência deve ser resolvida antes de mudança estrutural.

| Fonte | Responsabilidade principal |
| --- | --- |
| Código e migrations | Comportamento implementado e evolução real do schema. |
| Testes | Evidência automatizada do comportamento e das regressões cobertas. |
| ADRs | Decisões arquiteturais vigentes e seu porquê. |
| Requisitos e documentação formal | Comportamento, regras, fluxos e qualidade aprovados. |
| `PROJECT_STATE.md` | Estado operacional atual, marco, gate e bloqueadores. |
| `tasks/current.md` | Única autorização persistida e limites da execução corrente. |
| `tasks/plans/` | Decomposição opcional de tarefa complexa já autorizada. |
| `tasks/completed/` e documentos A1–A10 | Evidência histórica; consulta sob demanda. |
| Roadmap | Sequência e fronteiras futuras; nunca autorização de execução. |
| `AGENTS.md` | Regras curtas e obrigatórias de trabalho no repositório. |
| Skills A6 | Entradas independentes para fases recorrentes, sem nova autoridade. |
| `scripts/quality.ps1` e `quality/` | Gate autoritativo e evidências técnicas específicas. |
| JSONL A7 | Métricas de processo com proveniência; não substitui o gate. |

Esta divisão é mais útil que uma ordem linear universal: `tasks/current.md`
vence sobre escopo autorizado, ADR/requisito sobre decisão formal, e
código/migrations/testes mostram o estado executável. O índice
`docs/README.md` apenas localiza essas fontes.

## Autorização e ciclo da tarefa

O caminho administrativo definido em A2 é:

`NO_TASK_AUTHORIZED` → autorização explícita do usuário → bootstrap somente do
contrato → `AUTHORIZED` executável em sessão posterior.

O bootstrap não executa a tarefa. Restrições exclusivas dessa sessão não entram
no contrato permanente e `Done When` sempre descreve a conclusão real. Sem
contrato `AUTHORIZED`, nenhuma implementação começa.

O workflow oficial v1.0 é:

`autorização` → `start-task` → implementação mínima → testes focados → review
proporcional → gate → `finish-task` com estado, arquivo e métricas → checkpoint
Git expressamente autorizado.

- Obrigatório: contrato autorizado, A3, preservação de escopo, verificação
  aplicável, `git diff --check`, gate GREEN e encerramento evidenciado.
- Proporcional: plano, amplitude dos testes e profundidade do review.
- Opcional: plano para tarefa simples e checkpoint Git quando não autorizado.
- Tarefa documental: valida fatos/links/diff e ainda passa pelo gate geral; não
  cria teste funcional artificial.
- Tarefa complexa: pode exigir plano persistente, contexto ampliado por risco e
  review profundo; `XL` deve ser decomposta.
- Review profundo: segurança, migration, integridade, dados críticos,
  arquitetura ampla ou risco high/critical — não apenas tamanho.

As quatro Skills permanecem independentes. `start-task` valida, mas não
autoriza; `implement-current-task` edita, mas não encerra;
`run-quality-gate` mede, mas não corrige fora do escopo; `finish-task` arquiva
somente com evidência e não inicia a próxima tarefa.

## Progressive disclosure, implementação e qualidade

A3 permanece a política detalhada: começar por `AGENTS.md` e contrato, abrir o
contexto diretamente relacionado, escalar diante de ambiguidade/risco e parar
quando houver evidência suficiente. `PROJECT_STATE.md`, índice, ADRs, Roadmap e
histórico são lidos somente nos gatilhos definidos em A3.

Implementação preserva a menor mudança suficiente. Alteração de comportamento
recebe teste pertinente; bug deve, quando possível, ser reproduzido antes da
correção. A8 revisa critérios, regressões, escopo e riscos concretos. Gate GREEN
não substitui review nem teste essencial; review aprovado não substitui o gate.

## Modelos, reasoning e métricas

A7 mantém modelo e reasoning como decisões separadas, orientadas por risco,
dificuldade e evidência. O princípio é usar o modelo menos dispendioso
plausivelmente suficiente. Escalonamento exige evidência; incidente de
infraestrutura ou contrato não é falha de modelo. Não existem multiplicadores
rígidos de consumo.

O JSONL registra apenas fatos disponíveis, com `unknown` para lacunas e fonte
para dados manuais ou inferidos. Gate, testes e cobertura continuam em suas
fontes técnicas. A captura externa de duração, reasoning e quotas ainda é
irregular e não será automatizada sem benefício comprovado.

## Finalização, Git e evolução

Após review proporcional e gate GREEN, `finish-task` confirma Done When e
ausência de P0/P1, atualiza o estado quando necessário, arquiva o contrato,
registra as métricas disponíveis e retorna `current.md` a
`NO_TASK_AUTHORIZED`. Commit, push, tag e release são checkpoints separados e
somente ocorrem com autorização expressa. A próxima etapa começa em nova
autorização; preparar contrato futuro não permite executá-lo na mesma sessão.

A baseline deve evoluir apenas diante de conflito real, atrito repetido,
regressão operacional, nova necessidade do projeto ou série de métricas útil.
Mudanças devem ser mínimas, preservar história e indicar compatibilidade ou
nova versão da arquitetura.

## Auditoria A1–A9

| Componente | Decisão | Evidência e consequência |
| --- | --- | --- |
| A1 — baseline | SIMPLIFY | Útil como fotografia histórica; deixa de ser guia operacional corrente e permanece somente como histórico. |
| A2 — contrato | FIX | Autoridade e campos funcionaram na A9; A7 provou a necessidade de separar bootstrap administrativo, restrições transitórias e Done When real. |
| A3 — disclosure | KEEP | A9 chegou à correção factual sem leitura indiscriminada; regras MUST/SHOULD/ON-DEMAND e stop são suficientes. |
| A4 — tarefas/planos | KEEP | Separação current/plans/completed é clara; plano continua opcional e não foi criado para A10 porque o contrato já fornece decomposição suficiente. |
| A5 — configuração | KEEP | A9 não revelou necessidade de `.codex/config.toml` ou rules; ausência continua deliberada. |
| A6 — `start-task` | KEEP | Delimitou autoridade e working tree no piloto; sem redundância material. |
| A6 — `implement-current-task` | KEEP | Sustentou mudança mínima e escopo protegido; não deve absorver review ou fechamento. |
| A6 — `run-quality-gate` | KEEP | Preservou comando e resultado autoritativos sem duplicar o script. |
| A6 — `finish-task` | KEEP | Impediu fechamento sem evidência e separou a próxima autorização. |
| A7 — modelos/métricas | FIX | Estrutura leve é sustentável; A10 corrigiu campos A8 contraditórios e tornou explícita a consistência entre campos, notas e fontes. |
| A8 — review | KEEP | A9 demonstrou review leve útil; profundidades e estados complementam gate/Skills sem checklist universal. |
| A9 — piloto | KEEP | Evidência operacional principal: fluxo completo, GREEN na primeira passagem, nenhuma workaround ou expansão de escopo. |

Redundância aceitável limita-se a referências curtas entre `AGENTS.md`, A2/A3
e Skills. Foram removidos do desenho final dois pesos sem função: instruções
transitórias dentro de contratos permanentes e uso de A1 como guia corrente.
Não foi encontrada razão para fundir Skills, criar Skill de review, criar
configuração Codex ou automatizar o fluxo como pipeline rígido.

O incidente de owner/ACL de `.agents`, `SetNamedSecurityInfoW` error 5 e
`setup refresh had errors` permanece classificado como infraestrutura
Windows/Codex. A evidência já está no JSONL; não justifica camada permanente ou
nova política de produto.

## DEFER e futuro Project Starter

- DEFER: padronizar captura externa de duração, reasoning e quotas somente
  após mais execuções comparáveis ou suporte confiável do ambiente.
- DEFER: extrair Project Starter depois de usar esta baseline em V0.4 e
  observar portabilidade, atrito e parametrizações reais.

Potencialmente reutilizáveis: contrato A2, disclosure A3, separação A4, quatro
fronteiras A6, princípios A7/A8 e interface de gate único. Específicos do
Caderno de Erros: requisitos/ADRs de domínio, estado e roadmap, script e
manifestos concretos do gate, thresholds, testes e evidências V0.3. Exigem
parametrização: nomes/versões, comandos do gate, taxonomia de risco/modelos,
estrutura documental e campos de evidência.

Antes de extrair, V0.4 deve testar a baseline em trabalho funcional real,
incluindo ao menos uma tarefa mais complexa e seu encerramento. Não foi criado
Project Starter, dashboard, integração, Skill nova, CI/CD ou configuração
Codex.

## Critério e decisão de freeze

A9 validou o fluxo; as quatro Skills têm fronteiras claras; review e gate são
complementares; o JSONL é sustentável; a redundância relevante foi reduzida;
e a correção A2 elimina o conflito de bootstrap. A revisão A8 profunda da A10
foi APPROVED, sem findings, e o gate autoritativo ficou GREEN na primeira
execução, exit code 0, com 280 testes e 87% de cobertura. Não há blocker
arquitetural conhecido.

**Project Development Architecture v1.0 está APPROVED/FROZEN como baseline
operacional.** A1–A10 estão encerradas. Mudanças futuras exigem evidência e
evolução versionada; V0.4 pode usar esta baseline somente após autorização
própria.

## Referências detalhadas

- `A2_Contrato_de_Tarefa_Atual.md` — autorização e contrato;
- `A3_Progressive_Disclosure.md` — leitura proporcional;
- `../tasks/plans/README.md` — planos opcionais;
- `A7_Politica_de_Modelos_Reasoning_Escalonamento_e_Metricas.md` — modelos e métricas;
- `review/code-review.md` — review proporcional;
- `../.agents/skills/` — quatro fases independentes;
- `../scripts/quality.ps1` — gate autoritativo;
- `../tasks/completed/a9-operational-architecture-real-pilot.md` — piloto real.
