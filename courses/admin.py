import hashlib
import logging
import pandas as pd
from dal import autocomplete
from dalf.admin import DALFModelAdmin, DALFRelatedFieldAjax
from django import forms
from django.contrib import admin, messages
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import path, reverse
from django.utils.html import format_html
from django_jalali.admin.filters import JDateFieldListFilter

from commons.admin import DetailedLogAdminMixin, DropdownFilter
from financials.admin import CourseTransactionInline
from financials.models import FinancialAccount

from .models import (
    PAYMENT_STATUS_CHOICES,
    PAYMENT_TYPE_CHOICES,
    Attendance,
    Course,
    CourseSession,
    CourseType,
    Registration,
)
from .permissions import CoursePermissionMixin, requires_course_managing_permission


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
class CourseAdmin(DetailedLogAdminMixin, CoursePermissionMixin, DALFModelAdmin):
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

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}

        try:
            course = Course.objects.get(pk=object_id)
            if self.has_course_manage_permission(request, course):
                extra_context["show_export_registrations"] = True

                export_url = reverse("admin:courses_course_export_registrations", args=[object_id])
                extra_context["export_button"] = format_html(
                    '<a class="button" href="{}" style="display:inline-block;">export registrations</a>', export_url
                )
        except Course.DoesNotExist:
            pass

        return super().change_view(request, object_id, form_url, extra_context)


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
        ("Timestamps", {"fields": ("_created_at", "_updated_at"), "classes": ("collapse",)}),
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
        queryset=Course.objects.select_related('course_type'),
        widget=autocomplete.ModelSelect2(url="course-autocomplete"),
        label="Course",
        required=True,
        help_text="Select the course for which you are uploading registrations.",
    )


class RegistrationSazitoUploadForm(forms.Form):
    csv_file = forms.FileField(label="Registration csv file", required=True)
    update_name = forms.BooleanField(initial=False, required=False)
    make_transaction = forms.BooleanField(initial=True, required=False)
    course = forms.ModelChoiceField(
        queryset=Course.objects.select_related('course_type'),
        widget=autocomplete.ModelSelect2(url="course-autocomplete"),
        label="Course",
        required=True,
        help_text="Select the course for which you are uploading registrations.",
    )


@admin.register(Registration)
class RegistrationAdmin(DetailedLogAdminMixin, CoursePermissionMixin, DALFModelAdmin):
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
        "_created_at",
        "_updated_at",
        "paid_amount",
    ]
    autocomplete_fields = ["user", "course", "supporting_user"]
    fieldsets = (
        (
            "Registration Information",
            {"fields": ("user", "course", "status", "registration_date", "supporting_user")},
        ),
        (
            "Payment Information",
            {
                "fields": (
                    "payment_status",
                    ("initial_price", "discount", "tuition", "paid_amount"),
                    "next_payment_date",
                    "payment_description",
                )
            },
        ),
        ("Additional Information", {"fields": ("description",)}),
        (
            "Timestamps",
            {"fields": ("_created_at", "_updated_at")},
        ),
    )
    
    change_list_template = "admin/courses/registration/change_list.html"
    inlines = [CourseTransactionInline]

    def paid_amount(self, obj):
        amount = obj.paid_amount()
        return f"{amount:,}" if amount else "0"

    def changelist_view(self, request, extra_context=None):
        if extra_context is None:
            extra_context = {}
        upload_url = reverse("admin:registration-upload-excel")
        extra_context["upload_excel_button"] = format_html(
            '<a class="button" href="{}" style="display:inline-block;">Upload Excel</a>', upload_url
        )
        sazito_url = reverse("admin:registration-upload-sazito")
        extra_context["upload_sazito_button"] = format_html(
            '<a class="button" href="{}" style="display:inline-block;">Upload Sazito</a>', sazito_url
        )
        return super().changelist_view(request, extra_context=extra_context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("upload-excel/", self.admin_site.admin_view(self.upload_excel), name="registration-upload-excel"),
            path("upload-sazito/", self.admin_site.admin_view(self.upload_sazito_file), name="registration-upload-sazito"),
            path(
                "<int:course_id>/export_registrations/",
                self.admin_site.admin_view(self.export_registrations),
                name="courses_course_export_registrations",
            ),
        ]
        return custom_urls + urls

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        try:
            registration = self.model.objects.get(pk=object_id)
            url_user = reverse("admin:users_user_change", args=[registration.user.id])
            url_crm = reverse("admin:users_crmuser_change", args=[registration.user._crm_user.id])
            extra_context["user_button"] = format_html('<a class="button" href="{}" style="display:inline-block;">Go to User</a>', url_user)
            extra_context["crm_user_button"] = format_html('<a class="button" href="{}" style="display:inline-block;">Go to CRM User</a>', url_crm)
        except Exception:
            extra_context["crm_user_button"] = None
            extra_context["user_button"] = None
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        user = request.user
        if user.is_superuser:
            return fieldsets
        if obj and obj.course.managing_users.filter(pk=user.pk).exists():
            return fieldsets
        filtered_fieldsets = []
        for name, options in fieldsets:
            if name == "Payment Information":
                continue
            filtered_fieldsets.append((name, options))
        return filtered_fieldsets

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if obj is None:
            return readonly_fields
        return [*readonly_fields, "user", "course", "registration_date"]

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
        if obj.course.managing_users.filter(pk=user.pk).exists() or obj.supporting_user == user or obj.user == user:
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

    @staticmethod
    def add_and_register_users(users_data, course, update_user=False, make_transaction=False):
        from tqdm import tqdm

        from commons.utils import get_status_from_text, normalize_national_id
        from courses.models import Registration
        from financials.models import INCOME_CATEGORY_REGISTRATION, CourseTransaction
        from users.models import User

        def make_none_empty_str(text):
            if text == "":
                return None
            return text

        users_dic = {user[1]: user for user in User.objects.all().values_list("id", "username", "first_name", "last_name", "phone_number")}
        users_dup_check = {f"{u[2]}{u[3]}".replace(" ", ""): u for u in users_dic.values() if u[3] not in [None, ""]}

        registration_dic = {r[0]: r[1] for r in Registration.objects.filter(course=course).values_list("user_id", "id")}
        course_transaction_dic = dict.fromkeys(
            CourseTransaction.objects.filter(course=course).values_list("registration_id", flat=True), True
        )
        bad_name = 0
        made_users = 0
        made_registration = 0
        logs = []

        for data in tqdm(users_data):
            phone = data["phone"]
            username = data["username"]
            first_name = data.get("first_name", "")
            last_name = data.get("last_name", "")
            telegram_id = data.get("telegram_id", "")
            email = data.get("email", "")
            education = User.get_education_from_text(data.get("education", None))
            profession = data.get("profession", "")
            age = data.get("age", None)
            gender = User.get_gender_from_text(data.get("gender", ""))
            national_id = normalize_national_id(data.get("national_id", "")) or ""
            english_first_name = data.get("english_first_name", "")
            english_last_name = data.get("english_last_name", "")
            referer_name = data.get("referer_name", "")
            tuition = data.get("tuition", 0) or 0
            status, payment_status = get_status_from_text(data.get("status", None))
            registration_date = data.get("registration_date", None)
            discount = data.get("discount", 0) or 0
            initial_price = data.get("initial_price", 0) or 0
            paid_amount = data.get("paid_amount", 0) or 0

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
                    if update_user:
                        User.objects.filter(username=username).update(first_name=first_name, last_name=last_name)

            elif users_dup_check.get(f"{first_name}{last_name}".replace(" ", ""), None) is not None:
                user = users_dup_check[f"{first_name}{last_name}".replace(" ", "")]
                u = User.objects.get(id=user[0])
                if user[4] is None:
                    u.phone_number = phone
                    u.username = username
                    users_dic[username] = [u.id, username, first_name, last_name, phone]
                    user = users_dic[username]
                u.telegram_id = make_none_empty_str(u.telegram_id) or telegram_id
                u.email = make_none_empty_str(u.email) or email
                u.profession = make_none_empty_str(u.profession) or profession
                u.education = make_none_empty_str(u.education) or education
                u.age = make_none_empty_str(u.age) or age
                u.gender = u.gender if u.gender is not None else gender
                u.national_id = make_none_empty_str(u.national_id) or national_id
                u.english_first_name = make_none_empty_str(u.english_first_name) or english_first_name
                u.english_last_name = make_none_empty_str(u.english_last_name) or english_last_name
                u.referer_name = make_none_empty_str(u.referer_name) or referer_name
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

            if registration_dic.get(user[0], None) is None:
                try:
                    reg = Registration.objects.create(
                        user_id=user[0],
                        course=course,
                        status=status,
                        payment_status=payment_status,
                        tuition=tuition,
                        initial_price=initial_price,
                        discount=discount,
                        registration_date=registration_date,
                    )
                    registration_dic[user[0]] = reg.id
                    made_registration += 1
                except Exception as e:
                    logs.append(["Error", str(phone), str(user[2]), str(user[3]), first_name, str(e)])
            if make_transaction and course_transaction_dic.get(registration_dic[user[0]], None) is None and paid_amount > 0:
                course_transaction = CourseTransaction.objects.create(
                    registration_id=registration_dic[user[0]],
                    user_account_id=user[0],
                    course=course,
                    amount=paid_amount,
                    transaction_type=1,
                    transaction_category=INCOME_CATEGORY_REGISTRATION,
                    financial_account=data["financial_account"],
                    date=registration_date,
                    entry_user=data["entry_user"],
                    tracking_code=data.get("tracking_code", ""),
                )
                course_transaction.transaction = course_transaction.create_transaction()
                course_transaction.save()
                course_transaction_dic[registration_dic[user[0]]] = True
        return logs, made_users, made_registration, bad_name

    def upload_excel(self, request):
        if request.method == "POST":
            form = RegistrationExcelUploadForm(request.POST, request.FILES)
            if form.is_valid():
                excel_file = request.FILES["excel_file"]
                sheet_name = form.cleaned_data.get("sheet_name")
                try:
                    df = pd.read_excel(excel_file, sheet_name=sheet_name, dtype={"fix phone": str, "سن": str})
                except Exception as e:
                    self.message_user(request, f"Error reading Excel file: {e}", level="error")
                    return redirect(request.path)
                if not request.POST.get("confirm_preview"):
                    preview_data = df.loc[:, ["fix phone", "نام", "نام خانوادگی", "مبلغ نهایی"]]
                    df = df.dropna(how="all", subset=["نام", "نام خانوادگی", "fix phone"])
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

                    from commons.utils import normalize_phone

                    df = df.where(pd.notnull(df), None)
                    df = df.dropna(how="all", subset=["نام", "نام خانوادگی", "fix phone"])
                    good_phone = []
                    bad_phone = []
                    for phone in df["fix phone"]:
                        if len(str(phone).strip()) == 11 and str(phone).startswith("09"):
                            good_phone.append("+989" + phone[2:])
                        else:
                            bad_phone.append(phone)
                    good_phone = list(set(good_phone))
                    bad_phone = list(set(bad_phone))

                    no_phone = 0
                    logs = []
                    users_data = []
                    for index, row in tqdm(df.iterrows(), total=df.shape[0]):
                        phone = normalize_phone(row["fix phone"])
                        first_name = row.get("نام", "")
                        if first_name:
                            first_name = first_name.strip()
                        last_name = row.get("نام خانوادگی", "")
                        if last_name:
                            last_name = last_name.strip()
                        telegram_id = row.get("تلگرام", None) or row.get("آی‌دی تلگرام", None)

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

                        users_data.append(
                            {
                                "username": username,
                                "phone": phone,
                                "first_name": first_name,
                                "last_name": last_name,
                                "telegram_id": telegram_id,
                                "email": row.get("ایمیل", ""),
                                "education": row.get("تحصیلات", ""),
                                "profession": row.get("حرفه", ""),
                                "national_id": row.get("کد ملی", ""),
                                "age": row.get("سن", None),
                                "gender": row.get("جنسیت", None),
                                "english_first_name": row.get("Name", ""),
                                "english_last_name": row.get("Surname", ""),
                                "referer_name": row.get("معرف", None),
                                "status": row.get("وضعیت", None),
                                "tuition": float(row.get("مبلغ نهایی", 0) or 0) * currency_to_toman_multiplier,
                            }
                        )
                    new_logs, made_users, made_registration, bad_name = self.add_and_register_users(
                        users_data, selected_course, update_name
                    )
                    logs = logs + new_logs
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

    @requires_course_managing_permission
    def export_registrations(self, request, course_id):
        try:
            course = Course.objects.get(id=course_id)
            registrations = (
                Registration.objects.filter(course=course).select_related("user", "supporting_user").order_by("-registration_date")
            )
            data = []
            for reg in registrations:
                data.append(
                    {
                        "first name": reg.user.first_name,
                        "last name": reg.user.last_name,
                        "phone": getattr(reg.user, "phone_number", ""),
                        "email": reg.user.email,
                        "status": reg.status_display,
                        "registration date": reg.registration_date.strftime("%Y/%m/%d %H:%M") if reg.registration_date else "",
                        "قیمت اولیه": reg.initial_price,
                        "تخفیف": reg.discount,
                        "tax": reg.vat,
                        "شهریه": reg.tuition,
                        "وضعیت پرداخت": dict(PAYMENT_STATUS_CHOICES).get(reg.payment_status, ""),
                        "نوع پرداخت": dict(PAYMENT_TYPE_CHOICES).get(reg.payment_type, ""),
                        "تاریخ پرداخت بعدی": reg.next_payment_date.strftime("%Y/%m/%d") if reg.next_payment_date else "",
                        "پشتیبان": f"{reg.supporting_user.first_name} {reg.supporting_user.last_name}" if reg.supporting_user else "",
                        "توضیحات": reg.description or "",
                        "توضیحات پرداخت": reg.payment_description or "",
                    }
                )
            df = pd.DataFrame(data)
            response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            response["Content-Disposition"] = f'attachment; filename="{course.course_name}_registrations.xlsx"'

            from io import BytesIO

            excel_buffer = BytesIO()

            with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="registration")

            excel_buffer.seek(0)
            response.write(excel_buffer.getvalue())

            messages.success(request, f"فایل اکسل ثبت نام های دوره {course.course_name} با موفقیت ایجاد شد.")
            return response

        except Course.DoesNotExist:
            messages.error(request, "دوره مورد نظر یافت نشد.")
            return redirect("admin:courses_course_changelist")
        except Exception as e:
            messages.error(request, f"خطا در ایجاد فایل اکسل: {e!s}")
            return redirect("admin:courses_course_change", course_id)

    def upload_sazito_file(self, request):
        if request.method == "POST":
            form = RegistrationSazitoUploadForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = request.FILES["csv_file"]
                try:
                    df = pd.read_csv(csv_file, dtype={"first name": str, "last name": str, "Payment Reference Code": str})
                except Exception as e:
                    self.message_user(request, f"Error reading csv file: {e}", level="error")
                    return redirect(request.path)
                if not request.POST.get("confirm_preview"):
                    preview_data = df.loc[:, ["first name", "last name", "Mobile Number"]]
                    df = df.dropna(how="all", subset=["first name", "last name", "Mobile Number"])
                    preview_html = preview_data.to_html(index=False, classes="table table-bordered table-sm")
                    return render(
                        request,
                        "admin/courses/registration/upload_sazito_file.html",
                        {
                            "form": form,
                            "preview_html": preview_html,
                            "show_confirm": True,
                        },
                    )
                selected_course = form.cleaned_data["course"]
                update_name = form.cleaned_data.get("update_name")
                make_transaction = form.cleaned_data.get("make_transaction", True)
                try:
                    import hashlib
                    from datetime import datetime

                    from commons.utils import normalize_phone

                    bad_name = 0
                    logs = []
                    data = []
                    no_phone = 0
                    df = df.where(pd.notnull(df), None)
                    df = df.dropna(how="all", subset=["first name", "last name", "Mobile Number"])
                    for index, row in df.iterrows():
                        phone = normalize_phone(row["Mobile Number"])
                        first_name = (row["first name"] or "").strip()
                        last_name = (row["last name"] or "").strip()
                        if phone is None or str(phone).strip() == "":
                            continue
                        details = {}
                        if row["Product Details"] is not None:
                            details = {
                                item.split(":", 1)[0].strip(): item.split(":", 1)[1].strip()
                                for item in row["Product Details"].split(",")
                                if ":" in item
                            }

                        if phone == "":
                            phone = None
                        if phone is None and first_name is None and last_name is None:
                            continue
                        last_name = last_name or ""
                        if phone is None:
                            name_hash = hashlib.sha256(f"{first_name}{last_name}".encode()).hexdigest()[:10]
                            username = f"from_upload_{name_hash}"
                            no_phone += 1
                            logs.append(["No Phone", str(first_name), str(last_name), str(phone)])
                        else:
                            username = phone

                        data.append(
                            {
                                "index": index,
                                "phone": phone,
                                "username": username,
                                "first_name": first_name,
                                "last_name": last_name,
                                "email": row["Email"],
                                "paid_amount": row["Final Total"],
                                "tuition": int(row["Net Total"]) - int(row["Discount Amount"]),
                                "initial_price": row["Net Total"],
                                "discount": row["Discount Amount"],
                                "education": details.get("تحصیلات", ""),
                                "profession": details.get("حرفه تخصصی", ""),
                                "telegram_id": details.get("آی\u200cدی تلگرام جهت عضو شدن در گروه دوره", ""),
                                "age": details.get("سن", None),
                                "referer_name": details.get("معرف", ""),
                                "registration_date": datetime.strptime(str(row["Created at (gregorian)"]), "%m/%d/%Y %H:%M"),
                                "tracking_code": row["Payment Reference Code"],
                                "financial_account": FinancialAccount.objects.get(name="پی‌پینگ"),
                                "entry_user": request.user,
                                "status": "حاضر در دوره - عدم سررسید"
                            }
                        )

                    new_logs, made_users, made_registration, bad_name = self.add_and_register_users(
                        data, selected_course, update_name, make_transaction
                    )
                    logs = logs + new_logs
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
            form = RegistrationSazitoUploadForm()
        context = {
            "form": form,
            **self.admin_site.each_context(request),
        }
        return render(request, "admin/courses/registration/upload_sazito_file.html", context)


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
    search_fields = ["user__first_name", "user__last_name", "session__session_name", "user__phone_number"]
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
