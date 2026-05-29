from typing import Any, Dict, Optional
from django.db.models import QuerySet
from .models import Expense
from django.contrib.auth import get_user_model

User = get_user_model()


class ExpenseNotFoundError(Exception):
    pass


class ExpenseActionConflictError(Exception):
    pass


class ExpenseService:
    """
    Thin service wrapper for Expense operations.

    Expected methods used by views:
      - list_for_user(user, filters) -> QuerySet[Expense]
      - list_for_admin(filters) -> QuerySet[Expense]
      - get_by_id(pk, user=None) -> Expense or raise ExpenseNotFoundError
      - create_expense(data_dict, user) -> Expense
      - delete_expense(pk, user) -> None
      - approve_expense(pk, admin_user) -> Expense or raise ExpenseActionConflictError
      - reject_expense(pk, admin_user, reason=None) -> Expense or raise ExpenseActionConflictError

    This is intentionally thin; adapt to existing business logic if a real service exists.
    """

    @staticmethod
    def list_for_user(user: User, filters: Optional[Dict[str, Any]] = None) -> QuerySet:
        qs = Expense.objects.filter(submitted_by=user).select_related("submitted_by", "reviewed_by")
        if filters:
            if "status" in filters:
                qs = qs.filter(status=filters.get("status"))
            if "category" in filters:
                qs = qs.filter(category=filters.get("category"))
        return qs

    @staticmethod
    def list_for_admin(filters: Optional[Dict[str, Any]] = None) -> QuerySet:
        qs = Expense.objects.all().select_related("submitted_by", "reviewed_by")
        if filters:
            if "status" in filters:
                qs = qs.filter(status=filters.get("status"))
            if "category" in filters:
                qs = qs.filter(category=filters.get("category"))
            if "submitted_by" in filters:
                qs = qs.filter(submitted_by__id=filters.get("submitted_by"))
        return qs

    @staticmethod
    def get_by_id(pk: int, user: Optional[User] = None) -> Expense:
        try:
            expense = Expense.objects.select_related("submitted_by", "reviewed_by").get(pk=pk)
        except Expense.DoesNotExist as exc:
            raise ExpenseNotFoundError from exc
        # If user is provided, ensure ownership or admin will be checked elsewhere
        return expense

    @staticmethod
    def create_expense(data: Dict[str, Any], user: User) -> Expense:
        # data expected to include: title, amount, category, description, receipt (optional), workspace (optional)
        expense = Expense.objects.create(
            workspace=user,
            title=data.get("title", ""),
            amount=data.get("amount"),
            category=data.get("category"),
            description=data.get("description", ""),
            receipt=data.get("receipt"),
            submitted_by=user,
        )
        return expense

    @staticmethod
    def delete_expense(pk: int, user: User) -> None:
        try:
            expense = Expense.objects.get(pk=pk)
        except Expense.DoesNotExist as exc:
            raise ExpenseNotFoundError from exc
        # allow owner or staff to delete (views will enforce)
        expense.delete()

    @staticmethod
    def approve_expense(pk: int, admin_user: User) -> Expense:
        try:
            expense = Expense.objects.get(pk=pk)
        except Expense.DoesNotExist as exc:
            raise ExpenseNotFoundError from exc
        try:
            expense.approve(admin_user)
        except ValueError as exc:
            raise ExpenseActionConflictError from exc
        return expense

    @staticmethod
    def reject_expense(pk: int, admin_user: User, reason: Optional[str] = None) -> Expense:
        try:
            expense = Expense.objects.get(pk=pk)
        except Expense.DoesNotExist as exc:
            raise ExpenseNotFoundError from exc
        try:
            expense.reject(admin_user, reason or "")
        except ValueError as exc:
            raise ExpenseActionConflictError from exc
        return expense
