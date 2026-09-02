# Caderno de Erros Inteligente

## Etapa 4 — Requisitos Não Funcionais

| Campo | Valor |
|---|---|
| Documento | Especificação de Requisitos Não Funcionais |
| Projeto | Caderno de Erros Inteligente |
| Versão | 1.0 — aprovada |
| Data | 30 de agosto de 2026 |
| Status | Aprovada e congelada |
| Aprovação | Aprovada integralmente pelo responsável pelo produto em 30 de agosto de 2026 |
| Base congelada | Visão 1.0; Escopo 1.0; Requisitos Funcionais 1.0 |
| Próxima etapa após aprovação | Etapa 5 — Regras de Negócio |

---

## 1. Finalidade

Este documento define os atributos de qualidade e as restrições operacionais do Caderno de Erros Inteligente. Os RNFs descrevem **como o sistema deverá se comportar** quanto a desempenho, usabilidade, segurança, privacidade, confiabilidade, integridade, backup, portabilidade, acessibilidade, manutenção, escala, compatibilidade, observabilidade e testabilidade.

Cada requisito possui critério verificável. Valores numéricos representam metas iniciais de engenharia e deverão ser reavaliados com medições do protótipo, sem serem relaxados silenciosamente.

---

## 2. Convenções e baseline

### 2.1 Prioridades

| Prioridade | Significado |
|---|---|
| MVP — Crítico | Sem atendimento, dados, segurança ou ciclo central não são confiáveis. |
| MVP — Essencial | Obrigatório para liberar o MVP a uso real controlado. |
| MVP — Alta | Necessário para experiência adequada, podendo ser calibrado por medição. |
| V1 — Alta | Obrigatório para consolidação pública/contínua da V1. |
| V1 — Média | Melhoria desejável, ordenada pelo roadmap. |

### 2.2 Baseline de capacidade `BCR-1`

Os testes de qualidade do uso individual adotarão inicialmente:

- 10.000 questões entre ativas, arquivadas e rascunhos;
- 100.000 tentativas;
- 100.000 registros de revisão entre pendentes e concluídos;
- 200 disciplinas/assuntos/subassuntos ativos por nível combinado de uso;
- dez anos de datas históricas;
- um estudante por espaço de dados;
- ambiente de referência documentado no SDD.

Esse baseline não amplia o produto para escala institucional. Ele serve para evitar degradação precoce durante anos de uso pessoal.

### 2.3 Métodos de verificação

| Método | Significado |
|---|---|
| Teste automatizado | Execução repetível em pipeline ou ambiente local controlado. |
| Teste de carga | Medição com o `BCR-1` ou carga equivalente. |
| Inspeção | Revisão de configuração, código, documento ou interface. |
| Teste de usabilidade | Sessão com tarefas representativas e observação de conclusão. |
| Teste de segurança | Análise automatizada e validação manual dos controles relevantes. |
| Exercício operacional | Simulação de backup, restauração, falha ou incidente. |

---

## 3. Desempenho

### `RNF-001` — Tempo de carregamento das telas principais

- **Prioridade:** MVP — Alta.
- **Requisito:** Dashboard, lista de revisões e lista de questões deverão apresentar conteúdo utilizável em até 3 segundos no percentil 95, usando o `BCR-1` e o ambiente de referência.
- **Critério de aceitação:** Pelo menos 95% das medições ficam em até 3 s, sem erro e sem contagem inconsistente.
- **Verificação:** Teste automatizado de desempenho com cache frio e quente documentados separadamente.
- **Observação:** Tempo de rede externa será medido separadamente quando houver implantação remota.

### `RNF-002` — Tempo de resposta de consultas

- **Prioridade:** MVP — Alta.
- **Requisito:** Busca textual e aplicação de filtros básicos deverão responder em até 2 segundos no percentil 95 com o `BCR-1`.
- **Critério de aceitação:** 95% das buscas e filtros válidos concluem em até 2 s; nenhuma retorna registros de outro espaço.
- **Verificação:** Teste de carga sobre consultas representativas.
- **Observação:** Pesquisa semântica não integra o MVP.

### `RNF-003` — Confirmação de gravações críticas

- **Prioridade:** MVP — Crítico.
- **Requisito:** Registrar tentativa, concluir revisão ou salvar questão deverá receber confirmação de sucesso ou falha em até 2 segundos no percentil 95 no ambiente de referência.
- **Critério de aceitação:** Operação confirmada está persistida; falha não produz mensagem de sucesso.
- **Verificação:** Testes de integração e desempenho, incluindo falha simulada.
- **Observação:** A interface poderá usar estado de processamento, mas não confirmação otimista irreversível.

### `RNF-004` — Atualização do dashboard

- **Prioridade:** MVP — Alta.
- **Requisito:** Após operação que altere métricas, o painel deverá refletir os novos valores em até 3 segundos após confirmação, sem exigir reinício da aplicação.
- **Critério de aceitação:** Totais atualizados correspondem ao registro confirmado dentro do limite.
- **Verificação:** Teste funcional temporizado.
- **Observação:** Reprocessamentos extensos futuros poderão ser assíncronos se indicarem claramente o estado.

### `RNF-005` — Degradação controlada

- **Prioridade:** V1 — Alta.
- **Requisito:** Com até duas vezes o `BCR-1`, o sistema não deverá perder dados ou falhar silenciosamente; aumento de latência deverá ser mensurável e comunicado quando ultrapassar os limites.
- **Critério de aceitação:** Carga 2× não causa corrupção, duplicação nem encerramento inesperado; relatório registra a degradação.
- **Verificação:** Teste de estresse.
- **Observação:** Não constitui compromisso de escala institucional.

---

## 4. Usabilidade

### `RNF-006` — Conclusão do fluxo central

- **Prioridade:** MVP — Essencial.
- **Requisito:** Em teste moderado, pelo menos 90% dos participantes representativos deverão concluir sem ajuda os fluxos de cadastrar questão com tentativa incorreta e realizar revisão devida.
- **Critério de aceitação:** Taxa mínima de 90% em cada tarefa, com erros observados documentados.
- **Verificação:** Teste de usabilidade com roteiro padronizado.
- **Observação:** A amostra inicial poderá ser pequena, mas deverá ser registrada; resultados orientarão o roadmap.

### `RNF-007` — Cadastro sem perda por validação

- **Prioridade:** MVP — Essencial.
- **Requisito:** Um erro de validação não deverá apagar os demais campos preenchidos.
- **Critério de aceitação:** Após corrigir o campo inválido, todo conteúdo válido permanece disponível.
- **Verificação:** Testes de interface para cada validação importante.
- **Observação:** Fechamento voluntário sem salvar seguirá aviso definido no requisito seguinte.

### `RNF-008` — Proteção contra abandono acidental

- **Prioridade:** MVP — Alta.
- **Requisito:** Ao sair de formulário com alterações não salvas, o sistema deverá alertar o estudante ou preservar rascunho recuperável.
- **Critério de aceitação:** Navegação acidental não elimina conteúdo sem aviso ou recuperação.
- **Verificação:** Teste de interface em navegação, recarregamento e fechamento suportado.
- **Observação:** Limitações do navegador deverão ser documentadas.

### `RNF-009` — Clareza terminológica

- **Prioridade:** MVP — Essencial.
- **Requisito:** A interface deverá distinguir questão, questão realizada, tentativa, revisão, ciclo concluído e domínio.
- **Critério de aceitação:** Nenhum indicador usa termos incompatíveis; glossário ou ajuda contextual está disponível.
- **Verificação:** Inspeção de conteúdo e teste de compreensão.
- **Observação:** “Ciclo concluído” não poderá aparecer como sinônimo de “dominado”.

### `RNF-010` — Feedback de operação

- **Prioridade:** MVP — Essencial.
- **Requisito:** Toda ação de gravação deverá indicar processamento, sucesso ou falha com mensagem compreensível e próxima ao contexto.
- **Critério de aceitação:** O usuário consegue determinar se a operação foi concluída e qual ação tomar após falha.
- **Verificação:** Testes de interface com sucessos e erros simulados.
- **Observação:** Códigos técnicos poderão ser incluídos como referência secundária, não como mensagem principal.

### `RNF-011` — Eficiência do fluxo de revisão

- **Prioridade:** MVP — Alta.
- **Requisito:** Excluído o tempo de raciocínio, uma revisão correta deverá poder ser aberta, respondida e concluída sem navegação por páginas não relacionadas.
- **Critério de aceitação:** O fluxo ocorre em uma sequência contínua e retorna à fila ou ao próximo estado claro.
- **Verificação:** Inspeção do fluxo e teste de usabilidade.
- **Observação:** Não se fixa número absoluto de cliques antes do protótipo, mas cada etapa deverá ter finalidade necessária.

---

## 5. Segurança

### `RNF-012` — Autenticação condicionada à exposição

- **Prioridade:** MVP — Crítico.
- **Requisito:** Se o sistema puder ser acessado por rede ou internet, deverá exigir autenticação antes de disponibilizar dados; instalação estritamente local poderá operar com perfil único.
- **Critério de aceitação:** Implantação remota não expõe tela ou endpoint de dados sem sessão válida.
- **Verificação:** Teste de acesso não autenticado e inspeção de implantação.
- **Observação:** O SDD decidirá o mecanismo; a exceção local deverá ser explícita.

### `RNF-013` — Isolamento e autorização

- **Prioridade:** MVP — Crítico.
- **Requisito:** Toda leitura e escrita deverá ser autorizada para o espaço atual, independentemente de identificadores enviados pelo cliente.
- **Critério de aceitação:** Alterar um identificador não permite acessar ou modificar dados de outro espaço.
- **Verificação:** Testes negativos de autorização em todas as operações protegidas.
- **Observação:** Mesmo um produto individual deverá preservar essa fronteira quando hospedado.

### `RNF-014` — Proteção da comunicação

- **Prioridade:** MVP — Crítico quando remoto.
- **Requisito:** Dados transmitidos por rede não local deverão usar canal criptografado e configuração segura.
- **Critério de aceitação:** Acesso inseguro é bloqueado ou redirecionado; nenhum dado sensível trafega em texto aberto.
- **Verificação:** Inspeção de implantação e teste de protocolo.
- **Observação:** Não aplicável a processo estritamente local sem tráfego de rede.

### `RNF-015` — Armazenamento seguro de credenciais

- **Prioridade:** MVP — Crítico quando houver senha.
- **Requisito:** Senhas nunca deverão ser armazenadas em texto simples ou reversível; deverão usar função de derivação resistente e salt individual.
- **Critério de aceitação:** Base e logs não contêm senha; verificação usa hash adequado configurado no SDD.
- **Verificação:** Inspeção de código, configuração e armazenamento.
- **Observação:** Preferência por provedor de identidade pode eliminar armazenamento local de senhas.

### `RNF-016` — Validação de entrada e saída

- **Prioridade:** MVP — Crítico.
- **Requisito:** Entradas deverão ser validadas no servidor ou camada de domínio, e conteúdo exibido deverá ser tratado contra execução indevida.
- **Critério de aceitação:** Casos de injeção, scripts e payloads malformados não executam comandos, não alteram consultas e não quebram a interface.
- **Verificação:** Testes automatizados e teste de segurança direcionado.
- **Observação:** Validação apenas no navegador é insuficiente.

### `RNF-017` — Proteção contra requisições indevidas

- **Prioridade:** MVP — Crítico quando remoto.
- **Requisito:** Operações de alteração deverão resistir a falsificação de requisição, repetição não intencional e reenvio fora de contexto.
- **Critério de aceitação:** Requisição sem contexto/autorização válida é rejeitada; conclusão repetida não duplica tentativa.
- **Verificação:** Testes de segurança e idempotência.
- **Observação:** Controles específicos serão escolhidos conforme arquitetura.

### `RNF-018` — Gestão de segredos

- **Prioridade:** MVP — Crítico.
- **Requisito:** Chaves, tokens, senhas e credenciais não deverão ficar no código-fonte, arquivos versionados, mensagens de erro ou logs.
- **Critério de aceitação:** Varredura do repositório e dos logs não encontra segredos reais.
- **Verificação:** Inspeção e análise automatizada.
- **Observação:** Configuração local sensível deverá ter instrução segura.

### `RNF-019` — Dependências e vulnerabilidades

- **Prioridade:** MVP — Alta.
- **Requisito:** Dependências deverão ser inventariadas, fixadas de forma reproduzível e verificadas quanto a vulnerabilidades conhecidas antes de cada entrega.
- **Critério de aceitação:** Nenhuma vulnerabilidade crítica conhecida permanece sem correção, mitigação documentada ou bloqueio da entrega.
- **Verificação:** Análise automatizada e revisão do relatório.
- **Observação:** Critérios para severidades inferiores serão definidos no processo de manutenção.

---

## 6. Privacidade

### `RNF-020` — Minimização de dados pessoais

- **Prioridade:** MVP — Essencial.
- **Requisito:** O sistema deverá coletar apenas dados necessários ao espaço individual, segurança e funcionamento aprovado.
- **Critério de aceitação:** Cada dado pessoal coletado possui finalidade documentada; campos desnecessários não são obrigatórios.
- **Verificação:** Inspeção de modelo, formulários e documentação.
- **Observação:** O conteúdo de estudo pode revelar interesses e desempenho e será tratado como dado privado.

### `RNF-021` — Não transmissão externa por padrão

- **Prioridade:** MVP — Crítico.
- **Requisito:** Enunciados, respostas, erros e métricas não deverão ser enviados a IA, analytics ou terceiros sem capacidade aprovada e consentimento explícito.
- **Critério de aceitação:** Tráfego do MVP não contém conteúdo de estudo destinado a serviços não essenciais.
- **Verificação:** Inspeção de rede, código e configuração.
- **Observação:** Integrações estão fora do MVP.

### `RNF-022` — Conteúdo fora de logs

- **Prioridade:** MVP — Crítico.
- **Requisito:** Logs operacionais não deverão registrar integralmente enunciados, alternativas, respostas, explicações ou pegadinhas.
- **Critério de aceitação:** Logs usam identificadores e metadados mínimos; amostragem confirma ausência de conteúdo.
- **Verificação:** Inspeção e testes de erro.
- **Observação:** Trechos somente poderão ser incluídos em diagnóstico explícito, controlado e removível.

### `RNF-023` — Transparência de tratamento

- **Prioridade:** V1 — Alta; versão mínima no MVP remoto.
- **Requisito:** O usuário deverá receber informação clara sobre dados coletados, armazenamento, backup, retenção, exportação e exclusão.
- **Critério de aceitação:** Documento acessível corresponde ao comportamento real da versão.
- **Verificação:** Inspeção de produto e configuração.
- **Observação:** Não serão feitas promessas incompatíveis com a implantação escolhida.

### `RNF-024` — Controle e portabilidade do titular

- **Prioridade:** V1 — Alta.
- **Requisito:** O estudante deverá poder exportar e solicitar exclusão de seus dados conforme regras aprovadas, sem formato deliberadamente bloqueador.
- **Critério de aceitação:** Exportação é legível e exclusão informa consequências; dados retidos por integridade são explicados.
- **Verificação:** Testes funcionais de exportação e exclusão.
- **Observação:** Detalhes legais serão avaliados antes de oferta pública.

---

## 7. Confiabilidade e integridade dos dados

### `RNF-025` — Atomicidade da conclusão de revisão

- **Prioridade:** MVP — Crítico.
- **Requisito:** Concluir revisão, criar tentativa, atualizar etapa e invalidar pendência anterior deverá ocorrer integralmente ou não ocorrer.
- **Critério de aceitação:** Falha em qualquer parte não deixa revisão concluída sem tentativa nem duas etapas ativas indevidas.
- **Verificação:** Testes de integração com falhas injetadas.
- **Observação:** Implementação será definida no SDD.

### `RNF-026` — Idempotência das operações críticas

- **Prioridade:** MVP — Crítico.
- **Requisito:** Repetir uma solicitação de conclusão ou criação devido a clique duplo, retry ou rede instável não deverá duplicar efeitos.
- **Critério de aceitação:** A mesma operação lógica gera no máximo um resultado válido.
- **Verificação:** Testes concorrentes e de repetição.
- **Observação:** Abrange especialmente `RF-024`, `RF-034` e `RF-043`.

### `RNF-027` — Integridade referencial

- **Prioridade:** MVP — Crítico.
- **Requisito:** Não deverão existir tentativa sem questão, revisão sem ciclo/questão ou subassunto fora de assunto e disciplina válidos.
- **Critério de aceitação:** Restrições e serviços rejeitam referências inválidas; verificação do `BCR-1` encontra zero órfãos.
- **Verificação:** Testes de banco, integração e auditoria de consistência.
- **Observação:** Arquivamento preserva referências.

### `RNF-028` — Preservação histórica

- **Prioridade:** MVP — Crítico.
- **Requisito:** Nova tentativa ou revisão não deverá sobrescrever eventos anteriores.
- **Critério de aceitação:** Linha do tempo mantém todos os eventos válidos após múltiplas revisões.
- **Verificação:** Teste funcional e inspeção de persistência.
- **Observação:** Correções da V1 usam anulação/substituição.

### `RNF-029` — Consistência das métricas

- **Prioridade:** MVP — Crítico.
- **Requisito:** Métricas deverão ser reproduzíveis a partir dos registros válidos e da regra identificada.
- **Critério de aceitação:** Recálculo independente produz os mesmos valores, dentro da precisão definida.
- **Verificação:** Testes automatizados com conjuntos conhecidos.
- **Observação:** Cache não poderá ser fonte autoritativa divergente.

### `RNF-030` — Tratamento correto do tempo

- **Prioridade:** MVP — Crítico.
- **Requisito:** Instantes históricos deverão ser preservados e datas de calendário calculadas usando fuso identificável.
- **Critério de aceitação:** Casos de virada do dia, mudança de fuso e horário de verão produzem resultado definido e testado.
- **Verificação:** Testes automatizados com relógio controlado.
- **Observação:** Regras exatas serão congeladas na Etapa 5.

### `RNF-031` — Prevenção de atualização perdida

- **Prioridade:** MVP — Alta.
- **Requisito:** Duas alterações concorrentes do mesmo registro não deverão sobrescrever uma à outra silenciosamente.
- **Critério de aceitação:** Conflito é detectado ou serializado; usuário recebe estado atual e opção segura.
- **Verificação:** Teste de concorrência.
- **Observação:** Mesmo uso individual pode ter abas ou requisições simultâneas.

### `RNF-032` — Erro sem confirmação falsa

- **Prioridade:** MVP — Crítico.
- **Requisito:** Nenhuma operação falha deverá ser apresentada como salva ou concluída.
- **Critério de aceitação:** Falha de armazenamento, validação ou conexão resulta em estado de erro e mantém opção segura de repetição.
- **Verificação:** Testes com falha simulada.
- **Observação:** Relaciona-se a `RNF-010` e `RNF-026`.

### `RNF-033` — Migrações seguras

- **Prioridade:** V1 — Alta; necessária antes de qualquer alteração de esquema no MVP.
- **Requisito:** Mudanças no armazenamento deverão ser versionadas, testadas com cópia e possuir estratégia de retorno ou restauração.
- **Critério de aceitação:** Migração preserva contagens, vínculos e histórico; falha não destrói a versão recuperável.
- **Verificação:** Teste automatizado de migração e exercício de rollback/restauração.
- **Observação:** Migração destrutiva exige backup verificado.

---

## 8. Backup e recuperação

### `RNF-034` — Cobertura do backup

- **Prioridade:** MVP — Crítico.
- **Requisito:** O backup deverá incluir todos os dados necessários para reconstruir hierarquia, questões, tentativas, erros, ciclos, revisões, configurações e versões de regras relevantes.
- **Critério de aceitação:** Restauração não depende de recriar manualmente vínculos ou datas.
- **Verificação:** Exercício de backup e restauração.
- **Observação:** Logs transitórios e caches não precisam integrar o backup.

### `RNF-035` — Objetivos de recuperação

- **Prioridade:** MVP — Alta para piloto com dados reais.
- **Requisito:** O ambiente de validação deverá atingir RPO máximo de 24 horas e RTO máximo de 4 horas.
- **Critério de aceitação:** Exercício documentado comprova perda máxima de até 24 h e restauração operacional em até 4 h.
- **Verificação:** Simulação operacional temporizada.
- **Observação:** Metas poderão ser reduzidas na V1 hospedada, nunca ampliadas sem aprovação.

### `RNF-036` — Integridade do arquivo de backup

- **Prioridade:** MVP — Crítico.
- **Requisito:** Backups deverão possuir verificação de integridade e não ser considerados válidos apenas porque o arquivo existe.
- **Critério de aceitação:** Arquivo corrompido é detectado antes de substituir dados; backup válido passa por verificação.
- **Verificação:** Teste com arquivo íntegro e corrompido.
- **Observação:** Mecanismo exato será definido no SDD.

### `RNF-037` — Proteção e retenção de backups

- **Prioridade:** MVP — Alta.
- **Requisito:** Backup contendo dados privados deverá possuir acesso restrito e, quando armazenado fora do dispositivo protegido, criptografia; a retenção inicial deverá manter ao menos sete versões diárias e quatro semanais durante piloto contínuo.
- **Critério de aceitação:** Pessoas/processos não autorizados não acessam o conteúdo e a política de retenção é verificável.
- **Verificação:** Inspeção de armazenamento e exercício de restauração de versão anterior.
- **Observação:** A política poderá ser adaptada à implantação, preservando RPO/RTO.

### `RNF-038` — Teste periódico de restauração

- **Prioridade:** MVP — Crítico.
- **Requisito:** Antes do uso real e após mudanças relevantes de esquema, deverá ser executada restauração em ambiente isolado.
- **Critério de aceitação:** Relatório confirma abertura de questões, histórico e pendências sem inconsistência.
- **Verificação:** Exercício operacional.
- **Observação:** Backup nunca restaurado será considerado não validado.

### `RNF-039` — Backup e restauração pela interface

- **Prioridade:** V1 — Alta.
- **Requisito:** O fluxo de usuário deverá validar formato, versão, pertencimento e integridade antes de restaurar, com confirmação reforçada e resultado auditável.
- **Critério de aceitação:** Arquivo inválido não altera dados; sucesso apresenta resumo reconciliável.
- **Verificação:** Testes funcionais e de segurança.
- **Observação:** Implementa `RF-070`.

---

## 9. Portabilidade

### `RNF-040` — Formato aberto de exportação

- **Prioridade:** V1 — Alta.
- **Requisito:** A exportação deverá usar formato aberto, documentado, codificado em UTF-8 e independente do banco de dados interno.
- **Critério de aceitação:** Ferramenta comum consegue ler o arquivo; documentação descreve campos, relações e ausências.
- **Verificação:** Inspeção e teste com leitor independente.
- **Observação:** JSON estruturado poderá ser combinado com CSVs de consulta; decisão final no SDD/modelo de dados.

### `RNF-041` — Versionamento do formato

- **Prioridade:** V1 — Alta.
- **Requisito:** Todo arquivo exportado ou de backup deverá identificar versão do esquema e data de geração.
- **Critério de aceitação:** Importador/restaurador reconhece versão compatível e rejeita versão desconhecida com mensagem clara.
- **Verificação:** Testes entre versões.
- **Observação:** Migração deverá ser explícita.

### `RNF-042` — Completude e reconciliação da exportação

- **Prioridade:** V1 — Alta.
- **Requisito:** A exportação deverá permitir reconciliar quantidades de questões, tentativas, revisões e classificações com o sistema.
- **Critério de aceitação:** Totais exportados coincidem com a origem e relações são reconstruíveis.
- **Verificação:** Teste automatizado sobre conjunto conhecido e `BCR-1` reduzido.
- **Observação:** Dados derivados poderão ser recalculados se a regra/versionamento estiver presente.

### `RNF-043` — Ausência de bloqueio proprietário

- **Prioridade:** V1 — Alta.
- **Requisito:** Dados do estudante não deverão ficar acessíveis somente por formato binário proprietário não documentado.
- **Critério de aceitação:** Conteúdo principal pode ser lido e transformado sem depender da aplicação original.
- **Verificação:** Inspeção da exportação.
- **Observação:** Não obriga importação universal por outros produtos.

---

## 10. Acessibilidade

### `RNF-044` — Conformidade de acessibilidade

- **Prioridade:** MVP — Alta; conformidade integral até a V1.
- **Requisito:** Fluxos centrais deverão buscar conformidade WCAG 2.2 nível AA, com desvios registrados e corrigidos antes da V1.
- **Critério de aceitação:** Auditoria automatizada e manual não encontra falha crítica nos fluxos de cadastro, revisão, lista e dashboard.
- **Verificação:** Ferramentas automáticas e inspeção manual.
- **Observação:** Aprovação automática isolada não comprova conformidade.

### `RNF-045` — Operação por teclado

- **Prioridade:** MVP — Essencial.
- **Requisito:** Todas as funções centrais deverão ser executáveis por teclado, com ordem de foco lógica e foco visível.
- **Critério de aceitação:** Cadastro e revisão são concluídos sem mouse; nenhum foco fica preso indevidamente.
- **Verificação:** Teste manual por teclado.
- **Observação:** Atalhos adicionais são opcionais.

### `RNF-046` — Rótulos e mensagens acessíveis

- **Prioridade:** MVP — Essencial.
- **Requisito:** Campos, botões, erros e estados deverão possuir nomes programáticos e associação clara.
- **Critério de aceitação:** Leitor de tela anuncia rótulo, obrigatoriedade, erro e instrução relevante.
- **Verificação:** Inspeção semântica e teste com leitor de tela.
- **Observação:** Placeholder não substituirá rótulo.

### `RNF-047` — Contraste e uso de cor

- **Prioridade:** MVP — Essencial.
- **Requisito:** Texto e controles deverão atender contraste AA aplicável, e nenhum estado dependerá apenas de cor.
- **Critério de aceitação:** Acerto, erro, atraso e foco continuam distinguíveis sem percepção de cor.
- **Verificação:** Medição de contraste e inspeção visual.
- **Observação:** Ícone e texto deverão complementar cores de status.

### `RNF-048` — Redimensionamento e zoom

- **Prioridade:** MVP — Alta.
- **Requisito:** Conteúdo deverá permanecer utilizável com zoom de 200% sem perda de função ou rolagem horizontal desnecessária em texto principal.
- **Critério de aceitação:** Fluxos centrais continuam completos a 200% em viewport de referência.
- **Verificação:** Teste manual e visual.
- **Observação:** Tabelas extensas poderão ter solução responsiva específica.

### `RNF-049` — Semântica e leitor de tela

- **Prioridade:** V1 — Alta; baseline no MVP.
- **Requisito:** Cabeçalhos, regiões, listas, tabelas e atualizações dinâmicas deverão usar semântica compatível com tecnologias assistivas.
- **Critério de aceitação:** Estrutura pode ser navegada e atualizações importantes são anunciadas sem repetição excessiva.
- **Verificação:** Teste com leitor de tela e inspeção de acessibilidade.
- **Observação:** Gráficos deverão possuir alternativa textual ou tabular.

### `RNF-050` — Movimento e tempo de interação

- **Prioridade:** V1 — Média.
- **Requisito:** Animações não essenciais deverão respeitar preferência de movimento reduzido; operações não deverão expirar durante leitura normal sem aviso.
- **Critério de aceitação:** Preferência reduz animação e nenhum formulário perde dados por limite curto invisível.
- **Verificação:** Teste de preferências e sessão.
- **Observação:** Segurança de sessão remota poderá exigir expiração com aviso.

---

## 11. Manutenibilidade

### `RNF-051` — Separação de responsabilidades

- **Prioridade:** MVP — Essencial.
- **Requisito:** Código deverá separar interface, regras de domínio, persistência e integrações técnicas, evitando cálculo crítico apenas na camada visual.
- **Critério de aceitação:** Regras de revisão e métricas podem ser testadas sem iniciar a interface completa.
- **Verificação:** Revisão arquitetural e testes.
- **Observação:** O SDD definirá a arquitetura concreta.

### `RNF-052` — Padrão de código automatizado

- **Prioridade:** MVP — Alta.
- **Requisito:** Formatação, análise estática e lint deverão executar por comando documentado e bloquear erros definidos como críticos.
- **Critério de aceitação:** Pipeline local/CI reproduz o resultado e a base aprovada não contém erro bloqueante.
- **Verificação:** Execução automatizada.
- **Observação:** Ferramentas dependem da stack.

### `RNF-053` — Documentação de desenvolvimento

- **Prioridade:** MVP — Essencial.
- **Requisito:** O repositório deverá documentar instalação, configuração, execução, testes, migrações, backup e solução de falhas comuns.
- **Critério de aceitação:** Um ambiente limpo pode ser preparado seguindo somente a documentação e pré-requisitos indicados.
- **Verificação:** Exercício de onboarding técnico.
- **Observação:** Segredos reais não integrarão exemplos.

### `RNF-054` — Configuração fora do código

- **Prioridade:** MVP — Alta.
- **Requisito:** Valores dependentes de ambiente, como conexão, modo de implantação e logging, deverão ser configuráveis sem editar regras de domínio.
- **Critério de aceitação:** Ambientes de desenvolvimento e teste usam configurações distintas sem mudança no código-fonte.
- **Verificação:** Inspeção e execução.
- **Observação:** Regras de negócio versionadas não serão tratadas como configuração arbitrária.

### `RNF-055` — Versionamento de regras críticas

- **Prioridade:** MVP — Alta para revisão; V1 — Crítico para domínio.
- **Requisito:** Algoritmos de revisão, métricas e domínio deverão possuir identificação de versão quando uma mudança puder alterar resultados históricos.
- **Critério de aceitação:** É possível determinar qual regra produziu data ou índice relevante.
- **Verificação:** Inspeção de dados e testes de migração.
- **Observação:** Não exige manter indefinidamente código obsoleto, mas exige rastreabilidade.

### `RNF-056` — Dependências reproduzíveis

- **Prioridade:** MVP — Alta.
- **Requisito:** Versões diretas e transitivas necessárias à construção deverão ser travadas ou resolvidas de forma reproduzível.
- **Critério de aceitação:** Duas instalações a partir da mesma revisão produzem conjunto equivalente de dependências.
- **Verificação:** Construção limpa repetida.
- **Observação:** Atualizações serão intencionais e testadas.

### `RNF-057` — Evolução de esquema compatível

- **Prioridade:** V1 — Alta.
- **Requisito:** Mudanças no modelo deverão usar migrações ordenadas, identificadas e testadas desde a versão anterior suportada.
- **Critério de aceitação:** Atualização preserva histórico e permite diagnóstico da versão aplicada.
- **Verificação:** Testes de migração.
- **Observação:** Relaciona-se a `RNF-033`.

### `RNF-058` — Rastreabilidade documental

- **Prioridade:** MVP — Essencial.
- **Requisito:** Requisitos, regras, componentes, entidades e casos de teste deverão referenciar IDs relacionados.
- **Critério de aceitação:** Requisito crítico pode ser rastreado até teste; regra de negócio aponta requisitos afetados.
- **Verificação:** Inspeção da matriz de rastreabilidade.
- **Observação:** Alteração aprovada deverá atualizar os artefatos impactados.

---

## 12. Escalabilidade

### `RNF-059` — Suporte ao baseline pessoal

- **Prioridade:** MVP — Essencial.
- **Requisito:** O sistema deverá operar corretamente com o `BCR-1` sem exigir arquivamento forçado ou perda de histórico.
- **Critério de aceitação:** Fluxos principais passam nos limites de desempenho e integridade usando o baseline.
- **Verificação:** Teste de carga e regressão.
- **Observação:** Índices e estratégias serão definidos no SDD/modelo de dados.

### `RNF-060` — Crescimento sem recálculo integral síncrono

- **Prioridade:** V1 — Alta.
- **Requisito:** Operações comuns não deverão recalcular todo o histórico quando apenas um subconjunto de métricas é afetado, se isso romper limites de desempenho.
- **Critério de aceitação:** Inserir tentativa no `BCR-1` respeita `RNF-003` e atualiza agregados necessários.
- **Verificação:** Perfil de desempenho.
- **Observação:** Otimização prematura não deverá sacrificar correção.

### `RNF-061` — Paginação ou carregamento limitado

- **Prioridade:** MVP — Alta.
- **Requisito:** Listas extensas não deverão carregar todos os registros simultaneamente no cliente.
- **Critério de aceitação:** Listar 10.000 questões mantém tempo e memória dentro do ambiente de referência.
- **Verificação:** Teste de carga de interface.
- **Observação:** Tamanho de página será definido no SDD.

### `RNF-062` — Limite institucional explícito

- **Prioridade:** MVP — Essencial.
- **Requisito:** Nenhuma decisão de infraestrutura do MVP será obrigada a suportar turmas, organizações ou acesso massivo simultâneo.
- **Critério de aceitação:** Documentação de capacidade distingue claramente escala pessoal de institucional.
- **Verificação:** Inspeção do SDD e testes.
- **Observação:** Mudança de público exige revisão de escopo e RNFs.

---

## 13. Compatibilidade e responsividade

### `RNF-063` — Navegadores desktop do MVP

- **Prioridade:** MVP — Essencial.
- **Requisito:** Fluxos centrais deverão funcionar nas versões estáveis vigentes de Chrome e Edge em Windows 11 no momento da entrega.
- **Critério de aceitação:** Suite funcional crítica passa em ambos sem bloqueio visual ou de dados.
- **Verificação:** Testes automatizados e manuais.
- **Observação:** Versões exatas serão registradas em cada entrega.

### `RNF-064` — Compatibilidade ampliada da V1

- **Prioridade:** V1 — Alta.
- **Requisito:** A V1 deverá suportar também versões estáveis vigentes e imediatamente anteriores de Firefox e Safari, quando tecnicamente aplicável.
- **Critério de aceitação:** Fluxos centrais passam na matriz publicada de navegadores.
- **Verificação:** Testes cruzados.
- **Observação:** Exceções deverão ser documentadas antes da entrega.

### `RNF-065` — Layout responsivo

- **Prioridade:** MVP — Essencial.
- **Requisito:** A interface deverá permanecer funcional entre 360 e 1920 pixels de largura, priorizando cadastro em desktop e revisão em tela móvel.
- **Critério de aceitação:** Não há perda de campos, botões inacessíveis ou sobreposição nos fluxos centrais.
- **Verificação:** Testes visuais e funcionais em viewports representativos.
- **Observação:** Responsivo não significa aplicativo nativo nem offline.

### `RNF-066` — Português e Unicode

- **Prioridade:** MVP — Essencial.
- **Requisito:** O produto inicial deverá usar português do Brasil e preservar acentos, símbolos e caracteres Unicode nos dados de estudo.
- **Critério de aceitação:** Textos como “questão”, fórmulas digitadas e nomes acentuados são salvos, buscados e exportados sem corrupção.
- **Verificação:** Testes de codificação e interface.
- **Observação:** Internacionalização completa fica fora do MVP.

### `RNF-067` — Fusos horários padronizados

- **Prioridade:** MVP — Crítico.
- **Requisito:** Fusos deverão usar identificadores padronizados com regras históricas, evitando apenas deslocamentos fixos quando houver horário de verão.
- **Critério de aceitação:** Datas são reproduzíveis em testes com diferentes zonas e transições.
- **Verificação:** Testes temporais automatizados.
- **Observação:** O mecanismo técnico será escolhido no SDD.

---

## 14. Observabilidade

### `RNF-068` — Logs estruturados

- **Prioridade:** MVP — Essencial.
- **Requisito:** Operações críticas e falhas deverão produzir logs estruturados com nível, horário, evento e identificador de correlação.
- **Critério de aceitação:** Uma falha de conclusão de revisão pode ser localizada sem expor conteúdo privado.
- **Verificação:** Inspeção dos logs em cenários simulados.
- **Observação:** Aplica `RNF-022`.

### `RNF-069` — Correlação de operações

- **Prioridade:** MVP — Alta.
- **Requisito:** Requisições e etapas de uma operação crítica deverão compartilhar identificador que permita acompanhar seu percurso.
- **Critério de aceitação:** É possível relacionar entrada, tentativa de gravação e erro/sucesso sem usar dados do enunciado.
- **Verificação:** Teste de diagnóstico.
- **Observação:** Formato depende da arquitetura.

### `RNF-070` — Registro de eventos críticos

- **Prioridade:** MVP — Alta; ampliado na V1.
- **Requisito:** Criação de ciclo, conclusão de revisão, falha de backup, restauração e migração deverão ser eventos diagnosticáveis.
- **Critério de aceitação:** Cada evento informa resultado e objeto técnico mínimo.
- **Verificação:** Inspeção e testes de integração.
- **Observação:** Auditoria funcional da V1 é coberta por `RF-071`.

### `RNF-071` — Métricas operacionais

- **Prioridade:** V1 — Alta para implantação remota.
- **Requisito:** O ambiente deverá medir latência, taxa de erro, falhas de gravação, sucesso de backup e uso de recursos sem coletar conteúdo de estudo.
- **Critério de aceitação:** Painel técnico ou relatório permite identificar violação dos limites críticos.
- **Verificação:** Simulação de carga e falha.
- **Observação:** Não se confunde com analytics comportamental.

### `RNF-072` — Verificação de saúde

- **Prioridade:** V1 — Alta quando remoto.
- **Requisito:** O serviço deverá expor verificação restrita de saúde e prontidão das dependências essenciais.
- **Critério de aceitação:** Falha de persistência impede sinal de prontidão saudável.
- **Verificação:** Teste operacional.
- **Observação:** Endpoint não deverá revelar configuração sensível.

### `RNF-073` — Alertas de falha crítica

- **Prioridade:** V1 — Alta quando remoto.
- **Requisito:** Falhas repetidas de gravação, backup, restauração ou disponibilidade deverão gerar alerta ao responsável técnico.
- **Critério de aceitação:** Cenário crítico simulado produz alerta único e acionável dentro da janela configurada.
- **Verificação:** Exercício operacional.
- **Observação:** Alertas ao estudante sobre revisão são outra funcionalidade e permanecem fora do MVP.

---

## 15. Testabilidade

### `RNF-074` — Relógio controlável em testes

- **Prioridade:** MVP — Crítico.
- **Requisito:** Regras dependentes de data/hora deverão receber fonte de tempo substituível em testes.
- **Critério de aceitação:** Testes reproduzem hoje, atraso, virada do dia e mudanças de fuso sem alterar o relógio real.
- **Verificação:** Inspeção de arquitetura e testes automatizados.
- **Observação:** Essencial para revisão espaçada.

### `RNF-075` — Regras de domínio testáveis isoladamente

- **Prioridade:** MVP — Crítico para revisão/estatística; V1 para domínio.
- **Requisito:** Cálculos de resultado, revisão, métricas e domínio deverão ser testáveis sem interface ou serviços externos.
- **Critério de aceitação:** Testes unitários recebem entradas explícitas e comparam saídas determinísticas.
- **Verificação:** Execução da suite.
- **Observação:** Reforça `RNF-051`.

### `RNF-076` — Cobertura das regras críticas

- **Prioridade:** MVP — Essencial.
- **Requisito:** Cada regra crítica deverá possuir casos automatizados positivos, negativos e de fronteira; módulos de domínio deverão atingir ao menos 80% de cobertura de linhas, sem usar a porcentagem como substituta da qualidade.
- **Critério de aceitação:** Relatório atende o limite e a matriz confirma casos críticos.
- **Verificação:** Cobertura automatizada e revisão dos testes.
- **Observação:** Código gerado e adaptadores triviais poderão ser excluídos justificadamente.

### `RNF-077` — Testes de integração do ciclo completo

- **Prioridade:** MVP — Crítico.
- **Requisito:** Deverá existir teste automatizado desde tentativa inicial incorreta até conclusão das revisões, histórico e atualização de métricas.
- **Critério de aceitação:** Cenário central e falhas de gravação passam em ambiente isolado reproduzível.
- **Verificação:** Suite de integração.
- **Observação:** Nenhuma etapa poderá ser simulada por alteração manual do banco.

### `RNF-078` — Dados de teste reproduzíveis

- **Prioridade:** MVP — Alta.
- **Requisito:** Fixtures e geradores deverão criar cenários conhecidos, incluindo `BCR-1`, sem usar dados reais do estudante.
- **Critério de aceitação:** Mesma semente gera conjunto equivalente e testes não contêm conteúdo privado real.
- **Verificação:** Execução repetida e inspeção.
- **Observação:** Dados volumosos poderão ser gerados sob demanda.

### `RNF-079` — Ambientes isolados

- **Prioridade:** MVP — Crítico.
- **Requisito:** Testes automatizados nunca deverão escrever no ambiente ou banco de dados de produção/uso real.
- **Critério de aceitação:** Configuração bloqueia conexão acidental e os testes usam recursos isolados descartáveis.
- **Verificação:** Inspeção de configuração e teste de proteção.
- **Observação:** Credenciais de produção não estarão disponíveis no pipeline de testes comum.

### `RNF-080` — Gate de regressão

- **Prioridade:** MVP — Essencial.
- **Requisito:** Antes de uma entrega, testes críticos, análise estática e validações de migração aplicáveis deverão passar por comando ou pipeline único documentado.
- **Critério de aceitação:** Falha bloqueante impede marcar a versão como pronta.
- **Verificação:** Execução do pipeline.
- **Observação:** Exceção exige registro, impacto e aprovação explícita.

---

## 16. Critérios gerais de liberação do MVP

O MVP não poderá ser liberado para uso real controlado se ocorrer qualquer uma das condições:

- possibilidade conhecida de concluir revisão sem tentativa;
- duplicação de tentativa por reenvio comum;
- acesso remoto sem autenticação e isolamento;
- senha ou segredo armazenado inadequadamente;
- conteúdo de estudo exposto em logs ou enviado a terceiros;
- ausência de backup recuperável;
- falha nos testes temporais críticos;
- métricas que não possam ser reconciliadas;
- perda de conteúdo após erro de validação;
- fluxo central impossível por teclado;
- regressão crítica conhecida sem decisão explícita.

---

## 17. Matriz MVP versus V1

| Categoria | MVP | V1 |
|---|---|---|
| Desempenho | Limites no `BCR-1`. | Estresse 2× e otimizações de agregação. |
| Segurança | Controles obrigatórios conforme exposição. | Operação remota consolidada e monitorada. |
| Privacidade | Minimização, isolamento e nenhum envio externo. | Controles completos de exportação/exclusão. |
| Backup | Procedimento técnico, RPO/RTO e restauração testada. | Backup/restauração pela interface. |
| Portabilidade | Estrutura preparada e sem perda interna. | Exportação aberta, versionada e reconciliável. |
| Acessibilidade | Fluxos centrais e baseline AA. | Conformidade integral e testes ampliados. |
| Observabilidade | Logs e diagnóstico local/servidor. | Métricas, health checks e alertas remotos. |
| Testabilidade | Relógio controlável, regras e ciclo automatizados. | Migrações, domínio e cenários operacionais ampliados. |

---

## 18. Rastreabilidade principal

| Origem | RNFs relacionados |
|---|---|
| `VIS-PRI-002` e `RF-043` — histórico e conclusão | `RNF-025` a `RNF-029` |
| `VIS-PRI-005` — métricas explicáveis | `RNF-029`, `RNF-055`, `RNF-075` |
| `VIS-PRI-009` — evolução rastreável | `RNF-033`, `RNF-041`, `RNF-055`, `RNF-057` |
| `VIS-PRI-011` — privacidade | `RNF-012` a `RNF-024` |
| `ESC-MVP-015` — integridade operacional | `RNF-003`, `RNF-025` a `RNF-039` |
| `RF-002` e `RF-035` — datas e fuso | `RNF-030`, `RNF-067`, `RNF-074` |
| `RF-047` a `RF-056` — dashboard | `RNF-001`, `RNF-004`, `RNF-029`, `RNF-060` |
| `RF-067` a `RF-071` — proteção dos dados | `RNF-034` a `RNF-043`, `RNF-068` a `RNF-073` |

---

## 19. Decisões propostas nesta etapa

| ID | Decisão proposta |
|---|---|
| `RNF-DEC-001` | O baseline pessoal `BCR-1` será 10 mil questões, 100 mil tentativas e 100 mil revisões. |
| `RNF-DEC-002` | Telas principais terão meta p95 de 3 s; busca/filtros, 2 s; gravações críticas, 2 s. |
| `RNF-DEC-003` | Uso remoto exigirá autenticação, autorização e canal criptografado; uso estritamente local poderá ter perfil único. |
| `RNF-DEC-004` | Conteúdo de estudo não será enviado a terceiros nem incluído integralmente em logs no MVP. |
| `RNF-DEC-005` | Conclusão de revisão será atômica e idempotente. |
| `RNF-DEC-006` | O piloto com dados reais terá RPO máximo de 24 h e RTO máximo de 4 h. |
| `RNF-DEC-007` | Serão mantidas ao menos sete versões diárias e quatro semanais durante piloto contínuo, ajustáveis sem violar RPO/RTO. |
| `RNF-DEC-008` | O MVP deverá buscar WCAG 2.2 AA nos fluxos centrais; conformidade integral é meta da V1. |
| `RNF-DEC-009` | O ambiente primário do MVP será Chrome/Edge em Windows 11, com responsividade entre 360 e 1920 px. |
| `RNF-DEC-010` | Regras críticas usarão fonte de tempo controlável e testes automatizados isolados. |
| `RNF-DEC-011` | Domínio/regras de negócio terão cobertura mínima de linhas de 80%, além de casos críticos explícitos. |
| `RNF-DEC-012` | Nenhuma meta de escala institucional será imposta ao MVP. |

---

## 20. Pontos ainda em aberto

| ID | Ponto | Etapa de decisão |
|---|---|---|
| `RNF-ABR-001` | Hardware e configuração exatos do ambiente de referência. | SDD e Plano de Testes. |
| `RNF-ABR-002` | Mecanismo de autenticação e sessão se houver hospedagem. | SDD. |
| `RNF-ABR-003` | Criptografia em repouso da base local versus proteção do sistema operacional. | SDD e análise de risco. |
| `RNF-ABR-004` | Ferramentas de segurança, acessibilidade e observabilidade. | SDD. |
| `RNF-ABR-005` | Política final de retenção após V1 pública. | Regras, SDD e operação. |
| `RNF-ABR-006` | Formato final de exportação e backup. | SDD e Modelo de Dados. |
| `RNF-ABR-007` | Matriz final de navegadores móveis. | Roadmap e Plano de Testes. |
| `RNF-ABR-008` | Meta de disponibilidade caso o sistema seja hospedado. | SDD e Roadmap. |
| `RNF-ABR-009` | Limites finais de texto e arquivo futuro. | Regras e Modelo de Dados. |
| `RNF-ABR-010` | Critérios de severidade para vulnerabilidades não críticas. | SDD e processo de manutenção. |

---

## 21. Riscos

| ID | Risco | Resposta proposta |
|---|---|---|
| `RNF-RIS-001` | Metas de desempenho serem medidas em hardware favorável demais. | Fixar ambiente de referência e publicar resultados com configuração. |
| `RNF-RIS-002` | Autenticação ser adiada apesar de implantação em rede. | Tratar exposição remota como gatilho obrigatório, não como melhoria futura. |
| `RNF-RIS-003` | Backup existir sem restauração válida. | Exigir exercício antes do piloto e após migrações. |
| `RNF-RIS-004` | Logs exporem enunciados ou respostas. | Proibir conteúdo por padrão e testar cenários de erro. |
| `RNF-RIS-005` | Cobertura de código criar falsa confiança. | Exigir casos críticos e de fronteira além do percentual. |
| `RNF-RIS-006` | Acessibilidade ser tratada somente no fim. | Inserir teclado, rótulos e contraste nos critérios do MVP. |
| `RNF-RIS-007` | Cache produzir métricas divergentes. | Manter registros como fonte autoritativa e testar reconciliação. |
| `RNF-RIS-008` | Mudança de fuso alterar revisões silenciosamente. | Preservar instantes/datas e exigir regras temporais versionadas. |
| `RNF-RIS-009` | Baseline alto levar a otimização prematura. | Priorizar correção; otimizar apenas quando testes mostrarem violação. |
| `RNF-RIS-010` | Escopo de navegadores aumentar custo do MVP. | Fixar Chrome/Edge no desktop e expandir a matriz na V1. |

---

## 22. Sugestões de melhoria

### 22.1 Criar um pacote de dados de referência

O `BCR-1` deverá ser gerado de forma determinística para medir busca, dashboard, migrações e restauração sempre sobre a mesma distribuição.

### 22.2 Executar teste de restauração antes do primeiro dado valioso

O momento correto para testar recuperação é antes do piloto real. A existência de uma cópia não comprova que o sistema consegue utilizá-la.

### 22.3 Automatizar verificações desde a V0.1

Lint, testes críticos, análise de dependências e verificação de segredos custam menos quando entram no início do repositório.

### 22.4 Medir experiência real antes de endurecer metas secundárias

Metas críticas de integridade e segurança não devem ser relaxadas; tempos de interface e objetivos de usabilidade podem ser calibrados com dados do protótipo.

### 22.5 Manter dois conjuntos de observabilidade

Logs técnicos devem diagnosticar falhas sem coletar conteúdo de estudo. Analytics de produto, se existir futuramente, precisará de decisão e consentimento separados.

---

## 23. Itens que precisam de aprovação

1. Os requisitos `RNF-001` a `RNF-080` e suas prioridades.
2. O baseline `BCR-1`.
3. As metas de desempenho p95.
4. Os gatilhos de segurança para implantação remota.
5. A política de não transmissão externa e de conteúdo fora dos logs.
6. Atomicidade, idempotência e integridade referencial como bloqueadores.
7. RPO de 24 h, RTO de 4 h e retenção inicial.
8. Baseline WCAG 2.2 AA e operação por teclado.
9. Matriz inicial de navegadores e dimensões responsivas.
10. Testes com relógio controlável e cobertura mínima do domínio.
11. Os bloqueadores gerais de liberação do MVP.
12. As decisões `RNF-DEC-001` a `RNF-DEC-012`.
13. A manutenção de `RNF-ABR-001` a `RNF-ABR-010` para as etapas indicadas.

---

## 24. Critério de encerramento

A Etapa 4 será concluída quando:

- todos os atributos de qualidade solicitados estiverem cobertos;
- requisitos críticos possuírem critérios verificáveis;
- MVP e V1 estiverem claramente separados;
- nenhum RNF exigir integração ou IA proibida no MVP;
- metas numéricas estiverem aprovadas ou substituídas explicitamente;
- pontos arquiteturais permanecerem encaminhados ao SDD;
- os RNFs puderem ser rastreados até testes e critérios de liberação.

A etapa foi aprovada integralmente em 30 de agosto de 2026. Os requisitos `RNF-001` a `RNF-080` e as decisões `RNF-DEC-001` a `RNF-DEC-012` passam a ser considerados congelados e somente poderão ser alterados mediante registro explícito e análise de impacto.
