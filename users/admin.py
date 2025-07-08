from dalf.admin import DALFModelAdmin, DALFRelatedFieldAjax
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.urls import reverse
from django.utils.html import format_html

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

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if not request.user.is_superuser:
            fieldsets = [fs for fs in fieldsets if fs[0] != "Permissions"]
            fieldsets = [
                (title, {**opts, "fields": tuple(f for f in opts["fields"] if f != "password")})
                if opts.get("fields") else (title, opts)
                for title, opts in fieldsets
            ]
        return fieldsets

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        try:
            user = self.model.objects.get(pk=object_id)
            crm_user = user.crm_user
            url = reverse("admin:users_crmuser_change", args=[crm_user.id])
            extra_context["crm_user_button"] = format_html(
                '<a class="button" href="{}";display:inline-block;">Go to CRM User</a>', url
            )
        except Exception:
            extra_context["crm_user_button"] = None
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

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


class CrmUserAdminForm(forms.ModelForm):
    first_name = User._meta.get_field('first_name').formfield()
    last_name = User._meta.get_field('last_name').formfield()
    email = User._meta.get_field('email').formfield()
    telegram_id = User._meta.get_field('telegram_id').formfield()
    age = User._meta.get_field('age').formfield()
    gender = User._meta.get_field('gender').formfield()
    education = User._meta.get_field('education').formfield()
    profession = User._meta.get_field('profession').formfield()
    more_phone_numbers = User._meta.get_field('more_phone_numbers').formfield()
    referer = User._meta.get_field('referer').formfield()
    referer_name = User._meta.get_field('referer_name').formfield()
    national_id = User._meta.get_field('national_id').formfield()
    country = User._meta.get_field('country').formfield()
    city = User._meta.get_field('city').formfield()
    orgnization = User._meta.get_field('orgnization').formfield()
    main_user = User._meta.get_field('main_user').formfield()

    new_fields = ["first_name", "last_name", "email", "telegram_id", "age", "gender", "education", "profession", "more_phone_numbers", "referer", "referer_name", "national_id", "country", "city", "orgnization", "main_user"]

    class Meta:
        model = CrmUser
        fields = "__all__"
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            for new_field in self.new_fields:
                self.fields[new_field].initial = getattr(self.instance.user, new_field, None)
            
    def save(self, commit=True):
        instance = super().save(commit=commit)
        for new_field in self.new_fields:
            setattr(instance.user, new_field, self.cleaned_data.get(new_field))
        instance.user.save()
        return instance
        

@admin.register(CrmUser)
class CrmUserAdmin(DetailedLogAdminMixin, DALFModelAdmin):
    form = CrmUserAdminForm
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
                    ("user", "registered_courses_list"),
                    ("first_name", "last_name"),
                    ("email", "telegram_id", "age", "gender", "education", "profession", "more_phone_numbers"),
                )
            }
        ),
        ("More info", {"fields": (("referer", "referer_name", "national_id", "country", "city", "orgnization", "main_user"),)}),
        ("Support", {"fields": (
            ("supporting_user", "status"),
            "joined_main_group",
            "last_follow_up",
            "next_follow_up",
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
        registrations = obj.user.registrations.select_related("course__course_type").filter(
            status__in=[3, 4, 5, 7, 8, 9]
        )
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
