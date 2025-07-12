from dal import autocomplete
from dalf.admin import DALFModelAdmin, DALFRelatedFieldAjax
from django import forms
from django.contrib import admin, messages
from django.db.models import Q
from django.shortcuts import render, redirect
from django.urls import path, reverse
from django.utils.html import format_html
from django_jalali.admin.filters import JDateFieldListFilter
import pandas as pd

from commons.admin import DetailedLogAdminMixin, DropdownFilter
from financials.admin import CourseTransactionInline

from .models import Attendance, Course, CourseSession, CourseType, Registration


class CourseSessionInline(admin.TabularInline):
    model = CourseSession
    extra = 1
    fields = [
        "session_name",
        "start_date",
        "end_date",
        "location",
    ]


@admin.register(Course)
class CourseAdmin(DetailedLogAdminMixin, DALFModelAdmin):
    list_display = [
        "course_name",
        "course_type",
        "number",
        "start_date",
        "price",
        "_created_at",
    ]
    list_filter = [
        ("course_type", DALFRelatedFieldAjax),
        ("number", DropdownFilter),
        ("supporting_users", DALFRelatedFieldAjax),
    ]
    search_fields = ["course_type__name_fa", "number", "course_name"]
    readonly_fields = ["_created_at", "_updated_at"]
    inlines = [CourseSessionInline]
    list_select_related = True
    ordering = ["-id"]
    autocomplete_fields = ["instructors", "supporting_users", "managing_users"]
    fieldsets = (
        (
            "Course Information",
            {"fields": (("course_name", "course_type", "number"), "price", ("start_date", "end_date"))},
        ),
        ("Administration", {"fields": ("managing_users", "supporting_users", "instructors")}),
        (
            "Timestamps",
            {"fields": ("_created_at", "_updated_at")},
        ),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related("managing_users", "supporting_users", "instructors")


@admin.register(CourseSession)
class CourseSessionAdmin(DetailedLogAdminMixin, DALFModelAdmin):
    list_display = [
        "session_name",
        "course",
        "start_date",
        "end_date",
        "location",
        "description",
        "_created_at",
        "_updated_at",
    ]
    list_filter = [
        ("start_date", JDateFieldListFilter),
        ("course", DALFRelatedFieldAjax),
    ]
    search_fields = ["session_name", "course__number", "course__course_type", "location", "description"]
    readonly_fields = ["_created_at", "_updated_at"]
    autocomplete_fields = ["course"]
    fieldsets = (
        (
            "Session Information",
            {"fields": ("session_name", "course", "start_date", "end_date", "location", "description")},
        ),
        (
            "Timestamps",
            {"fields": ("_created_at", "_updated_at"), "classes": ("collapse",)},
        ),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("course")


class RegistrationExcelUploadForm(forms.Form):
    excel_file = forms.FileField(label="Registration Excel File", required=True)
    sheet_name = forms.CharField(required=False, initial="Registeration")
    update_name = forms.BooleanField(initial=False, required=False)
    currency_to_toman_multiplier = forms.FloatField(
        initial=1000000,
        help_text="Multiplier to convert currency to Toman. Default is 1000 for Rials to Tomans.",
    )
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        widget=autocomplete.ModelSelect2(url="course-autocomplete"),
        label="Course",
        required=True,
        help_text="Select the course for which you are uploading registrations.",
    )


@admin.register(Registration)
class RegistrationAdmin(DetailedLogAdminMixin, DALFModelAdmin):
    list_display = [
        "user",
        "course",
        "status",
        "supporting_user",
        "payment_status",
        "tuition",
        "next_payment_date",
        "registration_date",
        "description",
        "payment_description",
        "_created_at",
        "_updated_at",
    ]
    list_filter = [
        "status",
        "payment_status",
        ("registration_date", JDateFieldListFilter),
        ("course", DALFRelatedFieldAjax),
    ]
    search_fields = [
        "user__phone_number",
        "course__number",
        "course__course_type__name",
    ]
    readonly_fields = [
        "user",
        "course",
        "registration_date",
        "_created_at",
        "_updated_at",
    ]
    autocomplete_fields = ["supporting_user"]
    fieldsets = (
        (
            "Registration Information",
            {"fields": ("user", "course", "status", "registration_date", "supporting_user")},
        ),
        (
            "Payment Information",
            {"fields": ("payment_status", "tuition", "next_payment_date", "payment_description")},
        ),
        ("Additional Information", {"fields": ("description",)}),
        (
            "Timestamps",
            {"fields": ("_created_at", "_updated_at")},
        ),
    )
    change_list_template = "admin/courses/registration/change_list.html"
    inlines = [CourseTransactionInline]

    def changelist_view(self, request, extra_context=None):
        if extra_context is None:
            extra_context = {}
        upload_url = reverse("admin:registration-upload-excel")
        extra_context["upload_excel_button"] = format_html(
            '<a class="button" href="{}";display:inline-block;">Upload Excel</a>', upload_url
        )
        return super().changelist_view(request, extra_context=extra_context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("upload-excel/", self.admin_site.admin_view(self.upload_excel), name="registration-upload-excel"),
        ]
        return custom_urls + urls

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        try:
            registration = self.model.objects.get(pk=object_id)
            url_user = reverse("admin:users_user_change", args=[registration.user.id])
            url_crm = reverse("admin:users_crmuser_change", args=[registration.user._crm_user.id])
            extra_context["user_button"] = format_html(
                '<a class="button" href="{}";display:inline-block;">Go to User</a>', url_user
            )
            extra_context["crm_user_button"] = format_html(
                '<a class="button" href="{}";display:inline-block;">Go to CRM User</a>', url_crm
            )
        except Exception:
            extra_context["crm_user_button"] = None
            extra_context["user_button"] = None
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def upload_excel(self, request):
        if request.method == "POST":
            form = RegistrationExcelUploadForm(request.POST, request.FILES)
            if form.is_valid():
                excel_file = request.FILES["excel_file"]
                sheet_name = form.cleaned_data.get("sheet_name")
                try:
                    df = pd.read_excel(excel_file, sheet_name=sheet_name)
                except Exception as e:
                    self.message_user(request, f"Error reading Excel file: {e}", level="error")
                    return redirect(request.path)
                if not request.POST.get("confirm_preview"):
                    preview_data = df.loc[:, ["fix phone", "نام", "نام خانوادگی"]]
                    preview_html = preview_data.to_html(index=False, classes="table table-bordered table-sm")
                    return render(
                        request,
                        "admin/courses/registration/upload_registration_excel.html",
                        {
                            "form": form,
                            "preview_html": preview_html,
                            "show_confirm": True,
                        },
                    )
                selected_course = form.cleaned_data["course"]
                update_name = form.cleaned_data.get("update_name")
                currency_to_toman_multiplier = form.cleaned_data.get("currency_to_toman_multiplier", 1000000)
                try:
                    import hashlib
                    from tqdm import tqdm

                    from commons.utils import get_national_id, get_status_from_text, normalize_phone
                    from courses.models import Registration
                    from users.models import User

                    df = pd.read_excel(excel_file, sheet_name=sheet_name, dtype={"fix phone": str, "سن": str})
                    df = df.where(pd.notnull(df), None)
                    good_phone = []
                    bad_phone = []
                    for phone in df["fix phone"]:
                        if len(str(phone).strip()) == 11 and str(phone).startswith("09"):
                            good_phone.append("+989" + phone[2:])
                        else:
                            bad_phone.append(phone)
                    good_phone = list(set(good_phone))
                    bad_phone = list(set(bad_phone))

                    users_dic = {
                        user[1]: user
                        for user in User.objects.all().values_list(
                            "id", "username", "first_name", "last_name", "phone_number"
                        )
                    }
                    users_dup_check = {
                        f"{u[2]}{u[3]}".replace(" ", ""): u for u in users_dic.values() if u[3] not in [None, ""]
                    }

                    def get_gender(gender):
                        if gender in ["M", "m", "مرد", "آقا"]:
                            return 1
                        elif gender in ["F", "f", "زن", "خانم"]:
                            return 2
                        return None

                    def get_education(education):
                        if education in ["کمتر از کارشناسی"]:
                            return 1
                        elif education in ["کارشناسی"]:
                            return 2
                        elif education in ["کارشناسی ارشد"]:
                            return 3
                        elif education in ["دکتری و بالاتر"]:
                            return 4
                        return None

                    done_registrations = Registration.objects.values_list("user_id", "course_id")
                    registration_dic = {f"{reg[0]}-{reg[1]}": True for reg in done_registrations}

                    bad_name = 0
                    made_users = 0
                    made_registration = 0
                    no_phone = 0
                    logs = []

                    for index, row in tqdm(df.iterrows(), total=df.shape[0]):
                        phone = normalize_phone(row["fix phone"])
                        first_name = row.get("نام", "")
                        if first_name:
                            first_name = first_name.strip()
                        last_name = row.get("نام خانوادگی", "")
                        if last_name:
                            last_name = last_name.strip()
                        telegram_id = row.get("تلگرام", None) or row.get("آی‌دی تلگرام", None) or ""
                        email = row.get("ایمیل", "") or ""
                        education = get_education(row.get("تحصیلات", ""))
                        profession = row.get("حرفه", "") or ""
                        age = row.get("سن", None)
                        gender = get_gender(row.get("جنسیت", None))
                        national_id = get_national_id(row.get("کد ملی", "")) or ""
                        english_first_name = row.get("Name", "") or ""
                        english_last_name = row.get("Surname", "") or ""
                        referer_name = row.get("معرف", None) or ""

                        if phone == "":
                            phone = None
                        if phone is None and first_name is None and last_name is None:
                            continue
                        last_name = last_name or ""

                        if phone is None:
                            name_hash = hashlib.sha256(f"{first_name}{last_name}".encode()).hexdigest()[:10]
                            username = f"from_upload_{name_hash}"
                            no_phone += 1
                            logs.append(["No Phone", str(index), str(first_name), str(last_name), str(phone)])
                        else:
                            username = phone
                        if username in users_dic:
                            user = users_dic[username]
                            if user[2] != first_name or user[3] != last_name:
                                bad_name += 1
                                logs.append(
                                    [
                                        "bad name",
                                        str(phone),
                                        str(user[2]),
                                        str(user[3]),
                                        str(first_name),
                                        str(last_name),
                                    ]
                                )
                                if update_name:
                                    User.objects.filter(username=username).update(
                                        first_name=first_name, last_name=last_name
                                    )

                        elif users_dup_check.get(f"{first_name}{last_name}".replace(" ", ""), None) is not None:
                            user = users_dup_check[f"{first_name}{last_name}".replace(" ", "")]
                            u = User.objects.get(id=user[0])
                            if user[4] is None:
                                u.phone_number = phone
                                u.username = username
                                users_dic[username] = [u.id, username, first_name, last_name, phone]
                                user = users_dic[username]
                            u.telegram_id = u.telegram_id if u.telegram_id not in [None, ""] else telegram_id
                            u.email = u.email if u.email not in [None, ""] else email
                            u.profession = u.profession if u.profession not in [None, ""] else profession
                            u.education = u.education if u.education not in [None, ""] else education
                            u.age = u.age if u.age not in [None, 0] else age
                            u.gender = u.gender if u.gender not in [None, ""] else gender
                            u.national_id = u.national_id if u.national_id not in [None, ""] else national_id
                            u.english_first_name = (
                                u.english_first_name if u.english_first_name not in [None, ""] else english_first_name
                            )
                            u.english_last_name = (
                                u.english_last_name if u.english_last_name not in [None, ""] else english_last_name
                            )
                            u.referer_name = u.referer_name if u.referer_name not in [None, ""] else referer_name
                            u.save()
                        else:
                            user = User.objects.create(
                                username=username,
                                phone_number=phone,
                                first_name=first_name,
                                last_name=last_name,
                                telegram_id=telegram_id,
                                email=email,
                                profession=profession,
                                education=education,
                                age=age,
                                gender=gender,
                                national_id=national_id,
                                english_first_name=english_first_name,
                                english_last_name=english_last_name,
                                referer_name=referer_name,
                            )
                            made_users += 1
                            user = [user.id, user.username, user.first_name, user.last_name, user.phone_number]
                            users_dup_check[f"{first_name}{last_name}".replace(" ", "")] = user
                            users_dic[username] = user
                        status, payment_status = get_status_from_text(row.get("وضعیت", None))
                        tuition = row.get("مبلغ نهایی", 0) or 0
                        tuition = float(tuition) * currency_to_toman_multiplier
                        if registration_dic.get(f"{user[0]}-{selected_course.id}", None) is not None:
                            continue
                        try:
                            Registration.objects.create(
                                user_id=user[0],
                                course=selected_course,
                                status=status,
                                payment_status=payment_status,
                                tuition=tuition,
                            )
                            registration_dic[f"{user[0]}-{selected_course.id}"] = True
                            made_registration += 1
                        except Exception as e:
                            logs.append(["Error", str(phone), str(user[2]), str(user[3]), row.get("نام"), str(e)])
                    self.message_user(
                        request,
                        "Registrations imported"
                        + " ".join(
                            [
                                "Done",
                                str(bad_name),
                                "bad name",
                                str(no_phone),
                                "no_phone",
                                str(made_registration),
                                "made registrations",
                                str(made_users),
                                "made users",
                            ]
                        )
                        + "\n".join([" ".join(log) for log in logs]),
                        messages.SUCCESS,
                    )
                except Exception as e:
                    import logging

                    logger = logging.getLogger(__name__)
                    logger.exception("Error importing registrations from Excel")
                    self.message_user(request, f"Error importing registrations: {e}", messages.ERROR)
                return redirect("..")
        else:
            form = RegistrationExcelUploadForm()
        context = {
            "form": form,
            **self.admin_site.each_context(request),
        }
        return render(request, "admin/courses/registration/upload_registration_excel.html", context)

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        user = request.user
        if user.is_superuser:
            return fieldsets
        if obj and obj.course.managing_users.filter(id=user.id).exists():
            return fieldsets
        filtered_fieldsets = []
        for name, options in fieldsets:
            if name == "Payment Information":
                continue
            filtered_fieldsets.append((name, options))
        return filtered_fieldsets

    def get_list_display(self, request):
        list_display = super().get_list_display(request)
        user = request.user
        if user.is_superuser:
            return list_display
        return [field for field in list_display if field != "payment_status"]

    def get_list_filter(self, request):
        list_filter = super().get_list_filter(request)
        user = request.user
        if user.is_superuser:
            return list_filter
        return [field for field in list_filter if field != "payment_status"]

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related("user", "course", "supporting_user")
        user = request.user
        if user.is_superuser:
            return qs
        return qs.filter(
            Q(course__managing_users=user) | Q(course__supporting_users=user) | Q(supporting_user=user) | Q(user=user)
        ).distinct()

    def _has_registration_permission(self, request, obj=None):
        user = request.user
        if user.is_superuser or obj is None:
            return True
        if obj.course.managing_users.filter(id=user.id).exists() or obj.supporting_user == user or obj.user == user:
            return True
        return False

    def has_view_permission(self, request, obj=None):
        return self._has_registration_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        return self._has_registration_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        user = request.user
        if user.is_superuser:
            return True
        if obj is None:
            return True
        return False


@admin.register(Attendance)
class AttendanceAdmin(DetailedLogAdminMixin, admin.ModelAdmin):
    list_display = [
        "user",
        "session",
        "attended_at",
        "_created_at",
        "_updated_at",
    ]
    list_filter = [("attended_at", JDateFieldListFilter)]
    search_fields = ["user__full_name", "session__session_name", "user__phone_number"]
    readonly_fields = ["user", "session", "attended_at", "_created_at", "_updated_at"]
    autocomplete_fields = ["user", "session"]
    fieldsets = (
        ("Attendance Information", {"fields": ("user", "session", "attended_at")}),
        ("Timestamps", {"fields": ("_created_at", "_updated_at"), "classes": ("collapse",)}),
    )

    def get_queryset(self, request):
        # Select related user and session for performance
        qs = super().get_queryset(request)
        return qs.select_related("user", "session")


@admin.register(CourseType)
class CourseTypeAdmin(DetailedLogAdminMixin, admin.ModelAdmin):
    list_display = ["name", "name_fa", "category", "description", "_created_at", "_updated_at"]
    search_fields = ["name", "name_fa", "description"]
    list_filter = ["category"]
    readonly_fields = ["_created_at", "_updated_at"]
