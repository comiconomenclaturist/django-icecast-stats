from django.db.models import Count
from dateutil import parser
from datetime import timedelta
from psycopg2.extras import DateTimeTZRange
from rest_framework import views, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import *
from .serializers import BrowserSerializer
from listener.models import Listener

class Browsers(viewsets.ReadOnlyModelViewSet):
	def get_queryset(self):
		station = self.request.query_params.get('station', 'A')
		end = self.request.query_params.get('end', None)
		start = self.request.query_params.get('start', None)

		if start and end:
			start = parser.parse(start).astimezone()
			end = parser.parse(end).astimezone()
		else:
			end = Listener.objects.last().session.upper.replace(minute=0, second=0) + timedelta(hours=1)
			start = end - timedelta(days=1)

		queryset = Listener.objects.filter(session__overlap=DateTimeTZRange(start, end))

		if station != 'A':
			queryset = queryset.filter(stream__station=station)

		queryset = queryset.values('user_agent__browser__family').annotate(count=Count('*')).order_by('-count')

		return queryset

	serializer_class = BrowserSerializer
	permission_classes = [IsAuthenticated]
