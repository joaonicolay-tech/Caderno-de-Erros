# ADR-012 — Parâmetros executáveis de BCR-1 e CT-125 na V0.3

| Campo | Valor |
|---|---|
| Status | Aprovada — complemento controlado da V0.3 |
| Data | 9 de setembro de 2026 |
| Marco | V0.3 — Etapa 5 aberta, sem promoção |
| Relacionado | ADR-011 §8; `CT-107`, `CT-125`, `BCR-1`, `RNF-003`, `RNF-009`–`011` |
| Decisão | Fixar parâmetros de execução e prova pendentes, sem alterar decisões históricas ou registrar resultado. |

## 1. Contexto e precedência

O resultado E5 em `quality/v03-stage5-validation-result.md` identificou que
`CT-107` não era executável de modo reproduzível e que `CT-125` não possuía
amostra manual formalizada. Este ADR complementa esses parâmetros. Não altera
o escopo, a matriz ou as decisões técnicas de ADR-011; onde houver conflito,
ADR-011 continua prevalecendo, exceto para os parâmetros explicitamente
complementados aqui.

Não há conflito identificado com `RNF-003`, o Plano de Testes ou ADR-011:
as metas de persistência real e p95 já eram obrigatórias; os parâmetros abaixo
somente tornam a prova auditável.

## 2. BCR-1 e CT-107

O dataset é o `BCR-1` autoritativo, sintético e determinístico, com seed fixa
registrada no relatório. Não serão usados dados pessoais reais. O benchmark usa
um banco SQLite descartável dedicado, populado antes da medição, e mede
persistência SQLite real, sem mock de banco.

As operações vinculantes são exatamente: salvar questão, salvar tentativa e
concluir/persistir revisão, nos limites autoritativos de `RNF-003` e `CT-107`.
Preparação de fixtures, bootstrap e pré-condições ficam fora da região
cronometrada. O benchmark não introduz concorrência artificial; concorrência
permanece coberta pelos CTs próprios, inclusive `CT-111`.

Para cada operação, em cada execução completa independente:

1. executar 20 operações de warm-up, excluídas das estatísticas;
2. coletar 100 amostras medidas;
3. ordenar as `N` amostras crescentemente e calcular p95 pela posição
   `ceil(0.95 × N)` (nearest-rank).

São obrigatórias três execuções completas independentes. `CT-107` recebe PASS
somente se, em cada uma das três, o p95 de todas as três operações for menor ou
igual a 2 segundos. Qualquer p95 acima de 2 segundos, ausência de uma execução,
ou evidência incompleta resulta em FAIL; até a execução real, o caso permanece
**aguardando execução**, sem PASS por especificação.

O relatório deverá registrar: Windows, versões de Python e SQLite, perfil
Django, modelo e quantidade de núcleos do CPU, memória RAM, tipo e espaço livre
do armazenamento usado pelo banco, seed, composição do BCR-1, banco
descartável, operações, warm-ups, amostras, as três execuções, p95 por
operação, comando e resultado PASS/FAIL.

## 3. CT-125

`CT-125` será executado seguindo integralmente
`quality/v03-ct125-manual-protocol.md`, com dez participantes em amostra de
conveniência apropriada à validação do MVP. A evidência não alegará
representatividade estatística. O registro individual usa identificador
pseudônimo e não coleta dado pessoal desnecessário; respostas não podem ser
inventadas.

O caso recebe PASS se pelo menos 9 dos 10 participantes demonstrarem
compreensão do próximo passo, conforme o protocolo. Recebe FAIL se 8 ou menos
demonstrarem essa compreensão. Sem sessão humana real e registro individual
completo, permanece **aguardando execução humana**, sem PASS.

## 4. Efeito operacional

Este ADR autoriza somente a futura prova objetiva de `CT-107` e a futura prova
humana de `CT-125`; não executa benchmark, não preenche resultados e não
promove V0.3. A Etapa 5 continua aberta, V0.3 continua não promovida e V0.4
continua não autorizada.
