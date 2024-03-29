from django.db.models import *
from django.db.models.functions import Least, Greatest, Extract, Cast, Round
from django.contrib.postgres.fields.ranges import RangeStartsWith, RangeEndsWith
from django.contrib.postgres.fields import DateTimeRangeField as DTRangeField
from psycopg2.extras import DateTimeTZRange
from rest_framework import viewsets
from rest_framework.response import Response
from datetime import datetime, timedelta
from dateutil import relativedelta
from dateutil.rrule import MINUTELY, HOURLY, DAILY, WEEKLY, MONTHLY, YEARLY
from dateutil.rrule import rrule, rruleset, MO, TU, WE, TH, FR, SA, SU
from .models import Listener
from .serializers import *
from listener.forms import *


class GetParamsMixin(object):
    @property
    def form(self):
        form = ListenerForm(self.request.GET)

        if form.is_valid():
            if form.cleaned_data["period"]:
                self.period = form.cleaned_data["period"]
            else:
                end = datetime.now().astimezone()
                start = end - timedelta(days=1)
                self.period = DateTimeTZRange(start, end)

            self.listeners = Listener.objects.filter(session__overlap=self.period)
            self.streams = "stream__station__name"
            self.stream_order = "-stream"

            if form.cleaned_data["station"]:
                self.listeners = self.listeners.filter(
                    stream__station=form.cleaned_data["station"]
                )
                self.streams = "stream__mountpoint"
                self.stream_order = "stream"

            if form.cleaned_data["region"]:
                countries = form.cleaned_data["region"].countries.values("country")
                self.listeners = self.listeners.filter(country__in=countries)

            if self.request.GET.getlist("referrer"):
                q = Q()
                for referrer in self.request.GET.getlist("referrer"):
                    q = q | Q(referer__contains=referrer)

                self.listeners = self.listeners.filter(q)

        return form


class DateRangesMixin(GetParamsMixin):
    @property
    def date_ranges(self):
        date_ranges = []
        weekdays = (
            MO,
            TU,
            WE,
            TH,
            FR,
            SA,
            SU,
        )

        if self.form.cleaned_data["dow"] and self.form.cleaned_data["slot"]:
            dow = int(self.form.cleaned_data["dow"])
            slot = self.form.cleaned_data["slot"]

            start = self.period.lower.replace(
                hour=slot.start.hour, minute=slot.start.minute, tzinfo=None
            )

            if slot.start > slot.stop:
                end = self.period.upper.replace(tzinfo=None)
                # Assuming that the slot end time is the following day
                next_day = start + timedelta(days=1)
                delta = (
                    next_day.replace(hour=slot.stop.hour, minute=slot.stop.minute)
                    - start
                )
            else:
                end = self.period.upper.replace(
                    hour=slot.stop.hour, minute=slot.stop.minute, tzinfo=None
                )
                delta = end - self.period.upper.replace(
                    hour=slot.start.hour, minute=slot.start.minute, tzinfo=None
                )

            if self.form.cleaned_data["dom"]:
                dom = int(self.form.cleaned_data["dom"])
                dates = rrule(
                    MONTHLY, dtstart=start, until=end, byweekday=weekdays[dow](dom)
                )
            else:
                dates = rrule(WEEKLY, dtstart=start, until=end, byweekday=dow)

            for date in dates:
                date = date.astimezone()
                date_ranges.append(DateTimeTZRange(date, date + delta))

        else:
            start, end = self.period.lower.replace(
                tzinfo=None
            ), self.period.upper.replace(tzinfo=None)
            rd = relativedelta.relativedelta(end, start)

            if rd.years > 1:
                rr = rrule(YEARLY, dtstart=start, until=end)
                delta = relativedelta.relativedelta(years=1)
            elif rd.years or rd.months > 6:
                rr = rrule(MONTHLY, dtstart=start, until=end)
                delta = relativedelta.relativedelta(months=1)
            elif rd.months > 1:
                rr = rrule(WEEKLY, dtstart=start, until=end)
                delta = relativedelta.relativedelta(weeks=1)
            elif rd.months or rd.days >= 7:
                rr = rrule(DAILY, dtstart=start, until=end)
                delta = relativedelta.relativedelta(days=1)
            elif rd.days > 1:
                rr = rrule(HOURLY, interval=2, dtstart=start, until=end)
                delta = relativedelta.relativedelta(hours=2)
            elif rd.days or rd.hours > 12:
                rr = rrule(HOURLY, dtstart=start, until=end)
                delta = relativedelta.relativedelta(hours=1)
            elif rd.hours > 6:
                rr = rrule(MINUTELY, interval=30, dtstart=start, until=end)
                delta = relativedelta.relativedelta(minutes=30)
            else:
                rr = rrule(MINUTELY, interval=15, dtstart=start, until=end)
                delta = relativedelta.relativedelta(minutes=15)

            # Make a ruleset, add the rule from above and exclude the upper datetime bound
            rrset = rruleset()
            rrset.rrule(rr)
            rrset.exdate(end)

            # Convert the rrule list to DateTimeTZRanges in local timezone
            date_ranges = [
                DateTimeTZRange(dt.astimezone(), (dt + delta).astimezone())
                for dt in rrset
            ]

        return date_ranges


class ListenerReadOnlyModelViewSet(DateRangesMixin, viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        if not self.date_ranges:
            return Listener.objects.none()

        query = Q()

        for date_range in self.date_ranges:
            query = query | Q(session__overlap=date_range)

        return self.listeners.filter(query)


class CountriesViewSet(ListenerReadOnlyModelViewSet):
    def get_queryset(self):
        qs = super(CountriesViewSet, self).get_queryset()
        return qs.values(self.field).annotate(count=Count("*")).order_by("-count")

    def list(self, request, *args, **kwargs):
        response = super(CountriesViewSet, self).list(request, args, kwargs)
        response.data["total"] = (
            self.get_queryset().aggregate(Sum("count")).get("count__sum")
        )
        response.data["distinct"] = (
            self.get_queryset().values("country").distinct().count()
        )
        return response

    field = "country"
    serializer_class = CountriesSerializer


class RefererViewSet(ListenerReadOnlyModelViewSet):
    def get_queryset(self):
        qs = super(RefererViewSet, self).get_queryset()
        self.direct = qs.filter(referer="").count()

        qs = qs.exclude(referer="").annotate(
            domain=Func(
                F("referer"),
                Value("https?://(?:www\.)?(.+?)(?:\:\d+)?(?:\/.*)?"),
                function="regexp_matches",
            ),
        )
        qs = (
            qs.order_by("domain")
            .values("domain")
            .annotate(count=Count("*"))
            .order_by("-count")
        )

        return qs

    def list(self, request, *args, **kwargs):
        response = super(RefererViewSet, self).list(request, args, kwargs)
        response.data["total"] = (
            self.get_queryset().aggregate(Sum("count")).get("count__sum") or 0
        )
        response.data["direct"] = self.direct
        return response

    field = "referer"
    serializer_class = RefererSerializer


class CountViewSet(ListenerReadOnlyModelViewSet):
    def totals(self):
        queryset = Listener.objects.none()

        for date_range in self.date_ranges:
            queryset = queryset.union(
                self.get_queryset()
                .filter(session__overlap=date_range)
                .values(self.streams)
                .order_by(self.streams)
                .annotate(
                    period=Value(date_range.lower, DateTimeField()),
                    count=Count(self.streams),
                    stream=Cast(self.streams, CharField()),
                )
            )

        if len(self.date_ranges) > 1:
            return queryset.order_by("period", self.stream_order)
        else:
            return queryset

    def list(self, request, *args, **kwargs):
        response = {"results": CountSerializer(self.totals(), many=True).data}
        response.update(
            {
                "period": {
                    "start": self.period.lower,
                    "end": self.period.upper,
                },
                "totals": self.get_queryset()
                .order_by(self.stream_order)
                .values(self.streams)
                .annotate(
                    count=Count(self.streams), stream=Cast(self.streams, CharField())
                )
                .values("stream", "count"),
            }
        )
        return Response(response)


class HoursViewSet(ListenerReadOnlyModelViewSet):
    def totals(self):
        qs = Listener.objects.none()

        for date_range in self.date_ranges:
            qs = qs.union(
                self.get_queryset()
                .filter(
                    session__overlap=date_range,
                )
                .annotate(
                    period=Value(date_range, DTRangeField()),
                )
                .annotate(
                    start=Greatest(
                        RangeStartsWith("period"), RangeStartsWith("session")
                    ),
                    end=Least(RangeEndsWith("period"), RangeEndsWith("session")),
                )
                .annotate(
                    length=ExpressionWrapper(
                        F("end") - F("start"), output_field=DurationField()
                    )
                )
                .values(self.streams)
                .order_by(self.streams)
                .annotate(
                    count=ExpressionWrapper(
                        Round(
                            Extract(Sum("length"), "epoch") / 36,
                        )
                        / 100,
                        output_field=FloatField(),
                    ),
                    period=Value(date_range.lower, DateTimeField()),
                    stream=Cast(self.streams, CharField()),
                )
            )

        if qs.count():
            return qs.order_by(
                "period",
                self.stream_order,
            )
        return qs

    def list(self, request, *args, **kwargs):
        response = {"results": HoursSerializer(self.totals(), many=True).data}
        response.update(
            {
                "period": {
                    "start": self.period.lower,
                    "end": self.period.upper,
                },
            }
        )
        return Response(response)
