from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import CourseTransaction


@receiver(post_save, sender=CourseTransaction)
def course_transaction_post_save(sender, instance, **kwargs):
    if not instance.pk:
        return
    if instance.registration:
        instance.registration.save()

@receiver(post_delete, sender=CourseTransaction)
def course_transaction_post_delete(sender, instance, **kwargs):
    if instance.registration:
        instance.registration.save()