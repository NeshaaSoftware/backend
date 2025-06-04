from typing import ClassVar

from django.contrib import admin

from .models import Course, CourseSession


class CourseSessionInline(admin.TabularInline):
    model = CourseSession
    extra = 1
    fields: ClassVar[list[str]] = [
        "session_name",
        "start_date",
        "end_date",
        "location",
        "max_participants",
    ]


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display: ClassVar[list[str]] = [
        "name",  # display property
        "course_type",
        "number",
        "_created_at",
    ]
    list_filter: ClassVar[list[str]] = ["course_type", "_created_at"]
    search_fields: ClassVar[list[str]] = ["course_type", "number"]
    readonly_fields: ClassVar[list[str]] = ["_created_at", "_updated_at", "name"]
    
    filter_horizontal: ClassVar[list[str]] = ["admin_users"]
    inlines: ClassVar[list[type[admin.TabularInline]]] = [CourseSessionInline]

    fieldsets = (
        (
            "Course Information",
            {"fields": ("course_type", "number", "name")},  # add 'name' as a readonly field
        ),
        ("Administration", {"fields": ("admin_users",)}),
        (
            "Timestamps",
            {"fields": ("_created_at", "_updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(CourseSession)
class CourseSessionAdmin(admin.ModelAdmin):
    list_display: ClassVar[list[str]] = [
        "session_name",
        "course",
        "start_date",
        "end_date",
        "location",
        "max_participants",
    ]
    list_filter: ClassVar[list[str]] = ["course", "start_date"]
    search_fields: ClassVar[list[str]] = ["session_name", "course__name", "location"]
    readonly_fields: ClassVar[list[str]] = ["_created_at", "_updated_at"]
