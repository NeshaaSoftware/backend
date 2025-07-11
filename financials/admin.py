from dalf.admin import DALFModelAdmin, DALFRelatedFieldAjax
from django import forms
from django.contrib import admin

from commons.admin import DetailedLogAdminMixin

from .models import Commodity, CourseTransaction, Customer, FinancialAccount, Invoice, InvoiceItem, Transaction


@admin.register(FinancialAccount)
class FinancialAccountAdmin(DetailedLogAdminMixin, DALFModelAdmin):
    list_display = ("name", "description", "_created_at", "_updated_at")
    search_fields = ("name", "description")
    readonly_fields = ("_created_at", "_updated_at")
    filter_horizontal = ("course",)
    fieldsets = (
        ("اطلاعات حساب", {"fields": ("name", "description", "course")}),
        ("زمان‌بندی", {"fields": ("_created_at", "_updated_at"), "classes": ("collapse",)}),
    )


@admin.register(Commodity)
class CommodityAdmin(DetailedLogAdminMixin, DALFModelAdmin):
    list_display = ("name", "description", "_created_at", "_updated_at")
    search_fields = ("name", "description")
    readonly_fields = ("_created_at", "_updated_at")
    fieldsets = (
        ("اطلاعات کالا", {"fields": ("name", "description")}),
        ("زمان‌بندی", {"fields": ("_created_at", "_updated_at"), "classes": ("collapse",)}),
    )


@admin.register(Customer)
class CustomerAdmin(DetailedLogAdminMixin, DALFModelAdmin):
    list_display = ("name", "tax_id", "national_id", "contact", "address", "customer_type")
    search_fields = ("name", "tax_id", "national_id", "contact", "address")
    readonly_fields = ("_created_at", "_updated_at")
    fieldsets = (
        ("اطلاعات مشتری", {"fields": ("name", "customer_type", "tax_id", "national_id", "contact", "address")}),
        ("زمان‌بندی", {"fields": ("_created_at", "_updated_at"), "classes": ("collapse",)}),
    )


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
        "total_amount",
        "is_paid",
        "course",
        "items_amount",
        "discount",
        "vat",
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
    fieldsets = (
        ("اطلاعات فاکتور", {"fields": ("type", "date", "customer", "course", "orgnization", "description")}),
        ("مبالغ", {"fields": ("items_amount", "discount", "vat", "total_amount", "is_paid")}),
        ("زمان‌بندی", {"fields": ("_created_at", "_updated_at"), "classes": ("collapse",)}),
    )


class BigNumberInput(forms.NumberInput):
    def __init__(self, *args, **kwargs):
        attrs = kwargs.get("attrs", {})
        attrs["style"] = attrs.get("style", "") + "font-size: 1.2em; min-width: 140px;"
        super().__init__(*args, **kwargs)


class FinancialNumberFormMixin(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for _, field in self.fields.items():
            if isinstance(field.widget, forms.NumberInput):
                field.widget = BigNumberInput(attrs=field.widget.attrs)


class InvoiceItemAdminForm(FinancialNumberFormMixin, forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = "__all__"  # noqa


@admin.register(InvoiceItem)
class InvoiceItemAdmin(DetailedLogAdminMixin, DALFModelAdmin):
    form = InvoiceItemAdminForm
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
    fieldsets = (
        ("اطلاعات آیتم فاکتور", {"fields": ("invoice", "commodity", "description")}),
        ("مبالغ", {"fields": ("unit_price", "quantity", "discount", "vat", "total_price")}),
        ("زمان‌بندی", {"fields": ("_created_at", "_updated_at"), "classes": ("collapse",)}),
    )


class TransactionAdminForm(FinancialNumberFormMixin, forms.ModelForm):
    class Meta:
        model = Transaction
        fields = "__all__"  # noqa


@admin.register(Transaction)
class TransactionAdmin(DetailedLogAdminMixin, DALFModelAdmin):
    form = TransactionAdminForm
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
    readonly_fields = ("net_amount", "_created_at", "_updated_at")
    autocomplete_fields = (
        "invoice",
        "account",
        "course",
        "user_account",
        "entry_user",
    )
    fieldsets = (
        (
            "اطلاعات تراکنش",
            {
                "fields": (
                    "invoice",
                    "transaction_type",
                    "transaction_category",
                    "date",
                    "account",
                    "course",
                    "user_account",
                    "entry_user",
                    "tracking_code",
                    "name",
                    "description",
                )
            },
        ),
        ("مبالغ", {"fields": ("amount", "fee", "net_amount")}),
        ("زمان‌بندی", {"fields": ("_created_at", "_updated_at"), "classes": ("collapse",)}),
    )


class CourseTransactionInlineForm(forms.ModelForm):
    class Meta:
        model = CourseTransaction
        fields = "__all__"  # noqa
        help_texts = {
            "amount": "مبلغ به تومان",
            "fee": "کارمزد به تومان",
            "net_amount": "خالص مبلغ به تومان",
        }

    def __init__(self, *args, parent_registration=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent_registration = parent_registration

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.parent_registration is not None:
            instance.registration = self.parent_registration
            if hasattr(self.parent_registration, "course"):
                instance.course = self.parent_registration.course
        if commit:
            instance.save()
        return instance


class CourseTransactionInline(admin.TabularInline):
    model = CourseTransaction
    form = CourseTransactionInlineForm
    extra = 0
    readonly_fields = ("net_amount", "entry_user")
    exclude = ("course", "user_account",)
    show_change_link = True
    verbose_name = "تراکنش مالی ثبت‌نام"
    verbose_name_plural = "تراکنش‌های مالی ثبت‌نام"

    def get_formset(self, request, obj=None, **kwargs):
        FormSet = super().get_formset(request, obj, **kwargs)
        parent_registration = obj

        class WrappedFormSet(FormSet):
            def _construct_form(self, i, **form_kwargs):
                form_kwargs["parent_registration"] = parent_registration
                return super()._construct_form(i, **form_kwargs)

        return WrappedFormSet


@admin.register(CourseTransaction)
class CourseTransactionAdmin(DetailedLogAdminMixin, DALFModelAdmin):
    list_display = (
        "id",
        "transaction",
        "transaction_type",
        "transaction_category",
        "course",
        "registration",
        "amount",
        "fee",
        "net_amount",
        "date",
        "entry_user",
        "user_account",
        "customer_name",
        "tracking_code",
        "description",
        "_created_at",
        "_updated_at",
    )
    search_fields = (
        "transaction__id",
        "course__name",
        "registration__id",
        "entry_user__username",
        "user_account__username",
        "customer_name",
        "tracking_code",
        "description",
    )
    list_filter = (
        "transaction_type",
        "transaction_category",
        ("course", DALFRelatedFieldAjax),
        ("registration", DALFRelatedFieldAjax),
        ("entry_user", DALFRelatedFieldAjax),
        ("user_account", DALFRelatedFieldAjax),
        "date",
    )
    readonly_fields = ("net_amount", "_created_at", "_updated_at")
    autocomplete_fields = (
        "transaction",
        "course",
        "registration",
        "entry_user",
        "user_account",
    )
    fieldsets = (
        (
            "اطلاعات تراکنش دوره",
            {
                "fields": (
                    "transaction",
                    "transaction_type",
                    "transaction_category",
                    "course",
                    "registration",
                    "entry_user",
                    "user_account",
                    "customer_name",
                    "tracking_code",
                    "description",
                )
            },
        ),
        ("مبالغ", {"fields": ("amount", "fee", "net_amount")}),
        ("زمان‌بندی", {"fields": ("date", "_created_at", "_updated_at"), "classes": ("collapse",)}),
    )
