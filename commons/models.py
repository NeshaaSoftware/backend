import logging
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

logger = logging.getLogger("audit")


class TimeStampedModel(models.Model):
    """Abstract base class that adds created_at and updated_at fields to models."""

    _created_at = models.DateTimeField(auto_now_add=True)
    _updated_at = models.DateTimeField(auto_now=True)

    @property
    def created_at(self):
        return self._created_at

    @property
    def updated_at(self):
        return self._updated_at

    class Meta:
        abstract = True


class AuditLog(models.Model):
    """Model to track all changes to other models"""

    ACTION_CHOICES = [
        ("CREATE", "Create"),
        ("UPDATE", "Update"),
        ("DELETE", "Delete"),
        ("VIEW", "View"),
    ]

    # Generic foreign key to link to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    # Action details
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    # Change details
    old_values = models.JSONField(null=True, blank=True)
    new_values = models.JSONField(null=True, blank=True)
    changed_fields = models.JSONField(null=True, blank=True)

    # Additional context
    notes = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["timestamp"]),
            models.Index(fields=["user"]),
            models.Index(fields=["action"]),
        ]

    def __str__(self):
        return (
            f"{self.get_action_display()} on {self.content_type.model} by {self.user or 'System'} at {self.timestamp}"
        )


class AuditMixin:
    """Mixin to add audit logging to models"""

    def save(self, *args, **kwargs):
        # Check if this is an update or create
        is_update = self.pk is not None

        # Get old values for comparison if updating
        old_values = {}
        if is_update:
            try:
                old_instance = self.__class__.objects.get(pk=self.pk)
                old_values = self._get_model_fields_dict(old_instance)
            except self.__class__.DoesNotExist:
                old_values = {}

        # Call the original save method
        super().save(*args, **kwargs)

        # Get new values
        new_values = self._get_model_fields_dict(self)

        # Determine action and changed fields
        if is_update:
            action = "UPDATE"
            changed_fields = []
            for field, new_value in new_values.items():
                if field in old_values and old_values[field] != new_value:
                    changed_fields.append(field)
        else:
            action = "CREATE"
            changed_fields = list(new_values.keys())
            old_values = None

        # Create audit log entry
        self._create_audit_log(action, old_values, new_values, changed_fields)

    def delete(self, *args, **kwargs):
        # Get values before deletion
        old_values = self._get_model_fields_dict(self)

        # Call the original delete method
        result = super().delete(*args, **kwargs)

        # Create audit log entry
        self._create_audit_log("DELETE", old_values, None, list(old_values.keys()))

        return result

    def _get_model_fields_dict(self, instance):
        """Get a dictionary of field names and values for the model instance"""
        fields_dict = {}
        for field in instance._meta.fields:
            try:
                value = getattr(instance, field.name)
                # Convert complex objects to string representation
                if hasattr(value, "pk"):
                    fields_dict[field.name] = str(value)
                else:
                    fields_dict[field.name] = value
            except AttributeError:
                fields_dict[field.name] = None
        return fields_dict

    def _create_audit_log(self, action, old_values, new_values, changed_fields):
        """Create an audit log entry"""
        try:
            from django.contrib.contenttypes.models import ContentType
            from .middleware import get_current_user, get_current_ip, get_current_user_agent

            AuditLog.objects.create(
                content_type=ContentType.objects.get_for_model(self),
                object_id=self.pk,
                action=action,
                user=get_current_user(),
                ip_address=get_current_ip(),
                user_agent=get_current_user_agent(),
                old_values=old_values,
                new_values=new_values,
                changed_fields=changed_fields,
            )

            # Log to file as well
            user_info = get_current_user() or "System"
            logger.info(
                f"Audit: {action} on {self.__class__.__name__} (ID: {self.pk}) by {user_info} - Changed fields: {changed_fields}"
            )

        except Exception as e:
            # Don't fail the operation if audit logging fails
            logger.error(f"Failed to create audit log: {str(e)}")


class LoggedTimeStampedModel(TimeStampedModel, AuditMixin):
    """Abstract base class that combines timestamp and audit logging functionality"""

    class Meta:
        abstract = True
