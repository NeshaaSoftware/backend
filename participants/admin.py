from typing import ClassVar

from django.contrib import admin

from .models import Participant


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display: ClassVar[list[str]] = [
        "full_name",
        "phone_number",
        "email",
        "gender",
        "age",
        "joined_main_group",
        "created_at",
    ]
    list_filter: ClassVar[list[str]] = ["gender", "education", "joined_main_group", "created_at"]
    search_fields: ClassVar[list[str]] = ["full_name", "phone_number", "email", "telegram_id"]
    readonly_fields: ClassVar[list[str]] = ["created_at", "updated_at"]

    fieldsets = (
        (
            "Personal Information",
            {"fields": ("full_name", "gender", "age", "education", "occupation")},
        ),
        (
            "Contact Information",
            {"fields": ("phone_number", "fixed_phone", "email", "telegram_id")},
        ),
        ("Status", {"fields": ("joined_main_group",)}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )
