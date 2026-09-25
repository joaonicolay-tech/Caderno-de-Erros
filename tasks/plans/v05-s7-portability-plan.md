# V0.5-S7 — A4 de portabilidade e recuperação

- Tarefa: `V0.5-S7`, autorizada em `tasks/current.md`.
- Estado do plano: `CLOSED` em 2026-09-25; auditoria e decisões de S7 registradas antes da primeira edição funcional.
- Baseline observada em 2026-09-25: branch `main`; `HEAD` e `origin/main` = `461e2bd1f1abe7321726d30e7e5e47737faa6be2`; somente `tasks/current.md` modificado; `git diff --check` sem erro.
- Modelo/reasoning solicitados: GPT-6 Sol / High; duração e quota não observáveis: `unknown`.

## Fontes e estado executável

O contrato e `AGENTS.md` exigem este A4 antes da primeira edição funcional. Foram auditados o plano V0.5-P0, `PROJECT_STATE.md`, o contrato S1, os requisitos RF-069–071/RNF-034–043, CT-113–120, Modelo de Dados §16 e decisões, SDD §21, FL-022, ADR-007, o guia V0.4-S6 e o código de `modules.data_management`. Os artefatos S2A–S2D e S5/S6, modelos atuais e padrões da UI foram consultados para identificar fatos novos e riscos de recuperação. RF-072 não existe na lista aprovada de RF-001–071; a referência condicional do pedido não autoriza criá-lo.

O Modelo de Dados §16.1 propõe `cei-export-AAAA-MM-DD.zip` com JSON UTF-8, README, UUIDs/códigos preservados, instantes UTC, contagens/tamanhos/SHA-256 e snapshots opcionais. `MD-DEC-015` congela o **identificador** `CEI-EXPORT-1.0`, não o contrato integral de cada arquivo. O próprio §16 chama o pacote de proposta. SDD §21.3 o chama de recomendado, permite CSV auxiliar, e S1 registra `V05-OD05 = DEFERRED_TO_S7`; o plano P0 registra schema/manifesto/importabilidade ainda abertos. Tratar a lista como schema final seria uma decisão normativa nova.

`create_sqlite_backup` produz snapshot SQLite e sidecar `CEI-SQLITE-BACKUP` 1.0 (instante UTC, bytes, SHA-256). `validate_sqlite_backup` confere sidecar, tamanho, hash, `integrity_check` e FKs. `restore_sqlite_backup` confere migrations/fundação, contagens e S5 em cópia isolada, publica somente destino **novo**, e não troca o banco ativo (`src/modules/data_management/services.py`; ADR-007; guia V0.4-S6). A recuperação existente não é uma implementação de restore pela UI. O checksum físico detecta alteração acidental, não autentica proveniência. Os testes `test_backup_restore.py` e `test_backup_recovery.py` cobrem a base técnica. Nenhuma implementação de CEI-EXPORT-1.0 existe.

## Auditoria dos 23 pontos obrigatórios

| Ponto | Evidência e estado para S7 |
| --- | --- |
| 1–2. Formato/schema | ZIP + JSON é proposta do Modelo §16.1; o schema final por entidade, cardinalidade, null e nomes de campos não está fechado. `tags.json` foi proposto, mas não há model Tag atual. |
| 3–5. Manifesto/checksums/versionamento | Identificador 1.0, data, contagens, tamanhos e SHA-256 têm respaldo geral; lista exata de chaves, checksum do próprio manifesto, ordenação/canonicalização e política de versões futuras não estão especificadas. Rejeição de versão desconhecida é obrigatória. |
| 6–8. Relações/IDs/Workspace | UUIDs preservados constam do Modelo §16.1. Não há contrato para destino vazio com UUID canônico diferente, remapeamento permitido, conflito, owner nem identidade de Workspace entre máquinas. Todos os vínculos devem ser validados no mesmo Workspace; nunca misturar espaços. |
| 9–11. Fatos/derivados/importabilidade | O pacote proposto nomeia Questões, revisões, Attempts, erros, ciclos, Reviews, agenda, mastery e auditoria, mas não cobre explicitamente `ErrorClassificationRevision`, `QuestionOrigin` nem `SavedFilter` agora persistidos. `MasteryStateEvent` é fato append-only; score Domain/Priority atual é cálculo, sem snapshot. `OperationReceipt` é técnico e omitido por padrão no Modelo. Importação mínima para destino vazio e reexportação não foi contratada. |
| 12–13. Backup/restore | Mecanismo físico existe e é verificado isoladamente; não há troca ativa, upload UI, pré-backup automático, nem semântica de adoção do banco restaurado. |
| 14–17. Staging/pré-backup/retorno/integridade | FL-022 e RF-070 exigem validar antes de mutar, mostrar impacto, pré-backup e retorno. A implementação atual só publica cópia nova. A8 deve avaliar contenção de escrita/conexões, falha durante troca e prova de estado sem mistura. S5 permanece read-only. |
| 18. Segurança de arquivo | Validar nomes ZIP, traversal, separadores Windows, duplicatas, symlinks e expansão somente se ZIP for confirmado. Upload de backup físico requer staging sob nome interno, ignorando filename enviado. Arquivo não confiável nunca define path final. |
| 19–20. UI/acessibilidade | Há padrões de formulário POST/CSRF, confirmação, cancelamento, foco e mensagens em `questions`, `accounts` e templates; não existe UI de data management. Confirmar impacto, rótulos, erro e resultado verificável sem depender de cor; GET sem mutação. |
| 21. Testes | CT-113–116 têm base técnica existente; CT-117–120 exigem casos novos de falha/retorno, leitor independente, round-trip semântico e versão incompatível. Cobrir Workspace, Unicode, histórico, segredos, arquivos hostis e cleanup após contrato final. |
| 22. Migration | Auditoria de models/migrations não revela necessidade intrínseca de nova tabela para exportação ou staging efêmero. **Provisório: `Migration: NO`**, sujeito apenas a decisão humana que imponha persistência necessária; nenhuma migration criada. |
| 23. OD05 | `OPEN / BLOCKED_HUMAN_DECISION`. Os blocos abaixo exigem decisão antes de código funcional dependente. |

## Classificação de dados e reconciliação

Fatos funcionais observados nos models atuais: `Workspace` e preferências funcionais; `TaxonomyItem`; `OriginCatalogItem`, `QuestionOrigin`, `Question`, `QuestionRevision`, `Alternative`; `Attempt` com `status`, `replaces_attempt`, anulação e versão usada; `ErrorCategory`, `ErrorClassification` e `ErrorClassificationRevision`; `ReviewCycle`, `Review`, `ReviewScheduleChange`; `MasteryStateEvent`; `AuditEvent` sanitizado; `SavedFilter`. O contrato deve decidir campos e dependências de cada um, inclusive metadados do owner e regras/versões. O modelo S1 exige que VOIDED continue histórico, correção de gabarito não reinterprete Attempts, e auditoria de exclusão não recrie Question eliminada.

Projeções e derivados: métricas, fila, estado/score Domain e ranking Priority são cálculos da política vigente; não há snapshot S5/S6 que demande exportação. Busca e caches são reconstruíveis. `OperationReceipt` é recibo técnico de idempotência, não substitui `AuditEvent`; o Modelo o omite por padrão, mas seu impacto na retomada após importação requer decisão. Dados de autenticação, `SECRET_KEY`, tokens, senhas, variáveis de ambiente, caminhos e logs técnicos não entram no export funcional. Backup físico contém banco completo, inclusive conteúdo privado, e segue proteção operacional RNF-037.

Reconciliação a provar após decisão: totais por tipo e Workspace, integridade de referências, cadeia de substituição/VOIDED, versões e conteúdo histórico de questões, classificações e revisões, agenda/ciclos, mastery events, auditoria sanitizada e equivalência de fatos autoritativos após reexportação. Timestamp de geração pode diferir. O leitor independente deve usar apenas formato documentado e bytes do artefato, sem ORM/SQLite.

## Fronteiras de arquivo e falha a projetar após OD05

O upload deve copiar em blocos para temporário privado, com nome gerado internamente; o nome fornecido pelo cliente é metadado não confiável. O ZIP proposto exigirá validação de entradas e rejeição de paths absolutos, `..`, separadores Windows, nomes reservados, duplicatas, links e conteúdo inesperado antes de extração ou leitura. Parser/validator read-only ficará separado de qualquer mutator. Evitar `read()` integral de artefatos potencialmente grandes; medir dataset sintético antes de impor qualquer limite de tamanho/tempo. Não há budget numérico aprovado. Temporários devem ser limpos em sucesso, recusa, cancelamento e exceção; relatório técnico sanitizado deve distinguir cleanup falho sem expor path privado. Não criar política nova de retenção para staging/export; backups seguem RNF-037 e guia V0.4-S6.

| Fronteira | Estado exigido para CT-117 e FL-022 |
| --- | --- |
| Upload ou parse falha | Destino intacto; staging removido; original do usuário não é modificado. |
| Formato, versão, checksum, referências ou Workspace recusados | Destino intacto; mensagem segura da fase; nenhum pré-backup/restore substitui validação. |
| Confirmação cancelada ou preview obsoleto | Nenhuma mutação; temporário e token de confirmação invalidados/limpos. |
| Pré-backup falha ou não é restaurável | Restore principal não começa; destino intacto. |
| Preparação isolada falha | Destino intacto; cópia candidata removida; pré-backup preservado. |
| Falha durante adoção controlada | Sem mistura parcial; aplicação retorna ao banco anterior ou ao pré-backup validado conforme procedimento aprovado. A técnica exata de parada/troca/retorno permanece dependente da decisão 4. |
| Pós-validação/reconciliação falha | Não declarar sucesso; preservar pré-backup e evidência sanitizada; executar retorno aprovado antes de reabrir escrita. |

Uma transação ORM não resolve sozinha troca do arquivo SQLite ativo. `os.replace` com conexões abertas no Windows não constitui estratégia aprovada. A decisão de adoção deve fechar esta fronteira antes de implementar a UI de restore.

## Decisões humanas necessárias — V05-OD05

1. **Contrato funcional:** aprovar ZIP com JSON UTF-8 como base normativa de `CEI-EXPORT-1.0` e autorizar um schema explícito que inclua os fatos atuais, ou escolher outro formato. A proposta do Modelo cobre arquivos principais, mas suas omissões e o S1 `DEFERRED_TO_S7` impedem congelar unilateralmente campos, relações e manifesto. Opções: (A) ZIP/JSON com schema completo e README, mantendo apenas arquivos necessários; (B) JSON único; (C) CSVs com manifesto. A facilita streaming por arquivo, leitura independente e evolução por entidade, mas exige defesa contra ZIP hostil. B simplifica transporte/validação de paths, mas pode exigir processamento integral e dificultar streaming. C facilita planilhas, mas relações, null, Unicode e histórico complexo tornam round-trip mais frágil. **Recomendação técnica:** A, como evolução da proposta aprovada no Modelo, após aprovação explícita da lista/campos e sem CSV extra por conveniência.
2. **Manifesto e escopo:** aprovar chaves obrigatórias (`format`, `format_version`, `generated_at`, entradas/contagens/tamanhos/SHA-256 e versões de política necessárias), definição de checksums por entrada, representação de relações/ausências, ordenação e tratamento de versões desconhecidas. A fonte exige esses conceitos, mas não fixa um schema verificável. Sem isso, CT-118–120 podem aceitar interpretações incompatíveis. **Recomendação técnica:** manifesto pequeno, fechado, com SHA-256 de cada JSON de dados, versão exata 1.0 e rejeição de versão desconhecida antes de mutação; sem hash autorreferente.
3. **Identidade e round-trip:** decidir se o importador mínimo aceita apenas destino vazio com o mesmo Workspace/owner/UUIDs, se remapeia IDs para um Workspace vazio distinto, ou se exige um ambiente novo com identidades canônicas preservadas. Preservar IDs mantém referências e auditoria simples, mas pode conflitar com o Workspace canônico existente; remapear permite transferência, mas muda referências e dificulta auditoria; validar apenas evita risco de mistura, mas restringe portabilidade. O contrato deve fixar conflitos, dados de owner e pertencimento. **Recomendação técnica:** instalação vazia compatível com preservação/validação estrita dos UUIDs, sem merge, se isso satisfizer a portabilidade desejada.
4. **Fronteira de restore pela UI:** confirmar que a UI recebe o par operacional SQLite+manifesto, faz staging e restore isolado, exige confirmação/pré-backup e só então adota o estado completo da instalação, com parada coordenada e retorno; ou definir outra semântica explícita. O serviço atual proíbe overwrite, enquanto FL-022 descreve importação lógica e substituição de um espaço. A escolha altera isolamento, downtime, risco de perda, testes CT-117 e relação com o importador CEI-EXPORT. **Recomendação técnica:** manter backup físico separado do importador CEI, validar cópia isolada e planejar adoção controlada com pré-backup e rollback observáveis; não usar upload→replace direto.
5. **Dados de S2–S6 no formato:** decidir inclusão/representação de `ErrorClassificationRevision`, `QuestionOrigin`, `SavedFilter`, `MasteryStateEvent`, `AuditEvent` sanitizado e eventual `OperationReceipt`, além do tratamento de `tags.json` sem model atual. Excluir fatos necessários pode perder história; incluir dados técnicos/segredos amplia superfície. **Recomendação técnica:** incluir fatos funcionais e históricos efetivamente persistidos, omitir Tag inexistente, caches/snapshots e recibos técnicos se sua ausência não comprometer a retomada; documentar explicitamente cada exclusão.

Essas decisões afetam leitura independente, round-trip, compatibilidade, segurança e risco de perda de dados. A recomendação técnica não é aprovação normativa. Registrar respostas como adendo datado, sem atribuí-las retroativamente às fontes.

## Sequência condicionada à decisão

Após decisões aprovadas: fechar schema/manifesto e lista de fatos; confirmar `Migration: NO` ou justificar schema antes de migration; implementar serializer/validator e leitor independente; importação mínima em destino vazio autorizado; UI de download/export/backup; staging e restore operacional com preview, confirmação, pré-backup, retorno e relatório; testar CT-117–120 e regressões; A8 deep (Blocker 0/Major 0); gate `quality.ps1` com exit 0 observado; evidence em `quality/`; encerrar por `finish-task`. Não executar S8+ nem commit/push/tag/release.

O bloqueio acima documenta o estado até a decisão humana de S7. O adendo a seguir o encerra; este A4 não declara S7 concluída.

## Adendo de decisão humana — 2026-09-25

Fonte: pedido do usuário «DECISÕES HUMANAS — V0.5-S7 / V05-OD05», recebido depois da auditoria acima. **Esta é uma decisão nova de S7**, não uma atribuição retroativa ao Modelo de Dados, SDD ou S1. `V05-OD05 = RESOLVED`; a implementação de S7 está autorizada por `tasks/current.md` e por este adendo. `Migration: NO` fica aprovado se o schema atual bastar; necessidade inevitável de nova persistência exige nova parada antes de migration.

| Assunto | Contrato aprovado |
| --- | --- |
| Contêiner e dados | Um ZIP `CEI-EXPORT` versão exata `1.0`, com múltiplos JSON UTF-8 e `README.txt`. Sem SQLite, CSV ou JSON monolítico como formato funcional. |
| Schema | Documento canônico `docs/CEI_EXPORT_1_0.md` com arquivos, campos, tipos, nullability, relações, enums, omissões e compatibilidade. Validators automatizados bastam; JSON Schema formal não é obrigatório. |
| Tempo e ausências | Datas `YYYY-MM-DD`, instantes ISO 8601 UTC, timezone funcional/histórico separado, ausência JSON `null`. |
| Manifesto | `manifest.json` com identificador, versão, `generated_at`, versão de aplicação/schema, UUID/zone do Workspace, entradas, contagens, tamanho e SHA-256 por payload, policies necessárias. Sem hash autorreferente nem checksum do ZIP no ZIP. |
| Identidade | UUIDs funcionais e códigos preservados. Importação CEI apenas para destino funcional vazio compatível, rejeitando conflito, sem merge/remapeamento. Credenciais excluídas; Workspace e `SavedFilter.owner_user` podem se vincular ao usuário local autorizado sem mudar UUID funcional. |
| Fatos | Exportar os models funcionais/históricos atuais necessários: hierarquia, catálogo/origens, Questions/revisões/alternativas, Attempts inclusive void/replacement, categorias/diagnóstico/revisões, ciclos/Reviews/reagendamentos, SavedFilters, MasteryStateEvents e AuditEvents sanitizados. Não criar Tag inexistente. |
| Derivados e exclusões | Métricas, Domain/Priority atuais, cache, busca, snapshots não autoritativos, `OperationReceipt`, logs, sessão, credenciais e segredos são excluídos. Preservar versões de policy e fatos para recálculo; auditoria de exclusão não revive conteúdo apagado. |
| Backup e restore | Backup físico SQLite permanece separado. Restore pela UI: staging, validação estrutural/versão/hash/isolada, impacto, confirmação reforçada, pré-backup validado, adoção controlada, reconciliação, relatório. Não sobrescrever SQLite aberto; fechamento de conexões/reinício explícitos quando necessários. |
| Round-trip | Exportar, importar em destino vazio compatível, recalcular derivados e reexportar; comparar semanticamente fatos, UUIDs, relações e histórico, permitindo `generated_at` diferente. Versão desconhecida é rejeitada antes de mutação. |

### Técnica de implementação fechada no A4

- O conjunto de arquivos JSON deriva dos **models concretos atuais**; uma lista explícita de campos funcionalmente necessários será congelada no documento do formato antes da primeira emissão. `QuestionOrigin` e `ErrorClassificationRevision` são arquivos próprios; `tags.json` inexiste.
- Datas e decimais serão convertidos explicitamente, sem serialização indiscriminada do ORM; relacionamentos são UUIDs. Ordenação por UUID torna conteúdo estável; `generated_at` permanece variável. SHA-256 incide sobre os bytes UTF-8 de cada JSON armazenado. Manifesto declara uma lista fechada; membros ZIP inesperados, duplicados ou com path são recusados.
- Export lê somente o Workspace autorizado. Import/validator são separados: arquivo não confiável passa por staging privado e validação de formato, hash, estrutura, referências e escopo antes de transação de escrita em destino vazio. Nenhum password/hash ou conta é importado.
- Restore operacional reutiliza `create_sqlite_backup`, `validate_sqlite_backup` e `restore_sqlite_backup` no estágio isolado. A adoção do banco ativo deve ser coordenada fora de conexões abertas, com pré-backup verificado, publicação atômica suportada no Windows e retorno comprovável. A UI não executará cópia sobre SQLite aberto.
- Testes específicos: CT-117–120, reader independente, round-trip de histórico S2B/S2C/S2D/S5, corrupção/path/versão, ausência de segredos, cancelamento/cleanup, UI POST/CSRF/acessibilidade e recuperação em cópia isolada. Após revisão A8 deep e gate final exit 0, registrar evidence e só então encerrar.
