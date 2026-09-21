"""Verificação read-only de invariantes operacionais do banco local SQLite."""

from __future__ import annotations

import re
import sqlite3
from collections import Counter
from contextlib import closing
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from pathlib import Path
from typing import Final

from django.db import connections

from modules.operations.structured_logging import REDACTED
from shared.domain.time import TimeZoneId

DEFAULT_FINDING_LIMIT: Final = 100
MAX_FINDING_LIMIT: Final = 1000
_UUID_PATTERN: Final = re.compile(
    r"(?:[0-9a-f]{32}|[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\Z",
    re.IGNORECASE,
)
_DATE_PATTERN: Final = re.compile(r"\d{4}-\d{2}-\d{2}\Z")
_SAFE_CODES: Final = frozenset(
    {
        "ACTIVE",
        "ATTEMPT_CORRECTION",
        "ATTEMPT_REPLACED",
        "ATTEMPT_VOIDED",
        "ANSWER_KEY_CORRECTED",
        "ARCHIVED",
        "ERROR_CATEGORY",
        "MANUAL",
        "MANUAL_INCLUSION_D1",
        "MERGED",
        "PERSONAL",
        "REVIEW_CYCLE",
        "REVIEW_RESCHEDULED",
        "MANUAL_REVIEW_INCLUDED",
        "PERSONAL_CATEGORY_RENAMED",
        "PERSONAL_CATEGORY_ARCHIVED",
        "PERSONAL_CATEGORY_MERGED",
        "STANDARD",
        "ATTEMPT",
        "ATTENTION",
        "CALCULATION",
        "COMPLETED",
        "CORRECTION_RETRY_VOIDED",
        "CORRECTION_PRESERVE_MANUAL",
        "CONCEPTUAL",
        "D1",
        "D7",
        "D14",
        "D30",
        "DRAFT",
        "ERROR",
        "FORMULA_RULE",
        "GUESS",
        "INITIAL",
        "INITIAL_CORRECT",
        "INITIAL_ERROR",
        "INITIAL_ERROR_TO_D1",
        "INTERPRETATION",
        "INVALID",
        "OTHER",
        "PENDING",
        "PROCEDURE",
        "QUESTION_ACTIVATION",
        "QUESTION_ACTIVATION_D1",
        "QUESTION",
        "REVIEW",
        "REVIEW_COMPLETION",
        "SUSPENDED",
        "SUPERSEDED",
        "TIME_SHORTAGE",
        "TRAP",
        "VALID",
        "VOIDED",
        "ADVANCE_D1_TO_D7",
        "ADVANCE_D7_TO_D14",
        "ADVANCE_D14_TO_D30",
        "RESET_TO_D1_AFTER_ERROR",
        "complete_current",
        "correct_alternative",
        "incomplete_current",
        "alternative_owner",
        "revision_owner",
        "accounts_user",
        "accounts_workspace",
        "attempts_attempt",
        "attempts_operationreceipt",
        "django_content_type",
        "errors_error_category",
        "errors_errorclassification",
        "errors_errorclassificationrevision",
        "operations_auditevent",
        "questions_alternative",
        "questions_board",
        "questions_exam",
        "questions_question",
        "questions_questionorigin",
        "questions_questionrevision",
        "questions_source",
        "reviews_review",
        "reviews_reviewcycle",
        "reviews_reviewschedulechange",
        "taxonomy_discipline",
        "taxonomy_subject",
        "taxonomy_subsubject",
    }
)


class IntegrityCheckOperationalError(RuntimeError):
    """Indique que o checker não conseguiu concluir, sem confundir com finding."""


class InvariantSeverity(StrEnum):
    """Severidades impeditivas mantidas intencionalmente pequenas."""

    CRITICAL = "CRITICAL"
    ERROR = "ERROR"


@dataclass(frozen=True, slots=True)
class InvariantSpec:
    """Entrada estável e auditável do catálogo de invariantes."""

    invariant_id: str
    name: str
    description: str
    domain: str
    expected_condition: str
    evidence_type: str
    severity: InvariantSeverity
    rationale: str
    impact: str
    detection_strategy: str
    false_positive_risk: str
    source_reference: str
    message: str
    operational_action: str


@dataclass(frozen=True, slots=True)
class IntegrityFinding:
    """Diagnóstico mínimo; nunca carrega conteúdo de estudo ou objeto inteiro."""

    invariant_id: str
    severity: InvariantSeverity
    entity_type: str
    technical_id: str
    message: str
    technical_context: tuple[tuple[str, str], ...]
    operational_action: str


@dataclass(frozen=True, slots=True)
class IntegrityCheckResult:
    """Resultado determinístico com contagem total independente do limite visual."""

    checks_executed: int
    total_findings: int
    findings: tuple[IntegrityFinding, ...]
    severity_counts: tuple[tuple[InvariantSeverity, int], ...]
    queries_executed: int

    @property
    def has_blocking_findings(self) -> bool:
        return self.total_findings > 0

    @property
    def truncated(self) -> bool:
        return self.total_findings > len(self.findings)


_SAFE_ACTION = (
    "Interrompa restore ou promoção, preserve um backup e investigue a entidade antes de "
    "qualquer correção manual autorizada."
)


INVARIANT_CATALOG: Final[tuple[InvariantSpec, ...]] = (
    InvariantSpec(
        "DB-001",
        "Estrutura SQLite íntegra",
        "O arquivo deve passar pelo diagnóstico interno do SQLite.",
        "database",
        "PRAGMA integrity_check retorna somente ok.",
        "PRAGMA read-only",
        InvariantSeverity.CRITICAL,
        "Corrupção física não é coberta pelos validators da aplicação.",
        "Leituras e restaurações podem produzir resultados não confiáveis.",
        "Executar integrity_check na conexão aberta em modo read-only.",
        "Baixo; o próprio SQLite produz a evidência.",
        "ADR-007 e modules.data_management.services._validate_sqlite_file",
        "O SQLite relatou corrupção estrutural.",
        _SAFE_ACTION,
    ),
    InvariantSpec(
        "DB-002",
        "Foreign keys válidas",
        "Toda foreign key persistida deve apontar para a linha esperada.",
        "database",
        "PRAGMA foreign_key_check não retorna linhas.",
        "PRAGMA read-only",
        InvariantSeverity.CRITICAL,
        "FKs podem ter sido importadas com enforcement desativado.",
        "Relações órfãs quebram todos os domínios dependentes.",
        "Executar foreign_key_check e reportar apenas tabela/rowid/parent.",
        "Baixo; depende do catálogo de FKs do schema aplicado.",
        "ADR-007 e migrations vigentes",
        "Existe uma referência de banco órfã.",
        _SAFE_ACTION,
    ),
    InvariantSpec(
        "WS-001",
        "Hierarquia taxonômica no mesmo Workspace",
        "Subject/Subsubject devem compartilhar Workspace com seus ancestrais.",
        "taxonomy",
        "Cada relação da hierarquia preserva Workspace e ancestral direto.",
        "SQL relacional",
        InvariantSeverity.CRITICAL,
        "A validação de model não é uma constraint intertabelas.",
        "Filtros e agregações podem vazar ou classificar dados incorretamente.",
        "Comparar em lote os Workspaces das relações reais.",
        "Baixo; arquivamento não altera pertencimento.",
        "taxonomy.models e CT-074",
        "A hierarquia taxonômica cruza Workspaces.",
        _SAFE_ACTION,
    ),
    InvariantSpec(
        "WS-002",
        "Catálogo de origem no mesmo Workspace",
        "Exam e QuestionOrigin devem compartilhar Workspace com suas referências.",
        "question origin",
        "Banca, questão e referências de origem preservam o Workspace do vínculo.",
        "SQL relacional",
        InvariantSeverity.CRITICAL,
        "As regras existem em save(), não como constraints compostas.",
        "Metadados podem ser atribuídos ao estudante errado.",
        "Comparar em lote cada referência opcional existente.",
        "Baixo; referências nulas são excluídas do teste.",
        "questions.models Exam/QuestionOrigin",
        "Uma referência de origem cruza Workspaces.",
        _SAFE_ACTION,
    ),
    InvariantSpec(
        "WS-003",
        "Timezone do Workspace válido",
        "O timezone persistido deve ser um identificador IANA aceito pelo domínio.",
        "workspace time",
        "TimeZoneId aceita timezone_name sem normalização persistente.",
        "Leitura em lote e helper temporal",
        InvariantSeverity.ERROR,
        "O validator de model não é uma constraint SQLite.",
        "Fila, dashboard e datas civis podem falhar ou usar referência incorreta.",
        "Validar uma projeção de ID/timezone com o mesmo value object do domínio.",
        "Baixo; usa a base IANA instalada que também atende a aplicação.",
        "accounts.models.Workspace e shared.domain.time.TimeZoneId",
        "O timezone do Workspace não é válido.",
        _SAFE_ACTION,
    ),
    InvariantSpec(
        "QUE-001",
        "Taxonomia da Question coerente",
        "A taxonomia da Question deve manter Workspace e encadeamento.",
        "question",
        "Discipline -> Subject -> Subsubject coincide com os vínculos da Question.",
        "SQL relacional",
        InvariantSeverity.CRITICAL,
        "Question._validate_taxonomy pode ser contornada por SQL/importação.",
        "Consulta e analytics podem agrupar a questão no universo errado.",
        "Comparar em uma consulta todos os níveis presentes.",
        "Baixo; taxonomia arquivada continua válida e não é sinalizada.",
        "questions.models.Question e V0.4-S1",
        "A taxonomia da questão é incompatível.",
        _SAFE_ACTION,
    ),
    InvariantSpec(
        "QUE-002",
        "Conteúdo versionado pertence à Question",
        "Revisões, alternativas e gabarito devem manter questão e Workspace.",
        "question versioning",
        "Todo snapshot e alternativa pertence à cadeia declarada.",
        "SQL relacional",
        InvariantSeverity.CRITICAL,
        "FK simples não expressa os vínculos compostos.",
        "Tentativas podem apontar para conteúdo ou gabarito de outra questão.",
        "Comparar relações de revisão, alternativa e gabarito em lote.",
        "Baixo; revisões históricas não precisam continuar atuais.",
        "questions.models.QuestionRevision/Alternative",
        "A cadeia de conteúdo versionado é incompatível.",
        _SAFE_ACTION,
    ),
    InvariantSpec(
        "QUE-003",
        "Sequência e revisão corrente coerentes",
        "Versões devem ser contíguas e questões utilizáveis ter revisão corrente completa.",
        "question versioning",
        "Versões começam em 1; ACTIVE/ARCHIVED têm uma current; ACTIVE está completa.",
        "SQL com window/aggregation",
        InvariantSeverity.ERROR,
        "Unicidade impede duplicação, mas não lacunas nem ausência.",
        "A apresentação ou a semântica da tentativa deixa de ser determinística.",
        "Calcular row_number e agregar revisão/alternativas correntes.",
        "Baixo; DRAFT sem revisão é explicitamente aceito.",
        "questions.services._create_revision e contratos V0.2",
        "A sequência ou revisão corrente da questão é inválida.",
        _SAFE_ACTION,
    ),
    InvariantSpec(
        "ATT-001",
        "Contexto e resultado da Attempt coerentes",
        "Attempt deve apontar para questão, revisão, alternativa, review e resultado compatíveis.",
        "attempt",
        "Todos os vínculos e is_correct correspondem ao snapshot apresentado.",
        "SQL relacional",
        InvariantSeverity.CRITICAL,
        "A semântica composta é validada na escrita, não pelo schema.",
        "RN-057 e todas as métricas de acerto podem ser corrompidas.",
        "Comparar em lote IDs, Workspaces, gabarito e eventual substituição.",
        "Baixo; a revisão histórica é preservada e não comparada à current.",
        "attempts.models.Attempt e V0.4-S1/S2",
        "O contexto persistido da tentativa é incompatível.",
        _SAFE_ACTION,
    ),
    InvariantSpec(
        "ATT-002",
        "Data civil histórica da Attempt coerente",
        "local_date deve derivar de occurred_at e timezone_name persistidos.",
        "attempt time",
        "A conversão IANA do instante produz exatamente local_date.",
        "Leitura em lote e helper temporal",
        InvariantSeverity.ERROR,
        "Timezone IANA e conversão civil não cabem em constraint SQLite.",
        "Filtros por período e métricas diárias ficam incorretos.",
        "Iterar uma projeção de quatro campos sem carregar models.",
        "Baixo; usa o mesmo TimeZoneId do domínio e não compara timezone atual.",
        "attempts.models.Attempt._validate_references e V0.4-S1",
        "A data civil histórica da tentativa é inválida.",
        _SAFE_ACTION,
    ),
    InvariantSpec(
        "ATT-003",
        "Lifecycle e grafo de substituição coerentes",
        "VOIDED, sucessoras, contexto e ponta devem formar cadeia finita e determinística.",
        "attempt correction",
        "Campos de void fecham; sucessora preserva contexto; não há ciclo nem VALID não terminal.",
        "SQL relacional recursivo",
        InvariantSeverity.CRITICAL,
        "Constraints locais não expressam aciclicidade nem o contexto composto da cadeia.",
        "Analytics, classificação e reconstrução podem escolher fatos divergentes.",
        "Percorrer replaces_attempt em CTE finita e validar estados/contexto.",
        "Baixo; VOIDED sem sucessora é explicitamente permitido.",
        "V0.5-S1 V05-INV-005/006/007",
        "O lifecycle ou grafo de substituição da Attempt é incompatível.",
        _SAFE_ACTION,
    ),
    InvariantSpec(
        "REV-001",
        "Origem do ReviewCycle coerente",
        "Ciclo deve preservar questão, revisão e origem no mesmo contexto.",
        "review cycle",
        "Origem INITIAL_ERROR ou QUESTION_ACTIVATION satisfaz o contrato vigente.",
        "SQL relacional",
        InvariantSeverity.CRITICAL,
        "A constraint de origem não valida as entidades relacionadas.",
        "O ciclo pode nascer de fato alheio ou semanticamente incompatível.",
        "Comparar ciclo, questão, revisão e tentativa de origem.",
        "Baixo; ambos os tipos históricos aprovados são aceitos.",
        "ADR-013 e reviews.models.ReviewCycle",
        "A origem do ciclo de revisão é incompatível.",
        _SAFE_ACTION,
    ),
    InvariantSpec(
        "REV-002",
        "Review e âncora coerentes",
        "Review deve pertencer ao ciclo/questão e ter âncora válida quando exigida.",
        "review",
        "Somente D1 de ativação omite âncora; demais âncoras mantêm contexto.",
        "SQL relacional",
        InvariantSeverity.CRITICAL,
        "A constraint não expressa Workspace, questão e encadeamento anterior.",
        "A progressão pode usar uma resposta de outro ciclo.",
        "Comparar em lote ciclo, questão, âncora e Attempt de conclusão.",
        "Baixo; D1 histórico por erro inicial é aceito.",
        "reviews.models.Review e CompleteReviewService",
        "A revisão ou sua âncora é incompatível.",
        _SAFE_ACTION,
    ),
    InvariantSpec(
        "REV-003",
        "Estado do ciclo coerente com suas Reviews",
        "ACTIVE, COMPLETED e SUSPENDED devem refletir as pendências/fatos do ciclo.",
        "review cycle state",
        "Ciclo ativo tem uma pending; completo termina em D30 correta; suspenso tem suspensa.",
        "SQL agregada",
        InvariantSeverity.ERROR,
        "Constraints locais não relacionam o estado agregado do ciclo.",
        "Fila e dashboard podem apresentar estados mutuamente incompatíveis.",
        "Agregar estados e validar a Review terminal sem recalcular analytics.",
        "Baixo; ciclo completo de questão arquivada continua válido.",
        "REV-FIXA-1.0, Question.archive e V0.4-S1",
        "O estado agregado do ciclo de revisão é inválido.",
        _SAFE_ACTION,
    ),
    InvariantSpec(
        "REV-004",
        "Sequência e agenda da Review coerentes",
        "A sequência e as transições D1/D7/D14/D30 devem seguir a policy vigente.",
        "review schedule",
        "Sequência contígua, transição conhecida e due date derivada da âncora.",
        "SQL com window/date",
        InvariantSeverity.ERROR,
        "A policy decide na escrita, mas o banco não valida a progressão inteira.",
        "Uma revisão pode aparecer na etapa ou data civil errada.",
        "Comparar row_number, transition_code e Attempt.local_date em lote.",
        "Médio; current_due_date não é congelada e por isso não é comparada.",
        "reviews.policies.ReviewSchedulePolicy REV-FIXA-1.0",
        "A sequência ou agenda da revisão é incompatível.",
        _SAFE_ACTION,
    ),
    InvariantSpec(
        "ERR-001",
        "ErrorClassification coerente",
        "Classificação existente deve apontar para erro válido e categoria do mesmo Workspace.",
        "error classification",
        "Attempt é VALID/incorreta e categoria/contexto pertencem ao Workspace.",
        "SQL relacional",
        InvariantSeverity.CRITICAL,
        "OneToOne não expressa correção, status ou tenant composto.",
        "Categorias e drill-downs podem vazar ou contar eventos inelegíveis.",
        "Comparar somente classificações existentes; ausência legítima não é finding.",
        "Baixo; resíduo analítico sem classificação é explicitamente preservado.",
        "V0.4-S1/S2 e errors.models.ErrorClassification",
        "A classificação de erro é incompatível.",
        _SAFE_ACTION,
    ),
    InvariantSpec(
        "ERR-002",
        "Histórico da classificação coerente",
        "Revisões do diagnóstico devem ser contíguas, isoladas e reconciliar a projeção atual.",
        "error classification history",
        "r1..rN pertencem ao contexto e rN coincide com a projeção atual.",
        "SQL com window",
        InvariantSeverity.ERROR,
        "Unicidade não impede lacunas nem divergência da projeção.",
        "Histórico e diagnóstico atual podem contar histórias incompatíveis.",
        "Comparar sequência, Workspace, categoria e última revisão.",
        "Baixo; classificação nunca corrigida pode legitimamente não ter revisões.",
        "errors.services.ErrorClassificationRevisionService",
        "O histórico da classificação é incompatível.",
        _SAFE_ACTION,
    ),
    InvariantSpec(
        "OPS-001",
        "OperationReceipt aponta para resultado compatível",
        "Recibo deve resolver a Attempt correta no mesmo Workspace e operação.",
        "idempotency receipt",
        "Alvo existe, tenant/chave coincidem e tipo/resultado correspondem à operação.",
        "SQL relacional",
        InvariantSeverity.ERROR,
        "result_entity_id é referência técnica sem FK.",
        "Replay idempotente pode confirmar o resultado errado.",
        "Resolver alvos em lote e validar hash/chave/tipo/resultado.",
        "Baixo; não exige recibo para todo fato histórico.",
        "attempts.models.OperationReceipt",
        "O recibo idempotente aponta para resultado incompatível.",
        _SAFE_ACTION,
    ),
    InvariantSpec(
        "CAT-001",
        "Lifecycle e consolidação de categoria coerentes",
        "Categorias padrão permanecem estáveis e merge pessoal termina em alvo ativo local.",
        "error category",
        "Kind/state/target respeitam V05-INV-001, V05-INV-011 e V05-INV-012.",
        "SQL relacional recursivo",
        InvariantSeverity.CRITICAL,
        "Constraints locais não validam Workspace nem cadeias entre linhas.",
        "Analytics pode vazar Workspace, entrar em ciclo ou contar alvo incorreto.",
        "Validar lifecycle, alvo e cadeia até categoria pessoal ACTIVE.",
        "Baixo; categorias arquivadas sem merge são válidas.",
        "V0.5-S1 V05-INV-001/011/012",
        "O lifecycle ou a cadeia de categoria é incompatível.",
        _SAFE_ACTION,
    ),
    InvariantSpec(
        "REV-005",
        "Histórico de reagendamento coerente",
        "A última mudança auditada deve explicar a data operacional da Review.",
        "review reschedule",
        "Mudança, Review e AuditEvent coincidem em Workspace, correlação e datas.",
        "SQL relacional/window",
        InvariantSeverity.CRITICAL,
        "A atomicidade de serviço não é uma constraint intertabelas.",
        "Fila pode usar data sem histórico ou auditoria correspondente.",
        "Comparar cada mudança, evento correlato e última data por Review.",
        "Baixo; Review sem reagendamento é explicitamente válida.",
        "V0.5-S1 V05-INV-002/003/014",
        "O histórico de reagendamento é incompatível.",
        _SAFE_ACTION,
    ),
    InvariantSpec(
        "REV-006",
        "Projeção reconstruída de Review coerente",
        "Ciclo superseded não tem pendência e correção corrente usa origem local válida.",
        "review reconstruction",
        "SUPERSEDED preserva fatos sem fila; ATTEMPT_CORRECTION corrente é determinística.",
        "SQL relacional",
        InvariantSeverity.CRITICAL,
        "A relação entre história preservada e projeção atual atravessa tabelas.",
        "Fila pode manter agenda anulada ou duplicar ciclo corrente.",
        "Validar estados, pendências, origem e uma única projeção ativa por questão.",
        "Baixo; ciclos históricos completed/suspended permanecem aceitos.",
        "V0.5-S1 V05-INV-006/007",
        "A projeção reconstruída de revisão é incompatível.",
        _SAFE_ACTION,
    ),
    InvariantSpec(
        "AUD-001",
        "Auditoria funcional mínima e isolada",
        "Eventos S2A devem usar entidade técnica do mesmo Workspace e metadados fechados.",
        "functional audit",
        "Evento, entidade, relação, correlação e razão codificada respeitam V05-INV-014.",
        "SQL relacional",
        InvariantSeverity.CRITICAL,
        "entity_id é referência técnica deliberadamente sem FK genérica.",
        "Uma trilha órfã ou cross-Workspace deixa de explicar a mutação.",
        "Resolver somente os tipos fechados S2A sem ler conteúdo funcional.",
        "Baixo; motivo opcional da inclusão manual continua permitido.",
        "V0.5-S1 V05-INV-001/014",
        "Um evento de auditoria funcional é incompatível.",
        _SAFE_ACTION,
    ),
)


_SQL_RULES: Final[dict[str, str]] = {
    "WS-001": """
        SELECT s.id AS entity_id, 'Subject' AS entity_type,
               s.workspace_id AS workspace_id, d.workspace_id AS related_workspace_id
        FROM taxonomy_subject s JOIN taxonomy_discipline d ON d.id = s.discipline_id
        WHERE s.workspace_id != d.workspace_id
        UNION ALL
        SELECT ss.id, 'Subsubject', ss.workspace_id, s.workspace_id
        FROM taxonomy_subsubject ss JOIN taxonomy_subject s ON s.id = ss.subject_id
        JOIN taxonomy_discipline d ON d.id = s.discipline_id
        WHERE ss.workspace_id != s.workspace_id OR ss.workspace_id != d.workspace_id
    """,
    "WS-002": """
        SELECT e.id AS entity_id, 'Exam' AS entity_type,
               e.workspace_id AS workspace_id, b.workspace_id AS related_workspace_id
        FROM questions_exam e JOIN questions_board b ON b.id = e.board_id
        WHERE e.workspace_id != b.workspace_id
        UNION ALL
        SELECT o.id, 'QuestionOrigin', o.workspace_id, q.workspace_id
        FROM questions_questionorigin o JOIN questions_question q ON q.id = o.question_id
        WHERE o.workspace_id != q.workspace_id
        UNION ALL
        SELECT o.id, 'QuestionOrigin', o.workspace_id, s.workspace_id
        FROM questions_questionorigin o JOIN questions_source s ON s.id = o.source_id
        WHERE o.workspace_id != s.workspace_id
        UNION ALL
        SELECT o.id, 'QuestionOrigin', o.workspace_id, e.workspace_id
        FROM questions_questionorigin o JOIN questions_exam e ON e.id = o.exam_id
        WHERE o.workspace_id != e.workspace_id
        UNION ALL
        SELECT o.id, 'QuestionOrigin', o.workspace_id, b.workspace_id
        FROM questions_questionorigin o JOIN questions_board b ON b.id = o.board_id
        WHERE o.workspace_id != b.workspace_id
    """,
    "QUE-001": """
        SELECT q.id AS entity_id, 'Question' AS entity_type,
               q.workspace_id AS workspace_id, q.status AS status
        FROM questions_question q
        LEFT JOIN taxonomy_discipline d ON d.id = q.discipline_id
        LEFT JOIN taxonomy_subject s ON s.id = q.subject_id
        LEFT JOIN taxonomy_subsubject ss ON ss.id = q.subsubject_id
        WHERE (d.id IS NOT NULL AND d.workspace_id != q.workspace_id)
           OR (s.id IS NOT NULL AND (s.workspace_id != q.workspace_id
                                     OR s.discipline_id != q.discipline_id))
           OR (ss.id IS NOT NULL AND (ss.workspace_id != q.workspace_id
                                      OR ss.subject_id != q.subject_id))
    """,
    "QUE-002": """
        SELECT r.id AS entity_id, 'QuestionRevision' AS entity_type,
               r.question_id AS question_id, 'revision_owner' AS relation
        FROM questions_questionrevision r JOIN questions_question q ON q.id = r.question_id
        WHERE r.workspace_id != q.workspace_id
        UNION ALL
        SELECT a.id, 'Alternative', r.question_id, 'alternative_owner'
        FROM questions_alternative a
        JOIN questions_questionrevision r ON r.id = a.question_revision_id
        WHERE a.workspace_id != r.workspace_id
        UNION ALL
        SELECT r.id, 'QuestionRevision', r.question_id, 'correct_alternative'
        FROM questions_questionrevision r
        JOIN questions_alternative a ON a.id = r.correct_alternative_id
        WHERE a.workspace_id != r.workspace_id OR a.question_revision_id != r.id
    """,
    "QUE-003": """
        WITH ranked AS (
            SELECT id, question_id, version_number,
                   ROW_NUMBER() OVER (PARTITION BY question_id ORDER BY version_number, id) AS expected
            FROM questions_questionrevision
        ), current_counts AS (
            SELECT q.id, q.status, COUNT(r.id) AS current_count
            FROM questions_question q
            LEFT JOIN questions_questionrevision r
              ON r.question_id = q.id AND r.is_current = 1
            WHERE q.status IN ('ACTIVE', 'ARCHIVED')
            GROUP BY q.id, q.status
        )
        SELECT id AS entity_id, 'QuestionRevision' AS entity_type,
               CAST(version_number AS TEXT) AS observed,
               CAST(expected AS TEXT) AS expected
        FROM ranked WHERE version_number != expected
        UNION ALL
        SELECT id, 'Question', CAST(current_count AS TEXT), '1'
        FROM current_counts WHERE current_count != 1
        UNION ALL
        SELECT q.id, 'Question', 'incomplete_current', 'complete_current'
        FROM questions_question q
        JOIN questions_questionrevision r ON r.question_id = q.id AND r.is_current = 1
        WHERE q.status = 'ACTIVE'
          AND (r.stem IS NULL OR r.correct_alternative_id IS NULL
               OR (SELECT COUNT(*) FROM questions_alternative a
                   WHERE a.question_revision_id = r.id) < 2)
    """,
    "ATT-001": """
        SELECT a.id AS entity_id, 'Attempt' AS entity_type,
               a.question_id AS question_id, a.attempt_type AS attempt_type,
               a.status AS status
        FROM attempts_attempt a
        JOIN questions_question q ON q.id = a.question_id
        JOIN questions_questionrevision r ON r.id = a.question_revision_id
        JOIN questions_alternative alt ON alt.id = a.selected_alternative_id
        LEFT JOIN reviews_review rv ON rv.id = a.review_id
        LEFT JOIN attempts_attempt replaced ON replaced.id = a.replaces_attempt_id
        WHERE a.workspace_id != q.workspace_id
           OR a.workspace_id != r.workspace_id OR r.question_id != a.question_id
           OR a.workspace_id != alt.workspace_id OR alt.question_revision_id != r.id
           OR a.is_correct != CASE WHEN r.correct_alternative_id = alt.id THEN 1 ELSE 0 END
           OR (rv.id IS NOT NULL AND (rv.workspace_id != a.workspace_id
                                      OR rv.question_id != a.question_id))
           OR (replaced.id IS NOT NULL AND (replaced.workspace_id != a.workspace_id
                                            OR replaced.question_id != a.question_id
                                            OR replaced.question_revision_id != a.question_revision_id
                                            OR COALESCE(replaced.review_id, '') != COALESCE(a.review_id, '')
                                            OR replaced.attempt_type != a.attempt_type
                                            OR replaced.status != 'VOIDED'))
    """,
    "ATT-003": """
        WITH RECURSIVE ancestry(start_id, current_id) AS (
            SELECT a.id, a.replaces_attempt_id
            FROM attempts_attempt a
            WHERE a.replaces_attempt_id IS NOT NULL
            UNION
            SELECT ancestry.start_id, parent.replaces_attempt_id
            FROM ancestry
            JOIN attempts_attempt parent ON parent.id = ancestry.current_id
            WHERE parent.replaces_attempt_id IS NOT NULL
        ), graph_findings AS (
            SELECT a.id AS entity_id, 'invalid_void_state' AS observed
            FROM attempts_attempt a
            WHERE (a.status = 'VALID' AND
                   (a.voided_at IS NOT NULL OR a.void_reason IS NOT NULL))
               OR (a.status = 'VOIDED' AND
                   (a.voided_at IS NULL OR a.void_reason IS NULL OR a.void_reason = ''))
            UNION
            SELECT child.id, 'invalid_replacement_context'
            FROM attempts_attempt child
            JOIN attempts_attempt parent ON parent.id = child.replaces_attempt_id
            WHERE parent.status != 'VOIDED'
               OR parent.workspace_id != child.workspace_id
               OR parent.question_id != child.question_id
               OR parent.question_revision_id != child.question_revision_id
               OR COALESCE(parent.review_id, '') != COALESCE(child.review_id, '')
               OR parent.attempt_type != child.attempt_type
            UNION
            SELECT parent.id, 'valid_non_terminal'
            FROM attempts_attempt parent
            JOIN attempts_attempt child ON child.replaces_attempt_id = parent.id
            WHERE parent.status = 'VALID'
            UNION
            SELECT start_id, 'cycle'
            FROM ancestry
            WHERE current_id = start_id
        )
        SELECT entity_id, 'Attempt' AS entity_type, observed
        FROM graph_findings
    """,
    "REV-001": """
        SELECT c.id AS entity_id, 'ReviewCycle' AS entity_type,
               c.question_id AS question_id, c.origin_kind AS origin_kind
        FROM reviews_reviewcycle c
        JOIN questions_question q ON q.id = c.question_id
        JOIN questions_questionrevision r ON r.id = c.origin_question_revision_id
        LEFT JOIN attempts_attempt a ON a.id = c.origin_attempt_id
        WHERE c.workspace_id != q.workspace_id OR c.workspace_id != r.workspace_id
           OR c.question_id != r.question_id
           OR (c.origin_kind = 'INITIAL_ERROR' AND
               (a.id IS NULL OR a.workspace_id != c.workspace_id
                OR a.question_id != c.question_id
                OR a.question_revision_id != c.origin_question_revision_id
                OR a.attempt_type != 'INITIAL' OR a.is_correct != 0
                OR (c.state != 'SUPERSEDED' AND a.status != 'VALID')))
           OR (c.origin_kind = 'QUESTION_ACTIVATION' AND c.origin_attempt_id IS NOT NULL)
           OR (c.origin_kind = 'MANUAL' AND
               (a.id IS NULL OR a.workspace_id != c.workspace_id
                OR a.question_id != c.question_id
                OR a.question_revision_id != c.origin_question_revision_id
                OR a.attempt_type != 'INITIAL' OR a.is_correct != 1
                OR (c.state != 'SUPERSEDED' AND a.status != 'VALID')))
           OR (c.origin_kind = 'ATTEMPT_CORRECTION' AND
               ((a.id IS NOT NULL AND
                 (a.workspace_id != c.workspace_id OR a.question_id != c.question_id
                  OR a.question_revision_id != c.origin_question_revision_id
                  OR (c.state != 'SUPERSEDED' AND a.status != 'VALID')))
                OR (c.state = 'COMPLETED' AND a.id IS NULL)))
    """,
    "REV-002": """
        SELECT r.id AS entity_id, 'Review' AS entity_type,
               r.review_cycle_id AS cycle_id, CAST(r.sequence_number AS TEXT) AS sequence_number
        FROM reviews_review r
        JOIN reviews_reviewcycle c ON c.id = r.review_cycle_id
        JOIN questions_question q ON q.id = r.question_id
        LEFT JOIN attempts_attempt anchor ON anchor.id = r.scheduled_from_attempt_id
        WHERE r.workspace_id != c.workspace_id OR r.question_id != c.question_id
           OR r.workspace_id != q.workspace_id
           OR (anchor.id IS NULL AND NOT (
                r.sequence_number = 1 AND r.stage_code = 'D1' AND (
                    (c.origin_kind = 'QUESTION_ACTIVATION'
                     AND r.transition_code = 'QUESTION_ACTIVATION_D1')
                    OR (c.origin_kind = 'ATTEMPT_CORRECTION'
                        AND r.transition_code = 'CORRECTION_RETRY_VOIDED'))))
           OR (anchor.id IS NOT NULL AND
               (anchor.workspace_id != r.workspace_id OR anchor.question_id != r.question_id
                OR (r.state = 'PENDING' AND anchor.status != 'VALID')
                 OR (r.sequence_number = 1 AND NOT (
                    (c.origin_kind = 'INITIAL_ERROR' AND anchor.id = c.origin_attempt_id
                     AND anchor.attempt_type = 'INITIAL' AND anchor.is_correct = 0
                     AND r.transition_code = 'INITIAL_ERROR_TO_D1')
                    OR (c.origin_kind = 'MANUAL' AND anchor.id = c.origin_attempt_id
                        AND anchor.attempt_type = 'INITIAL' AND anchor.is_correct = 1
                        AND r.transition_code = 'MANUAL_INCLUSION_D1')
                    OR c.origin_kind = 'ATTEMPT_CORRECTION'))
                OR (r.sequence_number > 1 AND c.origin_kind != 'ATTEMPT_CORRECTION' AND
                    (anchor.attempt_type != 'REVIEW' OR NOT EXISTS (
                        SELECT 1 FROM reviews_review previous
                        WHERE previous.id = anchor.review_id
                          AND previous.review_cycle_id = r.review_cycle_id
                          AND previous.sequence_number = r.sequence_number - 1)))))
           OR (r.state = 'COMPLETED' AND c.state != 'SUPERSEDED' AND NOT EXISTS (
                SELECT 1 FROM attempts_attempt done
                WHERE done.review_id = r.id AND done.attempt_type = 'REVIEW'
                  AND done.status = 'VALID'))
           OR (r.state != 'COMPLETED' AND EXISTS (
                SELECT 1 FROM attempts_attempt done
                WHERE done.review_id = r.id AND done.status = 'VALID'))
    """,
    "REV-003": """
        SELECT c.id AS entity_id, 'ReviewCycle' AS entity_type,
               c.state AS state, q.status AS question_status
        FROM reviews_reviewcycle c JOIN questions_question q ON q.id = c.question_id
        WHERE (c.state = 'ACTIVE' AND
               (q.status != 'ACTIVE' OR
                (SELECT COUNT(*) FROM reviews_review r
                 WHERE r.review_cycle_id = c.id AND r.state = 'PENDING') != 1))
           OR (c.state = 'SUSPENDED' AND
               (q.status != 'ARCHIVED' OR
                (SELECT COUNT(*) FROM reviews_review r
                 WHERE r.review_cycle_id = c.id AND r.state = 'PENDING') != 0 OR
                (SELECT COUNT(*) FROM reviews_review r
                 WHERE r.review_cycle_id = c.id AND r.state = 'SUSPENDED') != 1))
           OR (c.state = 'COMPLETED' AND
               ((SELECT COUNT(*) FROM reviews_review r
                 WHERE r.review_cycle_id = c.id AND r.state = 'PENDING') != 0 OR
                (c.origin_kind != 'ATTEMPT_CORRECTION' AND NOT EXISTS (
                    SELECT 1 FROM reviews_review terminal
                    JOIN attempts_attempt a ON a.review_id = terminal.id
                    WHERE terminal.review_cycle_id = c.id AND terminal.stage_code = 'D30'
                      AND terminal.state = 'COMPLETED' AND a.status = 'VALID'
                      AND a.attempt_type = 'REVIEW' AND a.is_correct = 1
                      AND terminal.sequence_number = (
                          SELECT MAX(last.sequence_number) FROM reviews_review last
                          WHERE last.review_cycle_id = c.id)))
                OR (c.origin_kind = 'ATTEMPT_CORRECTION' AND NOT EXISTS (
                    SELECT 1 FROM attempts_attempt corrected
                    JOIN reviews_review original ON original.id = corrected.review_id
                    WHERE corrected.id = c.origin_attempt_id
                      AND corrected.status = 'VALID' AND corrected.is_correct = 1
                      AND original.stage_code = 'D30'))))
           OR (c.state = 'SUPERSEDED' AND
               (c.superseded_at IS NULL OR EXISTS (
                   SELECT 1 FROM reviews_review pending
                   WHERE pending.review_cycle_id = c.id AND pending.state = 'PENDING')))
    """,
    "REV-004": """
        WITH ranked AS (
            SELECT r.*,
                   ROW_NUMBER() OVER (
                       PARTITION BY r.review_cycle_id ORDER BY r.sequence_number, r.id
                   ) AS expected_sequence
            FROM reviews_review r
        )
        SELECT r.id AS entity_id, 'Review' AS entity_type,
               CAST(r.sequence_number AS TEXT) AS sequence_number,
               r.stage_code AS stage_code, r.transition_code AS transition_code
        FROM ranked r
        JOIN reviews_reviewcycle c ON c.id = r.review_cycle_id
        LEFT JOIN attempts_attempt a ON a.id = r.scheduled_from_attempt_id
        WHERE r.sequence_number != r.expected_sequence
           OR (r.sequence_number = 1 AND r.stage_code != 'D1'
               AND c.origin_kind != 'ATTEMPT_CORRECTION')
           OR (r.sequence_number = 1 AND a.id IS NOT NULL AND NOT (
                (c.origin_kind = 'INITIAL_ERROR'
                 AND r.transition_code = 'INITIAL_ERROR_TO_D1'
                 AND r.first_due_date = date(a.local_date, '+1 day'))
                OR (c.origin_kind = 'MANUAL'
                    AND r.transition_code = 'MANUAL_INCLUSION_D1')
                OR (c.origin_kind = 'ATTEMPT_CORRECTION' AND (
                    (r.transition_code = 'CORRECTION_RETRY_VOIDED')
                    OR (r.transition_code = 'CORRECTION_PRESERVE_MANUAL')
                    OR (r.transition_code = 'RESET_TO_D1_AFTER_ERROR'
                        AND r.stage_code = 'D1')
                    OR (r.transition_code = 'ADVANCE_D1_TO_D7'
                        AND r.stage_code = 'D7')
                    OR (r.transition_code = 'ADVANCE_D7_TO_D14'
                        AND r.stage_code = 'D14')
                    OR (r.transition_code = 'ADVANCE_D14_TO_D30'
                        AND r.stage_code = 'D30')))))
           OR (r.sequence_number > 1 AND NOT (
                (r.transition_code = 'RESET_TO_D1_AFTER_ERROR' AND r.stage_code = 'D1')
                OR (r.transition_code = 'ADVANCE_D1_TO_D7' AND r.stage_code = 'D7')
                OR (r.transition_code = 'ADVANCE_D7_TO_D14' AND r.stage_code = 'D14')
                OR (r.transition_code = 'ADVANCE_D14_TO_D30' AND r.stage_code = 'D30')))
           OR (a.id IS NOT NULL
               AND (r.sequence_number > 1 OR c.origin_kind = 'ATTEMPT_CORRECTION')
               AND r.transition_code NOT IN (
                   'CORRECTION_RETRY_VOIDED', 'CORRECTION_PRESERVE_MANUAL')
               AND r.first_due_date != date(
                a.local_date,
                CASE r.transition_code
                    WHEN 'RESET_TO_D1_AFTER_ERROR' THEN '+1 day'
                    WHEN 'ADVANCE_D1_TO_D7' THEN '+7 days'
                    WHEN 'ADVANCE_D7_TO_D14' THEN '+14 days'
                    WHEN 'ADVANCE_D14_TO_D30' THEN '+30 days'
                    ELSE '+0 days'
                END))
    """,
    "ERR-001": """
        SELECT c.id AS entity_id, 'ErrorCategory' AS entity_type,
               NULL AS attempt_id, c.code AS category_code
        FROM errors_error_category c
        WHERE c.category_kind = 'STANDARD' AND c.code NOT IN (
            'CONCEPTUAL', 'INTERPRETATION', 'CALCULATION', 'ATTENTION',
            'FORMULA_RULE', 'PROCEDURE', 'TRAP', 'TIME_SHORTAGE', 'GUESS', 'OTHER'
        )
        UNION ALL
        SELECT e.id, 'ErrorClassification',
               e.attempt_id AS attempt_id, c.code AS category_code
        FROM errors_errorclassification e
        JOIN attempts_attempt a ON a.id = e.attempt_id
        JOIN errors_error_category c ON c.id = e.category_id
        WHERE e.workspace_id != a.workspace_id OR e.workspace_id != c.workspace_id
           OR a.is_correct = 1
            OR (c.category_kind = 'STANDARD' AND c.code NOT IN (
                 'CONCEPTUAL', 'INTERPRETATION', 'CALCULATION', 'ATTENTION',
                 'FORMULA_RULE', 'PROCEDURE', 'TRAP', 'TIME_SHORTAGE', 'GUESS', 'OTHER'
           ))
           OR c.category_kind NOT IN ('STANDARD', 'PERSONAL')
           OR (c.code = 'OTHER' AND e.other_description IS NULL)
    """,
    "ERR-002": """
        WITH ranked AS (
            SELECT r.*,
                   ROW_NUMBER() OVER (
                       PARTITION BY r.error_classification_id
                       ORDER BY r.revision_number, r.id
                   ) AS expected_revision,
                   MAX(r.revision_number) OVER (
                       PARTITION BY r.error_classification_id
                   ) AS latest_revision
            FROM errors_errorclassificationrevision r
        )
        SELECT r.id AS entity_id, 'ErrorClassificationRevision' AS entity_type,
               CAST(r.revision_number AS TEXT) AS revision_number,
               CAST(r.expected_revision AS TEXT) AS expected_revision
        FROM ranked r
        JOIN errors_errorclassification e ON e.id = r.error_classification_id
        JOIN errors_error_category c ON c.id = r.category_id
        WHERE r.workspace_id != e.workspace_id OR r.workspace_id != c.workspace_id
           OR r.revision_number != r.expected_revision
           OR (c.code = 'OTHER' AND r.other_description IS NULL)
           OR (r.revision_number = r.latest_revision AND
               (r.category_id != e.category_id
                OR COALESCE(r.other_description, '') != COALESCE(e.other_description, '')))
    """,
    "OPS-001": """
        SELECT o.id AS entity_id, 'OperationReceipt' AS entity_type,
               o.operation_kind AS operation_kind, o.result_entity_id AS result_entity_id
        FROM attempts_operationreceipt o
        LEFT JOIN attempts_attempt a
          ON o.result_entity_type = 'ATTEMPT' AND a.id = o.result_entity_id
        WHERE a.id IS NULL OR a.workspace_id != o.workspace_id
           OR a.idempotency_key != o.idempotency_key
           OR length(o.request_hash) != 64 OR o.request_hash GLOB '*[^0-9a-f]*'
           OR (o.operation_kind = 'INITIAL_CORRECT'
               AND (a.attempt_type != 'INITIAL' OR a.is_correct != 1))
           OR (o.operation_kind = 'INITIAL_ERROR'
               AND (a.attempt_type != 'INITIAL' OR a.is_correct != 0))
           OR (o.operation_kind = 'REVIEW_COMPLETION' AND a.attempt_type != 'REVIEW')
    """,
    "CAT-001": """
        WITH RECURSIVE walk(source_id, workspace_id, current_id, path, cycle) AS (
            SELECT c.id, c.workspace_id, c.merged_into_id, ',' || c.id || ',', 0
            FROM errors_error_category c
            WHERE c.category_kind = 'PERSONAL' AND c.state = 'MERGED'
            UNION ALL
            SELECT w.source_id, w.workspace_id, target.merged_into_id,
                   w.path || target.id || ',',
                   CASE WHEN instr(w.path, ',' || target.id || ',') > 0
                             OR target.workspace_id != w.workspace_id
                             OR target.category_kind != 'PERSONAL'
                        THEN 1 ELSE 0 END
            FROM walk w
            JOIN errors_error_category target ON target.id = w.current_id
            WHERE w.cycle = 0 AND target.state = 'MERGED'
        ), invalid_chain AS (
            SELECT DISTINCT w.source_id
            FROM walk w
            LEFT JOIN errors_error_category terminal ON terminal.id = w.current_id
            WHERE w.cycle = 1 OR terminal.id IS NULL
               OR (terminal.state != 'MERGED' AND
                   (terminal.workspace_id != w.workspace_id
                    OR terminal.category_kind != 'PERSONAL'
                    OR terminal.state != 'ACTIVE'))
        )
        SELECT c.id AS entity_id, 'ErrorCategory' AS entity_type,
               c.category_kind AS category_kind, c.state AS state
        FROM errors_error_category c
        LEFT JOIN errors_error_category target ON target.id = c.merged_into_id
        WHERE (c.category_kind = 'STANDARD' AND
               (c.state != 'ACTIVE' OR c.merged_into_id IS NOT NULL OR c.code NOT IN (
                 'CONCEPTUAL', 'INTERPRETATION', 'CALCULATION', 'ATTENTION',
                 'FORMULA_RULE', 'PROCEDURE', 'TRAP', 'TIME_SHORTAGE', 'GUESS', 'OTHER')))
           OR (c.category_kind = 'PERSONAL' AND
               (c.code NOT LIKE 'PERSONAL_%' OR c.name_key = ''
                OR (c.state = 'MERGED') != (c.merged_into_id IS NOT NULL)))
           OR c.category_kind NOT IN ('STANDARD', 'PERSONAL')
           OR c.id IN (SELECT source_id FROM invalid_chain)
    """,
    "REV-005": """
        WITH latest AS (
            SELECT h.*,
                   ROW_NUMBER() OVER (
                       PARTITION BY h.review_id ORDER BY h.created_at DESC, h.id DESC
                   ) AS latest_rank
            FROM reviews_reviewschedulechange h
        )
        SELECT h.id AS entity_id, 'ReviewScheduleChange' AS entity_type,
               h.review_id AS review_id, h.reason_code AS reason_code
        FROM latest h
        JOIN reviews_review r ON r.id = h.review_id
        LEFT JOIN operations_auditevent a
          ON a.workspace_id = h.workspace_id
         AND a.event_code = 'REVIEW_RESCHEDULED'
         AND a.entity_type = 'REVIEW'
         AND a.entity_id = h.review_id
         AND a.correlation_id = h.correlation_id
        WHERE h.workspace_id != r.workspace_id OR h.previous_due_date = h.new_due_date
           OR a.id IS NULL OR a.previous_date != h.previous_due_date
           OR a.new_date != h.new_due_date OR a.reason_code != h.reason_code
           OR a.timezone_name != h.timezone_name
           OR (h.latest_rank = 1 AND r.current_due_date != h.new_due_date)
        UNION ALL
        SELECT r.id, 'Review', r.id, 'MISSING_SCHEDULE_CHANGE'
        FROM reviews_review r
        WHERE r.current_due_date != r.first_due_date
          AND NOT EXISTS (
              SELECT 1 FROM reviews_reviewschedulechange h WHERE h.review_id = r.id
          )
    """,
    "REV-006": """
        SELECT c.id AS entity_id, 'ReviewCycle' AS entity_type,
               c.state AS state, c.origin_kind AS origin_kind
        FROM reviews_reviewcycle c
        LEFT JOIN attempts_attempt a ON a.id = c.origin_attempt_id
        WHERE (c.state = 'SUPERSEDED' AND
               (c.superseded_at IS NULL OR EXISTS (
                   SELECT 1 FROM reviews_review pending
                   WHERE pending.review_cycle_id = c.id AND pending.state = 'PENDING')))
           OR (c.state != 'SUPERSEDED' AND c.superseded_at IS NOT NULL)
           OR (c.origin_kind = 'ATTEMPT_CORRECTION' AND c.state != 'SUPERSEDED' AND
               (a.id IS NOT NULL AND
                (a.workspace_id != c.workspace_id OR a.question_id != c.question_id
                 OR a.status != 'VALID')))
           OR (c.state = 'ACTIVE' AND (
               SELECT COUNT(*) FROM reviews_reviewcycle current
               WHERE current.question_id = c.question_id
                 AND current.workspace_id = c.workspace_id
                 AND current.state = 'ACTIVE') != 1)
    """,
    "AUD-001": """
        SELECT a.id AS entity_id, 'AuditEvent' AS entity_type,
               a.event_code AS event_code, a.entity_type AS audited_entity_type
        FROM operations_auditevent a
        LEFT JOIN reviews_review r
          ON a.event_code = 'REVIEW_RESCHEDULED' AND r.id = a.entity_id
        LEFT JOIN reviews_reviewcycle c
          ON a.event_code = 'MANUAL_REVIEW_INCLUDED' AND c.id = a.entity_id
        LEFT JOIN questions_question q
          ON a.event_code = 'MANUAL_REVIEW_INCLUDED' AND q.id = a.related_entity_id
        LEFT JOIN errors_error_category source
          ON a.event_code IN ('PERSONAL_CATEGORY_RENAMED', 'PERSONAL_CATEGORY_ARCHIVED',
                              'PERSONAL_CATEGORY_MERGED') AND source.id = a.entity_id
        LEFT JOIN errors_error_category target
          ON a.event_code = 'PERSONAL_CATEGORY_MERGED' AND target.id = a.related_entity_id
        LEFT JOIN attempts_attempt attempt_source
          ON a.event_code IN ('ATTEMPT_VOIDED', 'ATTEMPT_REPLACED')
         AND attempt_source.id = a.entity_id
        LEFT JOIN attempts_attempt attempt_target
          ON a.event_code = 'ATTEMPT_REPLACED'
         AND attempt_target.id = a.related_entity_id
        LEFT JOIN questions_question answer_question
          ON a.event_code = 'ANSWER_KEY_CORRECTED' AND answer_question.id = a.entity_id
        LEFT JOIN questions_questionrevision previous_revision
          ON a.event_code = 'ANSWER_KEY_CORRECTED'
         AND previous_revision.id = a.previous_entity_id
        LEFT JOIN questions_questionrevision new_revision
          ON a.event_code = 'ANSWER_KEY_CORRECTED'
         AND new_revision.id = a.related_entity_id
        WHERE (a.reason_code IS NOT NULL AND
               (a.reason_code NOT GLOB '[A-Z]*' OR a.reason_code GLOB '*[^A-Z0-9_]*'))
           OR (a.event_code = 'REVIEW_RESCHEDULED' AND
               (a.entity_type != 'REVIEW' OR r.id IS NULL OR r.workspace_id != a.workspace_id))
           OR (a.event_code = 'MANUAL_REVIEW_INCLUDED' AND
               (a.entity_type != 'REVIEW_CYCLE' OR c.id IS NULL OR q.id IS NULL
                OR c.workspace_id != a.workspace_id OR q.workspace_id != a.workspace_id))
           OR (a.event_code IN ('PERSONAL_CATEGORY_RENAMED', 'PERSONAL_CATEGORY_ARCHIVED') AND
               (a.entity_type != 'ERROR_CATEGORY' OR source.id IS NULL
                OR source.workspace_id != a.workspace_id OR a.related_entity_id IS NOT NULL))
           OR (a.event_code = 'PERSONAL_CATEGORY_MERGED' AND
               (a.entity_type != 'ERROR_CATEGORY' OR source.id IS NULL OR target.id IS NULL
                OR source.workspace_id != a.workspace_id OR target.workspace_id != a.workspace_id))
           OR (a.event_code IN ('PERSONAL_CATEGORY_RENAMED', 'PERSONAL_CATEGORY_ARCHIVED',
                                'PERSONAL_CATEGORY_MERGED') AND a.reason_code IS NULL)
           OR (a.event_code = 'ATTEMPT_VOIDED' AND
               (a.entity_type != 'ATTEMPT' OR attempt_source.id IS NULL
                OR attempt_source.workspace_id != a.workspace_id
                OR attempt_source.status != 'VOIDED' OR a.reason_code IS NULL))
           OR (a.event_code = 'ATTEMPT_REPLACED' AND
               (a.entity_type != 'ATTEMPT' OR attempt_source.id IS NULL
                OR attempt_target.id IS NULL OR attempt_source.workspace_id != a.workspace_id
                OR attempt_target.workspace_id != a.workspace_id
                OR attempt_target.replaces_attempt_id != attempt_source.id
                OR a.reason_code IS NULL))
           OR (a.event_code = 'ANSWER_KEY_CORRECTED' AND
               (a.entity_type != 'QUESTION' OR answer_question.id IS NULL
                OR previous_revision.id IS NULL OR new_revision.id IS NULL
                OR answer_question.workspace_id != a.workspace_id
                OR previous_revision.workspace_id != a.workspace_id
                OR new_revision.workspace_id != a.workspace_id
                OR previous_revision.question_id != answer_question.id
                OR new_revision.question_id != answer_question.id
                OR new_revision.version_number != previous_revision.version_number + 1
                OR new_revision.change_kind != 'CRITICAL_CORRECTION'
                OR a.reason_code IS NULL))
           OR (a.event_code != 'ANSWER_KEY_CORRECTED' AND a.previous_entity_id IS NOT NULL)
           OR (a.event_code != 'REVIEW_RESCHEDULED' AND
               (a.previous_date IS NOT NULL OR a.new_date IS NOT NULL OR a.timezone_name IS NOT NULL))
    """,
}


def _database_path(using: str) -> Path:
    connection = connections[using]
    if connection.vendor != "sqlite":
        raise IntegrityCheckOperationalError("O checker S5 exige o banco SQLite do projeto.")
    configured_name = connection.settings_dict.get("NAME")
    if not configured_name or str(configured_name) == ":memory:":
        raise IntegrityCheckOperationalError("O banco SQLite precisa existir em arquivo local.")
    path = Path(str(configured_name)).resolve()
    if not path.is_file():
        raise IntegrityCheckOperationalError("O arquivo do banco SQLite não está disponível.")
    return path


def _finding(
    spec: InvariantSpec,
    *,
    entity_type: str,
    technical_id: str,
    context: tuple[tuple[str, str], ...] = (),
) -> IntegrityFinding:
    return IntegrityFinding(
        invariant_id=spec.invariant_id,
        severity=spec.severity,
        entity_type=entity_type,
        technical_id=_safe_technical_value(technical_id),
        message=spec.message,
        technical_context=tuple((key, _safe_technical_value(value)) for key, value in context),
        operational_action=spec.operational_action,
    )


def _safe_technical_value(value: object) -> str:
    text = str(value)
    if text == "database" or text.isdecimal() or _UUID_PATTERN.fullmatch(text):
        return text
    if _DATE_PATTERN.fullmatch(text) or text in _SAFE_CODES:
        return text
    try:
        return TimeZoneId(text).value
    except (TypeError, ValueError):
        return REDACTED


def _append_sql_findings(
    database: sqlite3.Connection,
    spec: InvariantSpec,
    query: str,
    findings: list[IntegrityFinding],
    *,
    limit: int,
) -> int:
    sample_limit = max(1, limit - len(findings))
    wrapped = "".join(
        (
            "SELECT violations.*, COUNT(*) OVER () AS _total_findings FROM (",
            query,
            ") AS violations ORDER BY entity_type, entity_id LIMIT ?",
        )
    )
    cursor = database.execute(wrapped, (sample_limit,))
    rows = cursor.fetchall()
    if not rows:
        return 0
    names = tuple(column[0] for column in cursor.description or ())
    total_index = names.index("_total_findings")
    total = int(rows[0][total_index])
    if len(findings) >= limit:
        return total
    for row in rows[: limit - len(findings)]:
        document = dict(zip(names, row, strict=True))
        entity_type = str(document.pop("entity_type"))
        technical_id = str(document.pop("entity_id"))
        document.pop("_total_findings")
        context = tuple((str(key), str(value)) for key, value in document.items())
        findings.append(
            _finding(
                spec,
                entity_type=entity_type,
                technical_id=technical_id,
                context=context,
            )
        )
    return total


def _append_integrity_findings(
    database: sqlite3.Connection,
    spec: InvariantSpec,
    findings: list[IntegrityFinding],
    *,
    limit: int,
) -> int:
    cursor = database.execute("PRAGMA integrity_check(1000000)")
    first = cursor.fetchone()
    if first == ("ok",) and cursor.fetchone() is None:
        return 0
    total = 0 if first is None else 1
    total += sum(1 for _row in cursor)
    if len(findings) < limit:
        findings.append(
            _finding(
                spec,
                entity_type="SQLiteDatabase",
                technical_id="database",
                context=(("issues_detected", str(total)),),
            )
        )
    return total


def _append_foreign_key_findings(
    database: sqlite3.Connection,
    spec: InvariantSpec,
    findings: list[IntegrityFinding],
    *,
    limit: int,
) -> int:
    total = 0
    for table, rowid, parent, foreign_key_id in database.execute("PRAGMA foreign_key_check"):
        total += 1
        if len(findings) >= limit:
            continue
        findings.append(
            _finding(
                spec,
                entity_type="DatabaseRow",
                technical_id=str(rowid),
                context=(
                    ("table", str(table)),
                    ("parent_table", str(parent)),
                    ("foreign_key_id", str(foreign_key_id)),
                ),
            )
        )
    return total


def _append_attempt_time_findings(
    database: sqlite3.Connection,
    spec: InvariantSpec,
    findings: list[IntegrityFinding],
    *,
    limit: int,
) -> int:
    total = 0
    rows = database.execute(
        "SELECT id, occurred_at, timezone_name, local_date FROM attempts_attempt ORDER BY id"
    )
    for technical_id, occurred_at, timezone_name, local_date in rows:
        try:
            instant = datetime.fromisoformat(str(occurred_at))
            if instant.tzinfo is None:
                instant = instant.replace(tzinfo=UTC)
            expected = instant.astimezone(TimeZoneId(str(timezone_name)).zone).date().isoformat()
        except (TypeError, ValueError):
            expected = "invalid-temporal-context"
        if str(local_date) == expected:
            continue
        total += 1
        if len(findings) >= limit:
            continue
        findings.append(
            _finding(
                spec,
                entity_type="Attempt",
                technical_id=str(technical_id),
                context=(
                    ("local_date", str(local_date)),
                    ("expected_local_date", expected),
                    ("timezone_name", str(timezone_name)),
                ),
            )
        )
    return total


def _append_workspace_timezone_findings(
    database: sqlite3.Connection,
    spec: InvariantSpec,
    findings: list[IntegrityFinding],
    *,
    limit: int,
) -> int:
    total = 0
    rows = database.execute("SELECT id, timezone_name FROM accounts_workspace ORDER BY id")
    for technical_id, timezone_name in rows:
        try:
            TimeZoneId(str(timezone_name))
        except (TypeError, ValueError):
            total += 1
            if len(findings) < limit:
                findings.append(
                    _finding(
                        spec,
                        entity_type="Workspace",
                        technical_id=str(technical_id),
                        context=(("timezone_name", str(timezone_name)),),
                    )
                )
    return total


def _append_inaugural_schedule_findings(
    database: sqlite3.Connection,
    spec: InvariantSpec,
    findings: list[IntegrityFinding],
    *,
    limit: int,
) -> int:
    total = 0
    rows = database.execute(
        "SELECT r.id, c.started_at, w.timezone_name, r.first_due_date "
        "FROM reviews_review r "
        "JOIN reviews_reviewcycle c ON c.id = r.review_cycle_id "
        "JOIN accounts_workspace w ON w.id = r.workspace_id "
        "WHERE c.origin_kind IN ('QUESTION_ACTIVATION', 'MANUAL') AND r.sequence_number = 1 "
        "ORDER BY r.id"
    )
    for technical_id, started_at, timezone_name, first_due_date in rows:
        try:
            instant = datetime.fromisoformat(str(started_at))
            if instant.tzinfo is None:
                instant = instant.replace(tzinfo=UTC)
            expected = (
                instant.astimezone(TimeZoneId(str(timezone_name)).zone).date() + timedelta(days=1)
            ).isoformat()
        except (TypeError, ValueError):
            continue
        if str(first_due_date) == expected:
            continue
        total += 1
        if len(findings) < limit:
            findings.append(
                _finding(
                    spec,
                    entity_type="Review",
                    technical_id=str(technical_id),
                    context=(
                        ("first_due_date", str(first_due_date)),
                        ("expected_first_due_date", expected),
                    ),
                )
            )
    return total


def run_integrity_check(
    *,
    using: str = "default",
    finding_limit: int = DEFAULT_FINDING_LIMIT,
) -> IntegrityCheckResult:
    """Execute todas as invariantes sobre snapshot lógico e conexão mode=ro."""
    if not 1 <= finding_limit <= MAX_FINDING_LIMIT:
        raise ValueError(f"finding_limit deve estar entre 1 e {MAX_FINDING_LIMIT}.")
    path = _database_path(using)
    findings: list[IntegrityFinding] = []
    totals: Counter[InvariantSeverity] = Counter()
    queries_executed = 0
    try:
        with closing(
            sqlite3.connect(f"{path.as_uri()}?mode=ro", uri=True, timeout=5.0)
        ) as database:
            database.execute("BEGIN")
            for spec in INVARIANT_CATALOG:
                if spec.invariant_id == "DB-001":
                    count = _append_integrity_findings(
                        database, spec, findings, limit=finding_limit
                    )
                elif spec.invariant_id == "DB-002":
                    count = _append_foreign_key_findings(
                        database, spec, findings, limit=finding_limit
                    )
                elif spec.invariant_id == "ATT-002":
                    count = _append_attempt_time_findings(
                        database, spec, findings, limit=finding_limit
                    )
                elif spec.invariant_id == "WS-003":
                    count = _append_workspace_timezone_findings(
                        database, spec, findings, limit=finding_limit
                    )
                else:
                    count = _append_sql_findings(
                        database,
                        spec,
                        _SQL_RULES[spec.invariant_id],
                        findings,
                        limit=finding_limit,
                    )
                    if spec.invariant_id == "REV-004":
                        count += _append_inaugural_schedule_findings(
                            database, spec, findings, limit=finding_limit
                        )
                        queries_executed += 1
                queries_executed += 1
                totals[spec.severity] += count
            database.rollback()
    except (OSError, sqlite3.Error, KeyError, TypeError, ValueError) as error:
        raise IntegrityCheckOperationalError(
            "O checker não conseguiu concluir a leitura consistente do banco."
        ) from error

    ordered_findings = tuple(
        sorted(findings, key=lambda item: (item.invariant_id, item.entity_type, item.technical_id))
    )
    severity_counts = tuple(
        (severity, totals[severity]) for severity in InvariantSeverity if totals[severity]
    )
    return IntegrityCheckResult(
        checks_executed=len(INVARIANT_CATALOG),
        total_findings=sum(totals.values()),
        findings=ordered_findings,
        severity_counts=severity_counts,
        queries_executed=queries_executed,
    )
