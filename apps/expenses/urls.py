from django.urls import path
from .views import ExpensesIndexView

app_name = "expenses"

urlpatterns = [
    path("", ExpensesIndexView.as_view(), name="index"),
]
