from django.shortcuts import render
from django.views.generic import FormView
from listener.models import ListenerAggregate
from listener.forms import ListenerAggregateForm


class Home(FormView):
	def get(self, request, *args, **kwargs):
		form = ListenerAggregateForm()
		context = {
			'form': form,
			'min_date': ListenerAggregate.objects.order_by('period').first().period.lower.astimezone().strftime('%Y/%m/%d %I:%m%p'),
			'max_date': ListenerAggregate.objects.order_by('period').last().period.upper.astimezone().strftime('%Y/%m/%d %I:%m%p'),
			}
		return render(request, 'base/home.html', context)

