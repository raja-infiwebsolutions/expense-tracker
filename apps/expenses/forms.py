from typing import Any
from django import forms
from django.contrib.auth import get_user_model
from .models import Expense

User = get_user_model()


class ExpenseFilterForm(forms.Form):
    status = forms.ChoiceField(
        choices=[("", "All")] + list(Expense.Status.choices), required=False
    )
    employee = forms.ModelChoiceField(queryset=User.objects.none(), required=False)
    category = forms.ChoiceField(choices=[("", "All")] + list(Expense.Category.choices), required=False)
    workspace_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args: Any, workspace_id: int | None = None, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if workspace_id:
            # Employee queryset: users who submitted expenses to this workspace
            qs = User.objects.filter(submitted_expenses__workspace_id=workspace_id).distinct()
            self.fields["employee"].queryset = qs
            self.fields["workspace_id"].initial = workspace_id
