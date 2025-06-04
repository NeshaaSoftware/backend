from typing import ClassVar

from django.conf import settings
from django.db import models

from commons.models import LoggedTimeStampedModel
from courses.models import Course
from users.models import User


class Registration(LoggedTimeStampedModel):

    STATUS_CHOICES: ClassVar[list[tuple[str, str]]] = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="registration")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="registrations")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    registration_date = models.DateTimeField(auto_now_add=True)
    payment_status = models.BooleanField(default=False)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    payment_date = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Registration"
        verbose_name_plural = "Registrations"
        ordering: ClassVar[list[str]] = ["-registration_date"]
        unique_together: ClassVar[list[list[str]]] = [["user", "course"]]

    def __str__(self):
        return f"{self.user.full_name or self.user.email} - {self.course.name}"
