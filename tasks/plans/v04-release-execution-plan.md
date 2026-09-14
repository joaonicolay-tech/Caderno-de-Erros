# Plano executável da Release V0.4

- ID da tarefa relacionada: `V0.4-P0`
- Status: `COMPLETED`
- Release: `V0.4 — Primeiro MVP local realmente utilizável`
- Baseline operacional: Project Development Architecture v1.0
- Autoridade de execução: cada etapa só poderá começar mediante novo contrato
  `AUTHORIZED` em `tasks/current.md`; este plano não autoriza implementação.

## 1. Objetivo, fontes e fronteiras

Entregar, ao fim da V0.4, uma jornada local contínua na qual o estudante possa
cadastrar e consultar questões, registrar erro inicial, concluir revisões,
compreender métricas e situação das revisões, navegar o histórico, recuperar os
dados e operar o produto no Windows com acessibilidade básica e evidência de
liberação.

Fontes aplicadas, sem usar intenção futura como prova de implementação:

1. contrato `V0.4-P0`;
2. Project Development Architecture v1.0 e estado promovido da V0.3;
3. Roadmap oficial, especialmente §§3.1, 7, 11, 13, 14, 17 e 18;
4. `RF-047`–`056`, `RF-063`–`068`, `RN-056`–`067`, RNFs e fluxos vinculados;
5. Plano de Testes, incluindo `CT-085`, `086`, `105`–`108`, `110`, `112`–`116`,
   `121`–`128` e regressões `129`–`143` aplicáveis;
6. SDD para serviços de leitura, backup/restore, logging, interface e Windows;
7. código e testes V0.3 apenas para confirmar o baseline executável;
8. ADR-012 e evidências finais V0.3 para os parâmetros vigentes do `BCR-1`.

Permanecem fora da implementação V0.4: domínio/prioridade, mastered/reopen,
reagendamento avançado, histórico de correções estruturais, categorias pessoais,
filtros salvos, exclusão permanente, exportação CEI pela UI, autenticação, API
pública, integrações, IA, OCR, anexos, notificações e gamificação. A restauração
da V0.4 é técnica; o fluxo de restore pela UI permanece V1. Gráficos, FTS,
snapshots/cache e instalador sofisticado só entram se uma medição ou decisão
posterior provar necessidade e houver autorização própria.

## 2. Auditoria do baseline real V0.3

### 2.1 Entregas reutilizáveis

- Workspace único, fuso IANA, `Clock`/`Calendar`, perfis locais, health e
  configuração reproduzível já existem.
- Taxonomia, origem, catálogo de questões, rascunho/ativação, edição versionada,
  arquivamento e detalhe fiel já existem e são isolados por Workspace.
- A listagem atual já oferece ativas por padrão, acesso explícito a rascunhos e
  arquivadas, busca textual em enunciado/explicação, filtros hierárquicos e por
  estado, empty state e paginação de dez itens com desempate total
  `-updated_at, id`.
- Tentativas iniciais e de revisão, classificação de erro, ciclo
  D1/D7/D14/D30, idempotência, fila de atrasadas/devidas/futuras e timeline de
  aprendizagem derivada dos fatos já existem.
- O detalhe versionado da questão, revisões de conteúdo e a timeline de
  aprendizagem existem em consultas/telas distintas; constituem base parcial
  para detalhe completo e histórico navegável.
- Logs estruturados/correlacionados e mensagens recuperáveis já cobrem a
  fundação e fluxos críticos da V0.3, com proteção contra conteúdo privado.
- Backup online consistente do SQLite, manifesto/checksum, validação de
  corrupção, restore em destino novo e reconciliação das entidades V0.3 já
  existem como serviços/comandos e testes automatizados.
- O gerador/executor sintético determinístico do `BCR-1` já prova as três
  gravações críticas com 10.000 questões, 100.000 tentativas, 100.000 revisões,
  três runs, 20 warm-ups, 100 amostras e p95 nearest-rank.
- Há baseline semântico/acessível e testes de templates para telas V0.1–V0.3,
  inclusive teclado, foco, labels, responsividade e zoom; telas novas ainda
  exigirão validação própria.

### 2.2 Lacunas para o MVP V0.4

- Ausentes: contratos executáveis de métricas, `StatisticsQueryService`/DTOs,
  dashboard, drill-down reconciliável, desempenho por taxonomia e frequência de
  categorias de erro.
- Parciais: consulta de questões (faltam filtros por situação de revisão,
  resultado inicial e erro, além da prova no `BCR-1`); detalhe/histórico (faltam
  integração e navegação completa); logs/mensagens (faltam cobertura dos novos
  fluxos); acessibilidade (faltam as telas V0.4 e validação transversal).
- Backup/restore é tecnicamente forte, mas ainda precisa de política operacional
  de uso real, retenção/RPO/RTO aplicáveis, documentação e exercício final com
  dados representativos antes do piloto.
- O `BCR-1` atual mede gravações V0.3, não as leituras V0.4 de dashboard, fila,
  listagem, busca e filtros exigidas por `CT-105`, `106`, `108`, `110` e `112`.
- Ausentes: invariant checker operacional, decisão mínima de inicialização/atalho
  Windows, guia de atualização/backup, piloto controlado e gate de promoção V0.4.

### 2.3 Divergências e tratamento

1. `PROJECT_STATE.md` anterior a P0 dizia “V0.4 não iniciada e não autorizada”,
   enquanto o contrato corrente autoriza somente o planejamento P0. O contrato é
   a autoridade de execução; o estado será corrigido no encerramento sem alegar
   implementação funcional.
2. O Roadmap trata listagem/pesquisa/filtros como entrega V0.4, mas uma parcela
   substancial já existe desde V0.2. A V0.4 amplia e valida o comportamento; não
   o reimplementa.
3. O Roadmap lista scripts de backup/restore como dependência V0.4, embora o
   mecanismo técnico e testes até V0.3 já existam. A etapa V0.4 fará gap
   assessment, extensão necessária, documentação e exercício; não presume que
   copiar SQLite seja suficiente.
4. `RF-065` formal inclui situação de revisão, resultado inicial e categoria de
   erro; a errata V0.2 limitou a entrega anterior a estado/hierarquia e remeteu
   filtros de aprendizagem à V0.4. Esses filtros permanecem responsabilidade da
   etapa V0.4-S4.
5. `RF-066` mistura combinar/limpar (MVP) e salvar filtros (V1). V0.4 implementa
   somente combinação, resumo visível e limpeza; `SavedFilter` continua fora.
6. O Plano de Testes mantém `CT-107` também como caso V1, mas ADR-012 e a prova
   V0.3 já fixaram e aprovaram as gravações vinculantes. V0.4 preserva esses
   thresholds e adiciona as leituras aplicáveis, sem redefini-los.
7. “Detalhe completo” não autoriza histórico de correções ou correção estrutural
   de tentativa/gabarito. Significa integrar os fatos e snapshots já suportados,
   com ausências explícitas e navegação segura.

## 3. Matriz de rastreabilidade

Estados: `existente` = comportamento executável já coberto; `parcial` = base
reutilizável, mas aceite V0.4 incompleto; `ausente` = capacidade ainda não
implementada; `precisa validação` = parece coberta, porém depende de prova V0.4.

| Requisito obrigatório | Etapa | Fonte de verdade | Estado atual | Evidência esperada | Dependências |
| --- | --- | --- | --- | --- | --- |
| Contratos explicáveis das métricas | S1 | RF-048–055; RN-056–067; SDD §13 | ausente | catálogo versionado e testes de exemplos/bordas | fatos V0.3 |
| Questões cadastradas | S1/S2 | RF-048; RN-056 | ausente | rascunhos + ativas + arquivadas, reconciliados por estado | contrato S1 |
| Questões realizadas | S1/S2 | RF-048; RN-057 | ausente | distintos `question_id` com tentativa inicial válida | contrato S1 |
| Tentativas | S1/S2 | RF-048/049; RN-058/061 | ausente | total e separação initial/review | contrato S1 |
| Acertos, erros e taxa | S1/S2 | RF-049; RN-059–061/067 | ausente | numerador + denominador + `sem dados` | contrato S1 |
| Período e filtros das métricas | S1/S2 | RF-055; RN-066 | ausente | intervalos explícitos e testes temporais | Clock/Calendar |
| Revisões concluídas hoje | S1/S2 | RF-050; RN-062 | ausente | total e lista pela data civil do Workspace | timezone V0.3 |
| Revisões devidas/atrasadas/futuras | S1/S2 | RF-051; RN-063 | parcial | totais iguais às seções da fila | ReviewStatusPolicy/fila |
| Desempenho por disciplina | S2 | RF-053; RN-064; FL-015 | ausente | volume/acerto/erro/taxa e drill-down | S1; taxonomia |
| Desempenho por assunto | S2 | RF-053; RN-064; FL-016 | ausente | agrupamento e drill-down reconciliados | S1; disciplina |
| Frequência por categoria de erro | S2 | RF-054; RN-065 | ausente | soma por categoria igual aos erros elegíveis | classificações V0.3 |
| Situação das questões no ciclo | S2 | RF-052 | ausente | estados mutuamente exclusivos e soma reconciliada | ciclos V0.3 |
| Dashboard básico | S3 | RF-047; FL-014 | ausente | view/template e jornada automatizada | S2 |
| Definições próximas aos indicadores | S3 | RF-055 | ausente | ajuda acessível com período/população/exclusões | S1/S2 |
| Drill-down de cada total | S2/S3 | RF-047/053–055 | ausente | links preservam o mesmo contrato/filtro | S2 |
| Empty states e nenhuma métrica falsa | S1/S3 | RF-047/049/053/055; CT-139 | parcial | taxa ausente, não 0%; orientação recuperável | S1/S2 |
| Listagem de questões | S4 | RF-063; FL-020 | existente | regressão e aceite BCR-1 | search atual |
| Busca textual | S4 | RF-064; CT-085 | existente | Unicode, limpeza e isolamento sob carga | search atual |
| Filtros básicos de estado/hierarquia | S4 | RF-063/065 | existente | regressão de opções hierárquicas | search atual |
| Filtros de revisão/resultado/erro | S4 | RF-065/066; errata V0.2 | ausente | filtros isolados/combinados/limpos | fatos V0.3 |
| Paginação estável | S4 | RNF-061; CT-086 | parcial | nenhuma omissão/duplicação em 10 mil itens | ordering atual; BCR-1 |
| Detalhe completo | S4 | RF-013/015; Roadmap §7.2 | parcial | conteúdo, origem, estado, aprendizagem e ausências fiéis | detalhe atual |
| Histórico navegável | S4 | FL-004/005 e timeline V0.3 | parcial | snapshots/tentativas/revisões/diagnósticos navegáveis | selectors existentes |
| Mensagens recuperáveis | S3–S8 | RNF-005/046; SDD §18 | parcial | falhas esperadas com próxima ação e sem códigos internos | cada novo fluxo |
| Logs estruturados e privados | S5 | RNF-068–070; CT-134 | parcial | novos eventos correlacionados e sentinelas ausentes | logging existente |
| Invariant checker | S5 | Roadmap §7.2; SDD §§6.3/21.4 | ausente | comando read-only, exit code e relatório sanitizado | invariantes V0.3/S2 |
| Backup SQLite consistente | S6 | RNF-034/036; CT-113/132 | existente | gap assessment e regressão V0.4 | serviço atual |
| Restauração técnica | S6 | RF-068; RNF-038; CT-115/133/143 | parcial | restore isolado, aplicação abre, reconciliação completa | backup atual; S5 |
| Teste de restauração/RPO/RTO | S6 | RNF-035/038; CT-116 | ausente | exercício cronometrado, contagens e vínculos | procedimento S6 |
| Política/guia de backup e atualização | S6/S7 | RNF-037/053/057 | ausente | documentação executável e revisão | S6; decisão Windows |
| Iniciar aplicação/ambiente/atalho | S7 | RD-ABR-003; SDD §22.3; CT-127 | parcial | decisão mínima e smoke Windows limpo | fluxos estabilizados |
| Atualização local documentada | S7 | RF-067; RNF-053/057 | ausente | ensaio em cópia, backup e retorno | S6 |
| Teclado/foco/labels | todas; S8 valida | RNF-044–046/049 | parcial | checks por tela e jornada manual transversal | telas S3/S4 |
| Contraste e não depender de cor | todas; S8 valida | RNF-047 | parcial | medidas e inspeção registrada | CSS/telas finais |
| Zoom 200%/responsividade | todas; S8 valida | RNF-048/065; CT-128 | parcial | Chrome/Edge, 360–1920 px e 200% | telas finais |
| `BCR-1` como gate | S8 | RNF-001–004/059/061; CT-105–108/110/112 | parcial | artefato reproduzível das leituras e gravações | S2–S4 |
| Piloto com dados copiados e backup prévio | S9 | Roadmap §§7.8/17; RD-ABR-009 | ausente | protocolo preenchido com fatos reais | S6–S8 |
| Rollback/recuperação do piloto | S9 | RNF-035/038; Roadmap RD-RIS-006 | ausente | restore/retorno ensaiado e decisão registrada | S6/S7 |
| Gate e promoção V0.4 | S9 | Roadmap §§7.4/11; RNF-080 | ausente | matriz final, review, gate e decisão | S1–S8 + piloto |

Nenhum requisito fica órfão. Responsabilidades compartilhadas indicam contrato
(S1) versus implementação/apresentação (S2/S3), incorporação de acessibilidade
em cada tela versus validação transversal (S8), ou mecanismo de recuperação
(S6) versus operação Windows/piloto (S7/S9); não são implementações duplicadas.

## 4. Contratos semânticos das métricas

S1 deve congelar, antes de qualquer cartão, os seguintes contratos. Todos são
limitados ao Workspace corrente; usam fatos persistidos, período civil no fuso
do Workspace quando houver data, inclusões/exclusões explícitas e um link para
o conjunto de origem. Mudança posterior exige teste de reconciliação.

| Métrica | Numerador/valor | Denominador | Período/filtros | Zero/empty state | Drill-down e interpretação |
| --- | --- | --- | --- | --- | --- |
| Questões cadastradas | rascunhos + ativas + arquivadas existentes, detalháveis por estado | não aplicável | `todo o histórico`; estado visível | `0` é contagem válida | lista com os mesmos estados; inventário atual, não atividade |
| Questões realizadas | `COUNT(DISTINCT question_id)` com tentativa inicial válida | não aplicável | ocorrência da tentativa inicial no intervalo | `0` é válido | questões que originaram tentativas iniciais; revisões nunca aumentam o total |
| Tentativas | tentativas válidas | não aplicável | ocorrência; tipo initial/review e demais filtros visíveis | `0` é válido | lista de fatos; volume, não número de questões |
| Acertos | tentativas válidas corretas | tentativas válidas no mesmo contexto | mesmo período/tipo/taxonomia | `0` válido se denominador > 0 | tentativas corretas |
| Erros | tentativas válidas incorretas | tentativas válidas no mesmo contexto | mesmo período/tipo/taxonomia | `0` válido se denominador > 0 | tentativas incorretas |
| Taxa de acerto | acertos | acertos + erros válidos | mesmo período/filtros; arredondar só na apresentação | `sem dados` quando denominador 0 | numerador/denominador visíveis; não confundir baixa amostra com baixo desempenho |
| Revisões concluídas hoje | revisões concluídas cuja tentativa correspondente ocorreu hoje | não aplicável | hoje no fuso do Workspace; somente tipo review | `0` válido | tentativas de revisão correspondentes; mede atividade concluída, não pendência |
| Revisões devidas | única pendência `DUE` de cada ciclo ativo não suspenso | não aplicável | data civil corrente pela policy/fuso | `0` válido | mesma seção `due`; carga executável de hoje |
| Revisões atrasadas | única pendência `OVERDUE` de cada ciclo ativo não suspenso | não aplicável | mesma policy/fuso; exclui suspensas/canceladas/concluídas | `0` válido | mesma seção `overdue`; carga vencida, não desempenho |
| Revisões futuras | única pendência `FUTURE` de cada ciclo ativo não suspenso | não aplicável | mesma policy/fuso; horizonte exibido deve ser explícito | `0` válido | mesma seção `future`; carga futura, não tarefa executável hoje |
| Desempenho por disciplina/assunto | acertos e erros válidos do grupo | tentativas válidas do grupo | período, tipo e nível taxonômico visíveis | sem taxa quando não há amostra | lista de tentativas/questões do grupo; não é domínio |
| Frequência de erro | tentativas incorretas elegíveis cuja classificação atual aponta a categoria | total de erros classificados elegíveis para percentual, se exibido | período/tipo/taxonomia; política de correção explícita | lista vazia sem ranking fictício | erros da categoria; frequência, não gravidade/prioridade |
| Situação no ciclo | questões em categorias mutuamente exclusivas definidas | questões cadastradas elegíveis ao recorte | estado no instante da consulta | zeros são válidos | questões de cada estado; “ciclo concluído” nunca vira “dominada” |

O contrato deverá decidir explicitamente como questões arquivadas entram em
inventário/histórico, como futuras são limitadas na apresentação e como a
classificação corrigida afeta agrupamentos, usando as regras aprovadas; nenhuma
dessas decisões será inferida do layout.

## 5. Decomposição executável

### V0.4-S1 — Contratos de métricas e exemplos de reconciliação

- Objetivo: transformar RF/RN/RNF em contratos semânticos inequívocos antes de
  escrever queries ou UI.
- Valor: elimina números visualmente plausíveis, mas semanticamente falsos.
- Expected Scope: documento versionado dos contratos; casos tabulares de
  inclusão/exclusão, período, fuso, zero e arredondamento; mapeamento para
  selectors/drill-down futuros.
- Protected Scope: modelos/migrations, views/templates, policies V0.3,
  thresholds `BCR-1` e itens V0.5+.
- Fora: implementar `StatisticsQueryService`, cartões, gráficos ou snapshots.
- Dependências: baseline V0.3 e P0 concluída.
- Tamanho/risco: `M / medium`.
- Modelo/reasoning: `Terra High`; o artefato é documental, mas combina regras
  temporais, populações e reconciliação com impacto transversal.
- Review A8: `profundo` nos contratos centrais; verificar órfãos, denominadores,
  timezone, arquivamento, correções e fronteira com domínio.
- Testes/verificações: exemplos executáveis ou testes de contrato apenas se
  houver código; validação de links, matriz e `git diff --check`; gate geral.
- Documentação: fonte curta de contratos analíticos e rastreabilidade afetada.
- Aceite/evidência: todas as métricas da seção 4 têm definição aprovada, casos
  positivos/negativos/fronteira e mapeamento de drill-down; review sem
  Blocker/Major; gate GREEN.
- Encerramento: contrato suficiente para implementar S2 sem decisão semântica
  implícita.
- Plano A4: não; o próprio contrato da etapa e a tabela semântica bastam.

### V0.4-S2 — Serviços analíticos, DTOs e drill-down reconciliável

- Objetivo: implementar consultas read-only autoritativas das métricas e das
  listas correspondentes.
- Valor: uma camada testável e independente de HTTP sustenta dashboard e
  análises sem acoplá-los a templates.
- Expected Scope: módulo/selectors de estatísticas, DTOs com valor,
  numerador/denominador, período e estado de disponibilidade; agregações por
  disciplina/assunto/categoria; filtros e drill-down; índices/migration somente
  se medição provar necessidade e o contrato da etapa autorizar.
- Protected Scope: fatos históricos, `ReviewStatusPolicy`, schema/migrations
  históricas, domínio/prioridade, cache/snapshots e escrita de analytics.
- Fora: dashboard visual e gráficos.
- Dependências: S1; modelos e selectors V0.3.
- Tamanho/risco: `L / high`.
- Modelo/reasoning: `Sol Medium`; múltiplas invariantes, ORM, timezone,
  isolamento e reconciliação justificam capacidade forte, sem presumir que
  `High` seja necessário antes da evidência.
- Review A8: `profundo` para integridade semântica, N+1, escopo, datas, estados
  impossíveis, segurança entre Workspaces e eventual migration.
- Testes focados: unidade para DTO/contratos; query/service com dois Workspaces;
  zeros/empty; limites de período/fuso; initial versus review; estados de ciclo;
  agrupamentos; classificação corrigida; reconciliação métrica↔drill-down;
  query count/perfil preliminar.
- Verificações/documentação: migrations quando aplicável, cobertura das regras,
  rastreabilidade e gate.
- Aceite/evidência: cada métrica e agrupamento reconcilia com seus fatos; nenhum
  cálculo em view/template; testes e relatório de review/gate.
- Encerramento: API interna read-only pronta para S3 e para o benchmark S8.
- Plano A4: sim; L/high, múltiplas consultas e possível impacto de índices.

### V0.4-S3 — Dashboard explicável e estados recuperáveis

- Objetivo: apresentar os DTOs de S2 em painel básico com definições e
  drill-down, priorizando cartões/listas/tabelas.
- Valor: o estudante compreende atividade, desempenho e revisões sem números
  falsos.
- Expected Scope: rota/view/template, filtros de período aplicáveis, cartões,
  tabelas acessíveis, ajuda próxima, links de drill-down e empty/error states.
- Protected Scope: cálculo autoritativo em presentation, gráficos obrigatórios,
  domínio/prioridade, cache/snapshots e API pública.
- Fora: polimento avançado, personalização e filtros salvos.
- Dependências: S2.
- Tamanho/risco: `M / medium`.
- Modelo/reasoning: `Terra Medium`; feature coesa sobre contratos prontos.
- Review A8: `padrão`, elevando pontos de semântica, escaping, exposição entre
  Workspaces e acessibilidade.
- Testes focados: view/template, links e filtros; vazio versus zero; erro
  recuperável; ausência de códigos internos; escaping; atualização após fatos;
  navegação por teclado automatizável.
- Verificações/documentação: definições visíveis, screenshots somente se úteis,
  guia de uso e gate.
- Aceite/evidência: todos os indicadores planejados aparecem ou sinalizam
  indisponibilidade, cada total abre o conjunto correspondente e nenhum gráfico
  é necessário para cumprir o MVP.
- Encerramento: dashboard funcional, reconciliável e apto ao hardening S8.
- Plano A4: não; o contrato S3 deve ser suficiente após S1/S2.

### V0.4-S4 — Consulta ampliada, detalhe e histórico navegável

- Objetivo: completar a consulta do acervo e integrar detalhe/histórico sem
  reimplementar listagem, detalhe ou timeline existentes.
- Valor: localizar material e compreender sua trajetória a partir de um fluxo
  único e estável.
- Expected Scope: filtros por situação de revisão, resultado inicial e categoria
  de erro; combinação/limpeza/resumo; preservação de busca/hierarquia/estado;
  navegação entre lista, detalhe versionado e timeline; paginação total estável.
- Protected Scope: `SavedFilter`, FTS sem benchmark, correção estrutural,
  exclusão permanente, histórico novo de correções e dados de outro Workspace.
- Fora: pesquisa semântica, tags pessoais e exportação.
- Dependências: V0.3; pode começar após S1 e em paralelo a S3, reutilizando S2
  somente se um drill-down compartilhar o mesmo contrato.
- Tamanho/risco: `M / medium`.
- Modelo/reasoning: `Terra Medium`; extensão funcional moderada sobre selectors
  existentes, com atenção a joins e paginação.
- Review A8: `padrão`, com foco profundo em isolamento, duplicação causada por
  joins, total ordering e exposição de gabarito.
- Testes focados: cada filtro e combinações; limpar; opção inválida/estrangeira;
  Unicode; empty; troca de filtro/página; empates e mutação concorrente;
  navegação/listas históricas; escaping e CSRF onde houver POST.
- Verificações/documentação: `CT-085/086` ampliados; mapa de navegação; gate.
- Aceite/evidência: dez mil questões podem ser consultadas sem
  duplicação/omissão; detalhe e timeline são alcançáveis e fiéis; ausências não
  viram fatos fictícios.
- Encerramento: fluxo de consulta pronto para BCR-1 e piloto.
- Plano A4: não inicialmente; criar somente se uma migration/FTS comprovadamente
  necessária ampliar a etapa, o que exigirá reavaliação do contrato.

### V0.4-S5 — Integridade operacional, logs e invariant checker

- Objetivo: detectar estados inválidos e diagnosticar os fluxos V0.4 sem alterar
  dados nem registrar conteúdo privado.
- Valor: transforma falhas silenciosas em evidência acionável antes de backup,
  piloto e promoção.
- Expected Scope: catálogo explícito de invariantes; comando operacional
  read-only; relatório sanitizado, códigos de saída e correlação; extensão dos
  eventos/logs para métricas, consulta e ciclos; instrução de execução.
- Invariantes mínimas: `integrity_check`/FKs; Workspace consistente nas relações;
  uma revisão corrente por questão; alternativa correta pertencente à revisão;
  classificação/attempt/ciclo/review coerentes; no máximo um ciclo ativo e uma
  pendência executável; estados/data/estágio compatíveis; receipts/idempotência;
  totais analíticos reconciliáveis em amostra ou modo completo documentado.
- Protected Scope: reparo automático, mutação/backfill, exclusão, migrations
  históricas, conteúdo privado em logs e novo sistema de auditoria funcional.
- Fora: monitoramento remoto e alertas/notificações.
- Dependências: S2 para invariantes analíticas; fatos V0.3.
- Tamanho/risco: `L / high`.
- Modelo/reasoning: `Sol High`; integridade persistente, failure modes e
  diagnóstico seguro justificam ambos.
- Review A8: `profundo` obrigatório.
- Testes focados: banco íntegro; cada violação sintética isolada; múltiplas
  violações; comando/exit code; read-only; dois Workspaces; volume; falha
  operacional; logs correlacionados e sanitizados.
- Verificações/documentação: execução no candidato, catálogo de invariantes,
  saída adequada para gate e procedimento de incidente.
- Aceite/evidência: exit 0 apenas no estado íntegro; falhas localizam invariantes
  sem dados privados e nunca corrigem silenciosamente; review/gate GREEN.
- Encerramento: checker executável e incorporável a backup/S8/S9.
- Plano A4: sim; L/high e dados críticos exigem passos/failure modes explícitos.

### V0.4-S6 — Backup, restauração e recuperação comprovada

- Objetivo: elevar o mecanismo técnico existente a procedimento V0.4
  recuperável, documentado e exercitado antes de dados reais.
- Valor: o usuário pode retornar a um conjunto íntegro após falha.
- Expected Scope: gap assessment do serviço/comandos; cobertura de todas as
  entidades V0.4; política local de destino/retenção; backup online consistente;
  manifesto/checksum; restore em destino isolado; abertura da aplicação;
  invariant checker/reconciliação; RPO/RTO vigentes e guia operacional.
- Protected Scope: restore sobre banco ativo, fluxo pela UI, exportação CEI,
  nuvem/integração, criptografia própria ou promessa de recuperação não testada.
- Fora: substituir o mecanismo provado sem lacuna concreta.
- Dependências: S5 e schema final aplicável até esta etapa; antes de S9.
- Tamanho/risco: `M / high`.
- Modelo/reasoning: `Sol High`; embora o delta possa ser pequeno, perda de dados
  e reversibilidade determinam a escolha.
- Review A8: `profundo` obrigatório.
- Testes focados: escrita concorrente; corrupção/checksum/versão; falha antes de
  publicação; destino existente; restore de conjunto representativo; aplicação
  inicia; contagens/FKs/invariantes; logs; exercício cronometrado de `CT-116`.
- Verificações/documentação: comandos copiados e executados em ambiente isolado;
  retenção/RPO/RTO sem inventar novos thresholds; relatório de restore.
- Aceite/evidência: backup não é mera cópia durante escrita; restore separado
  recupera fatos V0.4 e checker passa; procedimento informa pré-condições,
  retorno e falhas.
- Encerramento: evidência elegível para permitir S9, sem tocar dado real.
- Plano A4: sim; recuperação e failure modes justificam plano persistente.

### V0.4-S7 — Operação local Windows e atualização segura

- Objetivo: decidir e provar o menor mecanismo suficiente para iniciar,
  atualizar e proteger o MVP no Windows.
- Valor: uso local reproduzível sem conhecimento oculto.
- Expected Scope: spike limitado `RD-ABR-003`; comparação curta entre ambiente
  virtual documentado + script/atalho e empacotamento simples; decisão; launcher
  mínimo se justificado; perfis/caminhos; start/stop; atualização com backup;
  rollback; referência aos comandos S6.
- Protected Scope: instalador sofisticado, auto-update, serviço remoto,
  credenciais/configuração pessoal versionada e Project Starter.
- Fora: distribuição pública e suporte V1.
- Dependências: fluxos S3/S4 estabilizados e S6.
- Tamanho/risco: `M / medium`.
- Modelo/reasoning: `Terra Medium`; decisão operacional delimitada, com fallback
  já aprovado via ambiente virtual.
- Review A8: `padrão`, profundo nos caminhos, quoting, falha de atualização e
  risco ao banco.
- Testes focados: `CT-127` em Windows limpo/controlado; dois inícios; paths com
  espaços; falha de pré-requisito; banco ausente; smoke da jornada; update em
  cópia com backup/retorno.
- Verificações/documentação: guia de instalação, uso, atualização e backup
  executado literalmente por pessoa/ambiente que não dependa de passos ocultos.
- Aceite/evidência: decisão mínima registrada; atalho opcional não mascara
  erros; fallback documentado funciona; nenhum dado real é usado.
- Encerramento: operação reproduzível pronta para S8/S9.
- Plano A4: não; usar spike time-boxed dentro do contrato e criar plano apenas se
  a investigação revelar mudança transversal autorizada.

### V0.4-S8 — Hardening transversal, acessibilidade e gate `BCR-1`

- Objetivo: validar o candidato integrado quanto a acessibilidade, segurança,
  performance, integridade e regressão antes do piloto.
- Valor: impede que qualidade transversal fique para depois dos dados reais.
- Expected Scope: correções delimitadas nas telas/consultas V0.4; teclado, foco,
  labels, semântica, contraste, zoom 200%, 360–1920 px, Chrome/Edge; executor
  `BCR-1` ampliado para leituras; invariant checker; jornada E2E e gate.
- Protected Scope: thresholds congelados, `BCR-2`, gráficos/FTS/cache/snapshots
  sem evidência, conformidade normativa integral não demonstrada e V0.5.
- Fora: alegar WCAG integral apenas por ferramenta automática.
- Dependências: S1–S7.
- Tamanho/risco: `L / high`.
- Modelo/reasoning: `Sol High`; integração multicamada, performance e segurança
  antes de dados reais justificam revisão e raciocínio máximos da faixa usual.
- Review A8: `profundo` obrigatório.
- Testes focados: `CT-105/106/108/110/112`, regressão `CT-107`, `CT-121/123`,
  `CT-128`, acessibilidade automatizável e protocolo manual, checker, logs,
  migrations e backup smoke.
- Verificações: três runs e parâmetros vigentes quando vinculantes; p95 de telas
  principais ≤3 s, busca/filtros ≤2 s, gravações ≤2 s e atualização do dashboard
  ≤3 s conforme fontes atuais; ambiente/seed/amostras/método preservados; gate
  autoritativo e diff review.
- Documentação/evidência: relatório `BCR-1`, matriz acessível com versões dos
  navegadores, findings/correções, limitações e candidato identificado.
- Aceite: sem P0/P1; métricas reconciliadas; checker/backup smoke GREEN; jornada
  central funciona por teclado e zoom; thresholds existentes atendidos ou a
  release não avança.
- Encerramento: candidato elegível para piloto, sem promover ainda.
- Plano A4: sim; L/high, matriz manual+automatizada e múltiplas dependências.

### V0.4-S9 — Piloto controlado e promoção do primeiro MVP

- Objetivo: executar uso local real controlado e decidir promoção com evidência,
  sem fabricar observações humanas.
- Valor: prova que o MVP é utilizável e recuperável fora da fixture sintética.
- Expected Scope: protocolo; critério e tamanho do conjunto copiado definidos
  antes da execução; consentimento/minimização; backup prévio; cópia isolada;
  ambiente local; cenários cadastro→erro→revisão→consulta→dashboard→backup;
  `CT-124`–`126` aplicáveis; registro de problemas; rollback/restore; retestes;
  release review, gate final, estado e documentação.
- Protected Scope: banco original, dados pessoais em logs/artefatos, alteração de
  critérios após resultados, invenção de participantes/métricas, V0.5 e qualquer
  promoção com P0/P1 impeditivo.
- Fora: uso irrestrito, telemetria externa, publicação/tag sem autorização.
- Dependências: S8 GREEN e backup S6 executado imediatamente antes do piloto.
- Tamanho/risco: `M / high`.
- Modelo/reasoning: `Sol Medium`; coordenação e decisão de release exigem modelo
  forte, enquanto side effects críticos ficam controlados por protocolo e
  revisão profunda; elevar a High somente diante de finding complexo.
- Review A8: `profundo` obrigatório para evidência, dados, rollback e promoção.
- Testes/verificações: piloto real não é substituído por automação; retestar
  correções; invariant checker antes/depois; restore/rollback; BCR-1 atual;
  acessibilidade; gate; `git diff --check`; working tree/release coerentes.
- Documentação: guia MVP final, release notes, relatório sanitizado do piloto,
  matriz de promoção, estado e arquivo da tarefa.
- Aceite/evidência: critérios de sucesso predefinidos atingidos; problemas e
  ajuda crítica registrados; backup/retorno provados; nenhuma perda/exposição;
  review APPROVED e gate final GREEN; promoção explicitamente decidida.
- Encerramento: V0.4 promovida documentalmente como primeiro MVP, mas commit,
  tag, push e release externa continuam exigindo autorização separada.
- Plano A4: sim; piloto, dados copiados, rollback e promoção exigem sequência
  persistida.

## 6. Dependências e checkpoints

```text
S1 contratos
  -> S2 queries/DTOs/drill-down
       -> S3 dashboard ---------+
       -> S4 consulta/histórico +-> S5 integridade/logs -> S6 backup/restore
                                                         -> S7 Windows
S1 -> S4 -----------------------------------------------+-> S8 hardening/BCR-1
                                                            -> S9 piloto/promoção
```

S4 pode começar após S1 e o baseline V0.3, mas integra com os contratos de S2
quando servir como drill-down. S5 aguarda S2 para verificar também invariantes
analíticas. S6 precede qualquer dado copiado. S7 ocorre após estabilidade dos
fluxos, sem bloquear correções funcionais anteriores. S8 integra tudo; S9 só
recebe candidato GREEN. Não há dependência circular.

Cada etapa termina com árvore consistente, task arquivada, `current.md` sem
autorização e checkpoint Git limpo possível — embora Git continue dependendo de
autorização expressa separada. Nenhuma etapa autoriza automaticamente a seguinte.

## 7. Estratégia de testes e review

- S1: validação documental e exemplos de contrato; não criar teste funcional
  artificial.
- S2: unidade, domínio temporal, query/service, isolamento, reconciliação e
  perfil preliminar.
- S3/S4: views/templates/integração, segurança de saída, paginação/filtros,
  empty/error states e acessibilidade incorporada.
- S5/S6: testes negativos de integridade, comandos, read-only, corrupção,
  atomicidade, restore isolado, logs e failure modes.
- S7: smoke operacional real em Windows limpo/controlado e update em cópia.
- S8: integração/E2E, performance, acessibilidade manual+automatizável,
  compatibilidade e regressão total.
- S9: protocolo humano/operacional real, recuperação e gate final; fatos ausentes
  ficam `unknown`/pendentes, nunca PASS inferido.

Review A8 é padrão em S3, S4 e S7; profundo em S1 (semântica central), S2, S5,
S6, S8 e S9. A profundidade pode subir por evidência real. Cada review verifica
contrato, Expected/Protected Scope, testes, regressões, documentação e diff;
findings Blocker/Major impedem encerramento.

## 8. `BCR-1`, invariant checker, backup e promoção

### 8.1 `BCR-1`

O dataset, seed/ambiente documentado, persistência real, três runs, 20 warm-ups,
100 amostras, p95 nearest-rank e limites de gravação permanecem os de ADR-012.
S8 estende a cobertura às leituras V0.4 previstas no Plano de Testes, preserva
resultados brutos/ambiente/comando/exit e compara cada total a seu drill-down.
Não altera threshold. Regressão de gravação, tela, busca/filtro ou atualização
do dashboard bloqueia o candidato; otimizações estruturais exigem evidência e
contrato próprio dentro da etapa.

### 8.2 Invariant checker

É um comando operacional read-only, também chamado pelo gate de candidato e
pelos exercícios de restore/piloto. Tem modo completo ou escopo explicitamente
documentado, exit code não zero para qualquer violação e saída sanitizada por
invariante, sem IDs/conteúdo desnecessários. Testes unitários não o substituem;
ele também não repara dados. O catálogo mínimo está em S5 e poderá crescer
somente junto a novos fatos/invariantes autorizados.

### 8.3 Backup/restore

Quatro evidências distintas são obrigatórias: criação consistente; restore em
destino novo; teste que abre/reconcilia a aplicação e roda o checker; guia de
operação com retenção, RPO/RTO vigentes, atualização e recuperação. O backup do
piloto é adicional e imediatamente anterior à cópia/uso. “Arquivo criado” sem
restore aprovado não é evidência de recuperação.

### 8.4 Gate final de promoção

V0.4 só pode ser promovida quando:

1. S1–S9 estiverem encerradas com critérios/evidências e contratos arquivados;
2. suite aplicável, cobertura segundo política vigente (incluindo ≥80% nos
   módulos de domínio críticos), Ruff, mypy, checks/migrations, detect-secrets e
   `pip-audit` estiverem GREEN no gate autoritativo;
3. migrations limpa e upgrade desde release anterior suportada preservarem
   dados, com backup/caminho de retorno;
4. `BCR-1` atender aos thresholds vigentes com artefato reproduzível;
5. invariant checker passar no candidato e nas cópias restaurada/piloto;
6. backup/restore, RPO/RTO aplicáveis e documentação estiverem provados;
7. jornada por teclado, foco, labels, contraste, Chrome/Edge, responsividade e
   zoom 200% estiver registrada sem prometer conformidade não testada;
8. piloto real controlado e retestes necessários estiverem concluídos;
9. documentação de uso, instalação, atualização, backup e recuperação estiver
   executável e consistente;
10. review profundo final estiver APPROVED, sem Blocker/Major, sem P0/P1 ou
    defeito impeditivo aberto;
11. working tree, `PROJECT_STATE.md`, matriz de release e artefatos de qualidade
    forem coerentes; `git diff --check` e gate final tiverem exit code 0.

Nenhum threshold novo é criado por este plano. Falha crítica de integridade,
perda de dados, acesso cruzado, duplicação de tentativa, gabarito exposto,
backup irrecuperável ou migration destrutiva bloqueia promoção conforme Roadmap.

## 9. Registro de riscos

| Risco | Impacto | Etapa dona | Mitigação | Evidência |
| --- | --- | --- | --- | --- |
| Métrica semanticamente incorreta | decisão enganosa/P0 | S1/S2 | contrato antes da query; reconciliação | casos e testes drill-down |
| Dashboard acoplado a views/templates | divergência/manutenção | S2/S3 | serviço/DTO read-only | review de dependências |
| Query lenta/N+1 | MVP inutilizável | S2/S8 | perfil antes de índice/cache; BCR-1 | contagem de queries e p95 |
| Paginação instável com joins/mutação | omissão/duplicação | S4/S8 | total ordering, distinct e testes | CT-086 ampliado |
| Datas/fuso inconsistentes | fila/métrica errada | S1/S2/S8 | policy/Clock únicos e fronteiras | testes DST/fusos |
| Estado de revisão classificado diferente da fila | totais falsos | S2 | reutilizar `ReviewStatusPolicy` | total = seção da fila |
| Backup existe mas não recupera | perda de dados/P0 | S6/S9 | restore separado + checker | relatório de exercício |
| Restore/launcher toca banco real | perda de dados/P0 | S6/S7 | destinos explícitos e perfis bloqueados | testes sentinela |
| Empacotamento Windows frágil | atraso/indisponibilidade | S7 | spike limitado e venv fallback | CT-127 |
| Acessibilidade tardia | retrabalho/exclusão | todas/S8 | aceite por tela + hardening | matriz manual/automática |
| Logs expõem conteúdo | privacidade/P0 | S5/S8 | eventos mínimos/sentinelas | testes de sanitização |
| Invariant checker altera dados ou gera falso GREEN | corrupção silenciosa | S5 | read-only, violações sintéticas | testes/exit codes |
| Piloto usa original ou não tem retorno | perda/exposição | S6/S9 | cópia, backup prévio e rollback | protocolo preenchido |
| Scope creep para V0.5 | atraso/arquitetura prematura | todas | Protected Scope e review | diff/classificação de findings |
| Gráfico/FTS/cache prematuro | custo e invalidação | S3/S4/S8 | tabela/ORM primeiro; medir | decisão baseada em BCR-1 |

## 10. Validação da decomposição e condição de saída de P0

- Requisito órfão: não; a matriz cobre todos os itens obrigatórios.
- Etapa grande demais: não após separar semântica, query e apresentação; S8 é L,
  mas coeso como hardening de candidato e exige plano A4.
- Burocracia pura: não; S1 remove ambiguidade verificável e S9 executa o piloto
  e a decisão real de promoção.
- Dependência circular: não.
- Repo consistente após qualquer etapa: sim; cada etapa fecha seu próprio
  contrato/gate e não depende de estado parcial autorizado.
- Checkpoints Git limpos: sim; um checkpoint coerente é possível após cada etapa,
  sob autorização separada.
- Contexto/cota: razoável; S1 evita reabrir semântica nas telas, S2 centraliza
  leitura, S3/S4 reutilizam serviços, e apenas cinco etapas exigem plano A4.
- Dividir/fundir: S2 não deve fundir com S3; S5 não deve fundir com S6; S8 e S9
  permanecem separados para impedir piloto antes do candidato GREEN. S4 agrega
  listagem/detalhe/histórico porque o baseline já compartilha navegação e torna
  uma divisão adicional artificial.

Planos A4 inicialmente exigidos: S2, S5, S6, S8 e S9. S1, S3, S4 e S7 devem
caber em contratos completos; a execução pode reavaliar com evidência, sem este
plano ampliar autoridade.

P0 termina quando este documento estiver revisado, com matriz completa, gate
GREEN e registros operacionais encerrados. A recomendação para a primeira
execução futura é `V0.4-S1 — Contratos de métricas e exemplos de reconciliação`,
mas ela permanece **não autorizada** até novo contrato explícito.
