from typing import ClassVar

from django.contrib import admin

from .models import Registration


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display: ClassVar[list[str]] = [
        "user",
        "course",
        "status",
        "payment_status",
        "registration_date",
    ]
    list_filter: ClassVar[list[str]] = [
        "status",
        "payment_status",
        "course",
        "registration_date",
    ]
    search_fields: ClassVar[list[str]] = [
        "user__full_name",
        "course__name",
        "user__phone_number",
    ]
    readonly_fields: ClassVar[list[str]] = [
        "registration_date",
        "_created_at",
        "_updated_at",
    ]

    fieldsets = (
        (
            "Registration Information",
            {"fields": ("user", "course", "status", "registration_date")},
        ),
        (
            "Payment Information",
            {"fields": ("payment_status", "payment_amount", "payment_date")},
        ),
        ("Additional Information", {"fields": ("notes",)}),
        (
            "Timestamps",
            {"fields": ("_created_at", "_updated_at"), "classes": ("collapse",)},
        ),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related("user", "course")
        user = request.user
        if user.is_superuser:
            return qs
        # If user is registration admin for any course, only show registrations for those courses
        managed_courses = user.managed_courses.all()
        if managed_courses.exists():
            return qs.filter(course__in=managed_courses)
        # Otherwise, show only their own registration (if any)
        return qs.filter(user=user)

    def has_view_permission(self, request, obj=None):
        user = request.user
        if user.is_superuser:
            return True
        if obj is None:
            return True  # List view handled by get_queryset
        # Only allow if user manages the course
        return obj.course in user.managed_courses.all()

    def has_change_permission(self, request, obj=None):
        user = request.user
        if user.is_superuser:
            return True
        if obj is None:
            return True  # List view handled by get_queryset
        # Only allow if user manages the course
        return obj.course in user.managed_courses.all()

    def has_delete_permission(self, request, obj=None):
        user = request.user
        if user.is_superuser:
            return True
        if obj is None:
            return True  # List view handled by get_queryset
        # Only allow if user manages the course
        return obj.course in user.managed_courses.all()
