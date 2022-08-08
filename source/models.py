from django.db import models
from django.contrib.postgres.fields import DateTimeRangeField
from listener.models import Stream


class Disconnection(models.Model):
    stream = models.ForeignKey(Stream, on_delete=models.PROTECT)
    period = DateTimeRangeField()

    class Meta:
        ordering = ("-period", "-stream")

    def __str__(self):
        return self.stream.mountpoint

    @property
    def disconnected_at(self):
        return self.period.lower.astimezone()

    @property
    def connected_at(self):
        return self.period.upper.astimezone()
