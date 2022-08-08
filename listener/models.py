from django.db import models
from django import forms
from django.core.validators import MinValueValidator
from django_countries.fields import CountryField
from django.contrib.postgres.fields import DateTimeRangeField
from django.contrib.postgres.indexes import GistIndex
from datetime import timedelta
from useragent.models import UserAgent


class IngestParameters(models.Model):
    minimum_duration = models.PositiveSmallIntegerField(
        default=3,
        validators=[MinValueValidator(1)],
        help_text="Minimum listener duration (in seconds) required to import connection to database",
    )
    session_threshold = models.PositiveSmallIntegerField(
        default=120,
        help_text="Maximum gap between connections (in seconds) to concatenate connections to sessions",
    )

    class Meta:
        verbose_name = "Ingest Parameters"
        verbose_name_plural = "Ingest Parameters"

    def __str__(self):
        h, m = divmod(self.session_threshold, 60)
        return "Minimum duration: %d secs, Session threshold: %02d:%02d" % (
            self.minimum_duration,
            h,
            m,
        )


class Station(models.Model):
    name = models.CharField(max_length=127, unique=True)

    class Meta:
        ordering = ("-name",)

    def __str__(self):
        return self.name


class Stream(models.Model):
    mountpoint = models.CharField(max_length=255, unique=True)
    bitrate = models.PositiveSmallIntegerField()
    station = models.ForeignKey(Station, on_delete=models.PROTECT)

    class Meta:
        ordering = ("-station__name", "-bitrate", "mountpoint")

    def __str__(self):
        return "%s – %skbps" % (self.mountpoint, self.bitrate)


class Listener(models.Model):
    ip_address = models.GenericIPAddressField(verbose_name="IP address")
    stream = models.ForeignKey(Stream, on_delete=models.PROTECT)
    session = DateTimeRangeField()
    duration = models.DurationField()
    referer = models.CharField(max_length=255)
    user_agent = models.ForeignKey(UserAgent, on_delete=models.SET_NULL, null=True)
    country = CountryField(null=True)
    city = models.CharField(max_length=255, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)

    class Meta:
        unique_together = ("ip_address", "stream", "session", "user_agent")
        ordering = ("-session",)
        indexes = [
            GistIndex(
                fields=[
                    "session",
                ]
            ),
        ]

    @property
    def connected_at(self):
        return self.session.lower

    @property
    def disconnected_at(self):
        return self.session.upper

    def __str__(self):
        return self.ip_address


class Region(models.Model):
    name = models.CharField(max_length=127)

    def __str__(self):
        return self.name


class Country(models.Model):
    country = CountryField(null=True)
    region = models.ForeignKey(
        Region, on_delete=models.CASCADE, related_name="countries"
    )

    class Meta:
        verbose_name_plural = "Countries"

    def __str__(self):
        return self.country.code
