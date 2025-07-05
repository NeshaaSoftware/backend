from django.core.management.base import BaseCommand
from django.utils import timezone

from users.models import CrmUser


class Command(BaseCommand):
    help = "Populate the database with initial or test data."

    def handle(self, *args, **options):
        from django.contrib.auth.models import Group, Permission

        from courses.models import Course, CourseSession, CourseType, Registration
        from users.models import User

        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                username="admin", phone_number="+989120000000", email="admin@example.com", password="adminpass"
            )
        done_users = dict.fromkeys(User.objects.values_list("username", flat=True), True)
        users = [
            User(
                username=f"testuser{i}",
                phone_number="+9891200" + str(10000 + i),
                password="testpass",
                first_name=f"Test{i}",
                last_name="User",
            )
            for i in range(10000)
            if f"testuser{i}" not in done_users
        ]
        if users:
            User.objects.bulk_create(users)
        done_course_types = dict.fromkeys(CourseType.objects.values_list("id", flat=True), True)
        course_types = {1: ("L1", "ال۱"), 2: ("L2", "ال۲"), 3: ("L3", "ال۳"), 4: ("L4", "ال۴")}
        course_types = [
            CourseType(id=i, name=name, name_fa=name_fa)
            for i, (name, name_fa) in course_types.items()
            if i not in done_course_types
        ]
        if course_types:
            CourseType.objects.bulk_create(course_types)
        print("Course types created:", CourseType.objects.count())
        done_courses = dict.fromkeys(Course.objects.values_list("number", flat=True), True)
        ct1 = CourseType.objects.get(id=1)
        courses = [Course(course_type=ct1, number=i) for i in range(300) if i not in done_courses]
        if courses:
            Course.objects.bulk_create(courses)
        print("Courses created:", Course.objects.count())
        done_sessions = dict.fromkeys(CourseSession.objects.values_list("session_name", flat=True), True)
        sessions = [
            CourseSession(
                course_id=i // 10 + 1,
                session_name=f"Session {i % 10 + 1}",
                start_date=timezone.now(),
                end_date=timezone.now() + timezone.timedelta(days=i),
                location="Location " + str(i + 1),
            )
            for i in range(3000)
            if f"Session {i + 1}" not in done_sessions
        ]
        if sessions:
            CourseSession.objects.bulk_create(sessions)
        print("Sessions created:", CourseSession.objects.count())
        done_registrations = {
            (f"{a[0]}-{a[1]}"): True for a in Registration.objects.values_list("course_id", "user_id")
        }
        registrations = [
            Registration(
                course_id=i + 1,
                user_id=i + j + 1,
                status=1,
            )
            for i in range(300)
            for j in range(500)
            if f"{i + 1}-{i + j + 1}" not in done_registrations
        ]
        if registrations:
            Registration.objects.bulk_create(registrations)
        print("Registrations created:", Registration.objects.count())
        user1 = User.objects.get(username="testuser1")
        user2 = User.objects.get(username="testuser2")
        done_crms = dict.fromkeys(CrmUser.objects.values_list("id", flat=True), True)
        for i in range(200):
            if i + 1 in done_crms:
                continue
            CrmUser.objects.create(
                user_id=i + 1,
                status=1,
                last_follow_up=timezone.now(),
                next_follow_up=timezone.now() + timezone.timedelta(days=i % 10),
                joined_main_group=True,
            )
        CrmUser.objects.filter(id__lte=200).update(supporting_user=user2)
        CrmUser.objects.filter(id__lte=100).update(supporting_user=user1)
        user1.is_staff = True
        user1.set_password("testpass")
        user1.save()
        user2.is_staff = True
        user2.set_password("testpass")
        user2.save()
        print("Users created and updated:", User.objects.count())
        Course.objects.get(course_type=1, number=1).instructors.add(user1)
        Course.objects.get(course_type=1, number=2).managing_users.add(user1)
        Course.objects.get(course_type=1, number=3).supporting_users.add(user1)
        if not Group.objects.filter(name="supporting").exists():
            group_supporting = Group.objects.create(name="supporting")
            permissions_code = [
                "add_registration",
                "change_registration",
                "view_registration",
                "view_course",
                "view_crmuser",
                "view_crmuser",
                "view_user",
                "view_crmlog",
                "add_crmlog",
                "change_crmlog",
            ]
            group_supporting.permissions.set(Permission.objects.filter(codename__in=permissions_code))
            user1.groups.add(group_supporting)
            user2.groups.add(group_supporting)
        registrations = Registration.objects.select_related("user").filter(course_id=3)
        for registration in registrations:
            registration.supporting_user = user1 if registration.user_id % 2 == 0 else user2
            registration.save()
        print("Users updated with roles and permissions.", registrations.count())
