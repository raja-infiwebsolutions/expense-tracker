from typing import Any
from rest_framework import serializers
from .models import Expense
from django.contrib.auth import get_user_model
from .services import ExpenseService

User = get_user_model()


class SubmittedBySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email")


class ExpenseSerializer(serializers.ModelSerializer):
    submitted_by = SubmittedBySerializer(read_only=True)
    reviewed_by = SubmittedBySerializer(read_only=True)
    receipt_url = serializers.SerializerMethodField()

    class Meta:
        model = Expense
        fields = (
            "id",
            "title",
            "amount",
            "category",
            "description",
            "status",
            "submitted_by",
            "reviewed_by",
            "review_notes",
            "reviewed_at",
            "created_at",
            "updated_at",
            "receipt_url",
        )
        read_only_fields = (
            "id",
            "status",
            "submitted_by",
            "reviewed_by",
            "review_notes",
            "reviewed_at",
            "created_at",
            "updated_at",
            "receipt_url",
        )

    def get_receipt_url(self, obj: Expense) -> Any:
        request = self.context.get("request")
        if obj.receipt and request is not None:
            return request.build_absolute_uri(obj.receipt.url)
        if obj.receipt:
            return obj.receipt.url
        return None


class ExpenseCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    category = serializers.ChoiceField(choices=Expense.Category.choices)
    description = serializers.CharField(allow_blank=True, required=False)
    receipt = serializers.FileField(required=False, allow_null=True)

    def create(self, validated_data: dict) -> Expense:
        request = self.context.get("request")
        user = getattr(request, "user", None)
        expense = ExpenseService.create_expense(validated_data, user)
        return expense

    def to_representation(self, instance: Expense) -> dict:
        return ExpenseSerializer(instance, context=self.context).data
