import tempfile
import shutil
import os
from decimal import Decimal
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from apps.expenses.models import Expense
from apps.expenses.services import ExpenseService

User = get_user_model()


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class ExpenseServiceTest(TestCase):
    @classmethod
    def tearDownClass(cls) -> None:
        # cleanup temp media
        try:
            shutil.rmtree(cls._media_root)
        except Exception:
            pass
        return super().tearDownClass()

    def setUp(self) -> None:
        # capture MEDIA_ROOT set by override_settings
        self._media_root = os.environ.get("DJANGO_TEST_TMP_MEDIA") or None
        self.user = User.objects.create_user(username="tester", password="pass123")

    def test_submit_creates_expense_and_saves_receipt(self) -> None:
        content = b"receiptpdf"
        uploaded = SimpleUploadedFile("receipt.pdf", content, content_type="application/pdf")
        data = {"title": "Taxi", "amount": "12.34", "category": Expense.Category.TRAVEL}

        expense = ExpenseService.submit_expense(self.user, data, receipt_file=uploaded)

        self.assertEqual(expense.title, "Taxi")
        self.assertEqual(str(expense.amount), str(Decimal("12.34")))
        self.assertEqual(expense.status, Expense.Status.SUBMITTED)
        self.assertIsNotNone(expense.receipt)
        # ensure file exists on disk
        self.assertTrue(os.path.exists(expense.receipt.path))

    def test_approve_only_submitted(self) -> None:
        expense = Expense.objects.create(
            workspace=self.user,
            title="Lunch",
            amount=10,
            category=Expense.Category.MEALS,
            status=Expense.Status.DRAFT,
        )
        with self.assertRaises(ValidationError):
            ExpenseService.approve_expense(self.user, expense.id)

        # now submit and approve
        expense.submit(self.user)
        approved = ExpenseService.approve_expense(self.user, expense.id)
        self.assertEqual(approved.status, Expense.Status.APPROVED)
        self.assertIsNotNone(approved.reviewed_at)
        self.assertEqual(approved.reviewed_by, self.user)

    def test_reject_requires_notes_and_only_submitted(self) -> None:
        expense = Expense.objects.create(
            workspace=self.user,
            title="Software",
            amount=100,
            category=Expense.Category.SOFTWARE,
            status=Expense.Status.DRAFT,
        )
        with self.assertRaises(ValidationError):
            ExpenseService.reject_expense(self.user, expense.id, review_notes="")

        # submit then reject
        expense.submit(self.user)
        with self.assertRaises(ValidationError):
            ExpenseService.reject_expense(self.user, expense.id, review_notes="   ")

        rejected = ExpenseService.reject_expense(self.user, expense.id, review_notes="Not eligible")
        self.assertEqual(rejected.status, Expense.Status.REJECTED)
        self.assertEqual(rejected.review_notes, "Not eligible")

    def test_delete_removes_receipt_and_prevents_deleting_approved(self) -> None:
        # create expense with receipt
        content = b"receiptpdf"
        uploaded = SimpleUploadedFile("receipt2.pdf", content, content_type="application/pdf")
        expense = Expense.objects.create(
            workspace=self.user,
            title="Train",
            amount=20,
            category=Expense.Category.TRAVEL,
            status=Expense.Status.DRAFT,
        )
        expense.receipt.save(uploaded.name, uploaded, save=True)
        path = expense.receipt.path
        self.assertTrue(os.path.exists(path))

        # cannot delete if approved
        expense.submit(self.user)
        expense.approve(self.user)
        with self.assertRaises(ValidationError):
            ExpenseService.delete_expense(self.user, expense.id)
        # file should still exist
        self.assertTrue(os.path.exists(path))

        # create deletable expense
        expense2 = Expense.objects.create(
            workspace=self.user,
            title="Cab",
            amount=15,
            category=Expense.Category.TRAVEL,
            status=Expense.Status.DRAFT,
        )
        uploaded2 = SimpleUploadedFile("receipt3.pdf", b"x", content_type="application/pdf")
        expense2.receipt.save(uploaded2.name, uploaded2, save=True)
        path2 = expense2.receipt.path
        self.assertTrue(os.path.exists(path2))

        # delete via service
        deleted = ExpenseService.delete_expense(self.user, expense2.id)
        self.assertTrue(deleted)
        self.assertFalse(os.path.exists(path2))
        with self.assertRaises(Expense.DoesNotExist):
            Expense.objects.get(pk=expense2.id)
