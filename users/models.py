import abc

import jdatetime
import requests
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django_jalali.db import models as jmodels
from phonenumber_field.modelfields import PhoneNumberField

from commons.models import TimeStampedModel

GENDER_CHOICES = [
    (1, "مرد"),
    (2, "زن"),
    (3, "دیگر"),
]

EDUCATION_CHOICES = [
    (1, "کمتر از کارشناسی"),
    (2, "کارشناسی"),
    (3, "کارشناسی ارشد"),
    (4, "دکتری و بالاتر"),
    (5, "دیگر"),
]

CRM_USER_STATUS_CHOICES = [
    (1, "نیاز به پیگیری"),
    (2, "در حال پیگیری"),
    (3, "پیگیری شده"),
]

CRM_LOG_ACTION_CHOICES = [(1, "تماس موفق"), (2, "تماس ناموفق"), (3, "پیامک ارسال شد"), (4, "تلگرام ارسال شد")]


class Organization(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    contact_user = models.ForeignKey(
        "User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contacted_organizations",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class User(TimeStampedModel, AbstractUser):
    phone_number = PhoneNumberField(null=True, blank=True, unique=True)
    more_phone_numbers = models.TextField(blank=True, default="")
    telegram_id = models.CharField(max_length=50, blank=True, default="")
    gender = models.IntegerField(choices=GENDER_CHOICES, blank=True, null=True, db_index=True)
    age = models.PositiveIntegerField(blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(120)])
    birth_date = models.DateField(blank=True, null=True)
    education = models.IntegerField(choices=EDUCATION_CHOICES, blank=True, null=True)
    profession = models.CharField(max_length=100, blank=True, default="")
    english_first_name = models.CharField(max_length=50, blank=True, db_index=True)
    english_last_name = models.CharField(max_length=50, blank=True, db_index=True)
    referer = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="referrals")
    referer_name = models.CharField(max_length=100, blank=True)
    national_id = models.CharField(max_length=10, blank=True, default="")
    country = models.CharField(max_length=50, blank=True, default="")
    city = models.CharField(max_length=50, blank=True, default="")
    description = models.TextField(blank=True, null=True)
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, blank=True, related_name="organization_users")
    main_user = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="other_users")

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ["-_created_at"]
        indexes = [
            models.Index(fields=["first_name"]),
            models.Index(fields=["last_name"]),
            models.Index(fields=["phone_number"]),
            models.Index(fields=["national_id"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["first_name", "last_name", "phone_number"],
                name="unique_first_last_name_phone",
                nulls_distinct=False,
            ),
        ]

    def __str__(self):
        return f"{self.full_name} - {self.phone_number}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new and not hasattr(self, "crm_user"):
            CrmUser.objects.get_or_create(user=self)

    @property
    def _crm_user(self):
        crm_user = getattr(self, "crm_user", None)
        if crm_user is None:
            crm_user, _ = CrmUser.objects.get_or_create(user=self)
        return crm_user

    @staticmethod
    def get_education_from_text(education):
        if education in ["کمتر از کارشناسی"]:
            return 1
        elif education in ["کارشناسی"]:
            return 2
        elif education in ["کارشناسی ارشد"]:
            return 3
        elif education in ["دکتری و بالاتر"]:
            return 4
        return None

    @staticmethod
    def get_gender_from_text(gender):
        if gender in ["M", "m", "مرد", "آقا"]:
            return 1
        elif gender in ["F", "f", "زن", "خانم"]:
            return 2
        return None


class CrmUserLabel(TimeStampedModel):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class CrmUser(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="crm_user")
    supporting_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="supported_users")
    last_follow_up = jmodels.jDateTimeField(blank=True, null=True, db_index=True)
    next_follow_up = jmodels.jDateTimeField(blank=True, null=True, db_index=True)
    joined_main_group = models.BooleanField(default=False, db_index=True)
    crm_description = models.TextField(blank=True, null=True)
    crm_label = models.ManyToManyField(CrmUserLabel, blank=True, related_name="crm_users")
    status = models.IntegerField(choices=CRM_USER_STATUS_CHOICES, default=3, db_index=True)

    class Meta:
        ordering = ["-_created_at"]

    def __str__(self):
        return f"{self.user.full_name} - {self.pk}"


class CrmLog(TimeStampedModel):
    crm = models.ForeignKey(CrmUser, on_delete=models.CASCADE, related_name="logs")
    description = models.TextField(blank=True, null=True)
    action = models.IntegerField(choices=CRM_LOG_ACTION_CHOICES, default=1, db_index=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name="crm_logs")
    date = jmodels.jDateTimeField(blank=True, default=jdatetime.datetime.now, db_index=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.pk} - {self.crm.user.full_name} - {self.get_action_display()} - {self.date}"


class SMSLine(TimeStampedModel):
    provider = models.CharField(max_length=50, blank=True, default="")
    line_number = models.CharField(max_length=20, unique=True, db_index=True)

    class Meta:
        ordering = ["line_number"]

    def __str__(self):
        return str(self.line_number) if self.line_number else "No Line Number"

    @staticmethod
    def get_available_line():
        return SMSLine.objects.filter(line_number__isnull=False).first()


class SMSProvider:
    line_number = None

    __metaclass__ = abc.ABCMeta

    def _log_sms(self, text, recieve_number, result_json):
        SMSLog.objects.create(line_number=self.line_number, phone_number=recieve_number, text=text, status=0, response=result_json)

    @abc.abstractmethod
    def _send(self, text, recieve_number):
        pass

    def send(self, text, recieve_number):
        result_json = self._send(text, recieve_number)
        self._log_sms(text, recieve_number, result_json)


class ElanakSMSProvider(SMSProvider):
    url_template = (
        "https://payammatni.com/webservice/url/send.php?method=sendsms&format=json"
        "&from={line_number}&to={recieve_number}&text={text}&type=0"
        "&username={username}&password={password}"
    )

    def __init__(self, line_number):
        self.line_number = line_number

    def _send(self, text, recieve_number):
        url = self.url_template.format(
            line_number=self.line_number,
            recieve_number=recieve_number,
            text=text,
            username=settings.ELANAK_USERNAME,
            password=settings.ELANAK_PASSWORD,
        )
        result = requests.get(url, timeout=30)
        return result.json()


class SMSLog(TimeStampedModel):
    line_number = models.ForeignKey(
        SMSLine, on_delete=models.CASCADE, related_name="sms_logs", default=SMSLine.get_available_line, blank=True
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sms_logs", null=True, blank=True, db_index=True)
    phone_number = PhoneNumberField(db_index=True)
    text = models.TextField()
    status = models.IntegerField(choices=[(0, "Pending"), (1, "Sent"), (2, "Failed")], default=0, db_index=True)
    response = models.JSONField(blank=True, null=True)
    date = jmodels.jDateTimeField(blank=True, default=jdatetime.datetime.now, db_index=True)

    class Meta:
        ordering = ["-_created_at"]

    def __str__(self):
        return f"{self.phone_number} - {self.text[:30]} - {self.status} - {self.date}"
