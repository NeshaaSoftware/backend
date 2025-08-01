from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import Registration


@receiver(pre_save, sender=Registration)
def registration_pre_save(sender, instance, **kwargs):
    if not instance.pk:
        return
    instance.update_paid_amount(commit=False)
