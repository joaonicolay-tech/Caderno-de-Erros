# V1.0-S2R4 — CEI QUE-003 pre-write remediation

**Decisão: HUMAN_DECISION_REQUIRED. Correção QUE-003 verificada; novo S6-F04 Major/P1 aberto na auditoria solicitada.**

O pacote F03 exato é agora rejeitado antes de escrita. O gate integral próprio passou. A auditoria exigida pela seção8 encontrou uma família mais ampla de invariantes determinísticas ausentes; uma delas, REV-003, foi reproduzida independentemente com commit inválido. A etapa não foi declarada concluída.

## Relatório final — 42 campos

| # | Campo | Resultado observado |
| --- | --- | --- |
| 1 | START_TIME | 2026-10-01 11:19:45 -03:00 |
| 2 | END_TIME | 2026-10-01 11:58:39 -03:00 |
| 3 | Duração observada | 0:38:54 |
| 4 | Modelo | GPT-6.1 Sol High, autorização humana específica S2R4 |
| 5 | S6-F03 histórico | RED original intacto: Question ACTIVE sem current aceita,24 INSERTs commitados,total_changes+24,checker25/1 QUE-003 ERROR. Novo pré-fix automatizado reproduziu exatamente isso, exit2 |
| 6 | Causa raiz | Preflight S2R3 consultava só ATT-001/ERR-001/REV-001/REV-002; QUE-003 omitida. Unicidade física não exige existência. Checker mode=ro separado dentro atomic vê destino anterior commitado vazio |
| 7 | QUE-003 normativa | Toda revisão: versão contígua desde1. ACTIVE/ARCHIVED: exatamente1 current. ACTIVE: current com stem/answer não-NULL e >=2 alternatives. DRAFT sem current/revisão legítimo; ARCHIVED incompleta permitida por esta regra; histórico não-current preservado |
| 8 | Implementação | Adicionar QUE-003 à tupla de regras executadas na mesma projeção privada SQLite :memory: já existente, com as mesmas oito tabelas. Nenhum hardcode de UUID, silent repair ou expansão de arquitetura implementada |
| 9 | Reutilização | invariant_sql_rules fornece SQL original inteiro do checker; integrity.py/QUE-003 byte-equal. Zero duplicação SQL/semântica; código de regra única compartilhada |
| 10 | Código alterado | src/modules/data_management/portability.py: docstring e inclusão de QUE-003 na seleção; único AST de função alterado _validate_semantics. Demais funções/constantes iguais à fotografia pré-fix |
| 11 | Testes | Novo tests/test_cei_question_invariant.py:20 negativos reader/direct mutated object e6 positivos importados/checker25/0. Testes S2R3/F01 e probes anteriores inalterados |
| 12 | RED histórica | S6 original e novo work/s2r3-s2r4-red-20261001 preservados NON-CANDIDATE, nunca reutilizados. quality/v10-s2r4-red-historical.json; rótulo bruto do harness F02 retido, caso F03 explicitamente separado |
| 13 | Reteste F03 | PASS / REJECTED_BEFORE_WRITE; mesmo ZIP adversarial preservado, target novo work/s2r3-s2r4-f03-20261001; erro explícito QUE-003; pacote hash-igual |
| 14 | INSERT/UPDATE/DELETE | F03 attempted/completed 0/0/0. Válido importa normalmente. Audit F04 distinto attempted/completed24/0/0 commitados |
| 15 | total_changes | F03 delta0; F01/F02 delta0; novo audit F04 delta+24. Rollback posterior não usado como prova pré-write |
| 16 | Counts | F03/F02 full counts antes=depois; F01 target igual; válido todos21conjuntos iguais à fonte preservada. F04 full counts mudaram por commit |
| 17 | Fingerprints | F03/F02 semântico/schema/físico iguais; F01 lógicos/físicos iguais. Válido projectionhash igual e leitura/checker/derivados sem mutação. F04 semântico/físico alterados/schema igual |
| 18 | Bordas QUE-003 | ACTIVE/ARCHIVED exatamente1 PASS; zero/>1 REJECT em ambos entrypoints; versões inicial2/lacuna/duplicada REJECT; ACTIVE sem stem/answer/<2alts REJECT; DRAFT sem current/sem revisions/incompleto e ARCHIVED current incompleto PASS com checker25/0 |
| 19 | Import válido | VALID_IMPORT_PASS: export produzido pelo runtime V0.5 real preservado, import freshV1 e reexport igualdade21sets/UUIDs/relações/history/revisions/attempts/policies/derived. SQLiteok/FKempty/checker25/0; nenhuma repetição de upgrade/recovery/segundo roundtrip |
| 20 | F01/N9 | Fresh target V0.4.4 rejeitado por migrations incompatíveis antes de attempted/completed0/0/0,total_changes0,full counts/fpsiguais. F01 continua protegido; FAIL histórico intacto |
| 21 | F02 | Mesmo ZIP original rejeitado antes de0writes com ATT-001/ERR-001/REV-001/REV-002 explícitos; fullcounts/fpsiguais; proteção S2R3 intacta |
| 22 | N1–N8 | ASTs de validadores estruturais e sua ordem intactos; provas diretas históricas preservadas. Regressões automatizadas destino/portability/focadas/fullgate executadas; nenhuma repetição manual completa S6 |
| 23 | Focados | 69 testes únicos PASS em execução+reteste. Inicial67PASS/2FAIL em254,13s; dois casos ARCHIVED tinham fixture com ciclo ACTIVE indevido. Ajustada à suspensão normativa e reteste2PASS/14,57s. Soma268,70s. FAIL/log/XML/fixture inicial preservados; gate depois569PASS em única execução |
| 24 | Migrations | 0nova/model/schema; gate makemigrations --check --dry-run PASS. Checker/modelos/migrations preservados; nenhuma migration necessária para QUE-003 |
| 25 | Formato | CEI-EXPORT-1.0 / format_version1.0 / allowlist V0.5,V1.0 / policies inalterados; nenhum merge/conversion/remapping/repair/coercion/schema adaptation |
| 26 | Gate S2R4 | GREEN próprio / exit0 observado / 741.38s. Lock/runtime/Ruff/mypy/Django/migrations/coverage/secrets/audit PASS. Predate novo finding F04 da A8 e não equivale a aprovação |
| 27 | Total testes | 569 PASS no gate integral; pytest 648.39s;69 únicos focados ao final |
| 28 | Coverage | 86.6284361915% global; verificação de cobertura de domínio PASS; fonte .tools/quality/coverage.json fotografada no JSON do gate |
| 29 | pip-audit | PASS próprio /0 vulnerabilidades conhecidas; gate concluiu auditoria sem alterar dependências. Não inferido de gate anterior |
| 30 | A8 deep | CHANGES_REQUIRED / NOT APPROVED. Correção QUE-003 verificada; auditoria obrigatória all25 invariants revelou gap material equivalente S6-F04/REV-003. Revisão pelo executor, sem alegar reviewer independente |
| 31 | Blocker/Major/Minor | 0/1/0: S6-F04 Major/P1 OPEN. Defeito F03 corrigido e testado, aceite formal da etapa retido por auditoria; outros candidatos por inspeção não classificados como commit findings reproduzidos |
| 32 | S6-F03 final | FIX_VERIFIED / PASS / REJECTED_BEFORE_WRITE. Não promover formalmente S2R4_COMPLETED/S6-F03 RESOLVED sob seção22 enquanto aceite S2R4 falha; nunca reinterpretar RED original |
| 33 | Artefatos | quality/v10-s2r4-{normative-rule,red-historical,f03-retest,f02-retest,n9-retest,valid-import,focused,preservation,invariant-audit,audit-f04-result,gate,a8-deep,final-verification}.json; quality/v10-s2r4-cei-que003-result.md; novo teste; logs/ZIPs/targets/provenance brutos em work |
| 34 | PROJECT_STATE | S2R4 AUTHORIZED/BLOCKED/HUMAN_DECISION_REQUIRED; S6 BLOCKED/PAUSED/RETOMÁVEL; F03 fix verified/F04 MajorOPEN; etapas anteriores COMPLETED; histórico preservado |
| 35 | tasks/current | V1.0-S2R4 AUTHORIZED / BLOCKED / HUMAN_DECISION_REQUIRED; não arquivada, não NO_TASK_AUTHORIZED, não restaurada a S6 antes de aceite |
| 36 | S6 retomável | Contrato bloqueado byte-preserved tasks/paused/v10-s6-upgrade-recovery-after-s2r3.md. Após decisão/remediação/aceite futuros, repetir só CEI afetado e final gate/A8 próprios; upgrade/clean/backup/restore/recovery/RPO-RTO/roundtrip válidos preservados |
| 37 | S7–S10 | NOT AUTHORIZED; nenhuma execução futura iniciada |
| 38 | .secrets.baseline | Bytes/detectores/filtros/staging anteriores iguais; somente baseline já staged pela autorização humana antiga; zero novos registros ou staging |
| 39 | git diff --check | PASS /exit0 observado; advertência CRLF antiga da métrica não é falha; verificação final e metadados em JSON próprio |
| 40 | git status --short | Todos caminhos classificados pela cadeia S6/S2R2/S2R3/S2R4; lista literal no JSON final. HEAD=origin/main=SHA1:5eb6930aba35a0d1083c92816a83c7c4c2451830 intactos |
| 41 | Git/publicação | Nenhum git add,commit,push,tag,release/checkpoint. Nenhuma S6 funcional/futura antecipada; no broader fix |
| 42 | Decisão | HUMAN_DECISION_REQUIRED. S2R4_COMPLETED não declarado; gateGREEN não supera Major da auditoria. Parada aplicada após reprodução F04, somente docs/read-only metadata afterward |

## Novo S6-F04 — finding material equivalente

**[Major/P1] portability.py:642 / integrity.py:819 — ARCHIVED Question com
ACTIVE ReviewCycle e PENDING Review passa as cinco regras e é commitada.**

- Fonte real V0.5 válida original preservada; somente Question.status mudou
  ACTIVE→ARCHIVED e archived_at recebeu o activated_at já existente. Checksums
  e tamanho desse único membro recalculados. Todos os outros membros idênticos.
- Revisão corrente/completude/UUIDs/Attempt/policies/schema/formato intactos.
  O pacote não viola QUE-003, que agora está corretamente protegida.
- Regra existente REV-003 exige Question ACTIVE para ciclo ACTIVE e exatamente
  uma Review PENDING; suspensão legítima ARCHIVED foi exercitada nos testes.
- validate_export ACCEPTED, import_into_empty sem exceção: **24 attempted e
  completed INSERTs commitados, UPDATE/DELETE0, total_changes+24**.
- Checker independente pós-commit: **25 checks /1 finding REV-003 ERROR** em
  ReviewCycle. SQLite integrity ok, FKempty; counts/fps semântico/físico mudam.
- Target novo work/s2r3-s2r4-audit-rev003-20261001 é NON-CANDIDATE preservado;
  nunca reutilizado. Pacote/provenance/log/result brutos intactos.
- Causa comum: SQL REV-003 não selecionado; checker mode=ro dentro atomic
  não vê linhas ainda não commitadas. Impacto: questão arquivada com lifecycle
  de aprendizado ativo/pendente incompatível com histórico e fila.

## Por que a autorização precisa de decisão humana

A alteração local QUE-003 usa todo o SQL normativo existente, incluindo
sequência/completude/exceções, e não requer nova arquitetura. A auditoria das
25 invariantes evidencia que as cinco regras pré-write não cobrem todo estado
CEI determinístico: há regras relacionais de taxonomia/revisões, lifecycle e
substituições, categorias e histórico, reviews/scheduling/audit, filtros e
domínio não consultadas, além de helpers IANA/datas civis/inaugurais.

Somente REV-003 foi confirmado como novo commit finding independente. Os
outros são gaps/candidatos por inspeção, sem inventar prova de commit. Receipts
excluídos do CEI, diagnósticos físicos e retenção dependente de relógio foram
separados dos predicados CEI determinísticos; nenhuma regra nova foi criada.

Uma proteção geral exige decidir seleção de invariantes, projeção dos outros
conjuntos e contexto de owner não exportado, reutilização de helpers Python e
limites do checker. Essa ampliação de responsabilidade ultrapassa a correção
exclusiva de QUE-003. A seção8 exige **HUMAN_DECISION_REQUIRED** para ampliação
grande; não se adicionou silenciosamente mais um patch específico REV-003.

Direção concreta para uma nova autorização: validação pré-write das invariantes
normativas determinísticas demonstráveis pelo CEI, com regra compartilhada,
projeção isolada e limites explícitos para receipts/retention/owner/runtime;
testes negativos por regra e imports históricos válidos. Isso não autoriza
migrations, formato novo, repair, merge ou retomada automática de S6.

## Preservação e revisão

46 arquivos protegidos e124 artefatos históricos hash-iguais; original de
portability.py e contrato S6 mais recente fotografados separadamente. Nenhum
modelo/schema/migration/checker/contrato CEI/A4/policy alterado. Somente
_validate_semantics mudou: docstring e inclusão de QUE-003 na tupla.

F03/F02/F01 zero-write e import válido PASS são resultados desta execução.
69 focados únicos passaram via execução+dois retestes de fixture, cuja falha
foi preservada; o gate depois passou todos569 em uma execução. A8 deep não
aprovou o candidato por S6-F04, apesar do gate GREEN.

S2R4 permanece AUTHORIZED/BLOCKED; S6 BLOCKED/PAUSED/RETOMÁVEL. Nenhum contrato
foi arquivado como concluído ou restaurado para execução S6. S7–S10 continuam
NOT AUTHORIZED. Sem staging/publicação/Git checkpoint. **STOP.**
