"""Smokes focais S8; sem antecipar a matriz integral S9."""

import io
import json
import zipfile
from collections.abc import Iterator
from datetime import UTC, datetime
from typing import cast

import pytest
from django.http import FileResponse
from django.test import Client
from django.urls import reverse
from pytest_django.fixtures import Settings

from modules.operations.integrity import run_integrity_check
from shared.infrastructure.local_boundary import ROOT
from tests.local_fixture import create_fixture


@pytest.mark.django_db(transaction=True)
def test_synthetic_lifecycle_checker_and_ui(
    caplog: pytest.LogCaptureFixture, settings: Settings
) -> None:
    fixture = create_fixture()
    checker = run_integrity_check(now=datetime(2026, 11, 9, 15, tzinfo=UTC))
    assert checker.total_findings == 0
    # O checker distingue contexto histórico ausente de violação: a fixture
    # fornece o oráculo de criação, sem ocultar os quatro LIMITED canônicos.
    assert checker.total_limited_verifications == 4
    assert {(x.invariant_id, x.reason_code) for x in checker.limited_verifications} == {
        ("REV-004", "TIMEZONE_CONTEXT_UNAVAILABLE")
    }
    client = Client(enforce_csrf_checks=True)
    page = client.get(
        reverse("questions:detail", kwargs={"question_id": fixture["question_ids"][0]})
    )
    assert page.status_code == 200
    assert b"<script>sentinela-local</script>" not in page.content
    assert b"&lt;script&gt;sentinela-local&lt;/script&gt;" in page.content
    assert (
        client.post(reverse("questions:quick-entry"), {"stem": "CSRF-SENTINEL"}).status_code == 403
    )
    assert (
        client.get(
            reverse("questions:detail", kwargs={"question_id": fixture["question_ids"][-1]})
        ).status_code
        == 404
    )
    assert any("INITIAL_CONFIRMED" in record.getMessage() for record in caplog.records)
    captured = json.dumps([record.__dict__ for record in caplog.records], default=str)
    assert "sentinela-local" not in captured
    assert "Diagnóstico gerado sinteticamente" not in captured
    assert settings.SECRET_KEY not in captured


def test_test_profile_database_and_uploads_are_confined(settings: Settings) -> None:
    assert str(settings.DATABASES["default"]["NAME"]).startswith(str(ROOT / "validation"))
    assert settings.FILE_UPLOAD_TEMP_DIR == str(ROOT / "validation" / "tmp")
    assert settings.DEBUG is False


@pytest.mark.django_db(transaction=True)
def test_export_ignores_foreign_workspace_reference_and_contains_only_local_records() -> None:
    fixture = create_fixture()
    client = Client(enforce_csrf_checks=True)
    url = reverse("data-management:portability")
    assert client.get(url).status_code == 200
    response = cast(
        FileResponse,
        client.post(
            url,
            {
                "action": "export",
                "workspace_id": fixture["secondary"],
                "csrfmiddlewaretoken": client.cookies["csrftoken"].value,
            },
        ),
    )
    assert response.status_code == 200
    data = b"".join(cast(Iterator[bytes], response.streaming_content))
    response.close()
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        documents = {
            name: json.loads(archive.read(name))
            for name in archive.namelist()
            if name.endswith(".json")
        }
    questions = documents["questions.json"]
    assert {row["id"] for row in questions} == set(fixture["question_ids"][:3])
    text = json.dumps(documents)
    assert fixture["secondary"] not in text
    assert fixture["question_ids"][-1] not in text
