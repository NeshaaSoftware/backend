from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

from financials.models import FinancialAccount


class Command(BaseCommand):
    help = "initialize structure of neshaa"

    def handle(self, *args, **options):
        FinancialAccount.objects.get_or_create(name="پی‌پینگ")
        reg, _ = Group.objects.get_or_create(name=settings.REGISTRATION_GROUP_NAME)
        sup, _ = Group.objects.get_or_create(name=settings.SUPPORT_GROUP_NAME)
        manag, _ = Group.objects.get_or_create(name=settings.MANAGING_GROUP_NAME)
        reg_permission_code = [
            "view_registration",
            "change_registration",
            "change_registration",
            "add_registration",
            "view_course",
            "add_coursetransaction",
            "change_coursetransaction",
            "view_coursetransaction",
            "add_user",
        ]
        reg_permissions = [Permission.objects.get(codename=permission) for permission in reg_permission_code]
        sup_permission_code = [
            "view_crmuserlabel",
            "view_crmlog",
            "change_crmlog",
            "add_crmlog",
            "view_user",
            "view_registration",
            "change_crmuser",
            "view_crmuser",
        ]
        sup_permissions = [Permission.objects.get(codename=permission) for permission in sup_permission_code]
        manag_permission_code = [
            "view_crmuserlabel",
            "view_crmuser",
            "view_crmlog",
            "change_crmuser",
            "add_crmlog",
            "view_user",
            "view_registration",
        ]
        manage_permissions = [Permission.objects.get(codename=permission) for permission in manag_permission_code]
        for permission in reg_permissions:
            reg.permissions.add(permission)
        for permission in sup_permissions:
            sup.permissions.add(permission)
        for permission in manage_permissions:
            manag.permissions.add(permission)
