from dalf.admin import DALFModelAdmin, DALFRelatedFieldAjax
from django.contrib import admin
from django.contrib.admin.filters import (
    AllValuesFieldListFilter,
    ChoicesFieldListFilter,
    RelatedFieldListFilter,
    RelatedOnlyFieldListFilter,
    SimpleListFilter,
)
from django.contrib.admin.models import ADDITION, LogEntry
from django.contrib.contenttypes.models import ContentType

from commons.models import DetailedLog


class SimpleDropdownFilter(SimpleListFilter):
    template = "admin/dropdown_filter.html"


class DropdownFilter(AllValuesFieldListFilter):
    template = "admin/dropdown_filter.html"


class ChoiceDropdownFilter(ChoicesFieldListFilter):
    template = "admin/dropdown_filter.html"


class RelatedDropdownFilter(RelatedFieldListFilter):
    template = "admin/dropdown_filter.html"


class RelatedOnlyDropdownFilter(RelatedOnlyFieldListFilter):
    template = "admin/dropdown_filter.html"


class DetailedLogAdminMixin:
    save_on_top = True

    def log_django_admin_action(self, request, object, action_flag, change_message=None):
        LogEntry.objects.log_action(
            user_id=request.user.pk if request.user.is_authenticated else None,
            content_type_id=ContentType.objects.get_for_model(object.__class__).pk,
            object_id=object.pk,
            object_repr=str(object),
            action_flag=action_flag,
            change_message=change_message or "",
        )

    def save_model(self, request, obj, form, change):
        if change:
            old_obj = obj.__class__.objects.get(pk=obj.pk)
            self.custom_old_values = {f.name: getattr(old_obj, f.name) for f in obj._meta.fields}
        else:
            self.custom_old_values = None
        super().save_model(request, obj, form, change)

    def log_addition(self, request, object, message):
        from commons.models import DetailedLog

        self.custom_new_values = {f.name: getattr(object, f.name) for f in object._meta.fields}

        return DetailedLog.objects.create(
            user_id=request.user.pk,
            content_type_id=ContentType.objects.get_for_model(object, for_concrete_model=False).id,
            object_id=object.pk,
            object_repr=str(object)[:200],
            action_flag=ADDITION,
            change_message=message or "",
            old_values={},
            changed_values=self.custom_new_values,
        )

    def log_change(self, request, object, message):
        from django.contrib.admin.models import CHANGE

        from commons.models import DetailedLog

        self.custom_new_values = {f.name: getattr(object, f.name) for f in object._meta.fields}
        self.custom_changed_values = []
        for k in self.custom_new_values:
            if self.custom_old_values[k] != self.custom_new_values[k]:
                self.custom_changed_values.append({k: self.custom_new_values[k]})

        return DetailedLog.objects.create(
            user_id=request.user.pk,
            content_type_id=ContentType.objects.get_for_model(object, for_concrete_model=False).id,
            object_id=object.pk,
            object_repr=str(object)[:200],
            action_flag=CHANGE,
            change_message=message or "",
            old_values=self.custom_old_values,
            changed_values=self.custom_changed_values,
        )

    def log_deletion(self, request, object, object_repr):
        import warnings

        from django.utils.deprecation import RemovedInDjango60Warning

        """
        Log that an object will be deleted. Note that this method must be
        called before the deletion.

        The default implementation creates an admin LogEntry object.
        """
        warnings.warn(
            "ModelAdmin.log_deletion() is deprecated. Use log_deletions() instead.",
            RemovedInDjango60Warning,
            stacklevel=2,
        )
        from django.contrib.admin.models import DELETION

        return DetailedLog.objects.create(
            user_id=request.user.pk,
            content_type_id=ContentType.objects.get_for_model(object, for_concrete_model=False).id,
            object_id=object.pk,
            object_repr=str(object)[:200],
            action_flag=DELETION,
            old_values={},
            changed_values={f.name: getattr(object, f.name) for f in object._meta.fields},
        )

    def log_deletions(self, request, queryset):
        import warnings

        from django.contrib.admin import ModelAdmin

        """
        Log that objects will be deleted. Note that this method must be called
        before the deletion.

        The default implementation creates admin LogEntry objects.
        """
        from django.contrib.admin.models import DELETION
        from django.utils.deprecation import RemovedInDjango60Warning

        # RemovedInDjango60Warning.
        if type(self).log_deletion != ModelAdmin.log_deletion:
            warnings.warn(
                "The usage of log_deletion() is deprecated. Implement log_deletions() instead.",
                RemovedInDjango60Warning,
                stacklevel=2,
            )
            return [self.log_deletion(request, obj, str(obj)) for obj in queryset]

        return [
            DetailedLog.objects.create(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(obj, for_concrete_model=False).id,
                object_id=obj.pk,
                object_repr=str(obj)[:200],
                action_flag=DELETION,
                old_values={},
                changed_values={f.name: getattr(obj, f.name) for f in obj._meta.fields},
            )
            for obj in queryset
        ]


@admin.register(DetailedLog)
class DetailedLogAdmin(DALFModelAdmin):
    list_display = ("action_time", "user", "content_type", "object_repr", "action_flag", "change_message")
    list_filter = ("action_time", ("user", DALFRelatedFieldAjax), "action_flag")
    search_fields = ("object_repr", "change_message")
    autocomplete_fields = ("user",)

    readonly_fields = [
        "action_time",
        "user",
        "content_type",
        "object_id",
        "object_repr",
        "action_flag",
        "change_message",
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
