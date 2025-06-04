from typing import ClassVar

from django.core.validators import MinValueValidator
from django.db import models

from courses.models import Course


class Cost(models.Model):
    """Track course and company level costs"""

    COST_TYPE_CHOICES: ClassVar[list[tuple[str, str]]] = [
        ("اقامت هتل - ثابت", "اقامت هتل - ثابت"),
        ("پذیرایی تیم اجرایی - ثابت", "پذیرایی تیم اجرایی - ثابت"),
        ("جابجایی تیم اجرایی - ثابت", "جابجایی تیم اجرایی - ثابت"),
        ("تجهیزات - ثابت", "تجهیزات - ثابت"),
        ("نیروی خدماتی - ثابت", "نیروی خدماتی - ثابت"),
        ("جبران خدمات تیم اجرا - ثابت", "جبران خدمات تیم اجرا - ثابت"),
        ("لوازم تحریر - متغیر", "لوازم تحریر - متغیر"),
        ("پذیرایی - متغیر", "پذیرایی - متغیر"),
    ]

    date = models.DateField()
    invoice_number = models.CharField(max_length=50, blank=True, null=True)
    title = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField()
    person = models.CharField(max_length=100, blank=True, null=True)
    amount = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(0)]
    )
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    total_amount = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(0)]
    )
    is_paid = models.BooleanField(default=False)
    cost_type = models.CharField(max_length=50, choices=COST_TYPE_CHOICES)

    # Relationship
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="costs", blank=True, null=True
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cost"
        verbose_name_plural = "Costs"
        ordering: ClassVar[list[str]] = ["-date", "-created_at"]

    def __str__(self):
        course_info = f" - {self.course.name}" if self.course else ""
        return f"{self.title or self.description[:50]}{course_info} ({self.date})"

    def save(self, *args, **kwargs):
        # Auto-calculate total_amount if not provided
        if not self.total_amount:
            self.total_amount = self.amount * self.quantity
        super().save(*args, **kwargs)
