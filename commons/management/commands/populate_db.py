from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = "Populate the database with initial or test data."

    def handle(self, *args, **options):
        from django.contrib.auth.models import Group, Permission

        from courses.models import Course, CourseSession, Registration
        from users.models import User

        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                username="admin", phone_number="+989120000000", email="admin@example.com", password="adminpass"
            )
        done_users = dict.fromkeys(User.objects.values_list("username", flat=True), True)
        users = [
            User(
                username=f"testuser{i}",
                phone_number="+9891200000" + str(i + 1),
                password="testpass",
                first_name=f"Test{i}",
                last_name="User",
            )
            for i in range(10000)
            if f"testuser{i}" not in done_users
        ]
        if users:
            User.objects.bulk_create(users)
        done_courses = dict.fromkeys(Course.objects.values_list("number", flat=True), True)
        courses = [Course(course_type=1, number=i) for i in range(300) if i not in done_courses]
        if courses:
            Course.objects.bulk_create(courses)
        done_sessions = dict.fromkeys(CourseSession.objects.values_list("session_name", flat=True), True)
        sessions = [
            CourseSession(
                course_id=i // 1000 + 1,
                session_name=f"Session {i + 1}",
                start_date=timezone.now(),
                end_date=timezone.now() + timezone.timedelta(days=i),
                location="Location " + str(i + 1),
            )
            for i in range(50000)
            if f"Session {i + 1}" not in done_sessions
        ]
        if sessions:
            CourseSession.objects.bulk_create(sessions)
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
        user1 = User.objects.get(username="testuser1")
        user2 = User.objects.get(username="testuser2")
        user1.is_staff = True
        user1.set_password("testpass")
        user1.save()
        user2.is_staff = True
        user2.set_password("testpass")
        user2.save()
        Course.objects.get(course_type=1, number=1).instructors.add(user1)
        Course.objects.get(course_type=1, number=2).managing_users.add(user1)
        Course.objects.get(course_type=1, number=3).assisting_users.add(user1)
        if not Group.objects.filter(name="assisting").exists():
            group_assist = Group.objects.create(name="assisting")
            permissions_code = ["add_registration", "change_registration", "view_registration", "view_course"]
            group_assist.permissions.set(Permission.objects.filter(codename__in=permissions_code))
            user1.groups.add(group_assist)
            user2.groups.add(group_assist)
        registrations = Registration.objects.filter(course_id=3)
        for registration in registrations:
            registration.assistant = user1 if registration.user_id % 2 == 0 else user2
            registration.save()
