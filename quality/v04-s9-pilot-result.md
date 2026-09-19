# V0.4-S9 — Evidência do piloto controlado

- Data: 19 de setembro de 2026.
- Base: branch `main`, commit inicial
  `03a6afd240efc485e9cb29c7f1f00e68c5008ba3`.
- Candidato de entrada: S8 `READY_FOR_PILOT`.
- Ambiente: Windows local, entry point oficial S7 em `127.0.0.1:8000`, banco
  SQLite piloto isolado sob `recovery/`.
- Resultado dos cenários: **PASS**.
- Julgamento humano não fornecido: **NOT OBSERVED**.

## Pré-condições e proteção

S8 estava `COMPLETED`, com review A8 `APPROVED`, Blocker/Major/Minor zero,
gate GREEN, 327 testes, 88% de cobertura, BCR-1 satisfatório, S5/S6/S7
saudáveis e nenhuma migration inesperada. O banco principal identificado foi
`var/development.sqlite3`; ele permaneceu protegido e nunca foi destino de
restore nem exemplar único do piloto.

O backup pré-piloto preservado é
`backups/v04-s9-prepilot-20260919T1927Z.sqlite3`, acompanhado de manifesto.
Criação e validação S6 terminaram exit 0. O restore isolado reconciliou SHA-256,
uma identidade local, um Workspace e dez categorias; SQLite e S5 terminaram
saudáveis, com S5 exit 0, 17 checks e zero findings.

O banco piloto foi derivado somente desse restore. A identidade da cópia foi
pseudonimizada localmente; nenhum conteúdo pessoal foi transcrito para esta
evidência.

## Baseline pré-piloto

| Indicador | Valor |
| --- | ---: |
| Workspaces | 1 |
| Questions | 7 |
| Attempts | 9 |
| ReviewCycles | 5 |
| Reviews | 7 |
| Classifications | 6 |
| S5 | exit 0; 17 checks; 0 findings |
| Aplicação | startup S7 e HTTP 200 em loopback |

## Cenários

| ID | Objetivo e passos essenciais | Resultado observado | Estado |
| --- | --- | --- | --- |
| S9-P01 | Iniciar pela superfície S7 e acessar em loopback | `start-local.ps1`, `127.0.0.1:8000` e HTTP 200 | PASS |
| S9-P02 | Usar dashboard e interpretar métricas | 7 cadastradas/realizadas, 9 tentativas, 3 acertos, 6 erros, 33,3%; revisões e recortes coerentes; `0,0%` distinto de `Sem dados` | PASS |
| S9-P03 | Listar, buscar, filtrar e paginar consulta | Controles funcionais; após dados sintéticos, 11 itens locais distribuídos em duas páginas sem duplicação; busca e filtros combinados retornaram o único item esperado | PASS |
| S9-P04 | Abrir detalhe, timeline e retornar à consulta | Detalhe e eventos coerentes; `return_to` preservou busca, filtros e página | PASS |
| S9-P05 | Criar questão sintética e tentativa inicial incorreta | Questão criada pela UI; tentativa registrada; classificação `Conceitual`; dashboard passou a 8 realizadas, 10 tentativas e 7 erros | PASS |
| S9-P06 | Confirmar classificação e resíduo legítimo | Classificação apareceu em consulta/dashboard; outro erro inicial sem classificação apareceu exatamente uma vez como resíduo | PASS |
| S9-P07 | Executar revisão real e observar estado temporal | Review incorreta concluída; timeline e próximo D7 coerentes; dashboard passou a 1 concluída hoje, 4 atrasadas e 5 futuras | PASS |
| S9-P08 | Confirmar analytics depois das operações | Estado final local: 11 Questions, 11 Attempts, 9 ciclos, 12 Reviews e 8 classifications; deltas reconciliados com as ações | PASS |
| S9-P09 | Testar isolamento entre Workspaces | Fixture sintética externa não apareceu em dashboard/busca; detalhe direto respondeu 404; contagem local permaneceu 11, não 12 | PASS |
| S9-P10 | Executar checker após mutações | S5 exit 0, 17 checks, zero findings | PASS |
| S9-P11 | Validar backup/restore pós-piloto | Backup final, manifesto, SQLite, SHA-256, reconciliação e restore isolado terminaram saudáveis; S5 exit 0 | PASS |
| S9-P12 | Reiniciar e confirmar persistência | Reinício pelo entry point oficial preservou 11 Questions/11 Attempts e respondeu em loopback | PASS |
| S9-P13 | Encerrar e liberar porta | Processos exatos do ensaio foram encerrados e a porta ficou sem listener | PASS com incidente de harness |

Observação visual limitada ao Brave/Chromium disponível: dashboard e consulta
foram legíveis no viewport desktop observado. Leitor de tela, Chrome, Edge,
dispositivo físico e opinião subjetiva não foram observados nesta etapa.

## Findings, correções e retestes

| ID | Tipo/severidade | Esperado versus observado | Tratamento e reteste |
| --- | --- | --- | --- |
| S9-F001 | Finding operacional / Major, resolvido | O primeiro restore pós-piloto deveria reconciliar uma identidade e um Workspace; a fixture temporária de isolamento ainda presente produziu dois de cada e S6 recusou o restore | A fixture sintética externa foi removida somente do banco piloto; `foreign_key_check`, S5, novo backup, validação e restore isolado passaram. Nenhum código de produto mudou |
| S9-I001 | Infraestrutura de automação | `Ctrl+C` deveria alcançar o servidor filho; o PTY interrompeu apenas o wrapper e deixou o Python escutando | PIDs e porta foram identificados antes da limpeza; os processos exatos foram encerrados e a porta foi comprovada livre. S7 do candidato permaneceu inalterado e seus testes passaram |
| S9-I002 | Harness, sem impacto em dados | Uma tentativa de restart por wrapper `.cmd` não herdou a variável do banco piloto e abriu o banco principal | Houve somente GET; nenhum dado principal foi alterado. O restart válido foi repetido pelo entry point oficial com configuração explícita e persistência confirmada |

Tentativas intermediárias de remover a fixture por ORM foram revertidas por
proteções do domínio; nenhuma deixou mutação parcial. A remoção final foi
restrita aos IDs sintéticos do segundo Workspace no banco piloto e seguida de
checks de chaves estrangeiras e S5. Não houve defect de produto, correção de
código, feature, redesign, schema ou migration.

## Baseline pós-piloto

| Indicador local | Antes | Depois | Explicação |
| --- | ---: | ---: | --- |
| Workspaces | 1 | 1 | fixture externa removida após o teste |
| Questions | 7 | 11 | quatro questões sintéticas do piloto |
| Attempts | 9 | 11 | uma inicial e uma REVIEW |
| ReviewCycles | 5 | 9 | quatro questões incorretas sintéticas |
| Reviews | 7 | 12 | D1 inicial e avanço D7 observado |
| Classifications | 6 | 8 | classificação inicial e de revisão |

O backup pós-piloto preservado é
`backups/v04-s9-postpilot-final-20260919T1942Z.sqlite3`, com manifesto. Sua
validação e seu restore isolado terminaram exit 0, com SHA-256 reconciliado,
uma identidade local, um Workspace, dez categorias e S5 exit 0. O backup
pré-piloto também foi revalidado e restaurado isoladamente ao final, exit 0.

## Evidência reutilizada e documentação

- BCR-1 S8 foi reutilizado: três execuções oficiais PASS, dashboard p95 máximo
  1,8390 s e todas as gravações abaixo de 2 s. Não houve mudança de performance.
- Acessibilidade S8 foi reutilizada: PASS assistido, com limitações explícitas
  de browser, zoom nativo e leitor de tela. Não houve mudança de HTML/CSS/UI.
- README e guia S7 cobrem iniciar, encerrar, dashboard, consulta, backup,
  validação, checker, restore, atualização e troubleshooting.
- Os novos artefatos registram apenas IDs sintéticos, contagens, estados e
  resultados; não incluem respostas pessoais, enunciados reais, secrets ou dump.

## Estado final do piloto

S5 final está saudável; S6 pré e pós-piloto está saudável; startup, acesso,
restart e persistência S7 passaram; nenhum processo piloto permanece ativo.
Não há Blocker ou Major aberto. A decisão de promoção e o gate autoritativo
ficam registrados no artefato final de promoção.
