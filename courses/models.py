from typing import ClassVar

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models


class Course(models.Model):
    """Course information and details"""

    COURSE_TYPE_CHOICES: ClassVar[list[tuple[str, str]]] = [
        ("دوره‌های پیشوایی", "دوره‌های پیشوایی"),
        ("دوره‌های رابطه", "دوره‌های رابطه"),
        ("دوره‌های مواجهه", "دوره‌های مواجهه"),
        ("تحویل سال دگرگون", "تحویل سال دگرگون"),
        ("جان کلام", "جان کلام"),
        ("پویش", "پویش"),
        ("پیله", "پیله"),
    ]

    name = models.CharField(max_length=100)
    course_type = models.CharField(max_length=50, choices=COURSE_TYPE_CHOICES, default="دوره‌های پیشوایی")
    course_number = models.CharField(max_length=10, default="1")
    fee = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    # Relationships
    admin_users = models.ManyToManyField(User, blank=True, related_name="managed_courses")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Course"
        verbose_name_plural = "Courses"
        ordering: ClassVar[list[str]] = ["-created_at"]
        unique_together: ClassVar[list[list[str]]] = ["course_type", "course_number"]

    def __str__(self):
        return f"{self.name} - {self.course_type} #{self.course_number}"


class CourseSession(models.Model):
    """Course session component"""

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="sessions")
    session_name = models.CharField(max_length=100)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    max_participants = models.PositiveIntegerField(blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Course Session"
        verbose_name_plural = "Course Sessions"
        ordering: ClassVar[list[str]] = ["start_date"]

    def __str__(self):
        return f"{self.course.name} - {self.session_name}"
