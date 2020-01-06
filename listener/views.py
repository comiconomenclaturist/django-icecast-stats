from django.db.models import Sum, Count, Value, DateTimeField, ExpressionWrapper, F, Func, DurationField, FloatField, CharField
from django.db.models.functions import Least, Greatest, Extract, Cast
from django.contrib.postgres.fields.ranges import RangeStartsWith, RangeEndsWith
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
						stream__station__in = stream.station,
						session__overlap = d).count()
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
					stream__station__in = stream.station,
					session__overlap = d)

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


class GetParamsMixin(object):
	@property
	def period(self):
		start = self.request.query_params.get('start')
		end = self.request.query_params.get('end')

		if start and end:
			start = parser.parse(start).astimezone()
			end = parser.parse(end).astimezone()
		else:
			end = Listener.objects.last().session.upper.astimezone().replace(minute=0, second=0) + timedelta(hours=1)
			start = end - timedelta(days=1)

		return DateTimeTZRange(start, end)

	@property
	def station(self):
		return self.request.query_params.get('station') or 'A'

	@property
	def region(self):
		if self.request.query_params.get('region'):
			return Region.objects.get(id=self.request.query_params.get('region'))
		return None


class ListenerQuerySetMixin(GetParamsMixin):
	def get_queryset(self):
		queryset = Listener.objects.filter(session__overlap=self.period)

		if self.station != 'A':
			queryset = queryset.filter(stream__station=self.station)

		if self.region:
			queryset = queryset.filter(country__in=self.region.countries.values('country'))

		return queryset.values(self.field).annotate(count=Count('*')).order_by('-count')


class DateRangesMixin(GetParamsMixin):
	@property
	def date_ranges(self):
		rd = relativedelta.relativedelta(self.period.upper, self.period.lower)

		if rd.years > 1:
			delta = relativedelta.relativedelta(years=1)
		elif rd.years or rd.months > 6:
			delta = relativedelta.relativedelta(months=1)
		elif rd.months > 1:
			delta = relativedelta.relativedelta(weeks=1)
		elif rd.months or rd.days >= 7:
			delta = relativedelta.relativedelta(days=1)
		elif rd.days > 1:
			delta = relativedelta.relativedelta(hours=2)
		elif rd.days or rd.hours > 12:
			delta = relativedelta.relativedelta(hours=1)
		elif rd.hours > 6:
			delta = relativedelta.relativedelta(minutes=30)
		else:
			delta = relativedelta.relativedelta(minutes=15)

		date_ranges = []
		start, end = self.period.lower, self.period.upper

		while start < end:
			interval = start + delta
			date_ranges.append(DateTimeTZRange(start, interval))
			start = interval

		return date_ranges


class CountriesViewSet(ListenerQuerySetMixin, viewsets.ReadOnlyModelViewSet):
	def list(self, request, *args, **kwargs):
		response = super(CountriesViewSet, self).list(request, args, kwargs)
		response.data['total'] = self.get_queryset().aggregate(Sum('count')).get('count__sum')
		response.data['distinct'] = self.get_queryset().values('country').distinct().count()
		return response

	field = 'country'
	serializer_class = CountriesSerializer


class RefererViewSet(GetParamsMixin, viewsets.ReadOnlyModelViewSet):
	def get_queryset(self):
		qs = Listener.objects.filter(session__overlap=self.period)

		if self.station != 'A':
			qs = qs.filter(stream__station=self.station)

		if self.region:
			qs = qs.filter(country__in=self.region.countries.values('country'))

		self.direct = qs.filter(referer='').count()

		qs = qs.filter(referer__gt='').annotate(
			domain = Func(
				F('referer'),
				Value('https?://(.+?)(?:\:\d+)?(?:\/.*)?'),
				Value('\\1'),
				function = 'regexp_replace'),
			)
		qs = qs.order_by('domain').values('domain').annotate(count=Count('*')).order_by('-count')

		return qs

	def list(self, request, *args, **kwargs):
		response = super(RefererViewSet, self).list(request, args, kwargs)
		response.data['total'] = self.get_queryset().aggregate(Sum('count')).get('count__sum')
		response.data['direct'] = self.direct
		return response

	field = 'referer'
	serializer_class = RefererSerializer


class CountViewSet(DateRangesMixin, viewsets.ReadOnlyModelViewSet):
	def get_queryset(self):
		qs = Listener.objects.none()

		if self.station == 'A':
			streams = 'stream__station__name'
			stream_order = '-stream'
			listeners = Listener.objects.all()
		else:
			streams = 'stream__mountpoint'
			stream_order = 'stream'
			listeners = Listener.objects.filter(stream__station=self.station)

		if self.region:
			listeners = listeners.filter(country__in=self.region.countries.values('country'))

		for date_range in self.date_ranges:
			qs = qs.union(
				listeners.filter(
					session__overlap = date_range
					)
				.values(streams)
				.order_by(streams)
				.annotate(
					period = Value(date_range.lower, DateTimeField()),
					count = Count(streams),
					stream = Cast(streams, CharField()),
					)
				)

		if qs:
			qs = qs.order_by('period', stream_order,)

		return qs

	def list(self, request, *args, **kwargs):
		listeners = Listener.objects.filter(session__overlap=self.period)
		
		if self.station == 'A':
			streams = 'stream__station__name'
			stream_order = '-stream'
		else:
			streams = 'stream__mountpoint'
			stream_order = 'stream'
			listeners = listeners.filter(stream__station=self.station)

		if self.region:
			listeners = listeners.filter(country__in=self.region.countries.values('country'))

		response = {
			'results': CountSerializer(self.get_queryset(), many=True).data
		}
		response.update({
			'period': {
				'start': self.period.lower,
				'end': self.period.upper,
				},
			'totals': listeners.order_by(
				stream_order).values(
				streams).annotate(
				count = Count(streams),
				stream = Cast(streams, CharField())).values('stream', 'count')
				})
		return Response(response)


class Count2ViewSet(DateRangesMixin, views.APIView):
	def get(self, request):
		qs = Listener.objects.none()

		if self.station == 'A':
			streams = 'stream__station'
			stream_order = '-stream'
			listeners = Listener.objects.all()
		else:
			streams = 'stream__mountpoint'
			stream_order = 'stream'
			listeners = Listener.objects.filter(stream__station=self.station)

		for date_range in self.date_ranges:
			qs = qs.union(
				listeners.filter(
					session__overlap = date_range
					)
				.values(streams)
				.order_by(streams)
				.annotate(
					period = Value(date_range.lower, DateTimeField()),
					count = Count(streams),
					stream = Cast(streams, CharField()),
					)
				)

		qs = qs.order_by('period', stream_order,)

		totals = listeners.filter(
			session__overlap = self.period
			).order_by(streams).values(streams).annotate(stream=Cast(streams, CharField()), count=Count(streams)).values('stream', 'count').order_by(stream_order)
		
		results = {}

		for period in self.date_ranges:
			p = period.lower.astimezone().isoformat()
			results[p] = []

			for total in totals:
				results[p].append({
					'stream': total['stream'],
					'count': 0,
					})

		queryset = {'totals': totals, 'results': results}

		for item in qs:
			for i, v in enumerate(queryset['results'][item['period'].astimezone().isoformat()]):
				if v['stream'] == item['stream']:
					queryset['results'][item['period'].astimezone().isoformat()][i]['count'] = item['count']

		return Response(queryset)


class HoursViewSet(DateRangesMixin, viewsets.ReadOnlyModelViewSet):
	def get_queryset(self):
		qs = Listener.objects.none()

		if self.station == 'A':
			streams = 'stream__station__name'
			stream_order = '-stream'
			listeners = Listener.objects.all()
		else:
			streams = 'stream__mountpoint'
			stream_order = 'stream'
			listeners = Listener.objects.filter(stream__station=self.station)

		if self.region:
			listeners = listeners.filter(country__in=self.region.countries.values('country'))

		for date_range in self.date_ranges:
			qs = qs.union(
				listeners.filter(
					session__overlap = date_range
					)
				.annotate(period=Value(date_range, DateTimeRangeField()),)
				.annotate(
					start = Greatest(RangeStartsWith('period'), RangeStartsWith('session')),
					end = Least(RangeEndsWith('period'), RangeEndsWith('session'))
					)
				.annotate(length=ExpressionWrapper(F('end') - F('start'), output_field=DurationField()))
				.values(streams)
				.order_by(streams)
				.annotate(
					hours = ExpressionWrapper(Extract(Sum('length'), 'epoch') / 3600, output_field=FloatField()),
					period = Value(date_range.lower, DateTimeField()),
					stream = Cast(streams, CharField()),
					)
				)

		return qs.order_by('period', stream_order,)

	serializer_class = HoursSerializer

