import re


def convert_to_english_digit(text):
    to_english = {
        "۰": "0",
        "۱": "1",
        "۲": "2",
        "۳": "3",
        "۴": "4",
        "۵": "5",
        "۶": "6",
        "۷": "7",
        "۸": "8",
        "۹": "9",
        "٠": "0",
        "١": "1",
        "٢": "2",
        "٣": "3",
        "٤": "4",
        "٥": "5",
        "٦": "6",
        "٧": "7",
        "٨": "8",
        "٩": "9",
    }
    for digit, english_digit in to_english.items():
        text = text.replace(digit, english_digit)
    text = "".join(re.findall(r"\d", text))
    return text


def normalize_phone(phone):
    phone = convert_to_english_digit(str(phone).strip())
    if len(phone) == 11 and phone.startswith("09"):
        return "+98" + phone[1:]
    elif len(phone) == 10 and phone.startswith("9"):
        return "+98" + phone
    elif len(phone) == 13 and phone.startswith("+98"):
        return phone
    elif len(phone) == 14 and phone.startswith("0098"):
        return "+" + phone[2:]
    elif len(phone) == 12 and phone.startswith("98"):
        return "+" + phone
    return None


def get_status_from_text(status):
    if status in ["انتقال به دوره های بعد", "انصراف قبل از دوره", "غایب", "انصراف پیش از دوره"]:
        return 2, 3
    elif status in ["انصراف روز اول", "انتخاب نماندن"]:
        return 3, 3
    elif status in ["انصراف روز اول - غایب", "ترک دوره"]:
        return 4, 3
    elif status in ["تیم اجرایی"]:
        return 7, 3
    elif status in ["مهمان"]:
        return 8, 3
    elif status in ["شرکت کننده", "حاضر در دوره"]:
        return 9, 3
    elif status in ["ثبت‌نام", "در انتظار پرداخت"]:
        return 1, 3
    elif status in ["حاضر در دوره - انتظار پرداخت"]:
        return 9, 2
    elif status in ["حاضر در دوره - عدم سررسید"]:
        return 9, 1
    elif status in ["حاضر در دوره - تسویه"]:
        return 9, 3
    return 9, 3
