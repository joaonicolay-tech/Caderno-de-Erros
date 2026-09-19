# V0.4.2-UX1 — resultado de encerramento

## Problema e mudança mínima

A fila mostrava apenas estágio e data, deixando itens futuros D1 da mesma data
indistinguíveis. O selector permanece a fonte única da fila e de sua semântica
temporal; ele agora carrega, em lote, a taxonomia da questão e sua revisão
corrente. O template mostra enunciado (truncado previsivelmente a 160
caracteres), disciplina/assunto quando presentes e os metadados já existentes.

Não foram exibidos resultado anterior, última tentativa ou dias de atraso:
não eram necessários para identificação e adicionariam densidade ou outra
semântica à superfície.

## Evidência

- Queries: três consultas para uma ou seis entradas (Workspace, Reviews com
  relações diretas e revisões correntes prefetched); o teste detecta regressão
  linear.
- Testes focados: `tests/test_stage4_learning.py` — 8 passed.
- Manual controlado: navegador local exibiu uma atrasada, Hoje vazio, quatro
  futuras D1 na mesma data e uma D7 futura; conteúdo e contexto as
  distinguiram, e o link existente abriu a revisão correta. Em 360 px não
  houve overflow ou sobreposição.
- Acessibilidade: headings, sections/articles, links nativos, estado temporal
  textual e foco existente verificados. Não é alegada conformidade WCAG total.
- Zoom: a automação disponível não produziu uma alteração observável ao tentar
  200%; esta verificação exata fica limitada, sem alegação indevida.
- Migration check: sem mudanças.
- A8 padrão: **APPROVED**, sem Blocker/Major.
- `git diff --check`: PASS.
- Gate autoritativo: **GREEN**, exit 0; 335 passed, cobertura global 88%;
  migrations em banco vazio, Ruff, mypy, detect-secrets e pip-audit aprovados.

## Limites preservados

Sem migration, schema, mudança de `ReviewStatusPolicy`, D1/D7/D14/D30,
ordenação, Workspace scope, fluxo de conclusão, V0.5, commit, push, tag ou
release. `v0.4.1` permanece uma tag anotada: objeto
`9aebb07f22d190666b26bb7b54d5ac447ac71de4`, apontando para o commit de
checkpoint HF1 `acbb497dbdc71f8a3d7893ae4772a87231c281f0`; `v0.4.2` não
existe. O contrato tinha esses hashes invertidos; a divergência foi apenas
registrada, sem alteração da tag.
