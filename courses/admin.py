from django.contrib import admin
from django.db.models import Case, CharField, Q, Value, When
from django_jalali.admin.filters import JDateFieldListFilter

from commons.admin import DetailedLogAdminMixin

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


class CourseTextInputFilter(admin.SimpleListFilter):
    title = "Course (search)"
    parameter_name = "course_search"
    template = "admin/input_filter.html"  # This template should render a text input

    def lookups(self, request, model_admin):
        return []

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            course_type_choices = dict(CourseType.objects.values_list("id", "name"))
            whens = [When(course__course_type=k, then=Value(v)) for k, v in course_type_choices.items()]
            queryset = queryset.annotate(course_type_display=Case(*whens, output_field=CharField()))
            return queryset.filter(
                Q(course__number__icontains=value)
                | Q(course__name__icontains=value)
                | Q(course_type_display__icontains=value)
            )
        return queryset

    def expected_parameters(self):
        return [self.parameter_name]


@admin.register(Course)
class CourseAdmin(DetailedLogAdminMixin, admin.ModelAdmin):
    list_display = [
        "name",
        "course_type",
        "number",
        "_created_at",
    ]
    list_filter = ["course_type", "_created_at"]
    search_fields = ["course_type", "number"]
    readonly_fields = ["_created_at", "_updated_at", "name"]
    filter_horizontal = ["managing_users", "supporting_users", "instructors"]
    inlines = [CourseSessionInline]
    autocomplete_fields = ["managing_users", "supporting_users", "instructors"]
    fieldsets = (
        (
            "Course Information",
            {"fields": ("course_type", "number", "name", "price", "start_date", "end_date")},
        ),
        ("Administration", {"fields": ("managing_users", "supporting_users", "instructors")}),
        (
            "Timestamps",
            {"fields": ("_created_at", "_updated_at"), "classes": ("collapse",)},
        ),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related("managing_users", "supporting_users", "instructors")


@admin.register(CourseSession)
class CourseSessionAdmin(DetailedLogAdminMixin, admin.ModelAdmin):
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
        CourseTextInputFilter,
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
        # Select related course for performance
        qs = super().get_queryset(request)
        return qs.select_related("course")


@admin.register(Registration)
class RegistrationAdmin(DetailedLogAdminMixin, admin.ModelAdmin):
    list_display = [
        "user",
        "course",
        "status",
        "support_user",
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
        CourseTextInputFilter,
    ]
    search_fields = [
        "user__full_name",
        "course__number",
        "course__course_type",
        "user__phone_number",
    ]
    readonly_fields = [
        "user",
        "course",
        "registration_date",
        "_created_at",
        "_updated_at",
    ]
    autocomplete_fields = ["support_user"]
    fieldsets = (
        (
            "Registration Information",
            {"fields": ("user", "course", "status", "registration_date", "support_user")},
        ),
        (
            "Payment Information",
            {"fields": ("payment_status", "tuition", "next_payment_date", "payment_description")},
        ),
        ("Additional Information", {"fields": ("description",)}),
        (
            "Timestamps",
            {"fields": ("_created_at", "_updated_at"), "classes": ("collapse",)},
        ),
    )

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        user = request.user
        if user.is_superuser:
            return fieldsets
        if obj and user.managed_courses.filter(id=obj.course.id).exists():
            return fieldsets
        filtered_fieldsets = []
        for name, options in fieldsets:
            if name == "Payment Information":
                continue
            filtered_fieldsets.append((name, options))
        return [tuple(filtered_fieldsets)]

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
        qs = super().get_queryset(request).select_related("user", "course", "support_user")
        user = request.user
        if user.is_superuser:
            return qs
        managed_courses = user.managed_courses.all()
        if managed_courses.exists():
            return qs.filter(Q(course__in=managed_courses) | Q(support_user=user))
        return qs.filter(user=user)

    def has_view_permission(self, request, obj=None):
        user = request.user
        if user.is_superuser:
            return True
        if obj is None:
            return True
        if obj.course in user.managed_courses.all() or obj.support_user == user or obj.user == user:
            return True
        return False

    def has_change_permission(self, request, obj=None):
        user = request.user
        if user.is_superuser:
            return True
        if obj is None:
            return True
        if obj.course in user.managed_courses.all() or obj.support_user == user or obj.user == user:
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        user = request.user
        if user.is_superuser:
            return True
        if obj is None:
            return True
        return obj.course in user.managed_courses.all()


@admin.register(Attendance)
class AttendenceAdmin(DetailedLogAdminMixin, admin.ModelAdmin):
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
