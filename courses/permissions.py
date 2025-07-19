from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


class CoursePermissionMixin:
    def has_course_manage_permission(self, request, course):
        user = request.user
        if user.is_superuser:
            return True

        if course and course.managing_users.filter(pk=user.pk).exists():
            return True

        return False


def requires_course_managing_permission(view_func):
    @wraps(view_func)
    def _wrapped_view(self, request, course_id, *args, **kwargs):
        try:
            from .models import Course

            course = Course.objects.get(id=course_id)
            user = request.user
            if not user.is_superuser and not course.managing_users.filter(pk=user.pk).exists():
                messages.error(request, "شما اجازه دسترسی به این عملیات را ندارید.")
                return redirect(".")
            return view_func(self, request, course_id, *args, **kwargs)

        except Exception as e:
            from .models import Course

            if isinstance(e, Course.DoesNotExist):
                messages.error(request, "دوره مورد نظر یافت نشد.")
                return redirect("admin:courses_course_changelist")
            else:
                messages.error(request, f"خطا در بررسی دسترسی: {e!s}")
                return redirect("admin:courses_course_changelist")

    return _wrapped_view
