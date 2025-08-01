from django.db import models
from django_jalali.db import models as jmodels

from commons.models import TimeStampedModel
from commons.utils import get_jdatetime_now_with_timezone
from users.models import User

STATUS_CHOICES = [
    (1, "در انتظار ثبت‌نام"),
    (2, "انصراف پیش از دوره"),
    (3, "انتخاب نماندن"),
    (4, "ترک دوره"),
    (5, "حاضر در دوره"),
    (6, "اخراج از دوره"),
    (7, "تیم اجرایی"),
    (8, "مهمان"),
    (9, "تکمیل دوره"),
]

PAYMENT_STATUS_CHOICES = [
    (1, "عدم سررسید"),
    (2, "در انتظار پرداخت"),
    (3, "تسویه"),
]

PAYMENT_TYPE_CHOICES = [
    (1, "نقدی"),
    (2, "اقساطی"),
    (3, "رایگان"),
    (4, "سازمانی"),
]


class CourseType(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    name_fa = models.CharField(max_length=100, unique=True, blank=True)
    category = models.IntegerField(
        choices=[
            (1, "دوره"),
            (2, "پویش"),
            (3, "دیدار"),
            (4, "سمینار"),
        ],
        default=1,
        db_index=True,
    )
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name_fa or self.name


class Course(TimeStampedModel):
    course_type = models.ForeignKey(CourseType, on_delete=models.CASCADE, related_name="courses", db_index=True)
    course_name = models.CharField(max_length=100, blank=True, db_index=True)
    number = models.IntegerField(db_index=True)
    price = models.JSONField(blank=True, default=dict)
    start_date = jmodels.jDateTimeField(blank=True, null=True, db_index=True)
    end_date = jmodels.jDateTimeField(blank=True, null=True)
    instructors = models.ManyToManyField(
        User,
        blank=True,
        related_name="instructed_courses",
    )
    managing_users = models.ManyToManyField(
        User,
        blank=True,
        related_name="managed_courses",
    )
    supporting_users = models.ManyToManyField(
        User,
        blank=True,
        related_name="supported_courses",
    )

    class Meta:
        ordering = ["-_created_at"]
        unique_together = ["course_type", "number"]

    @property
    def instructors_names(self):
        return [user.full_name or user.username or user.phone_number for user in self.instructors.all()]

    def __str__(self):
        return self.course_name


class CourseSession(TimeStampedModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="sessions")
    session_name = models.CharField(max_length=100)
    start_date = jmodels.jDateTimeField()
    end_date = jmodels.jDateTimeField()
    location = models.CharField(max_length=200, blank=True, default="")
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["start_date"]

    def __str__(self):
        return f"{self.session_name} ({self.course.course_name})"


class Registration(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="registrations")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="registrations")
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)
    registration_date = jmodels.jDateTimeField(blank=True, default=get_jdatetime_now_with_timezone)
    initial_price = models.PositiveIntegerField(default=0, help_text="تومان")
    discount = models.PositiveIntegerField(default=0, help_text="تومان")
    vat = models.PositiveIntegerField(default=0, help_text="تومان")
    tuition = models.IntegerField(default=0, help_text="تومان")
    invoice_item = models.ForeignKey(
        "financials.InvoiceItem",
        on_delete=models.SET_NULL,
        related_name="registrations",
        null=True,
        blank=True,
    )
    payment_status = models.IntegerField(choices=PAYMENT_STATUS_CHOICES, default=3)
    payment_type = models.IntegerField(choices=PAYMENT_TYPE_CHOICES, default=1)
    paid_amount = models.PositiveIntegerField(default=0, help_text="تومان")
    next_payment_date = jmodels.jDateTimeField(blank=True, null=True)
    supporting_user = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="supported_registrations", blank=True, null=True
    )
    description = models.TextField(blank=True, null=True)
    payment_description = models.TextField(blank=True, null=True)
    joined_group = models.BooleanField(default=False, help_text="عضویت در گروه دوره")

    class Meta:
        ordering = ["-registration_date"]
        unique_together = ["user", "course"]

    @property
    def status_display(self):
        return dict(STATUS_CHOICES)[self.status]

    def _paid_amount(self):
        return (self.transactions.filter(transaction_type=1).aggregate(total=models.Sum("amount"))["total"] or 0) - (
            self.transactions.filter(transaction_type=2).aggregate(total=models.Sum("amount"))["total"] or 0
        )

    def __str__(self):
        return f"{self.user} - {self.course} ({self.status_display})"

    def update_paid_amount(self, commit=True):
        self.paid_amount = self._paid_amount()
        if commit:
            self.save(update_fields=["paid_amount"])


class Attendance(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="attendances")
    session = models.ForeignKey(CourseSession, on_delete=models.CASCADE, related_name="attendances")
    attended_at = jmodels.jDateTimeField(blank=True, default=get_jdatetime_now_with_timezone)

    class Meta:
        verbose_name = "Attendance"
        verbose_name_plural = "Attendances"
        ordering = ["-attended_at"]
        unique_together = ["user", "session"]

    def __str__(self):
        return f"{self.user.full_name or self.user.phone_number} - {self.session.session_name}"


TEAM_STATUS_CHOICES = [
    (1, "اعلام شوق"),
    (2, "گفت‌وگو انجام شد"),
    (3, "رد شده"),
    (4, "تایید شده"),
    (5, "انصراف"),
]


class CourseTeam(TimeStampedModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="teams")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="course_teams")
    status = models.IntegerField(choices=TEAM_STATUS_CHOICES, default=1)

    class Meta:
        unique_together = ["course", "user"]
        ordering = ["-id"]

    def __str__(self):
        return f"{self.user.full_name or self.user.phone_number} - {self.course.course_name})"
