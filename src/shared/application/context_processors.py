"""Template context processors for shared application identity."""

from django.http import HttpRequest

from .version import PRODUCT_VERSION


def product_identity(request: HttpRequest) -> dict[str, str]:
    """Expose the canonical human-facing product version to shared templates."""
    del request
    return {"product_version": PRODUCT_VERSION}
