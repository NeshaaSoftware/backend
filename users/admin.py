import pandas as pd
from dalf.admin import DALFModelAdmin, DALFRelatedFieldAjax
from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import path, reverse
from django.utils.html import format_html
from django_jalali.admin.filters import JDateFieldListFilter

from commons.admin import DetailedLogAdminMixin
from commons.utils import get_jdatetime_now_with_timezone, normalize_phone
from courses.admin import CourseTeamInline

from .models import CrmLog, CrmUser, CrmUserLabel, Organization, User
from .permissions import ManagingGroupPermissionMixin, requires_managing_group_permission


@admin.register(User)
class UserAdmin(DetailedLogAdminMixin, DjangoUserAdmin):
    list_display = ["id", "phone_number", "username", "email", "full_name", "gender", "age", "is_active", "_created_at"]
    list_filter = ["gender", "education", "is_active", "is_staff", "is_superuser", "_created_at"]
    search_fields = ["username", "first_name", "last_name", "phone_number", "telegram_id"]
    readonly_fields = ["_created_at", "_updated_at", "date_joined", "last_login"]
    ordering = ["-id"]
    inlines = [CourseTeamInline]
    autocomplete_fields = ["referer", "main_user"]
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
                    "main_user",
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
            {"fields": ("country", "city", "organization")},
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
                if opts.get("fields")
                else (title, opts)
                for title, opts in fieldsets
            ]
        return fieldsets

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        try:
            user = self.model.objects.get(pk=object_id)
            url = reverse("admin:users_crmuser_change", args=[user._crm_user.id])
            extra_context["crm_user_button"] = format_html('<a class="button" href="{}" style="display:inline-block;">Go to CRM User</a>', url)
        except Exception:
            extra_context["crm_user_button"] = None
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def get_search_results(self, request, queryset, search_term):
        if request.GET.get("field_name") in ["supporting_user", "supporting_users", "managing_users", "instructors"]:
            queryset = queryset.filter(is_staff=True)
        return super().get_search_results(request, queryset, search_term)

    def get_model_perms(self, request):
        if not request.user.is_superuser:
            return {}
        return super().get_model_perms(request)


class CrmLogInline(DetailedLogAdminMixin, admin.TabularInline):
    model = CrmLog
    extra = 1
    fields = ("id", "description", "action", "date", "user", "_created_at")
    readonly_fields = ("user", "_created_at")
    show_change_link = True


class CrmUserAdminForm(forms.ModelForm):
    first_name = User._meta.get_field("first_name").formfield()
    last_name = User._meta.get_field("last_name").formfield()
    email = User._meta.get_field("email").formfield()
    telegram_id = User._meta.get_field("telegram_id").formfield()
    age = User._meta.get_field("age").formfield()
    gender = User._meta.get_field("gender").formfield()
    education = User._meta.get_field("education").formfield()
    profession = User._meta.get_field("profession").formfield()
    more_phone_numbers = User._meta.get_field("more_phone_numbers").formfield()
    referer = User._meta.get_field("referer").formfield(
        widget=admin.widgets.AutocompleteSelect(User._meta.get_field("referer"), admin.site)
    )
    referer_name = User._meta.get_field("referer_name").formfield()
    national_id = User._meta.get_field("national_id").formfield()
    country = User._meta.get_field("country").formfield()
    city = User._meta.get_field("city").formfield()
    organization = User._meta.get_field("organization").formfield(
        widget=admin.widgets.AutocompleteSelect(User._meta.get_field("organization"), admin.site)
    )
    main_user = User._meta.get_field("main_user").formfield(
        widget=admin.widgets.AutocompleteSelect(User._meta.get_field("main_user"), admin.site)
    )

    new_fields = [
        "first_name",
        "last_name",
        "email",
        "telegram_id",
        "age",
        "gender",
        "education",
        "profession",
        "more_phone_numbers",
        "referer_name",
        "referer",
        "national_id",
        "country",
        "city",
        "organization",
        "main_user",
    ]
    new_readonly_fields = []

    class Meta:
        model = CrmUser
        fields = "__all__"  # noqa

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            for new_field in self.new_fields:
                self.fields[new_field].initial = getattr(self.instance.user, new_field, None)
            for read_only_field in self.new_readonly_fields:
                self.fields[read_only_field].initial = getattr(self.instance.user, read_only_field, None)
                self.fields[read_only_field].widget.attrs["readonly"] = True

    def save(self, commit=True):
        instance = super().save(commit=commit)
        for new_field in self.new_fields:
            setattr(instance.user, new_field, self.cleaned_data.get(new_field))
        instance.user.save()
        return instance


class CrmUserLabelSetForm(forms.Form):
    excel_file = forms.FileField(
        label="labeling excel file contain <first name> <last name> <user phone> <support phone>", required=True
    )


@admin.register(CrmUserLabel)
class CrmUserLabelAdmin(ManagingGroupPermissionMixin, admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ["id"]

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        try:
            if self.has_managing_group_permission(request):
                extra_context["show_set_crm"] = True
                set_crm_url = reverse("admin:user_set_crm_view", args=[object_id])
                extra_context["set_crm_button"] = format_html(
                    '<a class="button" href="{}" style="display:inline-block;">Set CRM Users</a>', set_crm_url
                )
                extra_context["show_export_crms"] = True
                export_url = reverse("admin:user_export_crm_view", args=[object_id])
                extra_context["export_button"] = format_html('<a class="button" href="{}" style="display:inline-block;">Export CRMs</a>', export_url)
        except CrmUserLabel.DoesNotExist:
            pass

        return super().change_view(request, object_id, form_url, extra_context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:label_id>/set-crm/",
                self.admin_site.admin_view(self.set_crm_view),
                name="user_set_crm_view",
            ),
            path(
                "<int:label_id>/export-crms/",
                self.admin_site.admin_view(self.export_crms),
                name="user_export_crm_view",
            ),
        ]
        return custom_urls + urls

    @requires_managing_group_permission
    def export_crms(self, request, label_id):
        try:
            crm_label = CrmUserLabel.objects.get(pk=label_id)
            crms = CrmUser.objects.filter(crm_label=crm_label).select_related("user")
            data = []
            for crm in crms:
                data.append(
                    {
                        "first name": crm.user.first_name,
                        "last name": crm.user.last_name,
                        "phone": getattr(crm.user, "phone_number", ""),
                        "supporting user": crm.supporting_user.phone_number if crm.supporting_user else None,
                        "supporting user name": f"{crm.supporting_user.first_name} {crm.supporting_user.last_name}"
                        if crm.supporting_user
                        else "",
                    }
                )
            df = pd.DataFrame(data)
            response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            response["Content-Disposition"] = f'attachment; filename="{crm_label.name}.xlsx"'
            from io import BytesIO

            excel_buffer = BytesIO()
            with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="data")
            excel_buffer.seek(0)
            response.write(excel_buffer.getvalue())

            messages.success(request, f"فایل اکسل یوزرهای  {crm_label.name} با موفقیت ایجاد شد.")
            return response

        except CrmUserLabel.DoesNotExist:
            messages.error(request, "برچسب مورد نظر یافت نشد.")
            return redirect("..")
        except Exception as e:
            messages.error(request, f"خطا در ایجاد فایل اکسل: {e!s}")
            return redirect("..")

    @requires_managing_group_permission
    def set_crm_view(self, request, label_id):
        if request.method == "POST":
            crm_label = CrmUserLabel.objects.get(pk=label_id)
            form = CrmUserLabelSetForm(request.POST, request.FILES)
            if form.is_valid():
                excel_file = request.FILES["excel_file"]
                try:
                    df = pd.read_excel(
                        excel_file, dtype={"first name": str, "last name": str, "user phone": str, "support phone": str}
                    )
                    df = df.dropna(how="all", subset=["user phone"])
                except Exception as e:
                    self.message_user(request, f"Error reading excel file: {e}", level="error")
                    return redirect(request.path)
                if not request.POST.get("confirm_preview"):
                    try:
                        preview_data = df.loc[:, ["first name", "last name", "user phone", "support phone"]]
                        preview_html = preview_data.to_html(index=False, classes="table table-bordered table-sm")
                        return render(
                            request,
                            "admin/users/crmuserlabel/set_crm.html",
                            {
                                "form": form,
                                "preview_html": preview_html,
                                "show_confirm": True,
                            },
                        )
                    except Exception as e:
                        self.message_user(request, f"Error generating preview: {e}", level="error")
                        return redirect(request.path)
                support_map = {}
                phones = []
                for _, row in df.iterrows():
                    user_phone = normalize_phone(row["user phone"])
                    first_name = row.get("first name", "").strip()
                    last_name = row.get("last name", "").strip()
                    support_phone = normalize_phone(row["support phone"])
                    support_map[user_phone] = {"support": support_phone, "first_name": first_name, "last_name": last_name}
                    phones.append(user_phone)
                    phones.append(support_phone)
                phones = list(set(phones))
                crm_map = {
                    c.user.phone_number: c for c in CrmUser.objects.filter(user__phone_number__in=phones).select_related("user")
                }
                for user_phone, data in support_map.items():
                    if crm_map.get(user_phone, None) is None:
                        user = User.objects.create(
                            username=user_phone,
                            first_name=data["first_name"],
                            last_name=data["last_name"],
                            phone_number=user_phone,
                        )
                        crm_user = user._crm_user
                        crm_map[user_phone] = crm_user
                    else:
                        crm_user = crm_map.get(user_phone)
                    if str(data.get("support", None)) not in ["", "None", "Nan", "NaN", "nan"]:
                        crm_support = crm_map.get(data.get("support", None))
                        if crm_user.supporting_user is None:
                            crm_user.supporting_user = crm_support.user
                            crm_user.save()
                crm_label.crm_users.add(*[crm_map.get(phone) for phone in support_map.keys()])
                self.message_user(request, f"# {len(support_map)} updated with label {crm_label.name}")
                return redirect("..")
        else:
            form = CrmUserLabelSetForm()
        context = {
            "form": form,
            **self.admin_site.each_context(request),
        }
        return render(request, "admin/users/crmuserlabel/set_crm.html", context)


@admin.register(CrmUser)
class CrmUserAdmin(DetailedLogAdminMixin, DALFModelAdmin):
    form = CrmUserAdminForm
    autocomplete_fields = ("supporting_user", "crm_label")
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
    ordering = ["id"]
    select_related = ("user", "supporting_user")
    list_filter = (
        ("supporting_user", DALFRelatedFieldAjax),
        "last_follow_up",
        "next_follow_up",
        "status",
        ("crm_label", DALFRelatedFieldAjax),
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    ("user", "registered_courses_list"),
                    ("first_name", "last_name"),
                    ("email", "telegram_id", "age", "gender", "education", "profession", "more_phone_numbers"),
                )
            },
        ),
        (
            "More info",
            {"fields": (("referer", "referer_name", "national_id", "country", "city", "organization", "main_user"),)},
        ),
        (
            "Support",
            {
                "fields": (
                    ("supporting_user", "status"),
                    ("joined_main_group", "crm_label"),
                    "last_follow_up",
                    "next_follow_up",
                    "crm_description",
                )
            },
        ),
        ("Timestamps", {"fields": (("_created_at", "_updated_at"),)}),
    )

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser or request.user.groups.filter(name=settings.MANAGING_GROUP_NAME).exists():
            return super().get_readonly_fields(request, obj)
        return (*self.readonly_fields, "supporting_user")

    def save_formset(self, request, form, formset, change):
        crm_user = form.instance
        last_follow_up_updated = False

        for form_instance in formset.forms:
            if hasattr(form_instance, "instance") and isinstance(form_instance.instance, CrmLog):
                if form_instance.has_changed():
                    form_instance.instance.user = request.user
                if form_instance.instance.date is None:
                    form_instance.instance.date = get_jdatetime_now_with_timezone()
                if form_instance.instance.date and (
                    not crm_user.last_follow_up or form_instance.instance.date > crm_user.last_follow_up
                ):
                    crm_user.last_follow_up = form_instance.instance.date
                    last_follow_up_updated = True

        super().save_formset(request, form, formset, change)

        if last_follow_up_updated:
            crm_user.save()

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related("user")
        if request.user.is_superuser or request.user.groups.filter(name=settings.MANAGING_GROUP_NAME).exists():
            return qs
        return qs.filter(supporting_user=request.user)

    @admin.display(description="Registered Courses")
    def registered_courses_list(self, obj):
        registrations = obj.user.registrations.select_related("course__course_type").filter(status__in=[3, 4, 5, 7, 8, 9])
        return (
            ", ".join(
                [
                    f"{reg.course.course_type.name_fa or reg.course.course_type.name} {reg.course.number} - {reg.status_display}"
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


@admin.register(Organization)
class OrganizationAdmin(DetailedLogAdminMixin, DALFModelAdmin):
    autocomplete_fields = ("contact_user",)
    list_display = ("name", "contact_user")
    search_fields = ("name", "contact_user__username", "contact_user__phone_number")


@admin.register(CrmLog)
class CrmLogAdmin(DetailedLogAdminMixin, DALFModelAdmin):
    list_display = ("id", "crm", "user", "action", "date", "description")
    list_filter = ("action", ("crm", DALFRelatedFieldAjax), ("user", DALFRelatedFieldAjax), ("date", JDateFieldListFilter))
    search_fields = ("crm__user__username", "crm__user__phone_number", "user__username", "user__phone_number")
    autocomplete_fields = ("crm", "user")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            return qs.none()
        return qs

    def get_model_perms(self, request):
        if not request.user.is_superuser:
            return {}
        return super().get_model_perms(request)
