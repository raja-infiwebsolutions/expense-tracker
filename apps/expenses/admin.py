from django.contrib import admin
from .models import Expense


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ["title", "status", "submitted_by", "amount", "workspace", "created_at"]
    list_filter = ["status", "category"]
    search_fields = ["title", "submitted_by__username", "workspace__username"]
