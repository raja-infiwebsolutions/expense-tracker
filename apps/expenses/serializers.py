from rest_framework import serializers
from .models import Expense


class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = [
            "id",
            "owner",
            "title",
            "amount",
            "category",
            "description",
            "receipt",
            "status",
            "submitted_by",
            "reviewed_by",
            "reviewed_at",
            "review_notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "owner",
            "submitted_by",
            "reviewed_by",
            "reviewed_at",
            "created_at",
            "updated_at",
        ]
