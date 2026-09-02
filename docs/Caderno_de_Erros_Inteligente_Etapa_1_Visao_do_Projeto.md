# Caderno de Erros Inteligente

## Etapa 1 — Visão do Projeto

| Campo | Valor |
|---|---|
| Documento | Visão do Projeto |
| Projeto | Caderno de Erros Inteligente |
| Versão do documento | 1.0 — aprovada |
| Data | 30 de agosto de 2026 |
| Status | Aprovada e congelada |
| Aprovação | Aprovada integralmente pelo responsável pelo produto em 30 de agosto de 2026 |
| Próxima etapa | Etapa 2 — Escopo |

---

## 1. Finalidade deste documento

Este documento define a visão que orientará o produto **Caderno de Erros Inteligente**. Ele registra o problema a ser resolvido, o público atendido, a proposta de valor, os objetivos, os princípios, as premissas, as restrições e os critérios gerais de sucesso.

A visão funciona como referência para todas as etapas posteriores. Escopo, requisitos, regras de negócio, arquitetura, modelo de dados, fluxos, roadmap e testes deverão ser compatíveis com as decisões aqui aprovadas. Uma alteração futura nesta visão deverá ser registrada explicitamente e ter seus impactos avaliados antes de modificar os demais documentos.

Esta etapa não define ainda:

- a lista fechada de funcionalidades do MVP;
- fórmulas definitivas para o Índice de Domínio;
- tecnologias, banco de dados ou arquitetura de implantação;
- telas e detalhes de interface;
- regras completas de revisão e reagendamento;
- metas numéricas finais de adoção, desempenho ou aprendizagem.

Esses elementos serão tratados nas etapas apropriadas.

---

## 2. Identidade do projeto

### 2.1 Nome provisório

**Caderno de Erros Inteligente**.

O nome comunica os dois elementos centrais do produto:

1. **Caderno de erros:** registro estruturado das questões, respostas, erros e aprendizados.
2. **Inteligente:** transformação desses registros em revisões programadas, histórico, métricas explicáveis e prioridades de estudo.

O uso do termo “inteligente” não implica dependência de inteligência artificial. No contexto inicial, a inteligência do produto está na organização dos dados, na revisão espaçada, na análise histórica e na geração de indicadores úteis.

O nome permanece provisório e poderá ser reavaliado antes da identidade visual ou da publicação do produto, sem alterar sua finalidade.

### 2.2 Declaração de visão

> Transformar cada erro cometido durante os estudos em uma unidade organizada de aprendizagem, com revisão programada, histórico preservado e evidências claras de evolução.

### 2.3 Missão do produto

Ajudar estudantes a identificar por que erram, revisar o que realmente precisa ser revisto e acompanhar a consolidação do conhecimento de forma contínua, mensurável e compreensível.

---

## 3. Resumo executivo

O Caderno de Erros Inteligente será uma plataforma individual de estudo voltada ao registro e à análise de questões. O sistema ampliará o conceito de um caderno de erros tradicional ao relacionar cada questão a seu contexto acadêmico, às respostas dadas pelo estudante, às causas dos erros, às explicações aprendidas e a um ciclo de revisões espaçadas.

Uma questão será preservada como objeto de estudo, enquanto cada resolução ou revisão será registrada separadamente como uma tentativa. Essa separação permitirá reconstruir a trajetória do estudante: quando errou, qual foi a causa atribuída, como respondeu nas revisões e se o conhecimento se tornou mais estável ao longo do tempo.

O produto deverá converter esses dados em ações concretas. Em vez de apenas armazenar anotações, ele mostrará revisões devidas, atrasos, recorrências de erro, evolução do desempenho e níveis de domínio por disciplina, assunto e subassunto. As métricas deverão ser rastreáveis e explicáveis, evitando percentuais que escondam amostras pequenas, períodos analisados ou critérios utilizados.

O projeto começará como um sistema independente e de foco delimitado. Recursos de inteligência artificial, recomendações avançadas, integração com agentes, segundo cérebro ou painéis externos pertencem à visão de evolução, mas não deverão ampliar o escopo inicial.

---

## 4. Problema que o sistema resolve

### 4.1 Problema central — `VIS-PRB-001`

Estudantes resolvem muitas questões, mas frequentemente perdem o valor pedagógico dos erros porque não possuem um processo simples e consistente para:

- registrar o erro e seu contexto;
- distinguir a resposta dada da resposta correta;
- explicar a causa real do erro;
- guardar a regra, o raciocínio ou a pegadinha relevante;
- reencontrar a questão no momento adequado;
- comparar tentativas realizadas em datas diferentes;
- perceber erros recorrentes e fragilidades por assunto;
- verificar se o conteúdo foi efetivamente consolidado.

### 4.2 Limitações das soluções informais — `VIS-PRB-002`

Cadernos físicos, anotações soltas e planilhas genéricas podem guardar informações, mas normalmente exigem controle manual das datas e dificultam o histórico, os filtros, a consolidação de métricas e a identificação de padrões. Quando o volume cresce, o estudante tende a revisar por intuição ou conveniência, não necessariamente por prioridade.

### 4.3 Consequências do problema — `VIS-PRB-003`

Sem uma estrutura adequada, o estudante pode:

- repetir o mesmo tipo de erro sem reconhecê-lo;
- confundir volume de questões com domínio do conteúdo;
- gastar tempo revisando temas já estáveis enquanto negligencia fragilidades;
- perder explicações úteis elaboradas após uma questão;
- acumular revisões sem saber o que priorizar;
- acompanhar apenas acertos totais, ignorando recência, dificuldade e recorrência;
- tomar decisões de estudo com base em métricas incompletas ou enganosas.

### 4.4 Necessidade atendida — `VIS-PRB-004`

O produto deve fornecer um ciclo fechado entre **resolver, registrar, compreender, revisar e medir**, de modo que o erro deixe de ser somente um resultado negativo e se torne uma fonte reutilizável de aprendizagem.

---

## 5. Público-alvo

### 5.1 Público primário — `VIS-PUB-001`

Estudantes que utilizam questões como parte relevante de sua preparação e precisam revisar erros ao longo do tempo, especialmente:

- candidatos a concursos públicos;
- estudantes de vestibulares e exames nacionais;
- candidatos a certificações profissionais;
- universitários em disciplinas avaliadas por exercícios e provas;
- autodidatas que estudam conteúdos organizados por disciplinas e assuntos.

O público primário inclui tanto quem já mantém um caderno de erros manual quanto quem ainda não possui um método consistente para tratar questões erradas.

### 5.2 Perfil comportamental prioritário — `VIS-PUB-002`

O produto prioriza o estudante que:

- resolve questões com frequência;
- estuda mais de uma disciplina ou assunto;
- precisa reconhecer padrões de erro;
- deseja um método de revisão previsível;
- valoriza histórico e métricas, mas não quer manter cálculos manualmente;
- aceita registrar informações essenciais após uma resolução para obter benefícios futuros.

### 5.3 Público secundário — `VIS-PUB-003`

Em versões futuras, o sistema poderá atender professores, mentores ou responsáveis pelo acompanhamento de estudos, desde que isso não comprometa a experiência individual nem transforme o MVP em uma plataforma institucional.

### 5.4 Público não prioritário no início — `VIS-PUB-004`

Não são foco inicial:

- escolas, cursos preparatórios e operações com múltiplas turmas;
- autores ou editoras que desejem distribuir bancos comerciais de questões;
- equipes que precisem de colaboração simultânea;
- usuários que busquem um gerenciador geral de tarefas, notas ou produtividade;
- instituições que exijam recursos administrativos, cobrança ou gestão acadêmica.

---

## 6. Necessidades do usuário

As necessidades abaixo descrevem resultados desejados, não soluções técnicas definitivas.

| ID | Necessidade |
|---|---|
| `VIS-NEC-001` | Registrar uma questão com contexto suficiente para compreendê-la e encontrá-la posteriormente. |
| `VIS-NEC-002` | Registrar o resultado de cada resolução sem sobrescrever o histórico anterior. |
| `VIS-NEC-003` | Identificar a causa do erro, e não somente marcar que a resposta estava incorreta. |
| `VIS-NEC-004` | Guardar uma explicação curta, regra, procedimento ou pegadinha que ajude a evitar a repetição do erro. |
| `VIS-NEC-005` | Saber quais questões precisam ser revisadas hoje e quais estão atrasadas. |
| `VIS-NEC-006` | Visualizar a própria evolução por disciplina, assunto e subassunto. |
| `VIS-NEC-007` | Reconhecer erros recorrentes e temas que merecem prioridade. |
| `VIS-NEC-008` | Entender como cada métrica foi calculada e quais dados a sustentam. |
| `VIS-NEC-009` | Manter o processo útil mesmo antes de existirem recursos avançados ou inteligência artificial. |

---

## 7. Proposta de valor

### 7.1 Proposta principal — `VIS-VAL-001`

Para estudantes que resolvem questões e precisam transformar erros dispersos em progresso verificável, o Caderno de Erros Inteligente organiza cada questão, preserva todas as tentativas, agenda revisões e converte o histórico em indicadores explicáveis de desempenho e domínio.

Diferentemente de um caderno comum ou de uma planilha genérica, o produto conecta no mesmo ciclo:

**questão → tentativa → causa do erro → aprendizagem registrada → revisão → histórico → análise → nova prioridade.**

### 7.2 Benefícios centrais

| Benefício | Valor para o usuário |
|---|---|
| Memória estruturada | Reduz a perda de questões, regras e explicações relevantes. |
| Revisão orientada por datas | Diminui a dependência de lembretes e controles manuais. |
| Histórico de tentativas | Mostra se um acerto foi consistente ou apenas pontual. |
| Diagnóstico de erros | Ajuda a separar falta de conhecimento, interpretação, cálculo, atenção e outros motivos. |
| Visão hierárquica | Permite analisar disciplina, assunto e subassunto sem misturar níveis. |
| Métricas explicáveis | Dá contexto aos percentuais e reduz interpretações enganosas. |
| Priorização | Direciona o esforço para revisões vencidas, erros recorrentes e conteúdos frágeis. |

### 7.3 Trabalho principal a ser realizado

Quando eu errar ou revisar uma questão, quero registrar o que aconteceu e receber orientação objetiva sobre quando e por que revê-la, para diminuir a repetição dos mesmos erros e tomar decisões de estudo com base no meu histórico real.

---

## 8. Objetivos principais

| ID | Objetivo | Evidência geral de realização |
|---|---|---|
| `VIS-OBJ-P-001` | Estruturar o registro de questões e seus contextos de estudo. | Questões podem ser organizadas por disciplina, assunto, subassunto, fonte e demais metadados relevantes. |
| `VIS-OBJ-P-002` | Preservar a trajetória completa de resolução de cada questão. | Cada resolução ou revisão gera uma tentativa própria, datada e vinculada à questão, sem substituir tentativas anteriores. |
| `VIS-OBJ-P-003` | Transformar erros em registros acionáveis de aprendizagem. | O estudante pode registrar causa do erro, resposta correta, explicação/regra e pegadinha quando aplicável. |
| `VIS-OBJ-P-004` | Implementar um processo confiável de revisão espaçada. | O sistema calcula, apresenta e atualiza revisões a partir de regras conhecidas, começando pelos intervalos de 1, 7, 14 e 30 dias. |
| `VIS-OBJ-P-005` | Oferecer acompanhamento compreensível do desempenho e do domínio. | O painel apresenta métricas por período e por nível da hierarquia, com definição e origem dos dados acessíveis ao usuário. |
| `VIS-OBJ-P-006` | Apoiar a priorização do estudo. | O sistema evidencia revisões devidas, atrasos, recorrências e áreas frágeis sem exigir consolidação manual. |
| `VIS-OBJ-P-007` | Manter o produto focado e evolutivo. | O núcleo funciona de modo independente, e recursos avançados só são incorporados quando houver valor validado e compatibilidade com a visão. |

---

## 9. Objetivos secundários

| ID | Objetivo | Observação |
|---|---|---|
| `VIS-OBJ-S-001` | Reduzir o esforço de manutenção de um caderno de erros. | A redução não pode eliminar os campos necessários à reflexão do estudante. |
| `VIS-OBJ-S-002` | Facilitar pesquisas, filtros e recuperação de registros. | Os detalhes serão definidos no escopo e nos requisitos funcionais. |
| `VIS-OBJ-S-003` | Permitir que o estudante observe evolução ao longo do tempo. | A análise deve considerar período e volume de dados. |
| `VIS-OBJ-S-004` | Dar visibilidade aos tipos de erro mais frequentes. | A classificação deve permanecer compreensível e gerenciável. |
| `VIS-OBJ-S-005` | Preparar o domínio conceitual para futura revisão adaptativa. | A primeira versão não depende de algoritmo adaptativo. |
| `VIS-OBJ-S-006` | Preparar o sistema para futuras integrações controladas. | O sistema não deve depender dessas integrações para cumprir seu propósito. |
| `VIS-OBJ-S-007` | Favorecer confiança nos dados pessoais de estudo. | Integridade, privacidade, exportação e recuperação serão detalhadas nas próximas etapas. |

---

## 10. Não objetivos do produto

Os itens a seguir evitam que a visão seja interpretada como autorização para crescimento irrestrito:

| ID | Não objetivo inicial |
|---|---|
| `VIS-NAO-001` | Substituir uma plataforma completa de cursos, videoaulas ou materiais didáticos. |
| `VIS-NAO-002` | Tornar-se um gerenciador geral de tarefas, agenda pessoal ou segundo cérebro. |
| `VIS-NAO-003` | Criar um banco público ou comercial de questões no MVP. |
| `VIS-NAO-004` | Automatizar integralmente a aprendizagem ou dispensar a reflexão do estudante. |
| `VIS-NAO-005` | Prometer aprovação em provas ou domínio real apenas com base no uso do sistema. |
| `VIS-NAO-006` | Usar inteligência artificial como requisito para o funcionamento inicial. |
| `VIS-NAO-007` | Atender, no MVP, gestão de turmas, cobrança, marketplace, rede social ou colaboração em tempo real. |
| `VIS-NAO-008` | Definir o Índice de Domínio como verdade absoluta sobre conhecimento. |

---

## 11. Resultados esperados

### 11.1 Para o estudante

| ID | Resultado esperado |
|---|---|
| `VIS-RES-001` | Ter um repositório confiável das questões relevantes e do aprendizado extraído delas. |
| `VIS-RES-002` | Conseguir iniciar uma sessão de revisão sabendo quais itens estão devidos e atrasados. |
| `VIS-RES-003` | Reconhecer a diferença entre um erro isolado e um padrão recorrente. |
| `VIS-RES-004` | Ver a evolução de uma mesma questão por meio das tentativas sucessivas. |
| `VIS-RES-005` | Identificar disciplinas, assuntos e subassuntos que exigem maior atenção. |
| `VIS-RES-006` | Tomar decisões de estudo com base em dados compreensíveis, sem depender apenas de memória ou impressão. |
| `VIS-RES-007` | Reduzir, ao longo do uso, a recorrência de erros já estudados. |

### 11.2 Para o produto

| ID | Resultado esperado |
|---|---|
| `VIS-RES-008` | Validar que o ciclo de registro e revisão oferece valor mesmo em uma versão enxuta. |
| `VIS-RES-009` | Formar uma base histórica consistente para estatísticas e futuras recomendações. |
| `VIS-RES-010` | Evoluir sem quebrar o vínculo entre questões, tentativas, erros, revisões e métricas. |
| `VIS-RES-011` | Manter clara a separação entre recursos essenciais, incrementos da V1 e possibilidades futuras. |

### 11.3 Resultado de aprendizagem versus contribuição do sistema

O sistema pode ajudar o estudante a reduzir erros e consolidar conteúdos, mas não controla fatores como qualidade do material, dedicação, dificuldade das questões ou condições da prova. Portanto, seus indicadores devem representar **evidências do histórico registrado**, não garantias de conhecimento absoluto ou aprovação.

---

## 12. Diferenciais do produto

### `VIS-DIF-001` — Questão e tentativa como conceitos distintos

A questão mantém o conteúdo e o contexto; cada tentativa mantém o evento de resolução. Isso evita sobrescrever o passado e permite analisar mudanças de desempenho e de causa do erro.

### `VIS-DIF-002` — Erro tratado como diagnóstico

O sistema não se limita a contar respostas incorretas. Ele permite registrar por que o erro ocorreu e quais informações podem preveni-lo no futuro.

### `VIS-DIF-003` — Revisão integrada ao registro

A revisão não é uma lista paralela ou uma anotação manual: ela faz parte do ciclo da questão e produz novo histórico.

### `VIS-DIF-004` — Domínio hierárquico

O acompanhamento pode ser consolidado em disciplina, assunto e subassunto, preservando a possibilidade de investigar os dados que compõem cada nível.

### `VIS-DIF-005` — Métricas explicáveis

Resultados deverão indicar contexto suficiente para interpretação, como período, volume de tentativas, nível hierárquico e critérios aplicados. Uma pontuação não deverá aparecer como fato incontestável sem que o usuário possa compreender sua origem.

### `VIS-DIF-006` — Atenção à recorrência e à recência

O produto deverá ser capaz de distinguir um desempenho antigo de um desempenho recente e um erro eventual de um erro repetido, especialmente na evolução futura do Índice de Domínio.

### `VIS-DIF-007` — Foco deliberado

O produto é especializado em erros, tentativas e revisões. Ele não pretende competir, no início, com plataformas completas de produtividade ou ensino.

---

## 13. Princípios do produto

| ID | Princípio | Implicação prática |
|---|---|---|
| `VIS-PRI-001` | **Erro é informação, não punição.** | A linguagem e as métricas devem favorecer diagnóstico e melhoria, evitando constrangimento ou gamificação punitiva. |
| `VIS-PRI-002` | **O histórico não deve ser apagado silenciosamente.** | Edições, exclusões e correções que afetem tentativas ou métricas exigirão regras explícitas e proteção da integridade. |
| `VIS-PRI-003` | **Questão não é tentativa.** | Conteúdo e eventos de resolução terão ciclos de vida e responsabilidades diferentes. |
| `VIS-PRI-004` | **Toda revisão concluída gera histórico.** | Uma revisão não pode alterar apenas a próxima data; ela deve registrar o resultado que justificou a alteração. |
| `VIS-PRI-005` | **Métrica sem contexto pode enganar.** | Percentuais devem expor base, período e regra relevante; amostras insuficientes precisam ser sinalizadas. |
| `VIS-PRI-006` | **O valor central deve existir sem IA.** | Registro, revisão, histórico e métricas fundamentais devem funcionar de forma determinística e verificável. |
| `VIS-PRI-007` | **A revisão deve terminar em ação clara.** | O usuário precisa saber o que está devido, atrasado ou próximo, e o sistema deve registrar o resultado. |
| `VIS-PRI-008` | **Profundidade com baixo atrito.** | O sistema deve capturar dados úteis sem tornar cada registro tão demorado que o estudante abandone o processo. |
| `VIS-PRI-009` | **Evolução sem perda de rastreabilidade.** | Novos algoritmos ou integrações não podem romper o histórico nem esconder mudanças de cálculo. |
| `VIS-PRI-010` | **Prioridade é apoio, não ordem absoluta.** | Recomendações futuras devem explicar seus fatores e permitir decisão do estudante. |
| `VIS-PRI-011` | **Privacidade desde a concepção.** | Dados de estudo pertencem ao usuário e devem receber proteção, controle e possibilidade de recuperação ou portabilidade. |
| `VIS-PRI-012` | **O núcleo define o produto.** | Recursos futuros só entram se fortalecerem o ciclo resolver–compreender–revisar–medir. |

---

## 14. Premissas

Premissas são condições consideradas verdadeiras para orientar a documentação, mas que poderão precisar de validação.

| ID | Premissa | Impacto se estiver incorreta |
|---|---|---|
| `VIS-PRE-001` | O usuário aceita registrar ao menos os dados essenciais de uma questão e de sua tentativa. | Se o esforço percebido for alto, será necessário simplificar o fluxo, oferecer preenchimento progressivo ou rever campos obrigatórios. |
| `VIS-PRE-002` | O principal uso será individual. | Uso por turmas ou organizações exigiria permissões, papéis, compartilhamento e modelo operacional diferentes. |
| `VIS-PRE-003` | A hierarquia disciplina → assunto → subassunto atende à maioria dos casos iniciais. | Estruturas mais flexíveis poderão ser necessárias para estudos interdisciplinares ou taxonomias especiais. |
| `VIS-PRE-004` | Os intervalos iniciais de 1, 7, 14 e 30 dias oferecem um ponto de partida compreensível. | A validação poderá indicar necessidade de personalização ou outro calendário, sem eliminar o histórico já criado. |
| `VIS-PRE-005` | O usuário consegue avaliar o resultado de sua resposta e, quando houver erro, atribuir uma classificação útil. | Poderão ser necessários exemplos, categoria “não identificado” ou classificação posterior. |
| `VIS-PRE-006` | O histórico de tentativas gera mais valor do que armazenar apenas o último estado. | Se a consulta ficar complexa, a interface deverá simplificar a visualização sem eliminar os dados. |
| `VIS-PRE-007` | Métricas por disciplina e assunto ajudam a decidir o que estudar. | As métricas deverão ser ajustadas ou complementadas se não resultarem em decisões úteis. |
| `VIS-PRE-008` | O projeto pode validar seu núcleo sem integrações externas e sem recursos de IA. | Se a entrada manual impedir a validação, formas controladas de importação poderão ser antecipadas, com revisão de escopo. |

---

## 15. Restrições iniciais

| ID | Restrição | Justificativa |
|---|---|---|
| `VIS-RES-T-001` | O sistema será inicialmente um projeto independente. | Evita dependência técnica e expansão de escopo causada por agentes, painéis ou outros aplicativos. |
| `VIS-RES-T-002` | O primeiro ciclo usará revisão espaçada fixa de 1, 7, 14 e 30 dias. | Permite validar o fluxo antes de introduzir algoritmo adaptativo. |
| `VIS-RES-T-003` | IA, recomendações avançadas e integrações não serão pré-requisitos do MVP. | Preserva simplicidade, previsibilidade e testabilidade do núcleo. |
| `VIS-RES-T-004` | O Índice de Domínio não será reduzido a acertos divididos por questões. | A métrica precisa considerar qualidade e suficiência dos dados, mas sua fórmula será definida e justificada posteriormente. |
| `VIS-RES-T-005` | Nenhuma tentativa de revisão poderá ser descartada apenas por gerar um resultado inconveniente. | O histórico completo é essencial para análise de recorrência e evolução. |
| `VIS-RES-T-006` | Decisões de stack e implantação dependerão de requisitos e comparação técnica. | Evita vincular o produto prematuramente a tecnologias escolhidas por preferência. |
| `VIS-RES-T-007` | Funcionalidades gerais de produtividade permanecerão fora do núcleo. | Impede que o projeto perca foco e se torne um superaplicativo. |
| `VIS-RES-T-008` | Métricas e recomendações não poderão ocultar seus principais critérios. | Mantém confiança, auditabilidade e capacidade de correção. |

---

## 16. Critérios gerais de sucesso

Os critérios abaixo definem o que caracterizará um produto coerente com a visão. Metas numéricas de negócio e usabilidade serão estabelecidas no roadmap ou em ciclos de validação, após existir uma linha de base.

### 16.1 Sucesso funcional

| ID | Critério |
|---|---|
| `VIS-CSU-001` | O usuário consegue registrar uma questão, seu resultado, a causa de um erro e o aprendizado associado sem depender de ferramenta externa. |
| `VIS-CSU-002` | O sistema gera e apresenta as revisões previstas pelo ciclo inicial. |
| `VIS-CSU-003` | Cada resolução ou revisão concluída permanece consultável como tentativa distinta. |
| `VIS-CSU-004` | O painel diferencia, no mínimo, atividade, resultados, revisões e distribuição por conteúdo sem misturar conceitos. |

### 16.2 Sucesso informacional

| ID | Critério |
|---|---|
| `VIS-CSU-005` | Toda métrica importante pode ser explicada pelos dados e regras que a originaram. |
| `VIS-CSU-006` | O usuário consegue distinguir dados insuficientes de evidências reais de domínio ou fragilidade. |
| `VIS-CSU-007` | Alterações de questão ou tentativa não produzem inconsistências silenciosas no histórico ou nos indicadores. |

### 16.3 Sucesso de uso

| ID | Critério |
|---|---|
| `VIS-CSU-008` | O fluxo central é simples o bastante para ser repetido durante uma rotina real de estudos. |
| `VIS-CSU-009` | O usuário consegue identificar rapidamente a próxima ação de revisão. |
| `VIS-CSU-010` | O valor percebido do histórico e da priorização compensa o esforço de registrar os dados essenciais. |

### 16.4 Sucesso pedagógico

| ID | Critério |
|---|---|
| `VIS-CSU-011` | O sistema torna visíveis erros recorrentes que antes poderiam passar despercebidos. |
| `VIS-CSU-012` | O histórico permite observar se o desempenho em conteúdos revisados se estabiliza, melhora ou piora. |
| `VIS-CSU-013` | As informações produzidas ajudam o usuário a escolher onde concentrar o estudo, sem apresentar inferências frágeis como certezas. |

### 16.5 Indicadores candidatos para validação posterior

Estes indicadores são candidatos, não metas aprovadas:

- proporção de questões registradas que recebem ao menos uma revisão;
- proporção de revisões concluídas no prazo ou recuperadas após atraso;
- tempo mediano para registrar questão e tentativa;
- frequência de erros recorrentes por classificação e assunto;
- variação do desempenho entre tentativa inicial e revisões;
- retenção de uso do fluxo central ao longo de semanas;
- percentual de métricas cuja origem o usuário consegue compreender;
- avaliação subjetiva de utilidade das prioridades sugeridas.

Os valores-alvo deverão ser definidos somente após protótipo, teste com uso real ou obtenção de uma linha de base.

---

## 17. Visão de evolução futura

A evolução deve ocorrer em camadas e preservar o funcionamento independente do núcleo.

### 17.1 Núcleo inicial

- registro estruturado de questão;
- registro de resposta correta ou incorreta;
- classificação de erro;
- explicação/regra e pegadinha;
- tentativas separadas da questão;
- ciclo de revisão de 1, 7, 14 e 30 dias;
- revisões do dia e atrasadas;
- histórico de tentativas;
- dashboard e métricas básicos.

### 17.2 Consolidação do produto

- filtros e análises mais refinados;
- indicadores hierárquicos de desempenho;
- definição validada e versionada do Índice de Domínio;
- melhor tratamento de dados insuficientes;
- personalizações controladas do fluxo;
- recursos de portabilidade, backup e recuperação compatíveis com a estratégia técnica.

### 17.3 Inteligência adaptativa

- intervalos ajustados conforme erro, acerto, dificuldade percebida e histórico;
- recomendação explicável de “O que estudar agora?”;
- identificação de padrões de erro e assuntos prioritários;
- simulação ou comparação entre critérios de priorização;
- versionamento das regras para que mudanças não distorçam silenciosamente séries históricas.

### 17.4 Integrações futuras

- agente de revisão diária ou semanal;
- painel central de organização;
- segundo cérebro;
- importadores ou exportadores para ferramentas de estudo;
- APIs controladas para outros sistemas.

Integrações deverão ser opcionais. A ausência ou indisponibilidade de um serviço externo não deverá impedir o uso do núcleo do produto.

### 17.5 Expansões condicionais

Somente após validação poderão ser consideradas:

- acompanhamento por professores ou mentores;
- espaços compartilhados;
- importação automatizada de questões;
- apoio de IA para sugerir classificação, resumo ou explicação;
- recursos institucionais.

Essas possibilidades não constituem compromisso de implementação.

---

## 18. Hipótese de produto

### Hipótese principal — `VIS-HIP-001`

Se estudantes que resolvem questões puderem registrar seus erros de forma estruturada, revisar os itens em momentos definidos e consultar um histórico explicável de desempenho, então conseguirão reconhecer fragilidades e reduzir a repetição de erros com mais consistência do que usando anotações dispersas ou memória informal.

### Sinais que sustentariam a hipótese

- o usuário retorna para realizar as revisões geradas;
- o histórico é consultado para tomar decisões de estudo;
- erros recorrentes tornam-se identificáveis;
- questões revisadas mostram evolução observável em tentativas posteriores;
- o usuário considera o processo útil o bastante para manter o registro.

### Sinais que enfraqueceriam a hipótese

- o cadastro é abandonado por exigir esforço excessivo;
- as revisões acumulam sem ação;
- as métricas não mudam decisões de estudo;
- o usuário não confia na classificação ou no Índice de Domínio;
- o sistema passa a ser usado somente como arquivo de questões, sem fechar o ciclo de revisão.

---

## 19. Decisões registradas nesta etapa

As decisões abaixo são propostas para congelamento após aprovação desta etapa:

| ID | Decisão |
|---|---|
| `VIS-DEC-001` | O nome provisório será **Caderno de Erros Inteligente**. |
| `VIS-DEC-002` | O propósito central será transformar erros em aprendizagem mensurável e revisável. |
| `VIS-DEC-003` | Questão e tentativa serão conceitos distintos em todo o projeto. |
| `VIS-DEC-004` | Toda revisão concluída gerará uma nova tentativa no histórico. |
| `VIS-DEC-005` | O produto inicial será individual e independente de integrações externas. |
| `VIS-DEC-006` | A revisão inicial utilizará os marcos de 1, 7, 14 e 30 dias. |
| `VIS-DEC-007` | O sistema deverá analisar conteúdo na hierarquia disciplina → assunto → subassunto. |
| `VIS-DEC-008` | O Índice de Domínio combinará múltiplos fatores e deverá ser explicável; sua fórmula ainda não está definida. |
| `VIS-DEC-009` | Recursos de IA, adaptação avançada e integração ficarão para evolução posterior. |
| `VIS-DEC-010` | O sistema não será, no escopo inicial, uma plataforma geral de produtividade, ensino ou gestão institucional. |
| `VIS-DEC-011` | Métricas deverão indicar contexto, origem e limitações, inclusive quando houver dados insuficientes. |
| `VIS-DEC-012` | O sucesso será medido pela qualidade do ciclo de registro, revisão, histórico e decisão, e não apenas pelo volume de questões cadastradas. |

---

## 20. Pontos ainda em aberto

Estes pontos não impedem a aprovação da visão, mas deverão ser decididos antes ou durante as etapas indicadas.

| ID | Ponto em aberto | Alternativas principais | Recomendação inicial | Etapa adequada |
|---|---|---|---|---|
| `VIS-ABR-001` | Plataforma inicial | Web responsiva/PWA; desktop; aplicativo móvel | Avaliar uma aplicação web responsiva como primeira opção, sem congelar antes do SDD. | Escopo e SDD |
| `VIS-ABR-002` | Modelo de usuário do primeiro MVP | Conta autenticada; perfil local único; ambos | Decidir após requisitos de portabilidade, sincronização e privacidade. | Escopo e RNF |
| `VIS-ABR-003` | Campos obrigatórios no cadastro | Formulário completo; núcleo mínimo com complementação posterior | Preferir núcleo mínimo obrigatório e enriquecimento progressivo para reduzir atrito. | Requisitos e regras de negócio |
| `VIS-ABR-004` | Classificação de erros | Lista fixa; lista personalizável; modelo híbrido | Começar com categorias padrão e prever “outro”; avaliar personalização sem prejudicar estatísticas. | Requisitos e regras de negócio |
| `VIS-ABR-005` | Origem do ciclo de revisão | Somente erros; todas as questões; escolha do usuário | Priorizar erros no MVP e documentar exceções antes de decidir definitivamente. | Escopo e regras de negócio |
| `VIS-ABR-006` | Significado de “questão dominada” | Conclusão do ciclo; sequência de acertos; Índice de Domínio; combinação | Usar critério explícito e reversível, provavelmente combinando revisões e desempenho. | Regras de negócio |
| `VIS-ABR-007` | Reação a erro durante revisão | Reiniciar ciclo; voltar um estágio; reagendar por dificuldade | Comparar alternativas com casos concretos antes de congelar. | Regras de negócio |
| `VIS-ABR-008` | Fórmula do Índice de Domínio | Heurística ponderada; modelo por evidência; algoritmo de memória | Adotar primeiro uma fórmula determinística, explicável, versionada e testável. | Regras de negócio |
| `VIS-ABR-009` | Edição e exclusão do histórico | Bloqueio; correção auditável; exclusão definitiva | Preservar integridade com correção auditável e regras claras para exclusão. | Regras de negócio e RNF |
| `VIS-ABR-010` | Metas numéricas de sucesso | Metas fixas desde o início; linha de base antes das metas | Obter linha de base no protótipo/MVP e então definir metas realistas. | Roadmap e plano de testes |

---

## 21. Riscos principais

| ID | Risco | Probabilidade inicial | Impacto | Resposta proposta |
|---|---|---:|---:|---|
| `VIS-RIS-001` | O cadastro exigir dados demais e interromper o ritmo de estudo. | Alta | Alto | Definir campos essenciais, preenchimento progressivo e fluxo rápido; validar tempo de cadastro. |
| `VIS-RIS-002` | O Índice de Domínio transmitir falsa precisão. | Alta | Alto | Exibir componentes, confiança/amostra e versão da fórmula; sinalizar dados insuficientes. |
| `VIS-RIS-003` | Revisões atrasadas acumularem e desmotivarem o usuário. | Média/alta | Alto | Criar regras claras de atraso, priorização e recuperação, sem punição excessiva. |
| `VIS-RIS-004` | Categorias de erro se tornarem numerosas ou inconsistentes. | Média | Médio/alto | Manter taxonomia inicial pequena, definições claras e tratamento controlado de personalizações. |
| `VIS-RIS-005` | Acertos por memorização da resposta serem confundidos com domínio do assunto. | Alta | Alto | Tratar domínio como evidência contextual, considerar variedade e recência e evitar conclusões com amostras pequenas. |
| `VIS-RIS-006` | A mesma questão ser cadastrada repetidamente. | Média | Médio | Prever prevenção ou identificação de duplicidade sem bloquear casos legítimos. |
| `VIS-RIS-007` | Edições ou exclusões alterarem estatísticas sem explicação. | Média | Alto | Definir trilha de alteração e recálculo consistente nas regras de negócio. |
| `VIS-RIS-008` | O projeto crescer para IA, integrações e produtividade antes de validar o núcleo. | Alta | Alto | Usar a visão e o escopo como critérios de entrada; manter backlog futuro separado. |
| `VIS-RIS-009` | Métricas valorizarem volume e incentivarem cadastro de baixa qualidade. | Média | Médio | Equilibrar quantidade com recência, recorrência, dificuldade e qualidade das evidências. |
| `VIS-RIS-010` | Perda ou corrupção do histórico reduzir a confiança no produto. | Baixa/média | Muito alto | Definir integridade, backup, restauração e exportação como requisitos não funcionais relevantes. |
| `VIS-RIS-011` | A hierarquia fixa não representar todos os conteúdos. | Média | Médio | Validar com casos reais e permitir adaptação futura sem abandonar a hierarquia principal. |
| `VIS-RIS-012` | O usuário classificar incorretamente a causa de um erro. | Média/alta | Médio | Fornecer definições, exemplos e possibilidade de corrigir a classificação com rastreabilidade. |

---

## 22. Sugestões de melhoria para orientar as próximas etapas

### 22.1 Definir um cadastro em duas velocidades

Na Etapa 3, recomenda-se avaliar um **registro rápido** com os dados indispensáveis e um **enriquecimento posterior** para explicação, pegadinha e metadados adicionais. Isso enfrenta o risco de alto atrito sem eliminar profundidade.

### 22.2 Tratar confiança da métrica separadamente do valor de domínio

Um domínio de 80% baseado em duas tentativas não possui o mesmo peso que 80% baseado em dezenas de tentativas recentes. Recomenda-se estudar, na Etapa 5, uma indicação separada de suficiência ou confiança dos dados, em vez de distorcer silenciosamente a pontuação.

### 22.3 Versionar regras de cálculo

Se a fórmula de domínio ou o algoritmo de revisão mudar, o sistema deverá saber qual regra produziu cada resultado relevante. Essa necessidade deve aparecer nas regras de negócio, no SDD e no modelo de dados.

### 22.4 Evitar que “dominado” signifique “encerrado para sempre”

Uma questão ou assunto pode voltar a apresentar erros. Recomenda-se que domínio seja um estado reversível e que a futura regra considere recência, novas tentativas e reabertura.

### 22.5 Validar o núcleo com dados reais antes de introduzir IA

Um período de uso real ajudará a descobrir quais campos são utilizados, quais revisões acumulam e quais indicadores mudam decisões. Esses dados deverão orientar a automação futura.

---

## 23. Itens que precisam de aprovação

Para congelar a Etapa 1, o responsável pelo produto deverá aprovar ou solicitar ajustes nos itens abaixo:

1. **Declaração de visão e missão** apresentadas nas seções 2.2 e 2.3.
2. **Público primário individual**, com foco em estudantes que resolvem questões.
3. **Proposta de valor** baseada no ciclo questão → tentativa → erro → aprendizagem → revisão → análise.
4. **Objetivos principais e secundários** das seções 8 e 9.
5. **Não objetivos**, especialmente a exclusão inicial de gestão institucional, produtividade geral e IA obrigatória.
6. **Princípios do produto**, incluindo histórico preservado, métricas explicáveis e separação entre questão e tentativa.
7. **Premissas e restrições iniciais**, principalmente a revisão de 1, 7, 14 e 30 dias e a independência de integrações.
8. **Critérios gerais de sucesso**, mantendo metas numéricas para validação posterior.
9. **Visão de evolução futura**, sem compromisso imediato de implementação.
10. **Decisões `VIS-DEC-001` a `VIS-DEC-012`** como base congelada para a Etapa 2.
11. Manutenção dos **pontos em aberto `VIS-ABR-001` a `VIS-ABR-010`** para decisão nas etapas indicadas.

---

## 24. Critério de encerramento da Etapa 1

A Etapa 1 será considerada concluída quando:

- a visão, o problema, o público e a proposta de valor estiverem aprovados;
- os objetivos e não objetivos estiverem coerentes com o propósito central;
- princípios, premissas e restrições estiverem aceitos ou corrigidos;
- os riscos principais tiverem sido reconhecidos;
- os pontos em aberto estiverem registrados com etapa de resolução definida;
- as decisões aprovadas puderem ser tratadas como congeladas na elaboração da Etapa 2 — Escopo.

A etapa foi aprovada integralmente em 30 de agosto de 2026. As decisões `VIS-DEC-001` a `VIS-DEC-012` passam a ser consideradas congeladas e somente poderão ser alteradas mediante registro explícito da mudança e análise de impacto nas etapas posteriores.
