# V1.0-S1 — contratos e compatibilidade: resultado

## Baseline e escopo

- Data: 2026-09-28
- Task: `V1.0-S1`
- Baseline observado: branch `main`; `HEAD` e `origin/main` em
  `3a1048b3b73663095b65494ea48513b80c9107c8`.
- Preflight: `tasks/current.md` estava `AUTHORIZED` para V1.0-S1; alterações
  preexistentes limitadas ao contrato. S2+ não autorizado; tag `v1.0.0` ausente.
- Escopo executado: auditoria documental e dirigida de implementação/testes dos
  quatro contratos, identidade, matriz de suporte, findings beta e rastreabilidade.
  Nenhuma regra, schema, formato, migration ou feature foi alterada.

## Fontes consultadas

- `AGENTS.md`, `tasks/current.md`, `docs/A3_Progressive_Disclosure.md`,
  `PROJECT_STATE.md`, seção S1 de `tasks/plans/v10-release-execution-plan.md`,
  `quality/v10-p0-planning-result.md` e Roadmap V1 §9.
- Etapa 10: CT-023–043, CT-055–072, CT-092, CT-118–120, CT-127/128 e RNF-063–065;
  RF-034–038, RF-060–062, RF-069 e requisitos RN aplicáveis.
- `docs/V0.5_S1_Contratos_Normativos_e_Invariantes.md`,
  `docs/ADR-013_Ciclo_de_Revisao_na_Ativacao_da_Questao_V0.3.md`,
  `docs/CEI_EXPORT_1_0.md`, `docs/V0.5_S7_Portabilidade_e_Restore.md` e
  evidências S4/S5/S6/S7/S8/S9/S10.
- Policies/services/models diretamente relacionados e testes de revisão,
  lifecycle, Domain, Priority e CEI indicados na matriz do artefato S1.
- `pyproject.toml` e `src/modules/operations/apps.py` para identidade de pacote
  e log.

## Auditoria dos contratos

- **`REV-FIXA-1.0`: consistente para congelamento.** A policy usa D1/D7/D14/D30,
  datas civis explícitas do Workspace, resposta real como âncora, erro em D1+1,
  progressão +7/+14/+30, conclusão após acerto D30, ativação atômica e estado
  temporal derivado. Testes dirigidos cobrem agenda civil, erro por etapa,
  idempotência, facilidade sem efeito de agenda, ativação e ciclo histórico.
- **`DOM-HEUR-1.0`: consistente para congelamento.** Policy pura, adapter
  read-only, Workspace-scoped, componentes, teto pós-erro, confiança separada,
  suficiência, agregação hierárquica e domínio/reabertura permanecem conforme
  decisões V0.5-S4/S5. Não houve recalibração. Testes de policy/evidência e
  integração S5 foram revisados.
- **`PRI-HEUR-1.0`: consistente para congelamento.** Recomendação opcional por
  Subject, fórmula/fatores e evidência indisponível separados de zero,
  `COLLECT_MORE_EVIDENCE`, cálculo exato e desempate por UUID; não ordena a fila,
  não persiste estado nem cria revisão. Vetores puros e integração read-only
  foram revisados.
- **`CEI-EXPORT-1.0`: contrato consistente, compatibilidade futura definida.**
  Formato e manifesto preservados. O emissor V0.5 usa `application_version=V0.5`
  e o importador atual requer produtor e migrations exatos; ainda não implementa
  a política de produtor V1. Isso é gap conhecido do P0, alocado a S2/S6, não
  defeito novo nem motivo para alterar o formato em S1. Prova V0.5→V1 permanece
  obrigatória em S6.

## Decisões e findings

- V10-D1 preservada: `CEI-EXPORT`, `format_version=1.0`, allowlist condicional
  de produtores V0.5/V1.0, validação estrita pré-escrita, sem coerção,
  conversão silenciosa, merge ou adaptação automática de schema.
- V10-D2 preservada: Windows 11 x64, operação local individual em loopback;
  Chrome/Edge/Brave estáveis vigentes, Firefox vigente e imediatamente anterior;
  Safari N/A para a plataforma. A matriz é contrato, não prova de browser V1.
- Identidade contratual: produto `V1.0`, release/tag `v1.0.0`, pacote técnico
  `1.0.0`, e CEI `application_version=V1.0` separado de `format_version=1.0`.
  O estado real ainda contém `0.1.0` em `pyproject.toml` e no log de
  inicialização; gap conhecido encaminhado a S2, sem correção nesta etapa.
- S9 BCR-1: falha original preservada e reprodução controlada PASS,
  `TRANSIENT_NOT_REPRODUCED`. S9 mantém Minor histórico sobre precisão da
  evidência manual de acessibilidade (sem versão exata de browser/detalhe por
  página); o Minor não foi reclassificado e exige evidência direta na validação
  V1. S10-F01/F02/F03 têm falhas originais e retestes distintos, todos resolvidos.
- Nenhuma decisão material nova ou finding contratual S1 aberto foi identificado.
  Handoffs: identity surfaces a S2; prova CEI V0.5→V1 a S6; matriz de browser e
  evidência BCR/acessibilidade a etapas futuras de validação V1.

## Artefatos e revisão

- Artefato canônico: `docs/V1.0_S1_Contratos_e_Compatibilidade.md`.
- A8 standard: **APPROVED** nesta revisão documental; Blocker 0, Major 0 e
  nenhum Minor novo. A ressalva Minor histórica S9 permanece registrada.
- A7 recomendado na autorização: `GPT-6 Luna High`; o modelo efetivo desta
  execução não foi observável por telemetria disponível.
- Referências de arquivos no artefato foram verificadas localmente; o gate
  também validou Markdown/rastreabilidade. `git diff --check` passou.
- Decisão: **`CONTRACTS_FROZEN_FOR_V1`**, congelamento documental apenas. Não
  significa produto implementado, importação CEI V1 comprovada, browsers
  validados, promoção ou release.

## Gate autoritativo

- Comando: `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1`
- Resultado inicial: **GREEN**, exit code `0`, duração observada `319.1 s`;
  `505 passed` em `253.94 s`, cobertura global `86%`.
- Repetição final após atualizar estado, arquivar e restaurar
  `NO_TASK_AUTHORIZED`: **GREEN**, exit code `0`, duração observada `320.6 s`;
  `505 passed` em `261.65 s`, cobertura global `86%`.
- Checks: lock/sync, runtime, rastreabilidade e Markdown, perfis development/
  test/production_local, migrations protegidas, banco vazio, formatação,
  Ruff, mypy (193 fontes), cobertura de domínio, detect-secrets e pip-audit
  (`No known vulnerabilities found`). Nenhuma migration nova.
- Permaneceram 2 `ResourceWarning` de conexões SQLite em
  `tests/test_v05_s2d.py`; o gate terminou exit 0.
- Nenhum focused test foi executado separadamente; os vetores e seus nomes foram
  revisados e a suíte existente executou como parte do gate.

## Encerramento e não ações

- S1 concluída e arquivada; `PROJECT_STATE.md` atualizado; `tasks/current.md`
  retorna a `NO_TASK_AUTHORIZED`.
- S2+ permanece sem autorização. Nenhuma implementação, regra funcional,
  migration, feature, tag, release, commit ou push foi feita.
