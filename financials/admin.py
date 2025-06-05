from typing import ClassVar

from django import forms
from django.contrib import admin
from django_jalali.admin.filters import JDateFieldListFilter
from django_jalali.admin.widgets import AdminjDateWidget

from commons.admin import DetailedLogAdminMixin

from .models import Cost, FinancialAccount, Income


class CostAdminForm(forms.ModelForm):
    class Meta:
        model = Cost
        fields = [
            "course",
            "date",
            "invoice_number",
            "title",
            "description",
            "person",
            "amount",
            "quantity",
            "total_amount",
            "is_paid",
            "cost_type",
        ]
        widgets = {
            "date": AdminjDateWidget,
        }


@admin.register(Cost)
class CostAdmin(DetailedLogAdminMixin, admin.ModelAdmin):
    form = CostAdminForm
    list_display: ClassVar[list[str]] = [
        "title",
        "cost_type",
        "course",
        "amount",
        "quantity",
        "total_amount",
        "is_paid",
    ]
    list_filter: ClassVar[list[str]] = [
        "cost_type",
        "is_paid",
        "course",
        ("date", JDateFieldListFilter),
    ]
    search_fields: ClassVar[list[str]] = [
        "title",
        "description",
        "person",
        "invoice_number",
    ]
    readonly_fields: ClassVar[list[str]] = [
        "total_amount",
        "_created_at",
        "_updated_at",
    ]

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
            {"fields": ("_created_at", "_updated_at"), "classes": ("collapse",)},
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("course")

    def save_model(self, request, obj, form, change):
        # Auto-calculate total_amount
        obj.total_amount = obj.amount * obj.quantity
        super().save_model(request, obj, form, change)


class IncomeAdminForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = [
            "course",
            "date",
            "description",
            "name",
            "user",
            "amount",
        ]
        widgets = {
            "date": AdminjDateWidget,
        }


@admin.register(Income)
class IncomeAdmin(DetailedLogAdminMixin, admin.ModelAdmin):
    form = IncomeAdminForm
    list_display: ClassVar[list[str]] = [
        "name",
        "course",
        "user",
        "amount",
        "date",
    ]
    list_filter: ClassVar[list[str]] = ["course", "date"]
    search_fields: ClassVar[list[str]] = ["name", "description", "user__username", "course__number"]
    readonly_fields: ClassVar[list[str]] = ["_created_at", "_updated_at"]

    fieldsets = (
        (
            "Income Information",
            {"fields": ("name", "course", "user", "description", "date")},
        ),
        (
            "Financial Details",
            {"fields": ("amount",)},
        ),
        ("Timestamps", {"fields": ("_created_at", "_updated_at"), "classes": ("collapse",)}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("course", "user")

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)


@admin.register(FinancialAccount)
class FinancialAccountAdmin(DetailedLogAdminMixin, admin.ModelAdmin):
    list_display = ("name", "_created_at", "_updated_at")
    search_fields = ("name", "course__number")
    list_filter = ("course",)
    readonly_fields = ("_created_at", "_updated_at")
    filter_horizontal = ("course",)
