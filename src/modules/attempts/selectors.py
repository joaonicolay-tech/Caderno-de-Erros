"""Resolução centralizada e finita do grafo de substituição de Attempt."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from django.db.models import QuerySet

from .models import Attempt, AttemptStatus


class AttemptChainError(RuntimeError):
    """O grafo persistido não possui uma cadeia determinística válida."""


@dataclass(frozen=True, slots=True)
class AttemptChain:
    attempts: tuple[Attempt, ...]
    requested_id: uuid.UUID

    @property
    def tip(self) -> Attempt | None:
        candidate = self.attempts[-1]
        return candidate if candidate.status == AttemptStatus.VALID else None

    @property
    def root(self) -> Attempt:
        return self.attempts[0]


def resolve_attempt_chain(
    *,
    workspace_id: uuid.UUID,
    attempt_id: uuid.UUID,
    for_update: bool = False,
) -> AttemptChain:
    """Carregue o contexto uma vez e resolva ancestrais/sucessoras em memória."""
    seed = (
        Attempt.objects.filter(pk=attempt_id, workspace_id=workspace_id)
        .only("id", "question_id")
        .first()
    )
    if seed is None:
        raise AttemptChainError("Attempt não disponível neste Workspace.")
    queryset: QuerySet[Attempt] = Attempt.objects.filter(
        workspace_id=workspace_id,
        question_id=seed.question_id,
    ).select_related("question_revision", "selected_alternative", "review")
    if for_update:
        queryset = queryset.select_for_update()
    rows = list(queryset.order_by("occurred_at", "created_at", "id"))
    by_id = {row.id: row for row in rows}
    requested = by_id.get(attempt_id)
    if requested is None:
        raise AttemptChainError("Attempt não disponível neste Workspace.")

    successors: dict[uuid.UUID, list[Attempt]] = {}
    for row in rows:
        if row.replaces_attempt_id is not None:
            successors.setdefault(row.replaces_attempt_id, []).append(row)
    if any(len(items) != 1 for items in successors.values()):
        raise AttemptChainError("A cadeia possui mais de uma sucessora direta.")

    prefix: list[Attempt] = []
    cursor = requested
    visited: set[uuid.UUID] = set()
    while cursor.replaces_attempt_id is not None:
        if cursor.id in visited:
            raise AttemptChainError("A cadeia de substituição contém ciclo.")
        visited.add(cursor.id)
        parent = by_id.get(cursor.replaces_attempt_id)
        if parent is None:
            raise AttemptChainError("A cadeia referencia Attempt fora do contexto.")
        prefix.append(parent)
        cursor = parent
    prefix.reverse()

    chain = [*prefix, requested]
    cursor = requested
    seen = {row.id for row in chain}
    while cursor.id in successors:
        successor = successors[cursor.id][0]
        if successor.id in seen:
            raise AttemptChainError("A cadeia de substituição contém ciclo.")
        seen.add(successor.id)
        if (
            successor.workspace_id != cursor.workspace_id
            or successor.question_id != cursor.question_id
            or successor.question_revision_id != cursor.question_revision_id
            or successor.review_id != cursor.review_id
            or successor.attempt_type != cursor.attempt_type
        ):
            raise AttemptChainError("A sucessora atravessa o contexto da Attempt.")
        if cursor.status != AttemptStatus.VOIDED:
            raise AttemptChainError("Somente Attempt anulada pode possuir sucessora.")
        chain.append(successor)
        cursor = successor
    if any(row.status == AttemptStatus.VALID for row in chain[:-1]):
        raise AttemptChainError("A cadeia possui ponta válida não terminal.")
    return AttemptChain(tuple(chain), attempt_id)
