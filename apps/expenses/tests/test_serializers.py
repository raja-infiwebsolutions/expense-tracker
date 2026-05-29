from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from apps.expenses.models import Expense
from apps.expenses.serializers import ExpenseWriteSerializer


class ExpenseSerializerTests(TestCase):
    def setUp(self) -> None:
        # Create a dummy user to act as workspace
        from django.contrib.auth import get_user_model

        User = get_user_model()
        self.user = User.objects.create_user(username="tester", password="pass123")

    def make_jpeg_file(self, name: str = "test.jpg") -> SimpleUploadedFile:
        # Minimal JPEG header + minimal payload
        data = b"\xff\xd8\xff\xdb" + b"0" * 100
        return SimpleUploadedFile(name, data, content_type="image/jpeg")

    def make_png_file(self, name: str = "test.png") -> SimpleUploadedFile:
        data = b"\x89PNG\r\n\x1a\n" + b"0" * 100
        return SimpleUploadedFile(name, data, content_type="image/png")

    def make_pdf_file(self, name: str = "test.pdf") -> SimpleUploadedFile:
        data = b"%PDF-1.4\n%EOF\n" + b"0" * 100
        return SimpleUploadedFile(name, data, content_type="application/pdf")

    def make_text_file(self, name: str = "test.txt") -> SimpleUploadedFile:
        data = b"Hello, world!" * 10
        return SimpleUploadedFile(name, data, content_type="text/plain")

    def test_valid_receipts_accepted(self) -> None:
        for file_maker in (self.make_jpeg_file, self.make_png_file, self.make_pdf_file):
            receipt = file_maker()
            data = {
                "title": "Lunch",
                "amount": "12.50",
                "category": Expense.Category.MEALS,
                "description": "Team lunch",
                "receipt": receipt,
            }
            serializer = ExpenseWriteSerializer(data=data, context={"request": None})
            self.assertTrue(serializer.is_valid(), msg=serializer.errors)
            expense = serializer.save(workspace=self.user)
            self.assertIsInstance(expense, Expense)
            self.assertTrue(bool(expense.receipt))

    def test_invalid_receipt_rejected(self) -> None:
        receipt = self.make_text_file()
        data = {
            "title": "Stationery",
            "amount": "5.00",
            "category": Expense.Category.OTHER,
            "receipt": receipt,
        }
        serializer = ExpenseWriteSerializer(data=data, context={"request": None})
        self.assertFalse(serializer.is_valid())
        self.assertIn("receipt", serializer.errors)

    def test_large_receipt_rejected(self) -> None:
        # create a large file >10MB
        data_bytes = b"\xff\xd8\xff" + b"0" * (10 * 1024 * 1024 + 1)
        large_file = SimpleUploadedFile("big.jpg", data_bytes, content_type="image/jpeg")
        data = {
            "title": "Big",
            "amount": "1.00",
            "category": Expense.Category.OTHER,
            "receipt": large_file,
        }
        serializer = ExpenseWriteSerializer(data=data, context={"request": None})
        self.assertFalse(serializer.is_valid())
        self.assertIn("receipt", serializer.errors)

    def test_amount_and_title_validation(self) -> None:
        # zero amount
        data = {"title": "T", "amount": "0.00", "category": Expense.Category.OTHER}
        serializer = ExpenseWriteSerializer(data=data, context={"request": None})
        self.assertFalse(serializer.is_valid())
        self.assertIn("amount", serializer.errors)

        # long title
        data = {"title": "x" * 201, "amount": "1.00", "category": Expense.Category.OTHER}
        serializer = ExpenseWriteSerializer(data=data, context={"request": None})
        self.assertFalse(serializer.is_valid())
        self.assertIn("title", serializer.errors)
