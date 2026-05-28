from django.contrib import admin
from .models import Expense


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "amount", "status", "workspace", "submitted_by", "reviewed_by", "created_at")
    search_fields = ("title", "description")
    list_filter = ("status", "category")
