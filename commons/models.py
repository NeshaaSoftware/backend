from datetime import date, datetime
from json import JSONDecoder, JSONEncoder

from django.contrib.admin.models import LogEntry
from django.db import models
from django_jalali.db import models as jmodels
from jdatetime import date as jdate
from jdatetime import datetime as jdatetime


class TimeStampedModel(models.Model):
    _created_at = jmodels.jDateTimeField(auto_now_add=True)
    _updated_at = jmodels.jDateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-_created_at"]

    @property
    def created_at(self):
        return self._created_at

    @property
    def updated_at(self):
        return self._updated_at


class LogDecoder(JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, object_hook=self.dict_to_object)

    def dict_to_object(self, d):
        if "__type__" not in d:
            return d

        obj_type = d.pop("__type__")

        if obj_type == "datetime":
            date_str = d.pop("date")
            try:
                return datetime.fromisoformat(date_str)
            except ValueError:
                return jdatetime.fromisoformat(date_str)

        elif obj_type == "date":
            date_str = d.pop("date")
            try:
                return date.fromisoformat(date_str)
            except ValueError:
                return jdate.fromisoformat(date_str)

        elif obj_type == "model":
            from django.apps import apps

            model = apps.get_model(d["model"])
            return model(pk=d["pk"])

        d["__type__"] = obj_type
        return d


class LogEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime | jdatetime):
            return {
                "__type__": "datetime",
                "date": o.isoformat(),
            }
        elif isinstance(o, date | jdate):
            return {
                "__type__": "date",
                "date": o.isoformat(),
            }
        elif isinstance(o, models.Model):
            return {
                "__type__": "model",
                "model": o._meta.label,
                "pk": o.pk,
            }
        else:
            return str(o)


class DetailedLog(LogEntry):
    old_values = models.JSONField(encoder=LogEncoder, decoder=LogDecoder, help_text="Original values before change")
    changed_values = models.JSONField(encoder=LogEncoder, decoder=LogDecoder, help_text="New values after change")

    class Meta:
        verbose_name = "Detailed Log Entry"
        verbose_name_plural = "Detailed Log Entries"
