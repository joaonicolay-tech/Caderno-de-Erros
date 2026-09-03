"""Erros controlados dos casos de uso de Workspace."""


class WorkspaceAccessDenied(LookupError):
    """O espaço não pertence à identidade que executa a operação."""


class WorkspaceConcurrencyError(RuntimeError):
    """O Workspace foi alterado depois da versão apresentada ao estudante."""


class LocalBootstrapConflict(RuntimeError):
    """A identidade determinística local colide com dados inconsistentes."""
