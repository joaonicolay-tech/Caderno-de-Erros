# Documentação — Caderno de Erros Inteligente

Este diretório contém a documentação formal, as decisões arquiteturais e os registros de implementação do projeto **Caderno de Erros Inteligente**.

Este arquivo funciona como **índice operacional da documentação**.

Um agente não deve ler todos os documentos indiscriminadamente antes de cada tarefa. Deve primeiro consultar:

1. `../PROJECT_STATE.md`;
2. `../tasks/current.md`;
3. este índice;
4. somente os documentos relacionados ao escopo atual;
5. os ADRs aplicáveis.

As regras gerais de trabalho do repositório permanecem definidas em `../AGENTS.md`.

---

# 1. Documentação principal do produto

Os documentos das Etapas 1 a 10 formam a especificação principal do Caderno de Erros Inteligente.

Eles devem ser tratados como documentação formal aprovada, observadas as versões, erratas e decisões posteriores registradas nos ADRs.

## Etapa 1 — Visão do Projeto

**Arquivo:** `Caderno_de_Erros_Inteligente_Etapa_1_Visao_do_Projeto.md`

**Documento:** Visão do Projeto

**Finalidade:** define a visão geral que orienta o produto, incluindo:

* problema a ser resolvido;
* público-alvo;
* proposta de valor;
* missão;
* objetivos;
* princípios;
* premissas;
* restrições;
* não objetivos;
* critérios gerais de sucesso;
* direção de evolução futura.

### Consultar quando

Use este documento quando uma tarefa envolver:

* propósito do produto;
* interpretação dos objetivos gerais;
* dúvida sobre quem o sistema atende;
* discussão sobre uma funcionalidade estar alinhada à proposta do produto;
* avaliação de crescimento indevido do escopo;
* decisões que possam alterar princípios fundamentais do projeto.

Este documento é uma referência de alto nível. Ele não deve ser usado sozinho para decidir detalhes técnicos ou funcionais já definidos em documentos posteriores.

---

## Etapa 2 — Escopo

**Arquivo:** `Caderno_de_Erros_Inteligente_Etapa_2_Escopo.md`

**Documento:** Escopo do Produto e do MVP

**Finalidade:** transforma a visão aprovada em fronteiras explícitas de produto.

Define:

* o que pertence ao produto;
* o que pertence ao MVP;
* o que entra posteriormente até a V1;
* o que pertence a versões futuras;
* o que está explicitamente fora do escopo;
* dependências e limitações;
* responsabilidades do sistema e do usuário;
* critérios para evitar crescimento descontrolado.

### Consultar quando

Use este documento quando houver dúvida sobre:

* se uma funcionalidade pertence ao produto;
* se algo pode ser implementado na versão atual;
* MVP versus V1 versus Pós-V1;
* funcionalidades explicitamente excluídas;
* expansão de escopo;
* antecipação de recursos futuros.

O fato de uma capacidade existir na visão futura não autoriza sua implementação antecipada.

---

## Etapa 3 — Requisitos Funcionais

**Arquivo:** `Caderno_de_Erros_Inteligente_Etapa_3_Requisitos_Funcionais.md`

**Documento:** Especificação de Requisitos Funcionais

**Finalidade:** define **o que o sistema deve fazer** por meio de requisitos funcionais verificáveis e identificadores estáveis.

Os requisitos servem de base para rastreabilidade com:

* regras de negócio;
* arquitetura;
* modelo de dados;
* fluxos;
* testes.

### Consultar quando

Use este documento ao:

* implementar uma funcionalidade;
* modificar comportamento observável;
* criar ou alterar uma tela;
* criar operações de cadastro, edição, consulta ou arquivamento;
* definir critérios de aceite;
* criar testes funcionais;
* verificar se um comportamento está autorizado.

Sempre observe a fase do requisito antes de implementá-lo.

---

## Etapa 4 — Requisitos Não Funcionais

**Arquivo:** `Caderno_de_Erros_Inteligente_Etapa_4_Requisitos_Nao_Funcionais.md`

**Documento:** Especificação de Requisitos Não Funcionais

**Finalidade:** define **como o sistema deve se comportar** em atributos de qualidade e restrições operacionais.

Abrange:

* desempenho;
* usabilidade;
* segurança;
* privacidade;
* confiabilidade;
* integridade;
* backup;
* portabilidade;
* acessibilidade;
* manutenção;
* escala;
* compatibilidade;
* observabilidade;
* testabilidade.

### Consultar quando

Use este documento ao trabalhar com:

* segurança;
* privacidade;
* desempenho;
* acessibilidade;
* confiabilidade;
* backup/restauração;
* logs;
* navegadores suportados;
* ambientes;
* qualidade técnica;
* critérios não funcionais de teste ou liberação.

---

## Etapa 5 — Regras de Negócio

**Arquivo:** `Caderno_de_Erros_Inteligente_Etapa_5_Regras_de_Negocio.md`

**Documento:** Catálogo de Regras de Negócio

**Finalidade:** formaliza as regras que governam o comportamento do domínio.

As regras são independentes da tecnologia e devem ser aplicadas de maneira consistente pela:

* interface;
* camada de aplicação;
* domínio;
* persistência;
* importações futuras;
* testes.

### Consultar quando

Use este documento quando uma tarefa envolver:

* validações;
* estados;
* restrições do domínio;
* comportamento temporal;
* hierarquia acadêmica;
* questões;
* tentativas;
* erros;
* revisões;
* métricas;
* domínio;
* prioridade;
* histórico;
* arquivamento ou exclusão;
* cálculos e políticas versionadas.

Não recrie uma regra de negócio diretamente na interface quando ela já estiver formalizada neste documento ou encapsulada no domínio.

---

## Etapa 6 — SDD — Software Design Description

**Arquivo:** `Caderno_de_Erros_Inteligente_Etapa_6_SDD.md`

**Documento:** Descrição do Projeto de Software — SDD

**Finalidade:** define a arquitetura recomendada para implementar o sistema.

Descreve decisões e responsabilidades relacionadas a:

* arquitetura geral;
* módulos;
* camadas;
* serviços;
* selectors;
* persistência;
* transações;
* Django;
* SQLite;
* eventual gatilho para PostgreSQL;
* tratamento de erros;
* segurança;
* configuração;
* logging;
* integração entre componentes.

### Consultar quando

Use este documento antes de:

* criar um novo módulo;
* alterar responsabilidades entre camadas;
* criar ou modificar services/selectors;
* introduzir uma nova dependência arquitetural;
* alterar persistência;
* criar infraestrutura compartilhada;
* fazer refatoração estrutural;
* tomar uma nova decisão arquitetural.

Mudanças arquiteturais relevantes também devem respeitar os ADRs vigentes.

---

## Etapa 7 — Modelo de Dados

**Arquivo:** `Caderno_de_Erros_Inteligente_Etapa_7_Modelo_de_Dados.md`

**Documento:** Modelo Conceitual e Lógico de Dados

**Finalidade:** transforma requisitos, regras e arquitetura em um modelo de dados implementável.

Define:

* entidades;
* atributos;
* tipos;
* obrigatoriedade;
* relacionamentos;
* cardinalidades;
* restrições;
* índices;
* histórico;
* versionamento;
* exclusão;
* exportação;
* integridade entre entidades.

### Consultar quando

Use este documento ao:

* criar ou modificar models;
* criar migrations;
* alterar relacionamentos;
* adicionar constraints;
* definir índices;
* trabalhar com UUIDs;
* implementar histórico/versionamento;
* alterar integridade referencial;
* decidir onde um dado deve ser armazenado.

Migrations antigas protegidas não devem ser reescritas para representar uma alteração nova. Alterações legítimas de esquema devem gerar evolução versionada.

---

## Etapa 8 — Fluxos Principais

**Arquivo:** `Caderno_de_Erros_Inteligente_Etapa_8_Fluxos_Principais.md`

**Documento:** Especificação dos Fluxos Principais

**Finalidade:** descreve como estudante e sistema percorrem as capacidades aprovadas.

Os fluxos registram:

* ator;
* gatilho;
* pré-condições;
* passos;
* alternativas;
* erros;
* resultados;
* transações;
* idempotência;
* rastreabilidade.

### Consultar quando

Use este documento ao:

* implementar jornadas completas;
* criar views e formulários;
* modificar sequência de operações;
* tratar caminhos alternativos;
* tratar falhas;
* definir comportamento de cancelamento;
* trabalhar com concorrência;
* implementar transações ou idempotência.

Os fluxos descrevem comportamento e não devem ser tratados como protótipos visuais.

---

## Etapa 9 — Roadmap

**Arquivo:** `Caderno_de_Erros_Inteligente_Etapa_9_Roadmap (1).md`

**Documento:** Roadmap Incremental de Produto e Engenharia

**Finalidade:** transforma a documentação aprovada em uma sequência incremental de entregas verificáveis.

Define para cada versão:

* objetivo;
* funcionalidades;
* dependências;
* critérios de conclusão;
* riscos;
* exclusões;
* evidências necessárias para avançar.

### Consultar quando

Use este documento para determinar:

* em qual versão uma funcionalidade entra;
* o que não deve ser antecipado;
* dependências entre versões;
* critérios necessários para concluir uma versão;
* diferença entre V0.1, V0.2, V0.3, V0.4, V0.5 e V1.0;
* prioridades de implementação.

O roadmap define uma sequência de capacidades, não apenas um calendário.

Uma funcionalidade futura não deve entrar na versão em andamento sem decisão explícita.

---

## Etapa 10 — Plano de Testes

**Arquivo:** `Caderno_de_Erros_Inteligente_Etapa_10_Plano_de_Testes.md`

**Documento:** Plano Integrado de Testes e Qualidade

**Finalidade:** define como demonstrar que o sistema atende aos requisitos aprovados sem perder dados, distorcer métricas ou antecipar funcionalidades.

Abrange:

* testes unitários;
* testes de integração;
* testes funcionais;
* testes de interface;
* testes de banco;
* regressão;
* desempenho;
* segurança;
* privacidade;
* backup e restauração;
* usabilidade;
* automação;
* dados de teste;
* evidências;
* severidades;
* gates de liberação.

### Consultar quando

Use este documento ao:

* implementar testes;
* interpretar identificadores `CT-*`;
* verificar critérios de aceite;
* decidir cobertura necessária;
* validar regressão;
* preparar gates;
* avaliar severidade de defeitos;
* decidir se uma etapa possui evidência suficiente para promoção.

Não considere apenas percentual de cobertura como prova de correção. Casos críticos e critérios específicos continuam obrigatórios.

---

# 2. Architecture Decision Records — ADRs

Os ADRs registram decisões técnicas e arquiteturais já tomadas.

Uma decisão registrada em ADR deve ser tratada como vigente até que:

* outro ADR a substitua;
* seja encontrada incompatibilidade concreta;
* surja requisito novo que exija revisão;
* exista decisão formal explícita de mudança.

Não rediscuta uma decisão consolidada apenas por preferência de implementação.

---

## ADR-001 — Toolchain Reproduzível V0.1

**Arquivo:** `ADR-001_Toolchain_Reproduzivel_V0.1.md`

### Assunto

Define a toolchain reproduzível do projeto, incluindo versões fixadas de runtime, framework e ferramentas de desenvolvimento.

### Consultar quando

* alterar Python ou Django;
* alterar `uv`;
* adicionar ou atualizar ferramentas;
* alterar dependências;
* modificar política de versões;
* alterar configuração de lint, testes, segurança ou análise estática.

---

## ADR-002 — Perfis Django e isolamento de testes da V0.1

**Arquivo:** `ADR-002_Perfis_e_Isolamento_Django_V0.1.md`

### Assunto

Define os perfis de desenvolvimento, teste e produção local e o isolamento necessário para impedir que testes utilizem dados ou configurações de uso real.

### Consultar quando

* alterar settings;
* modificar banco de testes;
* trabalhar com variáveis de ambiente;
* modificar inicialização Django;
* alterar configuração de produção local.

---

## ADR-003 — Identidade, Workspace e tempo da V0.1

**Arquivo:** `ADR-003_Identidade_Workspace_e_Tempo_V0.1.md`

### Assunto

Define identidade, isolamento por Workspace e abstrações temporais usadas pelo projeto.

### Consultar quando

* trabalhar com User ou Workspace;
* alterar escopo de dados;
* lidar com fusos;
* utilizar Clock/Calendar;
* implementar operações dependentes de data/hora;
* garantir isolamento entre espaços.

---

## ADR-004 — Categorias padrão e seed da V0.1

**Arquivo:** `ADR-004_Categorias_Padrao_e_Seed_V0.1.md`

### Assunto

Define as categorias padrão de erro e o processo de criação/bootstrap idempotente.

### Consultar quando

* modificar categorias padrão;
* alterar seed/bootstrap;
* trabalhar com códigos canônicos;
* alterar inicialização do Workspace.

---

## ADR-005 — Logging, correlação e health local da V0.1

**Arquivo:** `ADR-005_Logging_Correlacao_e_Health_Local_V0.1.md`

### Assunto

Define logging estruturado, correlação de operações e diagnóstico técnico local.

### Consultar quando

* adicionar logs;
* alterar `correlation_id`;
* modificar tratamento de falhas;
* trabalhar com `/health/`;
* introduzir observabilidade;
* evitar exposição de dados privados em logs.

---

## ADR-006 — Interface acessível da fundação V0.1

**Arquivo:** `ADR-006_Interface_Acessivel_da_Fundacao_V0.1.md`

### Assunto

Define a base da interface utilizando Django Templates, Django Forms, HTML semântico e CSS próprio, além das decisões iniciais de acessibilidade e uso controlado de HTMX.

### Consultar quando

* criar ou alterar templates;
* criar formulários;
* modificar navegação;
* introduzir JavaScript ou HTMX;
* alterar padrões de acessibilidade;
* adicionar bibliotecas de interface.

---

## ADR-007 — Backup e restauração mínima SQLite da V0.1

**Arquivo:** `ADR-007_Backup_e_Restauracao_Minima_SQLite_V0.1.md`

### Assunto

Define a prova mínima de backup e restauração da fundação SQLite.

### Consultar quando

* modificar backup;
* modificar restauração;
* trabalhar com banco SQLite ativo;
* alterar manifesto/checksum;
* implementar capacidades futuras de exportação ou recuperação.

---

## ADR-008 — Gate único de qualidade e automação da V0.1

**Arquivo:** `ADR-008_Gate_Unico_de_Qualidade_V0.1.md`

### Assunto

Define o gate único e bloqueante de qualidade do projeto.

### Consultar quando

* modificar `scripts/quality.ps1`;
* modificar ferramentas do gate;
* alterar critérios de cobertura;
* alterar análise de vulnerabilidades ou segredos;
* modificar condições de promoção de uma etapa.

O gate autoritativo deve permanecer bloqueante: falha em verificação obrigatória impede conclusão.

---

## ADR-009 — Validação final e promoção da V0.1

**Arquivo:** `ADR-009_Validacao_Final_e_Promocao_V0.1.md`

### Assunto

Registra a validação final e a promoção formal da fundação V0.1.

### Consultar quando

* verificar o que já foi comprovado na V0.1;
* investigar regressões da fundação;
* conferir critérios usados na promoção anterior;
* distinguir pendências futuras de defeitos da baseline promovida.

---

## ADR-010 — Fronteira, Rastreabilidade e Dados da V0.2

**Arquivo:** `ADR-010_Fronteira_Rastreabilidade_e_Dados_V0.2.md`

### Assunto

Define a fronteira autoritativa da V0.2 e consolida as correções de fase, rastreabilidade e modelo aplicáveis ao Catálogo de Conteúdo.

### Consultar quando

Qualquer tarefa da V0.2 envolver:

* taxonomia;
* questões;
* origem;
* estados;
* filtros;
* versionamento de conteúdo;
* migrations;
* testes;
* definição do que pertence ou não à V0.2.

Para conflitos de interpretação sobre o escopo da V0.2, este ADR deve ser consultado antes de implementar.

Entre as decisões controladas estão:

* tags fora da V0.2;
* delimitação dos RFs aplicáveis;
* recortes dos fluxos de catálogo;
* filtros obrigatórios;
* origem mínima;
* revisões imutáveis de conteúdo;
* preservação da baseline V0.1.

---

## ADR-011 — Saneamento, Fronteira e Rastreabilidade da V0.3

**Arquivo:** `ADR-011_Saneamento_Fronteira_e_Rastreabilidade_V0.3.md`

### Assunto

Resolve os bloqueadores documentais da V0.3: fases de testes, orquestração,
contexto transitório, SQLite/idempotência, `OperationReceipt`, entidades e
plano incremental.

### Consultar quando

Qualquer tarefa da V0.3 envolver tentativa, diagnóstico, ciclo, revisão, fila,
arquivamento com suspensão, transação, concorrência ou rastreabilidade.

---

# 3. Documentos de gate, promoção e release

## Gate de Implementação — Auditoria Final da Documentação

**Arquivo:** `Caderno_de_Erros_Inteligente_Gate_de_Implementacao_Auditoria_Final.md`

**Documento:** Relatório do Gate de Implementação

### Finalidade

Registra a auditoria da documentação que autorizou o início da implementação e mantém o histórico das ressalvas e correções identificadas.

Também contém registros controlados posteriores relacionados às pendências documentais e à V0.2.

### Consultar quando

* investigar a origem de uma errata `ERR-V01-*`;
* verificar ressalvas históricas;
* compreender por que determinada correção documental foi criada;
* auditar a evolução da baseline;
* analisar uma divergência de rastreabilidade.

Este documento é histórico e de auditoria. Decisões posteriores formalizadas em ADRs podem substituir interpretações antigas.

---

## Release Notes V0.1

**Arquivo:** `RELEASE_NOTES_V0.1.md`

### Finalidade

Registra informações relativas à entrega e ao estado promovido da V0.1.

### Consultar quando

* precisar entender o que foi entregue na V0.1;
* comparar uma versão posterior com a baseline promovida;
* investigar regressão;
* preparar documentação de uma nova release.

---

# 4. Documentação operacional do repositório

Além dos documentos existentes neste diretório, três arquivos localizados fora de `docs/` possuem papel operacional especial.

## `../AGENTS.md`

Define **como agentes devem trabalhar no repositório**.

Consultar no início de qualquer nova sessão ou tarefa.

---

## `../PROJECT_STATE.md`

Define **onde o projeto está atualmente**.

Deve resumir:

* versão atual;
* etapa atual;
* último marco concluído;
* último gate;
* bloqueadores;
* próximo objetivo autorizado.

Não substitui requisitos, ADRs ou documentação formal.

---

## `../tasks/current.md`

Define **o que está autorizado a ser feito agora**.

Deve conter:

* objetivo;
* escopo;
* fora de escopo;
* arquivos relevantes;
* documentação relevante;
* restrições;
* critérios de aceite;
* testes;
* gate aplicável.

A existência de uma funcionalidade no Roadmap não autoriza sua implementação se ela não estiver dentro da tarefa atual.

---

# 5. Gate autoritativo

O comando oficial de qualidade do projeto é:

`./scripts/quality.ps1`

O gate verifica a qualidade técnica e as evidências automatizadas aplicáveis ao estado atual do projeto.

Uma tarefa não pode ser declarada concluída quando o gate autoritativo aplicável falhar.

Verificações específicas de uma etapa podem complementar o gate geral e devem ser registradas em `tasks/current.md`.

Os manifests e demais artefatos utilizados pelo gate permanecem em `../quality/`.

---

# 6. Ordem recomendada de consulta por tipo de tarefa

## Nova funcionalidade

Consultar normalmente:

1. `../PROJECT_STATE.md`;
2. `../tasks/current.md`;
3. Etapa 9 — Roadmap;
4. Etapa 3 — Requisitos Funcionais;
5. Etapa 5 — Regras de Negócio;
6. Etapa 8 — Fluxos;
7. SDD e Modelo de Dados quando aplicáveis;
8. ADRs relacionados;
9. Etapa 10 — Plano de Testes.

---

## Alteração de model ou migration

Consultar:

1. tarefa atual;
2. requisitos relacionados;
3. regras de negócio;
4. Etapa 7 — Modelo de Dados;
5. Etapa 6 — SDD;
6. ADRs aplicáveis;
7. histórico de migrations;
8. Plano de Testes.

Não alterar uma migration protegida apenas para adequá-la ao estado novo.

---

## Alteração de interface

Consultar:

1. tarefa atual;
2. requisitos funcionais;
3. fluxos;
4. requisitos não funcionais de usabilidade/acessibilidade;
5. ADR-006;
6. regras de negócio envolvidas;
7. testes aplicáveis.

---

## Alteração de arquitetura

Consultar:

1. tarefa atual;
2. SDD;
3. ADRs existentes;
4. requisitos funcionais e não funcionais afetados;
5. Modelo de Dados, quando aplicável;
6. Roadmap.

Uma decisão arquitetural relevante que não esteja coberta pelas decisões existentes pode exigir novo ADR.

---

## Correção de bug

Consultar:

1. comportamento atual;
2. teste que reproduz a falha;
3. RF/RNF/RN relacionado;
4. fluxo aplicável;
5. ADR relacionado;
6. Plano de Testes.

Evite alterar uma especificação aprovada apenas para fazer a implementação existente parecer correta.

---

## Encerramento de etapa

Antes de encerrar:

1. verificar todos os critérios de aceite de `tasks/current.md`;
2. executar testes específicos;
3. executar `./scripts/quality.ps1`;
4. exigir gate aprovado;
5. registrar a evidência aplicável;
6. atualizar `PROJECT_STATE.md`;
7. atualizar e arquivar a tarefa concluída em `tasks/completed/`;
8. não iniciar automaticamente a etapa seguinte.

---

# 7. Regras de manutenção deste índice

Atualize este arquivo quando:

* um novo documento formal for criado;
* um ADR for criado, substituído ou descontinuado;
* um documento for renomeado;
* a localização de uma fonte de verdade mudar;
* surgir uma nova categoria relevante de documentação.

Não replique aqui o conteúdo integral dos documentos.

Este README deve continuar sendo um **mapa para encontrar a fonte correta**, e não uma segunda especificação do produto.

---

# 8. Princípio operacional

O repositório é a memória permanente do projeto.

Use:

* `AGENTS.md` para saber **como trabalhar**;
* `PROJECT_STATE.md` para saber **onde o projeto está**;
* `tasks/current.md` para saber **o que fazer agora**;
* `docs/README.md` para saber **onde encontrar a informação**;
* ADRs para saber **quais decisões já foram tomadas**;
* documentação das Etapas 1–10 para saber **o que foi especificado**;
* `scripts/quality.ps1` para comprovar **se a qualidade exigida foi atendida**;
* Git para preservar **o histórico verificável da evolução do projeto**.
