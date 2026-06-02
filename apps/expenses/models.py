from django.db import models
from django.conf import settings
from django.utils import timezone


class Expense(models.Model):
    class Category(models.TextChoices):
        TRAVEL = "travel", "Travel"
        MEALS = "meals", "Meals"
        SOFTWARE = "software", "Software"
        EQUIPMENT = "equipment", "Equipment"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        SUBMITTED = "submitted", "Submitted"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    # Owner is a user who owns the expense list (previously workspace)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_expenses",
    )
    title = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, choices=Category.choices)
    description = models.TextField(blank=True)
    receipt = models.FileField(upload_to="receipts/%Y/%m/", blank=True, null=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.SUBMITTED)
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="submitted_expenses",
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_expenses",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.title} - {self.amount} ({self.status})"

    def approve(self, reviewer) -> None:
        """Mark this expense approved by reviewer and set reviewed_at."""
        self.status = self.Status.APPROVED
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.save()

    def reject(self, reviewer, notes: str = "") -> None:
        """Mark this expense rejected with optional notes."""
        self.status = self.Status.REJECTED
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.review_notes = notes
        self.save()
