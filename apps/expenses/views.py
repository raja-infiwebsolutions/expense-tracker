from django.shortcuts import render
from django.views import View

# Placeholder views for wiring; feature work is backend-only in this ticket.

class ExpensesIndexView(View):
    def get(self, request):
        return render(request, "expenses/index.html", {})
