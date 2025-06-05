from typing import ClassVar

from django.core.validators import MinValueValidator
from django.db import models
from django_jalali.db import models as jmodels

from commons.models import TimeStampedModel
from courses.models import Course


class Cost(TimeStampedModel):
    """Track course and company level costs"""

    COST_TYPE_CHOICES: ClassVar[list[tuple[int, str]]] = [
        (1, "اقامت هتل - ثابت"),
        (2, "پذیرایی تیم اجرایی - ثابت"),
        (3, "جابجایی تیم اجرایی - ثابت"),
        (4, "تجهیزات - ثابت"),
        (5, "نیروی خدماتی - ثابت"),
        (6, "جبران خدمات تیم اجرا - ثابت"),
        (7, "لوازم تحریر - متغیر"),
        (8, "پذیرایی - متغیر"),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="costs", blank=True, null=True)
    date = jmodels.jDateField()
    invoice_number = models.CharField(max_length=50, blank=True, null=True)
    title = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField()
    person = models.CharField(max_length=100, blank=True, null=True)
    amount = models.IntegerField(validators=[MinValueValidator(0)])
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    total_amount = models.IntegerField(validators=[MinValueValidator(0)])
    is_paid = models.BooleanField(default=False)
    cost_type = models.IntegerField(choices=COST_TYPE_CHOICES)

    class Meta:
        verbose_name = "Cost"
        verbose_name_plural = "Costs"
        ordering: ClassVar[list[str]] = ["-date", "-_created_at"]

    def __str__(self):
        course_info = f" - {self.course.name}" if self.course else ""
        return f"{self.title or self.description[:50]}{course_info} ({self.date})"

    def save(self, *args, **kwargs):
        # Auto-calculate total_amount if not provided
        if not self.total_amount:
            self.total_amount = self.amount * self.quantity
        super().save(*args, **kwargs)


class Income(TimeStampedModel):
    """Track course and company level incomes"""

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="incomes", blank=True, null=True)
    date = jmodels.jDateField()
    description = models.TextField()
    name = models.CharField(max_length=100, blank=True, null=True)
    user = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="incomes")
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])

    class Meta:
        verbose_name = "Income"
        verbose_name_plural = "Incomes"
        ordering: ClassVar[list[str]] = ["-date", "-_created_at"]

    def __str__(self):
        return f"{self.course} - {self.user.full_name} - {self.amount})"

    def save(self, *args, **kwargs):
        # Auto-calculate total_amount if not provided
        if not self.total_amount:
            self.total_amount = self.amount * self.quantity
        super().save(*args, **kwargs)


class FinancialAccount(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    course = models.ManyToManyField(Course, related_name="financial_accounts", blank=True)

    class Meta:
        verbose_name = "Financial Account"
        verbose_name_plural = "Financial Accounts"
        ordering: ClassVar[list[str]] = ["name"]

    def __str__(self):
        return f"{self.name} ({self.course.name if self.course else 'General'})"
