"""Catálogo padrão e bootstrap completo exigidos por CT-129."""

import uuid
from pathlib import Path
from typing import Any

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from modules.accounts.models import User, Workspace
from modules.accounts.services import LOCAL_USER_ID, LOCAL_WORKSPACE_ID
from modules.errors.catalog import STANDARD_ERROR_CATEGORIES, normalize_name_key
from modules.errors.models import ErrorCategory, ErrorCategoryCode
from modules.errors.services import seed_standard_error_categories
from shared.application.bootstrap import bootstrap_local_workspace

EXPECTED_CATEGORIES = {
    definition.code: (definition.display_name, definition.description)
    for definition in STANDARD_ERROR_CATEGORIES
}
PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.django_db
def test_complete_bootstrap_creates_exactly_the_canonical_ten_categories() -> None:
    result = bootstrap_local_workspace(timezone_id="America/Sao_Paulo")

    persisted = {
        category.code: (category.display_name, category.description)
        for category in ErrorCategory.objects.filter(workspace=result.workspace)
    }
    assert result.user.id == LOCAL_USER_ID
    assert result.workspace.id == LOCAL_WORKSPACE_ID
    assert len(result.categories) == 10
    assert persisted == EXPECTED_CATEGORIES
    assert set(persisted) == set(ErrorCategoryCode.values)


def test_catalog_exactly_matches_controlled_errata() -> None:
    requirements = (
        PROJECT_ROOT / "docs" / "Caderno_de_Erros_Inteligente_Etapa_3_Requisitos_Funcionais.md"
    ).read_text(encoding="utf-8")
    documented: dict[str, tuple[str, str]] = {}
    for line in requirements.splitlines():
        if line.startswith("| `") and line.count("|") == 4:
            _, raw_code, name, description, _ = line.split("|")
            code = raw_code.strip().strip("`")
            if code in ErrorCategoryCode.values:
                documented[code] = (name.strip(), description.strip())

    assert documented == EXPECTED_CATEGORIES


@pytest.mark.django_db
def test_repeated_bootstrap_does_not_duplicate_and_preserves_codes_and_ids() -> None:
    first = bootstrap_local_workspace(timezone_id="America/Sao_Paulo")
    first_ids = {category.code: category.id for category in first.categories}
    second = bootstrap_local_workspace(timezone_id="America/Sao_Paulo")

    assert second.created is False
    assert User.objects.count() == 1
    assert Workspace.objects.count() == 1
    assert ErrorCategory.objects.count() == 10
    assert {category.code: category.id for category in second.categories} == first_ids


@pytest.mark.django_db
def test_seed_updates_mutable_texts_but_preserves_canonical_code() -> None:
    result = bootstrap_local_workspace(timezone_id="America/Sao_Paulo")
    category = ErrorCategory.objects.get(workspace=result.workspace, code="CONCEPTUAL")
    category.display_name = "Texto anterior"
    category.description = "Descrição anterior"
    category.save()

    seed_standard_error_categories(result.workspace)
    category.refresh_from_db()
    expected_name, expected_description = EXPECTED_CATEGORIES["CONCEPTUAL"]
    assert category.code == "CONCEPTUAL"
    assert category.display_name == expected_name
    assert category.name_key == normalize_name_key(expected_name)
    assert category.description == expected_description


@pytest.mark.django_db
def test_canonical_code_cannot_be_changed_or_duplicated_in_workspace() -> None:
    result = bootstrap_local_workspace(timezone_id="America/Sao_Paulo")
    category = ErrorCategory.objects.get(workspace=result.workspace, code="CONCEPTUAL")
    category.code = "OTHER"
    with pytest.raises(ValidationError, match="imutável"):
        category.save()
    with pytest.raises(ValidationError, match="imutável"):
        ErrorCategory.objects.filter(pk=category.pk).update(code="OTHER")

    with pytest.raises(IntegrityError), transaction.atomic():
        ErrorCategory.objects.bulk_create(
            [
                ErrorCategory(
                    workspace=result.workspace,
                    code="CONCEPTUAL",
                    display_name="Duplicada",
                    name_key="duplicada",
                    description="Não deve persistir.",
                )
            ]
        )


@pytest.mark.django_db(transaction=True)
def test_categories_are_isolated_by_workspace_and_require_valid_parent() -> None:
    local = bootstrap_local_workspace(timezone_id="America/Sao_Paulo")
    another_user = User.objects.create_user(email="outro@example.test")
    another_workspace = Workspace.objects.create(
        owner_user=another_user,
        name="Outro espaço",
        timezone_name="UTC",
    )
    seed_standard_error_categories(another_workspace)

    assert ErrorCategory.objects.filter(workspace=local.workspace).count() == 10
    assert ErrorCategory.objects.filter(workspace=another_workspace).count() == 10
    assert ErrorCategory.objects.count() == 20

    with pytest.raises(IntegrityError), transaction.atomic():
        ErrorCategory.objects.bulk_create(
            [
                ErrorCategory(
                    workspace_id=uuid.uuid4(),
                    code="CONCEPTUAL",
                    display_name="Órfã",
                    name_key="órfã",
                    description="Não deve persistir.",
                )
            ]
        )


@pytest.mark.django_db
def test_standard_category_cannot_be_deleted_in_isolation() -> None:
    result = bootstrap_local_workspace(timezone_id="America/Sao_Paulo")

    with pytest.raises(ValidationError, match="não podem ser excluídas"):
        result.categories[0].delete()
    with pytest.raises(ValidationError, match="não podem ser excluídas"):
        ErrorCategory.objects.filter(workspace=result.workspace).delete()

    assert ErrorCategory.objects.filter(workspace=result.workspace).count() == 10


@pytest.mark.django_db
def test_complete_bootstrap_rolls_back_everything_when_seed_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original_update_or_create = ErrorCategory.objects.update_or_create
    calls = 0

    def fail_during_seed(*args: Any, **kwargs: Any) -> tuple[ErrorCategory, bool]:
        nonlocal calls
        calls += 1
        if calls == 5:
            raise RuntimeError("falha controlada no meio do seed")
        return original_update_or_create(*args, **kwargs)

    monkeypatch.setattr(ErrorCategory.objects, "update_or_create", fail_during_seed)

    with pytest.raises(RuntimeError, match="falha controlada"):
        bootstrap_local_workspace(timezone_id="America/Sao_Paulo")

    assert calls == 5
    assert User.objects.count() == 0
    assert Workspace.objects.count() == 0
    assert ErrorCategory.objects.count() == 0


@pytest.mark.django_db
def test_seed_creates_no_unrelated_domain_tables_or_records() -> None:
    bootstrap_local_workspace(timezone_id="America/Sao_Paulo")

    from django.db import connection

    project_tables = {
        name
        for name in connection.introspection.table_names()
        if name.startswith(("accounts_", "attempts_", "errors_", "reviews_"))
    }
    assert project_tables == {
        "accounts_user",
        "accounts_workspace",
        "attempts_attempt",
        "attempts_operationreceipt",
        "errors_error_category",
        "errors_errorclassification",
        "errors_errorclassificationrevision",
        "reviews_review",
        "reviews_reviewcycle",
    }
    for learning_table in project_tables - {
        "accounts_user",
        "accounts_workspace",
        "errors_error_category",
    }:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT COUNT(*) FROM {learning_table}")  # noqa: S608
            assert cursor.fetchone() == (0,)
