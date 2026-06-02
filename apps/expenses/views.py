from typing import Any
from rest_framework import viewsets, permissions, filters
from rest_framework.request import Request
from rest_framework.response import Response

from .models import Expense
from .serializers import ExpenseSerializer


class ExpenseViewSet(viewsets.ModelViewSet):
    """API endpoint for Expenses."""
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description"]

    def get_queryset(self) -> Any:
        # show only expenses owned by the requesting user
        return Expense.objects.filter(owner=self.request.user).select_related(
            "owner", "submitted_by", "reviewed_by"
        )

    def perform_create(self, serializer: Any) -> None:
        serializer.save(owner=self.request.user, submitted_by=self.request.user)


# Keep the template view for the frontend
from django.shortcuts import render
from django.views import View

class ExpensesIndexView(View):
    def get(self, request):
        return render(request, "expenses/index.html", {})
