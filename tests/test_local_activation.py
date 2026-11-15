"""Activation schema, native privacy and fixed-role isolation; no live release."""

import copy
from typing import Any

import pytest

from shared.infrastructure import local_activation as activation
from shared.infrastructure import local_boundary as boundary


def document_fixture() -> tuple[dict[str, Any], dict[str, Any]]:
    expected = {
        "code_root": str(boundary.ROOT / "installed/release-002/code"),
        "owner_sid": "UNIT_ONLY_SID",
        "release_zip_sha256": "1" * 64,
        "release_manifest_sha256": "2" * 64,
    }
    document = {
        **expected,
        "schema": "CEI_LOCAL_RELEASE_AUTHORIZATION_1",
        "purpose": "REAL_USE",
        "approved": True,
        "source": "USER_MESSAGE_THIS_CHAT",
        "decision_text": "SYNTHETIC_UNIT_FIXTURE_NOT_A_REAL_RELEASE",
        "decision_reference": "UNIT_ONLY",
    }
    return document, expected


@pytest.mark.parametrize(
    "missing",
    [
        "schema",
        "purpose",
        "approved",
        "source",
        "decision_text",
        "decision_reference",
        "code_root",
        "owner_sid",
        "release_zip_sha256",
        "release_manifest_sha256",
    ],
)
def test_real_activation_requires_every_exact_field(missing: str) -> None:
    document, expected = document_fixture()
    activation.validate_activation_document(document, expected)
    del document[missing]
    with pytest.raises(boundary.BoundaryError):
        activation.validate_activation_document(document, expected)


def test_numeric_approval_and_wrong_artifact_do_not_authorize_release() -> None:
    document, expected = document_fixture()
    document["approved"] = 1
    with pytest.raises(boundary.BoundaryError):
        activation.validate_activation_document(document, expected)
    document, expected = document_fixture()
    document["release_zip_sha256"] = "3" * 64
    with pytest.raises(boundary.BoundaryError):
        activation.validate_activation_document(document, expected)


def test_synthetic_authorization_cannot_be_used_as_real_owner_release() -> None:
    document, expected = document_fixture()
    document.update(purpose="SYNTHETIC_REHEARSAL", source="EXECUTOR_SYNTHETIC_TEST")
    activation.validate_activation_document(document, expected, synthetic=True)
    with pytest.raises(boundary.BoundaryError):
        activation.validate_activation_document(document, expected)


def test_private_acl_requires_exact_trusted_owners_and_rights() -> None:
    owner = "S-1-5-21-UNIT"
    aces = [
        {"sid": sid, "type": 0, "mask": 0x1F01FF} for sid in (owner, "S-1-5-18", "S-1-5-32-544")
    ]
    activation.validate_private_aces(owner, aces, owner)
    for field, value in (("sid", "S-1-1-0"), ("type", 1), ("mask", 0x1301BF)):
        bad = copy.deepcopy(aces)
        bad[0][field] = value
        with pytest.raises(boundary.BoundaryError):
            activation.validate_private_aces(owner, bad, owner)
    with pytest.raises(boundary.BoundaryError):
        activation.validate_private_aces("S-1-5-21-OTHER", aces, owner)


def test_candidate_or_cross_role_marker_is_rejected_before_private_reads() -> None:
    value = {
        "database_slot": "user/cei.sqlite3",
        "secret_slot": "user/secret.txt",  # pragma: allowlist secret -- fixed private slot path, not a credential
    }
    with pytest.raises(boundary.BoundaryError, match="instalação"):
        activation.activation_paths(value, boundary.ROOT / "candidate")
    value.update(activation_purpose="SYNTHETIC_REHEARSAL", data_origin="GENERATED_SYNTHETIC")
    with pytest.raises(boundary.BoundaryError, match="sintético"):
        activation.activation_paths(value, boundary.ROOT / "installed/release-002/code")
    with pytest.raises(boundary.BoundaryError, match="Slots"):
        activation.activation_paths(
            value, boundary.ROOT / "validation/s10-activation-rehearsal-002/code"
        )


def test_real_mode_never_admits_validation_or_test_database(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(boundary, "_REAL_USE", True)
    monkeypatch.setattr(boundary, "_USER_ACTIVE", True)
    assert (
        boundary.lexical(boundary.ROOT / "user/cei.sqlite3") == boundary.ROOT / "user/cei.sqlite3"
    )
    with pytest.raises(boundary.BoundaryError):
        boundary.lexical(boundary.ROOT / "validation/unqualified.sqlite3")
    with pytest.raises(boundary.BoundaryError, match="Perfil de teste"):
        boundary.database_path(test=True)
