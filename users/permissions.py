from functools import wraps

from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect


class ManagingGroupPermissionMixin:
    def has_managing_group_permission(self, request):
        user = request.user
        if user.is_superuser or user.groups.filter(name=settings.MANAGING_GROUP_NAME).exists():
            return True
        return False


def requires_managing_group_permission(view_func):
    @wraps(view_func)
    def _wrapped_view(self, request, *args, **kwargs):
        try:
            user = request.user
            if not user.groups.filter(name=settings.MANAGING_GROUP_NAME).exists() and not user.is_superuser:
                messages.error(request, "شما اجازه دسترسی به این عملیات را ندارید.")
                return redirect(".")
            return view_func(self, request, *args, **kwargs)

        except Exception as e:
            messages.error(request, f"خطا در اجرا: {e!s}")
            import logging

            logger = logging.getLogger(__name__)
            logger.exception("Error in requires_managing_group_permission")
            return redirect(".")

    return _wrapped_view
