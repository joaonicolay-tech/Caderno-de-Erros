# V0.3 — Etapa 5 — Integração, Migração, Regressão, Carga/Concorrência e Promoção

## Autorização e objetivo

Esta é a tarefa formal de **VALIDAÇÃO E PROMOÇÃO** da V0.3. O nome adota o recorte canônico de ADR-011 §9 e esclarece que "migração" inclui instalação limpa e upgrade representativo; não autoriza migration nova. E0–E4 estão concluídas e GREEN. A E5 está formalmente liberada, mas ainda não iniciada.

O objetivo é executar a validação integrada final do ciclo de aprendizagem e promover V0.3 somente se toda evidência obrigatória estiver GREEN. A etapa não cria capacidade de produto.

## Fontes, invariantes e fora de escopo

- Consultar `AGENTS.md`, `PROJECT_STATE.md`, `docs/README.md`, ADR-011 §§2–9, o Roadmap §§6, 11 e 23, o Plano de Testes e os resultados/manifestos E1–E4. Código, migrations e testes existentes continuam sendo a fonte primária.
- Preservar integralmente migrations V0.1/V0.2/V0.3-E1, ADR-011, manifestos E1–E4, Workspace, fatos históricos imutáveis, `REV-FIXA-1.0`, Clock/Calendar, contexto transitório, idempotência, transações curtas e política SQLite.
- Não criar funcionalidade V0.4, dashboard, métricas, domínio, prioridade, recomendação, revisão adaptativa, reagendamento, reativação, exportação, entidade, migration ou refatoração oportunista. Uma falha encontrada deve bloquear a promoção e ser registrada; correção só ocorre sob nova autorização.

## Fluxo completo de demonstração

Com dados sintéticos controlados, demonstrar e automatizar quando viável:

1. questão `ACTIVE` recebe resposta inicial incorreta, classificação e ciclo;
2. D1 é criada, acertada e progride para D7; D7 acertada progride para D14; D14 acertada progride para D30; D30 acertada conclui o ciclo;
3. fila derivada é correta em cada estado e a timeline permanece consultável;
4. erro em D7, D14 ou D30 reinicia em D1 e preserva o mesmo ciclo conforme `REV-FIXA-1.0` e ADR-011.

## Cenários integrados obrigatórios

- resposta inicial correta sem ciclo; abandono antes de confirmar; contexto expirado; replay com a mesma chave; e payload divergente sem mutação;
- duas abas, Review futura, isolamento de Workspace e nenhuma antecipação de gabarito; resultado calculado exclusivamente no servidor;
- correção auditável de diagnóstico, arquivamento com ciclo ativo, suspensão e preservação integral do histórico após arquivamento;
- CSRF, escaping, logs sanitizados, minimização de `OperationReceipt`, ausência de tentativa duplicada e rollback integral sem gravação parcial.

## Instalação limpa, upgrade e recuperação

- **Instalação limpa:** em banco vazio e isolado, aplicar todas as migrations, bootstrap e fixture aplicável; verificar integridade, inicialização da aplicação e gate. Não depender de arquivo acidental do ambiente local.
- **Upgrade:** provar `v0.2.0 → V0.3` em cópia representativa e descartável, preservando usuário, Workspace, timezone, locale, taxonomia, questões, `QuestionRevision`, alternativas, origem e fatos V0.2; depois criar e usar corretamente as entidades V0.3.
- **Backup/restauração:** exercitar dados V0.3 reais sintéticos, preservando `Attempt`, `OperationReceipt`, classificações e revisões, ciclos, Reviews, relações, timestamps, timezone/data civil e integridade referencial. A cópia corrompida deve ser rejeitada pelas garantias existentes antes de substituição.

## Concorrência e temporalidade

- Provar duas respostas iniciais concorrentes, duas conclusões da mesma Review, duas correções de diagnóstico e arquivamento concorrendo com conclusão. Confirmar contenção SQLite, `busy_timeout` de 5 s, único retry de 150 ms para `SQLITE_BUSY`/locked, ausência de duplicação e de falso sucesso.
- Cobrir D1/D7/D14/D30, data civil, timezone, atraso, Review futura, virada de dia e Clock/Calendar controláveis. Executar `CT-107`/`BCR-1` somente no recorte aplicável à V0.3; medir e registrar ambiente, carga e resultado.

## Acessibilidade e CTs

Definir no resultado o recorte automatizado e manual vinculante do Plano de Testes. Cobrir teclado, foco, labels, erros, fila, Review, timeline, correção de diagnóstico, zoom e largura reduzida; Chrome/Edge somente quando exigidos pelo Plano. Evidência manual fornecida pelo usuário deve ser identificada como tal.

Mapear em matriz executável todos os CTs V0.3 aplicáveis à promoção: `CT-013` a `CT-019`, `CT-021` a `CT-042` no recorte de ADR-011 §8, `CT-073`, `CT-074`, `CT-076` a `CT-082`, `CT-093`, `CT-100`, `CT-101`, `CT-107`, `CT-111`, `CT-123` e `CT-125`. Diferenciar explicitamente parcelas futuras (métricas e dashboard V0.4; reativação, reagendamento, domínio e prioridade posteriores).

## Manifesto, evidências e gate

Durante a execução futura, criar `quality/v03-stage5-gate.json` próprio e fazer o gate apontar somente para ele. E1–E4 são históricos imutáveis: manter hashes e proteção automatizada que os compare aos blobs históricos. Esta autorização não cria o manifesto.

Produzir uma matriz `critério → evidência → status`, sem PASS sem prova, para: E0–E4 concluídas; CTs obrigatórios; fluxo completo; instalação limpa; upgrade; backup/restauração; concorrência/idempotência; temporalidade; segurança e Workspace; migrations/manifestos preservados; cobertura; ausência de P0/P1; e ausência de capacidade V0.4 antecipada.

Executar e registrar obrigatoriamente:

`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1`

O exit code deve ser `0`. O gate deve cobrir suite completa, cobertura, Ruff, mypy, migrations, `git diff --check`, segredos, dependências, rastreabilidade, hashes e manifestos. Falha ambiental nunca é PASS artificial; ela bloqueia a promoção até evidência válida.

## Artefatos finais esperados

Se a E5 for executada e aprovada, entregar `quality/v03-stage5-gate.json`, resultado integrado com matriz de evidências/CTs, relatório de instalação/upgrade/backup-restauração/concorrência e decisão formal de promoção. Cada artefato deve usar dados sintéticos e registrar ambiente, comandos, status e limitações. Nenhum destes artefatos é criado nesta autorização.

## Promoção condicionada e encerramento

Somente com todos os critérios GREEN, registrar a decisão formal **V0.3 — PROMOVIDA**, criar evidência final de promoção, atualizar `PROJECT_STATE.md`, arquivar esta tarefa e deixar `tasks/current.md` sem tarefa autorizada. Informar apenas se o repositório está pronto para commit final, tag local `v0.3.0` e push da tag posteriores; não executar commit, push, tag ou release automaticamente.

## Critérios de aceite

- Toda a matriz de promoção possui evidência correspondente e status GREEN.
- O fluxo completo e todos os cenários integrados obrigatórios passam.
- Instalação limpa, upgrade e backup/restauração reconciliada passam.
- Provas de concorrência/idempotência/temporalidade e segurança/Workspace passam.
- CTs V0.3 aplicáveis passam; P0/P1 aplicável aberto é zero.
- Migrations E1 e manifestos E1–E4 permanecem intactos; E5 tem manifesto próprio.
- O gate final retorna exit code 0 e nenhuma capacidade V0.4 é antecipada.

## Proibido nesta execução futura

Não promover se qualquer condição falhar. Não criar funcionalidades, migrations ou entidades novas, nem iniciar/preparar V0.4. A presente execução é apenas a autorização documental: não implementar E5, não criar manifesto E5, não rodar a promoção, nem fazer commit, push, tag ou release.
