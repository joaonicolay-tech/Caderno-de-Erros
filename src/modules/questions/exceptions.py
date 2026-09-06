"""Falhas controladas do catálogo interno de origem."""


class OriginCatalogError(Exception):
    """Base para falhas esperadas dos casos de uso de origem."""


class OriginCatalogValidationError(OriginCatalogError, ValueError):
    """Um valor não satisfaz as regras documentadas de origem."""


class OriginCatalogNotFoundError(OriginCatalogError, LookupError):
    """A referência não existe no Workspace ou não pode ser revelada."""


class OriginCatalogStateConflictError(OriginCatalogError, RuntimeError):
    """A referência existe, mas seu estado impede a operação."""


class OriginCatalogConcurrencyError(OriginCatalogError, RuntimeError):
    """A referência mudou depois da versão apresentada ao chamador."""
