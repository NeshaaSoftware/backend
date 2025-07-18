from django.core.validators import MinValueValidator
from django.db import models
from django_jalali.db import models as jmodels

from commons.models import TimeStampedModel
from courses.models import Course


class FinancialAccount(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    course = models.ManyToManyField(Course, related_name="financial_accounts", blank=True)
    description = models.TextField(blank=True, default="")

    def __str__(self):
        return self.name


class Commodity(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, default="")

    class Meta:
        verbose_name = "Commodity"
        verbose_name_plural = "Commodities"

    def __str__(self):
        return self.name


CUSTOMER_TYPE_CHOICES = [
    (1, "حقیقی"),
    (2, "حقوقی"),
]


class Customer(TimeStampedModel):
    name = models.CharField(max_length=200)
    customer_type = models.IntegerField(choices=CUSTOMER_TYPE_CHOICES, default=1)
    tax_id = models.CharField(max_length=50, null=True, blank=True, unique=True, db_index=True)
    national_id = models.CharField(max_length=50, null=True, blank=True, unique=True, db_index=True)
    address = models.TextField(blank=True, default="")
    contact = models.CharField(max_length=200, blank=True, default="")

    def __str__(self):
        return self.name


INVOICE_TYPE_CHOICES = [(1, "خرید"), (2, "فروش")]


class Invoice(TimeStampedModel):
    orgnization = models.IntegerField(choices=[(1, "Neshaa"), (2, "azno")], default=1)
    type = models.IntegerField(choices=INVOICE_TYPE_CHOICES)
    date = jmodels.jDateField()
    course = models.ForeignKey(Course, null=True, blank=True, on_delete=models.SET_NULL, related_name="invoices")
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.SET_NULL)
    items_amount = models.PositiveBigIntegerField(default=0)
    discount = models.PositiveIntegerField(default=0)
    vat = models.PositiveIntegerField(default=0)
    total_amount = models.PositiveBigIntegerField(default=0)
    is_paid = models.BooleanField(default=False)
    description = models.TextField(blank=True, default="")

    def save(self, *args, **kwargs):
        self.update_items_amount()
        self.update_total_amount()
        return super().save(*args, **kwargs)

    def update_items_amount(self):
        total = self.items.aggregate(total=models.Sum("total_price"))["total"] or 0
        self.items_amount = total

    def update_total_amount(self):
        self.total_amount = self.items_amount - self.discount + self.vat

    @property
    def balance(self):
        from django.db.models import Sum

        total = self.transactions.aggregate(total=Sum("amount")).get("total") or 0
        return total - self.total_amount


class InvoiceItem(TimeStampedModel):
    invoice = models.ForeignKey(Invoice, related_name="items", on_delete=models.CASCADE)
    commodity = models.ForeignKey(Commodity, on_delete=models.CASCADE)
    description = models.CharField(max_length=200, blank=True, default="")
    unit_price = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    discount = models.PositiveIntegerField(default=0)
    vat = models.PositiveIntegerField(default=0)
    total_price = models.PositiveBigIntegerField(blank=True, default=0)

    def save(self, *args, **kwargs):
        self.total_price = max((self.unit_price * self.quantity) - self.discount + self.vat, 0)
        result = super().save(*args, **kwargs)
        if self.invoice:
            self.invoice.save()
        return result

    def delete(self, *args, **kwargs):
        invoice = self.invoice
        result = super().delete(*args, **kwargs)
        if invoice:
            invoice.save()
        return result


TRANSACTION_TYPE_CHOICES = [(1, "دریافت"), (2, "برداشت")]
TRANSACTION_CATEGORY_CHOICES = [
    (1, "ثبت‌نام دوره"),
    (2, "هزینه دوره"),
    (3, "قسط دوره"),
    (4, "شارژ اعتبار"),
    (5, "هزینه عملیاتی"),
    (6, "جبران خدمات"),
    (7, "تجهیزات"),
    (8, "سرمایه‌گذاری"),
]


class Transaction(TimeStampedModel):
    invoice = models.ForeignKey(Invoice, null=True, blank=True, on_delete=models.SET_NULL, related_name="transactions")
    account = models.ForeignKey(FinancialAccount, on_delete=models.CASCADE, related_name="transactions")
    course = models.ForeignKey(Course, null=True, blank=True, on_delete=models.SET_NULL)
    transaction_type = models.IntegerField(choices=TRANSACTION_TYPE_CHOICES, default=1)
    transaction_category = models.IntegerField(choices=TRANSACTION_CATEGORY_CHOICES, default=1)
    date = jmodels.jDateField()
    amount = models.PositiveIntegerField()
    fee = models.PositiveIntegerField()
    net_amount = models.PositiveIntegerField()
    name = models.CharField(max_length=100, blank=True, default="")
    user_account = models.ForeignKey(
        "users.User", null=True, blank=True, on_delete=models.SET_NULL, related_name="transactions"
    )
    tracking_code = models.CharField(max_length=100, blank=True, default="")
    entry_user = models.ForeignKey(
        "users.User", null=True, blank=True, on_delete=models.SET_NULL, related_name="entry_transactions"
    )
    description = models.TextField(blank=True, default="")

    def save(self, *args, **kwargs) -> None:
        if self.transaction_type == 1:
            self.net_amount = self.amount - self.fee
        else:
            self.net_amount = self.amount + self.fee
        return super().save(*args, **kwargs)


COST_CATEGORY_HOTEL = "اقامت هتل"
COST_CATEGORY_EXECUTIVE_CATERING = "پذیرایی تیم اجرایی"
COST_CATEGORY_EXECUTIVE_TRANSPORTATION = "جابجایی تیم اجرایی"
COST_CATEGORY_EQUIPMENT = "تجهیزات"
COST_CATEGORY_SERVICE_PERSONNEL = "نیروی خدماتی"
COST_CATEGORY_EXECUTIVE_COMPENSATION = "جبران خدمات تیم اجرا"
COST_CATEGORY_STATIONERY = "لوازم تحریر"
COST_CATEGORY_CATERING = "پذیرایی"
COST_CATEGORY_CHARGING_CREDIT = "شارژ اعتبار"
INCOME_CATEGORY_REGISTRATION = "ثبت‌نام"
INCOME_CATEGORY_INSTULLMENT = "قسط"

COURSE_TRANSACTION_CATEGORY_CHOICES = [
    (1, COST_CATEGORY_HOTEL),
    (2, COST_CATEGORY_EXECUTIVE_CATERING),
    (3, COST_CATEGORY_EXECUTIVE_TRANSPORTATION),
    (4, COST_CATEGORY_EQUIPMENT),
    (5, COST_CATEGORY_SERVICE_PERSONNEL),
    (6, COST_CATEGORY_EXECUTIVE_COMPENSATION),
    (7, COST_CATEGORY_STATIONERY),
    (8, COST_CATEGORY_CATERING),
    (9, COST_CATEGORY_CHARGING_CREDIT),
    (10, INCOME_CATEGORY_REGISTRATION),
    (11, INCOME_CATEGORY_INSTULLMENT),
]

FIXED_COST_CATEGORY = [1, 2, 3, 4, 5, 6]
VARIABLE_COST_CATEGORY = [7, 8, 9]


class CourseTransaction(TimeStampedModel):
    title = models.CharField(max_length=200, blank=True, default="")
    transaction_type = models.IntegerField(choices=TRANSACTION_TYPE_CHOICES, default=1)
    transaction_category = models.IntegerField(choices=COURSE_TRANSACTION_CATEGORY_CHOICES, default=1)
    financial_account = models.ForeignKey(
        FinancialAccount, on_delete=models.CASCADE, related_name="course_transactions"
    )
    transaction = models.ForeignKey(
        "Transaction", blank=True, null=True, on_delete=models.SET_NULL, related_name="course_transactions"
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="transactions")
    registration = models.ForeignKey(
        "courses.Registration", on_delete=models.CASCADE, related_name="transactions", null=True, blank=True
    )
    amount = models.PositiveIntegerField()
    fee = models.PositiveIntegerField(default=0)
    net_amount = models.PositiveIntegerField()
    customer_name = models.CharField(max_length=100, blank=True, default="")
    user_account = models.ForeignKey(
        "users.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="course_transactions"
    )
    date = jmodels.jDateField()
    tracking_code = models.CharField(max_length=100, blank=True, default="")
    entry_user = models.ForeignKey(
        "users.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="course_transactions_entry"
    )
    description = models.TextField(blank=True, default="")

    def save(self, *args, **kwargs) -> None:
        if self.transaction_type == 1:
            self.net_amount = self.amount - self.fee
        else:
            self.net_amount = self.amount + self.fee
        return super().save(*args, **kwargs)
