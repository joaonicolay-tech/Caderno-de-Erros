"""Exponha o invariant checker read-only como comando operacional Django."""

import logging
from typing import Any

from django.core.management.base import BaseCommand, CommandError, CommandParser

from modules.operations.correlation import correlation_scope
from modules.operations.events import EventCode, EventOutcome
from modules.operations.integrity import (
    DEFAULT_FINDING_LIMIT,
    MAX_FINDING_LIMIT,
    IntegrityCheckOperationalError,
    IntegrityCheckResult,
    InvariantSeverity,
    run_integrity_check,
)
from modules.operations.structured_logging import emit_event

EXIT_FINDINGS = 2
EXIT_OPERATIONAL_FAILURE = 3


class Command(BaseCommand):
    """Execute diagnóstico sanitizado sem reparar ou persistir qualquer dado."""

    help = "Verifica invariantes do banco local em modo read-only; nunca repara dados."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--limit",
            type=int,
            default=DEFAULT_FINDING_LIMIT,
            help=f"Máximo de findings exibidos (1..{MAX_FINDING_LIMIT}).",
        )
        parser.add_argument("--correlation-id", help="UUID técnico opcional para correlação.")

    def handle(self, *args: Any, **options: Any) -> None:
        del args
        finding_limit = int(options["limit"])
        if not 1 <= finding_limit <= MAX_FINDING_LIMIT:
            raise CommandError(
                f"--limit deve estar entre 1 e {MAX_FINDING_LIMIT}.",
                returncode=EXIT_OPERATIONAL_FAILURE,
            )
        with correlation_scope(options.get("correlation_id")):
            emit_event(
                EventCode.INTEGRITY_CHECK_STARTED,
                operation="integrity.check",
                outcome=EventOutcome.STARTED,
                context={"finding_limit": finding_limit},
            )
            try:
                result = run_integrity_check(finding_limit=finding_limit)
            except IntegrityCheckOperationalError as error:
                emit_event(
                    EventCode.INTEGRITY_CHECK_FAILED,
                    operation="integrity.check",
                    outcome=EventOutcome.FAILED,
                    level=logging.ERROR,
                    context={
                        "error_code": "INTEGRITY_CHECK_OPERATIONAL_FAILURE",
                        "error_type": type(error).__name__,
                    },
                )
                raise CommandError(
                    "O checker não conseguiu concluir. Tente novamente em ambiente seguro e "
                    "consulte os logs operacionais sanitizados.",
                    returncode=EXIT_OPERATIONAL_FAILURE,
                ) from error

            self._render_result(result)
            context = {
                "checks_executed": result.checks_executed,
                "total_findings": result.total_findings,
                "critical_findings": self._severity_count(result, InvariantSeverity.CRITICAL),
                "error_findings": self._severity_count(result, InvariantSeverity.ERROR),
                "findings_shown": len(result.findings),
                "queries_executed": result.queries_executed,
            }
            if result.has_blocking_findings:
                emit_event(
                    EventCode.INTEGRITY_CHECK_FINDINGS,
                    operation="integrity.check",
                    outcome=EventOutcome.FAILED,
                    level=logging.ERROR,
                    context=context,
                )
                raise CommandError(
                    "Foram encontradas inconsistências impeditivas. Não continue restore ou "
                    "promoção antes de investigação e correção autorizadas.",
                    returncode=EXIT_FINDINGS,
                )
            emit_event(
                EventCode.INTEGRITY_CHECK_SUCCEEDED,
                operation="integrity.check",
                outcome=EventOutcome.SUCCEEDED,
                context=context,
            )

    def _render_result(self, result: IntegrityCheckResult) -> None:
        status = "BLOCKED" if result.has_blocking_findings else "HEALTHY"
        critical = self._severity_count(result, InvariantSeverity.CRITICAL)
        errors = self._severity_count(result, InvariantSeverity.ERROR)
        self.stdout.write(f"Integrity checker: {status}")
        self.stdout.write(f"Checks executados: {result.checks_executed}")
        self.stdout.write(
            f"Findings: {result.total_findings} "
            f"(CRITICAL={critical}, ERROR={errors}, exibidos={len(result.findings)})"
        )
        for finding in result.findings:
            self.stdout.write(
                f"[{finding.severity.value}] {finding.invariant_id} "
                f"{finding.entity_type} id={finding.technical_id} - {finding.message}"
            )
            if finding.technical_context:
                context = ", ".join(f"{key}={value}" for key, value in finding.technical_context)
                self.stdout.write(f"  contexto: {context}")
            self.stdout.write(f"  ação: {finding.operational_action}")
        if result.truncated:
            self.stdout.write(
                f"Saída limitada: {len(result.findings)} de {result.total_findings} findings "
                "exibidos; a contagem total foi preservada."
            )
        self.stdout.write("Modo read-only: conexão SQLite mode=ro; nenhum reparo foi executado.")

    @staticmethod
    def _severity_count(result: IntegrityCheckResult, severity: InvariantSeverity) -> int:
        return dict(result.severity_counts).get(severity, 0)
