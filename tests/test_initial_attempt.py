"""CT-013-018/021/022/093/100/101: E2 sintética em banco descartável."""

import json
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from threading import Barrier
from typing import Any
from unittest.mock import Mock

import pytest
from django.db import OperationalError, close_old_connections
from django.test import Client
from django.urls import reverse

from modules.accounts.models import User, Workspace
from modules.attempts.context import ContextStore, InitialAttemptError
from modules.attempts.models import Attempt, OperationReceipt
from modules.attempts.services import AttemptService
from modules.errors.models import ErrorCategoryCode, ErrorClassification
from modules.errors.services import seed_standard_error_categories
from modules.operations.structured_logging import StructuredJsonFormatter
from modules.questions.models import Question
from modules.questions.services import create_active
from modules.reviews.models import Review, ReviewCycle
from modules.reviews.services import CompleteReviewService
from modules.taxonomy.services import create_discipline, create_subject
from shared.application.bootstrap import bootstrap_local_workspace
from shared.domain.time import FixedClock, Instant


def question(workspace: Workspace, suffix: str = "") -> Question:
    discipline = create_discipline(workspace_id=workspace.id, name=f"Disciplina{suffix}")
    subject = create_subject(
        workspace_id=workspace.id, discipline_id=discipline.id, name="Assunto sintético"
    )
    return create_active(
        workspace_id=workspace.id,
        discipline_id=discipline.id,
        subject_id=subject.id,
        stem="<script>conteudo-sintetico</script>",
        alternatives=["<b>opcao-um</b>", "opcao-dois"],
        correct_alternative_position=2,
        explanation="EXPLICACAO-RESERVADA",
        trap_note="PEGADINHA-RESERVADA",
    )


@pytest.fixture
def setup(db: None) -> tuple[AttemptService, Question, Workspace]:
    workspace = bootstrap_local_workspace(timezone_id="America/Sao_Paulo").workspace
    service = AttemptService(
        actor_id=workspace.owner_user_id,
        workspace_id=workspace.id,
        session="sessao-sintetica",
        store=ContextStore(),
        clock=FixedClock(Instant(datetime(2026, 9, 9, 2, 59, tzinfo=UTC))),
    )
    return service, question(workspace), workspace


def evaluate(service: AttemptService, item: Question, correct: bool = False) -> str:
    presentation = service.presentation(item.id)
    return service.evaluate(
        question_id=item.id,
        revision_id=presentation["revision_id"],
        lock_version=presentation["lock_version"],
        alternative_id=presentation["alternatives"][int(correct)][0],
    )


def counts() -> tuple[int, ...]:
    return tuple(
        model.objects.count()
        for model in (Attempt, ErrorClassification, ReviewCycle, Review, OperationReceipt)
    )


@pytest.mark.parametrize("correct", [True, False])
def test_initial_atomic_facts_and_replay(
    setup: tuple[AttemptService, Question, Workspace], correct: bool
) -> None:
    service, item, workspace = setup
    token = evaluate(service, item, correct)
    assert counts() == (0, 0, 0, 0, 0)
    assert service.feedback(token)["is_correct"] is correct
    key = uuid.uuid4()
    category = workspace.error_categories.get(code=ErrorCategoryCode.OTHER)
    kwargs: dict[str, Any] = (
        {}
        if correct
        else {"category_id": category.id, "other_description": "  diagnostico   sintetico  "}
    )
    receipt = service.confirm(token=token, key=key, **kwargs)
    assert service.confirm(token=token, key=key, **kwargs).id == receipt.id
    assert counts() == ((1, 0, 0, 0, 1) if correct else (1, 1, 1, 1, 1))
    attempt = Attempt.objects.get()
    assert attempt.is_correct is correct
    assert attempt.local_date.isoformat() == "2026-09-08"
    assert attempt.workspace_id == workspace.id
    if not correct:
        review = Review.objects.get()
        assert review.stage_code == "D1" and review.state == "PENDING"
        assert review.current_due_date.isoformat() == "2026-09-09"
        assert ErrorClassification.objects.get().other_description == "diagnostico sintetico"
    with pytest.raises(InitialAttemptError):
        service.confirm(token=token, key=uuid.uuid4(), **kwargs)
    with pytest.raises(InitialAttemptError):
        service.feedback(token)
    with pytest.raises(InitialAttemptError):
        evaluate(service, item)


def test_context_ttl_cancel_bindings_and_tampering(
    setup: tuple[AttemptService, Question, Workspace],
) -> None:
    service, item, workspace = setup
    token = evaluate(service, item)
    context = service.context(token)
    clock = service.clock
    assert isinstance(clock, FixedClock)
    clock.advance(timedelta(minutes=14, seconds=59))
    assert service.context(token).expires_at == context.expires_at
    for actor, ws, session in [
        (uuid.uuid4(), workspace.id, service.session),
        (service.actor_id, uuid.uuid4(), service.session),
        (service.actor_id, workspace.id, "outra-sessao"),
    ]:
        crossed = AttemptService(
            actor_id=actor, workspace_id=ws, session=session, store=service.store, clock=clock
        )
        with pytest.raises(InitialAttemptError):
            crossed.context(token)
    with pytest.raises(InitialAttemptError):
        service.context(token + "x")
    clock.advance(timedelta(seconds=1))
    with pytest.raises(InitialAttemptError):
        service.context(token)
    token = evaluate(service, item)
    service.cancel(token)
    with pytest.raises(InitialAttemptError):
        service.context(token)
    assert counts() == (0, 0, 0, 0, 0)


def test_validation_and_divergent_payload(
    setup: tuple[AttemptService, Question, Workspace],
) -> None:
    service, item, workspace = setup
    token = evaluate(service, item)
    other = workspace.error_categories.get(code="OTHER")
    for category_id, description in [
        (None, ""),
        (other.id, " \n "),
        (uuid.uuid4(), "x"),
        (other.id, "x" * 501),
    ]:
        with pytest.raises(InitialAttemptError):
            service.confirm(
                token=token,
                key=uuid.uuid4(),
                category_id=category_id,
                other_description=description,
            )
    assert counts() == (0, 0, 0, 0, 0)
    key = uuid.uuid4()
    service.confirm(token=token, key=key, category_id=other.id, other_description="original")
    with pytest.raises(InitialAttemptError):
        service.confirm(token=token, key=key, category_id=other.id, other_description="divergente")
    assert counts() == (1, 1, 1, 1, 1)


@pytest.mark.parametrize(
    "model", [Attempt, ErrorClassification, ReviewCycle, Review, OperationReceipt]
)
def test_rollback_at_every_error_boundary(
    setup: tuple[AttemptService, Question, Workspace],
    monkeypatch: pytest.MonkeyPatch,
    model: Any,
) -> None:
    service, item, workspace = setup
    token = evaluate(service, item)
    key = uuid.uuid4()
    category = workspace.error_categories.get(code="ATTENTION")
    original = model.save

    def failing_save(self: Any, *args: Any, **kwargs: Any) -> None:
        original(self, *args, **kwargs)
        raise OperationalError("injected failure")

    with monkeypatch.context() as patch:
        patch.setattr(model, "save", failing_save)
        with pytest.raises(InitialAttemptError, match="PERSISTENCE_FAILURE"):
            service.confirm(token=token, key=key, category_id=category.id)
    assert counts() == (0, 0, 0, 0, 0)
    item.refresh_from_db()
    assert item.lock_version == service.context(token).lock_version
    with pytest.raises(InitialAttemptError):
        service.confirm(token=token, key=uuid.uuid4(), category_id=category.id)
    service.confirm(token=token, key=key, category_id=category.id)
    assert counts() == (1, 1, 1, 1, 1)


@pytest.mark.parametrize("message, calls", [("database is locked", 2), ("disk error", 1)])
def test_sqlite_retry_and_correct_rollback(
    setup: tuple[AttemptService, Question, Workspace],
    monkeypatch: pytest.MonkeyPatch,
    message: str,
    calls: int,
) -> None:
    service, item, _ = setup
    token = evaluate(service, item, True)
    failure = Mock(side_effect=OperationalError(message))
    monkeypatch.setattr(service, "_receipt", failure)
    with pytest.raises(InitialAttemptError, match="PERSISTENCE_FAILURE"):
        service.confirm(token=token, key=uuid.uuid4())
    assert failure.call_count == calls
    assert counts() == (0, 0, 0, 0, 0)


def test_versions_alternative_status_and_owner(
    setup: tuple[AttemptService, Question, Workspace],
) -> None:
    service, item, workspace = setup
    data = service.presentation(item.id)
    for revision, version, alternative in [
        (uuid.uuid4(), item.lock_version, data["alternatives"][0][0]),
        (data["revision_id"], 999, data["alternatives"][0][0]),
        (data["revision_id"], item.lock_version, uuid.uuid4()),
    ]:
        with pytest.raises(InitialAttemptError):
            service.evaluate(
                question_id=item.id,
                revision_id=revision,
                lock_version=version,
                alternative_id=alternative,
            )
    token = evaluate(service, item, True)
    with pytest.raises(InitialAttemptError):
        service.confirm(token=token, key=uuid.uuid4(), category_id=uuid.uuid4())
    Question.objects.filter(pk=item.id).update(lock_version=item.lock_version + 1)
    with pytest.raises(InitialAttemptError):
        service.confirm(token=token, key=uuid.uuid4())
    Workspace.objects.filter(pk=workspace.id).update(lock_version=2)
    with pytest.raises(InitialAttemptError):
        service.feedback(token)
    User.objects.filter(pk=service.actor_id).update(status="DISABLED")
    with pytest.raises(InitialAttemptError):
        service.presentation(item.id)
    assert counts() == (0, 0, 0, 0, 0)


@pytest.mark.django_db(transaction=True)
def test_concurrent_distinct_keys_cannot_duplicate() -> None:
    workspace = bootstrap_local_workspace(timezone_id="America/Sao_Paulo").workspace
    item = question(workspace)
    services = [
        AttemptService(
            actor_id=workspace.owner_user_id,
            workspace_id=workspace.id,
            session=str(uuid.uuid4()),
            store=ContextStore(),
        )
        for _ in range(2)
    ]
    tokens = [evaluate(service, item) for service in services]
    category = workspace.error_categories.get(code="ATTENTION")
    barrier = Barrier(2)

    def confirm(index: int) -> str:
        close_old_connections()
        try:
            barrier.wait(timeout=10)
            services[index].confirm(token=tokens[index], key=uuid.uuid4(), category_id=category.id)
            return "success"
        except InitialAttemptError as error:
            return error.code
        finally:
            close_old_connections()

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(confirm, range(2)))
    assert results.count("success") == 1
    assert counts() == (1, 1, 1, 1, 1)


def test_http_protection_csrf_escape_and_confirmation(
    setup: tuple[AttemptService, Question, Workspace],
    caplog: pytest.LogCaptureFixture,
) -> None:
    _, item, _ = setup
    client = Client(enforce_csrf_checks=True)
    url = reverse("attempts:initial", args=[item.id])
    page = client.get(url)
    html = page.content.decode()
    assert page.status_code == 200
    assert "EXPLICACAO-RESERVADA" not in html and "PEGADINHA-RESERVADA" not in html
    assert "correct_alternative" not in html and "is_correct" not in html
    assert "<script>" not in html and "&lt;script&gt;" in html
    assert "no-store" in page["Cache-Control"]
    assert page["Referrer-Policy"] == "same-origin"
    answer = page.context["answer"]
    data = {
        "action": "answer",
        "revision_id": str(answer.initial["revision_id"]),
        "lock_version": answer.initial["lock_version"],
        "alternative_id": str(answer.fields["alternative_id"].choices[1][0]),
    }
    assert client.post(url, data).status_code == 403
    data["csrfmiddlewaretoken"] = client.cookies["csrftoken"].value
    assert client.post(url, {**data, "is_correct": "true"}).status_code == 400
    assert counts() == (0, 0, 0, 0, 0)
    page = client.post(url, data, follow=True)
    assert page.status_code == 200 and b"EXPLICACAO-RESERVADA" in page.content
    feedback_html = page.content.decode()
    assert "explanation-title" in feedback_html and "trap-note-title" in feedback_html
    assert "notes-title" not in feedback_html
    confirmation = page.context["confirmation"]
    token = confirmation.initial["token"]
    submit = {
        "action": "confirm",
        **confirmation.initial,
        "csrfmiddlewaretoken": client.cookies["csrftoken"].value,
    }
    confirmed = client.post(url, submit)
    assert confirmed.status_code == 200
    confirmed_html = confirmed.content.decode()
    assert "<h1>Resposta correta</h1>" in confirmed_html
    assert "VocÃª acertou. Sua tentativa foi registrada." in confirmed_html
    assert "nÃ£o entrou em ciclo de revisÃ£o" in confirmed_html
    assert "Responder outra questÃ£o" in confirmed_html
    assert str(confirmed.context["receipt"]) not in confirmed_html
    assert client.post(url, submit).status_code == 200
    assert counts() == (1, 0, 0, 0, 1)
    records = [record for record in caplog.records if record.name == "cei"]
    assert records
    formatted = "\n".join(StructuredJsonFormatter().format(record) for record in records)
    for sensitive in [token, "EXPLICACAO-RESERVADA", "PEGADINHA-RESERVADA", "opcao-dois"]:
        assert sensitive not in formatted
    assert all(
        json.loads(StructuredJsonFormatter().format(record))["correlation_id"] for record in records
    )


@pytest.mark.parametrize(
    ("host", "origin"),
    [("127.0.0.1:8000", "http://127.0.0.1:8000"), ("localhost:8000", "http://localhost:8000")],
)
def test_initial_http_same_origin_csrf_keeps_cross_site_rejection(
    setup: tuple[AttemptService, Question, Workspace],
    host: str,
    origin: str,
) -> None:
    """The local form posts from its actual origin; null/foreign origins stay blocked."""
    _, item, _ = setup
    client = Client(enforce_csrf_checks=True)
    url = reverse("attempts:initial", args=[item.id])
    page = client.get(url, HTTP_HOST=host)
    answer = page.context["answer"]
    data = {
        "action": "answer",
        "revision_id": str(answer.initial["revision_id"]),
        "lock_version": answer.initial["lock_version"],
        "alternative_id": str(answer.fields["alternative_id"].choices[0][0]),
        "csrfmiddlewaretoken": client.cookies["csrftoken"].value,
    }
    assert client.post(url, data, HTTP_HOST=host, HTTP_ORIGIN="null").status_code == 403
    assert (
        client.post(
            url,
            data,
            HTTP_HOST=host,
            HTTP_ORIGIN="http://untrusted.example",
        ).status_code
        == 403
    )
    assert (
        client.post(
            url,
            data,
            HTTP_HOST=host,
            HTTP_ORIGIN=origin,
        ).status_code
        == 302
    )


def test_http_cancel_session_and_unknown_fields(
    setup: tuple[AttemptService, Question, Workspace],
) -> None:
    _, item, _ = setup
    client = Client()
    url = reverse("attempts:initial", args=[item.id])
    assert client.post(url, {"action": "answer"}).status_code == 403
    page = client.get(url)
    form = page.context["answer"]
    page = client.post(
        url,
        {
            "action": "answer",
            "revision_id": form.initial["revision_id"],
            "lock_version": form.initial["lock_version"],
            "alternative_id": form.fields["alternative_id"].choices[0][0],
        },
        follow=True,
    )
    token = page.context["confirmation"].initial["token"]
    assert client.post(url, {"action": "cancel", "token": token}, follow=True).status_code == 200
    assert counts() == (0, 0, 0, 0, 0)


def test_real_workspace_crossing(setup: tuple[AttemptService, Question, Workspace]) -> None:
    service, item, workspace = setup
    user = User.objects.create_user()
    foreign = Workspace.objects.create(
        owner_user=user, name="Outro espaço sintético", timezone_name="Asia/Tokyo"
    )
    seed_standard_error_categories(foreign)
    foreign_question = question(foreign)
    other_service = AttemptService(
        actor_id=user.id,
        workspace_id=foreign.id,
        session=service.session,
        store=service.store,
        clock=service.clock,
    )
    token = evaluate(service, item)
    with pytest.raises(InitialAttemptError):
        other_service.context(token)
    with pytest.raises(InitialAttemptError):
        service.presentation(foreign_question.id)
    with pytest.raises(InitialAttemptError):
        service.confirm(
            token=token,
            key=uuid.uuid4(),
            category_id=foreign.error_categories.get(code="ATTENTION").id,
        )
    assert counts() == (0, 0, 0, 0, 0)
    other_service.confirm(
        token=evaluate(other_service, foreign_question),
        key=uuid.uuid4(),
        category_id=foreign.error_categories.get(code="ATTENTION").id,
    )
    assert not workspace.attempts.exists()
    assert not workspace.review_cycles.exists()
    assert not workspace.reviews.exists()
    assert foreign.attempts.count() == 1


@pytest.mark.parametrize("change", ["workspace", "revision", "archived"])
def test_context_invalidated_by_current_state(
    setup: tuple[AttemptService, Question, Workspace],
    change: str,
) -> None:
    service, item, workspace = setup
    token = evaluate(service, item)
    if change == "workspace":
        Workspace.objects.filter(pk=workspace.id).update(lock_version=2)
    elif change == "revision":
        item.revisions.update(is_current=False)
    else:
        Question.objects.filter(pk=item.id).update(
            status="ARCHIVED", archived_at=service.clock.now().value
        )
    with pytest.raises(InitialAttemptError):
        service.feedback(token)
    with pytest.raises(InitialAttemptError):
        service.confirm(
            token=token,
            key=uuid.uuid4(),
            category_id=workspace.error_categories.get(code="ATTENTION").id,
        )
    assert counts() == (0, 0, 0, 0, 0)


@pytest.mark.django_db
def test_already_answered_question_has_useful_navigation_not_technical_error(
    setup: tuple[AttemptService, Question, Workspace],
) -> None:
    service, item, workspace = setup
    service.confirm(
        token=evaluate(service, item, True),
        key=uuid.uuid4(),
    )

    response = Client().get(reverse("attempts:initial", args=[item.id]))
    html = response.content.decode()

    assert response.status_code == 409
    assert "Quest" in html
    assert "reviews/timeline" in html and 'href="/reviews/"' in html
    assert "Reabrir questÃ£o" not in html
    assert "CONFLICT" not in html and "INVALID_CONTEXT" not in html
    assert workspace.attempts.filter(question=item).count() == 1


@pytest.mark.django_db
def test_real_invalid_context_remains_recoverable_without_technical_code(
    setup: tuple[AttemptService, Question, Workspace],
) -> None:
    _, item, _ = setup

    # A malformed POST has no usable session/context.
    response = Client().post(reverse("attempts:initial", args=[item.id]), {"action": "confirm"})
    html = response.content.decode()

    assert response.status_code == 403
    assert "Sess" in html
    assert "CONFLICT" not in html and "INVALID_CONTEXT" not in html


def test_same_key_different_context_conflicts(
    setup: tuple[AttemptService, Question, Workspace],
) -> None:
    service, item, workspace = setup
    first = evaluate(service, item, True)
    second = evaluate(service, question(workspace, "2"), True)
    key = uuid.uuid4()
    service.confirm(token=first, key=key)
    with pytest.raises(InitialAttemptError):
        service.confirm(token=second, key=key)
    assert counts() == (1, 0, 0, 0, 1)


def test_retry_success_uses_same_key_and_delay(
    setup: tuple[AttemptService, Question, Workspace],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from modules.attempts.persistence import run_sqlite_critical_write

    service, item, _ = setup
    token = evaluate(service, item, True)
    key = uuid.uuid4()
    original = service._receipt
    receipt = Mock(side_effect=[OperationalError("database is locked"), None])
    sleep = Mock()

    def retry(operation: Any) -> Any:
        return run_sqlite_critical_write(operation, sleep=sleep)

    def create(*args: Any) -> OperationReceipt:
        receipt(*args)
        return original(*args)

    monkeypatch.setattr(service, "_receipt", create)
    monkeypatch.setattr("modules.attempts.services.run_sqlite_critical_write", retry)
    result = service.confirm(token=token, key=key)
    sleep.assert_called_once_with(0.150)
    assert result.idempotency_key == key
    assert counts() == (1, 0, 0, 0, 1)


def test_http_error_diagnosis_recovery_and_expiration(
    setup: tuple[AttemptService, Question, Workspace],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _, item, workspace = setup
    client = Client()
    url = reverse("attempts:initial", args=[item.id])
    page = client.get(url)
    form = page.context["answer"]
    page = client.post(
        url,
        {
            "action": "answer",
            "revision_id": form.initial["revision_id"],
            "lock_version": form.initial["lock_version"],
            "alternative_id": form.fields["alternative_id"].choices[0][0],
        },
        follow=True,
    )
    submit = {
        "action": "confirm",
        **page.context["confirmation"].initial,
        "category_id": workspace.error_categories.get(code="OTHER").id,
        "other_description": "   ",
    }
    page = client.post(url, submit)
    assert page.status_code == 400 and page.context["confirmation"].errors
    assert counts() == (0, 0, 0, 0, 0)
    submit["other_description"] = "diagnostico sintetico"
    with monkeypatch.context() as patch:
        patch.setattr(AttemptService, "_receipt", Mock(side_effect=OperationalError("disk error")))
        page = client.post(url, submit)
    assert page.status_code == 503
    assert str(page.context["confirmation"].data["key"]) == str(submit["key"])
    assert counts() == (0, 0, 0, 0, 0)
    confirmed = client.post(url, submit)
    assert confirmed.status_code == 200
    confirmed_html = confirmed.content.decode()
    assert "Tentativa confirmada com sucesso." in confirmed_html
    assert "Recibo:" not in confirmed_html
    assert str(confirmed.context["receipt"]) not in confirmed_html
    assert counts() == (1, 1, 1, 1, 1)


@pytest.mark.parametrize(
    "field",
    [
        "workspace_id",
        "revision_id",
        "alternative_id",
        "lock_version",
        "is_correct",
        "perceived_ease",
        "diagnosis",
    ],
)
def test_http_rejects_extra_confirmation_fields(
    setup: tuple[AttemptService, Question, Workspace],
    field: str,
) -> None:
    _, item, _ = setup
    client = Client()
    url = reverse("attempts:initial", args=[item.id])
    page = client.get(url)
    form = page.context["answer"]
    page = client.post(
        url,
        {
            "action": "answer",
            "revision_id": form.initial["revision_id"],
            "lock_version": form.initial["lock_version"],
            "alternative_id": form.fields["alternative_id"].choices[0][0],
        },
        follow=True,
    )
    submit = {"action": "confirm", **page.context["confirmation"].initial, field: "adulterado"}
    page = client.post(url, submit)
    assert page.status_code == 409
    assert b"EXPLICACAO-RESERVADA" not in page.content
    assert counts() == (0, 0, 0, 0, 0)


def test_orchestrator_direct_call_validates_context_and_payload(
    setup: tuple[AttemptService, Question, Workspace],
) -> None:
    service, item, workspace = setup
    orchestrator = CompleteReviewService(service)
    correct = evaluate(service, item, True)
    category = workspace.error_categories.get(code="OTHER")
    with pytest.raises(InitialAttemptError):
        orchestrator.complete_initial_error(
            token=correct, key=uuid.uuid4(), category_id=category.id, description="diagnostico"
        )
    token = evaluate(service, item)
    key = uuid.uuid4()
    receipt = orchestrator.complete_initial_error(
        token=token, key=key, category_id=category.id, description="  inicial "
    )
    assert (
        service.confirm(
            token=token, key=key, category_id=category.id, other_description="inicial"
        ).id
        == receipt.id
    )
    with pytest.raises(InitialAttemptError):
        orchestrator.complete_initial_error(
            token=token, key=key, category_id=category.id, description="divergente"
        )
    assert counts() == (1, 1, 1, 1, 1)
