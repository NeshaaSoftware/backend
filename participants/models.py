from typing import ClassVar

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Participant(models.Model):
    """Participant information and details"""

    GENDER_CHOICES: ClassVar[list[tuple[str, str]]] = [
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    ]

    EDUCATION_CHOICES: ClassVar[list[tuple[str, str]]] = [
        ("high_school", "High School"),
        ("associate", "Associate Degree"),
        ("bachelor", "Bachelor's Degree"),
        ("master", "Master's Degree"),
        ("phd", "PhD"),
        ("other", "Other"),
    ]

    full_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=20, unique=True)
    fixed_phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=100, unique=True, blank=True, null=True)
    telegram_id = models.CharField(max_length=50, blank=True, null=True)
    joined_main_group = models.BooleanField(default=False)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(120)])
    education = models.CharField(max_length=20, choices=EDUCATION_CHOICES, blank=True, null=True)
    occupation = models.CharField(max_length=100, blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Participant"
        verbose_name_plural = "Participants"
        ordering: ClassVar[list[str]] = ["-created_at"]

    def __str__(self):
        return self.full_name
