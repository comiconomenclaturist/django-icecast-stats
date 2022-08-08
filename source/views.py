from rest_framework import viewsets
from .models import Disconnection
from .serializers import DisconnectionSerializer
from listener.views import GetParamsMixin


class DisconnectionViewset(GetParamsMixin, viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        if self.form.is_valid():
            qs = Disconnection.objects.filter(
                period__overlap=self.period,
            )
            if self.form.cleaned_data["station"]:
                qs = qs.filter(stream__station=self.form.cleaned_data["station"])
            return qs

        return Disconnection.objects.none()

    serializer_class = DisconnectionSerializer
