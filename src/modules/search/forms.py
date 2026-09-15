"""Entradas GET validadas para a listagem de questões."""

import uuid
from typing import Any, cast

from django import forms
from django.http import QueryDict

from modules.errors.models import ErrorCategory
from modules.questions.models import QuestionStatus
from modules.reviews.policies import ReviewTemporalStatus
from modules.taxonomy.models import Discipline, Subject, Subsubject


class QuestionSearchForm(forms.Form):
    """Valide filtros do Workspace e mantenha a hierarquia consistente."""

    query = forms.CharField(
        required=False,
        max_length=200,
        label="Buscar no enunciado ou explicação",
        widget=forms.TextInput(attrs={"type": "search", "autocomplete": "off"}),
    )
    status = forms.ChoiceField(
        required=False,
        choices=QuestionStatus.choices,
        label="Estado",
    )
    discipline = forms.ModelChoiceField(
        required=False,
        queryset=Discipline.objects.none(),
        label="Disciplina",
    )
    subject = forms.ModelChoiceField(
        required=False,
        queryset=Subject.objects.none(),
        label="Assunto",
    )
    subsubject = forms.ModelChoiceField(
        required=False,
        queryset=Subsubject.objects.none(),
        label="Subassunto",
    )
    review_status = forms.ChoiceField(
        required=False,
        choices=(
            ("", "Todas as situações"),
            (ReviewTemporalStatus.OVERDUE, "Atrasada"),
            (ReviewTemporalStatus.DUE, "Devida hoje"),
            (ReviewTemporalStatus.FUTURE, "Futura"),
        ),
        label="Situação de revisão",
    )
    initial_result = forms.ChoiceField(
        required=False,
        choices=(
            ("", "Qualquer resultado"),
            ("correct", "Inicial correta"),
            ("incorrect", "Inicial incorreta"),
        ),
        label="Resultado inicial",
    )
    error_category = forms.ChoiceField(required=False, choices=(), label="Categoria de erro")

    def __init__(self, data: QueryDict | None = None, *, workspace_id: uuid.UUID) -> None:
        super().__init__(data=data)
        selected_discipline = self._uuid_value("discipline")
        selected_subject = self._uuid_value("subject")
        discipline_field = cast(Any, self.fields["discipline"])
        discipline_field.queryset = Discipline.objects.filter(workspace_id=workspace_id).order_by(
            "sort_order", "name_key", "id"
        )
        subjects = Subject.objects.filter(workspace_id=workspace_id)
        if selected_discipline is not None:
            subjects = subjects.filter(discipline_id=selected_discipline)
        subject_field = cast(Any, self.fields["subject"])
        subject_field.queryset = subjects.select_related("discipline").order_by(
            "discipline__sort_order", "name_key", "id"
        )
        subsubjects = Subsubject.objects.filter(workspace_id=workspace_id)
        if selected_subject is not None:
            subsubjects = subsubjects.filter(subject_id=selected_subject)
        subsubject_field = cast(Any, self.fields["subsubject"])
        subsubject_field.queryset = subsubjects.select_related("subject__discipline").order_by(
            "subject__name_key", "name_key", "id"
        )
        category_field = cast(Any, self.fields["error_category"])
        categories = ErrorCategory.objects.filter(workspace_id=workspace_id).order_by("code", "id")
        category_field.choices = [
            ("", "Todas as categorias"),
            ("unclassified", "Erros sem classificação (resíduo)"),
            *((str(category.id), category.display_name) for category in categories),
        ]

    def _uuid_value(self, field_name: str) -> uuid.UUID | None:
        value = self.data.get(field_name) if self.is_bound else self.initial.get(field_name)
        if not value:
            return None
        try:
            return uuid.UUID(str(value))
        except ValueError:
            return None

    def clean_status(self) -> str:
        return self.cleaned_data["status"] or QuestionStatus.ACTIVE

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean() or {}
        discipline = cleaned_data.get("discipline")
        subject = cleaned_data.get("subject")
        subsubject = cleaned_data.get("subsubject")
        if (
            discipline is not None
            and subject is not None
            and subject.discipline_id != discipline.id
        ):
            self.add_error("subject", "O assunto selecionado não pertence à disciplina.")
        if subject is not None and subsubject is not None and subsubject.subject_id != subject.id:
            self.add_error("subsubject", "O subassunto selecionado não pertence ao assunto.")
        if discipline is not None and subsubject is not None:
            if subsubject.subject.discipline_id != discipline.id:
                self.add_error("subsubject", "O subassunto selecionado não pertence à disciplina.")
        return cleaned_data
