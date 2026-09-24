# V0.5-S3 — UI de gestão, confirmações e filtros salvos

## Autoridade, baseline e plano

- Contrato executado: `tasks/current.md`, `V0.5-S3`, `AUTHORIZED`.
- Baseline: HEAD `53c92f517950a1a2d884e4fb41de939deb82bde7` (`main`).
- Plano A4: `tasks/plans/v05-s3-management-ui-plan.md`, concluído antes da
  primeira edição funcional; status final `COMPLETED`.
- Nenhuma etapa S4 ou posterior foi autorizada ou iniciada.

## Implementação e limites

- `SavedFilter` é uma preferência persistida por Workspace e owner. A migration
  aditiva `search.0001_initial` cria somente `search_savedfilter`; inclui nome e
  chave normalizada, contexto, versão do schema, payload JSON e timestamps, sem
  backfill. O payload é validado por lista fechada e pelos forms/selectors
  vigentes. Aplicação mantém a listagem e paginação existentes, ignora `page`,
  usa URL determinística e explica incompatibilidade de contexto, schema,
  categoria ou taxonomia.
- Categorias pessoais expõem create, rename, archive e merge exclusivamente por
  `PersonalCategoryService` S2A. O formulário de merge identifica origem/alvo,
  preservação física do histórico e atualização da projeção, e explica que merge
  não exclui categorias.
- Reviews expõem reschedule e inclusão manual por services S2A; Attempts expõem
  preview, void e replacement por S2B; correção prospectiva do gabarito chama o
  service S2C; exclusão permanente consome preview e delete S2D com fingerprint,
  confirmação explícita e backup/restore isolado obrigatório quando aplicável.
  Views não editam diretamente Reviews, Attempts, `QuestionRevision` ou o
  agregado de exclusão; checker, eligibility, políticas e services S2A–S2D não
  foram alterados.
- Todas as leituras e escritas de gestão são limitadas ao owner e Workspace
  corrente. Ações mutáveis usam POST e CSRF; previews/listas usam GET sem escrita.
  Formulários usam controles HTML nativos, labels, `aria-describedby`, erros
  associados e feedback `role=alert`/`role=status`. A revisão estática confirmou
  ordem normal de teclado; zoom e foco em navegador real não foram observados.
- Estados vazios, filtros incompatíveis, conflitos stale, bloqueio da exclusão e
  falha de restore têm feedback explícito. A consulta em lote de filtros mantém
  número de queries estável com nove filtros.
- A revisão corrigiu o relato após falha de limpeza do diretório temporário de
  restore: se o delete S2D já confirmou, a UI informa que a exclusão ocorreu e
  pede preservar `backups/` para inspeção. A linha do tempo oferece correção
  somente na Attempt efetiva.

## Migration, upgrade e recuperação

- Auditoria A4 constatou que `modules.search` não tinha app Django, modelo ou
  persistência. `SavedFilter` precisa de storage para cumprir create/apply/rename/
  delete; portanto uma única migration aditiva é necessária. A migration cria
  só a tabela de preferências e é reversível por sua remoção.
- `quality/v05-s3-migrations.json` acrescenta o hash de Search 0001 ao conjunto
  acumulado; `quality/v05-s2d-migrations.json` e manifestos anteriores ficaram
  inalterados. `tests/test_v05_s3_upgrade.py` provou upgrade após S2D, persistência
  de filtro, schema v1, rollback da tabela e preservação da Question.
- Os probes S2C/S2D continuam validando preservação no estágio histórico; antes
  de criar o backup de recuperação, avançam também para `search.0001`, de modo que
  o restore corresponda ao schema corrente. Nenhum serviço de recovery foi
  alterado.

## Testes e regressão

- S3 UI + migration/manifesto: **14 passed**.
- Regressões afetadas pelo novo link de categorias, pelo reagendamento e pelo
  schema corrente de recovery: **7 passed**. Expectativas de interface verificam
  o `href` exato de conclusão; não confundem o prefixo da rota de reagendamento.
- Gate completo: **423 passed**, cobertura global **87%**, cobertura mínima de
  domínio aprovada. Permaneceram dois `ResourceWarning` em
  `tests/test_v05_s2d.py`; não afetaram o resultado.
- `ruff check src tests`, `mypy src tests`, `manage.py check`,
  `makemigrations --check --dry-run`, migration em banco vazio, upgrade/rollback
  isolado, `git diff --check`, `detect-secrets` e `pip-audit` passaram. O audit
  informou `No known vulnerabilities found`.

## A8 standard

**APPROVED**; Blocker 0, Major 0 e Minor 0 abertos. A revisão cobriu contrato,
escopo, isolamento, payloads, chamadas S2A–S2D, concorrência, falhas pós-commit,
schema/migration, reversão, restore corrente, testes e templates.

Itens encontrados e resolvidos antes da aprovação:

- A tentativa inicial do gate encontrou 40 erros mypy de anotações nas novas
  forms/views/testes; todos foram tipados e mypy passou em 169 arquivos.
- A revisão identificou risco de feedback falso se a limpeza temporária falhasse
  após delete confirmado; o resultado agora distingue delete confirmado de aviso
  de limpeza e tem teste dedicado.
- A revisão identificou links de correção para Attempts anuladas ou substituídas;
  a linha do tempo agora expõe a ação somente para a ponta efetiva, com teste.
- A tentativa seguinte do gate encontrou quatro expectativas antigas de UI e
  dois probes de restore no schema pré-S3; as assertions e os probes foram
  atualizados e passaram antes do gate final.

## Gate autoritativo

Comando: `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1`

- Tentativa 1: **RED**, etapa `mypy`, 40 erros de tipagem nos arquivos novos.
- Tentativa 2: **RED**, etapa de testes, 6 falhas: 4 expectativas de UI que não
  consideravam as novas rotas/links e 2 restores S2C/S2D usando schema anterior.
- Tentativa 3: **GREEN**, exit code **0**, execução do gate em **238 s**; 423
  testes aprovados em **193,93 s**, cobertura **87%**; lint, tipos, migrations,
  profiles, cobertura de domínio, detect-secrets e pip-audit aprovados.
- `gate_first_pass: false`; tentativa aceita: **3**. Não houve bloqueio de rede
  nem incidente externo no gate. Uma consulta de ferramenta anterior aos testes
  foi repetida com os caminhos locais de `uv`/cache configurados e não contou
  como tentativa de gate.

## Encerramento

`PROJECT_STATE.md`, plano A4, métricas A7 e contrato arquivado foram atualizados
após o gate GREEN. `tasks/current.md` retorna ao formato `NO_TASK_AUTHORIZED`.
S4+ continuam não autorizadas. Não houve commit, push, tag, release ou operação
de exclusão fora dos testes isolados.
