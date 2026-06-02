from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Expense

User = get_user_model()


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ["title", "status", "owner", "created_at"]
    list_filter = ["status"]
    # Make search_fields resilient to custom user models
    search_fields = ["title"]
    if hasattr(User, "username"):
        search_fields.append("owner__username")
    if hasattr(User, "email"):
        search_fields.append("owner__email")
