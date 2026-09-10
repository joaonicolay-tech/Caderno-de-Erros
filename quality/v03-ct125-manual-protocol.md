# CT-125 — protocolo manual de pós-resposta

## Estado

**PASS — 9/10 (90%), aceito para o fechamento da V0.3 por ADR-014.** A sessão
humana abaixo é histórica e real. Não houve nova sessão pós-ADR-013; esta
limitação está formalizada em ADR-014. O protocolo não substitui testes
automatizados de interface nem a evidência de CT-107.

## Definição autoritativa

- `CT-125` (Plano de Testes, §9.11): com participantes e uma resposta errada,
  a pessoa deve identificar o resultado e classificar a causa. O resultado
  esperado é que pelo menos 90% entendam o próximo passo; termos ambíguos devem
  virar achados. Prioridade P1, aplicável a V0.3/V0.4.
- `RNF-009`: distinguir questão, questão realizada, tentativa, revisão, ciclo
  concluído e domínio; o glossário ou ajuda contextual deve estar disponível;
  ciclo concluído não é sinônimo de dominado.
- `RNF-010`: cada gravação informa processamento, sucesso ou falha de forma
  compreensível e contextual; a pessoa consegue saber se concluiu e o que fazer
  após falha.
- `RNF-011`: uma revisão correta ocorre em sequência contínua e retorna à fila
  ou a um próximo estado claro. A fonte não fixa quantidade de cliques.

A decisão complementar de ADR-012 fixa 10 participantes em amostra de
conveniência apropriada à validação do MVP. Esta amostra não permite alegação
de representatividade estatística. O roteiro e o registro abaixo são
vinculantes para a execução; o perfil efetivamente adotado continua sendo
registrado sem coletar dado pessoal desnecessário.

## Preparação do moderador

1. Usar ambiente local descartável, dados sintéticos e uma questão ACTIVE com
   alternativa incorreta selecionável.
2. Abrir o fluxo inicial da questão, sem revelar gabarito, categoria esperada ou
   próximo passo antes da tarefa.
3. Registrar ambiente (data/hora, navegador/versão, largura/zoom, perfil Django
   e identificação sintética do cenário), sem dados pessoais desnecessários.
4. Atribuir identificador pseudônimo a cada participante. Não registrar nome,
   resposta de estudo ou dado sensível.

## Cenário e tarefas do participante

1. Responda intencionalmente a questão de modo incorreto e confirme.
2. Sem orientação do moderador, diga qual foi o resultado apresentado.
3. Classifique a causa do erro e conclua a operação.
4. Diga qual é o próximo passo de estudo/revisão e onde encontrá-lo.
5. Identifique, com as suas palavras, o que significam tentativa, revisão e
   ciclo concluído, distinguindo este último de domínio.
6. Caso o moderador disponibilize um cenário de falha controlada, descreva se a
   interface indicou falha e qual a ação seguinte. Não induzir sucesso fictício.

## Perguntas e observações

Registrar literalmente ou por resumo fiel:

- Qual resultado você entende que obteve?
- O que você precisa fazer agora? Onde faria isso?
- O que "tentativa", "revisão" e "ciclo concluído" significam aqui? "Ciclo
  concluído" quer dizer "dominado"?
- A mensagem de confirmação ou falha deixou claro o estado da gravação e a ação
  seguinte?
- Houve termo, mensagem ou etapa ambígua? Qual?

Observar conclusão sem ajuda crítica, pedido de esclarecimento, interpretação
do feedback, classificação e caminho posterior. Cada termo ambíguo é um achado,
não uma resposta a ser corrigida durante a sessão.

## Registro por participante

### Sessão humana histórica aceita

O ambiente original não foi registrado retroativamente. A ausência desse dado
é uma limitação explícita; não se inventa ambiente. Foram preservados somente
os dados reais fornecidos, sem observações adicionais.

| ID pseudônimo | Perfil efetivo | Resultado identificado | Causa classificada | Próximo passo explicado | Termos compreendidos | Feedback de gravação compreendido | Ajuda crítica? | Achados/observações |
|---|---|---|---|---|---|---|---|---|
| P01 | familiar | Sim | Sim | Sim | Sim | Sim | Não | não foram registradas observações. |
| P02 | familiar | Sim | Sim | Sim | Sim | Sim | Não | não foram registradas observações. |
| P03 | familiar | Sim | Sim | Sim | Sim | Sim | Não | não foram registradas observações. |
| P04 | familiar | Sim | Sim | Sim | Sim | Sim | Não | não foram registradas observações. |
| P05 | amigo | Sim | Sim | Sim | Sim | Sim | Não | não foram registradas observações. |
| P06 | amigo | Sim | Sim | Sim | Sim | Sim | Não | não foram registradas observações. |
| P07 | amigo | Sim | Sim | Sim | Parcial | Sim | Não | não foram registradas observações. |
| P08 | amigo | Sim | Sim | Sim | Parcial | Sim | Não | não foram registradas observações. |
| P09 | amigo | Sim | Sim | Sim | Parcial | Sim | Não | não foram registradas observações. |
| P10 | amigo | Sim | Não | Não | Parcial | Não | Sim | não foram registradas observações. |

Resultado: **9/10 = 90% — PASS**. P07–P09 são achados de compreensão parcial
dos termos. P10 é um FAIL real; não foi omitido nem convertido em sucesso.

### Modelo histórico do protocolo

| ID pseudônimo | Perfil efetivo | Resultado identificado | Causa classificada | Próximo passo explicado | Termos compreendidos | Feedback de gravação compreendido | Ajuda crítica? | Achados/observações |
|---|---|---|---|---|---|---|---|---|
| P01 | _não preenchido_ |  |  |  |  |  |  |  |
| P02 | _não preenchido_ |  |  |  |  |  |  |  |
| P03 | _não preenchido_ |  |  |  |  |  |  |  |
| P04 | _não preenchido_ |  |  |  |  |  |  |  |
| P05 | _não preenchido_ |  |  |  |  |  |  |  |
| P06 | _não preenchido_ |  |  |  |  |  |  |  |
| P07 | _não preenchido_ |  |  |  |  |  |  |  |
| P08 | _não preenchido_ |  |  |  |  |  |  |  |
| P09 | _não preenchido_ |  |  |  |  |  |  |  |
| P10 | _não preenchido_ |  |  |  |  |  |  |  |

## Regra de decisão e local da evidência

- **PASS:** pelo menos 9 dos 10 participantes demonstram compreensão do
  próximo passo, e os termos ambíguos encontrados são registrados como
  achados. O resultado identifica a amostra de conveniência e o ambiente,
  sem alegar representatividade estatística.
- **FAIL:** 8 ou menos dos 10 participantes demonstram compreensão do próximo
  passo, a evidência não permite a contagem, ou há ambiguidade sem registro de
  achado.
- **PENDENTE/BLOCKED:** não houve sessão humana real ou o registro individual
  dos 10 participantes não está completo. Não preencher respostas por
  inferência.

O registro histórico e a decisão constam neste protocolo e em
`quality/v03-stage5-validation-result.md`. Não usar o resultado de testes
automatizados de CSRF/escaping como evidência humana.
