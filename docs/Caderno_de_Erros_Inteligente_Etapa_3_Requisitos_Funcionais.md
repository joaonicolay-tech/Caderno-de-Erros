# Caderno de Erros Inteligente

## Etapa 3 — Requisitos Funcionais

| Campo | Valor |
|---|---|
| Documento | Especificação de Requisitos Funcionais |
| Projeto | Caderno de Erros Inteligente |
| Versão | 1.0.1 — errata V0.2 |
| Data | 30 de agosto de 2026 |
| Status | Aprovada e congelada; errata de fase V0.2 incorporada em 5 de setembro de 2026 |
| Aprovação | Aprovada integralmente pelo responsável pelo produto em 30 de agosto de 2026 |
| Base congelada | Etapa 1 — Visão 1.0; Etapa 2 — Escopo 1.0 |
| Próxima etapa após aprovação | Etapa 4 — Requisitos Não Funcionais |

---

## 1. Finalidade

Este documento transforma o escopo aprovado em comportamentos funcionais verificáveis. Cada requisito possui identificador estável para rastreabilidade com regras de negócio, arquitetura, dados, fluxos e testes.

Este documento define **o que o sistema deverá fazer**. Ele não define ainda detalhes de tecnologia, fórmulas do Índice de Domínio, política completa de exclusão ou a regra exata após acerto, erro e atraso em uma revisão. Esses elementos serão especificados nas etapas correspondentes.

---

## 2. Convenções

### 2.1 Atores

| Ator | Definição |
|---|---|
| Estudante | Pessoa que utiliza seu espaço individual de estudo. |
| Sistema | Componentes que validam, calculam, armazenam e apresentam informações. |

Não há ator professor, administrador institucional, equipe ou integração externa no MVP.

### 2.2 Prioridades

| Prioridade | Significado |
|---|---|
| MVP — Essencial | Obrigatório para concluir o MVP. |
| MVP — Alta | Necessário para uso seguro ou contínuo do MVP. |
| V1 — Alta | Obrigatório para consolidar a V1, mas não bloqueia o primeiro MVP. |
| V1 — Média | Desejável na V1, sujeito à ordem do roadmap. |

### 2.3 Estados funcionais principais

| Conceito | Estados contemplados |
|---|---|
| Questão | Rascunho, ativa, arquivada. |
| Tentativa | Inicial ou revisão; correta ou incorreta; válida ou anulada quando a correção auditável existir. |
| Revisão | Futura, devida hoje, atrasada, concluída, cancelada por arquivamento ou substituída por reagendamento quando o recurso existir. |
| Ciclo | Não iniciado, em andamento, concluído, suspenso. |

“Ciclo concluído” não significa automaticamente “questão dominada”.

### 2.4 Critério de redação

Nos critérios de aceitação, “Dado/Quando/Então” indica um cenário funcional verificável. Casos adicionais serão detalhados no Plano de Testes.

---

## 3. Resumo por módulo

| Módulo | Requisitos | Horizonte predominante |
|---|---:|---|
| Espaço individual e configurações | `RF-001` a `RF-003` | MVP |
| Disciplinas, assuntos e subassuntos | `RF-004` a `RF-008` | MVP |
| Questões e origem | `RF-009` a `RF-020` | MVP e V1 |
| Tentativas | `RF-021` a `RF-027` | MVP e V1 |
| Erros | `RF-028` a `RF-033` | MVP e V1 |
| Revisões | `RF-034` a `RF-046` | MVP e V1 |
| Dashboard e estatísticas | `RF-047` a `RF-056` | MVP e V1 |
| Domínio e priorização | `RF-057` a `RF-062` | V1 |
| Pesquisa e filtros | `RF-063` a `RF-066` | MVP e V1 |
| Gestão e proteção funcional dos dados | `RF-067` a `RF-071` | MVP e V1 |

---

## 4. Espaço individual e configurações

### `RF-001` — Acessar o espaço individual

- **Descrição:** O sistema deverá disponibilizar ao estudante um espaço isolado para seus dados de estudo.
- **Ator:** Estudante.
- **Prioridade:** MVP — Essencial.
- **Pré-condições:** Aplicação inicializada; quando acessível por rede, identidade validada conforme RNFs e SDD.
- **Comportamento esperado:** Carregar somente disciplinas, questões, tentativas, revisões e indicadores pertencentes ao espaço atual.
- **Pós-condições:** O estudante acessa o painel e os módulos autorizados.
- **Exceções relevantes:** Espaço indisponível, sessão inválida ou dados não carregados deverão produzir erro compreensível sem exibir dados de outro espaço.
- **Critérios de aceitação:** (1) Dado um espaço válido, ao acessá-lo, somente seus registros são exibidos; (2) falha de carregamento não apresenta painel parcialmente atribuído a outro usuário; (3) o MVP funciona com um único estudante por espaço.

### `RF-002` — Configurar fuso horário

- **Descrição:** O estudante deverá poder informar o fuso usado para determinar “hoje”, vencimentos e datas de revisão.
- **Ator:** Estudante.
- **Prioridade:** MVP — Essencial.
- **Pré-condições:** Espaço individual acessível.
- **Comportamento esperado:** Exibir o fuso vigente, permitir seleção válida e usá-lo em novas classificações de data.
- **Pós-condições:** Operações posteriores utilizam o novo fuso.
- **Exceções relevantes:** Valor desconhecido ou inválido não poderá ser salvo.
- **Critérios de aceitação:** (1) O fuso salvo permanece entre sessões; (2) “devida hoje” segue o calendário do fuso configurado; (3) valor inválido é rejeitado com orientação.

### `RF-003` — Informar impacto da alteração de fuso

- **Descrição:** Antes de concluir uma alteração de fuso, o sistema deverá informar que a classificação entre futura, devida e atrasada poderá mudar.
- **Ator:** Estudante.
- **Prioridade:** MVP — Alta.
- **Pré-condições:** Existência de revisões e solicitação de mudança do fuso.
- **Comportamento esperado:** Mostrar confirmação e aplicar a política temporal definida nas regras de negócio sem reescrever datas históricas silenciosamente.
- **Pós-condições:** Mudança confirmada fica registrada; cancelamento mantém configuração anterior.
- **Exceções relevantes:** Se não houver revisões, a confirmação poderá ser simplificada.
- **Critérios de aceitação:** (1) A mudança não é aplicada antes da confirmação; (2) datas históricas realizadas permanecem identificáveis; (3) a lista de pendências é recalculada após a confirmação.

---

## 5. Disciplinas, assuntos e subassuntos

### `RF-004` — Gerenciar disciplinas

- **Descrição:** O estudante deverá criar, consultar e editar disciplinas usadas para organizar questões.
- **Ator:** Estudante.
- **Prioridade:** MVP — Essencial.
- **Pré-condições:** Espaço individual acessível.
- **Comportamento esperado:** Validar nome não vazio, impedir duplicidade exata ativa no mesmo espaço e apresentar a disciplina em seletores e filtros.
- **Pós-condições:** Disciplina fica disponível para vinculação.
- **Exceções relevantes:** Nome duplicado, vazio ou acima do limite definido deverá ser rejeitado.
- **Critérios de aceitação:** (1) Disciplina válida aparece nos seletores; (2) edição reflete nos locais vinculados sem recriar o histórico; (3) duplicidade exata é sinalizada.

### `RF-005` — Gerenciar assuntos

- **Descrição:** O estudante deverá criar, consultar e editar assuntos vinculados a uma disciplina.
- **Ator:** Estudante.
- **Prioridade:** MVP — Essencial.
- **Pré-condições:** Existência de disciplina ativa.
- **Comportamento esperado:** Exigir uma disciplina pai e impedir duplicidade exata de assunto dentro da mesma disciplina.
- **Pós-condições:** Assunto fica disponível sob sua disciplina.
- **Exceções relevantes:** Não permitir assunto órfão ou vínculo com disciplina arquivada sem tratamento explícito.
- **Critérios de aceitação:** (1) Assunto aparece apenas sob a disciplina correta; (2) duas disciplinas podem ter assuntos de mesmo nome; (3) assunto sem pai não é ativado.

### `RF-006` — Gerenciar subassuntos

- **Descrição:** O estudante deverá criar, consultar e editar subassuntos vinculados a um assunto.
- **Ator:** Estudante.
- **Prioridade:** MVP — Alta.
- **Pré-condições:** Existência de assunto ativo.
- **Comportamento esperado:** Exigir assunto pai, herdar o contexto da disciplina e permitir que questões omitam subassunto.
- **Pós-condições:** Subassunto fica disponível na seleção hierárquica.
- **Exceções relevantes:** Não permitir subassunto órfão ou associado diretamente a disciplina.
- **Critérios de aceitação:** (1) O subassunto aparece somente no assunto correto; (2) uma questão pode ser salva sem subassunto; (3) vínculo inválido é rejeitado.

### `RF-007` — Selecionar hierarquia de conteúdo

- **Descrição:** Formulários e filtros deverão apresentar a sequência disciplina → assunto → subassunto.
- **Ator:** Estudante.
- **Prioridade:** MVP — Essencial.
- **Pré-condições:** Existência dos níveis que serão selecionados.
- **Comportamento esperado:** Filtrar assuntos pela disciplina e subassuntos pelo assunto, limpando seleções incompatíveis quando um nível pai mudar.
- **Pós-condições:** O registro recebe uma combinação hierárquica válida.
- **Exceções relevantes:** Itens arquivados já vinculados poderão ser exibidos no histórico, mas não selecionados para novos registros.
- **Critérios de aceitação:** (1) Mudar a disciplina remove assunto incompatível; (2) não é possível salvar combinação cruzada; (3) histórico preserva o rótulo de item arquivado.

### `RF-008` — Arquivar elemento da hierarquia

- **Descrição:** O estudante deverá poder retirar disciplina, assunto ou subassunto de novos cadastros sem apagar registros antigos.
- **Ator:** Estudante.
- **Prioridade:** MVP — Alta.
- **Pré-condições:** Elemento existente.
- **Comportamento esperado:** Exibir quantidade de vínculos, solicitar confirmação e impedir novas seleções após arquivamento.
- **Pós-condições:** Elemento permanece consultável no histórico, mas deixa de ser oferecido em novos cadastros.
- **Exceções relevantes:** Arquivar pai com filhos ativos deverá exigir tratamento explícito conforme regras de negócio.
- **Critérios de aceitação:** (1) Nenhuma questão histórica é apagada; (2) item arquivado some dos seletores de novos registros; (3) o sistema não cria descendentes órfãos.

---

## 6. Questões e origem

### `RF-009` — Salvar questão como rascunho

- **Descrição:** O estudante deverá poder salvar uma questão incompleta para concluir depois.
- **Ator:** Estudante.
- **Prioridade:** MVP — Alta.
- **Pré-condições:** Espaço individual acessível.
- **Comportamento esperado:** Permitir dados parciais, identificar o registro como rascunho e não gerar tentativa, revisão ou estatística de questão realizada.
- **Pós-condições:** Rascunho fica recuperável na lista apropriada.
- **Exceções relevantes:** Deve existir ao menos um identificador mínimo, como trecho do enunciado ou título temporário.
- **Critérios de aceitação:** (1) Rascunho não aumenta questões realizadas; (2) não gera revisão; (3) pode ser retomado e ativado posteriormente.

### `RF-010` — Ativar questão objetiva

- **Descrição:** O estudante deverá transformar um rascunho ou novo registro em questão ativa apta a receber tentativas.
- **Ator:** Estudante.
- **Prioridade:** MVP — Essencial.
- **Pré-condições:** Disciplina e assunto ativos; enunciado; alternativas válidas; resposta correta definida.
- **Comportamento esperado:** Validar os campos mínimos e alterar o estado para ativa.
- **Pós-condições:** Questão pode receber tentativa inicial e aparecer em busca/listagem ativa.
- **Exceções relevantes:** Subassunto, fonte, banca, prova, ano, dificuldade, pegadinha e observações poderão ser opcionais.
- **Critérios de aceitação:** (1) Questão sem enunciado, disciplina, assunto ou resposta correta não é ativada; (2) subassunto pode ser omitido; (3) ativação não cria tentativa automaticamente.

### `RF-011` — Registrar alternativas e resposta correta

- **Descrição:** O sistema deverá permitir duas ou mais alternativas textuais e exatamente uma correta no MVP.
- **Ator:** Estudante.
- **Prioridade:** MVP — Essencial.
- **Pré-condições:** Criação ou edição de questão objetiva.
- **Comportamento esperado:** Permitir ordenar alternativas, marcar uma correta e impedir ativação com alternativas vazias ou duplicadas de modo indistinguível.
- **Pós-condições:** Gabarito fica disponível para avaliação, protegido durante a resposta.
- **Exceções relevantes:** Certo/errado utiliza duas alternativas; múltiplas respostas corretas não são suportadas no MVP.
- **Critérios de aceitação:** (1) Zero ou duas respostas corretas impedem ativação; (2) duas alternativas válidas suportam certo/errado; (3) a ordem é preservada.

### `RF-012` — Registrar origem da questão

- **Descrição:** O estudante deverá poder informar fonte, banca, prova/concurso, ano e referência textual quando aplicáveis.
- **Ator:** Estudante.
- **Prioridade:** MVP — Alta.
- **Pré-condições:** Questão em criação ou edição.
- **Comportamento esperado:** Aceitar campos opcionais e exibi-los no detalhe da questão.
- **Pós-condições:** Origem fica associada à questão e disponível para futuras análises.
- **Exceções relevantes:** Ausência de banca ou prova não impede ativação; ano inválido deve ser rejeitado.
- **Critérios de aceitação:** (1) Questão sem banca pode ser ativada; (2) dados informados aparecem no detalhe; (3) alterar origem não altera tentativas.

### `RF-013` — Registrar dificuldade da questão

- **Descrição:** O estudante poderá classificar a dificuldade como fácil, média ou difícil.
- **Ator:** Estudante.
- **Prioridade:** MVP — Alta.
- **Pré-condições:** Questão existente.
- **Comportamento esperado:** Permitir valor opcional de lista controlada e exibi-lo no detalhe e filtros futuros.
- **Pós-condições:** Dificuldade fica associada à questão, não a uma tentativa específica.
- **Exceções relevantes:** Ausência de avaliação não bloqueia cadastro; valores livres não são aceitos no MVP.
- **Critérios de aceitação:** (1) Somente três valores válidos são salvos; (2) campo pode ficar vazio; (3) edição não altera resultados anteriores.

### `RF-014` — Realizar cadastro rápido

- **Descrição:** O sistema deverá permitir registrar os dados essenciais sem exigir todos os metadados opcionais.
- **Ator:** Estudante.
- **Prioridade:** MVP — Essencial.
- **Pré-condições:** Disciplina e assunto disponíveis.
- **Comportamento esperado:** Priorizar enunciado, alternativas, resposta correta e contexto mínimo; permitir completar origem, dificuldade, explicação, pegadinha e observações depois.
- **Pós-condições:** Questão ativa ou rascunho é criado conforme os dados fornecidos.
- **Exceções relevantes:** Um registro incompleto para ativação deverá ser salvo como rascunho, nunca como questão ativa inválida.
- **Critérios de aceitação:** (1) Campos opcionais não bloqueiam ativação; (2) campos essenciais ausentes produzem rascunho ou validação clara; (3) o usuário não perde o que digitou após erro corrigível.

### `RF-015` — Enriquecer questão posteriormente

- **Descrição:** O estudante deverá adicionar ou atualizar explicação/regra, pegadinha, dificuldade, observações e origem após o cadastro.
- **Ator:** Estudante.
- **Prioridade:** MVP — Alta.
- **Pré-condições:** Questão existente.
- **Comportamento esperado:** Salvar os novos dados sem criar tentativa e registrar data de atualização.
- **Pós-condições:** Conteúdo enriquecido aparece no detalhe e nas revisões posteriores.
- **Exceções relevantes:** Alterar gabarito ou alternativas após tentativas segue `RF-018`.
- **Critérios de aceitação:** (1) Complementar explicação não altera contagens; (2) a nova versão aparece na próxima revisão; (3) tentativa não é criada pela edição.

### `RF-016` — Visualizar detalhe da questão

- **Descrição:** O estudante deverá consultar conteúdo, contexto, estado, ciclo e acesso ao histórico da questão.
- **Ator:** Estudante.
- **Prioridade:** MVP — Essencial.
- **Pré-condições:** Questão existente.
- **Comportamento esperado:** Exibir dados atuais e separar claramente conteúdo da questão, tentativa inicial, revisões e indicadores.
- **Pós-condições:** Nenhum dado é alterado pela consulta.
- **Exceções relevantes:** Questão arquivada deverá ser identificada; dados opcionais ausentes não devem gerar valores fictícios.
- **Critérios de aceitação:** (1) Questão e tentativas aparecem em seções distintas; (2) estado atual é visível; (3) campos ausentes são tratados como não informados.

### `RF-017` — Editar metadados e conteúdo não crítico

- **Descrição:** O estudante deverá corrigir enunciado, origem, dificuldade, explicação, pegadinha e observações.
- **Ator:** Estudante.
- **Prioridade:** MVP — Alta.
- **Pré-condições:** Questão existente e não bloqueada por operação concorrente.
- **Comportamento esperado:** Validar a edição, registrar atualização e preservar tentativas.
- **Pós-condições:** Versão atual da questão passa a ser exibida.
- **Exceções relevantes:** Mudança de disciplina/assunto exige hierarquia válida; mudanças críticas de gabarito seguem `RF-018`.
- **Critérios de aceitação:** (1) Histórico de tentativas permanece; (2) vínculo hierárquico inválido é rejeitado; (3) dashboard é atualizado quando o agrupamento muda.

### `RF-018` — Controlar alteração de alternativas ou gabarito

- **Descrição:** O sistema deverá impedir que uma alteração crítica torne resultados anteriores silenciosamente incorretos.
- **Ator:** Estudante e Sistema.
- **Prioridade:** MVP — Essencial.
- **Pré-condições:** Questão ativa; tentativa existente ou inexistente.
- **Comportamento esperado:** Sem tentativas, permitir edição validada; com tentativas, bloquear a alteração no MVP e orientar o fluxo de correção auditável da V1.
- **Pós-condições:** Resultados históricos não são reinterpretados sem decisão explícita.
- **Exceções relevantes:** Correção ortográfica que não muda o significado pode seguir edição comum.
- **Critérios de aceitação:** (1) Gabarito pode mudar antes da primeira tentativa; (2) após tentativa válida, mudança crítica é bloqueada no MVP; (3) o bloqueio explica o impacto.

### `RF-019` — Arquivar questão

- **Descrição:** O estudante deverá retirar uma questão do uso ativo sem apagar seu histórico.
- **Ator:** Estudante.
- **Prioridade:** MVP — Alta.
- **Pré-condições:** Questão existente.
- **Comportamento esperado:** Exibir revisões pendentes afetadas, solicitar confirmação, arquivar e suspender o ciclo.
- **Pós-condições:** Questão permanece consultável; não aparece em cadastros ativos nem na fila normal de revisão.
- **Exceções relevantes:** Arquivamento durante revisão iniciada deverá ser impedido até concluir ou abandonar com segurança.
- **Critérios de aceitação:** (1) Tentativas continuam acessíveis; (2) pendências deixam a fila ativa; (3) totais históricos não são apagados.

### `RF-020` — Excluir questão com análise de impacto

- **Descrição:** Na V1, o estudante deverá solicitar exclusão e compreender todos os registros afetados.
- **Ator:** Estudante.
- **Prioridade:** V1 — Alta.
- **Pré-condições:** Questão existente; política de exclusão aprovada.
- **Comportamento esperado:** Informar quantidade de tentativas, revisões e métricas afetadas, exigir confirmação reforçada e aplicar exclusão ou retenção conforme regras.
- **Pós-condições:** Dados e indicadores refletem a política aprovada.
- **Exceções relevantes:** Exclusão poderá ser bloqueada e substituída por arquivamento quando a integridade exigir.
- **Critérios de aceitação:** (1) Nenhuma exclusão ocorre sem confirmação; (2) impacto é informado antes; (3) recálculo não deixa referências órfãs.

---

## 7. Tentativas

### `RF-021` — Registrar tentativa inicial

- **Descrição:** O estudante deverá registrar a primeira resolução de uma questão ativa.
- **Ator:** Estudante.
- **Prioridade:** MVP — Essencial.
- **Pré-condições:** Questão ativa; nenhuma tentativa inicial válida existente.
- **Comportamento esperado:** Solicitar resposta dada, registrar data/hora, comparar com o gabarito e criar uma tentativa do tipo inicial.
- **Pós-condições:** Questão passa a ser considerada realizada; dashboard é atualizado.
- **Exceções relevantes:** Não permitir duas tentativas iniciais válidas para a mesma questão.
- **Critérios de aceitação:** (1) A tentativa possui identidade própria; (2) nova tentativa inicial duplicada é rejeitada; (3) a questão não é sobrescrita.

### `RF-022` — Determinar resultado objetivo

- **Descrição:** O sistema deverá calcular correto/incorreto comparando a alternativa dada com a alternativa correta.
- **Ator:** Sistema.
- **Prioridade:** MVP — Essencial.
- **Pré-condições:** Questão objetiva válida e resposta dada.
- **Comportamento esperado:** Aplicar comparação determinística e mostrar o resultado antes da confirmação final quando apropriado.
- **Pós-condições:** Resultado é armazenado na tentativa.
- **Exceções relevantes:** Questão com gabarito inconsistente deverá bloquear a tentativa e solicitar correção da questão.
- **Critérios de aceitação:** (1) Alternativa igual ao gabarito resulta em acerto; (2) alternativa diferente resulta em erro; (3) resultado não pode ser digitado arbitrariamente.

### `RF-023` — Registrar tentativa inicial correta

- **Descrição:** Uma resolução correta deverá compor o histórico e as estatísticas, sem iniciar automaticamente revisão no MVP.
- **Ator:** Estudante e Sistema.
- **Prioridade:** MVP — Essencial.
- **Pré-condições:** `RF-021` concluído com acerto.
- **Comportamento esperado:** Salvar tentativa, atualizar métricas e manter ciclo como não iniciado.
- **Pós-condições:** Questão realizada e sem revisão automática.
- **Exceções relevantes:** Inclusão manual em revisão somente será permitida pela capacidade V1 `RF-044`.
- **Critérios de aceitação:** (1) Acerto entra nas estatísticas; (2) nenhuma revisão automática é criada; (3) estado não é apresentado como dominado.

### `RF-024` — Registrar tentativa inicial incorreta

- **Descrição:** Uma resolução incorreta deverá exigir diagnóstico mínimo e iniciar o ciclo de revisão.
- **Ator:** Estudante e Sistema.
- **Prioridade:** MVP — Essencial.
- **Pré-condições:** `RF-021` concluído com erro.
- **Comportamento esperado:** Solicitar classificação principal do erro, permitir aprendizado complementar e, após confirmação, acionar `RF-034`.
- **Pós-condições:** Tentativa incorreta registrada e ciclo iniciado.
- **Exceções relevantes:** Se a classificação não for informada, o sistema deverá manter a tentativa pendente de finalização ou solicitar “outra” com descrição; não deverá fingir conclusão.
- **Critérios de aceitação:** (1) Erro finalizado possui classificação; (2) gera ciclo uma única vez; (3) explicação e pegadinha podem ser enriquecidas depois.

### `RF-025` — Registrar tentativa de revisão

- **Descrição:** Cada revisão respondida deverá produzir uma tentativa do tipo revisão.
- **Ator:** Estudante e Sistema.
- **Prioridade:** MVP — Essencial.
- **Pré-condições:** Revisão válida iniciada.
- **Comportamento esperado:** Registrar resposta, resultado, data/hora real, revisão de origem e classificação se houver novo erro.
- **Pós-condições:** Histórico e ciclo são atualizados.
- **Exceções relevantes:** Atualização da página ou envio repetido não poderá criar duplicidade.
- **Critérios de aceitação:** (1) A tentativa referencia a revisão; (2) é distinguível da inicial; (3) uma revisão concluída possui exatamente uma tentativa válida.

### `RF-026` — Consultar linha do tempo de tentativas

- **Descrição:** O estudante deverá visualizar todas as tentativas de uma questão em ordem temporal.
- **Ator:** Estudante.
- **Prioridade:** MVP — Essencial.
- **Pré-condições:** Questão com ao menos uma tentativa.
- **Comportamento esperado:** Exibir tipo, data, resposta, resultado, erro e revisão relacionada sem misturar dados atuais da questão com o evento histórico.
- **Pós-condições:** Consulta não altera registros.
- **Exceções relevantes:** Tentativa anulada na V1 deverá continuar identificável conforme política de auditoria.
- **Critérios de aceitação:** (1) Ordem temporal é consistente; (2) tentativa inicial é identificada; (3) revisões mostram data prevista e realizada quando aplicável.

### `RF-027` — Corrigir tentativa por anulação e substituição

- **Descrição:** Na V1, uma tentativa finalizada com erro de lançamento deverá ser corrigida sem reescrever silenciosamente o evento original.
- **Ator:** Estudante.
- **Prioridade:** V1 — Alta.
- **Pré-condições:** Tentativa válida; motivo informado; política aprovada.
- **Comportamento esperado:** Anular a tentativa, criar substituta quando necessário, registrar motivo e recalcular efeitos.
- **Pós-condições:** Histórico mostra correção; métricas usam apenas registros válidos.
- **Exceções relevantes:** Correção que altere o ciclo deverá aplicar regra de reconstrução definida na Etapa 5.
- **Critérios de aceitação:** (1) Original não desaparece; (2) substituta referencia a anulada; (3) métricas não contam ambas como válidas.

---

## 8. Erros

### `RF-028` — Classificar erro principal

- **Descrição:** Cada tentativa incorreta finalizada deverá possuir exatamente uma classificação principal no MVP.
- **Ator:** Estudante.
- **Prioridade:** MVP — Essencial.
- **Pré-condições:** Resultado incorreto determinado.
- **Comportamento esperado:** Exibir categorias ativas com definições curtas e exigir seleção.
- **Pós-condições:** Classificação fica vinculada à tentativa, não à questão inteira.
- **Exceções relevantes:** Se o motivo ainda não for conhecido, usar “outra” com descrição, evitando categoria fictícia.
- **Critérios de aceitação:** (1) Erro não é finalizado sem categoria; (2) acerto não exige categoria; (3) revisões diferentes podem ter categorias diferentes.

### `RF-029` — Disponibilizar categorias padrão

- **Descrição:** O sistema deverá fornecer as categorias conceitual, interpretação, cálculo, atenção, fórmula/regra, procedimento, pegadinha, falta de tempo, chute e outra.
- **Ator:** Sistema.
- **Prioridade:** MVP — Essencial.
- **Pré-condições:** Espaço inicializado.
- **Comportamento esperado:** Manter códigos estáveis e nomes/descrições apresentáveis ao estudante.
- **Pós-condições:** Categorias podem ser usadas em registros e estatísticas.
- **Exceções relevantes:** Renomeação visual futura não deverá quebrar agregações históricas.
- **Critérios de aceitação:** (1) As dez categorias estão disponíveis; (2) cada uma tem explicação; (3) códigos não dependem do texto exibido.

### `RF-030` — Descrever categoria “outra”

- **Descrição:** Ao escolher “outra”, o estudante deverá informar uma descrição curta do motivo.
- **Ator:** Estudante.
- **Prioridade:** MVP — Alta.
- **Pré-condições:** Tentativa incorreta; categoria “outra” selecionada.
- **Comportamento esperado:** Exigir texto não vazio e preservá-lo junto à classificação.
- **Pós-condições:** O erro permanece analisável sem forçar categoria inadequada.
- **Exceções relevantes:** Texto composto apenas por espaços ou acima do limite deverá ser rejeitado.
- **Critérios de aceitação:** (1) “Outra” sem descrição não finaliza; (2) descrição aparece no histórico; (3) estatística agrega em “outra” sem perder o detalhe.

### `RF-031` — Editar diagnóstico do erro

- **Descrição:** O estudante deverá corrigir classificação ou descrição do erro sem mudar a resposta e o resultado da tentativa.
- **Ator:** Estudante.
- **Prioridade:** MVP — Alta.
- **Pré-condições:** Tentativa incorreta existente.
- **Comportamento esperado:** Validar a nova classificação, registrar atualização e recalcular estatísticas de erro.
- **Pós-condições:** Diagnóstico atual é usado nos relatórios; tentativa permanece a mesma.
- **Exceções relevantes:** Alteração de resultado exige `RF-027`, não esta função.
- **Critérios de aceitação:** (1) Resultado não pode ser alterado por esse fluxo; (2) frequência por categoria é atualizada; (3) data de atualização fica disponível para auditoria futura.

### `RF-032` — Consultar erros por categoria e conteúdo

- **Descrição:** O estudante deverá acessar os registros que compõem uma contagem de erros.
- **Ator:** Estudante.
- **Prioridade:** MVP — Alta.
- **Pré-condições:** Existência de tentativas incorretas.
- **Comportamento esperado:** Permitir partir de uma categoria ou agrupamento acadêmico para a lista de tentativas correspondentes.
- **Pós-condições:** Consulta não altera dados.
- **Exceções relevantes:** Filtros sem resultados deverão mostrar estado vazio explicativo.
- **Critérios de aceitação:** (1) Total exibido corresponde à lista; (2) tentativas anuladas não entram como válidas; (3) o usuário chega ao detalhe da questão.

### `RF-033` — Gerenciar categorias pessoais

- **Descrição:** Na V1, o estudante poderá criar, renomear, desativar e consolidar categorias pessoais sem alterar as categorias padrão.
- **Ator:** Estudante.
- **Prioridade:** V1 — Média.
- **Pré-condições:** Espaço acessível; regras de consolidação aprovadas.
- **Comportamento esperado:** Validar duplicidades, preservar códigos, impedir exclusão destrutiva e diferenciar categorias pessoais nas estatísticas.
- **Pós-condições:** Categorias ativas ficam disponíveis para novos erros.
- **Exceções relevantes:** Categoria vinculada deverá ser desativada ou consolidada, não apagada sem tratamento.
- **Critérios de aceitação:** (1) Histórico mantém categoria desativada; (2) nova categoria aparece no seletor; (3) consolidação não duplica contagens.

---

## 9. Revisões

### `RF-034` — Iniciar ciclo automático após erro inicial

- **Descrição:** O sistema deverá iniciar um ciclo fixo de revisão quando uma tentativa inicial incorreta for finalizada.
- **Ator:** Sistema.
- **Prioridade:** MVP — Essencial.
- **Pré-condições:** Tentativa inicial incorreta válida, classificada e sem ciclo existente.
- **Comportamento esperado:** Registrar o plano de 1, 7, 14 e 30 dias e definir a primeira revisão conforme a regra temporal.
- **Pós-condições:** Questão passa a “em revisão”; primeira pendência fica programada.
- **Exceções relevantes:** Reenvio da mesma operação não poderá criar segundo ciclo.
- **Critérios de aceitação:** (1) Erro inicial cria um ciclo; (2) acerto inicial não cria; (3) duplicidade de ciclo é impedida.

### `RF-035` — Calcular data de revisão

- **Descrição:** O sistema deverá calcular a data prevista de cada etapa usando data-base, intervalo e fuso configurado.
- **Ator:** Sistema.
- **Prioridade:** MVP — Essencial.
- **Pré-condições:** Ciclo ou etapa anterior válida.
- **Comportamento esperado:** Aplicar regra determinística e armazenar dados suficientes para explicar o cálculo.
- **Pós-condições:** Revisão possui data prevista.
- **Exceções relevantes:** Mudança de fuso, horário de verão e atraso deverão seguir regras da Etapa 5.
- **Critérios de aceitação:** (1) Mesmo dado produz mesma data; (2) intervalo aplicado é identificável; (3) data inválida não é criada silenciosamente.

### `RF-036` — Classificar situação temporal da revisão

- **Descrição:** O sistema deverá classificar revisão como futura, devida hoje, atrasada ou concluída.
- **Ator:** Sistema.
- **Prioridade:** MVP — Essencial.
- **Pré-condições:** Revisão com data prevista e fuso válido.
- **Comportamento esperado:** Comparar a data prevista com a data local atual sem alterar a data original.
- **Pós-condições:** Situação correta fica disponível para listas e dashboard.
- **Exceções relevantes:** Revisão cancelada por arquivamento não deverá aparecer como atraso ativo.
- **Critérios de aceitação:** (1) Data igual a hoje resulta em “devida hoje”; (2) anterior não concluída resulta em “atrasada”; (3) conclusão remove da fila pendente.

### `RF-037` — Listar revisões devidas hoje

- **Descrição:** O estudante deverá visualizar revisões cuja data prevista coincide com a data local atual.
- **Ator:** Estudante.
- **Prioridade:** MVP — Essencial.
- **Pré-condições:** Fuso configurado; revisões devidas existentes ou não.
- **Comportamento esperado:** Ordenar de modo previsível e permitir abrir cada questão.
- **Pós-condições:** Consulta não altera a situação.
- **Exceções relevantes:** Lista vazia deverá informar que não há revisões devidas.
- **Critérios de aceitação:** (1) Apenas revisões ativas de hoje aparecem; (2) concluir remove o item; (3) total coincide com o dashboard.

### `RF-038` — Listar revisões atrasadas

- **Descrição:** O estudante deverá visualizar separadamente revisões vencidas e não concluídas.
- **Ator:** Estudante.
- **Prioridade:** MVP — Essencial.
- **Pré-condições:** Existência de revisão anterior a hoje não concluída.
- **Comportamento esperado:** Mostrar data originalmente prevista e tempo de atraso sem reagendar automaticamente.
- **Pós-condições:** Estudante pode iniciar a revisão atrasada.
- **Exceções relevantes:** Itens suspensos ou cancelados não entram na lista ativa.
- **Critérios de aceitação:** (1) Data original permanece visível; (2) item não é movido para hoje apenas por abrir a lista; (3) conclusão registra a data real.

### `RF-039` — Listar próximas revisões

- **Descrição:** O estudante deverá consultar revisões futuras.
- **Ator:** Estudante.
- **Prioridade:** MVP — Alta.
- **Pré-condições:** Revisões futuras existentes.
- **Comportamento esperado:** Ordenar por data e mostrar etapa e contexto da questão.
- **Pós-condições:** Nenhum agendamento é alterado.
- **Exceções relevantes:** Revisões concluídas ou suspensas não aparecem como futuras ativas.
- **Critérios de aceitação:** (1) Datas futuras estão em ordem; (2) a etapa é identificável; (3) abrir detalhe não conclui revisão.

### `RF-040` — Iniciar revisão protegendo o gabarito

- **Descrição:** Ao iniciar uma revisão, o sistema deverá apresentar a questão sem revelar previamente a resposta correta, explicação ou pegadinha.
- **Ator:** Estudante e Sistema.
- **Prioridade:** MVP — Essencial.
- **Pré-condições:** Revisão ativa e questão não arquivada.
- **Comportamento esperado:** Mostrar enunciado e alternativas, aceitar seleção e impedir exposição acidental do gabarito.
- **Pós-condições:** Revisão fica em andamento até envio ou abandono seguro.
- **Exceções relevantes:** Se o conteúdo estiver inválido, bloquear conclusão e orientar correção.
- **Critérios de aceitação:** (1) Gabarito não aparece antes do envio; (2) alternativas são apresentadas; (3) abrir a revisão não cria tentativa.

### `RF-041` — Submeter resposta e apresentar correção

- **Descrição:** Após o estudante enviar sua resposta, o sistema deverá calcular o resultado e revelar gabarito e aprendizado registrado.
- **Ator:** Estudante e Sistema.
- **Prioridade:** MVP — Essencial.
- **Pré-condições:** Revisão iniciada; alternativa selecionada.
- **Comportamento esperado:** Bloquear alteração silenciosa da resposta enviada, mostrar correto/incorreto, resposta correta, explicação/regra e pegadinha quando existentes.
- **Pós-condições:** Resultado aguarda os dados complementares necessários à finalização.
- **Exceções relevantes:** Envio sem resposta deverá ser rejeitado; ausência de explicação deverá ser indicada como não informada.
- **Critérios de aceitação:** (1) Resultado corresponde ao gabarito; (2) resposta correta aparece após envio; (3) erro exige classificação antes da conclusão.

### `RF-042` — Registrar facilidade percebida

- **Descrição:** O estudante poderá avaliar a revisão como fácil, média ou difícil.
- **Ator:** Estudante.
- **Prioridade:** MVP — Alta.
- **Pré-condições:** Resposta de revisão submetida.
- **Comportamento esperado:** Oferecer escala opcional controlada e registrar o valor na tentativa.
- **Pós-condições:** Dado fica disponível para análise futura.
- **Exceções relevantes:** No MVP, a avaliação não altera o calendário; ausência não bloqueia conclusão.
- **Critérios de aceitação:** (1) Somente três valores são aceitos; (2) campo pode ser omitido; (3) data seguinte é igual com ou sem avaliação no MVP.

### `RF-043` — Concluir revisão exatamente uma vez

- **Descrição:** A conclusão deverá gerar uma tentativa válida e impedir duplicidade causada por cliques ou reenvios.
- **Ator:** Estudante e Sistema.
- **Prioridade:** MVP — Essencial.
- **Pré-condições:** Resposta submetida; classificação preenchida quando incorreta.
- **Comportamento esperado:** Salvar tentativa e conclusão como uma operação lógica única.
- **Pós-condições:** Revisão concluída, tentativa vinculada e fila atualizada.
- **Exceções relevantes:** Falha parcial não poderá deixar revisão concluída sem tentativa nem criar duas tentativas.
- **Critérios de aceitação:** (1) Reenvio não duplica; (2) revisão concluída tem exatamente uma tentativa; (3) falha mantém estado recuperável.

### `RF-044` — Atualizar etapa seguinte do ciclo

- **Descrição:** Após concluir a revisão, o sistema deverá aplicar a regra vigente para avançar, retornar, reiniciar ou concluir o ciclo.
- **Ator:** Sistema.
- **Prioridade:** MVP — Essencial.
- **Pré-condições:** `RF-043` concluído.
- **Comportamento esperado:** Considerar resultado e demais fatores autorizados, registrar regra aplicada e produzir o próximo estado.
- **Pós-condições:** Próxima revisão programada ou ciclo concluído.
- **Exceções relevantes:** A fórmula exata será definida na Etapa 5; nenhuma decisão poderá depender de IA no MVP.
- **Critérios de aceitação:** (1) Regra aplicada é identificável; (2) resultado não deixa ciclo em estado impossível; (3) repetição da operação não cria nova etapa.

### `RF-045` — Incluir manualmente questão correta em revisão

- **Descrição:** Na V1, o estudante deverá poder iniciar ciclo para uma questão inicialmente correta que considere insegura ou importante.
- **Ator:** Estudante.
- **Prioridade:** V1 — Alta.
- **Pré-condições:** Questão ativa com tentativa inicial correta e sem ciclo ativo.
- **Comportamento esperado:** Solicitar confirmação e motivo opcional, criar ciclo conforme modelo vigente e distinguir origem manual.
- **Pós-condições:** Questão passa a “em revisão”.
- **Exceções relevantes:** Não permitir segundo ciclo ativo para a mesma questão.
- **Critérios de aceitação:** (1) Origem manual é visível; (2) ciclo não altera o resultado inicial; (3) duplicidade é bloqueada.

### `RF-046` — Reagendar revisão de forma controlada

- **Descrição:** Na V1, o estudante deverá reagendar uma revisão preservando a data anterior e o motivo.
- **Ator:** Estudante.
- **Prioridade:** V1 — Alta.
- **Pré-condições:** Revisão ativa não concluída.
- **Comportamento esperado:** Exibir impacto, exigir nova data válida, registrar motivo e manter histórico do agendamento original.
- **Pós-condições:** Nova pendência substitui operacionalmente a anterior sem apagar o atraso ou a data original.
- **Exceções relevantes:** Limites e condições serão definidos na Etapa 5; reagendamento retroativo inválido é rejeitado.
- **Critérios de aceitação:** (1) Data original continua consultável; (2) motivo fica registrado; (3) dashboard não conta simultaneamente as duas como pendências independentes.

---

## 10. Dashboard e estatísticas

### `RF-047` — Exibir resumo do dashboard

- **Descrição:** O sistema deverá apresentar um painel inicial com atividade, desempenho e situação das revisões.
- **Ator:** Estudante.
- **Prioridade:** MVP — Essencial.
- **Pré-condições:** Espaço acessível; dados podem existir ou não.
- **Comportamento esperado:** Exibir cartões e agrupamentos básicos sem misturar questões, tentativas e revisões.
- **Pós-condições:** O estudante identifica a situação atual e acessa os detalhes.
- **Exceções relevantes:** Espaço vazio deverá mostrar orientação inicial, não divisões por zero.
- **Critérios de aceitação:** (1) Dashboard abre sem dados; (2) conceitos são rotulados distintamente; (3) indicadores conduzem ao conjunto correspondente quando houver detalhamento.

### `RF-048` — Contabilizar questões e tentativas separadamente

- **Descrição:** O sistema deverá informar questões cadastradas, questões realizadas e tentativas como contagens distintas.
- **Ator:** Sistema.
- **Prioridade:** MVP — Essencial.
- **Pré-condições:** Dados existentes ou conjunto vazio.
- **Comportamento esperado:** Excluir rascunhos de “realizadas”, contar uma questão uma única vez nesse indicador e contar cada tentativa válida no indicador próprio.
- **Pós-condições:** Totais ficam disponíveis ao dashboard.
- **Exceções relevantes:** Questões arquivadas podem integrar histórico, desde que o período e o critério sejam informados.
- **Critérios de aceitação:** (1) Três revisões da mesma questão aumentam tentativas, não questões realizadas; (2) rascunho não aumenta realizadas; (3) definição é consultável.

### `RF-049` — Calcular acertos, erros e taxa de acerto

- **Descrição:** O sistema deverá calcular contagens e taxa usando tentativas válidas no período e contexto exibidos.
- **Ator:** Sistema.
- **Prioridade:** MVP — Essencial.
- **Pré-condições:** Tentativas existentes ou conjunto vazio.
- **Comportamento esperado:** Somar resultados, mostrar numerador/denominador e permitir distinguir tentativas iniciais de revisões.
- **Pós-condições:** Métricas coerentes ficam disponíveis.
- **Exceções relevantes:** Sem tentativas, taxa deve ser “sem dados”, não 0% enganoso.
- **Critérios de aceitação:** (1) Acertos + erros = tentativas válidas consideradas; (2) denominador é visível; (3) tentativas anuladas na V1 não entram.

### `RF-050` — Exibir atividade de hoje

- **Descrição:** O dashboard deverá mostrar questões/tentativas e revisões realizadas na data local atual.
- **Ator:** Estudante e Sistema.
- **Prioridade:** MVP — Alta.
- **Pré-condições:** Fuso configurado.
- **Comportamento esperado:** Agrupar eventos pela data real, separar revisão de tentativa inicial e atualizar após novas ações.
- **Pós-condições:** Atividade diária fica visível.
- **Exceções relevantes:** Mudança de fuso aplica a política aprovada sem reescrever instante histórico.
- **Critérios de aceitação:** (1) Eventos de hoje entram; (2) anteriores não entram; (3) total é atualizado após conclusão.

### `RF-051` — Exibir carga de revisões

- **Descrição:** O dashboard deverá mostrar devidas hoje, atrasadas e próximas revisões.
- **Ator:** Estudante e Sistema.
- **Prioridade:** MVP — Essencial.
- **Pré-condições:** Ciclos existentes ou não.
- **Comportamento esperado:** Reutilizar a mesma classificação temporal das listas e oferecer acesso às pendências.
- **Pós-condições:** Contagens coincidem com suas listas.
- **Exceções relevantes:** Revisões suspensas, canceladas ou concluídas não contam como pendentes.
- **Critérios de aceitação:** (1) Total de “hoje” coincide com `RF-037`; (2) atrasadas coincidem com `RF-038`; (3) concluir atualiza ambos.

### `RF-052` — Exibir situação das questões no ciclo

- **Descrição:** O sistema deverá contabilizar questões sem ciclo, em revisão, com ciclo concluído e arquivadas.
- **Ator:** Sistema.
- **Prioridade:** MVP — Alta.
- **Pré-condições:** Questões existentes ou não.
- **Comportamento esperado:** Aplicar estados mutuamente compreensíveis e não chamar ciclo concluído de domínio.
- **Pós-condições:** Distribuição é apresentada no painel.
- **Exceções relevantes:** Questão arquivada com ciclo suspenso deverá aparecer como arquivada, com histórico preservado.
- **Critérios de aceitação:** (1) Uma questão não é contada simultaneamente em estados incompatíveis; (2) soma pode ser reconciliada; (3) rótulo “dominada” não aparece no MVP.

### `RF-053` — Exibir desempenho por disciplina e assunto

- **Descrição:** O sistema deverá agrupar tentativas válidas por disciplina e assunto.
- **Ator:** Estudante e Sistema.
- **Prioridade:** MVP — Alta.
- **Pré-condições:** Questões realizadas e classificadas na hierarquia.
- **Comportamento esperado:** Mostrar volume, acertos, erros e taxa, distinguindo amostra ausente de desempenho baixo.
- **Pós-condições:** O estudante pode abrir o grupo analisado.
- **Exceções relevantes:** Mudança de classificação da questão exige recálculo; grupos sem tentativas não recebem taxa.
- **Critérios de aceitação:** (1) Totais do grupo correspondem às tentativas listadas; (2) denominador é visível; (3) sem dados não é mostrado como 0%.

### `RF-054` — Exibir frequência de tipos de erro

- **Descrição:** O sistema deverá ordenar ou apresentar categorias de erro pela quantidade de tentativas incorretas válidas.
- **Ator:** Estudante e Sistema.
- **Prioridade:** MVP — Alta.
- **Pré-condições:** Erros classificados.
- **Comportamento esperado:** Contar por classificação da tentativa, mostrar quantidade e permitir acesso aos registros.
- **Pós-condições:** Padrões de erro ficam visíveis.
- **Exceções relevantes:** Alteração de classificação atualiza os agrupamentos; “outra” preserva descrições individuais.
- **Critérios de aceitação:** (1) Cada tentativa incorreta entra em uma categoria principal; (2) total por categorias corresponde aos erros válidos; (3) detalhe é acessível.

### `RF-055` — Explicar métricas

- **Descrição:** Cada métrica importante deverá possuir definição acessível, período, população considerada e principais exclusões.
- **Ator:** Estudante e Sistema.
- **Prioridade:** MVP — Essencial.
- **Pré-condições:** Métrica exibida.
- **Comportamento esperado:** Fornecer ajuda ou detalhamento próximo ao indicador e, quando aplicável, lista de registros de origem.
- **Pós-condições:** Usuário consegue compreender o significado da métrica.
- **Exceções relevantes:** Nenhuma métrica calculada deverá aparecer sem definição documentada.
- **Critérios de aceitação:** (1) Taxa informa denominador; (2) período é visível; (3) “sem dados” é diferente de zero.

### `RF-056` — Atualizar estatísticas após mudanças

- **Descrição:** Operações que afetam os dados deverão refletir no dashboard sem produzir números contraditórios.
- **Ator:** Sistema.
- **Prioridade:** MVP — Essencial.
- **Pré-condições:** Criação, edição, arquivamento, tentativa ou revisão concluída.
- **Comportamento esperado:** Recalcular ou invalidar agregados afetados e apresentar estado atualizado após sucesso.
- **Pós-condições:** Métricas correspondem aos registros válidos.
- **Exceções relevantes:** Falha de recálculo deverá ser detectável e não confirmar silenciosamente valor antigo como atual.
- **Critérios de aceitação:** (1) Nova tentativa altera os totais; (2) edição de hierarquia move o agrupamento; (3) atualização da interface não duplica dados.

---

## 11. Domínio e priorização — V1

### `RF-057` — Calcular Índice de Domínio multifatorial

- **Descrição:** Na V1, o sistema deverá calcular domínio usando a fórmula aprovada, sem reduzi-lo à taxa simples de acerto.
- **Ator:** Sistema.
- **Prioridade:** V1 — Alta.
- **Pré-condições:** Fórmula e dados elegíveis definidos na Etapa 5.
- **Comportamento esperado:** Considerar somente fatores autorizados, armazenar versão do cálculo e retornar valor ou “dados insuficientes”.
- **Pós-condições:** Índice fica disponível nos níveis previstos.
- **Exceções relevantes:** Ausência de evidência suficiente não gera pontuação artificial.
- **Critérios de aceitação:** (1) Mesmos dados e versão produzem mesmo valor; (2) fórmula simples de acertos não substitui a aprovada; (3) insuficiência é sinalizada.

### `RF-058` — Calcular suficiência ou confiança dos dados

- **Descrição:** O sistema deverá apresentar separadamente quão sustentado está o Índice de Domínio.
- **Ator:** Sistema.
- **Prioridade:** V1 — Alta.
- **Pré-condições:** Tentativas elegíveis e regra de suficiência aprovada.
- **Comportamento esperado:** Avaliar volume, variedade, recência ou critérios autorizados sem confundir confiança com domínio.
- **Pós-condições:** Índice é acompanhado de indicador de evidência.
- **Exceções relevantes:** Alta taxa com pequena amostra deverá poder ter baixa confiança.
- **Critérios de aceitação:** (1) Domínio e confiança são campos distintos; (2) baixa amostra é sinalizada; (3) regra aplicada é explicável.

### `RF-059` — Consolidar domínio hierárquico

- **Descrição:** O sistema deverá calcular e apresentar domínio por disciplina, assunto e subassunto.
- **Ator:** Sistema e Estudante.
- **Prioridade:** V1 — Alta.
- **Pré-condições:** Hierarquia válida; fórmula de agregação aprovada.
- **Comportamento esperado:** Consolidar evidências sem fazer média ingênua de percentuais incompatíveis e permitir navegação entre níveis.
- **Pós-condições:** Valores hierárquicos e suas bases ficam disponíveis.
- **Exceções relevantes:** Nível sem evidência suficiente deverá ser marcado adequadamente.
- **Critérios de aceitação:** (1) Disciplina permite detalhar assuntos; (2) assunto permite detalhar subassuntos; (3) base de cada nível é identificável.

### `RF-060` — Explicar e versionar o domínio

- **Descrição:** O estudante deverá consultar fatores, versão da regra, período e limitações do Índice de Domínio.
- **Ator:** Estudante e Sistema.
- **Prioridade:** V1 — Alta.
- **Pré-condições:** Índice calculado ou tentativa de cálculo com dados insuficientes.
- **Comportamento esperado:** Apresentar explicação compreensível sem expor apenas um número isolado.
- **Pós-condições:** O usuário compreende por que o valor foi produzido.
- **Exceções relevantes:** Mudança de fórmula não poderá ser ocultada em série histórica.
- **Critérios de aceitação:** (1) Versão é identificável; (2) fatores principais são listados; (3) dados insuficientes explicam o motivo.

### `RF-061` — Determinar e reabrir questão dominada

- **Descrição:** Na V1, o sistema deverá aplicar critério reversível para marcar domínio e reabrir a questão quando houver evidência contrária.
- **Ator:** Sistema e Estudante, conforme regra aprovada.
- **Prioridade:** V1 — Alta.
- **Pré-condições:** Critério de domínio aprovado; histórico elegível.
- **Comportamento esperado:** Distinguir domínio de ciclo concluído, registrar mudança de estado e permitir reabertura válida.
- **Pós-condições:** Estado atual e histórico de transição ficam disponíveis.
- **Exceções relevantes:** Ação manual não poderá apagar evidências anteriores.
- **Critérios de aceitação:** (1) Ciclo concluído não implica domínio automaticamente; (2) novo erro pode reabrir conforme regra; (3) transição é registrada.

### `RF-062` — Recomendar prioridades de estudo de forma determinística

- **Descrição:** Na V1, o sistema deverá produzir uma lista explicável de assuntos prioritários.
- **Ator:** Sistema e Estudante.
- **Prioridade:** V1 — Média.
- **Pré-condições:** Critérios aprovados e dados suficientes.
- **Comportamento esperado:** Considerar fatores autorizados como atraso, baixo domínio, recorrência e volume; mostrar justificativa e permitir que o usuário ignore a sugestão.
- **Pós-condições:** Lista de apoio à decisão fica disponível.
- **Exceções relevantes:** Dados insuficientes deverão limitar ou impedir a recomendação; não usar IA obrigatória.
- **Critérios de aceitação:** (1) Cada prioridade possui motivo; (2) ordem é reproduzível; (3) recomendação não bloqueia outra escolha do estudante.

---

## 12. Pesquisa e filtros

### `RF-063` — Listar questões

- **Descrição:** O estudante deverá visualizar questões com identificação, conteúdo acadêmico e estado.
- **Ator:** Estudante.
- **Prioridade:** MVP — Essencial.
- **Pré-condições:** Espaço acessível.
- **Comportamento esperado:** Listar ativas por padrão, permitir acesso a rascunhos e arquivadas e apresentar estado vazio quando necessário.
- **Pós-condições:** Nenhum dado é alterado.
- **Exceções relevantes:** Grandes conjuntos deverão respeitar paginação ou carregamento definido nos RNFs/SDD.
- **Critérios de aceitação:** (1) Ativas aparecem por padrão; (2) rascunhos são distinguíveis; (3) item abre o detalhe correto.

### `RF-064` — Pesquisar por texto

- **Descrição:** O estudante deverá pesquisar palavras ou trechos no enunciado e, quando suportado, na explicação.
- **Ator:** Estudante.
- **Prioridade:** MVP — Alta.
- **Pré-condições:** Questões existentes.
- **Comportamento esperado:** Retornar resultados do próprio espaço, indicar ausência e permitir limpar a busca.
- **Pós-condições:** Lista reflete o termo sem alterar registros.
- **Exceções relevantes:** Busca vazia retorna comportamento padrão; pesquisa semântica está fora do MVP.
- **Critérios de aceitação:** (1) Trecho existente encontra a questão; (2) registros de outro espaço não aparecem; (3) limpar restaura a lista.

### `RF-065` — Aplicar filtros básicos

- **Descrição:** O estudante deverá filtrar por disciplina, assunto, subassunto, situação de revisão, resultado inicial e classificação de erro.
- **Ator:** Estudante.
- **Prioridade:** MVP — Alta.
- **Pré-condições:** Valores disponíveis ou conjunto vazio.
- **Comportamento esperado:** Mostrar somente registros compatíveis e atualizar opções hierárquicas conforme seleções.
- **Pós-condições:** Filtros ativos ficam visíveis.
- **Exceções relevantes:** Combinação sem resultado deverá ser informada, não tratada como erro.
- **Critérios de aceitação:** (1) Cada filtro isolado funciona; (2) hierarquia inválida não pode ser formada; (3) contagem corresponde ao resultado.

### `RF-066` — Combinar, remover e salvar filtros

- **Descrição:** O MVP deverá combinar e limpar filtros; na V1 poderá salvar consultas pessoais recorrentes.
- **Ator:** Estudante.
- **Prioridade:** MVP — Alta para combinar/limpar; V1 — Média para salvar.
- **Pré-condições:** Lista ou análise filtrável.
- **Comportamento esperado:** Aplicar interseção coerente, exibir chips/resumo dos filtros e restaurar estado padrão ao limpar.
- **Pós-condições:** Resultado corresponde à combinação; filtros salvos na V1 ficam nomeados.
- **Exceções relevantes:** Filtro salvo que referencia item arquivado deverá continuar compreensível ou solicitar ajuste.
- **Critérios de aceitação:** (1) Dois filtros retornam somente itens que atendem ambos; (2) limpar remove todos; (3) salvar não é exigido para concluir o MVP.

---

## 13. Gestão e proteção funcional dos dados

### `RF-067` — Preservar dados entre sessões

- **Descrição:** Questões, tentativas, erros, revisões e configurações confirmadas deverão permanecer disponíveis após encerrar e reabrir a aplicação.
- **Ator:** Sistema.
- **Prioridade:** MVP — Essencial.
- **Pré-condições:** Operação de gravação concluída com sucesso.
- **Comportamento esperado:** Persistir os registros e reconstruir o estado funcional na próxima sessão.
- **Pós-condições:** Usuário retoma o trabalho sem recadastro.
- **Exceções relevantes:** Falha de gravação deverá ser comunicada antes de afirmar sucesso.
- **Critérios de aceitação:** (1) Dados confirmados reaparecem; (2) revisões mantêm situação coerente; (3) falha não produz confirmação falsa.

### `RF-068` — Executar recuperação técnica do MVP

- **Descrição:** O MVP deverá possuir procedimento operacional verificado para recuperar dados após falha do ambiente.
- **Ator:** Responsável técnico e Sistema.
- **Prioridade:** MVP — Alta.
- **Pré-condições:** Backup compatível e procedimento documentado.
- **Comportamento esperado:** Restaurar conjunto consistente em ambiente controlado e validar vínculos essenciais.
- **Pós-condições:** Questões, tentativas e revisões recuperadas podem ser consultadas.
- **Exceções relevantes:** Backup inválido ou incompatível não deverá substituir dados íntegros silenciosamente.
- **Critérios de aceitação:** (1) Teste de restauração é concluído; (2) contagens e vínculos críticos são conferidos; (3) falha preserva o estado anterior quando possível.

### `RF-069` — Exportar dados pelo usuário

- **Descrição:** Na V1, o estudante deverá exportar seus dados em formato documentado e reutilizável.
- **Ator:** Estudante e Sistema.
- **Prioridade:** V1 — Alta.
- **Pré-condições:** Espaço acessível.
- **Comportamento esperado:** Gerar arquivo com questões, hierarquia, tentativas, erros, revisões e metadados necessários à interpretação.
- **Pós-condições:** Arquivo é disponibilizado sem alterar a base.
- **Exceções relevantes:** Falha de geração deverá informar o problema; segredos técnicos não devem ser exportados.
- **Critérios de aceitação:** (1) Exportação inclui histórico; (2) formato e versão são informados; (3) totais podem ser reconciliados com o sistema.

### `RF-070` — Criar e restaurar backup pela interface

- **Descrição:** Na V1, o estudante deverá criar backup e solicitar restauração com validação e confirmação.
- **Ator:** Estudante e Sistema.
- **Prioridade:** V1 — Alta.
- **Pré-condições:** Formato compatível; autorização válida; política de restauração definida.
- **Comportamento esperado:** Validar antes de substituir, mostrar impacto, solicitar confirmação e produzir relatório de resultado.
- **Pós-condições:** Dados restaurados formam estado consistente ou a operação é revertida.
- **Exceções relevantes:** Versão incompatível, arquivo corrompido e pertencimento inválido deverão bloquear restauração.
- **Critérios de aceitação:** (1) Arquivo inválido não altera a base; (2) sucesso restaura relações; (3) usuário recebe confirmação verificável.

### `RF-071` — Registrar alterações sensíveis

- **Descrição:** Na V1, correções, anulações, exclusões, reagendamentos e mudanças de regra deverão deixar registro auditável.
- **Ator:** Estudante e Sistema.
- **Prioridade:** V1 — Alta.
- **Pré-condições:** Operação sensível autorizada.
- **Comportamento esperado:** Registrar tipo, data, objeto, motivo quando exigido e relação com o registro anterior.
- **Pós-condições:** Impactos podem ser explicados e investigados.
- **Exceções relevantes:** Informações técnicas sensíveis não deverão ser expostas ao usuário final.
- **Critérios de aceitação:** (1) Correção de tentativa deixa trilha; (2) reagendamento preserva data anterior; (3) registro não pode ser editado pelo fluxo comum.

---

## 14. Requisitos explicitamente condicionais ou adiados

Os seguintes itens do escopo não geram requisitos de MVP nesta etapa:

- IA para classificação, explicação ou recomendação;
- algoritmo adaptativo de revisão;
- importação em massa, OCR ou captura de páginas;
- anexos e imagens;
- aplicativos nativos e offline garantido;
- notificações externas;
- professores, mentores, equipes ou compartilhamento;
- banco público de questões;
- gamificação;
- API pública.

Eles somente poderão receber requisitos funcionais executáveis após aprovação de mudança de escopo ou entrada formal no roadmap Pós-V1.

---

## 15. Matriz de rastreabilidade com o Escopo

| Escopo aprovado | Requisitos relacionados |
|---|---|
| `ESC-MVP-001` a `ESC-MVP-003` — uso individual e configuração | `RF-001` a `RF-003` |
| `ESC-MVP-004` — estrutura acadêmica | `RF-004` a `RF-008` |
| `ESC-MVP-005` — cadastro de questão | `RF-009` a `RF-019`; `RF-020` é V1 conforme sua própria definição |
| `ESC-MVP-006` — tentativa inicial | `RF-021` a `RF-024` |
| `ESC-MVP-007` e `ESC-MVP-008` — erro e aprendizado | `RF-028` a `RF-033`, `RF-014` e `RF-015` |
| `ESC-MVP-009` a `ESC-MVP-011` — revisão | `RF-034` a `RF-046` |
| `ESC-MVP-012` — histórico | `RF-025` a `RF-027` |
| `ESC-MVP-013` — dashboard | `RF-047` a `RF-056` |
| `ESC-V1-001` a `ESC-V1-004` — domínio e prioridade | `RF-057` a `RF-062` |
| `ESC-MVP-014` — busca e filtros | `RF-063` a `RF-066` |
| `ESC-MVP-015` e `ESC-V1-007` — integridade e gestão | `RF-067` a `RF-071` |

---

## 16. Decisões propostas nesta etapa

| ID | Decisão proposta |
|---|---|
| `RF-DEC-001` | Questões incompletas poderão existir como rascunho, sem tentativa, revisão ou contagem de questão realizada. |
| `RF-DEC-002` | Para ativar questão no MVP serão necessários disciplina, assunto, enunciado, ao menos duas alternativas e exatamente uma correta. |
| `RF-DEC-003` | Subassunto e dados de origem serão opcionais. |
| `RF-DEC-004` | Dificuldade da questão usará escala opcional fácil/média/difícil. |
| `RF-DEC-005` | Resultado objetivo será calculado pelo sistema, não digitado livremente. |
| `RF-DEC-006` | Erro inicial finalizado exigirá uma classificação principal; explicação e pegadinha poderão ser enriquecidas depois. |
| `RF-DEC-007` | A opção “outra” exigirá descrição curta. |
| `RF-DEC-008` | Facilidade da revisão poderá ser registrada em escala fácil/média/difícil, sem alterar datas no MVP. |
| `RF-DEC-009` | Mudança de gabarito após tentativa será bloqueada no MVP; correção auditável entrará na V1. |
| `RF-DEC-010` | Arquivamento preservará o histórico e suspenderá pendências. |
| `RF-DEC-011` | Ciclo concluído e domínio serão estados conceitualmente diferentes. |
| `RF-DEC-012` | Taxas sem denominador serão proibidas; ausência de dados não será apresentada como 0%. |
| `RF-DEC-013` | Conclusão de revisão e criação da tentativa deverão ocorrer como uma operação lógica única. |
| `RF-DEC-014` | Requisitos de V1 ficam documentados, mas não podem ser usados para impedir a entrega do MVP. |

---

## 17. Pontos ainda em aberto

| ID | Ponto | Etapa responsável |
|---|---|---|
| `RF-ABR-001` | Tamanho máximo de enunciado, alternativas, explicação e observações. | RNFs, regras e modelo de dados. |
| `RF-ABR-002` | Regra exata de nomes duplicados considerando maiúsculas, acentos e espaços. | Regras de negócio. |
| `RF-ABR-003` | Consequência de arquivar disciplina com descendentes ativos. | Regras de negócio. |
| `RF-ABR-004` | Regra após acerto ou erro em cada revisão. | Regras de negócio. |
| `RF-ABR-005` | Cálculo temporal em atraso, mudança de fuso e horário de verão. | Regras de negócio. |
| `RF-ABR-006` | Possibilidade de abandonar uma revisão iniciada sem resposta. | Regras e fluxos. |
| `RF-ABR-007` | Política completa de anulação, exclusão e reconstrução do ciclo. | Regras de negócio. |
| `RF-ABR-008` | Fórmula de domínio e confiança. | Regras de negócio. |
| `RF-ABR-009` | Forma de autenticação conforme implantação. | RNFs e SDD. |
| `RF-ABR-010` | Suporte a Markdown e notação matemática. | SDD. |
| `RF-ABR-011` | Limites e paginação para listas. | RNFs e SDD. |
| `RF-ABR-012` | Formato de exportação e compatibilidade de versões. | SDD e modelo de dados. |

---

## 18. Riscos funcionais

| ID | Risco | Resposta proposta |
|---|---|---|
| `RF-RIS-001` | Rascunhos aumentarem artificialmente o progresso. | Excluí-los de questões realizadas e métricas de tentativa. |
| `RF-RIS-002` | Gabarito incorreto contaminar histórico. | Validar estrutura, bloquear alteração crítica após tentativas e criar correção auditável na V1. |
| `RF-RIS-003` | Conclusão duplicada de revisão. | Exigir operação idempotente e vínculo único entre revisão e tentativa válida. |
| `RF-RIS-004` | Usuário abandonar classificação por atrito. | Categorias curtas, definições claras e enriquecimento posterior dos campos não essenciais. |
| `RF-RIS-005` | Facilidade percebida ser confundida com dificuldade da questão. | Usar campos e rótulos separados: dificuldade da questão versus facilidade da revisão. |
| `RF-RIS-006` | Dashboard misturar tentativas e questões. | Requisitos separados de contagem e definições acessíveis. |
| `RF-RIS-007` | Arquivamento esconder histórico. | Manter consulta e separar histórico de pendência ativa. |
| `RF-RIS-008` | Reagendamento apagar evidência de atraso. | Preservar data original e motivo. |
| `RF-RIS-009` | Índice de Domínio ser implementado cedo com fórmula frágil. | Manter requisito na V1 e exibir desempenho descritivo no MVP. |
| `RF-RIS-010` | Recuperação técnica não atender usuário comum. | Testar e antecipar backup pela interface se o piloto exigir. |

---

## 19. Sugestões de melhoria

### 19.1 Confirmação antes de finalizar tentativa

Exibir resposta dada e resultado calculado antes da confirmação reduz a necessidade de corrigir histórico no MVP.

### 19.2 Indicador “aprendizado pendente”

Quando explicação/regra e pegadinha estiverem vazias após um erro, a questão poderá ser sinalizada para enriquecimento sem bloquear a geração da revisão.

### 19.3 Glossário de classificações

As definições das categorias deverão incluir exemplos curtos para reduzir confusão entre erro conceitual, fórmula/regra e procedimento, ou entre interpretação e atenção.

### 19.4 Separação visual dos dois tipos de dificuldade

“Dificuldade da questão” pertence à questão; “facilidade da revisão” pertence à tentativa. A interface e o modelo de dados não deverão reutilizar o mesmo campo.

### 19.5 Detalhamento a partir das métricas

Sempre que possível, números do dashboard deverão abrir os registros correspondentes. Isso ajuda a explicar as métricas e facilita a futura validação dos cálculos.

---

## 20. Itens que precisam de aprovação

Para congelar a Etapa 3, deverão ser aprovados ou ajustados:

1. Os requisitos `RF-001` a `RF-071` e seus horizontes.
2. A existência de rascunhos fora das estatísticas de questões realizadas.
3. Os campos mínimos para ativar uma questão.
4. Questões objetivas com exatamente uma resposta correta no MVP.
5. Resultado calculado automaticamente.
6. Classificação principal obrigatória para erro finalizado.
7. Explicação e pegadinha permitidas como enriquecimento posterior.
8. Escalas separadas para dificuldade da questão e facilidade da revisão.
9. Bloqueio de mudança do gabarito após tentativas no MVP.
10. Arquivamento com suspensão de pendências e preservação do histórico.
11. Diferença entre ciclo concluído e domínio.
12. Requisitos de domínio, priorização, correção auditável, exportação e restauração como V1.
13. As decisões `RF-DEC-001` a `RF-DEC-014`.
14. A manutenção dos pontos `RF-ABR-001` a `RF-ABR-012` para as etapas indicadas.

---

## 21. Critério de encerramento da Etapa 3

A Etapa 3 será concluída quando:

- cada capacidade aprovada do MVP estiver coberta por ao menos um requisito funcional;
- os requisitos de V1 estiverem claramente marcados;
- todos os requisitos possuírem ator, prioridade, pré-condições, comportamento, pós-condições, exceções e aceitação;
- não houver requisito de IA, integração ou expansão proibida no MVP;
- os pontos dependentes de regra ou arquitetura estiverem encaminhados à etapa correta;
- as decisões aprovadas puderem orientar os RNFs, regras, dados, fluxos e testes.

A etapa foi aprovada integralmente em 30 de agosto de 2026. Os requisitos `RF-001` a `RF-071` e as decisões `RF-DEC-001` a `RF-DEC-014` passam a ser considerados congelados e somente poderão ser alterados mediante registro explícito e análise de impacto.

---

## 22. Errata controlada da V0.1 — `ERR-V01-009`

Em 2 de setembro de 2026, foram aprovados os textos canônicos iniciais exigidos
por `RF-029`. Esta errata preenche uma lacuna documental, sem criar funcionalidade
ou alterar o escopo. Os códigos são imutáveis; nomes e descrições podem evoluir
por decisão controlada sem mudança do código histórico.

| Código | Nome | Descrição canônica inicial |
|---|---|---|
| `CONCEPTUAL` | Conceitual | Erro causado por compreensão incorreta, incompleta ou ausente de um conceito necessário para resolver a questão. |
| `INTERPRETATION` | Interpretação | Erro causado pela compreensão incorreta do enunciado, texto, comando, gráfico, tabela ou informação apresentada. |
| `CALCULATION` | Cálculo | Erro causado durante a execução de operações matemáticas, algébricas ou numéricas, apesar de o método ou conceito estar correto. |
| `ATTENTION` | Atenção | Erro causado por distração, leitura apressada, troca de sinais, omissão de informação ou outro descuido de execução. |
| `FORMULA_RULE` | Fórmula/regra | Erro causado pelo desconhecimento, esquecimento ou aplicação incorreta de uma fórmula, regra, propriedade ou convenção. |
| `PROCEDURE` | Procedimento | Erro causado pela escolha, ordem ou execução inadequada das etapas necessárias para resolver a questão. |
| `TRAP` | Pegadinha | Erro provocado por alternativa, formulação ou detalhe do enunciado que induz a uma interpretação ou resposta aparentemente correta, mas inadequada. |
| `TIME_SHORTAGE` | Falta de tempo | Erro ou questão não concluída adequadamente porque o tempo disponível foi insuficiente para analisar ou resolver a questão. |
| `GUESS` | Chute | Resposta escolhida sem conhecimento ou justificativa suficiente, baseada predominantemente em tentativa ou acaso. |
| `OTHER` | Outra | Erro que não se enquadra adequadamente em nenhuma das demais categorias padrão. |

---

## 23. Errata controlada da V0.2 — `ERR-V02-002`, `004` e `005`

Esta seção não altera o texto integral dos requisitos congelados. Ela define a
parcela que constitui entrega da V0.2, conforme `ADR-010`.

| Requisito | Leitura autoritativa V0.2 | Parcela posterior |
|---|---|---|
| `RF-016` | Detalhe mostra conteúdo e metadados atuais, estado, classificação acadêmica, origem, dificuldade e revisões de conteúdo, sem valores fictícios | Tentativa/ciclo/histórico de aprendizagem: V0.3; indicadores: V0.4 |
| `RF-017` | Editar conteúdo, hierarquia válida, origem, dificuldade, explicação, pegadinha e observações; nova revisão preserva as anteriores | Preservação de tentativas e atualização de métricas/dashboard só podem ser comprovadas após V0.3/V0.4 |
| `RF-018` | Sem `Attempt` na V0.2, alteração de alternativas/gabarito é permitida apenas no estado estrutural sem tentativa e sempre cria revisão válida | Bloqueio com tentativa: V0.3; correção auditável: V1 |
| `RF-019` | Confirmar arquivamento, marcar a questão, retirar das ativas e preservar revisões de conteúdo | Tentativas, ciclo, revisão pendente e fila: V0.3 |
| `RF-020` | Não aplicável | V1, sem qualquer implementação antecipada |

---

## Errata controlada V0.3

`ADR-011` é a leitura autoritativa de fase para a aprendizagem: `RF-021`–`026`,
`RF-028`–`032` e `RF-034`–`044` são implementados nos recortes e etapas ali
definidos. Em especial, `RF-031` (correção de diagnóstico) entra na Etapa 4 da
V0.3 e não depende do dashboard; `RF-019` ganha somente o recorte V0.3 de
suspender ciclo/revisão/fila no arquivamento. `RF-027`, `RF-033`, `RF-045` e
`RF-046` continuam posteriores conforme seus próprios textos.
| `RF-063` | Ativas por padrão; acesso explícito e distinguível a rascunhos e arquivadas; paginação | Consultas analíticas posteriores |
| `RF-064` | Busca textual simples e limpeza da busca | FTS somente após benchmark e nova decisão |
| `RF-065` | Disciplina, assunto e subassunto; opções hierárquicas; filtros visíveis; estado vazio; contagem correspondente | Revisão, resultado e erro: V0.4 |
| `RF-066` | Não aplicável | Combinar/limpar genericamente na V0.5-A; salvar na V1 |

Estado da questão é filtro/lista de `RF-063`, não ampliação de `RF-065`.
Origem e dificuldade podem aparecer no catálogo, mas não são filtros
obrigatórios. Tags ficam fora por `ERR-V02-001`.
