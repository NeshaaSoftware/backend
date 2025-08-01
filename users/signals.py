from django.contrib.admin.models import ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from commons.models import DetailedLog
from commons.utils import arabic_to_persian_characters, get_jdatetime_now_with_timezone

from .models import CrmLog, User


@receiver(pre_save, sender=User)
def user_pre_save_fix_name(sender, instance, **kwargs):
    instance.first_name = arabic_to_persian_characters(instance.first_name) or ""
    instance.last_name = arabic_to_persian_characters(instance.last_name) or ""

@receiver(pre_save, sender=CrmLog)
def crm_log_pre_save(sender, instance, **kwargs):
    if instance.date is None:
        instance.date = get_jdatetime_now_with_timezone()
    if not instance.pk:
        return
    old_instance = CrmLog.objects.get(pk=instance.pk)
    changing_user = instance.user
    if instance.user.id != old_instance.user.id:
        instance.user = old_instance.user
    old_values = {}
    changes = {}
    for field in ["description", "action", "user", "date"]:
        old_value = getattr(old_instance, field)
        new_value = getattr(instance, field)
        old_values[field] = old_value
        if old_value != new_value:
            changes[field] = new_value
    if changes:
        DetailedLog.objects.create(
            user=changing_user,
            content_type=ContentType.objects.get_for_model(CrmLog),
            object_id=instance.pk,
            object_repr=str(instance)[:200],
            action_flag=CHANGE,
            change_message="",
            old_values=old_values,
            changed_values=changes,
        )


@receiver(post_save, sender=CrmLog)
def crm_log_post_save(sender, instance, created, **kwargs):
    if created:
        changed_values = {field: getattr(instance, field) for field in ["description", "action", "user", "date"]}
        DetailedLog.objects.create(
            user=instance.user,
            content_type=ContentType.objects.get_for_model(CrmLog),
            object_id=instance.pk,
            object_repr=str(instance)[:200],
            action_flag=ADDITION,
            change_message="",
            old_values={},
            changed_values=changed_values,
        )
