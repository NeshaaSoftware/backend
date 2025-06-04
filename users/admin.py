from typing import ClassVar

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display: ClassVar[list[str]] = [
        "id",
        "phone_number",
        "username",
        "email",
        "full_name",
        "gender",
        "age",
        "joined_main_group",
        "is_active",
        "_created_at",
    ]
    list_filter: ClassVar[list[str]] = [
        "gender",
        "education",
        "joined_main_group",
        "is_active",
        "is_staff",
        "is_superuser",
        "_created_at",
    ]
    search_fields: ClassVar[list[str]] = [
        "email",
        "username",
        "first_name",
        "last_name",
        "phone_number",
        "telegram_id",
    ]
    readonly_fields: ClassVar[list[str]] = ["_created_at", "_updated_at", "date_joined", "last_login"]
    ordering = ["-_created_at"]

    # Extend the default UserAdmin fieldsets
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "Personal Information",
            {
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "gender",
                    "age",
                    "education",
                    "description",
                )
            },
        ),
        (
            "Contact Information",
            {"fields": ("phone_number", "telegram_id")},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (
            "User Status",
            {"fields": ("joined_main_group",)},
        ),
        (
            "Important dates",
            {
                "fields": ("last_login", "date_joined", "_created_at", "_updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2"),
            },
        ),
        (
            "Personal Information",
            {
                "classes": ("wide",),
                "fields": ("first_name", "last_name", "phone_number"),
            },
        ),
    )
