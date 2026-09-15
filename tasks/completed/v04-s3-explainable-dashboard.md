# Task Contract

Status: AUTHORIZED

## Identification

- Task ID: V0.4-S3
- Product version: V0.4
- Stage: S3 — Dashboard explicável
- Task type: product implementation / dashboard / presentation
- Size: M
- Risk: medium

## Goal

Implementar o dashboard básico e explicável da V0.4, consumindo exclusivamente
a interface analítica S2 e respeitando integralmente os contratos semânticos S1.

## Context

- Semântica autoritativa: `docs/V0.4_S1_Contratos_de_Metricas_e_Reconciliacao.md`.
- Leitura autoritativa: `docs/V0.4_S2_Interface_Analitica_Interna.md`.
- Decomposição e limites da etapa: `tasks/plans/v04-release-execution-plan.md`.
- Modelo recomendado: GPT-5.6 Terra; reasoning recomendado: Medium.
- Review A8 esperado: padrão; elevar para profundo somente diante de risco inesperado.
- Plano A4 não é obrigatório inicialmente; reavaliar somente se a tarefa revelar
  múltiplos subfluxos dependentes ou complexidade maior que M.

## Acceptance Criteria

- Exibir, com explicação de universo, período quando aplicável e estado sem dados:
  questões cadastradas e realizadas; tentativas (incluindo parcelas INITIAL e REVIEW),
  acertos, erros e taxa; revisões concluídas hoje, atrasadas, devidas hoje e futuras.
- Exibir desempenho por disciplina e assunto, e frequência por categoria de erro,
  incluindo o resíduo de erros válidos sem classificação quando fornecido por S2.
- Distinguir corretamente `0%` de taxa indisponível por ausência de denominador;
  não ocultar resíduo nem fabricar categorias, contagens ou estados vazios.
- Implementar estados claros para ausência de cadastro, realização, pendências,
  desempenho, categorias e denominador, sem mensagens enganosas.
- Incorporar acessibilidade básica, responsividade compatível com os padrões atuais
  e CSS mínimo reutilizando tokens, classes e componentes existentes quando aplicável.
- Usar drill-down somente quando S2 o suportar e houver destino apropriado já
  disponível; não criar tela temporária nem antecipar S4.
- Preservar o Workspace corrente e não introduzir N+1 estrutural ou chamadas
  repetidas desnecessárias à fachada S2.

## Expected Scope

- View, rota e integração do dashboard com os serviços/read models S2.
- Templates, parciais/componentes, CSS estritamente necessário, textos
  explicativos, legendas/tooltips e estados zero/empty.
- Links para drill-downs existentes e documentação técnica necessária.
- Testes proporcionais de view/template e integração com S2: Workspace, zero/empty,
  taxa indisponível, revisões, desempenho, categorias/resíduo, estrutura HTML e
  acessibilidade relevante, links existentes e comportamento de queries quando verificável.
- Registro dos fatos disponíveis da execução nas métricas A7 e review A8.

## Protected Scope

- Contratos semânticos S1 e significado, denominadores, datas ou filtros das métricas.
- Serviços, selectors e read models S2, salvo blocker comprovado e autorizado.
- Schema, migrations, regras de escrita, ciclos de revisão e dados históricos.
- S4 e etapas posteriores; Architecture v1.0, Skills, políticas A7/A8 e `quality.ps1`.

## Constraints

- View e templates não acessam diretamente o ORM para recalcular métricas S2;
  não criar queries paralelas, agregações locais, filtros duplicados ou lógica de
  denominador na apresentação.
- S3 decide somente apresentação, composição, navegação, texto explicativo,
  empty states e integração da UI; não redefine S1 nem reimplementa analytics.
- As classificações temporais de revisões vêm de S2 e não podem ser reinterpretadas.
- Não introduzir gráficos, redesign global, sistema visual paralelo, cache ou
  interfaces/páginas de consulta que pertençam a S4 sem evidência e autorização.

## Verification

- Executar testes focados aplicáveis e revisar integração, isolamento de Workspace,
  semantic drift, query paralela, zero versus sem dados, resíduo, acessibilidade,
  escopo S4 e CSS fora de escopo.
- Review A8 APPROVED, sem Blocker ou Major aberto.
- `git diff --check`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1`

## Documentation Impact

Atualizar somente a documentação técnica necessária; registrar métricas A7 com
fatos reais, mantendo cotas desconhecidas como `unknown`.

## Done When

- O dashboard básico apresenta atividade, revisões, desempenho por disciplina e
  assunto, categorias e resíduo de acordo com S1 por meio exclusivo de S2.
- Explicações, estados zero/empty, taxa indisponível, Workspace, acessibilidade
  básica, responsividade e ausência de N+1 estrutural óbvio estão verificados.
- Testes focados, review A8, `git diff --check` e gate autoritativo estão GREEN.
- A tarefa é arquivada, as métricas reais são registradas, `tasks/current.md`
  retorna a `NO_TASK_AUTHORIZED` no encerramento e S4 permanece não autorizada.

## Evidência de encerramento

- Implementação: a home agora apresenta o dashboard S3 por meio exclusivo de
  `AnalyticsService`, com atividade, revisões, desempenho por disciplina e
  assunto, categorias e resíduo analítico explícito.
- Explicabilidade: cadastradas, realizadas e tentativas são distinguidas;
  taxa sem denominador mostra `Sem dados`, enquanto taxa com amostra mantém o
  valor percentual. As quatro situações de revisão têm rótulos próprios.
- Testes novos: 3 em `tests/test_dashboard.py`; a regressão de interface da
  home foi atualizada em `tests/test_interface.py` e
  `tests/test_taxonomy_interface.py`. A execução focada final aprovou 37 testes.
- Review A8 padrão: **APPROVED**, sem Blocker ou Major. A view apenas obtém o
  Workspace e invoca os cinco agregados S2, sem ORM analítico, N+1 estrutural
  ou query paralela. Não há migration ou alteração de schema.
- Drill-down: não foi criado destino novo. A fila de revisões já existente é
  apenas uma navegação para a capacidade atual; drill-downs completos, com os
  mesmos filtros do agregado, permanecem para S4.
- `git diff --check`: aprovado.
- Gate autoritativo final: **GREEN**, exit code 0, 288 testes aprovados em
  67,59 s e 87% de cobertura; migrations, formatação, Ruff, mypy,
  detect-secrets e pip-audit aprovados. A primeira execução foi impedida só
  pelo bloqueio de rede do pip-audit; a repetição autorizada em rede concluiu.
- Não houve commit, push, tag, release, migration, alteração de schema ou
  implementação de S4.
