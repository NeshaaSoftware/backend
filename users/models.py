from typing import ClassVar

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from commons.models import TimeStampedModel


class User(AbstractUser, TimeStampedModel):
    GENDER_CHOICES: ClassVar[list[tuple[str, str]]] = [
        (1, "Male"),
        (2, "Female"),
        (3, "Other"),
    ]

    EDUCATION_CHOICES: ClassVar[list[tuple[str, str]]] = [
        (1, "High School"),
        (2, "Associate Degree"),
        (3, "Bachelor's Degree"),
        (4, "Master's Degree"),
        (5, "PhD"),
        (6, "Other"),
    ]

    phone_number = PhoneNumberField(null=False, blank=False, unique=True)
    more_phone_numbers = models.TextField(blank=True, null=True)
    telegram_id = models.CharField(max_length=50, blank=True, null=True)
    joined_main_group = models.BooleanField(default=False)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(120)])
    education = models.CharField(max_length=20, choices=EDUCATION_CHOICES, blank=True, null=True)
    profession = models.CharField(max_length=100, blank=True, null=True)
    english_first_name = models.CharField(max_length=50, blank=True, null=True)
    english_last_name = models.CharField(max_length=50, blank=True, null=True)
    referer = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="referrals")
    referer_name = models.CharField(max_length=100, blank=True, null=True)
    national_id = models.CharField(max_length=10, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["phone_number"]

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering: ClassVar[list[str]] = ["-_created_at"]

    def __str__(self):
        return f"{self.full_name} - {self.phone_number}"
