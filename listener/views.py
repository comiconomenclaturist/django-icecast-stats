from django.db.models import Avg, Sum, Count, Value, CharField
from django.utils import timezone
from psycopg2.extras import DateTimeTZRange
from rest_framework import views, viewsets
from rest_framework.response import Response
from datetime import datetime, timedelta
from dateutil import relativedelta, parser
from .models import *
from .serializers import *


class ListenerCount(views.APIView):
	def get(self, request):
		data = []
		now = datetime.now().replace(minute=0, second=0, microsecond=0, year=2018).astimezone()
		date_ranges = [DateTimeTZRange(now - timedelta(hours=h), now - timedelta(hours=h-1)) for h in reversed(range(0, 24))]

		for d in date_ranges:
			listeners = []

			for stream in Stream.objects.distinct('station'):
				listeners.append({
					'mountpoint': stream.get_station_display(),
					'listeners': Listener.objects.filter(
						stream__station__in=stream.station,
						session__overlap=d).count()
					})

			data.append({
				'hour': d.lower,
				'stream': listeners
				})

		results = ListenerCountSerializer(data, many=True).data
		return Response(results)


class ListenerHours(views.APIView):
	def get(self, request):
		data = []
		now = datetime.now().replace(minute=0, second=0, microsecond=0, year=2018).astimezone()
		date_ranges = [DateTimeTZRange(now - timedelta(hours=h), now - timedelta(hours=h-1)) for h in reversed(range(0, 24))]

		for d in date_ranges:
			listenersHours = []

			for stream in Stream.objects.distinct('station'):
				l_hours = timedelta()

				listeners = Listener.objects.filter(
					stream__station__in=stream.station,
					session__overlap=d)

				for listener in listeners:
					l_hours += min(listener.session.upper, d.upper) - max(listener.session.lower, d.lower)

				listenersHours.append({
					'mountpoint': stream.get_station_display(),
					'listenerHours': l_hours
					})

			data.append({
				'hour': d.lower,
				'stream': listenersHours
				})

		results = ListenerHoursSerializer(data, many=True).data
		return Response(results)


class AggregateView(views.APIView):
	def get(self, request):
		data = []

		start = request.query_params.get('start', None)
		end = request.query_params.get('end', None)
		station = request.query_params.get('station') or 'A'

		if start and end:
			start = parser.parse(start).astimezone()
			start = ListenerAggregate.objects.filter(
				period__endswith__gt=start
				).order_by('period').first().period.lower

			end = parser.parse(end).astimezone()
			end = ListenerAggregate.objects.filter(
				period__startswith__lt=end
				).order_by('-period').first().period.upper
		else:
			# Default view
			end = ListenerAggregate.objects.order_by('-period').first().period.upper.replace(minute=0) + timedelta(hours=1)
			start = end - timedelta(days=1)

		if station == 'A':
			streams = Stream.objects.all().distinct('station')
		else:
			streams = Stream.objects.filter(
				station=station,
				listeneraggregate__period__overlap=DateTimeTZRange(start, end)
				).distinct()

		relative_range = relativedelta.relativedelta(end, start)

		if relative_range.years or relative_range.months > 6:
			delta = relativedelta.relativedelta(months=1)
		elif relative_range.months > 1:
			delta = relativedelta.relativedelta(weeks=1)
		elif relative_range.months or relative_range.days > 14:
			delta = relativedelta.relativedelta(days=1)
		elif relative_range.days > 7:
			delta = relativedelta.relativedelta(hours=12)
		elif relative_range.days > 2:
			delta = relativedelta.relativedelta(hours=6)
		elif relative_range.days > 0 or relative_range.hours > 12:
			delta = relativedelta.relativedelta(hours=1)
		elif relative_range.hours > 6:
			delta = relativedelta.relativedelta(minutes=30)
		else:
			delta = relativedelta.relativedelta(minutes=15)

		date_ranges = []
		first, last = start, end

		while first < last:
			interval = first + delta
			date_ranges.append(DateTimeTZRange(first, interval))
			first = interval

		for d in date_ranges:
			aggregates = []
			
			for stream in streams:
				count = ListenerAggregate.objects.filter(
					period__overlap=d,
					stream=stream).aggregate(Sum('count'))['count__sum'] or 0
				hours = ListenerAggregate.objects.filter(
					period__overlap=d,
					stream=stream).aggregate(Sum('duration'))['duration__sum'] or timedelta()
				hours = hours.total_seconds() / 60 / 60 / 24

				if station == 'A':
					mountpoint = stream.get_station_display()
				else:
					mountpoint = stream.mountpoint.lstrip('/')

				aggregates.append({
					'mountpoint': mountpoint,
					'count': count,
					'hours': hours,
					})

			data.append({
				'period': d.lower,
				'stream': aggregates,
				})
					
		results = AggregateSerializer(data, many=True).data
		return Response(results)


class ListenerQuerySetMixin(object):
	def get_queryset(self):
		station = self.request.query_params.get('station', 'A')
		start = self.request.query_params.get('start', None)
		end = self.request.query_params.get('end', None)

		if start and end:
			start = parser.parse(start).astimezone()
			end = parser.parse(end).astimezone()
		else:
			end = Listener.objects.last().session.upper.replace(minute=0, second=0)
			start = end - timedelta(days=1)

		queryset = Listener.objects.filter(session__overlap=DateTimeTZRange(start, end))

		if station != 'A':
			queryset = queryset.filter(stream__station=station)

		return queryset.values(self.field).annotate(count=Count('*')).order_by('-count')


class CountriesViewSet(ListenerQuerySetMixin, viewsets.ReadOnlyModelViewSet):
	field = 'country'
	serializer_class = CountriesSerializer


class RefererViewSet(ListenerQuerySetMixin, viewsets.ReadOnlyModelViewSet):
	field = 'referer'
	serializer_class = RefererSerializer


class NewListenerAggregateView(viewsets.ReadOnlyModelViewSet):
	# Using a model serializer and passing a values queryset to it. It's still slow though
	# Also the station display name is not shown, and the json format is different (results are not nested under the period)
	# There is also no auto range. See AggregateView class above for the desired results. 
	def get_queryset(self):
		station = self.request.query_params.get('station', 'A')
		start = self.request.query_params.get('start', None)
		end = self.request.query_params.get('end', None)

		if start and end:
			start = parser.parse(start).astimezone()
			end = parser.parse(end).astimezone()
		else:
			end = Listener.objects.last().session.upper.replace(minute=0, second=0)
			start = end - timedelta(days=1)

		date_ranges = [DateTimeTZRange(end - timedelta(hours=h), end - timedelta(hours=h-1)) for h in reversed(range(0, 24))]

		qs = Listener.objects.none()
		for date_range in date_ranges:
			qs = qs.union(
				Listener.objects.filter(
					session__overlap=date_range)
				.values('stream__station')
				.annotate(
					count=Count('stream__station'),
					hour=Value(date_range.lower, output_field=CharField()))
				.order_by('-count'))

		return qs
	
	serializer_class = NewListenerSerializer


