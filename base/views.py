from django.shortcuts import render
from django.views.generic import FormView
from listener.models import Listener
from listener.forms import ListenerForm


class Home(FormView):
	def get(self, request, *args, **kwargs):
		form = ListenerForm()
		context = {
			'form': form,
			'min_date': Listener.objects.order_by('session').first().session.lower.astimezone().strftime('%Y/%m/%d %I:%m%p'),
			'max_date': Listener.objects.order_by('session').last().session.upper.astimezone().strftime('%Y/%m/%d %I:%m%p'),
			}
		return render(request, 'base/home.html', context)


class HomeD3(FormView):
	def get(self, request, *args, **kwargs):
		form = ListenerForm()
		context = {
			'form': form,
			'min_date': Listener.objects.order_by('session').first().session.lower.astimezone().strftime('%Y/%m/%d %I:%m%p'),
			'max_date': Listener.objects.order_by('session').last().session.upper.astimezone().strftime('%Y/%m/%d %I:%m%p'),
			}
		return render(request, 'base/d3.html', context)
