# ADR-004 — Categorias padrão e seed da V0.1

- **Status:** Aceita
- **Data:** 2026-09-02
- **Decisão controlada:** `ERR-V01-009`
- **Requisitos:** `RF-029`, `RN-029`, `RNF-027`, `RNF-033`, `RNF-055`
- **Fluxo:** `FL-023`
- **Testes:** `CT-073`, `CT-081`, `CT-129`

## Decisão

`ErrorCategory` pertence a `modules.errors` (`SDD-MOD-005`) e, nesta etapa,
representa somente categorias padrão. Campos de categorias pessoais, consolidação
e classificação de ocorrências permanecem ausentes.

O código é imutável e único por Workspace. Nome, chave normalizada e descrição
são textos canônicos atualizáveis. O seed localiza cada registro por Workspace e
código e reaplica os textos do catálogo; assim, uma evolução textual controlada
não cria nova identidade nem quebra agregações históricas.

O catálogo em código reproduz literalmente `ERR-V01-009`. O bootstrap coordena
Accounts e Errors na camada de aplicação, dentro de uma única transação. Uma
falha no seed reverte também User e Workspace recém-criados. Repetições mantêm um
User, um Workspace e exatamente dez categorias.

## Schema mínimo da V0.1

- UUID;
- Workspace com exclusão em cascata do agregado;
- código canônico imutável;
- nome de exibição e `name_key` normalizada;
- descrição canônica;
- datas de criação e atualização;
- unicidade de `(workspace, code)`.

`category_kind`, status, consolidação e relações com classificações não são
necessários enquanto categorias pessoais e tentativas estão fora do escopo.

## Itens adiados

Categorias pessoais, arquivamento/consolidação, `ErrorClassification`, tentativas,
questões, taxonomia, interface e todas as capacidades das etapas posteriores.
