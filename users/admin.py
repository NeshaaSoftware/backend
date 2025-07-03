from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from commons.admin import DetailedLogAdminMixin

from .models import CrmLog, CrmUser, Orgnization, User


class CrmLogInline(admin.TabularInline):
    model = CrmLog
    extra = 1
    fields = ("description", "user", "action", "_created_at", "_updated_at")
    readonly_fields = ("_created_at", "_updated_at", "user")
    show_change_link = True


@admin.register(User)
class UserAdmin(DetailedLogAdminMixin, DjangoUserAdmin):
    list_display = [
        "id",
        "phone_number",
        "username",
        "email",
        "full_name",
        "gender",
        "age",
        "is_active",
        "_created_at",
    ]
    list_filter = [
        "gender",
        "education",
        "is_active",
        "is_staff",
        "is_superuser",
        "_created_at",
    ]
    search_fields = [
        "email",
        "username",
        "first_name",
        "last_name",
        "phone_number",
        "telegram_id",
    ]
    readonly_fields = ["_created_at", "_updated_at", "date_joined", "last_login"]
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


@admin.register(CrmUser)
class CrmUserAdmin(admin.ModelAdmin):
    autocomplete_fields = ("support_user",)
    list_display = ("user",)
    readonly_fields = ("_created_at", "_updated_at", "user", "registered_courses_list")
    search_fields = (
        "user__username",
        "user__phone_number",
        "user__first_name",
        "user__last_name",
        "user__email",
        "user__telegram_id",
    )
    inlines = [CrmLogInline]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "user",
                    "registered_courses_list",
                    "support_user",
                    "status",
                    "last_follow_up",
                    "next_follow_up",
                    "joined_main_group",
                    "crm_description",
                )
            },
        ),
        ("Timestamps", {"fields": ("_created_at", "_updated_at"), "classes": ("collapse",)}),
    )

    def save_formset(self, request, form, formset, change):
        super().save_formset(request, form, formset, change)
        if hasattr(formset, "new_objects") and hasattr(formset, "model") and formset.model is CrmLog:
            for obj in formset.new_objects:
                if hasattr(obj, "user") and not obj.user_id:
                    obj.user = request.user
                    obj.save()

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("user")

    @admin.display(description="Registered Courses")
    def registered_courses_list(self, obj):
        registrations = obj.user.registrations.select_related("course__course_type").all()
        return (
            ", ".join(
                [
                    f"{reg.course.course_type.name_fa or reg.course.course_type.name} {reg.course.number}"
                    for reg in registrations
                ]
            )
            or "-"
        )

    @admin.display(description="Phone Number")
    def user_phone_number(self, obj):
        return obj.user.phone_number

    @admin.display(description="Full Name")
    def user_full_name(self, obj):
        return (
            obj.user.get_full_name()
            if hasattr(obj.user, "get_full_name")
            else f"{obj.user.first_name} {obj.user.last_name}"
        )

    @admin.display(description="Email")
    def user_email(self, obj):
        return obj.user.email

    @admin.display(description="Telegram ID")
    def user_telegram_id(self, obj):
        return obj.user.telegram_id


@admin.register(Orgnization)
class OrgnizationAdmin(admin.ModelAdmin):
    autocomplete_fields = ("contact_user",)
    list_display = ("name", "contact_user")
    search_fields = ("name", "contact_user__username", "contact_user__phone_number")
