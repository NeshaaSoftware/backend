from typing import ClassVar

from django.db import models
from django_jalali.db import models as jmodels

from commons.models import TimeStampedModel
from users.models import User


class Course(TimeStampedModel):
    """Course information and details"""

    COURSE_TYPE_CHOICES: ClassVar[list[tuple[int, str]]] = [
        (1, "دوره‌های پیشوایی"),
        (2, "دوره‌های رابطه"),
        (3, "دوره‌های مواجهه"),
        (4, "تحویل سال دگرگون"),
        (5, "جان کلام"),
        (6, "پویش"),
        (7, "پیله"),
    ]

    course_type = models.IntegerField(choices=COURSE_TYPE_CHOICES, default="دوره‌های پیشوایی")
    number = models.IntegerField()
    price = models.JSONField(blank=True, null=True, db_index=True)
    instructors = models.ManyToManyField(
        User,
        blank=True,
        related_name="instructed_courses",
        help_text="Users who are instructors for this course.",
    )
    managing_users = models.ManyToManyField(
        User,
        blank=True,
        related_name="managed_courses",
    )

    assisting_users = models.ManyToManyField(
        User,
        blank=True,
        related_name="assisted_courses",
    )

    class Meta:
        verbose_name = "Course"
        verbose_name_plural = "Courses"
        ordering: ClassVar[list[str]] = ["-_created_at"]
        unique_together: ClassVar[list[list[str]]] = ["course_type", "number"]

    @property
    def instructors_names(self):
        return [user.full_name or user.username or user.phone_number for user in self.instructors.all()]

    @property
    def name(self):
        return f"{self.get_course_type_display()} - {self.number}"

    def __str__(self):
        return f"{self.name}"


class CourseSession(TimeStampedModel):
    """Course session component"""

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="sessions")
    session_name = models.CharField(max_length=100)
    start_date = jmodels.jDateTimeField()
    end_date = jmodels.jDateTimeField()
    location = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Course Session"
        verbose_name_plural = "Course Sessions"
        ordering: ClassVar[list[str]] = ["start_date"]

    def __str__(self):
        return f"{self.course.name} - {self.session_name}"


class Registration(TimeStampedModel):
    STATUS_CHOICES: ClassVar[list[tuple[str, str]]] = [
        (1, "Pending"),
        (2, "Confirmed"),
        (3, "Cancelled"),
        (4, "Completed"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="registration")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="registrations")
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)
    registration_date = jmodels.jDateTimeField(auto_now_add=True)
    payment_status = models.BooleanField(default=False)
    payment_amount = models.IntegerField(default=0)
    next_payment_date = jmodels.jDateTimeField(blank=True, null=True)
    assistant = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="assisted_registrations", blank=True, null=True
    )
    notes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Registration"
        verbose_name_plural = "Registrations"
        ordering: ClassVar[list[str]] = ["-registration_date"]
        unique_together: ClassVar[list[list[str]]] = [["user", "course"]]

    def __str__(self):
        return f"{self.user.full_name or self.user.phone_number} - {self.course.name}"


class Attendence(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="attendances")
    session = models.ForeignKey(CourseSession, on_delete=models.CASCADE, related_name="attendances")
    attended_at = jmodels.jDateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Attendance"
        verbose_name_plural = "Attendances"
        ordering: ClassVar[list[str]] = ["-attended_at"]
        unique_together: ClassVar[list[list[str]]] = [["user", "session"]]

    def __str__(self):
        return f"{self.user.full_name or self.user.phone_number} - {self.session.session_name}"
