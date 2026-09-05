"""Falhas de domínio controladas da taxonomia."""


class TaxonomyError(Exception):
    """Base para falhas esperadas dos casos de uso de taxonomia."""


class TaxonomyValidationError(TaxonomyError, ValueError):
    """Um valor não satisfaz as regras documentadas da taxonomia."""


class TaxonomyDuplicateNameError(TaxonomyValidationError):
    """Já existe um item ativo com o mesmo nome normalizado no escopo."""


class TaxonomyHierarchyError(TaxonomyValidationError):
    """A relação pai-filho não pertence à mesma hierarquia."""


class TaxonomyNotFoundError(TaxonomyError, LookupError):
    """O item não existe no Workspace informado ou não pode ser revelado."""


class TaxonomyStateConflictError(TaxonomyError, RuntimeError):
    """O item existe, mas seu estado atual impede a operação."""


class TaxonomyConcurrencyError(TaxonomyError, RuntimeError):
    """O item mudou depois da versão apresentada ao estudante."""
