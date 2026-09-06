# V0.2 — Etapa 8 — Fixture, Acessibilidade, Backup, Integração e Regressão

## Identificação

- Versão: V0.2.
- Etapa: 8.
- Status: formalmente liberada; não iniciada.
- Natureza: consolidação operacional, validação e regressão do Catálogo de Conteúdo.
- Pré-requisito confirmado: Etapa 7 concluída e arquivada em
  `tasks/completed/v02-stage7-content-list-search-filters.md`; último gate GREEN
  registrado em `quality/v02-stage7-result.md`.

## Objetivo

Comprovar que o Catálogo de Conteúdo V0.2 pode ser demonstrado, instalado,
atualizado, recuperado e usado nos fluxos centrais com dados sintéticos seguros,
sem regressão da V0.1/V0.2 e com a acessibilidade manual exigida. Esta etapa não
introduz capacidade funcional nova nem promove a versão.

## Escopo

- criar fixture sintética, determinística e reproduzível para a V0.2, carregável
  apenas em banco descartável e nunca automaticamente em dados reais ou como data
  migration;
- representar, sem dados pessoais ou conteúdo privado real, Workspace explícito,
  taxonomia, origem, rascunho, questões ACTIVE e ARCHIVED, revisões (inclusive
  duas revisões), alternativas/gabarito e cenários necessários à regressão;
- comprovar idempotência/equivalência da fixture para mesma semente, sem
  duplicação, e documentar/automatizar o carregamento seguro quando necessário;
- estender a prova técnica existente de backup SQLite para todas as entidades
  V0.2: gerar, validar e restaurar somente em destino isolado; reconciliar
  contagens, FKs, estados, revisão corrente e gabarito; rejeitar artefato
  corrompido antes de qualquer substituição;
- validar instalação limpa e migração de banco vazio para V0.2, e upgrade
  `v0.1.0` → V0.2, preservando as migrations protegidas e os dados/invariantes
  da baseline;
- executar regressão integral aplicável da V0.1 e da V0.2, incluindo taxonomia,
  origem, rascunho/ativação, alternativas/gabarito, detalhe, edição versionada,
  arquivamento, busca/listagem/filtros e isolamento de Workspace;
- executar e registrar a validação manual integral de acessibilidade do catálogo
  (`CT-142`) em Chrome e Edge vigentes no Windows 11: teclado, ordem e
  visibilidade do foco, rótulos/erros/nomes acessíveis, aproximadamente 360 px e
  zoom de 200%; corrigir somente defeitos encontrados que estejam dentro deste
  escopo;
- manter rastreabilidade, evidências sanitizadas e o gate autoritativo GREEN.

## Fora de escopo

- qualquer entidade ou capacidade de aprendizagem: Attempt, ErrorClassification,
  ReviewCycle, Review, fila, histórico de aprendizagem, métricas, dashboard,
  domínio ou prioridade;
- tags, `QuestionTag`, `SavedFilter`, `RF-066`, FTS/FTS5, filtros de
  aprendizagem, filtros de origem/dificuldade, APIs, PWA, OCR, anexos,
  importação em massa e autenticação remota;
- exportação de usuário, restauração pela interface, importação/mesclagem lógica,
  troca do banco ativo, confirmação de impacto e pré-backup do banco ativo
  (V0.5-C/V1);
- novas capacidades de produto, alterações arquiteturais não indispensáveis,
  migrations/models além da correção indispensável de um defeito encontrado;
- iniciar, preparar ou promover a Etapa 9; tag, release, commit ou push.

## Fontes obrigatórias

- Roadmap, §§5.1–5.7: `docs/Caderno_de_Erros_Inteligente_Etapa_9_Roadmap (1).md`.
- ADR-010, §§2.1–2.3, `ERR-V02-001` a `ERR-V02-009`, §§4–6.
- ADR-007; ADR-002, ADR-006 e ADR-008.
- RFs: `RF-067`, `RF-068` e RFs V0.2 já entregues (`RF-004`–`RF-019`,
  `RF-063`–`RF-065` no recorte do ADR-010).
- RNFs: `RNF-018`–`RNF-020`, `RNF-027`, `RNF-033`–`RNF-038`,
  `RNF-044`–`RNF-049`, `RNF-052`–`RNF-058`, `RNF-063`, `RNF-065`,
  `RNF-066`, `RNF-076`, `RNF-078`–`RNF-080`.
- RNs `RN-006`–`RN-020`, `RN-086`, `RN-087`, nos recortes V0.2;
  recortes V0.2 de `FL-001`, `FL-002`, `FL-004`–`FL-006`, `FL-020` e parcela
  técnica de `FL-022`.
- Plano de Testes, sobretudo `CT-073`–`CT-075`, `CT-081`, `CT-082`, `CT-085`,
  `CT-086`, `CT-095`, `CT-097`, `CT-122`, `CT-123`, `CT-141`–`CT-144`.

## RFs, RNs, RNFs e fluxos aplicáveis

- `RF-067` e `RF-068`: persistência e recuperação técnica comprovada em
  ambiente controlado; não autoriza interface de backup/restauração.
- RFs V0.2 e os recortes de `RN-006`–`RN-020`, `RN-086` e `RN-087`: regressão
  integral, sem introduzir parcelas V0.3+.
- `RNF-034`, `RNF-036` e `RNF-038`: backup abrangente, íntegro e restaurado em
  ambiente isolado; arquivo corrompido não substitui dados.
- `RNF-033`, `RNF-052`–`RNF-058`, `RNF-076`, `RNF-079` e `RNF-080`:
  migrations, instalação/upgrade, rastreabilidade, testes isolados e gate.
- `RNF-020` e `RNF-078`: fixture sem dados pessoais reais e reproduzível.
- `RNF-044`–`RNF-049`, `RNF-063`, `RNF-065`, `RNF-066`: WCAG 2.2 AA como
  baseline, teclado/foco, Chrome/Edge, 360–1920 px, português/Unicode.
- `FL-001`, `FL-002`, `FL-004`–`FL-006`, `FL-020`: regressão do catálogo;
  `FL-022` exclusivamente na parcela técnica de backup/recovery.

## Componentes existentes a reutilizar

- models e migrations existentes de `accounts`, `errors`, `taxonomy` e
  `questions`, preservando hashes e ordem protegidos;
- `modules.data_management` e `CEI-SQLITE-BACKUP` 1.0 do ADR-007;
- perfis Django/isolamento de testes, gate e manifestos de qualidade existentes;
- entidades e services/selectors do catálogo V0.2;
- `base.html`, `app.css`, Django Forms/templates e padrões existentes de
  acessibilidade.

## Áreas prováveis de implementação

- fixture/comando ou suporte de testes V0.2, documentação operacional e testes de
  repetibilidade/privacidade;
- testes de backup, validação e reconciliação das entidades V0.2; ajustes mínimos
  no mecanismo técnico existente somente se um CT aplicável demonstrar defeito;
- testes de instalação limpa/upgrade e regressão; evidências em `quality/`;
- testes e correções pontuais de templates/CSS/forms/views existentes, se CT-142
  encontrar falha dentro do catálogo.

## Restrições

- fixture, backups, logs, screenshots e relatórios são sintéticos e sanitizados:
  sem dados pessoais reais, conteúdo privado, credenciais, caminhos sensíveis ou
  segredos;
- fixture não é migration, não é seed automático e não escreve em banco real;
  backup/restauração usam destinos explícitos, descartáveis e não sobrescrevem o
  banco ativo;
- restaurar somente após manifesto/checksum, `integrity_check`,
  `foreign_key_check`, migrações e invariantes; falha preserva o destino anterior;
- não alterar migrations protegidas; uma migration nova exige defeito concreto,
  banco vazio/upgrade e manutenção dos manifests;
- não ampliar o catálogo nem antecipar V0.3+, Etapa 9, tag, release, commit ou
  push.

## CTs e testes previstos

- `CT-141` integral: fixture sintética determinística, segura, equivalente com a
  mesma semente e sem duplicação/carga automática;
- `CT-142` integral, P0: validação manual e automatizável do catálogo em
  Chrome/Edge, teclado/foco, cerca de 360 px e zoom 200%; inclui taxonomia,
  criação/edição/validação de questão, pesquisa e arquivamento;
- `CT-143` integral, P0: backup/recovery V0.2 de taxonomia, origem, rascunho,
  ACTIVE/ARCHIVED e duas revisões; reconciliação e rejeição de cópia corrompida;
- `CT-081`, `CT-082`, `CT-122`, `CT-123`: banco vazio/instalação limpa, upgrade
  `v0.1.0` → V0.2, migrations e preservação de baseline;
- `CT-073`–`CT-075`, `CT-085`, `CT-086`, `CT-095`, `CT-097`, `CT-137`–`CT-140`
  e `CT-144`: regressões de integridade, catálogo, isolamento, escaping, revisão
  e ausência de bloqueio semântico.

## Evidências manuais necessárias

- ambiente e versões vigentes de Chrome/Edge no Windows 11;
- roteiro/resultados de CT-142 sem mouse: Tab/Shift+Tab, Enter/Espaço, ordem/foco
  visível, sem armadilha, nomes/rótulos/erros, filtros e mensagens; repetir em
  aproximadamente 360 px e zoom 200%, sem rolagem horizontal indevida,
  sobreposição ou controle inacessível;
- instalação limpa e upgrade `v0.1.0` → V0.2 em ambientes descartáveis;
- backup/restauração íntegro e corrompido, em destino isolado, com reconciliação;
- gate, CTs, defeitos/P0/P1 e decisão explícita de não promover Etapa 9.

## Critérios objetivos de aceite

- fixture V0.2 é reproduzível, segura, explicitamente acionada e cobre estados e
  relações necessários, sem dados pessoais reais, duplicação ou escrita externa;
- backup/restauração técnica preserva e reconcilia entidades V0.2/relações; dados
  corrompidos ou incompatíveis falham antes de substituir qualquer destino;
- instalação limpa, banco vazio e upgrade `v0.1.0` → V0.2 passam; migrations,
  hashes e baseline permanecem intactos;
- CTs aplicáveis passam, incluindo CT-142 e CT-143; sem P0/P1 aplicável aberto;
- CT-142 comprova teclado, foco lógico/visível e nomes/erros acessíveis em
  Chrome/Edge, 360 px e zoom 200%;
- Ruff, mypy, cobertura, segurança, migrations, `git diff --check` e o gate
  autoritativo passam; evidências não contêm conteúdo sensível;
- encerrar somente após gate GREEN; arquivar então a tarefa sem iniciar ou
  promover a Etapa 9.

## Gate obrigatório

`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1`

Exit code diferente de 0 bloqueia a conclusão da Etapa 8.
