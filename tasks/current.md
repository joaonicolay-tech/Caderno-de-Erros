# V0.2 — Etapa 3 — Catálogo de Origem

## Identificação

- Versão: V0.2.
- Etapa: 3.
- Nome: Catálogo de Origem.
- Status: liberada, não iniciada.
- Execução: deve começar em novo chat.

## Objetivo

Criar a fundação persistente e interna do catálogo de origem da V0.2, composta por `Board`, `Exam` e `Source`, dentro de `SDD-MOD-003`, com isolamento por Workspace, normalização, criação/reuso, arquivamento e evolução reproduzível do banco.

## Escopo

- criar o módulo Django `questions` somente com a estrutura necessária a esta etapa;
- implementar `Board`, `Exam` e `Source` conforme o modelo aprovado;
- implementar a migration congelada `questions/0001_origin_catalog`, dependente de `accounts/0001_initial`;
- implementar validações, serviços internos e selectors necessários para criar, reutilizar, consultar e arquivar as referências de origem;
- aplicar `name_key`, unicidades, índices, estados e FKs protegidas documentadas;
- validar o ano de `Exam` entre 1900 e o ano corrente do Workspace + 2, usando `Clock`/`Calendar` no serviço;
- garantir isolamento integral entre Workspaces;
- ampliar o manifesto/gate intermediário apenas com evidências legítimas desta etapa;
- criar testes unitários, de integração, migrations e regressão.

## Fora de escopo

- interface ou módulo funcional independente para administrar origem;
- `Question`, `QuestionRevision`, `Alternative` e `QuestionOrigin`;
- `questions/0002_question_catalog`;
- cadastro, edição, detalhe, busca ou arquivamento de questões;
- tags, tentativas, classificações, revisões de aprendizagem, dashboard e métricas;
- qualquer capacidade da Etapa 4 ou posterior.

`QuestionOrigin` será introduzido somente por `questions/0002_question_catalog`, conforme a ordem congelada em `ADR-010`. Nesta etapa, `CT-138` é atendido apenas na parcela de `Board`/`Exam`/`Source`; sua associação à questão permanece futura.

## Documentação relevante

- `docs/README.md`;
- `docs/ADR-010_Fronteira_Rastreabilidade_e_Dados_V0.2.md`, especialmente `ERR-V02-006` e a ordem de migrations;
- `docs/Caderno_de_Erros_Inteligente_Etapa_3_Requisitos_Funcionais.md`, `RF-012`;
- `docs/Caderno_de_Erros_Inteligente_Etapa_4_Requisitos_Nao_Funcionais.md`, `RNF-013`, `RNF-027` e `RNF-074`;
- `docs/Caderno_de_Erros_Inteligente_Etapa_5_Regras_de_Negocio.md`, `RN-014`, `RN-019` e `RN-086` nos recortes aplicáveis;
- `docs/Caderno_de_Erros_Inteligente_Etapa_6_SDD.md`, `SDD-MOD-003` e o recorte V0.2;
- `docs/Caderno_de_Erros_Inteligente_Etapa_7_Modelo_de_Dados.md`, seções 3.6, 6.1–6.3 e 27;
- `docs/Caderno_de_Erros_Inteligente_Etapa_8_Fluxos_Principais.md`, somente os recortes de origem aplicáveis;
- `docs/Caderno_de_Erros_Inteligente_Etapa_9_Roadmap (1).md`, V0.2;
- `docs/Caderno_de_Erros_Inteligente_Etapa_10_Plano_de_Testes.md`, parcela aplicável de `CT-138` e testes técnicos correlatos.

## ADRs relevantes

- `ADR-001` — toolchain reproduzível;
- `ADR-002` — perfis e isolamento de testes;
- `ADR-003` — Workspace, Clock e Calendar;
- `ADR-008` — gate único de qualidade;
- `ADR-010` — fronteira, rastreabilidade, dados e migrations da V0.2.

## Arquivos e áreas prováveis

- `src/modules/questions/apps.py`;
- `src/modules/questions/models.py`;
- `src/modules/questions/validators.py`;
- `src/modules/questions/services.py`;
- `src/modules/questions/selectors.py`;
- `src/modules/questions/migrations/0001_origin_catalog.py`;
- `src/config/settings/base.py`, apenas para registrar o app;
- testes específicos de origem e migrations em `tests/`;
- `quality/v02-stage1-gate.json` e `scripts/quality.ps1`, somente se necessário para evidência legítima.

## Restrições

- preservar integralmente a tag/baseline `v0.1.0` e as migrations existentes;
- não reescrever `taxonomy/0001_initial` nem migrations históricas;
- não criar `QuestionOrigin` antes de `questions/0002_question_catalog`;
- não criar URLs, views, forms ou templates de administração de origem;
- não duplicar regras de normalização existentes sem avaliar reutilização compatível entre módulos;
- não usar o relógio do sistema diretamente na validação do limite anual;
- não criar dependências novas sem incompatibilidade comprovada;
- não iniciar funcionalidades de questões ou etapas posteriores.

## Critérios de aceite

- `Board`, `Exam` e `Source` correspondem ao modelo e às constraints aprovadas;
- nomes são normalizados e referências equivalentes são reutilizadas no mesmo Workspace;
- referências de Workspaces diferentes nunca são lidas, reutilizadas ou vinculadas entre si;
- `Exam.year` aceita 1900 e ano atual + 2 e rejeita 1899 e ano atual + 3;
- `Exam` pode omitir `Board`, e todos os componentes de origem permanecem opcionais;
- arquivamento preserva histórico e FKs usam `PROTECT` onde documentado;
- migration limpa e upgrade desde a baseline aplicam sem perda;
- nenhuma interface independente de origem ou entidade futura é criada;
- metas de cobertura aplicáveis são atendidas;
- nenhum P0/P1 aplicável permanece aberto;
- gate autoritativo retorna exit code 0.

## CTs e testes

- `CT-073`: integridade referencial e constraints das novas entidades;
- `CT-074`: isolamento por Workspace;
- `CT-081`: instalação limpa com `questions/0001_origin_catalog`;
- `CT-082`: upgrade preservando dados da V0.1 e da taxonomia existente;
- `CT-138`: parcela de criação/reuso normalizado, opcionalidade, anos-limite e isolamento de `Board`/`Exam`/`Source`;
- regressão integral de `CT-127` e da V0.1/V0.2 já implementada;
- testes adicionais de unicidade ativa, Unicode, estados, `PROTECT`, arquivamento, concorrência quando aplicável e ausência das entidades futuras.

## Verificações específicas

1. confirmar baseline verde antes de implementar;
2. validar o grafo e o nome congelado da migration;
3. executar `makemigrations --check --dry-run`;
4. migrar banco vazio isolado;
5. testar upgrade desde `v0.1.0` e desde o estado aprovado da Etapa 2;
6. confirmar hashes das migrations históricas;
7. confirmar ausência de `Question`, `QuestionOrigin`, URLs, views e templates futuros;
8. executar testes direcionados, Ruff, mypy, coverage, secrets e `pip-audit`;
9. executar `git diff --check`.

## Gate obrigatório

`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1`

Exit code diferente de 0 bloqueia a conclusão da Etapa 3.
