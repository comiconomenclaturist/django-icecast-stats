from django.db.models import Count
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import BrowserSerializer
from listener.views import ListenerQuerySetMixin


class BrowsersViewSet(ListenerQuerySetMixin, viewsets.ReadOnlyModelViewSet):
	def get_queryset(self):
		qs = super(BrowsersViewSet, self).get_queryset()
		return qs.values('user_agent__browser__family').annotate(count=Count('*')).order_by('-count')

	serializer_class = BrowserSerializer
	permission_classes = [IsAuthenticated]
