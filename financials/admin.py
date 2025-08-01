from dal import autocomplete
from dalf.admin import DALFModelAdmin, DALFRelatedFieldAjax
from django import forms
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from django.utils.html import format_html

from commons.admin import DetailedLogAdminMixin
from commons.forms import FinancialNumberFormMixin

from .models import Commodity, CourseTransaction, Customer, FinancialAccount, Invoice, InvoiceItem, Transaction


@admin.register(FinancialAccount)
class FinancialAccountAdmin(DetailedLogAdminMixin, DALFModelAdmin):
    list_display = ("name", "description", "_created_at", "_updated_at")
    search_fields = ("name", "description")
    readonly_fields = ("_created_at", "_updated_at", "balance")
    filter_horizontal = ("course",)
    fieldsets = (
        ("Account Information", {"fields": ("name", "description", "course", "asset_type", "balance")}),
        ("Timestamps", {"fields": ("_created_at", "_updated_at")}),
    )

    def balance(self, obj):
        amount = obj.balance()
        return f"{amount:,}" if amount else "0"


@admin.register(Commodity)
class CommodityAdmin(DetailedLogAdminMixin, DALFModelAdmin):
    list_display = ("name", "description", "_created_at", "_updated_at")
    search_fields = ("name", "description")
    readonly_fields = ("_created_at", "_updated_at")
    fieldsets = (
        ("Commodity Information", {"fields": ("name", "description")}),
        ("Timestamps", {"fields": ("_created_at", "_updated_at")}),
    )


@admin.register(Customer)
class CustomerAdmin(DetailedLogAdminMixin, DALFModelAdmin):
    list_display = ("name", "tax_id", "national_id", "contact", "address", "customer_type")
    search_fields = ("name", "tax_id", "national_id", "contact", "address")
    readonly_fields = ("_created_at", "_updated_at")
    fieldsets = (
        ("Customer Information", {"fields": ("name", "customer_type", "tax_id", "national_id", "contact", "address")}),
        ("Timestamps", {"fields": ("_created_at", "_updated_at")}),
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
        "organization",
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
        ("اطلاعات فاکتور", {"fields": ("type", "date", "customer", "course", "organization", "description")}),
        ("مبالغ", {"fields": ("items_amount", "discount", "vat", "total_amount", "is_paid")}),
        ("زمان‌بندی", {"fields": ("_created_at", "_updated_at")}),
    )


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
        ("زمان‌بندی", {"fields": ("_created_at", "_updated_at")}),
    )


class TransactionAdminForm(FinancialNumberFormMixin, forms.ModelForm):
    destination_account = forms.ModelChoiceField(
        queryset=FinancialAccount.objects.all(),
        widget=autocomplete.ModelSelect2(url="financialaccount-autocomplete"),
        label="Destination Account",
        required=False,
        help_text="Destination Account",
    )
    make_transfer = forms.BooleanField(required=False, initial=False, help_text="Make Transfer")

    class Meta:
        model = Transaction
        fields = "__all__"  # noqa

    def save(self, commit=True):
        instance = super().save(commit=commit)
        destination_account = self.cleaned_data.get("destination_account")
        make_transfer = self.cleaned_data.get("make_transfer", False)
        if destination_account and make_transfer:
            Transaction.objects.create(
                transaction_category=instance.transaction_category,
                transaction_type=3 - instance.transaction_type,
                account=destination_account,
                amount=instance.amount,
                course=instance.course,
                user_account=instance.user_account,
                entry_user=instance.entry_user,
                name=instance.name,
                transaction_date=instance.transaction_date,
                tracking_code=instance.tracking_code,
                description=f"{instance.description}\nTransfer for transfer",
            )
        return instance


@admin.register(Transaction)
class TransactionAdmin(DetailedLogAdminMixin, DALFModelAdmin):
    form = TransactionAdminForm
    list_display = (
        "id",
        "transaction_date",
        "ttype",
        "account",
        "tcategory",
        "amount",
        "fee",
        "name",
        "invoice",
        "tracking_code",
        "course",
        "user_account",
        "entry_user",
        "description",
        "net_amount",
        "_created_at",
        "_updated_at",
    )

    @admin.display(description="type", ordering="transaction_type")
    def ttype(self, obj):
        return obj.get_transaction_type_display()

    @admin.display(description="category", ordering="transaction_category")
    def tcategory(self, obj):
        return obj.get_transaction_category_display()

    search_fields = (
        "id",
        "user_account__username",
    )

    list_filter = (
        "transaction_type",
        ("account", DALFRelatedFieldAjax),
        ("course", DALFRelatedFieldAjax),
        ("invoice", DALFRelatedFieldAjax),
        ("user_account", DALFRelatedFieldAjax),
        ("entry_user", DALFRelatedFieldAjax),
        "transaction_date",
    )
    readonly_fields = ("net_amount", "entry_user", "_created_at", "_updated_at")
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
                    "transaction_date",
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
        ("زمان‌بندی", {"fields": ("_created_at", "_updated_at")}),
        (
            "transfer",
            {
                "fields": (
                    "destination_account",
                    "make_transfer",
                )
            },
        ),
    )
    ordering = ("-transaction_date",)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        try:
            transaction = self.get_object(request, object_id)
            if transaction:
                course_transactions_url = reverse("admin:financials_coursetransaction_changelist")
                course_transactions_url += f"?transaction__id__exact={transaction.id}"
                extra_context["go_to_course_transactions_button"] = format_html(
                    '<a class="button" href="{}" style="display:inline-block;">Go to Course Transactions</a>',
                    course_transactions_url,
                )
        except Exception:
            messages.error(request, "Error retrieving CourseTransaction.")
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("account", "course", "invoice", "user_account", "entry_user")

    def save_model(self, request, obj, form, change):
        if not change:
            obj.entry_user = request.user
        return super().save_model(request, obj, form, change)


class CourseTransactionInlineForm(FinancialNumberFormMixin, forms.ModelForm):
    class Meta:
        model = CourseTransaction
        fields = "__all__"  # noqa
        help_texts = {
            "amount": "مبلغ به تومان",
            "fee": "کارمزد به تومان",
            "net_amount": "خالص مبلغ به تومان",
        }

    def __init__(self, *args, parent_registration=None, request=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent_registration = parent_registration
        self.request = request
        if not self.instance.pk:
            self.fields["transaction_category"].initial = 10

        if parent_registration and hasattr(parent_registration, "course"):
            course = parent_registration.course
            self.fields["financial_account"].queryset = self.fields["financial_account"].queryset.filter(course=course)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.parent_registration is not None:
            instance.registration = self.parent_registration
            if hasattr(self.parent_registration, "course"):
                instance.course = self.parent_registration.course

        if not instance.pk and self.request:
            instance.entry_user = self.request.user

        if commit:
            instance.save()
        return instance


class CourseTransactionInline(admin.TabularInline):
    model = CourseTransaction
    form = CourseTransactionInlineForm
    extra = 0
    readonly_fields = ("net_amount", "entry_user", "_created_at", "_updated_at")
    exclude = (
        "course",
        "user_account",
    )
    show_change_link = True
    verbose_name = "تراکنش مالی ثبت‌نام"
    verbose_name_plural = "تراکنش‌های مالی ثبت‌نام"
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "transaction_date",
                    "transaction_type",
                    "transaction_category",
                    "financial_account",
                    "amount",
                    "fee",
                    "entry_user",
                    "tracking_code",
                    "description",
                    "_created_at",
                    "_updated_at",
                )
            },
        ),
    )

    def get_formset(self, request, obj=None, **kwargs):
        FormSet = super().get_formset(request, obj, **kwargs)
        parent_registration = obj

        class WrappedFormSet(FormSet):
            def get_form_kwargs(self, index):
                kwargs = super().get_form_kwargs(index)
                kwargs["parent_registration"] = parent_registration
                kwargs["request"] = request
                return kwargs

        return WrappedFormSet

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("financial_account", "course", "registration", "entry_user")
            .prefetch_related("financial_account__course")
        )


class CourseTransactionAdminForm(FinancialNumberFormMixin, forms.ModelForm):
    destination_account = forms.ModelChoiceField(
        queryset=FinancialAccount.objects.all(),
        widget=autocomplete.ModelSelect2(url="financialaccount-autocomplete"),
        label="Destination Account",
        required=False,
        help_text="Destination Account",
    )
    make_transfer = forms.BooleanField(required=False, initial=False, help_text="Make Transfer")

    class Meta:
        model = CourseTransaction
        fields = "__all__"  # noqa

    def save(self, commit=True):
        instance = super().save(commit=commit)
        destination_account = self.cleaned_data.get("destination_account")
        make_transfer = self.cleaned_data.get("make_transfer", False)
        if destination_account and make_transfer:
            CourseTransaction.objects.create(
                transaction_category=instance.transaction_category,
                transaction_type=3 - instance.transaction_type,
                financial_account=destination_account,
                amount=instance.amount,
                course=instance.course,
                registration=instance.registration,
                customer_name=instance.customer_name,
                entry_user=instance.entry_user,
                user_account=instance.user_account,
                transaction_date=instance.transaction_date,
                tracking_code=instance.tracking_code,
                description=f"{instance.description}\nTransfer for {instance.id}",
            )
        return instance


@admin.register(CourseTransaction)
class CourseTransactionAdmin(DetailedLogAdminMixin, DALFModelAdmin):
    form = CourseTransactionAdminForm
    list_display = (
        "id",
        "transaction",
        "transaction_type",
        "transaction_category",
        "financial_account",
        "course",
        "registration",
        "amount",
        "fee",
        "transaction_date",
        "entry_user",
        "user_account",
        "customer_name",
        "tracking_code",
        "description",
        "_created_at",
    )
    list_display_links = ("id", "transaction", "transaction_type")
    search_fields = (
        "id",
        "transaction__id",
        "user_account__username",
        "customer_name",
        "tracking_code",
    )
    list_filter = (
        "transaction_type",
        "transaction_category",
        ("transaction", DALFRelatedFieldAjax),
        ("financial_account", DALFRelatedFieldAjax),
        ("course", DALFRelatedFieldAjax),
        ("registration", DALFRelatedFieldAjax),
        ("entry_user", DALFRelatedFieldAjax),
        ("user_account", DALFRelatedFieldAjax),
        "transaction_date",
    )
    readonly_fields = ("net_amount", "entry_user", "_created_at", "_updated_at")
    autocomplete_fields = (
        "transaction",
        "financial_account",
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
                    "financial_account",
                    "course",
                    "registration",
                    "entry_user",
                    "user_account",
                    "customer_name",
                    "tracking_code",
                    "transaction_date",
                    "description",
                )
            },
        ),
        ("مبالغ", {"fields": ("amount", "fee", "net_amount")}),
        (None, {"fields": ("_created_at", "_updated_at")}),
        (
            "transfer",
            {
                "fields": (
                    "destination_account",
                    "make_transfer",
                )
            },
        ),
    )
    change_list_template = "admin/financials/coursetransaction/change_list.html"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "financial_account":
            course_id = None
            if hasattr(request, "resolver_match") and request.resolver_match:
                if "object_id" in request.resolver_match.kwargs:
                    try:
                        obj_id = request.resolver_match.kwargs["object_id"]
                        existing_obj = CourseTransaction.objects.get(pk=obj_id)
                        course_id = existing_obj.course_id
                    except CourseTransaction.DoesNotExist:
                        pass

            if not course_id:
                course_id = request.GET.get("course") or request.POST.get("course")

            if course_id:
                try:
                    kwargs["queryset"] = FinancialAccount.objects.filter(course=course_id)
                except Exception:
                    messages.error(request, "Error retrieving FinancialAccount.")

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.entry_user = request.user
        return super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = (
            super()
            .get_queryset(request)
            .select_related("financial_account", "course", "registration", "entry_user", "user_account", "transaction")
        )
        if not request.user.is_superuser:
            qs = qs.filter(course__managing_users=request.user)
        return qs

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        try:
            course_transaction = self.get_object(request, object_id)
            if course_transaction and not course_transaction.transaction:
                url = reverse("admin:make_course_transaction", args=[object_id])
                extra_context["make_transaction_button"] = format_html(
                    '<a class="button" href="{}" style="display:inline-block;">Make Transaction</a>', url
                )
        except Exception:
            messages.error(request, "Error retrieving CourseTransaction.")
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def make_course_transaction(self, request, object_id):
        try:
            course_transaction = self.get_object(request, object_id)
            if course_transaction is None:
                messages.error(request, "CourseTransaction not found.")
                return HttpResponseRedirect(reverse("admin:financials_coursetransaction_changelist"))

            if course_transaction.transaction:
                messages.warning(request, "Transaction already exists for this CourseTransaction.")
                return HttpResponseRedirect(reverse("admin:financials_coursetransaction_change", args=[object_id]))

            course_transaction.transaction = course_transaction.create_transaction(entry_user=request.user)
            course_transaction.save()

            messages.success(
                request,
                f"Transaction #{course_transaction.transaction.id} successfully created and linked to CourseTransaction #{course_transaction.id}.",
            )

        except Exception as e:
            messages.error(request, f"Error creating transaction: {e!s}")

        return HttpResponseRedirect(reverse("admin:financials_coursetransaction_change", args=[object_id]))

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:object_id>/make-transaction/",
                self.admin_site.admin_view(self.make_course_transaction),
                name="make_course_transaction",
            ),
        ]
        return custom_urls + urls
