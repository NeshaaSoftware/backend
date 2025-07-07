from dalf.admin import DALFModelAdmin, DALFRelatedFieldAjax
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from commons.admin import DetailedLogAdminMixin

from .models import CrmLog, CrmUser, Orgnization, User


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
        "username",
        "first_name",
        "last_name",
        "phone_number",
        "telegram_id",
    ]
    readonly_fields = ["_created_at", "_updated_at", "date_joined", "last_login"]
    ordering = ["-_created_at"]
    autocomplete_fields = ["referer"]
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
                    "birth_date",
                    "education",
                    "profession",
                    "english_first_name",
                    "english_last_name",
                    "description",
                )
            },
        ),
        (
            "Contact Information",
            {"fields": ("phone_number", "more_phone_numbers", "telegram_id")},
        ),
        (
            "Referral & National Info",
            {"fields": ("referer", "referer_name", "national_id")},
        ),
        (
            "Location & Organization",
            {"fields": ("country", "city", "orgnization")},
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

    def get_search_results(self, request, queryset, search_term):
        if request.GET.get("field_name") in ["supporting_user", "supporting_users", "managing_users", "instructors"]:
            queryset = queryset.filter(is_staff=True)
        return super().get_search_results(request, queryset, search_term)


class CrmLogInline(DetailedLogAdminMixin, admin.TabularInline):
    model = CrmLog
    extra = 1
    fields = ("id", "description", "action", "date", "user", "_created_at")
    readonly_fields = ("user", "_created_at")
    show_change_link = True


@admin.register(CrmUser)
class CrmUserAdmin(DetailedLogAdminMixin, DALFModelAdmin):
    autocomplete_fields = ("supporting_user",)
    list_display = ("user", "supporting_user", "status", "last_follow_up", "next_follow_up", "joined_main_group")
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
    select_related = ("user", "supporting_user")
    list_filter = (("supporting_user", DALFRelatedFieldAjax), "last_follow_up", "next_follow_up")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "user",
                    "registered_courses_list",
                    "supporting_user",
                    "status",
                    "last_follow_up",
                    "next_follow_up",
                    "joined_main_group",
                    "crm_description",
                )
            },
        ),
        ("Timestamps", {"fields": ("_created_at", "_updated_at")}),
    )

    def save_formset(self, request, form, formset, change):
        for form in formset.forms:
            if hasattr(form, "instance") and isinstance(form.instance, CrmLog):
                if form.has_changed():
                    form.instance.user = request.user
        super().save_formset(request, form, formset, change)

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


@admin.register(CrmLog)
class CrmLogAdmin(admin.ModelAdmin):
    list_display = ("id", "crm", "user", "action", "date", "description")
    search_fields = ("crm__user__username", "crm__user__phone_number", "user__username", "user__phone_number")
    autocomplete_fields = ("crm", "user")
