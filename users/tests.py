from django.test import TestCase
from commons.utils import arabic_to_persian_characters

class CoursePermissionTest(TestCase):
    def setUp(self):
        pass

    def test_user_name_convert(self):
        assert arabic_to_persian_characters("كلمه") == "کلمه"
        assert arabic_to_persian_characters("نيما") == "نیما"
        