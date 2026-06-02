import os
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from decimal import Decimal
from .models import Expense
from django.core.exceptions import ValidationError
from django.db import IntegrityError

User = get_user_model()

# Use an environment-provided test password or generate a random one to avoid hardcoded credentials
TEST_PASSWORD = os.environ.get("TEST_PASSWORD") or get_random_string(12)

class ExpenseModelTests(TestCase):
    def setUp(self):
        # create a user to act as both owner and submitter
        self.user = User.objects.create_user(username="tester", password=TEST_PASSWORD)

    def test_create_expense(self):
        expense = Expense.objects.create(
            owner=self.user,
            title="Business Lunch",
            amount=Decimal("45.50"),
            category="meals",
            description="Client meeting",
            submitted_by=self.user,
        )
        self.assertTrue(Expense.objects.exists())
        # __str__ returns: f"{self.title} - {self.amount} ({self.status})"
        self.assertEqual(str(expense), f"{expense.title} - {expense.amount} ({expense.status})")

    def test_negative_amount_rejected(self):
        expense = Expense(
            owner=self.user,
            title="Faulty Expense",
            amount=Decimal("-10.00"),
            category="other",
            submitted_by=self.user,
        )
        # Try model validation first
        try:
            expense.full_clean()
        except ValidationError:
            # model validation caught the issue — test passes
            return

        # If full_clean didn't raise, try saving and expect a DB-level rejection (IntegrityError) or that the object is not persisted
        try:
            expense.save()
        except IntegrityError:
            return

        # If save succeeded without raising, ensure the negative amount wasn't persisted
        exists = Expense.objects.filter(pk=expense.pk, amount__lt=0).exists()
        self.assertFalse(exists, "Expense with negative amount was persisted in the database")
