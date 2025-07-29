from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from commons.utils import get_jdatetime_now_with_timezone
from courses.models import Course, CourseSession, CourseType, Registration
from users.models import CrmUser, User


class Command(BaseCommand):
    help = "Populate the database with initial or test data."

    def add_arguments(self, parser):
        parser.add_argument("--users", type=int, default=1000, help="Number of test users to create (default: 1000)")
        parser.add_argument("--courses", type=int, default=50, help="Number of courses to create (default: 50)")

    def handle(self, *args, **options):
        num_users = options["users"]
        num_courses = options["courses"]

        with transaction.atomic():
            self.create_superuser()
            self.create_users(num_users)
            self.create_course_types()
            self.create_courses(num_courses)
            self.create_sessions()
            self.create_registrations()
            self.setup_staff_users()
            self.create_groups_and_permissions()
            self.assign_supporting_users()

    def create_superuser(self):
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(username="admin", phone_number="+989120000000", email="admin@example.com", password="adminpass")
            self.stdout.write(self.style.SUCCESS("Superuser created"))

    def create_users(self, num_users):
        done_users = set(User.objects.values_list("username", flat=True))
        users = [
            User(
                username=f"testuser{i}",
                phone_number=f"+9891200{10000 + i:05d}",
                password="testpass",
                first_name=f"Test{i}",
                last_name="User",
            )
            for i in range(num_users)
            if f"testuser{i}" not in done_users
        ]
        if users:
            User.objects.bulk_create(users)
        self.stdout.write(f"Users created: {User.objects.count()}")

    def create_course_types(self):
        done_course_types = set(CourseType.objects.values_list("id", flat=True))
        course_types_data = {1: ("L1", "ال۱"), 2: ("L2", "ال۲"), 3: ("L3", "ال۳"), 4: ("L4", "ال۴")}
        course_types = [
            CourseType(id=i, name=name, name_fa=name_fa) for i, (name, name_fa) in course_types_data.items() if i not in done_course_types
        ]
        if course_types:
            CourseType.objects.bulk_create(course_types)
        self.stdout.write(f"Course types created: {CourseType.objects.count()}")

    def create_courses(self, num_courses):
        done_courses = set(Course.objects.values_list("number", flat=True))
        try:
            ct1 = CourseType.objects.get(id=1)
        except CourseType.DoesNotExist:
            self.stdout.write(self.style.ERROR("CourseType with id=1 not found"))
            return

        courses = [Course(course_type=ct1, number=i) for i in range(num_courses) if i not in done_courses]
        if courses:
            Course.objects.bulk_create(courses)
        self.stdout.write(f"Courses created: {Course.objects.count()}")

    def create_sessions(self):
        done_sessions = set(CourseSession.objects.values_list("session_name", flat=True))
        sessions = [
            CourseSession(
                course_id=i // 10 + 1,
                session_name=f"Session {i % 10 + 1}",
                start_date=get_jdatetime_now_with_timezone(),
                end_date=get_jdatetime_now_with_timezone() + timezone.timedelta(days=i),
                location=f"Location {i + 1}",
            )
            for i in range(300)
            if f"Session {i % 10 + 1}" not in done_sessions
        ]
        if sessions:
            CourseSession.objects.bulk_create(sessions)
        self.stdout.write(f"Sessions created: {CourseSession.objects.count()}")

    def create_registrations(self):
        done_registrations = {f"{a[0]}-{a[1]}" for a in Registration.objects.values_list("course_id", "user_id")}
        registrations = [
            Registration(
                course_id=(i % 50) + 1,
                user_id=(i % 1000) + 1,
                status=1,
            )
            for i in range(2000)
            if f"{(i % 50) + 1}-{(i % 1000) + 1}" not in done_registrations
        ]
        if registrations:
            Registration.objects.bulk_create(registrations)
        self.stdout.write(f"Registrations created: {Registration.objects.count()}")

    def setup_staff_users(self):
        try:
            user1 = User.objects.get(username="testuser1")
            user2 = User.objects.get(username="testuser2")
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR("Required test users not found"))
            return

        done_crms = set(CrmUser.objects.values_list("user_id", flat=True))
        crm_users = [
            CrmUser(
                user_id=i,
                status=1,
                last_follow_up=get_jdatetime_now_with_timezone(),
                next_follow_up=get_jdatetime_now_with_timezone() + timezone.timedelta(days=i % 10),
                joined_main_group=True,
            )
            for i in range(1, 201)
            if i not in done_crms
        ]

        if crm_users:
            CrmUser.objects.bulk_create(crm_users)

        CrmUser.objects.filter(id__lte=200).update(supporting_user=user2)
        CrmUser.objects.filter(id__lte=100).update(supporting_user=user1)

        user1.is_staff = True
        user1.set_password("testpass")
        user1.save()

        user2.is_staff = True
        user2.set_password("testpass")
        user2.save()

        self.stdout.write(f"Staff users configured: {user1.username}, {user2.username}")

    def create_groups_and_permissions(self):
        try:
            user1 = User.objects.get(username="testuser1")
            user2 = User.objects.get(username="testuser2")
        except User.DoesNotExist:
            return

        try:
            Course.objects.get(course_type=1, number=1).instructors.add(user1)
            Course.objects.get(course_type=1, number=2).managing_users.add(user1)
            Course.objects.get(course_type=1, number=3).supporting_users.add(user1)
        except Course.DoesNotExist:
            self.stdout.write(self.style.WARNING("Some courses not found for user assignment"))

        if not Group.objects.filter(name="supporting").exists():
            group_supporting = Group.objects.create(name="supporting")
            permissions_code = [
                "add_registration",
                "change_registration",
                "view_registration",
                "view_course",
                "view_crmuser",
                "view_user",
                "view_crmlog",
                "add_crmlog",
                "change_crmlog",
            ]
            valid_permissions = Permission.objects.filter(codename__in=permissions_code)
            group_supporting.permissions.set(valid_permissions)
            user1.groups.add(group_supporting)
            user2.groups.add(group_supporting)
            self.stdout.write("Supporting group created and assigned")

    def assign_supporting_users(self):
        try:
            user1 = User.objects.get(username="testuser1")
            user2 = User.objects.get(username="testuser2")
        except User.DoesNotExist:
            return

        registrations = Registration.objects.select_related("user").filter(course_id=3)
        updated_registrations = []

        for registration in registrations:
            registration.supporting_user = user1 if registration.user.pk % 2 == 0 else user2
            updated_registrations.append(registration)

        if updated_registrations:
            Registration.objects.bulk_update(updated_registrations, ["supporting_user"])

        self.stdout.write(f"Supporting users assigned to {len(updated_registrations)} registrations")
