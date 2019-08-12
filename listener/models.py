from django.db import models
from django import forms
from django.core.validators import MinValueValidator
from django_countries.fields import CountryField
from django.contrib.postgres.fields import DateTimeRangeField
from datetime import timedelta
from useragent.models import UserAgent


class IngestParameters(models.Model):
	minimum_duration = models.PositiveSmallIntegerField(
		default=3,
		validators=[MinValueValidator(1)],
		help_text=u'Minimum listener duration (in seconds) required to import connection to database')
	session_threshold = models.PositiveSmallIntegerField(
		default=120,
		help_text=u'Maximum gap between connections (in seconds) to concatenate connections to sessions')

	class Meta:
		verbose_name = 'Ingest Parameters'
		verbose_name_plural = 'Ingest Parameters'

	def __str__(self):
		h, m = divmod(self.session_threshold, 60)
		return 'Minimum duration: %d secs, Session threshold: %02d:%02d' % (self.minimum_duration, h, m)
		

class Stream(models.Model):
	STATION_CHOICES = [
		('R', 'Resonance'),
		('E', 'Extra'),
	]
	
	mountpoint 	= models.CharField(max_length=255, unique=True)
	bitrate 	= models.PositiveSmallIntegerField()
	station		= models.CharField(choices=STATION_CHOICES, max_length=1)

	class Meta:
		ordering = ('-station', '-bitrate', 'mountpoint')

	def __str__(self):
		return '%s – %skbps' % (self.mountpoint, self.bitrate)


class Listener(models.Model):
	ip_address 		= models.GenericIPAddressField(verbose_name='IP address')
	stream 			= models.ForeignKey(Stream, on_delete='PROTECT')
	session 		= DateTimeRangeField()
	duration 		= models.DurationField()
	referer 		= models.CharField(max_length=255)
	user_agent 		= models.ForeignKey(UserAgent, on_delete=models.SET_NULL, null=True)
	country 		= CountryField(null=True)
	city 			= models.CharField(max_length=255, null=True)
	latitude		= models.DecimalField(max_digits=9, decimal_places=6, null=True)
	longitude		= models.DecimalField(max_digits=9, decimal_places=6, null=True)

	class Meta:
		unique_together = ('ip_address', 'stream', 'session', 'user_agent')
		ordering = ('session',)

	@property
	def connected_at(self):
		return self.session.lower

	@property
	def disconnected_at(self):
		return self.session.upper

	def __str__(self):
		return self.ip_address


class ListenerAggregate(models.Model):
	period		= DateTimeRangeField()
	stream		= models.ForeignKey(Stream, on_delete='PROTECT')
	count 		= models.PositiveIntegerField()
	duration 	= models.DurationField()

	@property
	def hours(self):
		m, s = divmod(self.duration.total_seconds(), 60)
		h, m = divmod(m, 60)
		return round(float(h + (m/60)), 2)

	class Meta:
		ordering = ['-period']

	def full_clean(self, *args, **kwargs):
		super(ListenerAggregate, self).full_clean(*args, **kwargs)
		la = ListenerAggregate.objects.filter(
			period__overlap=self.period,
			stream=self.stream).exclude(pk=self.pk).first()
		if la:
			raise forms.ValidationError('Period overlaps with "%s"' % la)	

	def save(self, *args, **kwargs):
		self.full_clean()
		super(ListenerAggregate, self).save(*args, **kwargs)
	
	def __str__(self):
		return str(self.period.lower) + ' – ' + str(self.period.upper) + ' – ' + str(self.stream)

	