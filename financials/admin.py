from dalf.admin import DALFModelAdmin, DALFRelatedFieldAjax
from django import forms
from django.contrib import admin
from django.utils.html import format_html

from commons.admin import DetailedLogAdminMixin

from .models import Commodity, Customer, FinancialAccount, Invoice, InvoiceItem, Transaction, CourseTransaction


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
    list_display = (
        "id",
        "type",
        "date",
        "customer",
        "formatted_total_amount",
        "is_paid",
        "course",
        "formatted_items_amount",
        "formatted_discount",
        "formatted_vat",
        "orgnization",
        "_created_at",
        "_updated_at",
    )
    search_fields = ("customer__name", "description")
    list_filter = ("type", "is_paid", ("course", DALFRelatedFieldAjax), ("customer", DALFRelatedFieldAjax), "date")
    readonly_fields = ("_created_at", "_updated_at")
    autocomplete_fields = (
        "course",
        "customer",
    )
    inlines = [InvoiceItemInline]

    @admin.display(description="Total Amount", ordering="total_amount")
    def formatted_total_amount(self, obj):
        return f"{obj.total_amount:,}"

    @admin.display(description="Items Amount", ordering="items_amount")
    def formatted_items_amount(self, obj):
        return f"{obj.items_amount:,}"

    @admin.display(description="Discount", ordering="discount")
    def formatted_discount(self, obj):
        return f"{obj.discount:,}"

    @admin.display(description="VAT", ordering="vat")
    def formatted_vat(self, obj):
        return f"{obj.vat:,}"


@admin.register(InvoiceItem)
class InvoiceItemAdmin(DetailedLogAdminMixin, DALFModelAdmin):
    list_display = (
        "invoice",
        "commodity",
        "description",
        "formatted_unit_price",
        "formatted_quantity",
        "formatted_discount",
        "formatted_vat",
        "formatted_total_price",
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

    @admin.display(description="Unit Price", ordering="unit_price")
    def formatted_unit_price(self, obj):
        return f"{obj.unit_price:,}"

    @admin.display(description="Quantity", ordering="quantity")
    def formatted_quantity(self, obj):
        return f"{obj.quantity:,}"

    @admin.display(description="Discount", ordering="discount")
    def formatted_discount(self, obj):
        return f"{obj.discount:,}"

    @admin.display(description="VAT", ordering="vat")
    def formatted_vat(self, obj):
        return f"{obj.vat:,}"

    @admin.display(description="Total Price", ordering="total_price")
    def formatted_total_price(self, obj):
        return f"{obj.total_price:,}"


@admin.register(Transaction)
class TransactionAdmin(DetailedLogAdminMixin, DALFModelAdmin):
    list_display = (
        "id",
        "invoice",
        "transaction_type",
        "date",
        "formatted_amount",
        "formatted_fee",
        "formatted_net_amount",
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
        "course__course_name",
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

    @admin.display(description="Amount", ordering="amount")
    def formatted_amount(self, obj):
        return f"{obj.amount:,}"

    @admin.display(description="Fee", ordering="fee")
    def formatted_fee(self, obj):
        return f"{obj.fee:,}"

    @admin.display(description="Net Amount", ordering="net_amount")
    def formatted_net_amount(self, obj):
        return f"{obj.net_amount:,}"


class CourseTransactionInlineForm(forms.ModelForm):
    class Meta:
        model = CourseTransaction
        fields = '__all__'
        help_texts = {
            'amount': 'مبلغ به تومان',
            'fee': 'کارمزد به تومان',
            'net_amount': 'خالص مبلغ به تومان',
        }

    def __init__(self, *args, parent_registration=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent_registration = parent_registration

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.parent_registration is not None:
            instance.registration = self.parent_registration
            if hasattr(self.parent_registration, 'course'):
                instance.course = self.parent_registration.course
        if commit:
            instance.save()
        return instance


class CourseTransactionInline(admin.TabularInline):
    model = CourseTransaction
    form = CourseTransactionInlineForm
    extra = 0
    readonly_fields = ("net_amount",)
    autocomplete_fields = ("entry_user", "user_account")
    show_change_link = True
    verbose_name = "تراکنش مالی ثبت‌نام"
    verbose_name_plural = "تراکنش‌های مالی ثبت‌نام"

    def get_formset(self, request, obj=None, **kwargs):
        FormSet = super().get_formset(request, obj, **kwargs)
        parent_registration = obj
        class WrappedFormSet(FormSet):
            def _construct_form(inner_self, i, **form_kwargs):
                form_kwargs['parent_registration'] = parent_registration
                return super(WrappedFormSet, inner_self)._construct_form(i, **form_kwargs)
        return WrappedFormSet
