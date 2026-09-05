# Caderno de Erros Inteligente

## Etapa 5 — Regras de Negócio

| Campo | Valor |
|---|---|
| Documento | Catálogo de Regras de Negócio |
| Projeto | Caderno de Erros Inteligente |
| Versão | 1.0.1 — errata V0.2 |
| Data | 30 de agosto de 2026 |
| Status | Aprovada e congelada; errata de fase V0.2 incorporada em 5 de setembro de 2026 |
| Aprovação | Aprovada integralmente pelo responsável pelo produto em 30 de agosto de 2026 |
| Base congelada | Visão 1.0; Escopo 1.0; RFs 1.0; RNFs 1.0 |
| Próxima etapa após aprovação | Etapa 6 — SDD |

---

## 1. Finalidade

Este documento formaliza as regras que governam o comportamento do Caderno de Erros Inteligente. As regras serão independentes da tecnologia e deverão ser aplicadas de modo consistente pela interface, serviços, persistência, importações futuras e testes.

Quando uma regra for alterada no futuro, a mudança deverá:

- receber nova versão quando afetar cálculos ou histórico;
- indicar a data de vigência;
- identificar registros afetados;
- preservar a capacidade de explicar resultados anteriores;
- atualizar requisitos, arquitetura, dados, fluxos e testes relacionados.

---

## 2. Convenções

### 2.1 Termos normativos

- **Deve:** regra obrigatória.
- **Não deve:** comportamento proibido.
- **Pode:** comportamento permitido, mas não obrigatório.
- **MVP:** regra necessária no primeiro produto utilizável.
- **V1:** regra comprometida para consolidação posterior ao MVP.

### 2.2 Registros válidos

Um registro **válido** é aquele que:

- foi confirmado com sucesso;
- não está anulado;
- pertence ao espaço individual correto;
- satisfaz as restrições estruturais aplicáveis;
- não foi removido por exclusão válida.

Somente registros válidos participam de métricas atuais, domínio e agendamento, salvo quando um relatório histórico indicar explicitamente outra base.

### 2.3 Precisão

Todos os cálculos deverão usar precisão interna suficiente. Arredondamento ocorrerá apenas na apresentação, conforme `RN-057`.

---

## 3. Alternativas estruturais analisadas

### 3.1 Interpretação dos intervalos 1d, 7d, 14d e 30d

| Alternativa | Funcionamento | Vantagens | Problemas |
|---|---|---|---|
| A — Marcos absolutos | Datas são D+1, D+7, D+14 e D+30 desde o erro inicial. | Ciclo termina em aproximadamente 30 dias. | Atrasos podem fazer várias etapas vencerem juntas ou exigir saltos artificiais. |
| B — Intervalos sucessivos | Após cada acerto, a próxima revisão ocorre 1, depois 7, depois 14 e depois 30 dias após a conclusão real anterior. | Cada etapa mantém espaçamento real; atraso não comprime o ciclo; regra simples. | Ciclo perfeito termina cerca de 52 dias após o erro inicial. |
| C — Adaptativa | Próxima data depende de acerto, erro e facilidade. | Personalização maior. | Fora do MVP; maior complexidade e menor previsibilidade inicial. |

**Recomendação:** Alternativa B. O produto pretende medir aprendizagem ao longo de revisões reais; garantir sete ou quatorze dias entre recuperações é mais coerente do que considerar cumprido um intervalo que passou enquanto a revisão estava atrasada.

### 3.2 Tratamento de erro durante revisão

| Alternativa | Funcionamento | Vantagens | Problemas |
|---|---|---|---|
| A — Reinício em 1 dia | Qualquer erro reinicia a sequência em 1d. | Clara, conservadora, previsível e adequada ao MVP. | Pode alongar o ciclo para erros ocasionais. |
| B — Voltar uma etapa | O erro reduz apenas um nível. | Menos punitiva. | Um erro na etapa de 30 dias poderia voltar para 14 dias sem reconsolidar a base curta. |
| C — Decisão por facilidade/algoritmo | Intervalo varia por contexto. | Mais flexível. | Pertence à revisão adaptativa futura. |

**Recomendação:** Alternativa A no ciclo fixo. O erro cria nova âncora de aprendizagem e exige recuperação curta. A regra poderá ser substituída por algoritmo versionado no Pós-V1.

### 3.3 Modelo de Índice de Domínio

| Alternativa | Funcionamento | Avaliação |
|---|---|---|
| A — Taxa simples de acerto | Acertos ÷ tentativas. | Rejeitada: ignora espaçamento, recência, fluência, recorrência e amostra. |
| B — Heurística multifatorial explicável | Combina acerto recente, progressão espaçada, fluência e controle de recorrência. | Recomendada para a V1: determinística, auditável e ajustável por versão. |
| C — Modelo probabilístico/Bayesiano ou de memória | Estima probabilidade de retenção. | Candidato Pós-V1 após volume de dados e validação; mais difícil de explicar e calibrar. |

**Recomendação:** Alternativa B, acompanhada por confiança de evidência separada. O índice expressa uma estimativa operacional, não conhecimento absoluto.

### 3.4 Exclusão de dados

| Alternativa | Funcionamento | Avaliação |
|---|---|---|
| A — Apenas exclusão física | Remove sempre. | Prejudica histórico e facilita acidentes. |
| B — Apenas arquivamento | Nunca remove. | Protege histórico, mas reduz controle do usuário sobre seus dados. |
| C — Híbrida | Arquivamento como padrão; exclusão permanente confirmada e transacional em casos autorizados. | Recomendada: equilibra recuperação, integridade e controle do usuário. |

---

## 4. Regras gerais, identidade e tempo

### `RN-001` — Isolamento do espaço individual

Todo registro deverá pertencer a exatamente um espaço individual. Nenhuma regra poderá agregar ou relacionar dados de espaços diferentes.

- **Aplicação:** MVP.
- **Exceção:** Nenhuma no escopo atual.
- **Rastreabilidade:** `RF-001`, `RNF-013`.

### `RN-002` — Determinação de “hoje”

“Hoje” será a data civil corrente no fuso configurado pelo estudante.

- **Aplicação:** MVP.
- **Consequência:** Revisões mudam de futura para devida e de devida para atrasada pela data local, não pelo fuso do servidor.
- **Rastreabilidade:** `RF-002`, `RF-036`, `RNF-030`.

### `RN-003` — Registro temporal da tentativa

Cada tentativa deverá guardar o instante real do evento e o fuso relevante para reconstrução da data exibida.

- **Aplicação:** MVP.
- **Consequência:** Mudança futura de fuso não reescreve o instante histórico.
- **Rastreabilidade:** `RF-021`, `RF-025`, `RNF-030`.

### `RN-004` — Data prevista como data civil

A revisão será devida por uma data civil, sem exigir horário específico dentro daquele dia.

- **Aplicação:** MVP.
- **Consequência:** Durante toda a data prevista, a revisão é “devida hoje”; somente na data seguinte torna-se atrasada.
- **Rastreabilidade:** `RF-035` a `RF-039`.

### `RN-005` — Mudança de fuso

Ao mudar o fuso, instantes históricos e datas previstas já calculadas permanecerão inalterados; somente a determinação da data corrente e os novos cálculos usarão o novo fuso.

- **Aplicação:** MVP.
- **Exceção:** Correção comprovada de fuso configurado incorretamente exigirá procedimento auditável futuro, não reescrita silenciosa.
- **Rastreabilidade:** `RF-003`, `RNF-030`, `RNF-067`.

---

## 5. Hierarquia acadêmica

### `RN-006` — Hierarquia obrigatória

Toda questão ativa deverá possuir exatamente uma disciplina e um assunto pertencente a essa disciplina.

- **Aplicação:** MVP.
- **Exceção:** Rascunho pode estar incompleto.
- **Rastreabilidade:** `RF-004` a `RF-007`.

### `RN-007` — Subassunto opcional e único

Uma questão pode ter zero ou um subassunto, que deverá pertencer ao assunto selecionado.

- **Aplicação:** MVP.
- **Proibição:** Múltiplos subassuntos por questão ficam fora do MVP.
- **Rastreabilidade:** `RF-006`, `RF-010`.

### `RN-008` — Normalização de nomes

Para detectar duplicidade exata em um mesmo nível, nomes serão comparados após remover espaços nas extremidades, reduzir espaços repetidos, normalizar Unicode e ignorar maiúsculas/minúsculas. Acentos não serão removidos.

- **Aplicação:** MVP.
- **Exemplo:** “Álgebra” e “  álgebra ” são duplicados; “Matemática” e “Matematica” geram aviso futuro, mas não bloqueio exato.
- **Rastreabilidade:** `RF-004` a `RF-006`, `RF-ABR-002`.

### `RN-009` — Arquivamento de elemento acadêmico

Arquivar disciplina, assunto ou subassunto tornará o item e seus descendentes indisponíveis para novos vínculos, sem remover vínculos históricos ou arquivar automaticamente questões.

- **Aplicação:** MVP.
- **Consequência:** Questões existentes continuam consultáveis e editáveis em campos não hierárquicos; para mudar sua hierarquia, deverão usar itens ativos.
- **Rastreabilidade:** `RF-008`.

### `RN-010` — Agrupamento pela classificação atual

No MVP, desempenho por conteúdo será agrupado pela hierarquia atual da questão. Se ela for reclassificada, suas tentativas válidas passam ao novo agrupamento.

- **Aplicação:** MVP.
- **Limitação:** Relatório histórico “como era na data” não integra o MVP.
- **Rastreabilidade:** `RF-017`, `RF-053`, `RF-056`.

---

## 6. Questões

### `RN-011` — Estado de rascunho

Questão incompleta será rascunho e não poderá receber tentativa, revisão, domínio ou contagem de questão realizada.

- **Aplicação:** MVP.
- **Exceção:** Será contada separadamente como rascunho quando esse indicador for exibido.
- **Rastreabilidade:** `RF-009`, `RF-048`.

### `RN-012` — Ativação mínima

Para ativar uma questão serão obrigatórios: disciplina ativa, assunto ativo, enunciado não vazio, duas ou mais alternativas textuais distintas e exatamente uma alternativa correta.

- **Aplicação:** MVP.
- **Opcional:** Subassunto, origem, dificuldade, explicação, pegadinha e observações.
- **Rastreabilidade:** `RF-010`, `RF-011`.

### `RN-013` — Tipo suportado no MVP

O MVP aceitará questão objetiva textual com uma única resposta correta. Certo/errado será representado por duas alternativas.

- **Aplicação:** MVP.
- **Proibição:** Discursiva, múltiplas corretas e mídia obrigatória não poderão ser ativadas como se fossem plenamente suportadas.
- **Rastreabilidade:** `ESC-DEC-004`, `RF-011`.

### `RN-014` — Origem opcional

Fonte, banca, prova/concurso, ano e referência poderão ser omitidos e não afetarão o resultado ou o ciclo.

- **Aplicação:** MVP.
- **Validação:** Ano informado deverá ser inteiro dentro de limite plausível definido no modelo de dados.
- **Rastreabilidade:** `RF-012`.

### `RN-015` — Dificuldade da questão

A dificuldade será opcional e limitada a fácil, média ou difícil. Ela descreve a questão e não será usada no Índice de Domínio V1.0.

- **Aplicação:** MVP.
- **Justificativa:** A avaliação é subjetiva e não deverá aumentar ou reduzir domínio sem validação.
- **Rastreabilidade:** `RF-013`, `RF-DEC-004`.

### `RN-016` — Aprendizado enriquecível

Explicação/regra, pegadinha e observações poderão ser preenchidas ou atualizadas após a tentativa inicial sem criar nova tentativa.

- **Aplicação:** MVP.
- **Consequência:** Ausência após erro poderá gerar indicador “aprendizado pendente”, mas não cancelará o ciclo.
- **Rastreabilidade:** `RF-014`, `RF-015`.

### `RN-017` — Estado da questão

Uma questão terá um estado principal entre rascunho, ativa e arquivada. Exclusão permanente não é um estado ativo.

- **Aplicação:** MVP.
- **Consequência:** Somente ativa pode iniciar tentativa ou revisão.
- **Rastreabilidade:** `RF-009`, `RF-010`, `RF-019`.

### `RN-018` — Duplicidade de questão

O MVP não bloqueará questões por semelhança de enunciado, pois versões ou fontes podem ser legítimas. A V1 poderá avisar possíveis duplicidades sem impedir o cadastro.

- **Aplicação:** MVP/V1.
- **Rastreabilidade:** `ESC-V1-008`.

### `RN-019` — Edição não crítica

Enunciado, origem, dificuldade, explicação, pegadinha, observações e hierarquia poderão ser editados, respeitando validações e atualização das métricas afetadas.

- **Aplicação:** MVP.
- **Limite:** Alteração que mude substancialmente o problema deverá preferir nova questão para não descaracterizar tentativas antigas.
- **Rastreabilidade:** `RF-017`.

### `RN-020` — Alteração crítica de gabarito

Antes da primeira tentativa, alternativas e gabarito podem ser alterados. Após tentativa válida, o MVP bloqueará mudança crítica; a V1 exigirá versão/correção auditável.

- **Aplicação:** MVP/V1.
- **Consequência:** Resultados antigos nunca serão reinterpretados silenciosamente.
- **Rastreabilidade:** `RF-018`, `RNF-028`.

---

## 7. Tentativas e classificação de erros

### `RN-021` — Unicidade da tentativa inicial

Cada questão poderá possuir no máximo uma tentativa inicial válida.

- **Aplicação:** MVP.
- **Correção:** Erro de lançamento futuro será tratado por anulação e substituição, não por segunda tentativa inicial concorrente.
- **Rastreabilidade:** `RF-021`, `RF-027`.

### `RN-022` — Imutabilidade de evento finalizado

Resposta dada, resultado, tipo e instante de uma tentativa finalizada não poderão ser editados diretamente.

- **Aplicação:** MVP.
- **Exceção:** Classificação e texto diagnóstico podem ser corrigidos conforme `RN-032`; correção estrutural usa anulação na V1.
- **Rastreabilidade:** `RF-025` a `RF-027`.

### `RN-023` — Resultado calculado

Em questão objetiva, o resultado será correto se e somente se a alternativa dada for a alternativa marcada como correta na versão aplicável da questão.

- **Aplicação:** MVP.
- **Proibição:** Resultado não será digitado livremente.
- **Rastreabilidade:** `RF-022`, `RF-DEC-005`.

### `RN-024` — Acerto inicial

Tentativa inicial correta será registrada e contará para desempenho, mas não iniciará ciclo automático no MVP.

- **Aplicação:** MVP.
- **V1:** Poderá ser incluída manualmente em revisão.
- **Rastreabilidade:** `RF-023`, `RF-045`.

### `RN-025` — Erro inicial

Tentativa inicial incorreta finalizada deverá possuir classificação principal e iniciará exatamente um ciclo.

- **Aplicação:** MVP.
- **Consequência:** Reenvio não cria segundo ciclo.
- **Rastreabilidade:** `RF-024`, `RF-034`, `RNF-026`.

### `RN-026` — Tentativa de revisão

Cada revisão concluída deverá possuir exatamente uma tentativa válida do tipo revisão, vinculada à etapa que a originou.

- **Aplicação:** MVP.
- **Rastreabilidade:** `RF-025`, `RF-043`, `RNF-025`.

### `RN-027` — Registros anulados

Tentativa anulada permanecerá no histórico auditável, mas será excluída de contagens, domínio e decisões de agendamento reconstruídas.

- **Aplicação:** V1.
- **Rastreabilidade:** `RF-027`, `RF-071`.

### `RN-028` — Classificação somente em erro

Tentativa correta não terá classificação de erro. Tentativa incorreta finalizada terá exatamente uma classificação principal.

- **Aplicação:** MVP.
- **Limitação:** Acerto por chute não será classificado como erro no MVP; poderá ser sinalizado pela facilidade percebida ou capacidade futura.
- **Rastreabilidade:** `RF-028`.

### `RN-029` — Categorias padrão estáveis

As categorias padrão terão códigos imutáveis: conceitual, interpretação, cálculo, atenção, fórmula/regra, procedimento, pegadinha, falta de tempo, chute e outra.

- **Aplicação:** MVP.
- **Consequência:** Alterar texto de exibição não altera o código histórico.
- **Rastreabilidade:** `RF-029`, `RNF-055`.

### `RN-030` — Categoria “outra”

Selecionar “outra” exige descrição não vazia após normalização de espaços.

- **Aplicação:** MVP.
- **Rastreabilidade:** `RF-030`.

### `RN-031` — Categorias pessoais

Na V1, categoria pessoal vinculada não poderá ser apagada diretamente; deverá ser desativada ou consolidada com regra auditável.

- **Aplicação:** V1.
- **Rastreabilidade:** `RF-033`.

### `RN-032` — Correção do diagnóstico

Alterar classificação ou descrição recalculará estatísticas de erro, mas não modificará resposta, resultado, data ou estágio da tentativa.

- **Aplicação:** MVP.
- **Rastreabilidade:** `RF-031`, `RF-054`, `RF-056`.

---

## 8. Ciclo de revisão

### `RN-033` — Criação do ciclo

O ciclo será criado após finalização da tentativa inicial incorreta e ficará vinculado à questão e à tentativa que o originou.

- **Aplicação:** MVP.
- **Rastreabilidade:** `RF-034`.

### `RN-034` — Intervalos sucessivos

O ciclo fixo utilizará, nesta ordem, intervalos de 1, 7, 14 e 30 dias contados a partir da conclusão válida que autorizou a próxima etapa.

- **Aplicação:** MVP.
- **Versão da regra:** `REV-FIXA-1.0`.
- **Rastreabilidade:** `VIS-DEC-006`, `RF-035`.

### `RN-035` — Primeira revisão

A primeira revisão será prevista para a data local da tentativa inicial incorreta mais 1 dia civil.

- **Aplicação:** MVP.
- **Exemplo:** Erro em 10/09 gera revisão em 11/09, independentemente do horário.
- **Rastreabilidade:** `RF-034`, `RF-035`.

### `RN-036` — Avanço após acerto

Acerto na etapa de 1d agenda 7d após a data real da conclusão; acerto em 7d agenda 14d; acerto em 14d agenda 30d; acerto em 30d conclui o ciclo.

- **Aplicação:** MVP.
- **Rastreabilidade:** `RF-044`.

### `RN-037` — Reinício após erro

Erro em qualquer etapa encerra a progressão atual, cria nova âncora na data real do erro e agenda revisão de 1d.

- **Aplicação:** MVP.
- **Consequência:** A sequência 1d→7d→14d→30d precisa ser reconstruída após o erro.
- **Rastreabilidade:** `RF-044`.

### `RN-038` — Facilidade sem efeito no MVP

Facilidade fácil/média/difícil será armazenada na tentativa de revisão, mas não alterará intervalo na regra `REV-FIXA-1.0`.

- **Aplicação:** MVP.
- **Futuro:** Algoritmo adaptativo poderá usar o dado sob nova versão.
- **Rastreabilidade:** `RF-042`, `RF-DEC-008`.

### `RN-039` — Uma pendência ativa por ciclo

Cada ciclo terá no máximo uma revisão ativa não concluída. Etapas futuras serão materializadas ou ativadas somente conforme a anterior.

- **Aplicação:** MVP.
- **Consequência:** Atraso não cria pilha de quatro revisões da mesma questão.
- **Rastreabilidade:** `RF-036` a `RF-039`.

### `RN-040` — Situação temporal

Uma revisão ativa será futura quando data prevista > hoje; devida hoje quando igual; atrasada quando menor; concluída quando possuir tentativa válida de conclusão.

- **Aplicação:** MVP.
- **Rastreabilidade:** `RF-036`.

### `RN-041` — Revisão atrasada não avança sozinha

Passagem do tempo não conclui, pula ou avança etapa. A revisão permanece atrasada até conclusão, reagendamento válido ou suspensão.

- **Aplicação:** MVP.
- **Rastreabilidade:** `RF-038`, `ESC-LIM-004`.

### `RN-042` — Início sem efeito histórico

Abrir uma revisão não cria tentativa nem altera sua situação para concluída.

- **Aplicação:** MVP.
- **Rastreabilidade:** `RF-040`.

### `RN-043` — Proteção do gabarito

Antes do envio, gabarito, explicação e pegadinha permanecem ocultos. Após envio, ficam disponíveis para correção.

- **Aplicação:** MVP.
- **Rastreabilidade:** `RF-040`, `RF-041`.

### `RN-044` — Resposta obrigatória

Revisão objetiva não poderá ser submetida sem alternativa selecionada.

- **Aplicação:** MVP.
- **Rastreabilidade:** `RF-041`.

### `RN-045` — Diagnóstico do novo erro

Se a revisão resultar incorreta, a conclusão exigirá classificação principal, que poderá diferir da classificação inicial.

- **Aplicação:** MVP.
- **Rastreabilidade:** `RF-025`, `RF-028`.

### `RN-046` — Conclusão atômica

Tentativa, conclusão, transição do ciclo e próxima data formam uma única operação lógica. Falha em uma parte invalida a operação inteira.

- **Aplicação:** MVP.
- **Rastreabilidade:** `RF-043`, `RNF-025`.

### `RN-047` — Ciclo concluído

O ciclo fica concluído somente após acerto válido na etapa de 30 dias da sequência atual.

- **Aplicação:** MVP.
- **Proibição:** Ciclo concluído não equivale automaticamente a domínio.
- **Rastreabilidade:** `RF-044`, `RF-052`, `RF-DEC-011`.

---

## 9. Atrasos, reagendamento e suspensão

### `RN-048` — Preservação da data prevista

Concluir revisão atrasada deverá preservar a data originalmente prevista e registrar separadamente a data real de conclusão.

- **Aplicação:** MVP.
- **Rastreabilidade:** `RF-038`, `RF-046`.

### `RN-049` — Próximo intervalo após atraso

Após acerto em revisão atrasada, o próximo intervalo será contado da data real de conclusão, não da data que havia sido prevista.

- **Aplicação:** MVP.
- **Justificativa:** Mantém o espaçamento real completo entre recuperações.
- **Rastreabilidade:** `RN-034`, `RF-044`.

### `RN-050` — Erro em revisão atrasada

Erro em revisão atrasada aplica o mesmo reinício de 1 dia de qualquer outro erro, usando a data real da tentativa como nova âncora.

- **Aplicação:** MVP.
- **Rastreabilidade:** `RN-037`.

### `RN-051` — Atraso não é erro de conteúdo

Uma revisão atrasada não será contabilizada como tentativa incorreta. Atraso e resultado são dimensões distintas.

- **Aplicação:** MVP.
- **Consequência:** O atraso influencia prioridade e disciplina de revisão, mas não reduz diretamente a taxa de acerto.
- **Rastreabilidade:** `RF-038`, `RF-049`.

### `RN-052` — Reagendamento permitido

Na V1, somente revisão ativa e não concluída poderá ser reagendada para hoje ou data futura.

- **Aplicação:** V1.
- **Proibição:** Data retroativa ou reagendamento de revisão concluída.
- **Rastreabilidade:** `RF-046`.

### `RN-053` — Histórico do reagendamento

Reagendamento deverá guardar data anterior, nova data, instante da ação e motivo obrigatório.

- **Aplicação:** V1.
- **Consequência:** Reagendar não apaga o fato de que a data original venceu.
- **Rastreabilidade:** `RF-046`, `RF-071`.

### `RN-054` — Métrica de atraso após reagendamento

Indicadores históricos de pontualidade usarão a primeira data válida prevista para a etapa; a fila operacional usará a última data reagendada válida.

- **Aplicação:** V1.
- **Justificativa:** Evita que reagendamento melhore artificialmente o histórico.
- **Rastreabilidade:** `RF-046`, `VIS-PRI-005`.

### `RN-055` — Arquivamento suspende ciclo

Arquivar questão ativa suspenderá sua revisão pendente e retirará o item das filas, preservando ciclo, datas e tentativas.

- **Aplicação:** MVP.
- **Reativação futura:** Deverá decidir se retoma a pendência ou inicia novo ciclo; essa função não integra o MVP.
- **Rastreabilidade:** `RF-019`.

---

## 10. Contabilização e desempenho

### `RN-056` — Questões cadastradas

“Questões cadastradas” contará rascunhos, ativas e arquivadas existentes, com possibilidade de detalhamento por estado.

- **Aplicação:** MVP.
- **Exclusão:** Questões permanentemente excluídas não permanecem no total atual.
- **Rastreabilidade:** `RF-048`.

### `RN-057` — Questões realizadas

“Questões realizadas” contará questões com uma tentativa inicial válida, cada questão no máximo uma vez.

- **Aplicação:** MVP.
- **Consequência:** Revisões não aumentam essa contagem.
- **Rastreabilidade:** `RF-021`, `RF-048`.

### `RN-058` — Total de tentativas

“Tentativas realizadas” contará todas as tentativas válidas, iniciais e de revisão, no período selecionado.

- **Aplicação:** MVP.
- **Exclusão:** Tentativas anuladas.
- **Rastreabilidade:** `RF-048`, `RF-049`.

### `RN-059` — Acertos e erros

Total de acertos e erros será calculado sobre tentativas válidas; a soma deverá ser igual ao total de tentativas objetivas válidas consideradas.

- **Aplicação:** MVP.
- **Rastreabilidade:** `RF-049`, `RNF-029`.

### `RN-060` — Taxa de acerto

Taxa de acerto = `tentativas corretas válidas ÷ tentativas válidas consideradas × 100`.

- **Aplicação:** MVP.
- **Sem dados:** Se o denominador for zero, exibir “sem dados”, nunca 0%.
- **Rastreabilidade:** `RF-049`, `RF-055`.

### `RN-061` — Separação por tipo

Sempre que uma métrica reunir tentativas iniciais e revisões, o sistema deverá permitir ver as duas parcelas ou informar explicitamente que o valor é combinado.

- **Aplicação:** MVP.
- **Justificativa:** Revisões repetidas da mesma questão não podem ser confundidas com novas questões.
- **Rastreabilidade:** `RF-048`, `RF-049`.

### `RN-062` — Revisões realizadas hoje

“Revisões realizadas hoje” contará revisões concluídas cuja tentativa correspondente ocorreu na data local atual.

- **Aplicação:** MVP.
- **Invariante:** O total deve ser igual ao número de tentativas de revisão válidas de hoje.
- **Rastreabilidade:** `RF-050`.

### `RN-063` — Revisões pendentes

Contagens de hoje, atrasadas e futuras considerarão apenas a única revisão ativa de cada ciclo não suspenso.

- **Aplicação:** MVP.
- **Rastreabilidade:** `RF-051`, `RN-039`.

### `RN-064` — Desempenho por hierarquia

Desempenho de disciplina, assunto ou subassunto usará tentativas válidas das questões atualmente vinculadas ao nível, respeitando o período e a separação por tipo.

- **Aplicação:** MVP.
- **Rastreabilidade:** `RF-053`, `RN-010`.

### `RN-065` — Frequência de erro

Frequência por categoria contará tentativas incorretas válidas classificadas naquela categoria, e não questões distintas, salvo indicador explicitamente denominado “questões afetadas”.

- **Aplicação:** MVP.
- **Rastreabilidade:** `RF-054`.

### `RN-066` — Período das métricas

Toda métrica temporal deverá declarar período inicial e final ou indicar “todo o histórico”.

- **Aplicação:** MVP.
- **Rastreabilidade:** `RF-047`, `RF-055`.

### `RN-067` — Arredondamento

Percentuais serão calculados com valor integral interno e exibidos com uma casa decimal. Limiares usarão o valor não arredondado.

- **Aplicação:** MVP.
- **Exemplo:** 74,96 será exibido como 75,0, mas um limiar de 75 será avaliado sobre 74,96 e não será alcançado.
- **Rastreabilidade:** `RNF-029`.

---

## 11. Índice de Domínio — modelo recomendado V1.0

### 11.1 Unidade de cálculo

O cálculo começa por questão. Disciplina, assunto e subassunto agregam os valores das questões, impedindo que repetir uma única questão muitas vezes domine a matéria inteira.

### 11.2 Componentes da questão

Para uma questão `q`, serão calculados quatro componentes de 0 a 100.

#### A. Acerto recente — `Aq`

Usa até as cinco tentativas válidas mais recentes, com pesos decrescentes a partir da mais recente:

`1,00; 0,70; 0,49; 0,343; 0,2401`.

Cada acerto vale 1 e cada erro vale 0:

`Aq = 100 × soma(peso × resultado) ÷ soma(pesos usados)`.

A razão 0,70 preserva memória do histórico, mas dá maior influência à evidência recente.

#### B. Progressão espaçada — `Pq`

| Maior etapa corretamente concluída desde o último erro | `Pq` |
|---|---:|
| Nenhuma | 0 |
| 1 dia | 25 |
| 7 dias | 50 |
| 14 dias | 75 |
| 30 dias | 100 |

Um erro reinicia `Pq` em 0 conforme `RN-037`.

#### C. Fluência de recuperação — `Fq`

Usa até três revisões corretas mais recentes com facilidade informada:

| Facilidade | Valor |
|---|---:|
| Fácil | 100 |
| Média | 75 |
| Difícil | 50 |

`Fq` é a média dos valores disponíveis. Se não houver facilidade informada, usa 75 como valor neutro e o fato é mostrado na explicação.

#### D. Controle de recorrência — `Eq`

Considera erros de revisão após a tentativa inicial no ciclo atual:

| Situação | `Eq` |
|---|---:|
| Menos de duas tentativas válidas | 50 |
| Nenhum erro de revisão no ciclo atual | 100 |
| Um erro de revisão no ciclo atual | 50 |
| Dois ou mais erros de revisão no ciclo atual | 0 |

### 11.3 Fórmula da questão

`M_q = 0,45 × Aq + 0,30 × Pq + 0,15 × Fq + 0,10 × Eq`

Justificativa dos pesos:

- **45% acerto recente:** evidência direta, mas não suficiente isoladamente;
- **30% progressão espaçada:** valoriza retenção em intervalos reais;
- **15% fluência:** diferencia acerto fácil de recuperação muito difícil;
- **10% recorrência:** penaliza repetição sem dominar o índice.

### `RN-068` — Fórmula versionada

O Índice de Domínio da questão V1.0 usará a fórmula acima sob o identificador `DOM-HEUR-1.0`.

- **Aplicação:** V1.
- **Rastreabilidade:** `RF-057`, `RF-060`, `RNF-055`.

### `RN-069` — Tentativas elegíveis

Somente tentativas válidas participam de `Aq`, `Pq`, `Fq` e `Eq`; rascunhos, revisões apenas abertas e tentativas anuladas são excluídos.

- **Aplicação:** V1.
- **Rastreabilidade:** `RF-057`, `RN-027`.

### `RN-070` — Limite de recuperação após erro

Após o último erro, `M_q` será limitado conforme a maior recuperação correta posterior:

| Evidência correta após o último erro | Teto |
|---|---:|
| Nenhuma | 40 |
| Etapa de 1 dia | 60 |
| Etapa de 7 dias | 75 |
| Etapa de 14 dias | 90 |
| Etapa de 30 dias | 100 |

- **Aplicação:** V1.
- **Justificativa:** O simples passar do tempo não aumenta domínio; é necessária recuperação bem-sucedida.
- **Rastreabilidade:** `VIS-DEC-008`, `RF-057`.

### `RN-071` — Domínio de questão sem erro

Questão inicialmente correta e sem ciclo poderá receber `M_q` provisório, mas não poderá ser marcada como dominada sem evidência espaçada.

- **Aplicação:** V1.
- **Rastreabilidade:** `RF-023`, `RF-045`, `RF-061`.

### 11.4 Confiança da questão

A confiança representa quantidade, espaçamento e atualidade da evidência, não desempenho.

Base de evidência desde o último erro:

| Evidência registrada | Confiança-base |
|---|---:|
| Tentativa inicial válida | 20 |
| Mais etapa 1d tentada | 40 |
| Mais etapa 7d tentada | 60 |
| Mais etapa 14d tentada | 80 |
| Mais etapa 30d tentada | 100 |

Fator de atualidade, calculado pelos dias desde a última tentativa válida:

| Idade da última evidência | Fator |
|---|---:|
| 0–60 dias | 1,00 |
| 61–120 dias | 0,90 |
| 121–180 dias | 0,75 |
| 181–365 dias | 0,50 |
| Mais de 365 dias | 0,25 |

`C_q = confiança-base × fator de atualidade`.

### `RN-072` — Confiança separada

`C_q` deverá ser exibida separadamente de `M_q`; baixa confiança não será escondida dentro da pontuação.

- **Aplicação:** V1.
- **Rastreabilidade:** `RF-058`, `VIS-PRI-005`.

### `RN-073` — Evidência antiga

Queda de confiança por envelhecimento não altera retroativamente `M_q`, mas pode remover o estado de domínio atual e gerar indicação “evidência desatualizada”.

- **Aplicação:** V1.
- **Rastreabilidade:** `RF-058`, `RF-061`.

### 11.5 Agregação hierárquica

Para um nível `h`:

`M_h = média aritmética dos M_q das questões ativas realizadas pertencentes ao nível`.

Cada questão possui peso igual. Número de tentativas da questão não aumenta seu peso na matéria.

Fator de quantidade de questões distintas `N_h`:

| Questões distintas | `N_h` |
|---|---:|
| 0 | 0 |
| 1–2 | 20 |
| 3–5 | 40 |
| 6–10 | 60 |
| 11–20 | 80 |
| 21 ou mais | 100 |

Cobertura média: `Cob_h = média dos C_q`.

Confiança hierárquica:

`C_h = 0,60 × N_h + 0,40 × Cob_h`.

### `RN-074` — Peso igual por questão

Na agregação V1.0, cada questão ativa realizada terá peso igual; dificuldade subjetiva e quantidade de revisões não aumentarão seu peso.

- **Aplicação:** V1.
- **Justificativa:** Evita que uma questão repetida ou marcada como difícil distorça todo o assunto.
- **Rastreabilidade:** `RF-059`.

### `RN-075` — Inclusão hierárquica

Disciplina inclui questões ligadas a todos os seus assuntos; assunto inclui questões diretas e de seus subassuntos; subassunto inclui somente suas questões.

- **Aplicação:** V1.
- **Rastreabilidade:** `RF-059`.

### `RN-076` — Questões arquivadas no domínio atual

Questões arquivadas serão excluídas do domínio atual, mas permanecerão disponíveis em relatórios históricos explicitamente identificados.

- **Aplicação:** V1.
- **Rastreabilidade:** `RF-019`, `RF-059`.

### `RN-077` — Faixas de confiança

| `C_h` | Interpretação |
|---|---|
| Sem questões | Sem dados |
| 0–39,99 | Evidência insuficiente |
| 40–59,99 | Confiança baixa |
| 60–79,99 | Confiança moderada |
| 80–100 | Confiança alta |

- **Aplicação:** V1.
- **Consequência:** Nível com confiança inferior a 40 não será classificado como forte ou fraco.
- **Rastreabilidade:** `RF-058`, `RF-059`.

### `RN-078` — Faixas descritivas de domínio

| `M` | Rótulo |
|---|---|
| 0–39,99 | Frágil |
| 40–59,99 | Em desenvolvimento |
| 60–74,99 | Intermediário |
| 75–89,99 | Bom |
| 90–100 | Forte |

- **Aplicação:** V1.
- **Condição:** O rótulo deverá ser acompanhado da confiança; com confiança insuficiente, será “provisório”.
- **Rastreabilidade:** `RF-057` a `RF-060`.

### `RN-079` — Critério de questão dominada

Uma questão será marcada como dominada somente se, simultaneamente:

1. concluiu corretamente a etapa de 30 dias desde o último erro;
2. possui `M_q ≥ 85` usando valor não arredondado;
3. possui `C_q ≥ 80`;
4. as duas revisões válidas mais recentes são corretas;
5. não possui revisão ativa atrasada;
6. está ativa.

- **Aplicação:** V1.
- **Justificativa:** Domínio exige retenção espaçada e evidência suficiente, não apenas pontuação.
- **Rastreabilidade:** `RF-061`, `ESC-ABR-007`.

### `RN-080` — Reabertura de questão dominada

Questão dominada deixará imediatamente esse estado se ocorrer novo erro válido, anulação que remova evidência essencial, arquivamento ou queda de `C_q` abaixo de 80. Ação manual poderá reabrir com motivo sem apagar o domínio anterior.

- **Aplicação:** V1.
- **Consequência:** Novo erro inicia ciclo de 1 dia conforme `RN-037`.
- **Rastreabilidade:** `RF-061`, `RF-071`.

---

## 12. Priorização “O que estudar agora?” — V1

### 12.1 Fatores normalizados

Para cada assunto elegível, serão calculados valores de 0 a 100:

- `W` — fraqueza: `100 - M_h`;
- `O` — pressão de atraso: proporção de questões ativas do assunto com revisão atrasada, limitada a 100;
- `R` — recorrência: proporção de questões distintas com erro de revisão recorrente no período de análise;
- `D` — queda recente: redução positiva entre desempenho histórico comparável e desempenho recente, limitada a 100.

### 12.2 Fórmula recomendada

`Prioridade_h = 0,40 × W + 0,30 × O + 0,20 × R + 0,10 × D`

Os pesos colocam fragilidade e atraso como fatores principais, sem ignorar recorrência e piora recente.

### `RN-081` — Elegibilidade da prioridade

Assunto com `C_h < 40` não receberá ranking normal de fraqueza; será classificado como “coletar mais evidências”. Revisões atrasadas continuam visíveis na fila operacional independentemente da confiança.

- **Aplicação:** V1.
- **Rastreabilidade:** `RF-062`, `RN-077`.

### `RN-082` — Fórmula versionada de prioridade

A fórmula recomendada será identificada como `PRI-HEUR-1.0` e usará os fatores e pesos da seção 12.2.

- **Aplicação:** V1.
- **Rastreabilidade:** `RF-062`, `RNF-055`.

### `RN-083` — Justificativa da prioridade

Cada assunto recomendado deverá mostrar os fatores que mais contribuíram, como “domínio baixo”, “quatro revisões atrasadas” ou “erro recorrente de interpretação”.

- **Aplicação:** V1.
- **Proibição:** Exibir apenas uma posição sem explicação.
- **Rastreabilidade:** `RF-062`, `VIS-PRI-010`.

### `RN-084` — Recomendação não obrigatória

O estudante poderá ignorar ou escolher outro assunto; a recomendação não alterará automaticamente revisões, domínio ou plano de estudos.

- **Aplicação:** V1.
- **Rastreabilidade:** `RF-062`.

---

## 13. Histórico, edição, anulação e exclusão

### `RN-085` — Histórico mínimo da questão

O histórico deverá permitir reconstruir tentativa inicial, revisões planejadas, datas realizadas, resultados, classificações, reinícios e conclusão do ciclo.

- **Aplicação:** MVP.
- **Rastreabilidade:** `RF-026`, `RNF-028`.

### `RN-086` — Edição não cria tentativa

Editar conteúdo ou metadado da questão não cria tentativa, não conclui revisão e não muda taxa de acerto por si só.

- **Aplicação:** MVP.
- **Exceção:** Mudar hierarquia altera agrupamentos atuais conforme `RN-010`.
- **Rastreabilidade:** `RF-015`, `RF-017`.

### `RN-087` — Arquivamento como ação padrão

Para questão com histórico, a ação recomendada será arquivar. O sistema deverá explicar que o histórico permanece e as revisões são suspensas.

- **Aplicação:** MVP.
- **Rastreabilidade:** `RF-019`, `RN-055`.

### `RN-088` — Exclusão de rascunho

Rascunho sem tentativa, ciclo ou dependência poderá ser excluído permanentemente após confirmação simples.

- **Aplicação:** MVP.
- **Rastreabilidade:** `RF-009`, `RF-020`.

### `RN-089` — Exclusão permanente de questão com histórico

Na V1, exclusão permanente deverá informar quantidades afetadas, oferecer exportação quando possível, exigir confirmação reforçada e remover questão, tentativas, revisões e dependências em uma única operação.

- **Aplicação:** V1.
- **Consequência:** Métricas atuais serão recalculadas; registros técnicos mínimos não poderão reter conteúdo excluído.
- **Rastreabilidade:** `RF-020`, `RF-071`, `RNF-024`.

### `RN-090` — Proibição de órfãos na exclusão

Nenhuma exclusão poderá deixar tentativa, revisão, ciclo ou classificação de ocorrência sem seu registro pai.

- **Aplicação:** MVP/V1.
- **Rastreabilidade:** `RNF-027`.

### `RN-091` — Tentativa não é excluída isoladamente

Na V1, erro de lançamento em tentativa será tratado por anulação e, quando necessário, substituição. Exclusão isolada direta não será oferecida.

- **Aplicação:** V1.
- **Justificativa:** Preserva explicação da mudança e permite reconstruir métricas.
- **Rastreabilidade:** `RF-027`.

### `RN-092` — Reconstrução após anulação

Se a tentativa anulada influenciou ciclo ou domínio, o sistema deverá reconstruir os estados derivados a partir do último evento válido anterior, usando a versão de regra aplicável.

- **Aplicação:** V1.
- **Proibição:** Apenas subtrair a tentativa das estatísticas e deixar datas incoerentes.
- **Rastreabilidade:** `RF-027`, `RNF-029`.

### `RN-093` — Correção de gabarito após histórico

Na V1, correção de gabarito criará nova versão da questão. Tentativas anteriores manterão a versão usada; eventual correção de resultados exigirá procedimento auditável separado.

- **Aplicação:** V1.
- **Rastreabilidade:** `RF-018`, `RNF-055`.

### `RN-094` — Exclusão de item acadêmico

Disciplina, assunto ou subassunto sem vínculo poderá ser excluído; com vínculo histórico deverá ser arquivado ou ter os vínculos validamente migrados antes da exclusão.

- **Aplicação:** MVP/V1.
- **Rastreabilidade:** `RF-008`, `RNF-027`.

### `RN-095` — Mudança de regra de cálculo

Nova fórmula de domínio, prioridade ou revisão receberá novo identificador. O valor atual poderá ser recalculado pela nova versão, mas snapshots ou eventos anteriores manterão a versão que os produziu.

- **Aplicação:** V1 e futuro.
- **Rastreabilidade:** `RF-060`, `RNF-055`.

### `RN-096` — Ordem de recálculo

Após alteração válida, o sistema deverá primeiro confirmar a fonte, depois reconstruir ciclos afetados, em seguida recalcular métricas e por último recalcular domínio/prioridades.

- **Aplicação:** V1.
- **Justificativa:** Evita valores derivados de estado intermediário inconsistente.
- **Rastreabilidade:** `RF-056`, `RNF-025`, `RNF-029`.

---

## 14. Tratamento de dados insuficientes

### `RN-097` — Ausência de tentativas

Sem tentativa válida, não haverá taxa de acerto nem Índice de Domínio; o estado será “sem dados”.

- **Aplicação:** MVP/V1.
- **Rastreabilidade:** `RF-049`, `RN-060`.

### `RN-098` — Amostra insuficiente

Pontuação baseada em uma ou duas questões poderá ser exibida como provisória, mas não classificará disciplina/assunto como forte ou fraco.

- **Aplicação:** V1.
- **Rastreabilidade:** `RN-077`, `RF-058`.

### `RN-099` — Evidência ausente não vira zero

Campo ou componente sem observação não será automaticamente transformado em desempenho zero; deverá usar valor neutro explicitado ou impedir o cálculo, conforme regra específica.

- **Aplicação:** MVP/V1.
- **Exemplo:** Facilidade ausente usa 75 neutro; taxa sem tentativas não existe.
- **Rastreabilidade:** `RN-060`, `RN-068`.

### `RN-100` — Explicação da insuficiência

Quando não houver dados suficientes, o sistema deverá informar o que falta: mais questões distintas, revisões espaçadas, evidência recente ou outro critério objetivo.

- **Aplicação:** V1.
- **Rastreabilidade:** `RF-058`, `RF-060`.

---

## 15. Exemplos normativos

### 15.1 Ciclo sem erros e no prazo

1. Tentativa inicial incorreta em 10/09.
2. Revisão 1d prevista para 11/09; acerto em 11/09.
3. Revisão 7d prevista para 18/09; acerto em 18/09.
4. Revisão 14d prevista para 02/10; acerto em 02/10.
5. Revisão 30d prevista para 01/11; acerto em 01/11.
6. Ciclo concluído em 01/11.

### 15.2 Revisão atrasada

1. Erro inicial em 10/09; revisão prevista em 11/09.
2. O estudante realiza em 15/09 e acerta.
3. O histórico mantém prevista 11/09 e realizada 15/09.
4. A próxima revisão é 22/09, sete dias após a realização real.

### 15.3 Erro no meio do ciclo

1. Etapas 1d e 7d foram concluídas corretamente.
2. Na etapa 14d, em 02/10, ocorre erro de interpretação.
3. A progressão é reiniciada e a próxima revisão fica para 03/10.
4. A nova tentativa guarda “interpretação”, sem apagar o erro inicial anterior.

### 15.4 Exemplo de domínio da questão

Considere tentativa inicial errada seguida por quatro revisões corretas e fáceis, concluindo 30d:

- `Aq ≈ 91,3` pela ponderação recente;
- `Pq = 100`;
- `Fq = 100`;
- `Eq = 100`;
- `M_q ≈ 0,45×91,3 + 0,30×100 + 0,15×100 + 0,10×100 ≈ 96,1`;
- `C_q = 100` se a evidência tiver até 60 dias.

Se as demais condições de `RN-079` forem atendidas, a questão será dominada.

### 15.5 Exemplo hierárquico

Um assunto com oito questões tem:

- média `M_h = 72`;
- `N_h = 60` pela faixa de 6–10 questões;
- média de confiança das questões `Cob_h = 75`.

Logo:

`C_h = 0,60×60 + 0,40×75 = 66`.

O domínio é **Intermediário**, com **confiança moderada**.

---

## 16. Rastreabilidade resumida

| Tema | Regras | Requisitos principais |
|---|---|---|
| Tempo e fuso | `RN-001` a `RN-005` | `RF-001` a `RF-003`, `RNF-030` |
| Hierarquia | `RN-006` a `RN-010` | `RF-004` a `RF-008` |
| Questões | `RN-011` a `RN-020` | `RF-009` a `RF-020` |
| Tentativas e erros | `RN-021` a `RN-032` | `RF-021` a `RF-033` |
| Revisão | `RN-033` a `RN-055` | `RF-034` a `RF-046` |
| Estatísticas | `RN-056` a `RN-067` | `RF-047` a `RF-056` |
| Domínio e confiança | `RN-068` a `RN-080` | `RF-057` a `RF-061` |
| Prioridade | `RN-081` a `RN-084` | `RF-062` |
| Histórico e exclusão | `RN-085` a `RN-096` | `RF-017` a `RF-020`, `RF-027`, `RF-071` |
| Dados insuficientes | `RN-097` a `RN-100` | `RF-049`, `RF-057` a `RF-060` |

---

## 17. Decisões propostas nesta etapa

| ID | Decisão proposta |
|---|---|
| `RN-DEC-001` | Os intervalos 1d, 7d, 14d e 30d serão sucessivos, contados da conclusão real anterior. |
| `RN-DEC-002` | Erro em qualquer revisão reiniciará o ciclo em 1 dia. |
| `RN-DEC-003` | Revisão atrasada não avança automaticamente nem conta como erro. |
| `RN-DEC-004` | Reagendamento V1 preservará data original e exigirá motivo. |
| `RN-DEC-005` | Taxas combinarão apenas tentativas válidas e sempre informarão denominador/período. |
| `RN-DEC-006` | O domínio V1 usará a heurística `DOM-HEUR-1.0`, separada da confiança. |
| `RN-DEC-007` | A fórmula da questão terá pesos 45% acerto recente, 30% progressão, 15% fluência e 10% recorrência. |
| `RN-DEC-008` | O domínio após erro ficará sujeito aos tetos de recuperação 40/60/75/90/100. |
| `RN-DEC-009` | Hierarquias usarão peso igual por questão e confiança combinando quantidade e cobertura. |
| `RN-DEC-010` | Questão dominada exigirá etapa 30d correta, `M_q ≥ 85`, `C_q ≥ 80` e demais condições de `RN-079`. |
| `RN-DEC-011` | Prioridade V1 usará `PRI-HEUR-1.0`, com pesos 40/30/20/10. |
| `RN-DEC-012` | Arquivamento será padrão; exclusão permanente seguirá modelo híbrido e transacional. |
| `RN-DEC-013` | Gabarito corrigido após tentativas gerará versão e procedimento auditável na V1. |
| `RN-DEC-014` | Dados insuficientes serão informados, nunca convertidos silenciosamente em zero ou certeza. |

---

## 18. Pontos ainda em aberto

| ID | Ponto | Etapa de decisão |
|---|---|---|
| `RN-ABR-001` | Limites máximos de textos e ano plausível. | Modelo de Dados e SDD. |
| `RN-ABR-002` | Fluxo de reativação de questão arquivada e retomada do ciclo. | Fluxos/Roadmap; V1. |
| `RN-ABR-003` | Janela temporal exata dos fatores recorrência e queda recente da prioridade. | Roadmap e testes com dados reais. |
| `RN-ABR-004` | Se o domínio atual será recalculado imediatamente ao lançar nova versão da fórmula ou mediante migração agendada. | SDD. |
| `RN-ABR-005` | Política legal/operacional de retenção de auditoria após exclusão pública. | RNFs, SDD e análise jurídica futura. |
| `RN-ABR-006` | Tratamento de tentativa iniciada e abandonada. | Fluxos principais. |
| `RN-ABR-007` | Possibilidade de pausar ciclo sem arquivar a questão. | Roadmap; não pertence ao MVP atual. |
| `RN-ABR-008` | Calibração futura dos pesos de domínio e prioridade com dados reais. | Pós-V1; exige nova versão das regras. |

---

## 19. Riscos

| ID | Risco | Resposta proposta |
|---|---|---|
| `RN-RIS-001` | Ciclo sucessivo parecer mais longo que o esperado. | Explicar que os números são intervalos reais; comparar no roadmap e na interface. |
| `RN-RIS-002` | Reinício em 1d desmotivar após erro tardio. | Manter no modelo fixo pela clareza; avaliar adaptativo apenas com evidência. |
| `RN-RIS-003` | Fórmula de domínio parecer científica demais. | Exibir componentes, versão, confiança e aviso de estimativa operacional. |
| `RN-RIS-004` | Facilidade subjetiva distorcer pontuação. | Peso limitado a 15%, escala curta e valor neutro quando ausente. |
| `RN-RIS-005` | Uma matéria com poucas questões parecer forte. | Confiança separada e bloqueio de classificação com evidência insuficiente. |
| `RN-RIS-006` | Reagendamento ocultar procrastinação. | Preservar primeira data e separar fila operacional da pontualidade histórica. |
| `RN-RIS-007` | Reclassificar questão reescrever análises históricas. | Documentar uso da hierarquia atual no MVP e avaliar snapshots depois. |
| `RN-RIS-008` | Exclusão destruir informação acidentalmente. | Arquivamento padrão, confirmação reforçada e backup/exportação. |
| `RN-RIS-009` | Mudança de fórmula quebrar comparações. | Versionamento e snapshots com identificador da regra. |
| `RN-RIS-010` | Acerto por memorização da alternativa inflar domínio. | Peso igual por questão, espaçamento real e confiança; variedade será avaliada futuramente. |

---

## 20. Sugestões de melhoria

### 20.1 Exibir uma linha do tempo do ciclo

Mostrar cada etapa, data prevista, data real, resultado e eventual reinício tornará a regra sucessiva intuitiva.

### 20.2 Simular a fórmula antes da implementação

Criar uma planilha ou pequeno simulador com cenários de acertos, erros, atrasos e facilidade permitirá validar `DOM-HEUR-1.0` antes de congelar a implementação.

### 20.3 Manter pontuação e confiança lado a lado

Nunca ocultar confiança em tooltip secundário. “90 com baixa confiança” é substancialmente diferente de “90 com alta confiança”.

### 20.4 Avaliar diversidade no Pós-V1

O domínio de assunto poderá futuramente considerar diversidade de fontes e questões, mas somente após evitar dupla contagem e viés por dificuldade subjetiva.

### 20.5 Registrar o motivo das mudanças sensíveis

Reagendamentos, anulações, consolidações de categoria e correções de gabarito devem solicitar motivo curto, tornando suporte e auditoria muito mais claros.

---

## 21. Itens que precisam de aprovação

1. As regras `RN-001` a `RN-100`.
2. Intervalos sucessivos em vez de marcos absolutos.
3. Reinício em 1 dia após qualquer erro de revisão.
4. Tratamento de atrasos e reagendamento.
5. Definições de questões, tentativas, acertos, erros e taxas.
6. A fórmula `DOM-HEUR-1.0` e seus pesos.
7. Os tetos de recuperação após erro.
8. O cálculo separado de confiança da questão e da hierarquia.
9. O critério formal de questão dominada e reabertura.
10. A fórmula de prioridade `PRI-HEUR-1.0`.
11. O modelo híbrido de arquivamento e exclusão.
12. As decisões `RN-DEC-001` a `RN-DEC-014`.
13. A manutenção dos pontos `RN-ABR-001` a `RN-ABR-008`.

---

## 22. Critério de encerramento

A Etapa 5 será concluída quando:

- regras de criação, tentativa, erro, revisão e atraso estiverem aprovadas;
- cálculos de desempenho forem inequívocos;
- domínio e confiança possuírem fórmula, versão e tratamento de insuficiência;
- estado dominado e reabertura forem formalizados;
- edição, anulação, arquivamento e exclusão preservarem integridade;
- alternativas rejeitadas e justificativas estiverem registradas;
- todas as regras puderem orientar SDD, modelo de dados, fluxos e testes.

A etapa foi aprovada integralmente em 30 de agosto de 2026. As regras `RN-001` a `RN-100` e as decisões `RN-DEC-001` a `RN-DEC-014` passam a ser consideradas congeladas e somente poderão ser alteradas mediante registro explícito, nova versão quando aplicável e análise de impacto.

---

## 23. Errata controlada da V0.2 — aplicação das regras

`ADR-010` define os seguintes recortes sem modificar a regra integral futura:

| Regra | Aplicação V0.2 | Parcela futura |
|---|---|---|
| `RN-006`–`RN-009` | Integral para taxonomia e vínculo de questão | N/A |
| `RN-010` | Apenas a classificação atual da questão é persistida | Reagrupamento de desempenho: V0.4 |
| `RN-011` | Rascunho não é ativo e não aparece na lista ativa | Tentativa/revisão/domínio/contagem: V0.3/V0.4 |
| `RN-012`–`RN-015` | Integral | Efeitos de origem/dificuldade sobre análises não entram |
| `RN-016` | Explicação, pegadinha e observações são enriquecíveis por nova revisão, sem criar tentativa | Comportamento após tentativa e indicador de aprendizado: V0.3/V0.4 |
| `RN-017`, `RN-018` | Integral para estados e ausência de bloqueio semântico | N/A |
| `RN-019` | Edição validada cria revisão quando altera conteúdo e não cria tentativa | Efeito em métricas: V0.4 |
| `RN-020` | Permitir e versionar mudança crítica no estado sem tentativa | Bloqueio após tentativa: V0.3; correção: V1 |
| `RN-085` | Não aplicável: trata história de aprendizagem | V0.3/V0.4 |
| `RN-086` | Edição do catálogo não cria tentativa ou revisão de aprendizagem | Comprovação com entidades de aprendizagem: V0.3 |
| `RN-087` | Arquivamento é a ação V0.2; conteúdo versionado permanece | Suspensão de revisões: V0.3 |
| `RN-088`–`RN-090` | Não aplicáveis: nenhuma exclusão física na V0.2 | V1, após política de `RF-020` |
| `RN-093` | Não aplicável | V1 |
| `RN-094` | Somente fundamenta que item com vínculo deve ser arquivado; exclusão não é oferecida | Exclusão/migração de vínculo: V1 |

Tags não recebem regra nova nesta versão. A leitura anterior do Roadmap que
associava indiscriminadamente `RN-085`–`RN-094` à V0.2 foi corrigida por
`ERR-V02-002` e `ERR-V02-004`.
