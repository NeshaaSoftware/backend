from email import header
import requests
from django.conf import settings
from django.utils import timezone
from datetime import datetime


def get_payping_transactions(from_date, to_date):
    headers = {
      "Authorization": f"Bearer {settings.PAYPING_TOKEN}",
      "Content-Type": "application/json"
    }
    request_json = {
        "offset": 0,
        "limit": 50,
        "transactionType": 6,
        "fromDate": from_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "toDate": to_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    data = []
    len_data = 50
    while len_data == 50:
        resp = requests.post(url="https://api.payping.ir/v1/report/TransactionReport", headers=headers, json=request_json)
        data = data + resp.json()
        len_data = len(resp.json())
        request_json["offset"] += len_data
    return data

def make_payping_transaction(res, fee, transaction_dic=None):
    amount = res["amount"]
    is_paid = res["isPaid"]
    if is_paid is False or amount <= 0:
        return False
    name = res["name"]
    description = f'{name if name else ""}\n{res["description"]}\n{res["cardNo"]}\n{res["code"]}'.strip()
    date = datetime.strptime(res["payDate"], "%Y-%m-%dT%H:%M:%S.%f")
    date = timezone.make_aware(date)
    date = date.replace(microsecond=0)
    phone_number = res["payerIdentity"]
    tracking_code = res["invoiceNo"]
    
    if transaction_dic and transaction_dic.get(tracking_code, None) is not None:
        d = transaction_dic[tracking_code][1]
        if date.date() == d.date() and date.time() == d.time():
            return False
    phone_number = normalize_phone(phone_number)
    
    user = None
    if User.objects.filter(phone_number=phone_number).count() != 0:
        user = User.objects.get(phone_number=phone_number)
    
    t = Transaction.objects.create(
        account=payping,
        user_account=user,
        transaction_date=date,
        amount=amount,
        description=description,
        tracking_code=tracking_code,
        transaction_type=1,
        transaction_category=1,
        fee=fee
    )
    return True

