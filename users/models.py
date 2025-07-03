from typing import ClassVar

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from commons.models import TimeStampedModel

GENDER_CHOICES = [
    (1, "Male"),
    (2, "Female"),
    (3, "Other"),
]

EDUCATION_CHOICES = [
    (1, "High School"),
    (2, "Associate Degree"),
    (3, "Bachelor's Degree"),
    (4, "Master's Degree"),
    (5, "PhD"),
    (6, "Other"),
]

CRM_USER_STATUS_CHOICES = [
    (1, "نیاز به پیگیری"),
    (2, "در حال پیگیری"),
    (3, "پیگیری شده"),
]

CRM_LOG_ACTION_CHOICES = [(1, "تماس"), (2, "پیام")]


class User(AbstractUser, TimeStampedModel):
    phone_number = PhoneNumberField(null=False, blank=False, unique=True)
    more_phone_numbers = models.TextField(blank=True, null=True)
    telegram_id = models.CharField(max_length=50, blank=True, null=True)
    gender = models.IntegerField(choices=GENDER_CHOICES, blank=True, null=True, db_index=True)
    age = models.PositiveIntegerField(blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(120)])
    birth_date = models.DateField(blank=True, null=True)
    education = models.IntegerField(choices=EDUCATION_CHOICES, blank=True, null=True)
    profession = models.CharField(max_length=100, blank=True, null=True)
    english_first_name = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    english_last_name = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    referer = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="referrals")
    referer_name = models.CharField(max_length=100, blank=True, null=True)
    national_id = models.CharField(max_length=10, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    orgnization = models.ForeignKey(
        "Orgnization", on_delete=models.SET_NULL, null=True, blank=True, related_name="orgnization_users"
    )

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["phone_number"]

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-_created_at"]
        indexes = [
            models.Index(fields=["first_name"]),
            models.Index(fields=["last_name"]),
        ]

    def __str__(self):
        return f"{self.full_name} - {self.phone_number}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            from users.models import CrmUser

            if not hasattr(self, "crm_user"):
                CrmUser.objects.create(user=self)


class CrmUser(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="crm_user")
    support_user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="supported_users"
    )
    last_follow_up = models.DateTimeField(blank=True, null=True, db_index=True)
    next_follow_up = models.DateTimeField(blank=True, null=True, db_index=True)
    joined_main_group = models.BooleanField(default=False, db_index=True)
    crm_description = models.TextField(blank=True, null=True)
    status = models.IntegerField(choices=CRM_USER_STATUS_CHOICES, default=3, db_index=True)

    def __str__(self):
        return f"{self.user.full_name} - {self.id}"


class CrmLog(TimeStampedModel):
    crm = models.ForeignKey(CrmUser, on_delete=models.CASCADE, related_name="logs")
    description = models.TextField(blank=True, null=True)
    action = models.IntegerField(choices=CRM_LOG_ACTION_CHOICES, default=1, db_index=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name="crm_logs")

    def __str__(self):
        return f"{self.crm.user.full_name} - {self._created_at}"


class Orgnization(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    contact_user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="contacted_organizations"
    )

    def __str__(self):
        return self.name
