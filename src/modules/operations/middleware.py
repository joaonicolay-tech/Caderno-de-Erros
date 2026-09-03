"""Fronteira HTTP local e propagação de correlação."""

from collections.abc import Callable
from ipaddress import ip_address

from django.http import HttpRequest, HttpResponse, JsonResponse

from .correlation import correlation_scope
from .events import EventCode, EventOutcome
from .structured_logging import emit_event

CORRELATION_HEADER = "X-Correlation-ID"


def _is_loopback(value: str) -> bool:
    try:
        return ip_address(value).is_loopback
    except ValueError:
        return False


class LocalCorrelationMiddleware:
    """Recuse clientes não locais e delimite a correlação de cada requisição."""

    sync_capable = True
    async_capable = False

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        supplied_id = request.headers.get(CORRELATION_HEADER)
        with correlation_scope(supplied_id) as correlation_id:
            if not _is_loopback(request.META.get("REMOTE_ADDR", "")):
                emit_event(
                    EventCode.LOCAL_ACCESS_REJECTED,
                    operation="http.local_access",
                    outcome=EventOutcome.REJECTED,
                    level=30,
                    context={"reason": "non_loopback_client"},
                )
                response: HttpResponse = JsonResponse({"status": "forbidden"}, status=403)
            else:
                response = self.get_response(request)
            response[CORRELATION_HEADER] = correlation_id
            return response
