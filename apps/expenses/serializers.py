"""
Expenses serializers with receipt validation.
Ticket: Add Expense serializers with receipt validation.
Note: We validate MIME types by inspecting file signatures (magic bytes) to avoid adding a dependency on python-magic.
If you prefer python-magic, add it to requirements.txt and switch to magic.from_buffer for more thorough detection.
"""
from typing import Any, Optional
from decimal import Decimal

from rest_framework import serializers
from django.core.files.uploadedfile import UploadedFile

from .models import Expense


MAX_RECEIPT_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_MIME_TYPES = ("image/jpeg", "image/png", "application/pdf")


class ExpenseSerializer(serializers.ModelSerializer):
    receipt_url = serializers.SerializerMethodField()

    class Meta:
        model = Expense
        # include commonly used fields; adjust if model changes
        fields = (
            "id",
            "title",
            "amount",
            "category",
            "description",
            "receipt_url",
            "status",
            "submitted_by",
            "reviewed_by",
            "reviewed_at",
            "review_notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "receipt_url", "created_at", "updated_at")

    def get_receipt_url(self, obj: Expense) -> Optional[str]:
        receipt_field = getattr(obj, "receipt", None)
        if not receipt_field:
            return None
        try:
            url = receipt_field.url
        except Exception:
            return None
        request = self.context.get("request")
        if request is not None:
            return request.build_absolute_uri(url)
        return url


class ExpenseWriteSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=200)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    category = serializers.ChoiceField(choices=Expense.Category.choices)
    receipt = serializers.FileField(required=False, allow_null=True, write_only=True)

    class Meta:
        model = Expense
        fields = ("title", "amount", "category", "description", "receipt")

    def validate_amount(self, value: Decimal) -> Decimal:
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0.")
        return value

    def validate_title(self, value: str) -> str:
        if len(value) > 200:
            raise serializers.ValidationError("Title must be 200 characters or fewer.")
        return value

    def validate_receipt(self, uploaded_file: Optional[UploadedFile]) -> Optional[UploadedFile]:
        if not uploaded_file:
            return None

        # Size check
        if uploaded_file.size > MAX_RECEIPT_SIZE:
            raise serializers.ValidationError("Receipt file size must be 10 MB or less.")

        # Read starting bytes for signature-based MIME detection
        try:
            # read first 8 bytes
            header = uploaded_file.read(8)
            uploaded_file.seek(0)
        except Exception:
            # if we cannot read, fall back to content_type
            header = b""

        mime: Optional[str] = None
        # JPEG
        if header.startswith(b"\xff\xd8\xff"):
            mime = "image/jpeg"
        # PNG
        elif header.startswith(b"\x89PNG"):
            mime = "image/png"
        # PDF
        elif header.startswith(b"%PDF"):
            mime = "application/pdf"
        else:
            # Fallback to provided content_type if available
            mime = getattr(uploaded_file, "content_type", None)

        if mime not in ALLOWED_MIME_TYPES:
            raise serializers.ValidationError("Unsupported file type. Allowed types: JPG, PNG, PDF.")

        return uploaded_file

    def create(self, validated_data: dict[str, Any]) -> Expense:
        # Pop receipt because FileField is not a model field on the same name until saved
        receipt = validated_data.pop("receipt", None)

        # Ensure workspace is set — prefer passed kwarg (serializer.save(workspace=user)) or request.user
        workspace = validated_data.pop("workspace", None)
        if workspace is None:
            request = self.context.get("request")
            if request is not None and hasattr(request, "user"):
                workspace = request.user

        if workspace is None:
            raise serializers.ValidationError({"workspace": "Workspace (user) must be provided."})

        expense = Expense.objects.create(workspace=workspace, **validated_data)

        if receipt:
            # Assign file to FileField and save
            expense.receipt.save(receipt.name, receipt, save=True)

        return expense
