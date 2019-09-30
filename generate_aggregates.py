import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stats.settings")
import django
django.setup()

from django.core.exceptions import ObjectDoesNotExist
from listener.models import Listener, ListenerAggregate, Stream
from psycopg2.extras import DateTimeTZRange
from datetime import timedelta

streams = Stream.objects.all()

first_aggregate = ListenerAggregate.objects.order_by('-period').first().period.lower

first_listener = Listener.objects.all().order_by('session').first().session.lower
first_listener = first_listener - timedelta(
	minutes=first_listener.minute % 15,
	seconds=first_listener.second,
	microseconds=first_listener.microsecond)

last_listener = Listener.objects.all().order_by('-session').first().session.upper
last_listener = last_listener - timedelta(
	minutes=last_listener.minute % 15,
	seconds=last_listener.second,
	microseconds=last_listener.microsecond) + timedelta(minutes=15)

start = max(first_aggregate, first_listener)

while start < last_listener:
	end = start + timedelta(minutes=15)
	period = DateTimeTZRange(lower=start, upper=end)

	for stream in streams:
		count = Listener.objects.filter(stream=stream, session__overlap=period).count()

		if count:
			duration = timedelta()
			for listener in Listener.objects.filter(stream=stream, session__overlap=period):
				duration += min(listener.session.upper, period.upper) - max(listener.session.lower, period.lower)
			try:
				la = ListenerAggregate.objects.get(period=period, stream=stream)
			except ObjectDoesNotExist:
				la = ListenerAggregate(period=period, stream=stream)
			la.count = count
			la.duration = duration
			la.save()
			
	start = end
