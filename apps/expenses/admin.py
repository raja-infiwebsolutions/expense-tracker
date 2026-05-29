from django.contrib import admin
from .models import Expense


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "amount", "user", "workspace_id", "date", "created_at"]
    search_fields = ["title", "receipt_original_name"]
