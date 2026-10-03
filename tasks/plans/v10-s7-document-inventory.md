# V1.0-S7 — Inventário documental (auditoria inicial)

Baseline lida: `ac13fb2c5023fbb1c6ccc69ab4059d0367f899ea`. Inventário read-only anterior a qualquer edição documental. “V1 atual?” indica alinhamento com o candidato V1, não promoção.

| Documento / superfície | Estado observado | V1 atual? | Conflito ou lacuna | Ação prevista |
|---|---|---:|---|---|
| `README.md` | Guia extenso: instalação, execução, backup, troubleshooting; status inicial ainda V0.5 beta e instalação identificada como suportada/validada | Parcial | Status V0.5 contrasta com estado S6 concluído/S7 autorizado; sem release notes de V1 e alegação CT-127 de instalação atual precisa revalidar | UPDATE |
| `docs/V0.4_S7_Operacao_Windows.md` | Guia operacional Windows com `uv`, scripts, update, troubleshooting e limites | Parcial | Guia corretamente preserva contexto legado V0.4, mas contém orientações genéricas de Git/pull e referência ao fluxo V0.5 | RECONCILE; manter histórico |
| `docs/V0.5_S7_Portabilidade_e_Restore.md` | Procedimento de CEI e adoção offline V0.5 | Parcial | Fonte beta/histórica; revisar compatibilidade com aplicação V1 sem reescrever fatos V0.5 | RECONCILE |
| `docs/V0.4_S6_Backup_e_Recuperacao.md` | Contrato técnico legado de backup/recovery | Parcial | Fonte histórica; reusar conceitos provados, marcar caminho operacional atual | KEEP; referência cruzada se aplicável |
| `docs/CEI_EXPORT_1_0.md` | Contrato de formato/manifesta; diz `application_version` fixa `V0.5` | Não | S1 e código estabelecem producer V0.5/V1.0; formato `CEI-EXPORT-1.0`/`format_version=1.0` continua | RECONCILE |
| `docs/V1.0_S1_Contratos_e_Compatibilidade.md` | Contrato congelado de versão, compatibilidade, browsers e canal | Sim | Normativo histórico; browser adendo S4 mais recente substitui a matriz inicial | KEEP; preservar congelamento |
| `docs/V1.0_Adendo_V10-D2_Matriz_de_Browsers_S4.md` | Matriz final vigente, Brave oficial validado e demais estados explícitos | Sim | Nenhum; é a fonte atual de browsers | KEEP; README aponta aqui |
| `docs/RELEASE_NOTES_V0.1.md` | Notas históricas V0.1 | Não se aplica | Sem notas V1; não apagar a história | KEEP; criar candidato V1 separado |
| Changelog na raiz ou `docs/` | Não localizado no inventário Markdown | Não | Convenção de changelog V1 não existe/confirmar busca integral antes de criar | HUMAN_DECISION_REQUIRED se nova convenção for necessária; caso contrário registrar fatos V1 em notas de release |
| Notas de release V1 | Não localizadas | Não | Artefato candidato ausente | Criar `docs/RELEASE_NOTES_V1.0.md` como release candidate |
| Guia de instalação V1 autônomo | Não localizado; `README.md` cobre os passos | Parcial | Evitar duplicar; promover README como guia canônico e validar CT-127 | UPDATE README; não criar duplicata |
| Guia de uso V1 autônomo | Não localizado | Parcial | README cobre primeiro acesso/operação mínima; validar lacunas funcionais com uso existente | RECONCILE no README; criar só se comprovada necessidade |
| Guia de atualização autônomo | Não localizado; seção existente em `docs/V0.4_S7_Operacao_Windows.md` | Parcial | Passos Git são genéricos e não estabelecem backup/restauração completos na versão atual | RECONCILE no guia operacional canônico |
| Guia de backup/restore/recovery autônomo V1 | README, V0.4-S6 e V0.5-S7 contêm partes | Parcial | Procedimentos dispersos; isolação/offline e checker devem ser consolidados | RECONCILE; preferir guia V1 único se documentação provar necessidade |
| Troubleshooting | Seções em README e guia Windows | Parcial | Verificar comandos/erros atuais, porta, runtime, migrações, banco, CEI e recovery | RECONCILE |
| Suporte | Não há guia V1 autônomo identificado | Não | Fronteira documental ausente/confirmar Issue habilitado antes de afirmar canal | Criar seção curta no README/notas; issues apenas se habilitado |
| `tasks/completed/v10-s4-accessibility-browser-usability.md` | Registro de execução amplo; inclui estados finais do browser | Sim, evidência | Evidência técnica, não guia de usuário | KEEP; não duplicar relato integral |
| `quality/v10-s4-accessibility-browser-usability-result.md` | Evidência de browser/acessibilidade | Sim, evidência | Fonte de comprovação | KEEP; referenciar adendo |
| `quality/v10-s6-upgrade-recovery-result.md` e `quality/v10-s6r1-result.md` | Evidência de upgrade/recovery, CEI e revalidação S6R1 | Sim, evidência | Devem sustentar apenas claims cobertos por cada prova | KEEP; mapear claims |
| `docs/operations/temporary-test-evidence.md` | Política interna de evidência temporária | Não é doc de usuário | Interna/auditoria; não expor como guia principal | KEEP; uso interno no plano |
| `docs/README.md` | Índice documental existente | Parcial | Deve apontar novos documentos sem classificar evidência como instrução de usuário | UPDATE |
| Roadmap legado `docs/Caderno_de_Erros_Inteligente_Etapa_9_Roadmap (1).md` | Planejamento histórico com estimativas, riscos e promessas de fases | Não | Usar apenas como histórico; não importar compromissos superados para release notes | KEEP; remover referência do caminho operacional se houver |
| Scripts referenciados | `scripts/start-local.ps1`, `start-local.cmd`, `quality.ps1`, verificadores recovery; management commands existentes para migrate/bootstrap/backup/restore/checker/import | Parcial | Validar todos os nomes/opções/paths contra fonte executável na prova A4 | RECONCILE; não renomear scripts |
| Versão UI/manifesta | `PRODUCT_VERSION="V1.0"`, pacote `1.0.0`, producer CEI usa `PRODUCT_VERSION`; testes cobrem V1.0 | Sim no código | README/contrato CEI documentalmente defasados; S1 exige produto e package distintos | RECONCILE docs; sem código previsto |

## Resultado da classificação

- Preservar os documentos históricos e falhas/evidências anteriores sem reescrita retroativa.
- Candidato documental central: README atualizado, guia operacional consolidado conforme convenção existente, índice `docs/README.md`, matriz browser referenciada e `docs/RELEASE_NOTES_V1.0.md`.
- Nenhum changelog foi identificado; a execução funcional deverá confirmar se há changelog fora de Markdown/ignorado antes de propor um novo formato.
- A auditoria de links/comandos e as provas CT-127, update, backup, restore e recovery permanecem pendentes para a execução S7 posterior.

## Execution reconciliation — 2026-10-03

The documented update flow and final V1.0 operational guide were exercised in an isolated synthetic V0.5.0-to-V1.0 candidate update. S7-F02 is resolved; final A8 approved with two nonblocking Minor notes. Inventory deliverables and link/command references were reconciled; see quality/v10-s7r2-execution-report.md. Historical pending classification above describes the pre-execution planning checkpoint.
