# CEI-EXPORT-1.0 — contrato funcional de portabilidade

Decisão humana de V0.5-S7 registrada em `tasks/plans/v05-s7-portability-plan.md`. Este formato é um ZIP com JSON UTF-8; não é o backup SQLite operacional. Um leitor comum de ZIP e JSON basta para interpretá-lo. A importação S7 exige instalação compatível com destino funcional vazio e preserva UUIDs, sem merge.

## Contêiner e manifesto

O nome sugerido é `cei-export-AAAA-MM-DD.zip`. A raiz contém exatamente `manifest.json`, `README.txt` e os JSON da tabela abaixo. Não há diretórios nem membros extras. Todos os JSON usam UTF-8 sem BOM; cada conjunto é um array de objetos, inclusive quando vazio. Registros são ordenados pelo UUID `id`. Chaves dos objetos têm ordem lexicográfica na emissão; a ordem das chaves não é semântica. Referências são UUIDs em texto canônico com hífens. A ausência é `null`; não se omitem campos definidos. Datas civis usam `YYYY-MM-DD`; instantes, ISO 8601 com offset UTC. Decimais são strings para preservar precisão. Booleanos são booleanos JSON. Inteiros são inteiros JSON.

`manifest.json` é um objeto com os campos obrigatórios:

| Campo | Tipo e significado |
| --- | --- |
| `format` | string fixa `CEI-EXPORT` |
| `format_version` | string fixa `1.0` |
| `generated_at` | instante UTC de geração |
| `application_version` | string fixa `V0.5` |
| `schema_migrations` | array ordenado de nomes `app.migration` requeridos; compatibilidade estrita |
| `workspace_id` | UUID do Workspace exportado |
| `workspace_timezone` | fuso IANA atual do Workspace |
| `policies` | objeto com `review`, `domain`, `priority`; nesta versão `REV-FIXA-1.0`, `DOM-HEUR-1.0`, `PRI-HEUR-1.0` |
| `files` | array com uma entrada para cada JSON e `README.txt`, sem duplicatas |

Cada entrada `files` contém exatamente `name` (nome simples), `count` (número de objetos no JSON; zero para README), `size_bytes` (bytes descomprimidos) e `sha256` (64 dígitos hexadecimais minúsculos sobre os bytes descomprimidos). O manifesto não contém checksum de si ou do ZIP. SHA-256 detecta alteração, mas não autentica o autor. Versão/formato/migrations/policies desconhecidos são recusados antes de escrita. Não há conversão silenciosa.

## Arquivos e campos

Cada linha é um arquivo `<conjunto>.json`. O tipo de cada campo é o do modelo funcional correspondente, salvo as convenções acima; campos terminados em `_at` são instantes, `_date`/`evaluated_on` são datas, `domain_index`/`confidence` são decimais. Os campos que apontam a outras entidades usam o **nome de relação sem `_id`** e contêm UUID ou `null`. `id`, `workspace` e referências permanecem estáveis. A nullability segue o schema compatível da aplicação; o validator a confere. Campos não listados são proibidos.

| Conjunto | Campos, além de `id` |
| --- | --- |
| `workspace` | `name timezone_name locale lock_version created_at updated_at` |
| `disciplines` | `workspace name name_key status sort_order archived_at lock_version created_at updated_at` |
| `subjects` | `workspace discipline name name_key status sort_order archived_at lock_version created_at updated_at` |
| `subsubjects` | `workspace subject name name_key status sort_order archived_at lock_version created_at updated_at` |
| `boards` | `workspace name name_key status archived_at lock_version created_at updated_at website_url` |
| `exams` | `workspace board name name_key status archived_at lock_version created_at updated_at year` |
| `sources` | `workspace name name_key status archived_at lock_version created_at updated_at source_type locator_url notes` |
| `questions` | `workspace discipline subject subsubject question_type status difficulty draft_title activated_at archived_at lock_version created_at updated_at` |
| `question_revisions` | `workspace question version_number is_current stem explanation trap_note notes correct_alternative change_kind change_reason created_at` |
| `alternatives` | `workspace question_revision position label text text_key created_at` |
| `question_origins` | `workspace question source exam board reference_year reference_text lock_version created_at updated_at` |
| `attempts` | `workspace question question_revision review attempt_type selected_alternative is_correct perceived_ease occurred_at timezone_name local_date status replaces_attempt voided_at void_reason idempotency_key created_at` |
| `error_categories` | `workspace code display_name name_key description category_kind state merged_into lock_version created_at updated_at` |
| `error_classifications` | `workspace attempt category other_description lock_version created_at updated_at` |
| `error_classification_revisions` | `workspace error_classification revision_number category other_description change_reason created_at` |
| `review_cycles` | `workspace question origin_attempt origin_question_revision origin_kind manual_purpose policy_code state started_at completed_at suspended_at superseded_at suspension_reason lock_version created_at updated_at` |
| `reviews` | `workspace review_cycle question sequence_number stage_code state first_due_date current_due_date scheduled_from_attempt transition_code policy_code completed_at suspended_at lock_version created_at updated_at` |
| `review_schedule_changes` | `workspace review previous_due_date new_due_date timezone_name reason_code correlation_id created_at` |
| `saved_filters` | `workspace name name_key context_code schema_version payload created_at updated_at` |
| `mastery_events` | `workspace question sequence event_type formula_code evaluated_on domain_index confidence trigger_attempt manual_cycle reason_code occurred_at` |
| `audit_events` | `workspace event_code entity_type entity_id previous_entity_id related_entity_id correlation_id reason_code previous_date new_date timezone_name created_at` |

Somente estes campos aceitam `null`; todos os demais são obrigatórios. String vazia é distinta de `null` quando permitida pelo modelo.

| Conjunto | Campos anuláveis |
| --- | --- |
| `workspace`, `review_schedule_changes`, `saved_filters` | nenhum |
| `disciplines`, `subjects`, `subsubjects` | `sort_order archived_at` |
| `boards` | `archived_at website_url` |
| `exams` | `board archived_at year` |
| `sources` | `archived_at locator_url notes` |
| `questions` | `discipline subject subsubject difficulty draft_title activated_at archived_at` |
| `question_revisions` | `stem explanation trap_note notes correct_alternative change_reason` |
| `alternatives` | `label` |
| `question_origins` | `source exam board reference_year reference_text` |
| `attempts` | `review perceived_ease replaces_attempt voided_at void_reason` |
| `error_categories` | `merged_into` |
| `error_classifications` | `other_description` |
| `error_classification_revisions` | `other_description change_reason` |
| `review_cycles` | `origin_attempt manual_purpose completed_at suspended_at superseded_at suspension_reason` |
| `reviews` | `scheduled_from_attempt completed_at suspended_at` |
| `mastery_events` | `domain_index confidence trigger_attempt manual_cycle reason_code` |
| `audit_events` | `entity_id previous_entity_id related_entity_id reason_code previous_date new_date timezone_name` |

Os campos com enum têm estes valores textuais; campos de policy e motivos codificados conservam os valores dos fatos, sem reinterpretá-los.

| Campo | Valores 1.0 |
| --- | --- |
| `workspace.locale` | `pt-BR` |
| `disciplines/subjects/subsubjects/boards/exams/sources.status` | `ACTIVE`, `ARCHIVED` |
| `sources.source_type` | `BOOK`, `PDF`, `WEBSITE`, `COURSE`, `QUESTION_BANK`, `OTHER` |
| `questions.question_type` | `OBJECTIVE_SINGLE` |
| `questions.status` | `DRAFT`, `ACTIVE`, `ARCHIVED` |
| `questions.difficulty`, `attempts.perceived_ease` | `EASY`, `MEDIUM`, `HARD` |
| `question_revisions.change_kind` | `INITIAL`, `ENRICHMENT`, `NON_CRITICAL_EDIT`, `CRITICAL_CORRECTION` |
| `attempts.attempt_type` | `INITIAL`, `REVIEW` |
| `attempts.status` | `VALID`, `VOIDED` |
| `error_categories.category_kind` | `STANDARD`, `PERSONAL` |
| `error_categories.state` | `ACTIVE`, `ARCHIVED`, `MERGED` |
| `review_cycles.origin_kind` | `INITIAL_ERROR`, `QUESTION_ACTIVATION`, `MANUAL`, `ATTEMPT_CORRECTION` |
| `review_cycles.manual_purpose` | `INCLUSION`, `MASTERY_REOPEN` |
| `review_cycles.state` | `ACTIVE`, `COMPLETED`, `SUSPENDED`, `SUPERSEDED` |
| `reviews.stage_code` | `D1`, `D7`, `D14`, `D30` |
| `reviews.state` | `PENDING`, `COMPLETED`, `SUSPENDED`, `CANCELLED` |
| `saved_filters.context_code` | `QUESTIONS_LIST` |
| `mastery_events.event_type` | `DOMINATED`, `AUTO_REOPENED`, `MANUAL_REOPENED` |
| `audit_events.event_code` | `REVIEW_RESCHEDULED`, `MANUAL_REVIEW_INCLUDED`, `PERSONAL_CATEGORY_RENAMED`, `PERSONAL_CATEGORY_ARCHIVED`, `PERSONAL_CATEGORY_MERGED`, `ATTEMPT_VOIDED`, `ATTEMPT_REPLACED`, `ANSWER_KEY_CORRECTED`, `QUESTION_PERMANENTLY_DELETED` |
| `audit_events.entity_type` | `REVIEW`, `REVIEW_CYCLE`, `ERROR_CATEGORY`, `ATTEMPT`, `QUESTION` |

`SavedFilter.payload` conserva a estrutura JSON fechada. Referências UUID são verificadas quanto à forma; referências antigas podem ficar obsoletas após exclusões e são apresentadas como incompatíveis pela UI, sem serem reinterpretadas na importação. `AuditEvent` já é sanitizado na origem; evento `QUESTION_PERMANENTLY_DELETED` não contém conteúdo apagado nem fornece dados para recriar Question. Eventos expurgados não aparecem. O export inclui `Attempt` VOIDED e sua cadeia `replaces_attempt`, preserva a revisão de Question usada e a história de reagendamento e classificação.

## Identidade, exclusões e ida e volta

O pacote contém somente um Workspace. `Workspace.owner_user` e `SavedFilter.owner_user` são associados ao usuário local autorizado na importação; senha, hash, sessão e token não são exportados. A importação preserva o UUID do Workspace e de todas as entidades funcionais. Se o destino já contém Workspace, rejeita antes da escrita. Relações ausentes, UUID duplicado, referência cross-Workspace, arquivo extra, path, checksum divergente e versão desconhecida são erros. Não há importação parcial, merge, remapeamento ou importação de terceiros.

`OperationReceipt`, caches, sessões, logs técnicos, índice de busca, arquivos temporários, variáveis de ambiente, credenciais, caminhos internos, snapshots e valores correntes derivados de Domain/Priority ficam fora. Não existe `tags.json`, pois não há Tag funcional na baseline. Métricas, fila, Domain e Priority podem ser recalculados a partir dos fatos e versões de política. Uma ida e volta compara registros e relações semanticamente; `generated_at` e bytes do ZIP podem mudar.
