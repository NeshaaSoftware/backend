from typing import ClassVar

from django.contrib import admin

from .models import Registration


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display: ClassVar[list[str]] = [
        "participant",
        "course",
        "status",
        "payment_status",
        "registration_date",
    ]
    list_filter: ClassVar[list[str]] = ["status", "payment_status", "course", "registration_date"]
    search_fields: ClassVar[list[str]] = [
        "participant__full_name",
        "course__name",
        "participant__phone_number",
    ]
    readonly_fields: ClassVar[list[str]] = ["registration_date", "created_at", "updated_at"]

    fieldsets = (
        (
            "Registration Information",
            {"fields": ("participant", "course", "status", "registration_date")},
        ),
        (
            "Payment Information",
            {"fields": ("payment_status", "payment_amount", "payment_date")},
        ),
        ("Additional Information", {"fields": ("notes",)}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("participant", "course")
