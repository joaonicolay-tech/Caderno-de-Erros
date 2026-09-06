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


class QuestionCatalogError(Exception):
    """Base para falhas esperadas dos comandos do catálogo de questões."""


class QuestionCatalogValidationError(QuestionCatalogError, ValueError):
    """O agregado informado viola uma regra do catálogo de questões."""


class QuestionCatalogNotFoundError(QuestionCatalogError, LookupError):
    """A questão não existe no Workspace ou não pode ser revelada."""


class QuestionCatalogStateConflictError(QuestionCatalogError, RuntimeError):
    """O estado atual da questão impede o comando solicitado."""


class QuestionCatalogConcurrencyError(QuestionCatalogError, RuntimeError):
    """A questão mudou depois da versão apresentada ao chamador."""
