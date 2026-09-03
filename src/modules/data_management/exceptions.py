"""Falhas públicas e sanitizadas de backup e restauração."""


class DataManagementError(Exception):
    """Base para erros operacionais que podem ser exibidos sem dados privados."""


class BackupCreationError(DataManagementError):
    """O snapshot consistente não pôde ser concluído."""


class BackupValidationError(DataManagementError):
    """O artefato ou o manifesto não passou nas validações."""


class RestoreError(DataManagementError):
    """A restauração isolada não pôde ser validada."""
