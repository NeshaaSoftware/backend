from typing import ClassVar

from django.contrib import admin

from .models import Cost


@admin.register(Cost)
class CostAdmin(admin.ModelAdmin):
    list_display: ClassVar[list[str]] = [
        "title",
        "cost_type",
        "course",
        "amount",
        "quantity",
        "total_amount",
        "is_paid",
        "date",
    ]
    list_filter: ClassVar[list[str]] = ["cost_type", "is_paid", "course", "date"]
    search_fields: ClassVar[list[str]] = ["title", "description", "person", "invoice_number"]
    readonly_fields: ClassVar[list[str]] = ["total_amount", "created_at", "updated_at"]
    date_hierarchy = "date"

    fieldsets = (
        (
            "Cost Information",
            {"fields": ("title", "cost_type", "description", "date", "course")},
        ),
        (
            "Financial Details",
            {"fields": ("amount", "quantity", "total_amount", "is_paid")},
        ),
        ("Additional Information", {"fields": ("person", "invoice_number")}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("course")

    def save_model(self, request, obj, form, change):
        # Auto-calculate total_amount
        obj.total_amount = obj.amount * obj.quantity
        super().save_model(request, obj, form, change)
