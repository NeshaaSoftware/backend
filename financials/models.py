import jdatetime
from django.core.validators import MinValueValidator
from django.db import models
from django_jalali.db import models as jmodels

from commons.models import TimeStampedModel
from courses.models import Course


ASSET_TYPE_CHOICES = [
    (1, "ریال"),
    (2, "صندوق درآمد ثابت"),
    (3, "رمز ارز"),
    (4, "ارز"),
]
class FinancialAccount(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    course = models.ManyToManyField(Course, related_name="financial_accounts", blank=True)
    description = models.TextField(blank=True, default="")
    asset_type = models.IntegerField(choices=ASSET_TYPE_CHOICES, default=1, help_text="نوع دارایی")

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
    organization = models.IntegerField(choices=[(1, "Neshaa"), (2, "azno")], default=1)
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
TRANSACTION_CATEGORY_COURSE_REGISTRATION = 1
TRANSACTION_CATEGORY_COURSE_COST = 2
TRANSACTION_CATEGORY_COURSE_INSTULMENT = 3
TRANSACTION_CATEGORY_CREDIT = 4
TRANSACTION_CATEGORY_OPERATION_COST = 5
TRANSACTION_CATEGORY_COMPENSATION = 6
TRANSACTION_CATEGORY_STATIONERY = 7
TRANSACTION_CATEGORY_INVESTMENT = 8
TRANSACTION_CATEGORY_PETTY_CASH = 9

TRANSACTION_CATEGORY_CHOICES = [
    (TRANSACTION_CATEGORY_COURSE_REGISTRATION, "ثبت‌نام دوره"),
    (TRANSACTION_CATEGORY_COURSE_COST, "هزینه دوره"),
    (TRANSACTION_CATEGORY_COURSE_INSTULMENT, "قسط دوره"),
    (TRANSACTION_CATEGORY_CREDIT, "شارژ اعتبار"),
    (TRANSACTION_CATEGORY_OPERATION_COST, "هزینه عملیاتی"),
    (TRANSACTION_CATEGORY_COMPENSATION, "جبران خدمات"),
    (TRANSACTION_CATEGORY_STATIONERY, "تجهیزات"),
    (TRANSACTION_CATEGORY_INVESTMENT, "سرمایه‌گذاری"),
    (TRANSACTION_CATEGORY_PETTY_CASH, "تنخواه"),
]


class Transaction(TimeStampedModel):
    invoice = models.ForeignKey(Invoice, null=True, blank=True, on_delete=models.SET_NULL, related_name="transactions")
    account = models.ForeignKey(FinancialAccount, on_delete=models.CASCADE, related_name="transactions")
    course = models.ForeignKey(Course, null=True, blank=True, on_delete=models.SET_NULL)
    transaction_type = models.IntegerField(choices=TRANSACTION_TYPE_CHOICES, default=1)
    transaction_category = models.IntegerField(choices=TRANSACTION_CATEGORY_CHOICES, default=1)
    transaction_date = jmodels.jDateTimeField(default=jdatetime.datetime.now, db_index=True, help_text="تاریخ تراکنش")
    amount = models.PositiveIntegerField()
    fee = models.PositiveIntegerField()
    net_amount = models.PositiveIntegerField()
    name = models.CharField(max_length=100, blank=True, default="")
    user_account = models.ForeignKey("users.User", null=True, blank=True, on_delete=models.SET_NULL, related_name="transactions")
    tracking_code = models.CharField(max_length=100, blank=True, default="")
    entry_user = models.ForeignKey("users.User", null=True, blank=True, on_delete=models.SET_NULL, related_name="entry_transactions")
    description = models.TextField(blank=True, default="")

    def save(self, *args, **kwargs) -> None:
        if self.transaction_type == 1:
            self.net_amount = self.amount - self.fee
        else:
            self.net_amount = self.amount + self.fee
        return super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.id}-{self.amount}-{self.account.name}-{self.get_transaction_type_display()}-{self.get_transaction_category_display()}"
        )


COST_CATEGORY_HOTEL = 1
COST_CATEGORY_EXECUTIVE_CATERING = 2
COST_CATEGORY_EXECUTIVE_TRANSPORTATION = 3
COST_CATEGORY_EQUIPMENT = 4
COST_CATEGORY_SERVICE_PERSONNEL = 5
COST_CATEGORY_EXECUTIVE_COMPENSATION = 6
COST_CATEGORY_STATIONERY = 7
COST_CATEGORY_CATERING = 8
COST_CATEGORY_CHARGING_CREDIT = 9
INCOME_CATEGORY_REGISTRATION = 10
INCOME_CATEGORY_INSTULLMENT = 11
COURSE_TRANSACTION_CATEGORY_PETTY_CASH = 12

COURSE_TRANSACTION_CATEGORY_CHOICES = [
    (COST_CATEGORY_HOTEL, "اقامت هتل"),
    (COST_CATEGORY_EXECUTIVE_CATERING, "پذیرایی تیم اجرایی"),
    (COST_CATEGORY_EXECUTIVE_TRANSPORTATION, "جابجایی تیم اجرایی"),
    (COST_CATEGORY_EQUIPMENT, "تجهیزات"),
    (COST_CATEGORY_SERVICE_PERSONNEL, "نیروی خدماتی"),
    (COST_CATEGORY_EXECUTIVE_COMPENSATION, "جبران خدمات تیم اجرا"),
    (COST_CATEGORY_STATIONERY, "لوازم تحریر"),
    (COST_CATEGORY_CATERING, "پذیرایی"),
    (COST_CATEGORY_CHARGING_CREDIT, "شارژ اعتبار"),
    (INCOME_CATEGORY_REGISTRATION, "ثبت‌نام"),
    (INCOME_CATEGORY_INSTULLMENT, "قسط"),
    (COURSE_TRANSACTION_CATEGORY_PETTY_CASH, "تنخواه"),
]

FIXED_COST_CATEGORY = [1, 2, 3, 4, 5, 6]
VARIABLE_COST_CATEGORY = [7, 8, 9]


class CourseTransaction(TimeStampedModel):
    title = models.CharField(max_length=200, blank=True, default="")
    transaction_type = models.IntegerField(choices=TRANSACTION_TYPE_CHOICES, default=1)
    transaction_category = models.IntegerField(choices=COURSE_TRANSACTION_CATEGORY_CHOICES, default=10)
    financial_account = models.ForeignKey(FinancialAccount, on_delete=models.CASCADE, related_name="course_transactions")
    transaction = models.ForeignKey("Transaction", blank=True, null=True, on_delete=models.SET_NULL, related_name="course_transactions")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="transactions")
    registration = models.ForeignKey("courses.Registration", on_delete=models.CASCADE, related_name="transactions", null=True, blank=True)
    amount = models.PositiveIntegerField(help_text="تومان")
    fee = models.PositiveIntegerField(default=0, help_text="تومان")
    net_amount = models.PositiveIntegerField(help_text="تومان")
    customer_name = models.CharField(max_length=100, blank=True, default="")
    user_account = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="course_transactions")
    transaction_date = jmodels.jDateTimeField(default=jdatetime.datetime.now, db_index=True, help_text="تاریخ تراکنش")
    tracking_code = models.CharField(max_length=100, blank=True, default="")
    entry_user = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="course_transactions_entry")
    description = models.TextField(blank=True, default="")

    def save(self, *args, **kwargs) -> None:
        if self.transaction_type == 1:
            self.net_amount = self.amount - self.fee
        else:
            self.net_amount = self.amount + self.fee
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.id}-{self.amount}-{self.title}-{self.get_transaction_type_display()}-{self.get_transaction_category_display()}-{self.course.course_name}"

    def create_transaction(self, entry_user=None) -> Transaction:
        if self.transaction is not None:
            return None
        transaction_category_mapping = {
            1: 2,
            2: 2,
            3: 2,
            4: 2,
            5: 2,
            6: 2,
            7: 2,
            8: 2,
            9: 4,
            10: 1,
            11: 3,
            12: 9,
        }

        transaction_category = transaction_category_mapping.get(self.transaction_category, 1)
        transaction = Transaction.objects.create(
            account=self.financial_account,
            course=self.course,
            transaction_type=self.transaction_type,
            transaction_category=transaction_category,
            transaction_date=self.transaction_date,
            amount=self.amount,
            fee=self.fee,
            user_account=self.user_account,
            tracking_code=self.tracking_code,
            entry_user=entry_user or self.entry_user,
            description=f"CT #{self.id}",
        )

        return transaction
