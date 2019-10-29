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
		station = self.request.query_params.get('station') or 'A'
		end = self.request.query_params.get('end')
		start = self.request.query_params.get('start')

		if start and end:
			start = parser.parse(start).astimezone()
			end = parser.parse(end).astimezone()
		else:
			end = Listener.objects.last().session.upper.replace(minute=0, second=0) + timedelta(hours=1)
			start = end - timedelta(days=1)

		qs = Listener.objects.filter(session__overlap=DateTimeTZRange(start, end))

		if station != 'A':
			qs = qs.filter(stream__station=station)

		qs = qs.values('user_agent__browser__family').annotate(count=Count('*')).order_by('-count')

		return qs

	serializer_class = BrowserSerializer
	permission_classes = [IsAuthenticated]
