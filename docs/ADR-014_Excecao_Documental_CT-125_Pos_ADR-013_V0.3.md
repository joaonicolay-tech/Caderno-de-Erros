# ADR-014 — Exceção documental do CT-125 pós-ADR-013 V0.3

| Campo | Valor |
|---|---|
| Status | Aprovada — decisão corretiva limitada de encerramento da V0.3 |
| Data | 10 de setembro de 2026 |
| Relacionado | ADR-012, ADR-013, CT-125 e `quality/v03-ct125-manual-protocol.md` |
| Decisão | Aceitar, para o fechamento da V0.3, a evidência humana histórica completa de CT-125, sem alegar uma nova sessão posterior ao ADR-013. |

## 1. Contexto e conflito resolvido

ADR-013 preservou a sessão humana histórica de CT-125 (9/10, 90%), mas exigiu
reteste do candidato corrigido antes da promoção. Posteriormente, os registros
individuais reais P01–P10 foram disponibilizados e o responsável pelo produto
decidiu não repetir uma sessão completa com dez participantes.

Esta decisão substitui **somente** a exigência de reteste humano pós-ADR-013
para CT-125. ADR-013 continua vigente para a regra de ativação, schema,
migration, ciclos, D1, tentativas, fila, timeline e regressões automatizadas.
ADR-012 continua sendo a definição do limiar e do registro humano; esta decisão
não altera seus critérios quantitativos.

## 2. Impacto no escopo específico de CT-125

CT-125 avalia identificação de resposta incorreta, classificação da causa,
compreensão do próximo passo, feedback de gravação e termos/ajuda contextual.
ADR-013 alterou a origem do `ReviewCycle`, o momento de criação da D1 e a
relação entre ativação, `Attempt` e ciclo. Não alterou a tarefa humana de
resposta incorreta, classificação, confirmação de gravação ou explicação do
próximo passo.

O fluxo final pós-ADR-013 foi validado manualmente pelo responsável pelo
produto como funcionalmente correto. Essa validação funcional não é uma nova
amostra de dez participantes nem substitui uma sessão humana; ela apenas
sustenta a análise de que a mudança estrutural não alterou o objeto de CT-125.

## 3. Aceitação e limitações

A evidência histórica registrada no protocolo é aceita como **CT-125: PASS**:
9 de 10 participantes (90%) demonstraram compreensão do próximo passo. P07,
P08 e P09 registram compreensão parcial dos termos como achados; P10 é um
FAIL real, com ajuda crítica. Não foram registradas observações adicionais.

Não houve nova sessão humana pós-ADR-013. Não foram inventados participantes,
respostas, ambiente, observações ou alegação de representatividade estatística.
A amostra continua sendo de conveniência, apropriada somente à validação do
MVP nos limites de ADR-012.

## 4. Efeito operacional

Após a regressão do candidato ADR-013, a execução integral do gate e a
confirmação de CT-107/BCR-1, CT-125 deixa de ser P1 bloqueante para o
fechamento da V0.3. Esta decisão não autoriza V0.4, reativação, mudança
funcional, migration, commit, tag, push ou release.
