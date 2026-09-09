"""Contextos efêmeros locais: nenhum conteúdo de estudo sai deste armazenamento."""

import secrets
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from threading import RLock


class InitialAttemptError(ValueError):
    """Falha segura de validação, conflito ou persistência."""

    def __init__(self, code: str = "CONFLICT") -> None:
        self.code = code
        super().__init__(code)


@dataclass(frozen=True)
class AnswerContext:
    """Avaliação imutável vinculada à identidade e versão apresentadas."""

    actor_id: uuid.UUID
    session: str
    workspace_id: uuid.UUID
    workspace_version: int
    question_id: uuid.UUID
    revision_id: uuid.UUID
    lock_version: int
    alternative_id: uuid.UUID
    is_correct: bool
    evaluated_at: datetime
    timezone_name: str
    review_id: uuid.UUID | None = None
    review_lock_version: int | None = None
    nonce: str = field(default_factory=lambda: secrets.token_urlsafe(32))

    @property
    def expires_at(self) -> datetime:
        return self.evaluated_at + timedelta(minutes=15)


class ContextStore:
    """Memória de um processo local; reinício invalida contextos sem criar fatos.

    O lock protege somente operações de memória, nunca espera pelo SQLite.
    Expurgos ocorrem em cada acesso; um limite impede crescimento ilimitado.
    """

    def __init__(self) -> None:
        self._lock = RLock()
        self._contexts: dict[str, AnswerContext] = {}
        self._claims: dict[str, tuple[uuid.UUID, str]] = {}

    def _purge(self, now: datetime) -> None:
        for token, context in list(self._contexts.items()):
            if now >= context.expires_at:
                self._contexts.pop(token)
                self._claims.pop(token, None)

    def put(self, context: AnswerContext) -> str:
        with self._lock:
            self._purge(context.evaluated_at)
            if len(self._contexts) >= 4096:
                raise InitialAttemptError("CONTEXT_CAPACITY")
            token = secrets.token_urlsafe(32)
            self._contexts[token] = context
            return token

    def get(self, token: str, now: datetime) -> AnswerContext:
        with self._lock:
            self._purge(now)
            context = self._contexts.get(token)
            if context is None:
                raise InitialAttemptError("INVALID_CONTEXT")
            return context

    def claim(self, token: str, key: uuid.UUID, request_hash: str, now: datetime) -> None:
        with self._lock:
            self.get(token, now)
            previous = self._claims.get(token)
            if previous is not None and previous != (key, request_hash):
                raise InitialAttemptError()
            self._claims[token] = (key, request_hash)

    def discard(self, token: str) -> None:
        with self._lock:
            self._contexts.pop(token, None)
            self._claims.pop(token, None)


contexts = ContextStore()
