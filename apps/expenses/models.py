from django.db import models
from django.conf import settings
from django.utils import timezone


class Expense(models.Model):
    workspace_id = models.IntegerField(null=True, blank=True, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="expenses",
    )
    title = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField(default=timezone.now)
    description = models.TextField(blank=True)
    receipt = models.FileField(upload_to="expenses/%Y/%m/%d/", null=True, blank=True)
    receipt_content_type = models.CharField(max_length=50, blank=True)
    receipt_original_name = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.title} - {self.amount}"
