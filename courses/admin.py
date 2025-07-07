from dalf.admin import DALFModelAdmin, DALFRelatedFieldAjax
from dal import autocomplete
from django import forms
from django.contrib import admin, messages
from django.db.models import Q
from django.shortcuts import redirect, render
from django.urls import path, reverse
from django.utils.html import format_html
from django_jalali.admin.filters import JDateFieldListFilter

from commons.admin import DetailedLogAdminMixin, DropdownFilter

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

    def changelist_view(self, request, extra_context=None):
        if extra_context is None:
            extra_context = {}
        upload_url = reverse("admin:registration-upload-excel")
        extra_context["upload_excel_button"] = format_html(
            '<a class="button" href="{}" style="margin:10px 0;display:inline-block;">Upload Excel</a>', upload_url
        )
        return super().changelist_view(request, extra_context=extra_context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("upload-excel/", self.admin_site.admin_view(self.upload_excel), name="registration-upload-excel"),
        ]
        return custom_urls + urls

    def upload_excel(self, request):
        if request.method == "POST":
            form = RegistrationExcelUploadForm(request.POST, request.FILES)
            if form.is_valid():
                # excel_file = form.cleaned_data["excel_file"]
                # selected_course = form.cleaned_data["course"]
                try:

                    # df = pd.read_excel(excel_file)
                    # You can now use selected_course in your import logic
                    created, skipped = 0, 0
                    self.message_user(
                        request, f"Registrations imported: {created}, skipped: {skipped}", messages.SUCCESS
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
        return render(request, "admin/upload_registration_excel.html", context)

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
