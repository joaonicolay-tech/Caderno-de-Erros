"""Falhas públicas e sanitizadas de backup e restauração."""


class DataManagementError(Exception):
    """Base para erros operacionais que podem ser exibidos sem dados privados."""


class BackupCreationError(DataManagementError):
    """O snapshot consistente não pôde ser concluído."""


class BackupValidationError(DataManagementError):
    """O artefato ou o manifesto não passou nas validações."""


class RestoreError(DataManagementError):
    """A restauração isolada não pôde ser validada."""


class RestoreIntegrityError(RestoreError):
    """Resultado impeditivo S5 preservado pela interface de restore."""

    def __init__(self, message: str, *, exit_code: int) -> None:
        super().__init__(message)
        self.exit_code = exit_code
