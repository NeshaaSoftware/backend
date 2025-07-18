import re


def convert_to_english_digit(text: str) -> str:
    persian_arabic_to_english = {
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

    for persian_digit, english_digit in persian_arabic_to_english.items():
        text = text.replace(persian_digit, english_digit)

    return "".join(re.findall(r"\d", text))


def normalize_phone(phone: str) -> str | None:
    if not phone:
        return None

    phone = convert_to_english_digit(str(phone).strip())

    # Handle different Iranian phone number formats
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
    elif len(phone) > 15 or len(phone) < 10:
        return None

    return phone


def normalize_national_id(national_id: str) -> str | None:
    if not national_id:
        return None

    cleaned_id = convert_to_english_digit(str(national_id).strip())

    if len(cleaned_id) == 8:
        return "00" + cleaned_id
    elif len(cleaned_id) == 10:
        return cleaned_id

    return None


def get_status_from_text(status: str) -> tuple[int, int]:
    status_mapping = {
        ("انتقال به دوره های بعد", "انصراف قبل از دوره", "غایب", "انصراف پیش از دوره"): (2, 3),
        ("انصراف روز اول", "انتخاب نماندن"): (3, 3),
        ("انصراف روز اول - غایب", "ترک دوره"): (4, 3),
        ("تیم اجرایی",): (7, 3),
        ("مهمان",): (8, 3),
        ("شرکت کننده", "حاضر در دوره"): (9, 3),
        ("ثبت‌نام", "در انتظار پرداخت"): (1, 3),
        ("حاضر در دوره - انتظار پرداخت",): (9, 2),
        ("حاضر در دوره - عدم سررسید",): (9, 1),
        ("حاضر در دوره - تسویه",): (9, 3),
    }

    for status_texts, (status_code, payment_status) in status_mapping.items():
        if status in status_texts:
            return status_code, payment_status
    return 9, 3


def merge_user_data(source_user, target_user) -> None:
    from courses.models import Registration

    for reg in Registration.objects.filter(user=source_user):
        if not Registration.objects.filter(user=target_user, course=reg.course).exists():
            reg.user = target_user
            reg.save()
    merge_fields = [
        "telegram_id",
        "profession",
        "email",
        "national_id",
        "english_first_name",
        "english_last_name",
        "referer_name",
    ]

    for field in merge_fields:
        source_value = getattr(source_user, field)
        target_value = getattr(target_user, field)

        if source_value and not target_value:
            setattr(target_user, field, source_value)

    if target_user.gender is None and source_user.gender is not None:
        target_user.gender = source_user.gender

    if target_user.age in [None, 0] and source_user.age not in [None, 0]:
        target_user.age = source_user.age

    if source_user.more_phone_numbers:
        target_user.more_phone_numbers = (
            target_user.more_phone_numbers + "\n" + source_user.more_phone_numbers
        ).strip()

    source_user.description = (
        f"{source_user.first_name} {source_user.last_name} "
        f"has been merged into {target_user.id}\n{source_user.username}"
    )
    source_user.first_name = "merged_user"
    source_user.last_name = f"{source_user.id}"
    source_user.username = f"merged_user_{source_user.id}"
    source_user.is_active = False
    source_user.main_user = target_user

    source_user.save()
    target_user.save()


def find_and_merge_duplicate_users() -> None:
    from users.models import User

    users = User.objects.values_list("first_name", "last_name", "id", "phone_number")
    user_dic = {}

    for first_name, last_name, user_id, phone_number in users:
        if last_name:
            name_key = f"{first_name}{last_name}".replace(" ", "").lower()

            if name_key not in user_dic:
                user_dic[name_key] = []

            user_dic[name_key].append({"id": user_id, "phone": str(phone_number) if phone_number else None})

    for _, user_list in user_dic.items():
        if len(user_list) > 1:
            users_with_phone = [u for u in user_list if u["phone"]]
            users_without_phone = [u for u in user_list if not u["phone"]]

            if users_with_phone and users_without_phone:
                target_user = User.objects.get(id=users_with_phone[0]["id"])

                for user_data in users_without_phone:
                    source_user = User.objects.get(id=user_data["id"])
                    merge_user_data(source_user, target_user)
