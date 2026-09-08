"""Erros explícitos da fundação de idempotência."""


class IdempotencyConflictError(ValueError):
    """A mesma chave foi reapresentada com um payload lógico diferente."""
