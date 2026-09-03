"""Correlação transitória para requisições e operações técnicas."""

from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from uuid import UUID, uuid4

_correlation_id: ContextVar[str | None] = ContextVar("cei_correlation_id", default=None)


def current_correlation_id() -> str | None:
    """Retorne o identificador corrente sem criar estado persistente."""
    return _correlation_id.get()


def new_correlation_id() -> str:
    """Crie um UUID aleatório adequado para correlação técnica."""
    return str(uuid4())


def normalized_correlation_id(candidate: str | None) -> str:
    """Aceite somente UUID canônico; entrada inválida recebe um novo ID."""
    if candidate:
        try:
            return str(UUID(candidate))
        except (ValueError, AttributeError):
            pass
    return new_correlation_id()


@contextmanager
def correlation_scope(candidate: str | None = None) -> Iterator[str]:
    """Propague o contexto existente ou delimite um novo identificador."""
    existing = current_correlation_id()
    if candidate is None and existing is not None:
        yield existing
        return

    correlation_id = normalized_correlation_id(candidate)
    token = _correlation_id.set(correlation_id)
    try:
        yield correlation_id
    finally:
        _correlation_id.reset(token)
