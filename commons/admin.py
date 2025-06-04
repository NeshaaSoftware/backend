from typing import ClassVar
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.utils.html import format_html

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display: ClassVar[list[str]] = [
        "action",
        "content_type",
        "object_id",
        "user",
        "timestamp",
        "get_changed_fields_display",
    ]
    list_filter: ClassVar[list[str]] = [
        "action",
        "content_type",
        "timestamp",
        "user",
    ]
    search_fields: ClassVar[list[str]] = [
        "user__username",
        "user__email",
        "object_id",
        "ip_address",
    ]
    readonly_fields: ClassVar[list[str]] = [
        "content_type",
        "object_id",
        "content_object",
        "action",
        "timestamp",
        "user",
        "ip_address",
        "user_agent",
        "old_values",
        "new_values",
        "changed_fields",
        "get_formatted_old_values",
        "get_formatted_new_values",
    ]

    date_hierarchy = "timestamp"
    ordering = ["-timestamp"]

    fieldsets = (
        (
            "Object Information",
            {
                "fields": (
                    "content_type",
                    "object_id",
                    "content_object",
                )
            },
        ),
        (
            "Action Details",
            {
                "fields": (
                    "action",
                    "timestamp",
                    "user",
                )
            },
        ),
        (
            "Request Information",
            {
                "fields": (
                    "ip_address",
                    "user_agent",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Change Details",
            {
                "fields": (
                    "changed_fields",
                    "get_formatted_old_values",
                    "get_formatted_new_values",
                ),
            },
        ),
        (
            "Raw Data",
            {
                "fields": (
                    "old_values",
                    "new_values",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Additional Information",
            {
                "fields": ("notes",),
                "classes": ("collapse",),
            },
        ),
    )

    def has_add_permission(self, request):
        """Disable adding audit logs manually"""
        return False

    def has_change_permission(self, request, obj=None):
        """Make audit logs read-only"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Disable deleting audit logs"""
        return False

    def get_changed_fields_display(self, obj):
        """Display changed fields in a readable format"""
        if obj.changed_fields:
            return ", ".join(obj.changed_fields)
        return "-"

    get_changed_fields_display.short_description = "Changed Fields"

    def get_formatted_old_values(self, obj):
        """Format old values for display"""
        if obj.old_values:
            html = "<table style='width:100%;'>"
            for field, value in obj.old_values.items():
                html += f"<tr><td><strong>{field}:</strong></td><td>{value}</td></tr>"
            html += "</table>"
            return format_html(html)
        return "-"

    get_formatted_old_values.short_description = "Old Values"

    def get_formatted_new_values(self, obj):
        """Format new values for display"""
        if obj.new_values:
            html = "<table style='width:100%;'>"
            for field, value in obj.new_values.items():
                html += f"<tr><td><strong>{field}:</strong></td><td>{value}</td></tr>"
            html += "</table>"
            return format_html(html)
        return "-"

    get_formatted_new_values.short_description = "New Values"
