from django.shortcuts import render
from django.views import View, generic
from django.http import JsonResponse
from listener.models import Listener, Station, Stream, Region
from listener.forms import ListenerForm
from stats.secret import ICECAST_AUTH
import xml.etree.ElementTree as ET
import requests


class Home(generic.FormView):
	def get(self, request, *args, **kwargs):
		form = ListenerForm(request.GET)
		
		context = {
			'form': form,
			'min_date': Listener.objects.order_by('session').first().session.lower.astimezone().strftime('%Y/%m/%d %H:%M'),
			'max_date': Listener.objects.order_by('session').last().session.upper.astimezone().strftime('%Y/%m/%d %H:%M'),
			}
		
		return render(request, 'base/home.html', context)


class HomeD3(generic.FormView):
	def get(self, request, *args, **kwargs):
		form = ListenerForm()
		context = {
			'form': form,
			'min_date': Listener.objects.order_by('session').first().session.lower.astimezone().strftime('%Y/%m/%d %H:%M'),
			'max_date': Listener.objects.order_by('session').last().session.upper.astimezone().strftime('%Y/%m/%d %H:%M'),
			}
		return render(request, 'base/d3.html', context)


class LiveListeners(View):
	def get(self, request, *args, **kwargs):
		live_listeners = {station: 0 for station in Station.objects.values_list('name', flat=True)}

		url = 'http://%s:%s/admin/listmounts' % (ICECAST_AUTH['host'], ICECAST_AUTH['port'])
		r = requests.get(url, auth=(ICECAST_AUTH['username'], ICECAST_AUTH['password']))
		tree = ET.fromstring(r.text)
		sources = tree.findall('source')

		for source in sources:
			stream = Stream.objects.filter(mountpoint = source.get('mount'))
			listeners = int(source.find('listeners').text)
			if stream and listeners:
				live_listeners[stream.get().station.name] += listeners
		
		return JsonResponse(live_listeners)