# Caderno de Erros Inteligente

## Etapa 10 — Plano de Testes

| Campo | Valor |
|---|---|
| Documento | Plano Integrado de Testes e Qualidade |
| Projeto | Caderno de Erros Inteligente |
| Versão | 1.0.2 — errata V0.2 |
| Data | 30 de agosto de 2026 |
| Status | Aprovada; errata documental da V0.2 incorporada em 5 de setembro de 2026 |
| Base congelada | Visão 1.0; Escopo 1.0; RFs 1.0; RNFs 1.0; Regras de Negócio 1.0; SDD 1.0; Modelo de Dados 1.0; Fluxos 1.0; Roadmap 1.0 |
| Próximo marco após a errata V0.2 | V0.2 — Etapa 1 — Taxonomia e migrations, mediante instrução específica |

---

## 1. Finalidade

Este plano define como demonstrar que o Caderno de Erros Inteligente atende aos requisitos aprovados sem perder dados, distorcer métricas ou antecipar funcionalidades futuras. Abrange:

- testes unitários, de integração, funcionais, de interface e de banco de dados;
- regras de negócio, revisão espaçada, datas, estatísticas, domínio e prioridade;
- regressão, desempenho, segurança, privacidade, backup, restauração e usabilidade;
- ambientes, dados sintéticos, automação, evidências, severidades e gates de liberação;
- distribuição dos casos entre MVP, V1 e Pós-V1.

O documento testa o comportamento observável. Nomes de ferramentas poderão ser ajustados na V0.1, mas critérios, rastreabilidade e resultados esperados somente mudarão mediante decisão registrada.

## 2. Objetivos de qualidade

1. Provar que tentativa, erro, ciclo e revisão formam um histórico íntegro e explicável.
2. Provar que datas e estados de revisão respeitam o fuso do espaço de dados.
3. Impedir duplicação, atualização perdida e confirmação falsa em operações críticas.
4. Reconciliar dashboard, relatórios e exportações com os registros autoritativos.
5. Validar `DOM-HEUR-1.0` e `PRI-HEUR-1.0` com exemplos determinísticos.
6. Preservar isolamento, privacidade, acessibilidade e recuperação dos dados.
7. Medir o produto no baseline pessoal `BCR-1` antes do piloto e da V1.

### 2.1 Princípios

- **Correção antes de cobertura:** porcentagem de linhas não substitui casos de fronteira.
- **Domínio isolado:** política de revisão, métricas e fórmulas devem ser testáveis sem interface.
- **Banco real nos limites:** restrições, transações e migrações são verificadas em SQLite e, quando aplicável, PostgreSQL.
- **Relógio controlável:** nenhum teste crítico depende da data real de execução.
- **Dados sintéticos:** testes não usam conteúdo pessoal do estudante.
- **Evidência reproduzível:** falha deve informar cenário, semente, versão, ambiente e diferença observada.
- **Pirâmide saudável:** muitos testes unitários, menos integrações e um conjunto pequeno de jornadas ponta a ponta.

## 3. Escopo por tipo de teste

| Tipo | Alvo principal | Evidência mínima | Automação |
|---|---|---|---|
| Unitário | Entidades, serviços, políticas, validadores e fórmulas | Entrada, saída e fronteiras determinísticas | Obrigatória no domínio |
| Integração | Aplicação, repositórios, transações, filas lógicas e banco | Estado anterior/posterior e rollback | Obrigatória |
| Funcional | RFs e fluxos do usuário | Jornada e resultado persistido | Obrigatória nos fluxos centrais |
| Interface | Formulários, HTMX, foco, mensagens e proteção de resposta | DOM acessível, navegação e payload | Automática + inspeção |
| Banco de dados | Constraints, índices, migrações e concorrência | SQL/schema e reconciliação | Obrigatória |
| Regras de negócio | `RN-001` a `RN-100` | Tabelas de decisão e fronteiras | Obrigatória |
| Datas e revisão | D1/D7/D14/D30, atraso e fuso | Clock fixo e matriz de datas | Obrigatória |
| Estatística | Contagens, denominadores, filtros e arredondamento | Resultado manual conhecido | Obrigatória |
| Domínio/prioridade | Fórmulas V1, confiança e explicações | Vetores de cálculo versionados | Obrigatória na V1 |
| Regressão | Capacidades já aprovadas | Suite verde e ausência de defeito bloqueador | Obrigatória por mudança |
| Desempenho | Latência, memória e crescimento | p50/p95/p99 e ambiente | Gate no MVP/V1 |
| Segurança/privacidade | Autorização, entrada, sessão, logs e arquivos | Relatório sem exposição de conteúdo | Gate contínuo |
| Backup/restauração | Integridade, compatibilidade e recuperação | RPO/RTO, checksum e reconciliação | Exercício obrigatório |
| Usabilidade | Eficiência, entendimento e prevenção de erro | Tarefas observadas e achados | Sessões por marco |

## 4. Níveis, ferramentas e organização

### 4.1 Estratégia de automação

A implementação deverá adotar ferramentas compatíveis com Python/Django. A seleção final será registrada na V0.1; a referência inicial é:

- `pytest` e `pytest-django` para domínio, aplicação e persistência;
- cliente de testes do Django para HTTP e autorização;
- Playwright para jornadas de navegador e regressão visual apenas quando esta agregar valor;
- verificador automatizado compatível com WCAG 2.2 AA, complementado por teclado e leitor de tela;
- gerador determinístico de `BCR-1` e executor de carga documentado;
- análise estática de dependências, segredos e padrões inseguros integrada ao pipeline.

### 4.2 Convenção de identificação

- caso: `CT-NNN`;
- execução: `EXE-AAAA-MM-DD-NNN`;
- defeito: `DEF-NNN`;
- conjunto de dados: `DAD-NNN`;
- relatório de desempenho: `PERF-AAAA-MM-DD`;
- exercício de recuperação: `REC-AAAA-MM-DD`.

Um caso automatizado deve manter seu `CT-NNN` no nome, marcador ou metadado, evitando uma planilha sem vínculo com o código.

### 4.3 Prioridade de caso

| Prioridade | Significado | Regra de execução |
|---|---|---|
| P0 | Integridade, segurança, ciclo central ou recuperação | Cada commit relevante e todo release |
| P1 | Função essencial e métrica confiável | Pull request e release |
| P2 | Experiência, compatibilidade e fronteiras menos frequentes | Pipeline completo e release |
| P3 | Exploração ou conveniência futura | Execução planejada |

## 5. Ambientes

| Ambiente | Banco | Uso | Regras |
|---|---|---|---|
| `TST-UNIT` | Nenhum/dublê explícito | Domínio puro | Clock, IDs e sementes fixos |
| `TST-SQLITE` | SQLite temporário | Integração principal do MVP | Mesmas pragmas e constraints da aplicação |
| `TST-WEB` | SQLite isolado | Navegador e acessibilidade | Chrome/Edge, 360–1920 px |
| `TST-PG` | PostgreSQL suportado | Portabilidade/hospedagem V1 | Obrigatório antes de uso remoto |
| `TST-PERF` | Cópia sintética | `BCR-1` e 2× | Hardware e software registrados |
| `TST-REC` | Diretório/banco descartável | Backup, restauração e migração | Nunca aponta para dados reais |

O pipeline deverá criar o ambiente do zero. Teste que depende de ordem, banco residual, internet ou relógio real é considerado defeituoso.

## 6. Dados de teste

### 6.1 Conjuntos canônicos

| ID | Conteúdo | Uso |
|---|---|---|
| `DAD-001` | Espaço vazio, fuso `America/Sao_Paulo` | estados sem dados |
| `DAD-002` | 2 disciplinas, 4 assuntos, 4 subassuntos e 20 questões | jornadas comuns |
| `DAD-003` | Ciclos completos, reinícios e atrasos em datas fixas | revisão e métricas |
| `DAD-004` | Unicode, acentos, limites e conteúdo potencialmente hostil | validação e segurança |
| `DAD-005` | Dois espaços de dados com IDs previsíveis | isolamento |
| `DAD-006` | Vetores manuais de domínio e prioridade | fórmulas V1 |
| `DAD-007` | Backups válidos, corrompidos e de versões distintas | recuperação |
| `BCR-1` | 10.000 questões, 100.000 tentativas, 100.000 revisões, 200 níveis ativos e 10 anos | desempenho e escala pessoal |
| `BCR-2` | Duas vezes `BCR-1` | estresse V1 |

Todo gerador deve aceitar semente, produzir manifesto de contagens e permitir recriar exatamente a mesma distribuição.

### 6.2 Oráculos

Resultados de datas, estatísticas e fórmulas terão arquivos de vetores independentes da implementação. O valor esperado não deverá ser calculado chamando o mesmo serviço testado. Para números decimais, cálculos internos usam precisão definida pela regra; arredondamento ocorre somente na apresentação.

## 7. Critérios de entrada, saída e suspensão

### 7.1 Entrada de uma capacidade

- requisito e versão identificados;
- regra de negócio aplicável aprovada;
- migração e rollback definidos quando houver esquema;
- dados e oráculos disponíveis;
- riscos de segurança e privacidade classificados;
- critérios de aceitação traduzidos em casos.

### 7.2 Saída de uma versão

- 100% dos P0 e P1 aplicáveis executados e aprovados;
- nenhum defeito S1/S2 aberto;
- casos críticos automatizados, salvo exceção documentada;
- cobertura de linhas do domínio/regras de pelo menos 80%, sem reduzir cobertura de branches críticos;
- migração de banco novo e de cópia representativa aprovada;
- regressão verde no ambiente suportado;
- evidências de segurança, acessibilidade e desempenho exigidas pelo gate;
- documentação de execução, backup e recuperação atualizada.

### 7.3 Suspensão imediata

Testes e liberação são interrompidos diante de corrupção, vazamento entre espaços, exposição de resposta protegida, backup irrecuperável, migração destrutiva sem cópia, resultados não determinísticos em regras críticas ou ambiente divergente sem explicação.

## 8. Gates por versão

| Versão | Suite obrigatória | Evidência que bloqueia avanço |
|---|---|---|
| V0.1 | bootstrap, perfis, workspace/fuso, seed idempotente, relógio, logs, health local, migração vazia, backup/restauração mínima, instalação Windows e CI | ambiente não reproduzível, isolamento ausente, seed duplicado, log inseguro ou recuperação mínima não comprovada |
| V0.2 | hierarquia, questões, revisões de conteúdo, busca básica, validação UI | questão inválida tornar-se praticável ou histórico de edição se perder |
| V0.3 | tentativas, erros, D1/D7/D14/D30, transações, idempotência, datas | duplicação, ciclo incorreto ou confirmação falsa |
| V0.4 | jornada E2E, dashboard básico, `BCR-1`, backup/restauração, teclado | fluxo central, recuperação ou metas MVP falharem |
| V0.5-A | arquivamento, correção/anulação, reconstrução e filtros salvos | histórico ou estado derivado divergir |
| V0.5-B | domínio, confiança, prioridade e explicações | fórmula, teto ou elegibilidade incorretos |
| V0.5-C | exportação/importação, PostgreSQL se ativado, operação V1 | arquivo irreconciliável ou portabilidade quebrada |
| V1.0 | regressão total, migração realista, segurança, WCAG, `BCR-1` e `BCR-2` | S1/S2, regressão P0/P1 ou recuperação não comprovada |
| Pós-V1 | casos específicos e regressão preservada | alteração não versionada de regra ou quebra do núcleo |

### 8.1 Rastreabilidade autoritativa da V0.1 após o Gate

Esta matriz corrige a rastreabilidade aplicável à V0.1 conforme `COR-P1-001` e formaliza os casos exigidos por `COR-P1-002`. “N/A” indica entrega técnica sem requisito funcional ou regra de negócio própria; nesses casos, o contrato é dado pelos RNFs, SDD e Roadmap, sem criar requisito de produto artificial.

| Entrega V0.1 | Requisito funcional | Regra de negócio | RNF/decisão aplicável | Fluxo/componente | Casos de teste |
|---|---|---|---|---|---|
| Dependências fixadas e perfis separados | Base técnica de `RF-067` | N/A — fundação técnica | `RNF-018`, `019`, `052`–`054`, `056`, `079`, `080`; `SDD-ABR-001` | Configuração Django e perfis dev/test/prod-local | `CT-099`, `104`, `127`, `130` |
| `User` UUID, `Workspace` e isolamento | `RF-001`, base de `RF-067` | `RN-001` | `RNF-013`, `027`, `033`; `MD-DEC-001`, `003`, `016` | Accounts/Workspace; primeira migração; `FL-023` | `CT-001`, `073`, `074`, `081`, `129` |
| Primeiro acesso, locale e fuso IANA | `RF-002`, `003` | `RN-002`–`005` | `RNF-030`, `067`, `074`; `FL-DEC-015` | `FL-023`; `Clock`/`Calendar`; configuração | `CT-002`, `135` |
| Seed idempotente das categorias padrão | `RF-029` | `RN-029` | `RNF-027`, `033`; Modelo `ErrorCategory` | Bootstrap/seed V0.1; `FL-023` | `CT-073`, `081`, `129` |
| Layout e navegação mínimos | `RF-001`–`003` | `RN-001`–`005` | `RNF-044`–`049`, `063`, `065`, `066` | Templates base e configuração | `CT-002`, `136` |
| Logging estruturado e sanitizado | Base técnica de `RF-067`, `068` | `RN-001` | `RNF-018`, `022`, `068`–`070` | Audit/Operations mínimo, sem `AuditEvent` obrigatório na V0.1 | `CT-099`, `134` |
| Diagnóstico/health local | Base técnica de `RF-067`, `068` | N/A — diagnóstico técnico | `RNF-068`, `070`, `072`; Gate V0.1 | Rota ou comando local restrito | `CT-131` |
| Migração limpa e banco de teste isolado | Base técnica de `RF-067` | `RN-001` | `RNF-027`, `033`, `057`, `079` | ORM, migrações e perfil de teste | `CT-073`, `074`, `081`, `130` |
| Backup/restauração mínima SQLite | `RF-068`, base de `RF-067` | `RN-001` | `RNF-034`–`038`; `SDD-ADR-006` | Parte técnica de `FL-022`; manifesto/checksum | `CT-132`, `133` |
| Comando único de qualidade e documentação Windows | Base técnica de `RF-067`, `068` | N/A — gate técnico | `RNF-019`, `052`, `053`, `056`, `058`, `076`, `079`, `080`; `RD-DEC-002` | Pipeline/test runner/README | `CT-081`, `099`, `104`, `123`, `127`, `130`–`136` |

As seguintes capacidades permanecem explicitamente fora da V0.1:

| Capacidade | Primeira fase possível | Condição documental |
|---|---|---|
| Taxonomia acadêmica, questão, versões e alternativas | V0.2 | Não criar entidades, telas ou módulos vazios na V0.1. |
| Tags | V0.5-A/V1; não V0.2 | `COR-P1-003` resolvida por `ERR-V02-001`; somente retornar após RF/RN/CT próprios. |
| Tentativas, erros finalizados, ciclos e revisões | V0.3 | Exigem transações, idempotência e política SQLite medidas. |
| Dashboard, métricas, busca e `BCR-1` como gate | V0.4 | Não antecipar FTS, cache, snapshots ou gráficos. |
| Categorias pessoais e inclusão manual de questão correta | V0.5-A | Resolver `COR-P1-004` e `COR-P1-005` antes da funcionalidade. |
| Reagendamento | V0.5-A | Resolver `COR-P1-006`; manter a mesma revisão `PENDING`. |
| Domínio, confiança e prioridade | V0.5-B | Não implementar `DOM-HEUR-1.0` ou `PRI-HEUR-1.0` na fundação. |
| Exportação V1, restauração pela interface e PostgreSQL | V0.5-C | Backup técnico mínimo V0.1 não é `CEI-EXPORT-1.0`. |
| API, IA, integração, OCR, anexos, PWA e notificações | Pós-V1 ou mudança formal | Continuam fora do escopo atual da V0.1. |

## 9. Catálogo detalhado de casos

Nas tabelas seguintes, “dados” integra a pré-condição. Cada caso contém objetivo, requisito relacionado, pré-condição/entrada, passos, resultado esperado, prioridade e fase.

### 9.1 Fundação, espaço de dados, taxonomia e questões

| ID | Objetivo | Rastreabilidade | Pré-condição e entrada | Passos | Resultado esperado | Pri. | Fase |
|---|---|---|---|---|---|---|---|
| `CT-001` | Isolar espaços | `RF-001`, `RN-001`, `RNF-013`, `MD-DEC-003` | `DAD-005`; usuário do espaço A | Consultar e alterar ID de B por URL/formulário | Acesso negado; nenhum dado de B é revelado ou alterado | P0 | V0.1 |
| `CT-002` | Configurar, alterar e persistir fuso | `RF-002`, `RF-003`, `RN-002`–`005`, `RNF-030`, `RNF-067`, `FL-023` | Primeiro acesso local; `America/Sao_Paulo` e segundo fuso IANA válido | Inicializar, reiniciar, tentar mudança inválida, cancelar uma mudança válida e por fim confirmá-la | Fuso inicial persiste; inválido é rejeitado; cancelamento preserva o anterior; confirmação persiste o novo; sem revisões, o impacto futuro é informado de forma simplificada | P1 | V0.1 |
| `CT-003` | Normalizar nomes | `RF-004`–`RF-006`, `RN-008`, `FL-001`, `SDD-MOD-002` | Nomes com espaços, caixa e acentos | Cadastrar equivalentes normalizados | Duplicata é rejeitada no mesmo pai; acentos legítimos são preservados | P1 | V0.2 |
| `CT-004` | Impedir hierarquia inválida | `RF-005`–`RF-007`, `RN-006`, `RN-007`, `FL-001`, `FL-002`, `SDD-MOD-002`, `SDD-MOD-003` | Assunto de disciplina A; subassunto informado para B | Salvar vínculo cruzado | Validação rejeita e transação não persiste parcial | P0 | V0.2 |
| `CT-005` | Excluir rascunho da prática | `RF-009`, `RF-063`, `RN-011`, `RN-017`, `FL-002`, recorte de `FL-020` | Questão sem gabarito, estado rascunho | Na V0.2, buscar/listar por estado; em V0.3/V0.4, iniciar tentativa e consultar métricas | Na V0.2 não aparece entre ativas e permanece recuperável; prática e denominadores são comprovados nas fases futuras | P0 | V0.2 parcial; V0.3/V0.4 integral |
| `CT-006` | Validar questão ativa | `RF-009`–`RF-011`, `RF-014`, `RN-006`, `RN-007`, `RN-011`–`RN-013`, `FL-002` | Enunciado e alternativas incompletas | Tentar ativar | Mensagens indicam campos; estado continua rascunho | P1 | V0.2 |
| `CT-007` | Garantir um gabarito | `RF-010`, `RF-011`, `RN-012`, `RN-013`, `FL-002`, `MD-DEC-006` | Quatro alternativas; zero ou duas corretas | Salvar como ativa | Rejeição; somente uma correta permite ativação | P0 | V0.2; proteção durante resposta V0.3 |
| `CT-008` | Versionar conteúdo | `RF-015`, `RF-017`, recorte de `RF-018`, `RN-016`, `RN-019`, `RN-020`, `RN-086`, `FL-005`, `MD-DEC-004` | Questão ativa sem tentativa | Editar enunciado e salvar | Nova revisão atual; anterior preservada e auditável | P1 | V0.2 |
| `CT-009` | Proteger gabarito usado | `RF-018`, `RN-020`, `FL-005`; Question/Attempt | Questão com tentativa válida | Alterar alternativa correta diretamente | Operação bloqueada ou encaminhada ao fluxo formal V1 | P0 | V0.3; correção formal V1 |
| `CT-010` | Arquivar sem apagar histórico | `RF-019`, `RN-017`, `RN-087`, recorte de `FL-006` | V0.2: questão com revisões de conteúdo; V0.3: tentativas/revisão pendente | Na V0.2 confirmar, arquivar e consultar versões; na V0.3 consultar histórico/fila | V0.2: sai das ativas e preserva revisões; V0.3: tentativas permanecem e pendência é suspensa | P0 | V0.2 parcial; V0.3 integral |
| `CT-011` | Cadastro rápido íntegro | `RF-014`, `RN-011`–`RN-013`, `RN-016`, `FL-002`, `SDD-SVC-001` | Taxonomia existente; dados mínimos válidos | Cadastrar pelo fluxo rápido | Questão ativa é criada no pai correto sem campos inconsistentes | P1 | V0.2 |
| `CT-012` | Validar Unicode e limites | `RNF-016`, `RNF-066`, Modelo §3.6, `FL-002`, `FL-005` | `DAD-004`; fronteiras de tamanho | Salvar mínimo, máximo e máximo+1 | Limites aceitam fronteiras válidas, rejeitam excesso e preservam UTF-8 | P1 | V0.2 |

### 9.2 Tentativas, erros e contexto de resposta

| ID | Objetivo | Rastreabilidade | Pré-condição e entrada | Passos | Resultado esperado | Pri. | Fase |
|---|---|---|---|---|---|---|---|
| `CT-013` | Registrar acerto inicial | `RF-021`–`RF-024`, `RN-023` | Questão ativa; alternativa correta | Responder e confirmar | Uma tentativa inicial válida; sem ciclo de erro ou revisão D1 | P0 | V0.3 |
| `CT-014` | Criar ciclo no erro inicial | `RF-025`–`RF-029`, `RN-024`, `RN-037` | Clock 10/08 14h; alternativa errada; categoria cálculo | Responder, classificar e concluir | Tentativa, erro, ciclo ativo e única D1 em 11/08 são persistidos atomicamente | P0 | V0.3 |
| `CT-015` | Calcular resultado no servidor | `RF-023`, `RN-022` | Questão com gabarito; cliente envia resultado adulterado | Submeter resposta | Resultado deriva da alternativa/gabarito; campo adulterado é ignorado/rejeitado | P0 | V0.3 |
| `CT-016` | Impedir duas iniciais válidas | `RN-026`, `MD-DEC-011` | Uma tentativa inicial válida | Repetir criação por duas requisições | No máximo uma válida; segunda é idempotente ou rejeitada | P0 | V0.3 |
| `CT-017` | Exigir descrição para Outra | `RF-027`, `RN-031` | Erro selecionado; categoria `OTHER`; descrição vazia | Concluir classificação | Não conclui e preserva escolhas; descrição válida permite salvar | P1 | V0.3 |
| `CT-018` | Não diagnosticar acerto | `RN-029` | Tentativa correta | Tentar enviar categoria de erro | Nenhum diagnóstico é associado à tentativa correta | P0 | V0.3 |
| `CT-019` | Corrigir diagnóstico com história | `RF-066`, `RN-033` | Erro já classificado | Alterar categoria no fluxo autorizado | Valor atual muda; autoria, instante e valor anterior permanecem auditáveis | P1 | V0.5-A |
| `CT-020` | Preservar tentativa imutável | `RN-027`, `RNF-028` | Tentativa válida persistida | Editar resultado/data diretamente | Atualização destrutiva é bloqueada; anulação/correção gera evento formal | P0 | V0.5-A |
| `CT-021` | Abandonar sem parcial persistente | `FL-004`, `FL-005`, `FX-DEC-004` | Questão aberta ou resposta ainda não finalizada | Fechar/navegar antes de concluir | Não existe tentativa parcial, ciclo ou revisão no banco | P0 | V0.3 |
| `CT-022` | Proteger contexto transitório | `SDD-DEC-014`, `RNF-016` | Token expirado ou adulterado | Abrir etapa pós-resposta | Rejeição segura; gabarito/contexto de outro usuário não é revelado | P0 | V0.3 |

### 9.3 Revisão espaçada, datas e concorrência

| ID | Objetivo | Rastreabilidade | Pré-condição e entrada | Passos | Resultado esperado | Pri. | Fase |
|---|---|---|---|---|---|---|---|
| `CT-023` | Agendar primeira D1 | `RF-030`–`RF-036`, `RN-037` | Erro válido em 10/08 no fuso do espaço | Finalizar operação | Revisão pendente `D1`, data 11/08, no ciclo ativo | P0 | V0.3 |
| `CT-024` | Avançar D1 para D7 | `RN-038` | D1 devida; resposta correta em 11/08 | Concluir revisão | D1 concluída; única D7 pendente para 18/08 | P0 | V0.3 |
| `CT-025` | Avançar D7 para D14 | `RN-038` | D7 devida; acerto em 20/08 | Concluir | Próxima D14 em 03/09, ancorada na execução real | P0 | V0.3 |
| `CT-026` | Avançar D14 para D30 | `RN-038` | D14 devida; acerto | Concluir | Única D30 pendente para data real +30 dias | P0 | V0.3 |
| `CT-027` | Encerrar após D30 | `RN-039` | D30 devida; acerto | Concluir | Ciclo concluído; nenhuma próxima revisão criada | P0 | V0.3 |
| `CT-028` | Reiniciar em qualquer erro | `RN-037`, `RN-040` | D1, D7, D14 ou D30 ativa | Errar em cada etapa parametrizada | Etapa atual concluída com erro; ciclo reinicia em D1 para +1 dia | P0 | V0.3 |
| `CT-029` | Manter uma pendência | `RN-041`, `MD-DEC-014` | Ciclo ativo | Criar avanço e repetir chamada | Apenas uma revisão pendente/ativa no ciclo | P0 | V0.3 |
| `CT-030` | Bloquear revisão futura | `RF-038`, `RN-044` | Revisão para amanhã | Tentar iniciar hoje | Abertura negada sem criar tentativa | P0 | V0.3 |
| `CT-031` | Reconhecer vencimento hoje | `RN-042` | Data local igual a `due_date` | Consultar fila | Estado “para hoje”; item pode ser iniciado | P1 | V0.3 |
| `CT-032` | Reconhecer atraso | `RN-043` | `due_date` anterior à data local | Consultar fila | Estado “atrasada”; dias de atraso corretos | P1 | V0.3 |
| `CT-033` | Ancorar acerto atrasado | `RN-040` | D7 atrasada 5 dias; acerto em 20/08 | Concluir | Próxima D14 = 03/09, não data originalmente prevista +14 | P0 | V0.3 |
| `CT-034` | Reiniciar erro atrasado | `RN-037` | Revisão atrasada; erro em 20/08 | Concluir | Nova D1 = 21/08 | P0 | V0.3 |
| `CT-035` | Preservar histórico ao mudar fuso | `RNF-030`, `RNF-067` | Eventos existentes; alterar fuso do espaço | Reabrir histórico e fila | Instantes históricos não mudam; derivação futura segue política registrada | P0 | V0.3 |
| `CT-036` | Tratar transição de horário | `RNF-030`, `RNF-074` | Fuso com DST e clock na transição | Criar/concluir revisão | Data local correta; não há revisão duplicada ou inexistente | P1 | V0.3 |
| `CT-037` | Tornar conclusão idempotente | `RNF-025`, `RNF-026` | Mesma operação, mesma chave e payload | Enviar duas vezes | Uma tentativa/um avanço; segunda retorna resultado original | P0 | V0.3 |
| `CT-038` | Detectar chave com payload distinto | `RNF-026`, `SDD-DEC-013` | Chave já consumida | Reenviar com resposta diferente | Conflito explícito; estado original não muda | P0 | V0.3 |
| `CT-039` | Reverter falha intermediária | `RNF-025`, `RNF-032` | Falha injetada após tentativa e antes da próxima revisão | Concluir operação | Transação inteira reverte; UI não confirma sucesso | P0 | V0.3 |
| `CT-040` | Resolver duas abas | `RNF-031`, `FL-010` | Mesma revisão aberta em duas abas | Concluir quase simultaneamente | Uma vence; outra recebe estado atualizado; sem duplicação | P0 | V0.3 |
| `CT-041` | Suspender ao arquivar | `RN-020`, `RN-046` | Questão com pendência | Arquivar | Pendência não aparece como executável; histórico preservado | P0 | V0.5-A |
| `CT-042` | Não deixar facilidade alterar agenda | `RN-049`, `RN-067` | Revisão correta; fácil/média/difícil | Repetir cenário por facilidade | Próxima data é igual em todos; facilidade só alimenta métrica V1 | P1 | V0.3 |
| `CT-043` | Reprogramar com auditoria | `RF-065`, `RN-047` | Revisão pendente V1 | Alterar data e informar motivo | Data nova válida; motivo e valor anterior registrados | P1 | V0.5-A |
| `CT-044` | Reabrir manualmente | `RF-061`, `RN-080` | Questão dominada; motivo informado | Reabrir | Estado deixa de dominado; novo ciclo começa em D1; domínio anterior permanece histórico | P1 | V0.5-B |

### 9.4 Estatísticas, dashboard e reconciliação

| ID | Objetivo | Rastreabilidade | Pré-condição e entrada | Passos | Resultado esperado | Pri. | Fase |
|---|---|---|---|---|---|---|---|
| `CT-045` | Separar questões de tentativas | `RF-047`–`RF-056`, `RN-051` | Uma questão com 5 tentativas | Abrir dashboard | Questões realizadas =1; tentativas válidas =5 | P0 | V0.4 |
| `CT-046` | Contar apenas válidas | `RN-052` | 3 acertos, 2 erros, 1 anulada | Calcular totais | Denominador 5; anulada não participa | P0 | V0.4 |
| `CT-047` | Evitar zero enganoso | `RN-053` | Espaço sem tentativas | Consultar taxa | Exibe “sem dados”, não `0%` | P1 | V0.4 |
| `CT-048` | Agrupar atividade por data local | `RN-054`, `RNF-067` | Instantes próximos à meia-noite UTC | Consultar “hoje” em dois fusos | Cada evento pertence à data local do espaço | P0 | V0.4 |
| `CT-049` | Reconciliar fila | `RF-034`–`RF-037`, `RN-055` | Pendentes hoje, atrasadas, futuras e suspensas | Abrir fila/dashboard | Totais coincidem com consulta autoritativa por estado | P0 | V0.4 |
| `CT-050` | Agrupar pela hierarquia atual | `RN-056` | Questão movida de assunto com história | Consultar métrica atual e histórica | Atual usa vínculo corrente; histórico explicitamente rotulado preserva contexto | P1 | V0.4 |
| `CT-051` | Contar categoria corrigida | `RN-057` | Diagnóstico alterado | Abrir frequência atual | Categoria atual conta uma vez; relatório auditável mostra mudança | P1 | V0.4 |
| `CT-052` | Reconciliar drill-down | `RF-052`–`RF-056`, `RNF-029` | `DAD-003` | Abrir cartão e itens detalhados | Soma dos itens explica exatamente o total exibido | P0 | V0.4 |
| `CT-053` | Validar período e arredondamento | `RN-058` | Valores 1/3 e eventos na fronteira | Aplicar intervalo inclusivo definido | Eventos corretos; cálculo interno preciso e apresentação arredondada conforme padrão | P1 | V0.4 |
| `CT-054` | Tratar arquivados | `RN-059`, `RN-076` | Questão arquivada após tentativas | Comparar visão atual/histórica | Atual exclui onde definido; história continua reconciliável e rotulada | P1 | V0.4 |

### 9.5 Índice de Domínio, confiança e prioridade — V1

| ID | Objetivo | Rastreabilidade | Pré-condição e entrada | Passos | Resultado esperado | Pri. | Fase |
|---|---|---|---|---|---|---|---|
| `CT-055` | Calcular `Aq` ponderado | `RN-068`, `RN-069` | Resultados recentes 1,0,1,1,0 | Aplicar pesos 1;0,7;0,49;0,343;0,2401 | Valor coincide com cálculo manual e usa no máximo cinco válidas | P0 | V0.5-B |
| `CT-056` | Mapear `Pq` | `RN-068` | Maior etapa nenhuma/D1/D7/D14/D30 | Calcular cada vetor | Retorna 0/25/50/75/100 | P0 | V0.5-B |
| `CT-057` | Calcular `Fq` | `RN-068` | Fácil, média, difícil e ausente | Calcular até três corretas recentes | 100/75/50; média correta; ausência usa 75 e é explicada | P0 | V0.5-B |
| `CT-058` | Calcular `Eq` | `RN-068` | <2 tentativas; 0,1,2 erros de revisão | Calcular | 50/100/50/0 conforme tabela | P0 | V0.5-B |
| `CT-059` | Aplicar `DOM-HEUR-1.0` | `RN-068` | `Aq=80`, `Pq=75`, `Fq=100`, `Eq=50` | Calcular `0,45A+0,30P+0,15F+0,10E` | `M_q=78,5`, versão e componentes disponíveis | P0 | V0.5-B |
| `CT-060` | Aplicar tetos pós-erro | `RN-070` | Valor bruto 95; recuperação nenhuma/D1/D7/D14/D30 | Calcular | Resultado limitado a 40/60/75/90/95 | P0 | V0.5-B |
| `CT-061` | Calcular confiança-base | `RN-072` | Inicial e etapas tentadas sucessivas | Calcular | Base 20/40/60/80/100 | P0 | V0.5-B |
| `CT-062` | Envelhecer confiança | `RN-073` | Idades 60,61,120,121,180,181,365,366 | Calcular `C_q` | Fatores 1/0,9/0,75/0,5/0,25 nas fronteiras corretas; `M_q` não muda | P0 | V0.5-B |
| `CT-063` | Dar peso igual por questão | `RN-074`, `RN-075` | Q1 com 50 tentativas e M=100; Q2 com 1 e M=0 | Agregar assunto | `M_h=50`; frequência não aumenta peso | P0 | V0.5-B |
| `CT-064` | Calcular confiança hierárquica | `RN-077` | 6 questões; `Cob_h=75` | Aplicar `0,60N+0,40Cob` | `N_h=60`, `C_h=66`; faixa moderada | P0 | V0.5-B |
| `CT-065` | Rotular domínio e insuficiência | `RN-077`, `RN-078` | Valores em todas as fronteiras; `C_h<40` | Exibir | Rótulos seguem faixas; domínio aparece provisório com evidência insuficiente | P1 | V0.5-B |
| `CT-066` | Exigir todos os critérios de domínio | `RN-079` | D30 correta, M=85, C=80, duas últimas corretas, sem atraso, ativa | Avaliar | Questão é dominada somente com os seis critérios simultâneos | P0 | V0.5-B |
| `CT-067` | Negar domínio por um critério | `RN-079` | Variar um dos seis critérios por execução | Avaliar vetores parametrizados | Qualquer critério falso impede domínio e explica a razão | P0 | V0.5-B |
| `CT-068` | Reabrir por novo erro | `RN-080` | Questão dominada | Registrar erro válido | Sai de dominada imediatamente; novo D1; história preservada | P0 | V0.5-B |
| `CT-069` | Reabrir por evidência/anulação | `RN-080` | Questão dominada | Arquivar, envelhecer abaixo de 80 ou anular evidência essencial | Estado é removido em cada cenário e motivo é auditável | P0 | V0.5-B |
| `CT-070` | Calcular `PRI-HEUR-1.0` | `RN-082` | W=80,O=50,R=25,D=10 | Calcular prioridade | Resultado 53; versão e fatores são exibidos | P0 | V0.5-B |
| `CT-071` | Excluir baixa confiança do ranking | `RN-081` | `C_h=39,99`; revisões atrasadas | Gerar recomendação e fila | Assunto = “coletar mais evidências”; atrasos continuam visíveis | P0 | V0.5-B |
| `CT-072` | Explicar recomendação | `RN-083`, `RN-084` | Dois assuntos elegíveis | Gerar e ignorar recomendação | Fatores dominantes aparecem; escolha do usuário não altera dados/revisões | P1 | V0.5-B |

### 9.6 Banco de dados, integridade e migrações

| ID | Objetivo | Rastreabilidade | Pré-condição e entrada | Passos | Resultado esperado | Pri. | Fase |
|---|---|---|---|---|---|---|---|
| `CT-073` | Aplicar chaves estrangeiras | `RNF-027`, modelo físico | IDs pais inexistentes | Inserir por serviço e acesso direto controlado | Ambos rejeitam; zero órfãos | P0 | V0.1–V0.3 |
| `CT-074` | Impedir vínculo entre espaços | `MD-DEC-003`, `RNF-013` | Entidades de A e B | Criar relacionamento cruzado | Constraint/serviço rejeita | P0 | V0.1–V0.3 |
| `CT-075` | Garantir revisão atual única | `RF-015`, `RF-017`, `RF-018`, `RN-019`, `RN-020`, `MD-DEC-004`, Modelo §6.6 | Questão existente | Marcar duas revisões como atuais | Constraint impede duplicidade | P0 | V0.2 |
| `CT-076` | Garantir tentativa inicial única | `MD-DEC-011` | Questão/ciclo aplicável | Inserir duas iniciais válidas | Apenas uma aceita | P0 | V0.3 |
| `CT-077` | Garantir tentativa de revisão única | `MD-DEC-012` | Uma revisão | Associar duas tentativas válidas | Apenas uma aceita; anulada segue regra formal | P0 | V0.3 |
| `CT-078` | Garantir ciclo ativo único | `MD-DEC-013` | Questão com ciclo ativo | Criar segundo ciclo ativo | Rejeição; ciclo concluído histórico permanece | P0 | V0.3 |
| `CT-079` | Garantir pendência única | `MD-DEC-014` | Ciclo ativo | Criar duas pendentes | Rejeição no banco e serviço | P0 | V0.3 |
| `CT-080` | Validar recibo idempotente | `SDD-DEC-013` | Mesmo workspace/operação/chave | Inserir hash igual e diferente | Igual recupera resultado; diferente conflita | P0 | V0.3 |
| `CT-081` | Migrar banco vazio | `RNF-033`, `RNF-057` | Instalação limpa | Aplicar todas as migrações | Schema final íntegro e aplicação inicia | P0 | Cada versão |
| `CT-082` | Migrar cópia representativa | `RNF-033` | Base da versão anterior com `DAD-003` | Backup, migrar e reconciliar | Contagens, vínculos, datas e histórico preservados | P0 | Cada versão |
| `CT-083` | Recuperar falha de migração | `RNF-033`, `RNF-038` | Falha injetada no meio | Executar e restaurar | Versão recuperável volta sem perda além do RPO aceito | P0 | V0.4+ |
| `CT-084` | Manter semântica SQLite/PostgreSQL | `SDD-DEC-003` | Mesmo conjunto nos dois bancos | Rodar suite de constraints/transações | Resultados de domínio são equivalentes; diferenças documentadas | P1 | V0.5-C |

### 9.7 Interface, busca e acessibilidade

| ID | Objetivo | Rastreabilidade | Pré-condição e entrada | Passos | Resultado esperado | Pri. | Fase |
|---|---|---|---|---|---|---|---|
| `CT-085` | Buscar e filtrar no espaço | `RF-063`–`RF-065`, `RNF-002`, recorte de `FL-020` | `DAD-005`; termos com acento; na V0.2 somente estado e hierarquia | Na V0.2 buscar, aplicar filtros taxonômicos permitidos e limpar texto; ampliar combinações nas fases próprias | Resultados corretos, estáveis e somente do espaço atual | P1 | V0.2 parcial; V0.4 ampliado |
| `CT-086` | Paginar sem omissão | `RF-063`, `RNF-061`, recorte de `FL-020` | V0.2: conjunto determinístico com empates; V0.4: 10.000 questões | Navegar páginas e alterar item | Sem duplicação/omissão; desempate estável | P1 | V0.2 funcional; V0.4 carga |
| `CT-087` | Salvar filtro V1 | `RF-066`; `SavedFilter` | Filtro composto | Salvar, reabrir, renomear e excluir | Configuração pertence ao espaço e reproduz a consulta | P2 | V0.5-A/V1; não V0.2 |
| `CT-088` | Operar fluxo central por teclado | `RNF-044`–`RNF-049` | Navegador suportado | Cadastrar, responder, classificar e revisar sem mouse | Ordem/foco visíveis; todas as ações alcançáveis | P0 | V0.4 |
| `CT-089` | Gerenciar foco e erros | `RNF-046`, `RNF-049` | Formulário inválido e atualização HTMX | Submeter e corrigir | Foco vai ao resumo/campo; mensagem é associada e anunciada | P1 | V0.4 |
| `CT-090` | Fornecer nomes acessíveis | `RNF-046`, `RNF-049` | Leitor de tela/verificador | Percorrer controles e estados | Nome, função, valor e erro são compreensíveis | P1 | V0.4/V1 |
| `CT-091` | Não depender de cor | `RNF-047` | Estados correto/erro/atraso | Inspecionar em escala de cinza | Texto/ícone/semântica distinguem todos os estados | P1 | V0.4 |
| `CT-092` | Suportar zoom e largura | `RNF-048`, `RNF-065` | 360 px e 200% zoom | Executar fluxos centrais | Sem perda de conteúdo/ação ou rolagem bidimensional indevida | P1 | V0.4/V1 |
| `CT-093` | Ocultar resposta antes da submissão | `RN-022`, `RNF-016` | Questão aberta | Inspecionar HTML, atributos e respostas parciais | Gabarito/explicação protegida não constam no payload antecipado | P0 | V0.3 |
| `CT-094` | Preservar entrada após validação | `RF-014`, `RNF-007`, `FL-002`, `FL-005` | Formulário longo com um campo inválido | Submeter | Campos válidos permanecem; erro é claro; nenhuma duplicata criada | P1 | V0.2 |

### 9.8 Segurança e privacidade

| ID | Objetivo | Rastreabilidade | Pré-condição e entrada | Passos | Resultado esperado | Pri. | Fase |
|---|---|---|---|---|---|---|---|
| `CT-095` | Autorizar toda referência direta | `RNF-012`, `RNF-013` | Usuário A conhece ID de B | Testar GET/POST/DELETE aplicáveis | Resposta segura e indistinguível; nenhum efeito em B | P0 | Contínuo |
| `CT-096` | Bloquear CSRF | `RNF-017` | Sessão válida | Enviar mutação sem token/origem válida | Rejeição; estado inalterado | P0 | V0.2+ |
| `CT-097` | Neutralizar XSS | `RNF-016` | `DAD-004` com script/atributos perigosos | Salvar e renderizar em todas as telas | Conteúdo aparece escapado; nenhum script executa | P0 | V0.2+ |
| `CT-098` | Proteger sessão remota | `RNF-012`–`RNF-015` | Perfil de implantação remota | Inspecionar login, cookies e transporte | Autenticação e autorização obrigatórias; cookies seguros; HTTPS configurado | P0 | Antes de remoto |
| `CT-099` | Detectar segredos | `RNF-018` | Repositório/configuração de release | Executar scanner e inspeção | Nenhum segredo no código, log ou artefato | P0 | Contínuo |
| `CT-100` | Evitar conteúdo em logs | `RNF-020`–`RNF-022`, `RNF-068` | Erro com enunciado/resposta sensível | Provocar validação e exceção | Log contém IDs/correlação, não conteúdo integral | P0 | V0.3+ |
| `CT-101` | Validar token transitório | `SDD-DEC-014` | Token de outro espaço, expirado e alterado | Reutilizar | Todos rejeitados; tentativa não é criada | P0 | V0.3 |
| `CT-102` | Autorizar exportação | `RNF-024`, `RF-069` | Usuário sem acesso ao espaço | Solicitar/baixar exportação | Negado; arquivo não é gerado ou exposto | P0 | V0.5-C |
| `CT-103` | Endurecer arquivo de restauração | `RNF-039`–`RNF-041` | Arquivo com traversal, expansão excessiva ou schema falso | Validar/restaurar em sandbox | Rejeição antes de alterar dados; motivo seguro | P0 | V0.5-C |
| `CT-104` | Bloquear vulnerabilidade crítica | `RNF-019`, `RNF-080` | Dependências travadas | Executar análise no pipeline | Achado crítico explorável bloqueia release ou possui exceção formal com prazo | P0 | Contínuo |

### 9.9 Desempenho, escala e confiabilidade

| ID | Objetivo | Rastreabilidade | Pré-condição e entrada | Passos | Resultado esperado | Pri. | Fase |
|---|---|---|---|---|---|---|---|
| `CT-105` | Medir telas principais | `RNF-001`, `BCR-1` | Ambiente documentado; cache frio/quente | Medir dashboard, fila e questões | p95 ≤3 s, sem erro ou total divergente | P0 | V0.4/V1 |
| `CT-106` | Medir busca/filtros | `RNF-002`, `BCR-1` | Consultas representativas | Executar carga e registrar percentis | p95 ≤2 s; isolamento preservado | P1 | V0.4/V1 |
| `CT-107` | Medir gravações críticas | `RNF-003`, `BCR-1` | Tentativa, revisão e questão | Executar carga controlada | p95 ≤2 s; confirmação implica persistência | P0 | V0.3/V1 |
| `CT-108` | Atualizar dashboard | `RNF-004` | Operação confirmada | Cronometrar até nova leitura | Totais corretos em até 3 s | P1 | V0.4 |
| `CT-109` | Degradar com segurança em 2× | `RNF-005`, `BCR-2` | Duas vezes o baseline | Estressar leitura/escrita | Sem corrupção, duplicação ou falha silenciosa; degradação registrada | P0 | V1.0 |
| `CT-110` | Evitar recálculo integral/N+1 | `RNF-060`, `RNF-061` | `BCR-1` | Perfilar tentativa, fila e paginação | Trabalho cresce conforme subconjunto previsto; memória/queries dentro do orçamento medido | P1 | V0.4/V1 |
| `CT-111` | Recuperar contenção SQLite | `RNF-031`, `SDD-DEC-003` | Escritas concorrentes | Forçar lock e repetir política prevista | Erro é recuperável/explicado; nenhuma confirmação falsa | P0 | V0.3 |
| `CT-112` | Reproduzir benchmark | `RNF-078`, `RNF-079` | Mesma semente e ambiente | Rodar duas execuções | Contagens idênticas; variação de latência registrada e analisável | P1 | V0.4/V1 |

### 9.10 Backup, restauração, exportação e portabilidade

| ID | Objetivo | Rastreabilidade | Pré-condição e entrada | Passos | Resultado esperado | Pri. | Fase |
|---|---|---|---|---|---|---|---|
| `CT-113` | Criar backup consistente | `RNF-034`, `RNF-036` | `DAD-003`; escrita concorrente controlada | Gerar backup e verificar | Snapshot corresponde a ponto consistente e contém manifesto/checksum | P0 | V0.4 |
| `CT-114` | Detectar corrupção | `RNF-036` | Backup válido com byte alterado | Validar | Corrupção detectada antes de substituir destino | P0 | V0.4 |
| `CT-115` | Restaurar integralmente | `RNF-034`, `RNF-038` | `DAD-007` válido | Restaurar em `TST-REC`, iniciar e reconciliar | Questões, tentativas, erros, ciclos, revisões e configurações coincidem | P0 | V0.4 |
| `CT-116` | Cumprir RPO/RTO | `RNF-035` | Política 24 h/4 h; cronômetro | Simular perda e recuperação | Perda máxima ≤24 h; operação volta ≤4 h | P0 | Antes do piloto |
| `CT-117` | Proteger restauração existente | `RNF-039` | Destino com dados e arquivo inválido/falha | Iniciar restauração | Pré-backup/estratégia de retorno preserva destino; falha não deixa mistura | P0 | V0.5-C |
| `CT-118` | Exportar formato aberto | `RF-069`, `RNF-040`–`RNF-042` | Conjunto conhecido | Exportar e ler com ferramenta independente | UTF-8, versão/data e relações documentadas; totais reconciliam | P0 | V0.5-C |
| `CT-119` | Fazer ida e volta | `RNF-041`, `RNF-042` | Exportação completa | Exportar, importar/restaurar em espaço vazio e reexportar | Sem perda semântica; manifestos e registros autoritativos equivalentes | P0 | V0.5-C |
| `CT-120` | Rejeitar versão incompatível | `RNF-041` | Versão futura/desconhecida | Importar/restaurar | Rejeição clara antes de mutação; arquivo original permanece intacto | P0 | V0.5-C |

### 9.11 Regressão, compatibilidade e usabilidade

| ID | Objetivo | Rastreabilidade | Pré-condição e entrada | Passos | Resultado esperado | Pri. | Fase |
|---|---|---|---|---|---|---|---|
| `CT-121` | Validar jornada ponta a ponta | `FL-001`–`FL-022`, `RNF-077` | Instalação limpa; `DAD-002` | Cadastrar, errar, classificar, concluir D1/D7/D14/D30 e abrir dashboard | Jornada fecha com história/métricas reconciliadas | P0 | V0.4/V1 |
| `CT-122` | Preservar dados entre versões | `RNF-033`, `RNF-057` | Banco de cada release anterior suportado | Atualizar sequencialmente até atual | Aplicação abre e suite de reconciliação passa | P0 | V0.2+ e cada release posterior |
| `CT-123` | Executar smoke crítico aplicável | `RNF-080` | Build de release e matriz de capacidades da versão | Rodar bootstrap/configuração, migração e backup; acrescentar questão, tentativa, revisão e dashboard somente nas versões em que existirem | Todas as capacidades presentes na versão são aprovadas; ausência planejada de capacidade futura não é falha; qualquer falha aplicável bloqueia promoção | P0 | Cada release |
| `CT-124` | Avaliar cadastro rápido | `RF-014`, `RNF-006`, `RNF-007`, `FL-002` | 5 participantes representativos; roteiro | Criar questão válida e corrigir erro | ≥90% concluem sem ajuda crítica; perda de entrada = zero | P1 | V0.2/V0.4 |
| `CT-125` | Avaliar pós-resposta | `RNF-009`–`RNF-011` | Participantes; resposta errada | Identificar resultado e classificar causa | ≥90% entendem próximo passo; termos ambíguos viram achados | P1 | V0.3/V0.4 |
| `CT-126` | Avaliar fila/dashboard | `RNF-006`, `RNF-009` | `DAD-003` | Encontrar o que revisar e explicar um total | ≥90% concluem; totais são interpretados corretamente | P1 | V0.4/V1 |
| `CT-127` | Validar instalação Windows limpa | `RF-067`, `RNF-053`, `RNF-056`, `RNF-063`, `RD-DEC-002` | Windows 11 sem ambiente prévio além dos pré-requisitos declarados | Seguir somente o README para instalar dependências, configurar perfil local, migrar, inicializar e executar o smoke da versão | Usuário inicia a V0.1 sem conhecimento não documentado; o caso volta a ser executado nos gates V0.4/V1 | P1 | V0.1; regressão V0.4/V1 |
| `CT-128` | Validar Chrome/Edge e responsividade | `RNF-063`–`RNF-065` | Versões suportadas; 360–1920 px | Rodar smoke visual/funcional | Sem perda funcional; diferenças aceitáveis documentadas | P1 | V0.4/V1 |

### 9.12 Casos técnicos formalizados para a V0.1

| ID | Objetivo | Rastreabilidade | Pré-condição e entrada | Passos | Resultado esperado | Pri. | Fase |
|---|---|---|---|---|---|---|---|
| `CT-129` | Tornar o bootstrap/seed idempotente | `RF-001`, `RF-029`, `RN-001`, `RN-029`, `RNF-027`, `FL-023` | Instalação sem espaço; fuso IANA escolhido; bootstrap disponível | Executar a inicialização duas vezes com a mesma entrada e consultar usuário, espaço e categorias | Existe um `User` UUID, um `Workspace` e exatamente dez categorias padrão com códigos estáveis; a segunda execução recupera o resultado sem duplicar | P0 | V0.1 |
| `CT-130` | Separar perfis e proteger dados reais | `RF-067`, `RNF-018`, `RNF-054`, `RNF-056`, `RNF-079`, `SDD-ABR-001` | Perfis desenvolvimento, teste e produção local; banco local sentinela | Iniciar cada perfil; executar a suite; inspecionar conexão e configuração efetivas | Perfis diferem somente por configuração autorizada; teste usa banco descartável, não lê/escreve o sentinela e não recebe segredos de produção | P0 | V0.1 |
| `CT-131` | Verificar diagnóstico/health local | `RF-067`, `RF-068`, `RNF-068`, `RNF-070`, `RNF-072` | Aplicação local; banco disponível e depois indisponível | Consultar a rota/comando nos dois estados e inspecionar a resposta | Estado saudável somente quando aplicação e persistência estão prontas; falha de banco não retorna prontidão; resposta não revela segredo, caminho privado ou configuração sensível | P1 | V0.1 |
| `CT-132` | Criar backup mínimo consistente | `RF-068`, `RNF-034`, `RNF-036`, `RNF-038`, `SDD-ADR-006`, `FL-022` | Banco V0.1 vazio ou mínimo com usuário, espaço, fuso e categorias | Executar backup pelo mecanismo consistente do SQLite; validar manifesto, tamanho e SHA-256 | Arquivo representa um ponto consistente, fica fora do principal e possui versão, instante, tamanho e checksum verificáveis | P0 | V0.1 |
| `CT-133` | Restaurar backup mínimo isoladamente | `RF-068`, `RNF-034`, `RNF-036`, `RNF-038`, `FL-022` | Backup de `CT-132`; destino `TST-REC`; cópia corrompida adicional | Validar/restaurar o arquivo íntegro; iniciar aplicação e reconciliar; repetir validação com arquivo corrompido | Íntegro restaura usuário, espaço, fuso e dez categorias; corrompido é rejeitado antes de substituir dados; nenhum ambiente real é tocado | P0 | V0.1 |
| `CT-134` | Sanitizar e correlacionar logs | `RNF-018`, `RNF-022`, `RNF-068`–`RNF-070` | Valores sentinela de segredo e conteúdo privado em erro controlado | Provocar inicialização, validação e falha de backup; buscar sentinelas e correlação nos logs | Logs possuem horário, nível, evento, correlação, operação e resultado, mas não segredo, conteúdo integral, stack trace inseguro ou corpo privado | P0 | V0.1 |
| `CT-135` | Controlar `Clock` e `Calendar` | `RF-002`, `RF-003`, `RN-002`–`005`, `RNF-030`, `RNF-067`, `RNF-074` | Dois instantes fixos e dois fusos IANA, incluindo fronteira de data | Obter `now`, calcular `today` e somar dias sem alterar o relógio do sistema | Mesmas entradas produzem mesmos instantes/datas; fusos podem produzir dias locais distintos; mudança de fuso não reescreve o instante fixado | P0 | V0.1 |
| `CT-136` | Validar layout/configuração base acessível | `RF-001`–`RF-003`, `RNF-044`–`RNF-049`, `RNF-063`, `RNF-065`, `RNF-066`, `FL-023` | Navegação mínima e configuração; Chrome/Edge; teclado; 360 px e zoom 200% | Percorrer primeiro acesso, cancelar/confirmar fuso, provocar erro e navegar sem mouse | Foco é visível e lógico; rótulos/erros são anunciáveis; nenhuma ação depende só de cor; Unicode é preservado; não há perda funcional no escopo da V0.1 | P1 | V0.1 |

### 9.13 Casos formalizados para a V0.2 — `ERR-V02-008`

| ID | Objetivo | Rastreabilidade | Pré-condição e entrada | Passos | Resultado esperado | Pri. | Fase |
|---|---|---|---|---|---|---|---|
| `CT-137` | Gerenciar e arquivar taxonomia | `RF-004`–`RF-008`, `RN-006`–`RN-009`, `RNF-027`, `RNF-031`, `FL-001`, `SDD-MOD-002`, `MD-DEC-002`, `MD-DEC-003` | Workspace válido; hierarquia ativa com e sem vínculos | Criar, consultar, renomear com lock, arquivar cada nível e tentar novo vínculo/descendente | Nomes e vínculos permanecem íntegros; cadeia arquivada fica indisponível para novos vínculos; descendentes não têm o estado alterado automaticamente; nenhuma exclusão ocorre | P0 | V0.2 |
| `CT-138` | Validar origem mínima | `RF-012`, `RF-015`, `RF-017`, `RN-014`, `RN-019`, `RN-086`, `RNF-013`, `RNF-027`, `RNF-074`, `FL-002`, `FL-005`, `SDD-MOD-003`, Modelo §6.1–6.5, `ERR-V02-006` | Dois Workspaces; Clock controlado; Board/Exam/Source opcionais; anos 1899, 1900, atual+2 e atual+3 | Criar/reusar referências normalizadas; associar origem; tentar mistura de Workspace e coexistência indevida de prova/banca | Omissão é aceita; limites válidos persistem; inválidos são rejeitados; com prova a banca deriva de Exam; origem e referências nunca cruzam Workspace | P1 | V0.2 |
| `CT-139` | Exibir detalhe sem valores fictícios | `RF-013`, `RF-015`, recorte de `RF-016`, `RN-014`–`RN-017`, `FL-004`, `SDD-MOD-003`, `ERR-V02-004` | Questões rascunho, ativa e arquivada, com e sem dificuldade/origem/conteúdo opcional | Abrir detalhes e comparar dados persistidos, ausências e estado | Estado e dados presentes são fiéis; ausência é indicada como não informada; nenhuma tentativa, ciclo, fila, métrica ou aprendizagem fictícia é exibida | P1 | V0.2 |
| `CT-140` | Versionar alteração crítica antes de tentativa | `RF-018`, `RN-020`, `RNF-028`, `RNF-031`, `FL-005`, `SDD-SVC-001`, `MD-DEC-004`, `MD-DEC-006`, `ERR-V02-007` | Questão ativa com revisão corrente de número 1 e sem entidade Attempt | Alterar alternativas/gabarito com lock válido e depois simular conflito/falha | Nova revisão válida torna-se a única corrente; anterior e alternativas permanecem imutáveis; gabarito pertence à nova revisão; conflito/falha preserva a corrente anterior | P0 | V0.2 |
| `CT-141` | Carregar fixture sintética reproduzível | `RNF-020`, `RNF-078`, `RNF-079`, Roadmap V0.2, `ADR-010` | Banco descartável; semente e Workspace de teste explícitos | Carregar duas vezes em ambientes isolados e inspecionar conteúdo/identidades | Mesma semente produz catálogo equivalente sem duplicação, dado pessoal real ou escrita em ambiente real; fixture não é data migration nem carga automática | P1 | V0.2 |
| `CT-142` | Validar acessibilidade do catálogo | `RF-004`–`RF-019`, `RF-063`–`RF-065`, `RNF-044`–`RNF-049`, `RNF-063`, `RNF-065`, `RNF-066`, `FL-001`, `FL-002`, `FL-004`, `FL-005`, `FL-006`, `FL-020` | Chrome/Edge vigentes; teclado; aproximadamente 360 px; zoom 200%; dados sintéticos | Criar/editar taxonomia e questão, corrigir validação, pesquisar e arquivar sem mouse; repetir inspeção responsiva | Foco e ordem são lógicos/visíveis; controles, filtros e erros possuem nomes/associações; conteúdo e ações permanecem disponíveis sem rolagem horizontal indevida | P0 | V0.2 |
| `CT-143` | Recuperar catálogo V0.2 | `RF-068`, `RNF-034`, `RNF-036`, `RNF-038`, `FL-022`, `ERR-V02-009` | Base V0.2 sintética com taxonomia, origem, rascunho, questão ativa/arquivada e duas revisões | Gerar/verificar backup, restaurar isoladamente e reconciliar; repetir com cópia corrompida | Íntegro preserva contagens, FKs, estados, revisão corrente e gabarito; corrompido é rejeitado antes de substituir; nenhum ambiente real é tocado | P0 | V0.2 |
| `CT-144` | Não bloquear similaridade semântica | `RN-018`, `SDD-MOD-003`, `ADR-010` | Duas questões válidas do mesmo Workspace com enunciados iguais ou semelhantes e identidades próprias | Cadastrar ambas pelo serviço | Ambas persistem; somente invariantes estruturais são aplicadas; não há comparação semântica, FTS ou alerta de duplicidade | P1 | V0.2 |

## 10. Casos críticos expandidos

### `CT-014` — Erro inicial cria ciclo D1 atomicamente

- **Objetivo:** provar o nascimento correto do ciclo de aprendizagem.
- **Requisitos:** `RF-021` a `RF-036`, `RN-024`, `RN-037`, `RNF-025`.
- **Pré-condição:** questão ativa sem tentativa; clock em 10/08/2026 14:00 no fuso do espaço.
- **Entrada:** alternativa incorreta, categoria “cálculo”, observação opcional válida e chave idempotente nova.
- **Passos:** responder; conferir resultado; classificar; concluir; consultar tentativa, erro, ciclo e revisão.
- **Resultado esperado:** exatamente uma tentativa inicial errada, um diagnóstico, um ciclo ativo e uma D1 pendente para 11/08; todos compartilham o espaço e vínculos corretos; nenhuma gravação parcial é visível.
- **Prioridade/fase:** P0, V0.3.

### `CT-039` — Falha intermediária não deixa estado parcial

- **Objetivo:** validar a fronteira transacional da conclusão.
- **Requisitos:** `RNF-025`, `RNF-026`, `RNF-032`, `SDD-DEC-012`.
- **Pré-condição:** mesma base de `CT-014`; ponto de falha injetável entre persistir tentativa e criar D1.
- **Entrada:** resposta errada e diagnóstico válido.
- **Passos:** executar com falha; inspecionar banco e mensagem; remover falha; repetir com a mesma chave.
- **Resultado esperado:** primeira execução reverte tudo e informa falha; repetição conclui uma única vez; recibo idempotente não registra sucesso inexistente.
- **Prioridade/fase:** P0, V0.3.

### `CT-066` — Domínio exige conjunção completa

- **Objetivo:** impedir rótulo de domínio baseado apenas em pontuação.
- **Requisitos:** `RN-079`, `RF-061`.
- **Pré-condição:** vetores determinísticos com os seis critérios de `RN-079`.
- **Entrada:** cenário base válido e seis variações, cada qual removendo um critério.
- **Passos:** avaliar cenário base; executar variações; verificar explicação.
- **Resultado esperado:** apenas o cenário base é dominado; cada variação não dominada identifica D30, `M_q`, `C_q`, últimos resultados, atraso ou estado ativo como causa.
- **Prioridade/fase:** P0, V0.5-B.

### `CT-119` — Portabilidade por ida e volta

- **Objetivo:** demonstrar que o estudante consegue recuperar dados fora da instância original.
- **Requisitos:** `RF-069`, `RNF-040` a `RNF-043`.
- **Pré-condição:** conjunto com Unicode, revisões concluídas/pendentes, correções e regras versionadas.
- **Entrada:** arquivo exportado e instalação vazia compatível.
- **Passos:** exportar; validar com leitor independente; importar/restaurar; reconciliar; reexportar.
- **Resultado esperado:** manifestos, contagens, relações e fatos autoritativos equivalem; diferenças de campos derivados são justificadas por recálculo versionado, nunca por perda silenciosa.
- **Prioridade/fase:** P0, V0.5-C.

## 11. Cobertura e rastreabilidade

### 11.1 Metas

| Área | Meta mínima | Complemento obrigatório |
|---|---:|---|
| Domínio e regras | 80% de linhas | 100% das decisões críticas e fronteiras mapeadas |
| Serviços transacionais | 85% de linhas | falha em cada fronteira e idempotência |
| Views/formulários | 75% de linhas | fluxos P0/P1 no cliente HTTP |
| Migrações | não medida isoladamente | instalação limpa, upgrade e recuperação |
| JavaScript/HTMX próprio | 75% quando houver lógica | jornada real no navegador |

Redução de cobertura exige justificativa no pull request; crescimento artificial por testes sem assertiva relevante não é aceito.

### 11.2 Matriz por fonte

| Fonte aprovada | Casos principais |
|---|---|
| Visão e Escopo | `CT-001`, `CT-005`, `CT-013`, `CT-014`, `CT-121`, `CT-127`, `CT-129` |
| Requisitos Funcionais | `CT-001`–`CT-012`, `CT-013`–`CT-054`, `CT-085`–`CT-094`, `CT-118`–`CT-121`, `CT-127`, `CT-129`–`CT-140`, `CT-142`, `CT-143` |
| Requisitos Não Funcionais | `CT-001`, `CT-002`, `CT-035`–`CT-040`, `CT-073`–`CT-084`, `CT-088`–`CT-143` |
| Regras de Negócio | `CT-001`–`CT-072`, `CT-129`, `CT-135`, `CT-137`–`CT-140`, `CT-144` |
| SDD | `CT-022`, `CT-037`–`CT-040`, `CT-080`, `CT-084`, `CT-101`, `CT-111`, `CT-130`, `CT-132`, `CT-137`–`CT-144` |
| Modelo de Dados | `CT-073`–`CT-084`, `CT-113`–`CT-120`, `CT-129`, `CT-137`–`CT-140`, `CT-143`, `CT-144` |
| Fluxos | `CT-001`, `CT-002`, `CT-011`, `CT-013`–`CT-044`, `CT-085`–`CT-094`, `CT-121`, `CT-129`, `CT-132`, `CT-133`, `CT-136`–`CT-143` |
| Roadmap | Gates da seção 8 e `CT-122`–`CT-144` |

Uma matriz executável posterior deverá relacionar cada `RF`, `RN`, `RNF`, fluxo e decisão a pelo menos um teste ou justificar “não aplicável”.

## 12. Regressão e pipeline

### 12.1 Ordem recomendada

1. análise estática, segredos e validação de migrações;
2. testes unitários de domínio;
3. integração SQLite e autorização;
4. casos funcionais HTTP;
5. navegador central e acessibilidade automatizada;
6. compatibilidade PostgreSQL quando ativada;
7. desempenho, restauração e usabilidade em jobs/marcos próprios.

### 12.2 Suites

- **Smoke:** P0 essenciais, alvo de poucos minutos.
- **Pull request:** unitários, integração, segurança básica e P0/P1 afetados.
- **Noturna:** navegador completo, combinações temporais e banco alternativo.
- **Release:** regressão total, migração, backup/restauração, acessibilidade e segurança.
- **Marco:** `BCR-1`, `BCR-2`, usabilidade e exercício operacional.

Teste instável é defeito. Ele pode ser isolado temporariamente somente com responsável, prazo e cobertura compensatória; nunca pode ocultar falha P0.

## 13. Desempenho

O relatório `PERF` registrará CPU, memória, disco, sistema operacional, versões, banco, semente, cache, concorrência e percentis. Média isolada não comprova requisito.

| Operação | Carga | Meta |
|---|---|---|
| Dashboard, fila e questões | `BCR-1` | p95 ≤3 s |
| Busca e filtros | `BCR-1` | p95 ≤2 s |
| Salvar questão/tentativa/revisão | `BCR-1` | p95 ≤2 s |
| Atualizar dashboard após confirmação | `BCR-1` | ≤3 s |
| Estresse V1 | `BCR-2` | sem perda/corrupção/falha silenciosa; degradação publicada |

O ambiente exato permanece ponto aberto controlado. Até sua medição na V0.1, resultados não deverão ser comparados como se viessem do mesmo hardware.

## 14. Segurança e privacidade

O gate inclui autorização por objeto e espaço, CSRF, XSS, validação de arquivos, sessão remota, dependências, segredos e conteúdo de logs. Testes ativos são executados somente em ambientes autorizados e descartáveis.

Achado crítico explorável, vazamento entre espaços, exposição de gabarito ou possibilidade de substituir dados por arquivo não validado bloqueiam imediatamente a liberação. Achados menores recebem severidade, prazo e decisão registrada.

## 15. Backup, restauração e continuidade

Antes do piloto com dados reais:

- backup deve conter todos os fatos e configurações necessários;
- checksum/integridade deve ser verificado antes da restauração;
- restauração deve ocorrer em ambiente isolado e ser reconciliada;
- RPO máximo deve ser 24 horas e RTO máximo, 4 horas;
- ao menos sete versões diárias e quatro semanais devem ser verificáveis durante o piloto contínuo;
- migração relevante exige novo exercício de restauração.

Backup nunca restaurado é classificado como não validado.

## 16. Usabilidade e acessibilidade

Sessões de usabilidade usam tarefas, não demonstrações guiadas. O moderador registra sucesso, tempo, pedido de ajuda, erro, abandono e comentário. Meta inicial para tarefas centrais: pelo menos 90% dos participantes representativos concluem sem ajuda crítica; qualquer perda de dados ou impossibilidade de corrigir erro é bloqueadora independentemente da taxa.

Automação de acessibilidade não substitui:

- percurso integral por teclado;
- foco após validação e atualização dinâmica;
- leitura dos estados por tecnologia assistiva;
- inspeção de contraste, zoom, responsividade e independência de cor.

## 17. Gestão de defeitos

| Severidade | Definição | Efeito |
|---|---|---|
| S1 — Crítica | Perda/corrupção, vazamento, execução indevida, backup irrecuperável | bloqueia tudo; correção e análise de causa |
| S2 — Alta | Fluxo central indisponível, métrica/regra crítica errada, migração quebrada | bloqueia versão |
| S3 — Média | Função secundária com contorno seguro, acessibilidade localizada | corrigir na versão ou aceitar formalmente |
| S4 — Baixa | Texto, estética ou conveniência sem risco funcional | backlog priorizado |

Todo defeito contém ambiente, versão, caso relacionado, passos, esperado, observado, evidência e impacto nos dados. Correção exige teste de regressão que falhe antes e passe depois, quando tecnicamente possível.

## 18. Evidências e relatório de execução

Cada execução de release produzirá:

- versão/commit e configuração;
- suites executadas e casos não aplicáveis;
- aprovados, falhos, bloqueados e não executados;
- cobertura por área;
- defeitos e exceções aceitas;
- migrações testadas;
- resumo de segurança/acessibilidade;
- relatório de desempenho aplicável;
- identificação do último exercício de restauração;
- decisão final de promover ou rejeitar.

Evidências não devem conter enunciados, respostas pessoais ou segredos. Logs usam IDs sintéticos e correlação.

## 19. Decisões propostas nesta etapa

| ID | Decisão |
|---|---|
| `PT-DEC-001` | Casos usarão identificadores permanentes `CT-NNN` e vínculo no código automatizado. |
| `PT-DEC-002` | P0/P1 aplicáveis e ausência de S1/S2 são condições mínimas de saída. |
| `PT-DEC-003` | Domínio/regras manterão pelo menos 80% de linhas e casos explícitos de todas as fronteiras críticas. |
| `PT-DEC-004` | Clock, IDs, sementes e dados críticos serão controláveis e reproduzíveis. |
| `PT-DEC-005` | SQLite será o banco principal de testes do MVP; PostgreSQL terá suite equivalente antes de uso remoto. |
| `PT-DEC-006` | `BCR-1` será determinístico; `BCR-2` será o estresse de segurança da V1. |
| `PT-DEC-007` | Percentil 95, e não média isolada, decidirá metas de latência. |
| `PT-DEC-008` | Conclusão de tentativa/revisão terá testes obrigatórios de atomicidade, idempotência e concorrência. |
| `PT-DEC-009` | Fórmulas terão vetores independentes, versão e precisão antes de arredondamento. |
| `PT-DEC-010` | Backup somente será considerado válido após verificação e restauração reconciliada. |
| `PT-DEC-011` | Acessibilidade combinará automação, teclado, zoom e tecnologia assistiva. |
| `PT-DEC-012` | Teste instável será tratado como defeito e não poderá mascarar P0. |
| `PT-DEC-013` | Dados pessoais reais não serão usados na suite; piloto empregará cópia protegida somente em exercício autorizado. |
| `PT-DEC-014` | Cada correção de defeito deverá acrescentar regressão automatizada quando possível. |
| `PT-DEC-015` | A aprovação desta etapa encerra o ciclo documental inicial e autoriza a V0.1, sem autorizar mudanças silenciosas de escopo. |
| `PT-DEC-016` | A errata V0.1 adiciona `CT-129` a `CT-136`, antecipa `CT-127` e torna `CT-123` sensível à fase, sem antecipar capacidades posteriores. |
| `PT-DEC-017` | A errata V0.2 corrige os casos mistos por recorte de fase e adiciona `CT-137` a `CT-144`, sem criar entidades de aprendizagem antecipadas. |

## 20. Pontos ainda em aberto

| ID | Ponto | Momento de decisão |
|---|---|---|
| `PT-ABR-001` | Versões exatas de pytest, navegador e ferramentas auxiliares. | V0.1, junto às versões da stack. |
| `PT-ABR-002` | Hardware exato do ambiente `TST-PERF`. | V0.1; congelar antes do primeiro benchmark. |
| `PT-ABR-003` | Executor de carga e formato final do relatório `PERF`. | V0.3/V0.4. |
| `PT-ABR-004` | Verificador automatizado e combinação de leitores de tela. | V0.2/V0.4. |
| `PT-ABR-005` | Matriz móvel final da V1. | V0.5-C. |
| `PT-ABR-006` | Duração exata do contexto transitório pós-resposta. | Spike/teste V0.3. |
| `PT-ABR-007` | Orçamento de queries/memória por operação. | Após baseline V0.4. |
| `PT-ABR-008` | Critérios de desempate de prioridade e janela de recorrência/queda. | Antes de V0.5-B. |
| `PT-ABR-009` | Amostra e protocolo final das sessões de usabilidade. | Antes do piloto V0.4. |
| `PT-ABR-010` | Política de exceção para vulnerabilidades não críticas. | V0.1, processo de manutenção. |

## 21. Riscos e mitigação

| ID | Risco | Mitigação |
|---|---|---|
| `PT-RIS-001` | Cobertura percentual esconder regras não testadas. | Matriz de decisões/fronteiras e revisão de assertivas. |
| `PT-RIS-002` | E2E excessivo tornar pipeline lento e instável. | Pirâmide; regra no domínio e poucos fluxos completos. |
| `PT-RIS-003` | SQLite em memória divergir do arquivo real. | Suite com arquivo e pragmas reais; exercício operacional. |
| `PT-RIS-004` | Datas passarem localmente e falharem em outro fuso. | Clock injetado e matriz de fusos/fronteiras. |
| `PT-RIS-005` | Oráculo repetir o mesmo erro do código. | Vetores manuais independentes e exemplos revisados. |
| `PT-RIS-006` | Benchmark variar por ambiente. | Manifesto de hardware/software, percentis e repetição. |
| `PT-RIS-007` | Backup ser confundido com cópia de arquivo inconsistente. | Snapshot controlado, checksum e restauração. |
| `PT-RIS-008` | Testes usarem dados pessoais. | Geradores sintéticos e inspeção de artefatos/logs. |
| `PT-RIS-009` | Segurança ser adiada até hospedagem. | Baseline desde o MVP e gate adicional antes de exposição remota. |
| `PT-RIS-010` | Ferramenta de acessibilidade produzir falsa aprovação. | Testes humanos de teclado, foco, zoom e leitor de tela. |
| `PT-RIS-011` | Suite crescer sem orçamento de manutenção. | Classificar por prioridade, remover redundância e medir duração. |
| `PT-RIS-012` | Documentos e testes divergirem. | ID obrigatório e análise de impacto na mesma mudança. |

## 22. Sugestões de melhoria

1. Criar um comando único para gerar dados, migrar e executar smoke local.
2. Manter um painel simples de duração, instabilidade, cobertura e defeitos escapados.
3. Executar mutation testing seletivo nas políticas D1/D7/D14/D30 e nas fórmulas V1.
4. Preservar uma pequena base de versão anterior como fixture de migração, sem dados reais.
5. Revisar trimestralmente casos redundantes e fronteiras surgidas em produção/piloto.
6. Vincular demonstrações de cada versão aos mesmos dados e casos do gate.

## 23. Itens que precisam de aprovação

**Aprovação registrada:** aprovada integralmente pelo responsável do projeto em 30 de agosto de 2026.

Solicita-se aprovação de:

1. objetivos, tipos de teste e pirâmide de automação;
2. prioridades P0–P3 e severidades S1–S4;
3. ambientes `TST-*`, conjuntos `DAD-*`, `BCR-1` e `BCR-2`;
4. critérios de entrada, saída e suspensão;
5. gates por versão;
6. catálogo `CT-001` a `CT-144`;
7. metas de cobertura e rastreabilidade;
8. metas de desempenho p95 já congeladas nos RNFs;
9. política de segurança, privacidade e acessibilidade;
10. validação de backup por restauração reconciliada;
11. decisões `PT-DEC-001` a `PT-DEC-017`;
12. manutenção dos pontos `PT-ABR-001` a `PT-ABR-010` para decisão nos marcos indicados.

## 24. Critério de encerramento da documentação inicial

A Etapa 10 será concluída quando:

- todos os tipos de teste solicitados estiverem cobertos;
- casos críticos apresentarem objetivo, requisito, pré-condição, entrada, passos, esperado e prioridade;
- revisão espaçada, datas, estatísticas, domínio e prioridade possuírem oráculos determinísticos;
- integridade, concorrência, segurança, backup e restauração possuírem gates bloqueadores;
- roadmap e plano de testes concordarem sobre o que libera cada versão;
- pontos abertos estiverem atribuídos a marcos, sem bloquear indevidamente a V0.1;
- o responsável aprovar o documento.

Após a aprovação, as dez etapas documentais iniciais estarão congeladas. A implementação poderá começar pela **V0.1 — Fundação Executável**, acompanhada desde o primeiro commit pelos casos aplicáveis deste plano.

A etapa foi aprovada integralmente em 30 de agosto de 2026. A errata 1.0.1, registrada em 1º de setembro de 2026, corrige a rastreabilidade aplicável à V0.1, formaliza `CT-129` a `CT-136`, antecipa `CT-127` e ajusta a aplicabilidade de `CT-122`/`CT-123`. A errata 1.0.2, registrada em 5 de setembro de 2026, formaliza os recortes V0.2 e `CT-137` a `CT-144` por `ERR-V02-003` e `ERR-V02-008`. Os casos `CT-001` a `CT-144` e as decisões `PT-DEC-001` a `PT-DEC-017` passam a ser considerados congelados e somente poderão ser alterados mediante registro explícito e análise de impacto.
