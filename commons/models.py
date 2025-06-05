import json
from datetime import date, datetime
from json import JSONDecoder, JSONEncoder

from django.contrib.admin.models import LogEntry
from django.db import models
from django_jalali.db import models as jmodels
from jdatetime import date as jdate
from jdatetime import datetime as jdatetime


class TimeStampedModel(models.Model):
    """Abstract base class that adds created_at and updated_at fields to models."""

    _created_at = jmodels.jDateTimeField(auto_now_add=True)
    _updated_at = jmodels.jDateTimeField(auto_now=True)

    class Meta:
        abstract = True

    @property
    def created_at(self):
        return self._created_at

    @property
    def updated_at(self):
        return self._updated_at


class LogDecoder(json.JSONDecoder):
    def __init__(self, *args, **kargs):
        JSONDecoder.__init__(self, object_hook=self.dict_to_object, *args, **kargs)  # noqa: B026

    def dict_to_object(self, d):
        if "__type__" not in d:
            return d

        type = d.pop("__type__")
        if type == "datetime":
            date_str = d.pop("date")
            try:
                return datetime.fromisoformat(date_str)
            except ValueError:
                return jdatetime.fromisoformat(date_str)
        elif type == "date":
            date_str = d.pop("date")
            try:
                return date.fromisoformat(date_str)
            except ValueError:
                return jdate.fromisoformat(date_str)
        elif type == "model":
            from django.apps import apps

            model = apps.get_model(d["model"])
            return model(pk=d["pk"])
        d["__type__"] = type
        return d


class LogEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime) or isinstance(obj, jdatetime):
            return {
                "__type__": "datetime",
                "date": obj.isoformat(),
            }
        elif isinstance(obj, date) or isinstance(obj, jdate):
            return {
                "__type__": "date",
                "date": obj.isoformat(),
            }
        elif isinstance(obj, models.Model):
            return {
                "__type__": "model",
                "model": obj._meta.label,
                "pk": obj.pk,
            }
        else:
            return str(obj)


class DetailedLog(LogEntry):
    old_values = models.JSONField(encoder=LogEncoder, decoder=LogDecoder)
    changed_values = models.JSONField(encoder=LogEncoder, decoder=LogDecoder)
