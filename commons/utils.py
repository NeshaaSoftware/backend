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
    elif len(phone) > 15 or len(phone) < 10:
        return None
    return phone


def get_national_id(national_id):
    if not national_id:
        return None
    if len(str(national_id).strip()) == 8:
        return "00" + convert_to_english_digit(str(national_id)).strip()
    return convert_to_english_digit(str(national_id)).strip()


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


def move_user(user1, user2):
    from courses.models import Registration

    for reg in Registration.objects.filter(user_id=user1.id):
        if not Registration.objects.filter(user_id=user2.id, course=reg.course).exists():
            reg.user_id = user2.id
            reg.save()
    user2.telegram_id = user1.telegram_id if user2.telegram_id in [None, ""] else user2.telegram_id
    user2.profession = user1.profession if user2.profession in [None, ""] else user2.profession
    user2.more_phone_numbers = (user1.more_phone_numbers + user2.more_phone_numbers).strip()
    user2.email = user1.email if user2.email in [None, ""] else user2.email
    user2.national_id = user1.national_id if user2.national_id in [None, ""] else user2.national_id
    user2.english_first_name = (
        user1.english_first_name if user2.english_first_name in [None, ""] else user2.english_first_name
    )
    user2.english_last_name = (
        user1.english_last_name if user2.english_last_name in [None, ""] else user2.english_last_name
    )
    user2.referer_name = user1.referer_name if user2.referer_name in [None, ""] else user2.referer_name
    user2.gender = user1.gender if user2.gender is None else user2.gender
    user2.age = user1.age if user2.age in [None, 0] else user2.age
    user1.description = f"{user1.first_name} {user1.last_name} has been merged into {user2.id}" + "\n" + user1.username
    user1.first_name = "testuser"
    user1.last_name = f"{user1.id}"
    user1.username = f"testuser{user1.id}"
    user1.active = False
    user1.main_user = user2
    user1.save()
    user2.save()


def merge_duplicate_users():
    from users.models import User

    users = User.objects.values_list("first_name", "last_name", "id", "phone_number")
    user_dic = {}
    for u in users:
        if u[1] != "":
            k = f"{u[0]}{u[1]}".replace(" ", "")
            if k not in user_dic:
                user_dic[k] = [[str(u[3]) if u[3] else None, u[2]]]
            else:
                user_dic[k].append([str(u[3]) if u[3] else None, u[2]])

    for k in user_dic:
        if len(user_dic[k]) > 1:
            if user_dic[k][0][0] is None:
                move_user(User.objects.get(id=user_dic[k][0][1]), User.objects.get(id=user_dic[k][1][1]))
            elif user_dic[k][1][0] is None:
                move_user(User.objects.get(id=user_dic[k][1][1]), User.objects.get(id=user_dic[k][0][1]))
