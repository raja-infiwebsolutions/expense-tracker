from typing import Any
from django.db.models import QuerySet
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import Expense


def get_expenses_for_workspace(workspace_id: int, filters: dict[str, Any]) -> QuerySet:
    # workspace_id param kept for backwards compatibility but filters by owner
    qs = Expense.objects.filter(owner_id=workspace_id).select_related("submitted_by", "reviewed_by", "owner")
    status = filters.get("status")
    if status:
        qs = qs.filter(status=status)
    employee = filters.get("employee")
    if employee:
        qs = qs.filter(submitted_by_id=employee)
    category = filters.get("category")
    if category:
        qs = qs.filter(category=category)
    return qs.order_by("-created_at")


def approve_expense(expense_id: int, reviewer_user: Any) -> Expense:
    expense = get_object_or_404(Expense, pk=expense_id)
    if expense.status != Expense.Status.SUBMITTED:
        raise ValueError("Only submitted expenses can be approved")
    expense.status = Expense.Status.APPROVED
    expense.reviewed_by = reviewer_user
    expense.reviewed_at = timezone.now()
    expense.save(update_fields=["status", "reviewed_by", "reviewed_at", "updated_at"]) 
    return expense


def reject_expense(expense_id: int, reviewer_user: Any, notes: str) -> Expense:
    if not notes:
        raise ValueError("Rejection notes are required")
    expense = get_object_or_404(Expense, pk=expense_id)
    if expense.status != Expense.Status.SUBMITTED:
        raise ValueError("Only submitted expenses can be rejected")
    expense.status = Expense.Status.REJECTED
    expense.reviewed_by = reviewer_user
    expense.review_notes = notes
    expense.reviewed_at = timezone.now()
    expense.save(update_fields=["status", "reviewed_by", "review_notes", "reviewed_at", "updated_at"]) 
    return expense
