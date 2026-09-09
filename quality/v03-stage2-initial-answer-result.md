# V0.3 — Etapa 2 — Resultado da Resposta Inicial Protegida

| Campo | Resultado |
|---|---|
| Data | 8 de setembro de 2026, America/Sao_Paulo |
| Decisão | **GREEN — Etapa 2 concluída** |
| Gate autoritativo final | Execução direta, exit code 0, 81,8 s |
| Testes E2 | 30 aprovados em banco descartável |
| Regressão completa | 240 aprovados; pytest em 60,66 s |
| Cobertura global | 87% (linhas e branches, relatório pytest-cov) |
| Cobertura crítica | Mínimo de 80% de linhas por módulo do manifesto atendido |
| P0/P1 aplicável aberto | Nenhum identificado |
| Migrations | Nenhuma criada ou alterada; checks e hashes GREEN |
| Próximo estado autorizado | Nenhuma tarefa; E3 não preparada nem iniciada |

## Entrega e fronteiras

`src/modules/attempts/services.py` implementa `AttemptService`: autorização pelo
proprietário ativo e Workspace, apresentação por projeção sem gabarito,
validação de revisão/versão/alternativa, avaliação exclusivamente no servidor,
contexto transitório, confirmação correta e replay por recibo/hash canônico.
Acerto grava somente `Attempt(INITIAL, correta)` e `OperationReceipt`.

`src/modules/reviews/services.py` implementa somente
`CompleteReviewService.complete_initial_error(...)`. Ele recupera o contexto
do servidor e calcula internamente o hash; não aceita resultado ou hash do
chamador. Após diagnóstico válido, grava na mesma transação `Attempt`,
`ErrorClassification`, `ReviewCycle(ACTIVE, INITIAL_ERROR, REV-FIXA-1.0)`,
`Review(PENDING, D1)` e `OperationReceipt`. A data D1 é a data civil da avaliação
mais um dia, usando o calendário existente. Não cria revisão histórica de
diagnóstico nem implementa `complete_review(...)`.

## Contexto e HTTP

- `src/modules/attempts/context.py`: memória efêmera do processo local, com
  identificador imprevisível, nonce, usuário, sessão, Workspace e sua versão,
  questão/revisão, alternativa, resultado calculado, lock_version, instante,
  fuso e expiração fixa em 15 minutos desde a avaliação.
- Cookie de sessão opaco e assinado, HttpOnly e SameSite=Strict; Secure quando
  servido por HTTPS. A identidade local permanece definida pelo servidor,
  conforme ADR-003/006. Nenhuma tabela de sessão ou infraestrutura externa.
- Expiração expurga o contexto; cancelamento o descarta. Nenhuma dessas ações
  cria fatos. Reinício do processo invalida os contextos e exige nova resposta.
  O armazenamento é deliberadamente local a um processo, sem coordenação entre
  processos; a integridade persistente depende também do SQLite e constraints.
- Reload do feedback usa GET após redirect, sem renovar TTL. Contexto consumido
  não revela novamente a correção; a mesma chave/payload recupera o recibo na
  confirmação e outra chave conflita. O contexto expirado é rejeitado.
- Forms, views, URLs e `src/templates/attempts/initial.html` adaptam a jornada
  em `/initial/<question_id>/`; o catálogo recebeu o acesso “Responder”.
- Projeção inicial não contém gabarito, explicação, pegadinha nem model de
  revisão no contexto do template. Cookies/tokens não carregam conteúdo de estudo.
- CSRF nas mutações, campos permitidos explícitos, rejeição de campos extras e
  repetidos, HTML escapado, respostas sem cache e Referrer-Policy no-referrer.
- Eventos mínimos em `operations/events.py` usam a correlação e sanitização
  existentes, sem conteúdo de estudo, token, sessão ou corpo HTTP.

## Atomicidade, contenção e conflitos

Confirmações usam `transaction.atomic(durable=True)`, sem sucesso antes do
commit. A atualização condicional de `Question.lock_version` adquire a escrita
SQLite e impede confirmação baseada em versão perdida; o incremento participa
do mesmo rollback dos fatos. Models E1, policies e constraints permanecem intactos.

O serviço reutiliza a política E1: busy_timeout de 5 s, uma repetição após
150 ms somente para SQLITE_BUSY/locked. Segunda contenção retorna
PERSISTENCE_FAILURE; outros erros não são repetidos. O contexto fica vinculado
à mesma chave e hash após a primeira confirmação válida, inclusive em rollback.

O hash canônico inclui identidade, Workspace, nonce, revisão, alternativa,
versão, resultado calculado e diagnóstico normalizado. O recibo contém somente
os metadados técnicos E1. Mesma chave/payload recupera o resultado; payload ou
chave divergente conflita sem duplicação.

## Provas executadas

`tests/test_initial_attempt.py` tem 30 casos parametrizados, determinísticos
quanto a entradas e asserções, sem dados pessoais reais, somente em banco
descartável; os testes exercitam persistência real, sem aprendizagem fictícia.

| CT / requisito | Evidência principal |
|---|---|
| CT-013, CT-016 | Avaliação sem fatos; acerto com tentativa/recibo; rejeição de segunda inicial |
| CT-014 | Cinco fatos no erro e rollback após cada save, inclusive recibo; disputa real entre duas threads/conexões com contextos distintos |
| CT-015 | Comparação no servidor e rejeição de resultado alegado/campos adicionais |
| CT-017 | Categoria obrigatória, OTHER vazio/whitespace e descrição excessiva recusados; normalização |
| CT-018 | Dois Workspaces reais, proprietários distintos e categoria cruzada recusada |
| CT-021 | Fronteira 14:59/15:00, TTL sem renovação, cancelamento e ausência de fatos |
| CT-022, CT-093 E2 | HTTP protegido, CSRF, escaping, ausência de correção antecipada, cache e confirmação |
| CT-100 | Eventos formatados com correlação e ausência de conteúdo/token nos logs |
| CT-101 E2 | Contexto adulterado, usuário/sessão/Workspace cruzados, versão, revisão, arquivamento e expiração |
| RNF-025/026/031/032 | Replay, hash divergente, contexto consumido, chave diferente após falha, rollback, contenção e recuperação |

Teste adicional de chamada direta ao orquestrador confirma que ele rejeita
acerto e payload divergente, sem depender da view ou de hash fornecido pelo
chamador. Os CTs das etapas futuras não foram promovidos por esses testes E2.

## Gate e ocorrência ambiental

Comando final executado diretamente em PowerShell:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1
```

Resultado: **exit code 0**, 81,8 s. Lock/toolchain, rastreabilidade, perfis,
migrations, instalação vazia, Ruff, mypy, testes/cobertura, segredos e auditoria
de vulnerabilidades passaram. `pip-audit`: nenhuma vulnerabilidade conhecida.

Uma execução intermediária falhou por bloqueio de rede do sandbox (WinError
10013); não foi considerada GREEN. Uma execução com saída redirecionada mostrou
sucesso interno mas retornou código externo 1; também não foi usada para encerrar.
A execução direta final, com acesso à rede, removeu essa ambiguidade.

`quality/v03-stage2-gate.json` preserva as evidências e hashes anteriores e
acrescenta os CTs E2 e os três novos módulos de domínio ao mínimo de cobertura.
`scripts/quality.ps1` aponta para esse manifesto. Relatório de cobertura local:
`.tools/quality/coverage.json`.

## Encerramento

`PROJECT_STATE.md` foi reconciliado com a autorização E2 recebida neste chat:
o estado anterior ainda dizia “E2 não preparada”, embora a tarefa formal e o
pedido autorizassem sua execução. A E2 foi arquivada em
`tasks/completed/v03-stage2-initial-answer.md`; `tasks/current.md` fica sem
próxima tarefa autorizada.

Sem migrations, dependências novas, mudanças em models/policies E1, E3+,
commit, push, tag, release ou promoção da versão. E3 não preparada nem iniciada.
