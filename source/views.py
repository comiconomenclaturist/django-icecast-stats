from rest_framework import viewsets
from django.db.models import Prefetch
from listener.models import Stream
from listener.views import GetParamsMixin
from .serializers import SourceSerializer
from .models import Source


class ConnectionViewset(GetParamsMixin, viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        if self.form.is_valid():
            sources = Source.objects.filter(
                timestamp__range=[self.period.lower, self.period.upper]
            )

            queryset = Stream.objects.filter(connections__in=sources).distinct()

            if self.form.cleaned_data["station"]:
                queryset = queryset.filter(station=self.form.cleaned_data["station"])

            queryset = queryset.prefetch_related(
                Prefetch("connections", queryset=sources)
            )

            return queryset

        return Stream.objects.none()

    serializer_class = SourceSerializer
