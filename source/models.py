from django.db import models
from listener.models import Stream


class Source(models.Model):
    stream = models.ForeignKey(
        Stream,
        related_name="connections",
        on_delete=models.PROTECT,
    )
    timestamp = models.DateTimeField()
    connection = models.BooleanField()

    class Meta:
        ordering = ("-timestamp", "-stream")

    def __str__(self):
        return self.stream.mountpoint
