from dalf.admin import DALFModelAdmin, DALFRelatedFieldAjax
from django.contrib import admin

from commons.admin import DetailedLogAdminMixin

from .models import Commodity, Customer, FinancialAccount, Invoice, InvoiceItem, Transaction


@admin.register(FinancialAccount)
class FinancialAccountAdmin(DetailedLogAdminMixin, DALFModelAdmin):
    list_display = ("name", "description", "_created_at", "_updated_at")
    search_fields = ("name", "description")
    readonly_fields = ("_created_at", "_updated_at")
    filter_horizontal = ("course",)


@admin.register(Commodity)
class CommodityAdmin(DetailedLogAdminMixin, DALFModelAdmin):
    list_display = ("name", "description", "_created_at", "_updated_at")
    search_fields = ("name", "description")
    readonly_fields = ("_created_at", "_updated_at")


@admin.register(Customer)
class CustomerAdmin(DetailedLogAdminMixin, DALFModelAdmin):
    list_display = ("name", "tax_id", "national_id", "contact", "address", "customer_type")
    search_fields = ("name", "tax_id", "national_id", "contact", "address")
    readonly_fields = ("_created_at", "_updated_at")


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0
    autocomplete_fields = ("commodity",)
    readonly_fields = ("_created_at", "_updated_at")
    show_change_link = True


@admin.register(Invoice)
class InvoiceAdmin(DetailedLogAdminMixin, DALFModelAdmin):
    list_display = ("id", "type", "date", "customer", "total_amount", "is_paid", "course", "items_amount", "discount", "vat", "orgnization", "_created_at", "_updated_at")
    search_fields = ("customer__name", "description")
    list_filter = ("type", "is_paid", ("course", DALFRelatedFieldAjax), ("customer", DALFRelatedFieldAjax), "date")
    readonly_fields = ("_created_at", "_updated_at")
    autocomplete_fields = (
        "course",
        "customer",
    )
    inlines = [InvoiceItemInline]


@admin.register(InvoiceItem)
class InvoiceItemAdmin(DetailedLogAdminMixin, DALFModelAdmin):
    list_display = (
        "invoice",
        "commodity",
        "description",
        "unit_price",
        "quantity",
        "discount",
        "vat",
        "total_price",
        "_created_at",
        "_updated_at",
    )
    search_fields = ("description", "commodity__name", "invoice__id")
    readonly_fields = ("_created_at", "_updated_at")
    autocomplete_fields = (
        "invoice",
        "commodity",
    )
    list_filter = (("invoice", DALFRelatedFieldAjax), ("commodity", DALFRelatedFieldAjax))


@admin.register(Transaction)
class TransactionAdmin(DetailedLogAdminMixin, DALFModelAdmin):
    list_display = (
        "id",
        "invoice",
        "transaction_type",
        "date",
        "amount",
        "fee",
        "net_amount",
        "name",
        "user_account",
        "tracking_code",
        "account",
        "course",
        "entry_user",
        "description",
        "_created_at",
        "_updated_at",
    )
    search_fields = (
        "invoice__id",
        "tracking_code",
        "account__name",
        "course__name",
        "user_account__username",
        "entry_user__username",
    )
    list_filter = (
        "transaction_type",
        ("account", DALFRelatedFieldAjax),
        ("course", DALFRelatedFieldAjax),
        ("invoice", DALFRelatedFieldAjax),
        ("user_account", DALFRelatedFieldAjax),
        ("entry_user", DALFRelatedFieldAjax),
        "date",
    )
    readonly_fields = ("_created_at", "_updated_at")
    autocomplete_fields = (
        "invoice",
        "account",
        "course",
        "user_account",
        "entry_user",
    )
