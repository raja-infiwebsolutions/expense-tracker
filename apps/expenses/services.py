from typing import Optional
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import transaction
from django.core.files.uploadedfile import UploadedFile
from django.contrib.auth import get_user_model
from .models import Expense

User = get_user_model()


class ExpenseService:
    """Service layer for expense business logic."""

    @staticmethod
    def submit_expense(user: User, expense_data: dict, receipt_file: Optional[UploadedFile] = None) -> Expense:
        """Create and submit an expense. Raises ValidationError on invalid data."""
        required_fields = ["title", "amount", "category"]
        missing = [f for f in required_fields if f not in expense_data or expense_data.get(f) in (None, "")]
        if missing:
            raise ValidationError({"missing_fields": f"Missing required fields: {', '.join(missing)}"})

        # normalize amount
        amount = expense_data["amount"]
        try:
            amount = Decimal(str(amount))
        except Exception:
            raise ValidationError({"amount": "Invalid amount value"})

        with transaction.atomic():
            expense = Expense(
                workspace=expense_data.get("workspace") or user,
                title=expense_data["title"],
                amount=amount,
                category=expense_data["category"],
                description=expense_data.get("description", ""),
            )
            # save first to get a PK for FileField save
            expense.save()

            if receipt_file is not None:
                # receipt_file is an UploadedFile or file-like
                expense.receipt.save(receipt_file.name, receipt_file, save=True)

            # mark submitted
            expense.submit(submitter=user)

        return expense

    @staticmethod
    def _get_expense_or_raise(expense_id: int) -> Expense:
        try:
            return Expense.objects.select_related("workspace", "submitted_by", "reviewed_by").get(pk=expense_id)
        except Expense.DoesNotExist:
            raise ValidationError({"expense": "Expense not found"})

    @staticmethod
    def approve_expense(user: User, expense_id: int) -> Expense:
        """Approve a submitted expense. Raises ValidationError if not allowed."""
        expense = ExpenseService._get_expense_or_raise(expense_id)
        if expense.status != Expense.Status.SUBMITTED:
            raise ValidationError({"status": "Only submitted expenses can be approved"})

        with transaction.atomic():
            expense.approve(reviewer=user)

        return expense

    @staticmethod
    def reject_expense(user: User, expense_id: int, review_notes: str) -> Expense:
        """Reject a submitted expense. review_notes required."""
        if not review_notes or not review_notes.strip():
            raise ValidationError({"review_notes": "Review notes are required to reject an expense."})

        expense = ExpenseService._get_expense_or_raise(expense_id)
        if expense.status != Expense.Status.SUBMITTED:
            raise ValidationError({"status": "Only submitted expenses can be rejected"})

        with transaction.atomic():
            expense.reject(reviewer=user, notes=review_notes.strip())

        return expense

    @staticmethod
    def delete_expense(user: User, expense_id: int) -> bool:
        """Delete an expense if allowed. Removes receipt file from storage. Returns True on success."""
        expense = ExpenseService._get_expense_or_raise(expense_id)
        if expense.status == Expense.Status.APPROVED:
            raise ValidationError({"status": "Approved expenses cannot be deleted"})

        with transaction.atomic():
            # remove receipt file from storage if present
            if expense.receipt:
                try:
                    expense.receipt.delete(save=False)
                except Exception as exc:  # catching storage exceptions
                    # re-raise as ValidationError
                    raise ValidationError({"receipt": f"Error deleting receipt file: {exc}"})
            expense.delete()

        return True
