"""Workspace-scoped batch adapter for the pure Subject priority policy."""

from __future__ import annotations

import uuid
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from zoneinfo import ZoneInfo

from modules.accounts.models import Workspace
from modules.analytics.read_models import AttemptFilters
from modules.analytics.selectors import eligible_reviews, review_reference_date, valid_attempts
from modules.attempts.models import AttemptType
from modules.domain.policy import aggregate_hierarchy
from modules.domain.services import current_domains
from modules.questions.models import Question, QuestionStatus
from modules.reviews.policies import ReviewTemporalStatus
from modules.taxonomy.models import Subject, TaxonomyStatus
from shared.domain.time import Clock

from .policy import (
    DeclineEvidence,
    PriorityInput,
    PriorityResult,
    RecurrenceEvidence,
    evaluate_priority,
    rank_priorities,
)


@dataclass(frozen=True, slots=True)
class SubjectPriority:
    subject: Subject
    result: PriorityResult


@dataclass(frozen=True, slots=True)
class PriorityList:
    ranked: tuple[SubjectPriority, ...]
    collect_more_evidence: tuple[SubjectPriority, ...]
    evaluated_on: date


def list_subject_priorities(*, workspace_id: uuid.UUID, clock: Clock | None = None) -> PriorityList:
    """Read existing facts in batches and leave Review Queue untouched."""
    workspace = Workspace.objects.only("timezone_name").get(pk=workspace_id)
    zone = ZoneInfo(workspace.timezone_name)
    today = review_reference_date(workspace_id=workspace_id, clock=clock)
    subjects = tuple(
        Subject.objects.filter(
            workspace_id=workspace_id,
            status=TaxonomyStatus.ACTIVE,
            discipline__workspace_id=workspace_id,
            discipline__status=TaxonomyStatus.ACTIVE,
        ).order_by("id")
    )
    questions = tuple(
        Question.objects.filter(
            workspace_id=workspace_id,
            status=QuestionStatus.ACTIVE,
            subject_id__in=(item.id for item in subjects),
        ).only("id", "subject_id")
    )
    question_ids = tuple(item.id for item in questions)
    ids_by_subject: dict[uuid.UUID, list[uuid.UUID]] = defaultdict(list)
    for item in questions:
        if item.subject_id is None:
            raise ValueError("Question ativa sem Subject.")
        ids_by_subject[item.subject_id].append(item.id)
    domains = current_domains(workspace_id=workspace_id, question_ids=question_ids, clock=clock)
    overdue_ids = (
        set(
            eligible_reviews(
                workspace_id=workspace_id,
                status=ReviewTemporalStatus.OVERDUE,
                clock=clock,
                reference_date=today,
            )
            .filter(question_id__in=question_ids)
            .values_list("question_id", flat=True)
        )
        if question_ids
        else set()
    )

    performed: set[uuid.UUID] = set()
    recurrence: dict[uuid.UUID, list[int]] = defaultdict(lambda: [0, 0])
    decline: dict[uuid.UUID, list[int]] = defaultdict(lambda: [0, 0, 0, 0])
    if question_ids:
        attempts = (
            valid_attempts(workspace_id=workspace_id, filters=AttemptFilters())
            .filter(question_id__in=question_ids)
            .values_list("question_id", "attempt_type", "occurred_at", "is_correct")
        )
        for question_id, kind, occurred_at, correct in attempts:
            if kind == AttemptType.INITIAL:
                performed.add(question_id)
                continue
            if kind != AttemptType.REVIEW:
                continue
            local_date = occurred_at.astimezone(zone).date()
            age = (today - local_date).days
            if 0 <= age <= 89:
                recurrence[question_id][0] += 1
                recurrence[question_id][1] += not correct
            if 0 <= age <= 29:
                decline[question_id][2] += 1
                decline[question_id][3] += correct
            elif 30 <= age <= 59:
                decline[question_id][0] += 1
                decline[question_id][1] += correct

    rows: list[SubjectPriority] = []
    for subject in subjects:
        ids = ids_by_subject[subject.id]
        aggregate = aggregate_hierarchy(
            tuple(domains[qid].result for qid in ids if qid in domains and qid in performed)
        )
        result = evaluate_priority(
            PriorityInput(
                subject_id=subject.id,
                evaluated_on=today,
                mastery=aggregate.domain_index,
                confidence=aggregate.confidence_hierarchical,
                active_question_count=len(ids),
                overdue_question_count=sum(qid in overdue_ids for qid in ids),
                recurrence=tuple(RecurrenceEvidence(qid, *recurrence[qid]) for qid in ids),
                decline=tuple(DeclineEvidence(qid, *decline[qid]) for qid in ids),
            )
        )
        rows.append(SubjectPriority(subject, result))
    by_id = {row.subject.id: row for row in rows}
    ranked = tuple(
        by_id[item.subject_id] for item in rank_priorities(tuple(row.result for row in rows))
    )
    collecting = tuple(row for row in rows if row.result.score is None)
    return PriorityList(ranked, collecting, today)
