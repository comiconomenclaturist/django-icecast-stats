from rest_framework import viewsets
from django.db.models import Prefetch, OuterRef, Subquery, Q
from listener.models import Stream
from listener.views import GetParamsMixin
from .serializers import SourceSerializer
from .models import Source


class ConnectionViewset(GetParamsMixin, viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        if self.form.is_valid():
            previous_status = Source.objects.filter(
                timestamp__lte=self.period.lower, stream=OuterRef("stream")
            ).order_by("-timestamp")[:1]

            next_status = Source.objects.filter(
                timestamp__gte=self.period.upper, stream=OuterRef("stream")
            ).order_by("timestamp")[:1]

            sources = Source.objects.filter(
                Q(id__in=Subquery(previous_status.values("id")))
                | Q(timestamp__range=[self.period.lower, self.period.upper])
                | Q(id__in=Subquery(next_status.values("id")))
            )

            qs = Stream.objects.distinct()

            if self.form.cleaned_data["station"]:
                qs = qs.filter(station=self.form.cleaned_data["station"])

            qs = qs.prefetch_related(
                Prefetch("connections", queryset=sources.order_by("timestamp"))
            )

            return qs

        return Stream.objects.none()

    serializer_class = SourceSerializer
