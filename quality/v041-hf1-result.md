# V0.4.1-HF1 — Evidência de fechamento

## Defeito, causa e regra

O teste manual pós-`v0.4.0` encontrou o limite A–D na camada de formulário e renderização. A auditoria confirmou que não havia limite correspondente no modelo, schema ou migrations. `RF-011` e `RN-012` exigem duas ou mais alternativas textuais distintas e exatamente uma correta; não definem máximo.

O hotfix passou a criar campos conforme a quantidade submetida ou já armazenada, adicionar uma alternativa sem JavaScript e gerar rótulos alfabéticos sustentáveis (`A`…`Z`, `AA`…), sem introduzir um máximo arbitrário. Fluxos INITIAL e REVIEW continuam usando as alternativas armazenadas e, portanto, aceitam a alternativa correta posterior a D. Questões históricas A–D permanecem compatíveis.

## Evidência funcional

- Reutilizada: 92 testes focados PASS, pois não houve alteração funcional depois dessa execução.
- Teste manual já realizado: questão com cinco alternativas e alternativa E correta; criação, seleção e correção concluídas.
- O gate final executou toda a suíte: 332 PASS, cobertura global 88%.
- Não houve migration nem mudança de schema.

## Auditoria proporcional de hardcodes A–D

Foram revisados os caminhos funcionais de formulário, views e template. Os limites de quatro e o recorte das quatro primeiras alternativas foram removidos dos caminhos de criação/edição. A busca final não encontrou outro pressuposto funcional A–D nesses caminhos. Ocorrências em fixtures, exemplos e testes que deliberadamente usam quatro alternativas não foram alteradas, pois não limitam o comportamento do produto.

## Gate e review

- `git diff --check`: PASS, exit 0 antes do fechamento.
- Primeira passagem do gate: inconclusiva por `pip-audit` com `WinError 10013` ao acessar PyPI; classificada como `infrastructure/network`, não como retrabalho funcional. `gate_first_pass: false`.
- Repetição autorizada com rede: GREEN, exit 0; 332 testes em 87,85 s, 88% de cobertura, migrations sem mudanças, formatação, Ruff, mypy, cobertura de domínio, `detect-secrets` e `pip-audit` aprovados; `pip-audit` informou “No known vulnerabilities found”. Duração total do gate: 123,3 s.
- A8 padrão: **APPROVED**; Blocker 0, Major 0, Minor 0 aberto. Não houve motivo para elevar a revisão: não há migration, mudança de armazenamento nem impacto estrutural.

## Tags e escopo

- `v0.4.0`: confirmada por leitura em `69026ffe91b39ea9c9772e7d2782b47c9d163f6b`; permaneceu inalterada.
- `v0.4.1`: inexistente; não foi criada.
- Não houve alteração em `quality.ps1`, fila de revisões, V0.5, commit, push, tag ou release.

O código está pronto somente para checkpoint Git humano e posterior criação explicitamente autorizada de `v0.4.1`.
