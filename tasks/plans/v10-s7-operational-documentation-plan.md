# V1.0-S7 — A4 Documentação operacional e candidato de release

**Estado deste artefato:** COMPLETED em 2026-10-03; A4 aprovada e provas concluídas. Registro inicial preservado abaixo.
**Baseline auditada:** `ac13fb2c5023fbb1c6ccc69ab4059d0367f899ea`, `HEAD == origin/main`; árvore inicial limpa.
**Classificação:** V1.0-S7; tamanho M; risco medium; migration expectation NO; dados reais NO; A7 GPT-6 Luna Medium (seleção autorizada pelo usuário; identidade runtime não observada); A8 standard.
**Janela da auditoria inicial:** START_TIME `2026-10-02 19:28:12 -03:00`.

## Objetivo e limite

Reconciliar documentação operacional do candidato V1.0 e decidir se um operador independente consegue instalar, usar, atualizar, proteger e recuperar uma cópia seguindo apenas as instruções candidatas. O resultado permanece `release candidate documentation` até promoção e autorização próprias.

Esta etapa não autoriza GitHub Release, tag `v1.0.0`, promoção, instalador/launcher novo, serviço/tray/auto-installer, empacotamento, experiência de um clique, redesign, feature, alteração de schema/contrato CEI, migration, S8, S9 ou S10. Nenhum dado pessoal real será usado. Cópias sintéticas/descartáveis somente.

## Fontes de decisão

1. Código/migrations, testes e evidência observada.
2. Contratos congelados S1–S6 e S6R1; V10-D1/D2; adendo de browsers S4.
3. Documentação formal compatível, sem editar retrospectivamente contratos congelados.
4. `PROJECT_STATE.md` para estado; `tasks/current.md` como autorização executável.

O adendo S4 prevalece para browsers. O contrato CEI permanece `CEI-EXPORT-1.0` com `format_version=1.0`; produtores permitidos `V0.5`/`V1.0`, destino compatível vazio, validação pré-escrita, sem merge, conversão, coerção, adaptação, importação parcial ou repair. Migration nova é NO; se documentação exigir mudança de schema/modelo, parar `HUMAN_DECISION_REQUIRED`.

## Auditoria inicial observada

- README cobre instalação, primeiro uso, operação, atualização, backup, restore e troubleshooting, mas abre como V0.5 beta; atualizar o estado e testar comandos.
- Guia Windows legado existe em `docs/V0.4_S7_Operacao_Windows.md`; preservar sua história e reconciliar seu uso como operação vigente.
- Contrato CEI existente descreve `application_version=V0.5`, enquanto S1/código/testes registram produtores V0.5/V1.0. É defasagem documental reconciliável, não mudança do formato.
- Notas de release só localizadas para V0.1; changelog não localizado no inventário Markdown. Confirmar busca na próxima execução antes de escolher/criar convenção.
- `PRODUCT_VERSION="V1.0"`; `pyproject.toml` package version `1.0.0`; CEI format `CEI-EXPORT-1.0`/`format_version=1.0`. Código, manifesto e testes sustentam distinção.
- Browser vigente: Brave 1.96.59, Windows 11 x64, padrão/extensões desabilitadas, VALIDADO OFICIALMENTE PARA V1; Chrome NOT_EXECUTED/NOT VALIDATED; Edge/Firefox atual/anterior NOT_EXECUTED/OPTIONAL; Safari N/A para Windows 11 x64.
- README já menciona `uv 0.12.7`, Python 3.13.15, `uv sync --locked`, `scripts/start-local.ps1`, loopback; S7 deve validar esses passos sem presumir validade pela presença documental.

## Fluxo proposto e evidência

Cada ensaio usa ambiente/cópia isolada sintética, registra comandos literais, hash/path dos artefatos, resultado e saída essencial. Capturar estado pré e pós; cópia descartável nunca é um banco ativo. Critérios de parada aplicam-se imediatamente. Conservar evidência anterior, inclusive FAILs, sem sobrescrever.

| Prova | Entrada e pré-condição | Passos/documentação | Evidência e esperado | Parada e recovery |
|---|---|---|---|---|
| CT-127 instalação limpa | Windows 11 x64 descartável; sem venv/runtime/banco/config do projeto; candidato identificado | Seguir somente README: pré-requisitos; obter checkout/candidato; `uv`; runtime Python; sync lock; setup/migrate/bootstrap; start-local; abrir 127.0.0.1; primeiro acesso; smoke mínimo; Ctrl+C | Comandos exatos, versões, logs/exit, health e estado mínimo, nenhum conhecimento implícito; PASS somente se todos os passos independentes | Comando/path inexistente, instrução ambígua, rede/pacote não disponível ou dado escrito fora alvo: parar; preservar logs/cópia e desfazer apenas o ambiente descartável |
| Primeiro uso | instalação limpa aprovada e banco sintético vazio | seguir setup inicial e fluxo mínimo descrito; verificar primeiro acesso e estado local | URL loopback, workspace/categorias conforme código atual; nenhum dado real | divergência de comportamento/config: parar e registrar |
| Atualização | checkout/snapshot V0.4.4 representativo sintético e cadeia comprovada S6; backup prévio validado | documentar obter candidato, parar server, preservar mudanças, backup, atualizar código, `uv sync --locked`, migrations explicitamente declaradas, validação e startup | comandos, revisão antes/depois, manifesto/hash, saída migrate/checker, reconciliação; separar update código/deps/migrations | upgrade falha, migration não documentada, fingerprint divergente; parar, manter cópias, seguir somente recovery comprovado; não inventar downgrade |
| Backup | banco sintético isolado, aplicação/config identificadas | quando/quais dados; pré-operação; executar backup; validar arquivo+manifesto; guardar separadamente | arquivo+sidecar, hash/tamanho, checker e localização; backup válido não equivale a restore provado | overwrite/paths ambíguos, falha checksum; preservar origem e artefato, novo nome/destino |
| Restore isolado | backup sintético íntegro; destino inexistente e fora da pasta ativa | restore em arquivo novo; integrity/checker; comparar estado | caminhos absolutos, hash, integrity_check/FK/checker, contagens/fingerprints iguais no escopo aplicável | jamais restaurar sobre banco ativo; qualquer divergência: parar e conservar ambos |
| Recovery offline | ticket/cópia preparada de modo sintético; servidor parado | seguir procedimento offline documentado; aplicar somente ao alvo descartável; retomar serviço conforme instruções | evidência de pre-backup, servidor parado, resultado de apply, checker/health, reconciliação | servidor ativo, destino não comprovado, pré-backup ausente ou checker com finding: não aplicar; manter cópia e preservar evidência |
| Troubleshooting | erros controlados/sintéticos ou documentação e código | conferir runtime/uv, lock, startup, migrations, perfil/banco, porta/loopback, checksum/CEI/schema, recovery | cada diagnóstico mapeia mensagem real, comando existente, resultado e recovery não destrutivo | instrução destrutiva, comando ausente ou recuperação não comprovada: parada/finding |
| Versões | fonte version, pyproject, CEI exporter e UI; sem editar código por padrão | rastrear produto, pacote, produtor e formato em todas as superfícies | V1.0 / 1.0.0 / CEI-EXPORT-1.0 e format_version 1.0 sem mistura; registrar UI | S1 exige alteração identificadora ausente/incoerente: classificar e parar antes de código salvo decisão clara dentro de S7; conflito normativo -> Luna High |
| Links, paths, comandos e scripts | docs candidatas e fontes executáveis | checar anchors, paths relativos, targets; comparar argumentos de scripts/management commands; executar checagens proporcionais | relatório por referência válida/quebrada e comando documentado/testado | link crítico quebrado ou comando não reproduzível: finding; não marcar PASS |
| Browser matrix | adendo S4 e evidência S4 | comparar claims do README/notas com adendo e evidência | Brave como validado; demais estados exatamente não validados/opcionais/N/A | claim divergente: bloquear texto candidato e corrigir somente por reconciliação autorizada |
| CEI | docs, código e S6R1 | comparar produtores, manifesto, preflight, destino, exclusões e semântica | afirmações exatas do contrato; sem prometer merge/conversão/repair/partial | qualquer claim sem evidência ou conflito de contrato: parar |
| Suporte | README/notas e configuração real do projeto | conferir Issue habilitado antes de mencionar canal | suporte documental V1; Issues apenas para defeitos se habilitado; sem SLA/comercial/24x7/garantia de resposta | canal desabilitado ou indefinido: não prometer; registrar limite |
| Changelog/notas | histórico de release e fontes confirmadas | preservar história; produzir notas V1 curtas de candidato com fatos comprovados | Added/Changed/Fixed/Security/Compatibility/limitations só se convenção sustentar; release notes cobrem V1, plataforma, instalação, capacidades, upgrade, backup/recovery, CEI, browser, limites e docs | sem fonte/fato verificável: omitir; nunca reescrever FAIL histórico |

## Plataforma, suporte e limites a publicar

Windows 11 x64; uso individual local em loopback, sem hospedagem pública e sem multiusuário remoto. Toolchain documentada conforme código/gate vigente (`uv`, runtime gerenciado pelo fluxo atual, ambiente reproduzível, `scripts/start-local.ps1`). Não prometer instalação nativa. Suporte oficial V1 documental; sem SLA, suporte comercial, 24/7, prazo garantido ou atendimento individual obrigatório. GitHub Issues somente se habilitado.

Upgrade comprovado a documentar: `V0.4.4 representativa → V0.5 → V1`; não inventar downgrade automático. Distinguir atualizar código, dependências, migrations declaradas, recovery offline, restore isolado e rollback operacional; evitar “rollback” sem qualificação.

Backup: quando necessário, parada/pré-operação, validação, arquivo e sidecar juntos, local protegido e verificação. Restore: destino novo isolado, nunca banco ativo, verificação/reconciliação. Recovery: procedimento offline, retorno controlado, checker/integridade. CEI funcional continua separado de backup SQLite.

## Arquivos canônicos planejados

- Contrato autorizado nesta tarefa: `tasks/current.md`.
- Este A4: `tasks/plans/v10-s7-operational-documentation-plan.md`.
- Inventário: `tasks/plans/v10-s7-document-inventory.md`.
- Reconciliar: `README.md`, `docs/README.md`, `docs/CEI_EXPORT_1_0.md` e `docs/V0.4_S7_Operacao_Windows.md`; preservar documentos congelados/históricos.
- Release notes candidata: `docs/RELEASE_NOTES_V1.0.md`.
- Decisão pós-auditoria: criar `docs/V1.0_Operacao_Local.md` como guia operacional canônico V1 e marcar os guias V0.4/V0.5 como históricos. O guia Windows V0.4 mantém nomenclatura e contexto da versão anterior, enquanto a documentação V0.5 descreve outro fluxo de restore; links isolados não resolveriam a ambiguidade de versão/procedimento.
- Resultado e evidência de execução: `quality/v10-s7-operational-documentation-result.md`, anexos de evidência CT-127 sob convenção `quality/v10-s7-ct127-*` sem banco pessoal; A8 standard sob `quality/v10-s7-a8-standard.json` ou formato atual equivalente.
- Nenhum changelog novo até confirmar se o repositório possui convenção em arquivos ignorados/não Markdown.

## Gate, revisão e critérios de saída

1. Somente documentação alterada: links/anchors, revisão de comandos contra scripts/fontes, checagem documental do gate e smoke proporcional às instruções documentadas; não executar suíte integral pesada por reflexo, salvo política do repositório.
2. Se código funcional, configuração, dependência ou schema mudar: parar e solicitar decisão humana quando fora do escopo; caso mudança identificadora autorizada ficar dentro do escopo, executar gate integral `scripts/quality.ps1` e nenhuma migration nova.
3. A8 standard independente cobre documentação, instalação, update, backup, restore, recovery, browsers, suporte, versões, CEI, changelog/notas, limites, links, comandos e escopo.
4. Conclusão futura exige provas requeridas concluídas sem finding aberto aplicável, claims mapeados a evidência, documentação reproduzível, A8 standard aprovado e relatório com gate observado. A promoção permanece fora desta etapa.

**Parar imediatamente** em instrução não reproduzível, comando inexistente, procedimento destrutivo inseguro, restore ativo, versão contraditória, claim de browser falso, suporte indefinido, link crítico quebrado, conhecimento implícito, necessidade de migration ou conflito normativo material. Conflito normativo real escala para `GPT-6 Luna High`. Não converter resultado inconclusivo em PASS.

## Closure — 2026-10-03

Status: COMPLETED. S7-F01 and S7-F02 resolved. Final A8 APPROVED WITH NOTES (0 Blocker / 0 Major / 2 Minor). Update proof: quality/v10-s7r2-update-proof.json; execution report: quality/v10-s7r2-execution-report.md. S8-S10 remain unauthorized.
